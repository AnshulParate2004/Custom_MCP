# Document Delivery Plan — LaTeX PDF + LLM-Generated Diagrams

**Project:** Custom MCP Browser Automation  
**Deliverable:** Two PDF documents (plan only — no code implementation)  
**Reference:** `D:\Projects_Main\Renewal-Upsell-Advisor\Document\`

---

## 1. What you will receive

| PDF | LaTeX source | Purpose |
|-----|--------------|---------|
| **Custom MCP Technical Architecture Plan.pdf** | `tech-plan/tech-plan.tex` | Engineering spec — layers, modules, MCP tools, LiteLLM, dependencies |
| **Custom MCP Browser Flow Framework.pdf** | `flow-logic/browser-flow-framework.tex` | Operational flows — Path A (Cursor) vs Path B (custom agent) |

Same production pipeline as Renewal-Upsell-Advisor:

```
Mermaid (source of truth)
    ↓
IMAGE_PROMPTS.md (LLM prompts)
    ↓
GenerateImage / ChatGPT / DALL·E → PNG in images/
    ↓
tech-plan.tex + browser-flow-framework.tex
    ↓
build.ps1 → pdflatex × 2
    ↓
PDF
```

---

## 2. Folder structure (final target)

```
D:\Custom_MCP\New\Plan\
├── README.md
├── DOCUMENT_DELIVERY_PLAN.md          ← this file
├── tech-plan/
│   ├── tech-plan.tex                  ← TO CREATE (Agent mode)
│   ├── tech-plan.pdf                  ← OUTPUT
│   ├── build.ps1                      ← TO CREATE
│   ├── TECHNICAL_PLAN.md              ← markdown draft (done)
│   ├── diagrams/
│   │   ├── README.md                  ← Mermaid sources (done)
│   │   └── IMAGE_PROMPTS.md           ← LLM prompts (done)
│   ├── images/                        ← 8 PNG files from LLM
│   │   ├── cbm-tech-platform-architecture.png
│   │   ├── cbm-mcp-tool-data-flow.png
│   │   ├── cbm-page-state-pipeline.png
│   │   ├── cbm-langgraph-react-agent.png
│   │   ├── cbm-litellm-providers.png
│   │   ├── cbm-session-lifecycle.png
│   │   ├── cbm-package-layout.png
│   │   └── cbm-mcp-deployment.png
│   └── schemas/
│       ├── browser_config.example.json
│       ├── mcp_config.example.json
│       └── litellm_config.example.json
└── flow-logic/
    ├── browser-flow-framework.tex     ← TO CREATE (Agent mode)
    ├── browser-flow-framework.pdf     ← OUTPUT
    ├── build.ps1                      ← TO CREATE
    ├── FLOW_LOGIC.md                  ← markdown draft (done)
    ├── diagrams/
    │   ├── README.md                  ← done
    │   └── IMAGE_PROMPTS.md           ← done
    └── images/                        ← 8 PNG files from LLM
        ├── cbm-flow-dual-path.png
        ├── cbm-flow-cursor-sequence.png
        ├── cbm-flow-agent-sequence.png
        ├── cbm-flow-element-index.png
        ├── cbm-flow-agent-decisions.png
        ├── cbm-flow-error-handling.png
        ├── cbm-flow-provider-switch.png
        └── cbm-flow-migration.png
```

---

## 3. Step-by-step delivery workflow

### Phase A — Diagrams (LLM image generation)

For **each** PNG listed in `IMAGE_PROMPTS.md`:

1. Open `tech-plan/diagrams/IMAGE_PROMPTS.md` or `flow-logic/diagrams/IMAGE_PROMPTS.md`
2. Copy the prompt block for that filename
3. Generate image via:
   - **Cursor GenerateImage tool**, or
   - ChatGPT / DALL·E / Gemini with the exact prompt text
4. Save PNG to the matching `images/` folder with **exact filename**
5. Verify: white background, navy `#0c3472`, accent `#c8d7eb`, readable labels at A4 size

**Total images:** 16 (8 technical + 8 flow)

### Phase B — LaTeX source files

Create two `.tex` files mirroring Renewal-Upsell-Advisor styling:

- Same preamble: `geometry`, `graphicx`, `hyperref`, `fancyhdr`, brand colors
- `\makecover` with project title
- `\tableofcontents`
- `\docfig` / `\docfigsafe` / `\docfiglandscape` macros for figures
- `\techblock` for implementation notes (tech plan)
- `\capblock` for business/flow value (flow framework)

Content source: merge `TECHNICAL_PLAN.md` + `FLOW_LOGIC.md` into LaTeX sections.

### Phase C — JSON schemas

Copy from `schemas/SCHEMAS.md` into three `.json` files (referenced in LaTeX appendices).

### Phase D — Build PDFs

```powershell
cd D:\Custom_MCP\New\Plan\tech-plan
.\build.ps1
# Output: tech-plan.pdf

cd D:\Custom_MCP\New\Plan\flow-logic
.\build.ps1
# Output: browser-flow-framework.pdf
```

**Prerequisite:** `pdflatex` on PATH (MiKTeX or TeX Live).

---

## 4. LaTeX document outlines

### 4.1 `tech-plan.tex` — sections

| § | Title | Key figure |
|---|-------|------------|
| 1 | Executive Technical Summary | — |
| 2 | System Context (replace browser-use) | — |
| 3 | Platform Architecture | Fig: platform-architecture |
| 4 | MCP Tool Data Flow | Fig: mcp-tool-data-flow |
| 5 | Service / Module Decomposition | Fig: package-layout |
| 6 | Browser Core (`browser/`) | Fig: page-state-pipeline |
| 7 | MCP Server Specification | Fig: mcp-deployment |
| 8 | Custom Agent (LangGraph + LiteLLM) | Fig: langgraph-react, litellm-providers |
| 9 | Session Lifecycle | Fig: session-lifecycle |
| 10 | Dependencies & Environment | — |
| 11 | Implementation Phases | — |
| A | Schema references | listings from JSON |

**Cover title:** Custom MCP Browser Automation — Technical Architecture Plan  
**Subtitle:** Playwright · MCP · LangChain · LiteLLM · LangGraph

### 4.2 `browser-flow-framework.tex` — sections

| § | Title | Key figure |
|---|-------|------------|
| 1 | Executive Summary (dual-path model) | Fig: dual-path |
| 2 | Path A — Cursor Orchestrated Flow | Fig: cursor-sequence |
| 3 | Path B — Custom Agent Flow | Fig: agent-sequence |
| 4 | Element Index Resolution | Fig: element-index |
| 5 | Agent Decision Rules | Fig: agent-decisions |
| 6 | Error Handling & Recovery | Fig: error-handling |
| 7 | Multi-Provider Switch (LiteLLM) | Fig: provider-switch |
| 8 | Migration from browser-use | Fig: migration |
| 9 | Typical Use Cases | — |

**Cover title:** Custom MCP Browser Automation — Flow & Operations Framework  
**Subtitle:** Cursor MCP Tools · Custom LangChain Agent · Multi-LLM

---

## 5. `build.ps1` specification

Identical pattern to Renewal-Upsell-Advisor `Document/tech-plan/build.ps1`:

```powershell
$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Validate all required PNGs exist before compiling
$requiredImages = @(
    "images/cbm-tech-platform-architecture.png",
    # ... full list per document
)

foreach ($img in $requiredImages) {
    if (-not (Test-Path $img)) {
        Write-Host "ERROR: Missing $img - regenerate via diagrams/IMAGE_PROMPTS.md"
        exit 1
    }
}

pdflatex -interaction=nonstopmode tech-plan.tex
pdflatex -interaction=nonstopmode tech-plan.tex

if (Test-Path "tech-plan.pdf") {
    Write-Host "Success: tech-plan.pdf"
} else { exit 1 }
```

---

## 6. Branding (match Renewal-Upsell-Advisor)

| Element | Value |
|---------|-------|
| Primary navy | `#0c3472` |
| Accent light blue | `#c8d7eb` |
| Body text gray | `#475569` |
| Font | Helvetica (`helvet`) |
| Cover badge | "Confidential — Engineering Review" (tech) / "For Implementation Review" (flow) |
| Figure style | Enterprise technical diagram, white background, no watermarks |

---

## 7. Current status vs remaining work

| Item | Status |
|------|--------|
| Mermaid diagram sources | **Done** |
| LLM image prompts | **Done** |
| Markdown drafts | **Done** |
| Config schema content | **Done** |
| PNG images (16) | **Done** |
| `tech-plan.tex` | **Done** |
| `browser-flow-framework.tex` | **Done** |
| `build.ps1` (×2) | **Done** |
| `.json` schema files | **Done** |
| **PDF output** | **Done** |
| MASTER_PLAN + ADRs + checklists | **Done** (loops 1–8) |

**Next phase:** Code implementation per [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)

---

## 8. How to execute this plan (when approved)

Say: **"execute the document plan"** or **"switch to agent mode and build the PDFs"**

Agent will:

1. Generate all 16 PNGs using `IMAGE_PROMPTS.md` prompts
2. Write `tech-plan.tex` and `browser-flow-framework.tex` (full LaTeX, Renewal-Upsell style)
3. Write `build.ps1` for each folder
4. Write `.json` schema files
5. Run `pdflatex` and deliver both PDFs

**No browser automation code** will be written — documentation only.

---

## 9. Comparison to Renewal-Upsell-Advisor

| Renewal-Upsell-Advisor | Custom MCP (this plan) |
|------------------------|-------------------------|
| `Document/tech-plan/tech-plan.tex` | `Plan/tech-plan/tech-plan.tex` |
| `Document/revenue-navigator-framework/*.tex` | `Plan/flow-logic/browser-flow-framework.tex` |
| `diagrams/IMAGE_PROMPTS.md` | Same pattern, `cbm-*` prefix |
| `diagrams/README.md` (Mermaid) | Same pattern |
| `build.ps1` + `images/*.png` | Same pattern |
| `schemas/postgres.ddl`, etc. | `schemas/*.json` for browser/MCP/LiteLLM |
