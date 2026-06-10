# Test Plan — Browser Automation

**Iteration:** 2 | **Parent:** [MASTER_PLAN.md](./MASTER_PLAN.md)

---

## 1. Unit tests (`browser/`)

| Test | Assert |
|------|--------|
| `test_session_start_close` | Browser launches and closes cleanly |
| `test_navigate_example_com` | URL matches after goto |
| `test_get_state_returns_indices` | `interactive_elements[0].index == 0` |
| `test_click_by_index` | Click succeeds on known fixture page |
| `test_state_cache_invalidation` | Cache miss after navigate |

**Fixture:** local HTML file or `https://example.com`

---

## 2. MCP integration tests (`browser_mcp.py`)

| Test | Method |
|------|--------|
| Tool list includes 9 browser tools | MCP client list_tools |
| `browser_start` → `browser_navigate` → `browser_get_state` | Sequential tool calls |
| Error without session | `browser_click` returns NO_SESSION |

---

## 3. Agent tests (`browser_agent/`)

| Test | Assert |
|------|--------|
| `run_browser_task("go to example.com")` | Returns success; browser closed |
| Max steps respected | Stops at AGENT_MAX_STEPS |
| Mock LLM tool sequence | Unit test with fixed tool responses |

---

## 4. Smoke test (manual)

1. Enable MCP in Cursor
2. Path A: "Start browser, go to google.com, get state, close"
3. Path B: `run_browser_task("Search for Playwright on Google")`
4. Verify no orphaned `chrome.exe` in Task Manager

---

## 5. CI (future)

```yaml
# .github/workflows/test.yml
- run: pip install -e ".[test]"
- run: python -m playwright install chromium
- run: pytest tests/ -m "not live_llm"
```

Mark live LLM tests with `@pytest.mark.live_llm` — skip in CI without keys.
