# Configuration Schemas

Example JSON configs for implementation. Copy to project root or load at runtime.

---

## browser_config.example.json

```json
{
  "browser": {
    "headless": false,
    "timeout_ms": 30000,
    "navigation_timeout_ms": 30000,
    "wait_after_navigate_ms": 500,
    "wait_after_click_ms": 200,
    "state_cache_ttl_seconds": 2,
    "downloads_path": "~/Downloads/browser-mcp",
    "viewport": { "width": 1280, "height": 720 }
  },
  "state_extraction": {
    "max_elements": 200,
    "max_text_length_per_element": 50,
    "max_page_text_length": 10000,
    "interactive_selectors": [
      "a[href]", "button", "input", "textarea", "select",
      "[role=button]", "[role=link]", "[role=textbox]", "[contenteditable=true]"
    ]
  },
  "session": {
    "auto_close_on_agent_finish": true,
    "max_open_tabs": 5
  }
}
```

---

## mcp_config.example.json

```json
{
  "mcpServers": {
    "Browser_Automation": {
      "command": "C:/Users/KAIZEN/.local/bin/uv.exe",
      "args": ["run", "--directory", "D:/Custom_MCP", "python", "browser_mcp.py"],
      "env": {
        "BROWSER_HEADLESS": "false",
        "BROWSER_TIMEOUT_MS": "30000"
      }
    },
    "Browser_Agent": {
      "command": "C:/Users/KAIZEN/.local/bin/uv.exe",
      "args": ["run", "--directory", "D:/Custom_MCP", "python", "browser_agent/mcp_server.py"],
      "env": {
        "LITELLM_MODEL": "openai/gpt-4o",
        "AGENT_MAX_STEPS": "25"
      }
    }
  }
}
```

---

## litellm_config.example.json

```json
{
  "default_model": "openai/gpt-4o",
  "temperature": 0.1,
  "max_tokens": 4096,
  "agent_max_steps": 25,
  "examples": {
    "openai": { "model": "openai/gpt-4o", "env_key": "OPENAI_API_KEY" },
    "anthropic": { "model": "anthropic/claude-sonnet-4-6", "env_key": "ANTHROPIC_API_KEY" },
    "ollama_local": { "model": "ollama/llama3", "api_base": "http://localhost:11434" },
    "groq": { "model": "groq/llama-3.3-70b-versatile", "env_key": "GROQ_API_KEY" }
  }
}
```

---

## BUILD_INSTRUCTIONS.md (LaTeX — create on execution)

When switching to Agent mode, create:

**tech-plan/build.ps1** and **flow-logic/build.ps1** — same pattern as Renewal-Upsell-Advisor:

```powershell
pdflatex -interaction=nonstopmode tech-plan.tex  # run twice
```

**tech-plan.tex** / **flow-logic.tex** — LaTeX versions of TECHNICAL_PLAN.md and FLOW_LOGIC.md with `\includegraphics` for PNG diagrams.
