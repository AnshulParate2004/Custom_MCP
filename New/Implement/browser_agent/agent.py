"""LangGraph ReAct agent using langchain-litellm (Path B)."""

from __future__ import annotations

from typing import Any

from browser.config import get_settings
from browser.session import close_session, is_active, start_session
from browser_agent.tools import get_browser_tools

SYSTEM_PROMPT = """You are a browser automation agent with Playwright tools.

Rules:
1. Call browser_start first if no session is active.
2. ALWAYS call browser_get_state before browser_click or browser_type.
3. Never guess element indices — read them from get_state output.
4. After navigation or major page changes, call browser_get_state again.
5. When the task is complete, call browser_close.
6. Minimize steps. Be precise.

Complete the user's browser task using the tools provided."""


async def run_task(task: str, model: str | None = None) -> dict[str, Any]:
    settings = get_settings()
    model_name = model or settings.litellm_model

    try:
        from langchain_litellm import ChatLiteLLM
        from langgraph.prebuilt import create_react_agent
    except ImportError as exc:
        return {
            "success": False,
            "error": f"Missing agent dependencies: {exc}. Install langchain-litellm and langgraph.",
            "code": "LLM_ERROR",
        }

    llm = ChatLiteLLM(model=model_name, temperature=settings.litellm_temperature)
    tools = get_browser_tools()
    agent = create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)

    if not is_active():
        await start_session()

    try:
        result = await agent.ainvoke(
            {"messages": [("user", task)]},
            config={"recursion_limit": settings.agent_max_steps},
        )
        messages = result.get("messages", [])
        final = messages[-1].content if messages else ""
        return {"success": True, "result": final, "model": model_name, "steps": len(messages)}
    except Exception as exc:
        return {"success": False, "error": str(exc), "code": "LLM_ERROR", "model": model_name}
    finally:
        if is_active():
            await close_session()
