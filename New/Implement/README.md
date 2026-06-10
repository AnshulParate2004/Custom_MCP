# Browser Automation Implementation

**Location:** `D:\Custom_MCP\New\Implement`  
**Plan docs:** [../Plan/MASTER_PLAN.md](../Plan/MASTER_PLAN.md)

Owned **Playwright + MCP + LangChain-LiteLLM** stack — no browser-use.

## Layout

```
Implement/
├── browser/              # Playwright core (session, state, actions)
├── browser_agent/        # LangGraph agent + MCP server
├── browser_mcp.py       # Path A — 9 MCP tools for Cursor
├── config.json         # Cursor MCP configuration
├── pyproject.toml
├── .env.example
└── tests/
```

## Setup

```powershell
cd D:\Custom_MCP\New\Implement
uv sync --extra test
uv run python -m playwright install chromium
copy .env.example .env
```

## MCP servers

| Server | Command |
|--------|---------|
| Browser_Automation | `uv run --directory D:/Custom_MCP/New/Implement python browser_mcp.py` |
| Browser_Agent | `uv run --directory D:/Custom_MCP/New/Implement python browser_agent/mcp_server.py` |

## Tools (Path A)

`browser_start`, `browser_close`, `browser_navigate`, `browser_get_state`, `browser_get_content`, `browser_click`, `browser_type`, `browser_scroll`, `browser_execute_javascript`

## Agent (Path B)

`run_browser_task(task, model?)` — uses `ChatLiteLLM` via langchain-litellm.

## Tests

```powershell
uv run pytest tests/ -m "not live_llm"
```
