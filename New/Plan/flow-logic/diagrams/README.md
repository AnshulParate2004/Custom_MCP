# Diagram Source Specifications — Flow Logic

Operational and business-flow diagrams for how users and agents interact with the browser system.

---

## 1. Dual-Path Overview (who decides what)

```mermaid
flowchart TB
    subgraph pathA [Path A — Cursor Orchestrates]
        UserA[User_types_natural_language_in_Cursor]
        CursorModel[Cursor_LLM]
        LowLevelTools[MCP_low_level_tools]
        UserA --> CursorModel
        CursorModel --> LowLevelTools
    end
    subgraph pathB [Path B — Custom Agent Orchestrates]
        UserB[User_calls_run_browser_task_or_CLI]
        CustomAgent[LangGraph_ReAct_Agent]
        AgentTools[Same_browser_actions_as_Path_A]
        UserB --> CustomAgent
        CustomAgent --> AgentTools
    end
    subgraph shared [Shared Browser Core]
        Playwright[Playwright_Chromium]
    end
    LowLevelTools --> Playwright
    AgentTools --> Playwright
```

**Rule:** Path A = Cursor's model is the brain. Path B = your LiteLLM-backed agent is the brain. Both use identical browser primitives.

---

## 2. Path A — Cursor Step-by-Step Flow

```mermaid
sequenceDiagram
    participant U as User
    participant C as Cursor_LLM
    participant M as browser_mcp.py
    participant B as Playwright

    U->>C: Go to google.com and search Playwright
    C->>M: browser_start
    M->>B: launch chromium
    M-->>C: success
    C->>M: browser_navigate url=google.com
    M->>B: page.goto
    M-->>C: success
    C->>M: browser_get_state
    M->>B: DOM scan + index elements
    M-->>C: elements list with indices
    C->>M: browser_click index=search_box
    M->>B: click indexed element
    C->>M: browser_type index=search_box text=Playwright
    M->>B: fill/type
    C->>M: browser_close
    M->>B: close session
    C-->>U: Task complete summary
```

---

## 3. Path B — Custom Agent Task Flow

```mermaid
sequenceDiagram
    participant U as User
    participant M as agent_mcp_server
    participant A as LangGraph_Agent
    participant L as ChatLiteLLM
    participant T as browser_tools
    participant B as Playwright

    U->>M: run_browser_task task=Search Google for Playwright tutorials
    M->>A: run_agent task model
    A->>T: browser_start
    T->>B: launch
    loop max 25 steps
        A->>L: messages + tool schemas
        L-->>A: tool_call browser_get_state
        A->>T: browser_get_state
        T->>B: DOM scan
        T-->>A: page state JSON
        A->>L: updated context
        L-->>A: tool_call browser_click browser_type
        A->>T: execute actions
        T->>B: interact
    end
    A->>T: browser_close
    A-->>M: final result + step history
    M-->>U: task outcome
```

---

## 4. Element Index Resolution Flow

```mermaid
flowchart TD
    ClickReq[browser_click index=5] --> Snapshot[last_state_snapshot]
    Snapshot --> Lookup{index 5 exists?}
    Lookup -->|no| Err404[error element not found — refresh state]
    Lookup -->|yes| Resolve[map index to DOM selector or handle]
    Resolve --> Visible{element visible and enabled?}
    Visible -->|no| ErrHidden[error not actionable]
    Visible -->|yes| PWClick[Playwright click or fill]
    PWClick --> Invalidate[invalidate state cache]
    Invalidate --> Success[return success JSON]
```

---

## 5. Agent Decision Loop (flow logic)

```mermaid
flowchart TD
    Task[Receive task string] --> Prompt[Load system prompt with tool rules]
    Prompt --> Rule1[Rule: always get_state before click or type]
    Rule1 --> Rule2[Rule: prefer smallest number of steps]
    Rule2 --> Rule3[Rule: call browser_close when done]
    Rule3 --> Step[Agent step N]
    Step --> Observe[Observe tool result or page state]
    Observe --> Goal{task complete?}
    Goal -->|yes| Summarize[summarize for user]
    Goal -->|no| Stuck{same action repeated 3x?}
    Stuck -->|yes| Abort[abort with error]
    Stuck -->|no| Step
    Summarize --> Close[browser_close]
    Abort --> Close
```

---

## 6. Error Handling Flow

```mermaid
flowchart TD
    Action[Any browser action] --> Try{success?}
    Try -->|yes| OK[return success JSON]
    Try -->|no| Classify{error type}
    Classify -->|no session| StartHint[error: call browser_start first]
    Classify -->|timeout| Retry[retry once with longer timeout]
    Classify -->|element missing| Refresh[error: call browser_get_state again]
    Classify -->|navigation failed| NavErr[error: check URL or network]
    Classify -->|LLM failure| LLMErr[error: check API key and model]
    Retry --> Try
```

---

## 7. Provider Switch Flow (LiteLLM)

```mermaid
flowchart LR
    User[Change LITELLM_MODEL in .env] --> Reload[Restart MCP process or CLI]
    Reload --> Parse[Parse provider/model string]
    Parse --> Keys[Load matching API key from env]
    Keys --> Agent[Agent uses new model on next task]
    Agent --> NoCodeChange[No code changes required]
```

---

## 8. Migration Flow (browser-use → owned stack)

```mermaid
flowchart TD
    Phase1[Phase 1: browser core + Playwright] --> Phase2[Phase 2: browser_mcp.py]
    Phase2 --> Phase3[Phase 3: browser_agent LangChain]
    Phase3 --> Phase4[Phase 4: update config.json paths]
    Phase4 --> Phase5[Phase 5: remove browser-use dep]
    Phase5 --> Phase6[Phase 6: smoke test both paths]
    Phase6 --> Done[Deprecate Browser_Agent.py and Browser_Automation_Fast.py]
```

---

## PNG target files

| Concept | PNG File |
|---------|----------|
| Dual-Path Overview | `images/cbm-flow-dual-path.png` |
| Path A Cursor Sequence | `images/cbm-flow-cursor-sequence.png` |
| Path B Agent Sequence | `images/cbm-flow-agent-sequence.png` |
| Element Index Resolution | `images/cbm-flow-element-index.png` |
| Agent Decision Loop | `images/cbm-flow-agent-decisions.png` |
| Error Handling | `images/cbm-flow-error-handling.png` |
| Provider Switch | `images/cbm-flow-provider-switch.png` |
| Migration Phases | `images/cbm-flow-migration.png` |
