from openai import OpenAI
import os

def chat_with_openai():
    """Chat application using OpenAI SDK"""
    
    # Initialize OpenAI client
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "your-api-key-here")
    )
    
    # Store conversation history
    messages = []
    
    print("OpenAI Chat Application")
    print("=" * 50)
    print("Type 'quit' or 'exit' to end the conversation")
    print("=" * 50)
    print()
    
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break
            
        if not user_input:
            continue
        
        # Add user message to conversation history
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        try:
            # Call OpenAI API using SDK
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            # Extract assistant's response
            assistant_message = response.choices[0].message.content
            
            # Add assistant message to conversation history
            messages.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # Display assistant's response
            print(f"\nAssistant: {assistant_message}\n")
            
        except Exception as e:
            print(f"\nError: {str(e)}\n")
            # Remove the last user message if there was an error
            messages.pop()

if __name__ == "__main__":
    chat_with_openai()
