# Risk Register

**Parent:** [MASTER_PLAN.md](./MASTER_PLAN.md) | **Iteration:** 4

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|------------|--------|------------|
| R1 | LLM chooses wrong element index | Medium | High | Require get_state; system prompt rules |
| R2 | Orphaned Chrome processes | Medium | Medium | finally close; session timeout |
| R3 | Anti-bot blocks automation | Medium | Medium | Phase 2: stealth; document limits |
| R4 | LiteLLM provider outage | Low | Medium | Document fallback models; optional Router Phase 2 |
| R5 | Large DOM → slow get_state | Medium | Low | Cap max_elements=200; cache TTL |
| R6 | JS execute malicious script | Low | High | Trust model; optional disable in prod |
| R7 | Migration breaks Cursor MCP config | Low | High | Keep tool names identical to old server |

---

## Decision: stop plan iteration when

- All ADRs documented
- Security, test, implementation checklists complete
- PDFs built and synced with markdown
- No open gaps in MASTER_PLAN document map
- Additional loops only fix typos or formatting

**Plateau reached at iteration 8** (target).
