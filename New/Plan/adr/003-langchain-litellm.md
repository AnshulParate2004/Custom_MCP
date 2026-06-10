# ADR-003: LangChain + LiteLLM for Agent LLM

**Status:** Accepted  
**Date:** 2026-06-11

## Context

Agent must support OpenAI, Anthropic, Ollama, Groq without code changes.

## Decision

Use `langchain-litellm.ChatLiteLLM` with `langgraph.prebuilt.create_react_agent`.

## Rationale

- Single model string: `provider/model`
- Standard LangChain tool interface
- User explicitly requested langchain-litellm

## Consequences

- Additional deps: langchain, langgraph, litellm, langchain-litellm
- Provider keys via standard env vars
