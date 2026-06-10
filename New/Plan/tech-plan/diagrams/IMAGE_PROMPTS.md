# AI Image Generation Prompts — Technical Architecture Plan

Custom MCP Browser Automation branding. Style for all images:
- Clean enterprise technical diagram, white background
- Primary color navy `#0c3472`, accent light blue `#c8d7eb`
- Sans-serif labels, readable at A4 print size
- No watermarks

Regenerate any image, copy to `images/`, then run `.\build.ps1`.

---

## Platform & Architecture

### cbm-tech-platform-architecture.png
Four-layer platform stack for Custom MCP Browser Automation. Top to bottom: (1) Presentation — Cursor Chat Agent, CLI Standalone Agent; (2) MCP Server Layer — browser_mcp.py, browser_agent/mcp_server.py; (3) Domain Layer — session.py, state.py, actions.py, agent.py, tools.py; (4) AI Layer — ChatLiteLLM, LangGraph ReAct Agent; (5) Browser Engine — playwright.async_api, Chromium. Arrows showing Cursor to MCP to domain to Playwright. Navy headers, light blue boxes.

### cbm-mcp-tool-data-flow.png
Horizontal MCP tool routing diagram. User in Cursor → Cursor LLM → MCP stdio → tool router diamond branching to browser_start, browser_navigate, browser_get_state, browser_click, browser_type, browser_close → Playwright → JSON TextContent back to Cursor. Navy and light blue.

### cbm-page-state-pipeline.png
Vertical pipeline: browser_get_state request → cache check diamond → page.evaluate DOM scanner → collect interactive elements → assign index 0..N → attach url/title → optional screenshot branch → build JSON → store cache → return. Navy and light blue flowchart.

### cbm-langgraph-react-agent.png
LangGraph ReAct loop state machine. Start run_browser_task → browser_start → loop diamond step < max → ChatLiteLLM invoke → tool_calls diamond with branches get_state, navigate, click, type, scroll, finish → loop back or max_steps → browser_close in finally → end. Navy nodes, light blue highlights on LLM node.

### cbm-litellm-providers.png
Hub diagram: browser_agent/agent.py → ChatLiteLLM → litellm.completion → router diamond → OpenAI, Anthropic, Ollama, Groq. .env API keys feeding litellm. browser_config.example.json feeding ChatLiteLLM. Navy and light blue.

### cbm-session-lifecycle.png
State diagram: Idle → Starting → Active (self-loop for actions) → Closing → Idle. Error path from Starting to Idle. Labels: browser_start, browser_close, session_timeout, agent_finally. Navy state boxes.

### cbm-package-layout.png
Tree diagram of Custom_MCP folder: browser/ (session, state, actions, config), browser_mcp.py, browser_agent/ (tools, agent, mcp_server), config.json, pyproject.toml. Folder icons, navy labels.

### cbm-mcp-deployment.png
Deployment wiring: Cursor IDE (MCP Settings, Agent Chat) → config.json → uv processes browser_mcp.py and browser_agent/mcp_server.py ← .env. stdio MCP arrows from Chat to processes. Navy and light blue.
