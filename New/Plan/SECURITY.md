# Security Plan — Browser Automation MCP

**Iteration:** 2 | **Parent:** [MASTER_PLAN.md](../MASTER_PLAN.md)

---

## 1. Threat model

| Threat | Mitigation |
|--------|------------|
| Arbitrary URL navigation (SSRF/internal) | Optional allowlist `BROWSER_ALLOWED_HOSTS`; block `file://`, `localhost` in prod |
| Arbitrary JavaScript execution | `browser_execute_javascript` restricted to trusted Cursor sessions; document risk |
| Credential leakage via screenshots | Screenshots stay local; never log base64 to stdout |
| Orphaned browser processes | Mandatory `browser_close`; session timeout; `finally` in agent |
| API key exposure | Keys in `.env` only; never in `config.json` committed to git |
| Download malware | Downloads to fixed path `~/Downloads/browser-mcp`; scan optional |

---

## 2. MCP process isolation

- Each MCP server = separate Python process via `uv run`
- No shared browser between `browser_mcp.py` and `browser_agent` unless explicitly designed later
- Stdio transport only (no network listener)

---

## 3. Environment secrets

```env
# Never commit .env
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
LITELLM_MODEL=openai/gpt-4o
```

Remove from repo: `BROWSER_USE_API_KEY`, hardcoded keys in `config.json`.

---

## 4. Browser hardening (Phase 1)

- Default: non-headless for dev visibility; headless via `BROWSER_HEADLESS=true`
- `ignore_https_errors=false` by default
- No persistent profile/cookies (fresh context each session)

---

## 5. Phase 2 security (implemented)

- [x] Host allowlist enforcement in `browser/security.py` + `BROWSER_ALLOWED_HOSTS`
- [x] Audit log of actions (local JSONL) — `browser/audit.py`
- [x] STALE_STATE guard in `browser/guards.py`
- [ ] Rate limit on `browser_navigate` per session (future / ops)
