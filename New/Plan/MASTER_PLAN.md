# Custom MCP Browser Automation — MASTER PLAN

> **Single source of truth.** All sub-documents derive from this file.  
> **Current iteration:** 2  
> **Last updated:** 2026-06-11  
> **Status:** Documentation complete; code implementation pending

---

## 1. Vision

Replace **browser-use** (vendor SDK + API key) with an **owned** stack:

| Layer | Technology |
|-------|------------|
| Browser | Playwright (Chromium) |
| Cursor integration | MCP stdio tools |
| Autonomous tasks | LangGraph + langchain-litellm |
| Config | `.env` + JSON schemas |

**Two entry paths, one core:**

- **Path A** — Cursor LLM calls MCP tools step-by-step
- **Path B** — Custom agent runs `run_browser_task` end-to-end

---

## 2. Document map

| Document | Path | Purpose |
|----------|------|---------|
| Master plan (this file) | `MASTER_PLAN.md` | Consolidated spec + iteration log |
| Iteration log | `PLAN_ITERATION_LOG.md` | Per-loop changelog |
| Technical spec | `tech-plan/TECHNICAL_PLAN.md` | Engineering detail |
| Flow spec | `flow-logic/FLOW_LOGIC.md` | Operational flows |
| PDF (tech) | `tech-plan/tech-plan.pdf` | Printable architecture |
| PDF (flow) | `flow-logic/browser-flow-framework.pdf` | Printable flows |
| Delivery workflow | `DOCUMENT_DELIVERY_PLAN.md` | LaTeX/PNG/PDF pipeline |
| Security | `SECURITY.md` | Threat model, secrets |
| Test plan | `TEST_PLAN.md` | Unit, MCP, agent, smoke tests |

---

## 3. Target codebase layout

```
D:/Custom_MCP/
  browser/
    __init__.py
    config.py
    session.py
    state.py
    actions.py
  browser_mcp.py
  browser_agent/
    __init__.py
    tools.py
    agent.py
    mcp_server.py
  pyproject.toml
  config.json
  .env
```

---

## 4. MCP tools (Path A)

| Tool | Purpose |
|------|---------|
| `browser_start` | Launch Chromium |
| `browser_close` | Release session |
| `browser_navigate` | Go to URL |
| `browser_get_state` | Indexed DOM + optional screenshot |
| `browser_get_content` | Page text |
| `browser_click` | Click by index |
| `browser_type` | Type into indexed input |
| `browser_scroll` | Scroll page |
| `browser_execute_javascript` | Run JS |

---

## 5. Agent (Path B)

- **LLM:** `ChatLiteLLM(model=os.getenv("LITELLM_MODEL"))`
- **Graph:** `langgraph.prebuilt.create_react_agent`
- **MCP tool:** `run_browser_task(task, model?)`
- **Max steps:** 25 (env `AGENT_MAX_STEPS`)
- **Rules:** get_state before click/type; close in finally

---

## 6. Implementation phases

| Phase | Deliverable | Acceptance |
|-------|-------------|------------|
| 1 | `browser/` core | navigate + get_state works |
| 2 | `browser_mcp.py` | Cursor can start browser |
| 3 | `browser_agent/` | run_browser_task completes search |
| 4 | Config migration | config.json → D:/Custom_MCP |
| 5 | Remove browser-use | pyproject clean |
| 6 | Smoke test | Both paths on same URL |

---

## 7. Non-goals (Phase 1)

- Vision/coordinate clicking
- Persistent browser profiles
- LiteLLM Router / load balancing
- Anti-bot stealth

---

## 8. Iteration policy

Improve this plan recursively until marginal gain < threshold. After each loop:

1. Update `MASTER_PLAN.md` version
2. Append entry to `PLAN_ITERATION_LOG.md`
3. Sync sub-documents if affected
4. Git commit + push

**Current iteration:** 2

---

## 10. Security & testing

See [SECURITY.md](SECURITY.md) and [TEST_PLAN.md](TEST_PLAN.md).

---

## 9. References

- Diagrams: `tech-plan/diagrams/README.md`, `flow-logic/diagrams/README.md`
- Image prompts: `*/diagrams/IMAGE_PROMPTS.md`
- Renewal-Upsell-Advisor doc pattern: `D:/Projects_Main/Renewal-Upsell-Advisor/Document/`
