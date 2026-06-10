# LaTeX Source Plan — tech-plan.tex

Full section-by-section content map for the Technical Architecture PDF.  
When executing the document plan, this becomes `tech-plan/tech-plan.tex`.

---

## Preamble (copy from Renewal-Upsell-Advisor pattern)

- `\documentclass[11pt,a4paper]{article}`
- Packages: geometry, graphicx, adjustbox, hyperref, fancyhdr, xcolor, tikz, float, listings, booktabs, longtable
- Colors: `brandblue` #0c3472, `brandlight` #c8d7eb, `textgray` #475569
- Macros: `\makecover`, `\docfig`, `\docfigsafe`, `\docfiglandscape`, `\techblock`

## Cover

```
Custom MCP Browser Automation
Technical Architecture Plan
Production Engineering Specification
Playwright · MCP · LangChain · LiteLLM · LangGraph
Confidential — Engineering Review
\today
Greenfield design replacing browser-use with owned stack
```

---

## Section 1: Executive Technical Summary

**Content from:** TECHNICAL_PLAN.md §1

- Goal: owned Playwright + MCP + LangChain stack
- Stack table (Playwright, MCP, LangGraph, LiteLLM, dotenv)
- NFR table (cold start, cache, max steps, no vendor lock-in)

---

## Section 2: System Context

**Content from:** TECHNICAL_PLAN.md §2

- Current files to replace (Browser_Agent.py, Browser_Automation_Fast.py)
- Target consumers: Cursor, custom agent MCP, CLI

---

## Section 3: Platform Architecture

**Figure:** `\docfiglandscape{images/cbm-tech-platform-architecture.png}{...}{fig:platform}`

Six-layer narrative:
1. Presentation (Cursor, CLI)
2. MCP servers
3. Domain (session, state, actions)
4. AI (LangGraph, ChatLiteLLM) — agent path only
5. Browser engine (Playwright, Chromium)

---

## Section 4: MCP Tool Data Flow

**Figure:** `\docfig{images/cbm-mcp-tool-data-flow.png}{...}{fig:mcpflow}`

- User → Cursor LLM → MCP stdio → tool router → Playwright → JSON back
- Emphasis: no LLM inside browser_mcp.py

---

## Section 5: Module Decomposition

**Figure:** `\docfig{images/cbm-package-layout.png}{...}{fig:package}`

**longtable:** Module | Responsibility | File

| Module | Responsibility | File |
|--------|----------------|------|
| Session | Playwright lifecycle | session.py |
| State | Indexed DOM extraction | state.py |
| Actions | navigate, click, type | actions.py |
| MCP server | Cursor tools | browser_mcp.py |
| Agent tools | LangChain wrappers | tools.py |
| Agent loop | ReAct | agent.py |
| Agent MCP | run_browser_task | mcp_server.py |

**lstlisting:** target package tree under Custom_MCP/

---

## Section 6: Browser Core Specification

**Figure:** `\docfig{images/cbm-page-state-pipeline.png}{...}{fig:statepipeline}`

### 6.1 session.py — methods table
### 6.2 state.py — algorithm + JSON output example (lstlisting)
### 6.3 actions.py — Playwright mapping table

---

## Section 7: MCP Server Tools

**Figure:** `\docfig{images/cbm-mcp-deployment.png}{...}{fig:deployment}`

**longtable:** Tool name | Input schema | Behavior

All 9 tools: browser_start through browser_execute_javascript

Include `\techblock` for config.json wiring example (lstlisting from schemas)

---

## Section 8: Custom Agent Architecture

**Figures:**
- `\docfig{images/cbm-langgraph-react-agent.png}{LangGraph ReAct loop}{fig:react}`
- `\docfig{images/cbm-litellm-providers.png}{LiteLLM multi-provider hub}{fig:litellm}`

- LangChain tools
- create_react_agent
- System prompt rules (itemize)
- run_browser_task MCP tool (lstlisting Python snippet)

---

## Section 9: Session Lifecycle

**Figure:** `\docfig{images/cbm-session-lifecycle.png}{...}{fig:session}`

State diagram narrative: Idle → Active → Closing

---

## Section 10: Dependencies & Environment

**Remove:** browser-use

**Add:** playwright, langchain, langgraph, langchain-litellm, litellm

**lstlisting:** .env example

**Post-install:** `python -m playwright install chromium`

---

## Section 11: Implementation Phases

**longtable:** Phase | Deliverable | Test criteria

Phases 1–6 from TECHNICAL_PLAN.md

---

## Appendix A: Configuration Schemas

Reference files:
- `schemas/browser_config.example.json`
- `schemas/mcp_config.example.json`
- `schemas/litellm_config.example.json`

Include abbreviated lstlisting excerpts.

---

## Appendix B: Out of Scope (Phase 1)

- Vision clicking
- Persistent profiles
- LiteLLM Router
- Anti-bot stealth

---

## Required images checklist (build.ps1 validates)

1. cbm-tech-platform-architecture.png
2. cbm-mcp-tool-data-flow.png
3. cbm-page-state-pipeline.png
4. cbm-langgraph-react-agent.png
5. cbm-litellm-providers.png
6. cbm-session-lifecycle.png
7. cbm-package-layout.png
8. cbm-mcp-deployment.png
