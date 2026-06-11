# Production Readiness Guide

**Implementation:** `D:\Custom_MCP\New\Implement`

## Pre-flight checklist

1. Copy `.env.example` → `.env` and set provider API keys
2. Set `BROWSER_HEADLESS=true` on servers
3. Set `BROWSER_ALLOWED_HOSTS` to your target domains (comma-separated)
4. Keep `BROWSER_BLOCK_LOCALHOST=true`
5. Review `BROWSER_ALLOW_JAVASCRIPT` — disable if agents don't need `browser_execute_javascript`
6. Enable audit: `BROWSER_AUDIT_ENABLED=true` (default)
7. Register MCP via `cursor-mcp.example.json` (no secrets in JSON)

## Security controls (implemented)

| Control | Env / Code |
|---------|------------|
| URL scheme block | `browser/security.py` — http/https only |
| Localhost block | `BROWSER_BLOCK_LOCALHOST=true` |
| Host allowlist | `BROWSER_ALLOWED_HOSTS=example.com,google.com` |
| JS restrictions | `BROWSER_MAX_SCRIPT_LENGTH`, pattern blocklist |
| State freshness | `browser/guards.py` — `STALE_STATE` error |
| Audit trail | `~/Downloads/browser-mcp/audit.jsonl` |
| Session cleanup | Agent `finally` + explicit `browser_close` |

## CI

GitHub Actions (`.github/workflows/test.yml`) runs 19 pytest cases on every push to `New/Implement`.

## Operational notes

- One browser session per MCP process; restart Cursor MCP if the browser hangs hangs
- Audit log rotates manually — archive or truncate `audit.jsonl` periodically
- For untrusted tasks, use Path A (Cursor orchestrates) with allowlist rather than Path B agent

## Live LLM smoke (optional)

```powershell
cd D:\Custom_MCP\New\Implement
# Requires OPENAI_API_KEY in .env
uv run python -c "import asyncio; from browser_agent.agent import run_task; print(asyncio.run(run_task('Open https://example.com and return the page title')))"
```
