# ADR-002: Remove browser-use Dependency

**Status:** Accepted  
**Date:** 2026-06-11

## Context

Current `Browser_Agent.py` requires `BROWSER_USE_API_KEY` and `ChatBrowserUse` SDK.

## Decision

Remove browser-use entirely. Implement owned `browser/` core + MCP + LangChain agent.

## Rationale

- No vendor API lock-in
- Full control over LLM provider via LiteLLM
- Simpler dependency tree

## Consequences

- Rewrite `Browser_Automation_Fast.py` and `Browser_Agent.py`
- Migration effort; documented in flow-logic migration diagram
