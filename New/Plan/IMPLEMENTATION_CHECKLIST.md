# Implementation Checklist

**Parent:** [MASTER_PLAN.md](./MASTER_PLAN.md) | **Status:** Complete (2026-06-11)

File-by-file implementation spec. All items verified in `New/Implement`.

---

## Phase 1 — `browser/` core

- [x] **`browser/config.py`** — env: headless, timeouts, allowlist, audit, agent settings
- [x] **`browser/session.py`** — singleton lifecycle, audit on start/close
- [x] **`browser/state.py`** — DOM extractor, cache, guards integration
- [x] **`browser/actions.py`** — navigate, click, type, scroll, evaluate, get_text_content
- [x] **`browser/security.py`** — URL + JS validation
- [x] **`browser/audit.py`** — JSONL audit log
- [x] **`browser/guards.py`** — STALE_STATE enforcement

---

## Phase 2 — `browser_mcp.py`

- [x] FastMCP with 9 tools (match `mcp_tools.schema.json`)
- [x] JSON string responses, stdio entry

---

## Phase 3 — `browser_agent/`

- [x] **`tools.py`** — LangChain wrappers
- [x] **`agent.py`** — create_react_agent, system prompt, finally close, API key check
- [x] **`mcp_server.py`** — `run_browser_task`

---

## Phase 4 — Config & deps

- [x] `pyproject.toml` — playwright, langchain, litellm, fastmcp
- [x] `config.json` paths → `D:/Custom_MCP/New/Implement`
- [x] `.env.example` with security vars
- [x] `cursor-mcp.example.json`, `setup.ps1`
- [x] Legacy code in `Old/` (deprecated)

---

## Phase 5 — Tests & CI

- [x] `tests/test_browser_core.py`
- [x] `tests/test_browser_integration.py`
- [x] `tests/test_security.py`
- [x] `tests/test_mcp_smoke.py`
- [x] `tests/test_agent.py`
- [x] `.github/workflows/test.yml`

---

## Acceptance gate

All MASTER_PLAN §6 acceptance criteria met. See [../Implement/DELIVERABLE_RATING.md](../Implement/DELIVERABLE_RATING.md).
