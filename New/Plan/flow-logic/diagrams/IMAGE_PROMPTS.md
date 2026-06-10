# AI Image Generation Prompts — Flow Logic Plan

Custom MCP Browser Automation — operational flows. Style:
- White background, navy `#0c3472`, accent `#c8d7eb`
- Sequence diagrams and decision flows, A4 readable
- No watermarks

---

## cbm-flow-dual-path.png
Split diagram with two paths converging on Playwright. Path A left: User → Cursor LLM → MCP low-level tools. Path B right: User → run_browser_task/CLI → LangGraph ReAct Agent → same browser actions. Shared box at bottom: Playwright Chromium. Label: "Path A = Cursor brain, Path B = Custom agent brain".

## cbm-flow-cursor-sequence.png
UML sequence diagram: User, Cursor_LLM, browser_mcp.py, Playwright. Messages: browser_start, browser_navigate google.com, browser_get_state, browser_click, browser_type, browser_close. Return arrows with JSON. Navy lifelines.

## cbm-flow-agent-sequence.png
UML sequence diagram: User, agent_mcp_server, LangGraph_Agent, ChatLiteLLM, browser_tools, Playwright. Loop box max 25 steps with LLM tool_call cycles. Final browser_close and result. Navy and light blue.

## cbm-flow-element-index.png
Decision flowchart: browser_click index=5 → last_state_snapshot → index exists? → map to DOM handle → visible and enabled? → Playwright click → invalidate cache → success. Error branches for not found and not actionable. Navy diamonds.

## cbm-flow-agent-decisions.png
Agent decision loop: Receive task → system prompt rules (get_state before click, minimize steps, close when done) → step N → observe → task complete? → summarize OR stuck same action 3x? → abort → browser_close. Navy flowchart.

## cbm-flow-error-handling.png
Error router from any browser action: success vs classify error type — no session, timeout, element missing, navigation failed, LLM failure — each with recovery hint. One retry branch for timeout. Navy and light blue.

## cbm-flow-provider-switch.png
Simple horizontal flow: Change LITELLM_MODEL in .env → restart MCP → parse provider/model → load API key → agent uses new model → no code change. Three provider icons optional (OpenAI, Anthropic, Ollama).

## cbm-flow-migration.png
Vertical phase timeline: Phase 1 browser core → Phase 2 browser_mcp → Phase 3 browser_agent → Phase 4 config.json → Phase 5 remove browser-use → Phase 6 smoke test → Done deprecate old files. Navy numbered steps.
