# LaTeX Source Plan — browser-flow-framework.tex

Full section map for the Flow & Operations Framework PDF.  
When executing the document plan, this becomes `flow-logic/browser-flow-framework.tex`.

Uses `\capblock` (business value) instead of `\techblock` — same pattern as  
`Renewal-Upsell-Advisor/Document/revenue-navigator-framework/revenue-navigator-framework.tex`.

---

## Cover

```
Custom MCP Browser Automation
Flow & Operations Framework
Cursor MCP Tools · Custom LangChain Agent · Multi-LLM
For Implementation Review
\today
Operational flows for dual-path browser automation
```

---

## Section 1: Executive Summary

**Figure:** `\docfig{images/cbm-flow-dual-path.png}{Dual-path overview}{fig:dualpath}`

- Path A: Cursor orchestrates via MCP tools
- Path B: Custom agent via LangChain + LiteLLM
- Shared Playwright core

**\capblock:** Why two paths — flexibility for interactive vs automated tasks

---

## Section 2: Path A — Cursor Orchestrated Flow

**Figure:** `\docfiglandscape{images/cbm-flow-cursor-sequence.png}{Cursor MCP sequence diagram}{fig:cursorseq}`

### 2.1 User story
### 2.2 Step-by-step sequence (enumerate)
### 2.3 Example conversation table (Step | Action | MCP tool)

**\capblock:** Best for interactive control and visibility

---

## Section 3: Path B — Custom Agent Flow

**Figure:** `\docfiglandscape{images/cbm-flow-agent-sequence.png}{Agent sequence diagram}{fig:agentseq}`

### 3.1 User story
### 3.2 run_browser_task flow
### 3.3 Agent loop (reference fig:agentdecisions)

**\capblock:** Best for one-shot automation and provider switching

---

## Section 4: Element Index Resolution

**Figure:** `\docfig{images/cbm-flow-element-index.png}{Index resolution flowchart}{fig:index}`

- Snapshot model
- Error: refresh state
- Rule: indexes not stable across navigation

---

## Section 5: Agent Decision Rules

**Figure:** `\docfig{images/cbm-flow-agent-decisions.png}{Agent decision loop}{fig:agentdecisions}`

**longtable:** Rule | Rationale

System prompt rules from FLOW_LOGIC.md §3

---

## Section 6: Error Handling & Recovery

**Figure:** `\docfig{images/cbm-flow-error-handling.png}{Error routing}{fig:errors}`

**longtable:** Error code | Message | Recovery

---

## Section 7: Multi-Provider Switch (LiteLLM)

**Figure:** `\docfig{images/cbm-flow-provider-switch.png}{Provider switch flow}{fig:provider}`

- Change LITELLM_MODEL → restart MCP → no code change
- Provider examples table

---

## Section 8: Migration from browser-use

**Figure:** `\docfig{images/cbm-flow-migration.png}{Six-phase migration}{fig:migration}`

What gets removed vs what stays (tool names, MCP transport)

---

## Section 9: Typical Use Cases

Three use cases from FLOW_LOGIC.md §8 (no figure — text + capblocks)

1. Research in Cursor (Path A)
2. One-shot automation (Path B)
3. Multi-provider testing (Path B)

---

## Required images checklist (build.ps1 validates)

1. cbm-flow-dual-path.png
2. cbm-flow-cursor-sequence.png
3. cbm-flow-agent-sequence.png
4. cbm-flow-element-index.png
5. cbm-flow-agent-decisions.png
6. cbm-flow-error-handling.png
7. cbm-flow-provider-switch.png
8. cbm-flow-migration.png

---

## IMAGE_PROMPTS cross-reference

All prompts are in `flow-logic/diagrams/IMAGE_PROMPTS.md` — copy verbatim into LLM image generator.

Style line (include in every generation):
> Clean enterprise technical diagram, white background, navy #0c3472 headers, light blue #c8d7eb boxes, sans-serif labels, A4 readable, no watermarks.
