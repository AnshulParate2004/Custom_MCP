# Implementation Checklist

**Parent:** [MASTER_PLAN.md](./MASTER_PLAN.md) | **Iteration:** 4

File-by-file implementation spec. Check off during code phase.

---

## Phase 1 — `browser/` core

- [ ] **`browser/config.py`** — load env: `BROWSER_HEADLESS`, `BROWSER_TIMEOUT_MS`, `STATE_CACHE_TTL`
- [ ] **`browser/session.py`**
  - [ ] `_playwright`, `_browser`, `_context`, `_page` singletons
  - [ ] `async def start(headless: bool) -> dict`
  - [ ] `async def close() -> dict`
  - [ ] `async def get_page() -> Page` (raise `NoSessionError` if idle)
- [ ] **`browser/state.py`**
  - [ ] In-page JS scanner for interactive elements
  - [ ] `_last_snapshot: dict` + cache timestamp
  - [ ] `async def get_state(include_screenshot, force_refresh) -> dict`
  - [ ] `def resolve_index(index: int) -> ElementHandle info`
- [ ] **`browser/actions.py`**
  - [ ] `navigate`, `click`, `type_text`, `scroll`, `evaluate`, `screenshot`, `get_text_content`
  - [ ] Invalidate state cache after mutating actions

---

## Phase 2 — `browser_mcp.py`

- [ ] FastMCP or mcp Server with 9 tools (match `mcp_tools.schema.json`)
- [ ] JSON string responses for all tools
- [ ] `if __name__ == "__main__"` stdio entry

---

## Phase 3 — `browser_agent/`

- [ ] **`tools.py`** — LangChain `@tool` wrappers calling `browser.actions`
- [ ] **`agent.py`**
  - [ ] `create_react_agent(llm, tools)`
  - [ ] System prompt with rules from FLOW_LOGIC.md
  - [ ] `async def run_task(task: str, model: str | None) -> str`
  - [ ] `try/finally` → `browser.close()`
- [ ] **`mcp_server.py`** — `@mcp.tool run_browser_task`

---

## Phase 4 — Config & deps

- [ ] Update `pyproject.toml` — remove browser-use, add playwright/langchain/litellm
- [ ] Update `config.json` paths to `D:/Custom_MCP`
- [ ] Add `.env.example`
- [ ] Deprecate `Browser_Agent.py`, `Browser_Automation_Fast.py`

---

## Phase 5 — Tests

- [ ] `tests/test_session.py`
- [ ] `tests/test_state.py`
- [ ] Manual smoke per TEST_PLAN.md

---

## Acceptance gate

All items in MASTER_PLAN §6 acceptance column pass before marking implementation complete.
