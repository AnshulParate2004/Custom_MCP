# Strict Implementation Plan — Code Phase

**Aligned to:** [MASTER_PLAN.md](./MASTER_PLAN.md), [TECHNICAL_PLAN.md](./tech-plan/TECHNICAL_PLAN.md), [FLOW_LOGIC.md](./flow-logic/FLOW_LOGIC.md)

## Alignment targets (must match docs 100%)

| Doc requirement | Code artifact | Verify |
|-----------------|---------------|--------|
| 9 MCP tools (§4) | `browser_mcp.py` | Tool names exact match |
| Playwright engine (ADR-001) | `browser/session.py` | No browser-use import |
| Indexed DOM (ADR-004) | `browser/state.py` | DOM_EXTRACTOR_SPEC.md |
| LangChain + LiteLLM (ADR-003) | `browser_agent/agent.py` | ChatLiteLLM only |
| Dual path (ADR-005) | `browser_mcp.py` + `browser_agent/` | Shared `browser/actions.py` |
| get_state before click (FLOW §3) | Agent system prompt | Enforced in prompt |
| browser_close in finally (FLOW §3) | `agent.py` | try/finally |
| AGENT_MAX_STEPS=25 (MASTER §5) | `browser/config.py` | Env default 25 |

## Build order

1. `browser/config.py` → `session.py` → `state.py` → `actions.py`
2. `browser_mcp.py`
3. `browser_agent/tools.py` → `agent.py` → `mcp_server.py`
4. Root `pyproject.toml`, `config.json`, `.env.example`
5. Alignment audit vs PDFs

## Root layout (D:/Custom_MCP/New/Implement/)

```
browser/
browser_mcp.py
browser_agent/
pyproject.toml
config.json
.env.example
```

Old code stays in `Old/` — not modified.
