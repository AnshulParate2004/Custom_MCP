# Diagram Source Specifications — Technical Plan

Mermaid source blocks for maintainability. Regenerate PNGs via `IMAGE_PROMPTS.md` when diagrams change.

Brand colors: navy `#0c3472`, accent `#c8d7eb`.

---

## 1. Platform Architecture (four layers)

```mermaid
flowchart TB
    subgraph presentation [Presentation Layer]
        CursorIDE[Cursor_Chat_Agent]
        CLI[CLI_Standalone_Agent]
    end
    subgraph mcpLayer [MCP Server Layer]
        BrowserMCP[browser_mcp.py]
        AgentMCP[browser_agent/mcp_server.py]
    end
    subgraph domainLayer [Domain Layer]
        Session[browser/session.py]
        State[browser/state.py]
        Actions[browser/actions.py]
        AgentCore[browser_agent/agent.py]
        LCTools[browser_agent/tools.py]
    end
    subgraph aiLayer [AI Layer — agent path only]
        LiteLLM[ChatLiteLLM_langchain_litellm]
        LangGraph[LangGraph_ReAct_Agent]
    end
    subgraph engineLayer [Browser Engine]
        Playwright[playwright.async_api]
        Chromium[Chromium_Browser]
    end
    CursorIDE --> BrowserMCP
    CursorIDE --> AgentMCP
    CLI --> AgentCore
    BrowserMCP --> Session
    BrowserMCP --> State
    BrowserMCP --> Actions
    AgentMCP --> AgentCore
    AgentCore --> LangGraph
    LangGraph --> LiteLLM
    LangGraph --> LCTools
    LCTools --> Actions
    Session --> Playwright
    Actions --> Session
    State --> Session
    Playwright --> Chromium
```

---

## 2. MCP Tool Data Flow

```mermaid
flowchart LR
    User[User_in_Cursor] --> CursorLLM[Cursor_Built_in_LLM]
    CursorLLM --> MCP[MCP_Protocol_stdio]
    MCP --> ToolRouter{tool_name}
    ToolRouter -->|browser_start| Start[session.start]
    ToolRouter -->|browser_navigate| Nav[actions.navigate]
    ToolRouter -->|browser_get_state| State[state.extract_elements]
    ToolRouter -->|browser_click| Click[actions.click_index]
    ToolRouter -->|browser_type| Type[actions.type_text]
    ToolRouter -->|browser_close| Close[session.close]
    Start --> PW[Playwright]
    Nav --> PW
    State --> PW
    Click --> PW
    Type --> PW
    Close --> PW
    PW --> Result[JSON_TextContent_to_Cursor]
    Result --> CursorLLM
```

---

## 3. Page State Extraction Pipeline

```mermaid
flowchart TD
    Request[browser_get_state] --> CacheCheck{cache_valid?}
    CacheCheck -->|yes| ReturnCache[return_cached_JSON]
    CacheCheck -->|no| GetPage[session.get_page]
    GetPage --> RunJS[page.evaluate_DOM_scanner]
    RunJS --> Collect[collect_interactive_elements]
    Collect --> Index[assign_index_0_to_N]
    Index --> Meta[attach_url_title]
    Meta --> Screenshot{include_screenshot?}
    Screenshot -->|yes| Shot[page.screenshot_base64]
    Screenshot -->|no| BuildJSON[build_state_JSON]
    Shot --> BuildJSON
    BuildJSON --> StoreCache[store_in_state_cache]
    StoreCache --> ReturnFresh[return_JSON]
```

---

## 4. LangGraph ReAct Agent Loop

```mermaid
flowchart TD
    Start([run_browser_task]) --> Init[browser_start]
    Init --> Loop{step_less_than_max?}
    Loop -->|yes| LLM[ChatLiteLLM.invoke_with_tools]
    LLM --> Decision{tool_calls?}
    Decision -->|browser_get_state| Observe[state.extract]
    Decision -->|browser_navigate| Nav[actions.navigate]
    Decision -->|browser_click| Click[actions.click]
    Decision -->|browser_type| Type[actions.type]
    Decision -->|browser_scroll| Scroll[actions.scroll]
    Decision -->|finish| Done[compile_result]
    Decision -->|unknown| Error[return_error]
    Observe --> Loop
    Nav --> Loop
    Click --> Loop
    Type --> Loop
    Scroll --> Loop
    Loop -->|no| Timeout[max_steps_reached]
    Done --> Finally[browser_close_in_finally]
    Timeout --> Finally
    Error --> Finally
    Finally --> End([return_to_MCP_or_CLI])
```

---

## 5. LiteLLM Multi-Provider Router

```mermaid
flowchart TB
    Agent[browser_agent/agent.py] --> ChatLiteLLM[ChatLiteLLM]
    ChatLiteLLM --> LiteLLMCore[litellm.completion]
    LiteLLMCore --> Router{model_string}
    Router -->|openai/gpt-4o| OpenAI[OpenAI_API]
    Router -->|anthropic/claude-*| Anthropic[Anthropic_API]
    Router -->|ollama/llama3| Ollama[Local_Ollama]
    Router -->|groq/llama-*| Groq[Groq_API]
    Env[.env_API_keys] --> LiteLLMCore
    Config[browser_config.example.json] --> ChatLiteLLM
```

---

## 6. Session Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Starting: browser_start
    Starting --> Active: Playwright_ready
    Active --> Active: navigate_click_type_scroll
    Active --> Active: get_state_cached
    Active --> Closing: browser_close
    Active --> Closing: session_timeout
    Active --> Closing: agent_finally_block
    Closing --> Idle: resources_released
    Starting --> Error: launch_failed
    Error --> Idle: cleanup
```

---

## 7. Package Layout

```mermaid
flowchart TB
    Root[Custom_MCP/]
    Root --> BrowserPkg[browser/]
    Root --> BrowserMCP[browser_mcp.py]
    Root --> AgentPkg[browser_agent/]
    Root --> Config[config.json]
    Root --> PyProject[pyproject.toml]
    BrowserPkg --> SessionPy[session.py]
    BrowserPkg --> StatePy[state.py]
    BrowserPkg --> ActionsPy[actions.py]
    BrowserPkg --> ConfigPy[config.py]
    AgentPkg --> ToolsPy[tools.py]
    AgentPkg --> AgentPy[agent.py]
    AgentPkg --> McpServerPy[mcp_server.py]
```

---

## 8. Deployment / MCP Wiring

```mermaid
flowchart LR
    subgraph cursor [Cursor IDE]
        Settings[MCP_Settings]
        Chat[Agent_Chat]
    end
    subgraph processes [Local Processes via uv]
        P1[browser_mcp.py]
        P2[browser_agent/mcp_server.py]
    end
    subgraph env [Environment]
        DotEnv[.env]
        MCPJson[config.json]
    end
    Settings --> MCPJson
    MCPJson --> P1
    MCPJson --> P2
    DotEnv --> P1
    DotEnv --> P2
    Chat -->|stdio_MCP| P1
    Chat -->|stdio_MCP| P2
```

---

## PNG target files

| Mermaid / Concept | PNG File |
|-------------------|----------|
| Platform Architecture | `images/cbm-tech-platform-architecture.png` |
| MCP Tool Data Flow | `images/cbm-mcp-tool-data-flow.png` |
| Page State Extraction | `images/cbm-page-state-pipeline.png` |
| LangGraph ReAct Loop | `images/cbm-langgraph-react-agent.png` |
| LiteLLM Multi-Provider | `images/cbm-litellm-providers.png` |
| Session Lifecycle | `images/cbm-session-lifecycle.png` |
| Package Layout | `images/cbm-package-layout.png` |
| MCP Deployment Wiring | `images/cbm-mcp-deployment.png` |
