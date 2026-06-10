# Custom MCP Browser Automation — Plan Documentation

Engineering and flow-logic specifications for replacing **browser-use** with an owned **Playwright + MCP + LangChain + LiteLLM** stack.

**Master delivery plan:** [DOCUMENT_DELIVERY_PLAN.md](DOCUMENT_DELIVERY_PLAN.md) — LaTeX + LLM images + PDF workflow (same as Renewal-Upsell-Advisor).

## Folder layout

```
Plan/
├── README.md
├── DOCUMENT_DELIVERY_PLAN.md          ← PDF delivery workflow (READ THIS)
├── tech-plan/
│   ├── TECHNICAL_PLAN.md              ← markdown draft → tech-plan.tex
│   ├── LATEX_PLAN.md                  ← section map for LaTeX/PDF
│   ├── tech-plan.tex                  ← PENDING (Agent mode)
│   ├── tech-plan.pdf                  ← PENDING (after build)
│   ├── build.ps1                      ← PENDING
│   ├── diagrams/
│   │   ├── README.md                  ← 8 Mermaid diagrams
│   │   └── IMAGE_PROMPTS.md           ← LLM prompts → PNG
│   ├── images/                        ← 8 PNGs from LLM (PENDING)
│   └── schemas/
│       └── SCHEMAS.md                 ← JSON examples
└── flow-logic/
    ├── FLOW_LOGIC.md                  ← markdown draft → browser-flow-framework.tex
    ├── LATEX_PLAN.md                  ← section map for LaTeX/PDF
    ├── browser-flow-framework.tex     ← PENDING
    ├── browser-flow-framework.pdf     ← PENDING
    ├── build.ps1                      ← PENDING
    ├── diagrams/
    │   ├── README.md
    │   └── IMAGE_PROMPTS.md
    └── images/                        ← 8 PNGs from LLM (PENDING)
```

## PDF production pipeline (same as Renewal-Upsell-Advisor)

1. **Mermaid** — maintain logic in `diagrams/README.md`
2. **LLM prompts** — `diagrams/IMAGE_PROMPTS.md` → generate 16 PNGs
3. **LaTeX** — `tech-plan.tex` + `browser-flow-framework.tex` (see `LATEX_PLAN.md` in each folder)
4. **Build** — `.\build.ps1` → `pdflatex` × 2 → PDF

```powershell
cd D:\Custom_MCP\New\Plan\tech-plan
.\build.ps1    # → tech-plan.pdf

cd D:\Custom_MCP\New\Plan\flow-logic
.\build.ps1    # → browser-flow-framework.pdf
```

**Prerequisite:** MiKTeX or TeX Live (`pdflatex` on PATH)

## Status

| Deliverable | Status |
|-------------|--------|
| Mermaid + IMAGE_PROMPTS | Done |
| TECHNICAL_PLAN.md + FLOW_LOGIC.md | Done |
| LATEX_PLAN.md (both) | Done |
| DOCUMENT_DELIVERY_PLAN.md | Done |
| 16 PNG images (LLM-generated) | **Done** |
| tech-plan.tex + browser-flow-framework.tex | **Done** |
| build.ps1 (both) | **Done** |
| tech-plan.pdf + browser-flow-framework.pdf | **Done** |
| JSON schema files | **Done** |

## Related code (target implementation root)

`D:\Custom_MCP\` — existing MCP servers to be migrated:

| Current file | Replaced by |
|--------------|-------------|
| `Browser_Automation_Fast.py` (browser-use) | `browser_mcp.py` (Playwright) |
| `Browser_Agent.py` (ChatBrowserUse API) | `browser_agent/` (LangChain + LiteLLM) |
