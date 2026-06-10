#!/usr/bin/env python3
"""MCP server — run_browser_task via LangChain + LiteLLM agent (Path B)."""

from __future__ import annotations

import json

from dotenv import load_dotenv
from fastmcp import FastMCP

from browser_agent.agent import run_task

load_dotenv()

mcp = FastMCP("Browser_Agent")


@mcp.tool()
async def run_browser_task(task: str, model: str | None = None) -> str:
    """Run a multi-step browser automation task using the custom LangChain + LiteLLM agent.

    Args:
        task: Natural language description of what to do in the browser.
        model: Optional LiteLLM model override (e.g. openai/gpt-4o, anthropic/claude-sonnet-4-6).
    """
    result = await run_task(task, model=model)
    return json.dumps(result, default=str)


if __name__ == "__main__":
    mcp.run()
