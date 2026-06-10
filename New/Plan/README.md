# Custom MCP Browser Automation — Plan Documentation

**Start here:** [MASTER_PLAN.md](MASTER_PLAN.md) — single source of truth (iteration 8, complete)

## Document index

| Doc | Description |
|-----|-------------|
| [MASTER_PLAN.md](MASTER_PLAN.md) | Consolidated vision, phases, document map |
| [PLAN_ITERATION_LOG.md](PLAN_ITERATION_LOG.md) | Git loop changelog |
| [DOCUMENT_DELIVERY_PLAN.md](DOCUMENT_DELIVERY_PLAN.md) | LaTeX/PDF pipeline |
| [SECURITY.md](SECURITY.md) | Threat model |
| [TEST_PLAN.md](TEST_PLAN.md) | Test strategy |
| [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) | File-by-file build list |
| [RISK_REGISTER.md](RISK_REGISTER.md) | Risk matrix |
| [adr/](adr/README.md) | Architecture decision records |
| [tech-plan/TECHNICAL_PLAN.md](tech-plan/TECHNICAL_PLAN.md) | Full technical spec |
| [tech-plan/tech-plan.pdf](tech-plan/tech-plan.pdf) | Technical PDF |
| [flow-logic/FLOW_LOGIC.md](flow-logic/FLOW_LOGIC.md) | Flow spec |
| [flow-logic/browser-flow-framework.pdf](flow-logic/browser-flow-framework.pdf) | Flow PDF |

## Build PDFs

```powershell
cd D:\Custom_MCP\New\Plan\tech-plan; .\build.ps1
cd D:\Custom_MCP\New\Plan\flow-logic; .\build.ps1
```

## Plan iteration status

**Complete at loop 8.** Further loops = code implementation phase, not plan docs.

See [PLAN_ITERATION_LOG.md](PLAN_ITERATION_LOG.md) for commit history.

## Code implementation (next)

Follow [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) after plan approval.
