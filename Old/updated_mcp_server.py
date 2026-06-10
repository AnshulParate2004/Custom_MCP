from fastmcp import FastMCP
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os
from typing import List, Dict, Optional
import google.generativeai as genai
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

# Initialize Qdrant client
qdrant_client = QdrantClient(
    url=os.getenv('QDRANT_URL'), 
    api_key=os.getenv('QDRANT_API_KEY'),
)

# Configure Google Generative AI for embeddings
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Initialize LangChain Google GenAI
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv('GOOGLE_API_KEY'),
    temperature=0
)

# Valid collections
VALID_COLLECTIONS = ['bio', 'chem']

# Create FastMCP server
mcp = FastMCP("chembio-qdrant-server")


# ==================== PYDANTIC MODEL ====================

class RelevanceEvaluation(BaseModel):
    """Model for relevance evaluation with structured output"""
    # db name consideration 
    db_name: Optional[str] = Field(
        default=None,
        description="Database name which is 'bio' or 'chem'. Set this ONLY if not already provided."
    )

    # retriever 
    is_relevant: Optional[bool] = Field(
        default=None,
        description="True if chunks are related to user query, False otherwise"
    )
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0, le=1.0,
        description="Confidence score between 0.0 and 1.0"
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Brief explanation of the decision"
    )
    refined_query: Optional[str] = Field(
        default="",
        description="Empty string if is_relevant=True, refined query if is_relevant=False"
    )


# ==================== HELPER FUNCTIONS ====================

def get_embedding(text: str) -> list:
    """
    Generate embedding for the given text using Google Generative AI.
    
    Args:
        text: Input text to embed
    
    Returns:
        List of floats representing the embedding vector
    """
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_query"
    )
    return result['embedding']


def perform_search(query: str, collection: str, num_chunks: int) -> list:
    """
    Perform actual Qdrant search.
    
    Args:
        query: Search query
        collection: Collection name
        num_chunks: Number of chunks to retrieve
    
    Returns:
        Search results list
    """
    query_vector = get_embedding(query)
    
    search_results = qdrant_client.query_points(
        collection_name=collection,
        query=query_vector,
        limit=num_chunks
    )
    
    results = []
    for idx, hit in enumerate(search_results.points, 1):
        results.append({
            "rank": idx,
            "score": float(hit.score),
            "id": str(hit.id),
            "payload": hit.payload
        })
    
    return results


def determine_database(query: str) -> RelevanceEvaluation:
    """
    Use LLM to determine which database (chem or bio) to search.
    Called ONLY when collection is None.
    
    Args:
        query: User's search query
    
    Returns:
        RelevanceEvaluation with db_name set to 'chem' or 'bio'
    """
    parser = PydanticOutputParser(pydantic_object=RelevanceEvaluation)
    
    prompt = PromptTemplate(
        template="""You are an expert in chemistry and biology. Determine which database to search based on the user's query.

User's Query: "{query}"

Your task: Classify this query as either CHEMISTRY or BIOLOGY.

- Chemistry topics: chemical reactions, molecular structure, organic/inorganic chemistry, acids/bases, 
  thermodynamics, periodic table, chemical bonding, stoichiometry, catalysis, electrochemistry, etc.
  
- Biology topics: cells, genetics, ecology, evolution, anatomy, physiology, organisms, 
  photosynthesis, respiration, DNA, proteins, ecosystems, microbiology, botany, zoology, etc.

IMPORTANT: 
- Set ONLY the 'db_name' field to either "chem" or "bio"
- Set 'confidence' between 0.0 and 1.0 (high confidence 0.7-1.0 if clearly one domain)
- Provide 'reasoning' explaining your choice
- Leave 'is_relevant' and 'refined_query' as null/empty (they are not needed for database selection)

{format_instructions}

Determine the database:""",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    try:
        _input = prompt.format_prompt(query=query)
        output = llm.invoke(_input.to_string())
        selection = parser.parse(output.content)
        
        # Ensure db_name is valid
        if not selection.db_name or selection.db_name not in VALID_COLLECTIONS:
            print(f"   [WARN] Invalid db_name '{selection.db_name}', defaulting to 'bio'")
            selection.db_name = "bio"
            
        return selection
        
    except Exception as e:
        print(f"Database determination error: {e}")
        # Default fallback
        return RelevanceEvaluation(
            db_name="bio",
            confidence=0.5,
            reasoning=f"Classification failed, defaulting to bio: {str(e)}"
        )


def evaluate_chunks_with_llm(query: str, chunks: list, db_name: str) -> RelevanceEvaluation:
    """
    Evaluate chunks using LLM with LangChain PydanticOutputParser.
    ONLY ONE LLM CALL.
    
    Args:
        query: User's search query
        chunks: Retrieved chunks from Qdrant
        db_name: Already determined database name ('bio' or 'chem')
    
    Returns:
        RelevanceEvaluation with is_relevant and refined_query
    """
    parser = PydanticOutputParser(pydantic_object=RelevanceEvaluation)
    
    # Format chunks for LLM
    chunks_text = "\n\n".join([
        f"Chunk {i+1} (Score: {chunk['score']:.3f}):\n{chunk['payload'].get('subtopic_text', 'No text')[:500]}"
        for i, chunk in enumerate(chunks[:3])  # Use top 3 chunks
    ])
    
    prompt = PromptTemplate(
        template="""You are an expert Vector DB Retriever. Evaluate if the retrieved chunks are relevant to answer the user's query.

Database: {db_name}
User's Query: "{query}"

Retrieved Chunks:
{chunks_text}

Your task:
1. Analyze if these chunks contain information that can answer the user's query
2. Check if the chunks are on-topic and relevant to the query

IMPORTANT:
- The 'db_name' is already set to "{db_name}" - DO NOT change it, leave it as null in your response
- Focus on setting 'is_relevant', 'confidence', 'reasoning', and 'refined_query'

If chunks ARE relevant (is_relevant=True):
- Set is_relevant to true
- Set refined_query to empty string ""
- Provide high confidence (0.7-1.0)
- Explain in 'reasoning' why the chunks are relevant

If chunks are NOT relevant (is_relevant=False):
- Set is_relevant to false
- Generate a better 'refined_query' using:
  * More specific scientific terminology
  * Related chemistry/biology concepts
  * Clearer and more focused keywords
- Provide 'reasoning' for why current chunks aren't good enough
- Set appropriate confidence level (0.0-0.6)
- The refined query should be different from the original query

{format_instructions}

Return your evaluation:""",
        input_variables=["query", "chunks_text", "db_name"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    try:
        _input = prompt.format_prompt(query=query, chunks_text=chunks_text, db_name=db_name)
        output = llm.invoke(_input.to_string())
        evaluation = parser.parse(output.content)
        
        # Ensure db_name stays the same
        evaluation.db_name = None  # Don't override the already determined db_name
        
        return evaluation
        
    except Exception as e:
        print(f"LLM evaluation error: {e}")
        # Default to accepting results if evaluation fails
        return RelevanceEvaluation(
            db_name=None,
            is_relevant=True,
            confidence=0.5,
            reasoning=f"Evaluation failed: {str(e)}",
            refined_query=""
        )


# ==================== MCP TOOL ====================

@mcp.tool()
def search_qdrant(query: str, collection: Optional[str] = None, num_chunks: int = 5) -> dict:
    """
    Search for relevant chunks in Qdrant collections with LLM-powered evaluation.
    
    Flow:
    1. If collection is None -> Use LLM to determine database (bio or chem)
    2. Search Qdrant with user query
    3. Send results to LLM for evaluation (ONE LLM CALL)
    4. If relevant -> return chunks
    5. If not relevant -> search again with refined query from LLM (up to 20 attempts)
    
    Args:
        query: The search query text
        collection: Collection name to search in ('bio' or 'chem'). If None, LLM will determine it.
        num_chunks: Number of chunks to retrieve (default: 5, max: 20)
    
    Returns:
        Dictionary containing search results with scores and payloads
    
    Examples:
        search_qdrant("What is photosynthesis?")  # Auto-determines 'bio'
        search_qdrant("Explain organic chemistry", "chem", 10)  # Manual collection
    """
    
    # Validate num_chunks
    if num_chunks < 1 or num_chunks > 20:
        return {
            "error": "num_chunks must be between 1 and 20",
            "provided": num_chunks
        }
    
    try:
        original_query = query
        db_name = collection
        
        # STEP 0: Determine database if not provided
        if db_name is None:
            print(f"\n[DB SELECT] Collection not specified. Using LLM to determine database...")
            db_selection = determine_database(query)
            db_name = db_selection.db_name
            print(f"   [SELECTED] Database: '{db_name}' (Confidence: {db_selection.confidence:.2f})")
            print(f"   [REASON] {db_selection.reasoning}")
        else:
            # Validate provided collection
            if db_name not in VALID_COLLECTIONS:
                return {
                    "error": f"Invalid collection name: '{db_name}'. Must be one of: {', '.join(VALID_COLLECTIONS)}",
                    "valid_collections": VALID_COLLECTIONS
                }
            print(f"\n[DB SELECT] Using provided collection: '{db_name}'")
        
        # Step 1: Perform initial search with user query
        print(f"\n[SEARCH] Searching '{db_name}' collection with query: '{query}'")
        initial_results = perform_search(query, db_name, num_chunks)
        
        if not initial_results:
            return {
                "status": "not_found",
                "message": "No results found in Qdrant",
                "original_query": original_query,
                "collection": db_name,
                "results": []
            }
        
        print(f"   [OK] Found {len(initial_results)} chunks")
        
        # Step 2 & 3: Iterative refinement with max 20 attempts
        current_query = query
        current_results = initial_results
        max_attempts = 20
        attempt = 1
        search_history = []
        
        while attempt <= max_attempts:
            print(f"\n   [ATTEMPT {attempt}/{max_attempts}] Evaluating query: '{current_query}'")
            print(f"   [LLM] Evaluating relevance with LLM...")
            
            # Evaluate chunks with LLM
            evaluation = evaluate_chunks_with_llm(current_query, current_results, db_name)
            
            print(f"   [EVAL] Relevant: {evaluation.is_relevant} (Confidence: {evaluation.confidence:.2f})")
            print(f"   [INFO] {evaluation.reasoning}")
            
            # Store search history
            search_history.append({
                "attempt": attempt,
                "query": current_query,
                "num_results": len(current_results),
                "evaluation": {
                    "is_relevant": evaluation.is_relevant,
                    "confidence": evaluation.confidence,
                    "reasoning": evaluation.reasoning,
                    "refined_query": evaluation.refined_query
                }
            })
            
            # Check if chunks are relevant
            if evaluation.is_relevant:
                # SUCCESS! Chunks are good, return them
                print(f"   [SUCCESS] Chunks meet user requirements!")
                return {
                    "status": "success",
                    "query": current_query,
                    "original_query": original_query,
                    "collection": db_name,
                    "num_chunks_requested": num_chunks,
                    "num_chunks_returned": len(current_results),
                    "attempts": attempt,
                    "search_history": search_history,
                    "evaluation": {
                        "is_relevant": evaluation.is_relevant,
                        "confidence": evaluation.confidence,
                        "reasoning": evaluation.reasoning
                    },
                    "results": current_results
                }
            
            # Chunks not relevant, check if we should continue
            if attempt >= max_attempts:
                # Max attempts reached, return failure
                print(f"   [FAIL] Max attempts ({max_attempts}) reached. No relevant chunks found.")
                return {
                    "status": "max_attempts_reached",
                    "message": f"Chunks not relevant after {max_attempts} attempts",
                    "original_query": original_query,
                    "final_query": current_query,
                    "collection": db_name,
                    "attempts": attempt,
                    "search_history": search_history,
                    "results": current_results
                }
            
            # Try to refine query
            if evaluation.refined_query and evaluation.refined_query.strip():
                refined_query = evaluation.refined_query
                print(f"   [REFINE] Searching with refined query: '{refined_query}'")
                
                # Search with refined query
                refined_results = perform_search(refined_query, db_name, num_chunks)
                
                if not refined_results:
                    print(f"   [FAIL] No results with refined query. Stopping.")
                    return {
                        "status": "not_found_refined",
                        "message": "No results found with refined query",
                        "original_query": original_query,
                        "final_query": refined_query,
                        "collection": db_name,
                        "attempts": attempt,
                        "search_history": search_history,
                        "results": []
                    }
                
                print(f"   [OK] Found {len(refined_results)} chunks with refined query")
                
                # Update for next iteration
                current_query = refined_query
                current_results = refined_results
                attempt += 1
            else:
                # No refined query provided, cannot continue
                print(f"   [FAIL] No refined query provided. Stopping.")
                return {
                    "status": "not_relevant",
                    "message": "Chunks not relevant and no refined query provided",
                    "original_query": original_query,
                    "collection": db_name,
                    "attempts": attempt,
                    "search_history": search_history,
                    "evaluation": {
                        "is_relevant": evaluation.is_relevant,
                        "confidence": evaluation.confidence,
                        "reasoning": evaluation.reasoning
                    },
                    "results": current_results
                }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Search failed: {str(e)}",
            "query": query,
            "collection": db_name if 'db_name' in locals() else None
        }


if __name__ == "__main__":
    # Run the FastMCP server
    mcp.run()
