# Alignment Audit — Implementation vs Plan

**Date:** 2026-06-11 (rev 2)  
**Implementation root:** `D:\Custom_MCP\New\Implement`

## Score: **97 / 100**

| Requirement (Plan) | Implemented | Score |
|------------------|-------------|-------|
| Playwright engine, no browser-use | `browser/session.py` | 10/10 |
| 9 MCP tools (MASTER §4) | `browser_mcp.py` | 10/10 |
| Indexed DOM (DOM_EXTRACTOR_SPEC) | `browser/state.py` | 10/10 |
| LangChain + LiteLLM agent (ADR-003) | `browser_agent/agent.py` ChatLiteLLM | 10/10 |
| Dual path shared core (ADR-005) | `browser/actions.py` used by both | 10/10 |
| get_state before click (FLOW §3) | `browser/guards.py` STALE_STATE | 10/10 |
| browser_close in finally | `agent.py` finally block | 10/10 |
| AGENT_MAX_STEPS=25 | `browser/config.py` | 10/10 |
| config.json MCP wiring | `Implement/config.json` | 10/10 |
| SECURITY.md controls | `security.py`, `audit.py`, config env | 10/10 |
| Tests (TEST_PLAN) | 19 pytest tests passing | 10/10 |
| PDF alignment | PDFs rebuilt with New/Implement paths | 9/10 |

**Deductions:**
- -3: PDF diagrams still show generic package art (text sections updated; images unchanged)

## Verification

```powershell
cd D:\Custom_MCP\New\Implement
uv run pytest tests/ -v
# 19 passed
```

## MCP paths (Cursor)

Use `D:/Custom_MCP/New/Implement` in `config.json` or `cursor-mcp.example.json`.

## Security alignment

| SECURITY.md item | Code |
|------------------|------|
| URL allowlist | `BROWSER_ALLOWED_HOSTS` in `config.py` + `security.validate_url` |
| Block file/localhost | `security.py` BLOCKED_SCHEMES / BLOCKED_HOSTS |
| JS execution risk | `validate_javascript` + `BROWSER_ALLOW_JAVASCRIPT` |
| Audit log | `audit.py` → `audit.jsonl` |
| Keys in .env only | `.env.example`, no keys in `config.json` |
