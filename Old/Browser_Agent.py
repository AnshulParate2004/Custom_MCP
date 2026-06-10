#!/usr/bin/env python3
import os
import sys

# CRITICAL: Set these FIRST before importing anything
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# Monkey-patch print to suppress all output
import builtins
_original_print = builtins.print
def silent_print(*args, **kwargs):
    pass
builtins.print = silent_print

# Disable all logging
import logging
logging.disable(logging.CRITICAL)

# Now safe to import
from browser_use import Agent, Browser, ChatBrowserUse
import asyncio
from fastmcp import FastMCP

# Restore print only for MCP
builtins.print = _original_print

mcp = FastMCP("Browser_Agent")

@mcp.tool()
async def browser_agent(task: str) -> str:
    """Execute a browser automation task using an AI agent
    
    Args:
        task: Description of the task to perform (e.g., "Go to google.com and search for Python")
    
    Returns:
        Execution history and results from the browser agent
    """
    api_key = os.getenv('BROWSER_USE_API_KEY')
    
    if not api_key or not api_key.strip():
        raise ValueError("API key is required for the ChatBrowserUse LLM.")
    try:
        browser = Browser()
        llm = ChatBrowserUse(api_key=api_key)
        agent = Agent(task=task, llm=llm, browser=browser)
        history = await agent.run()
        return history
    
    except Exception as e:
        return {"error": f"Browser agent failed: {str(e)}"}
    
if __name__ == "__main__":
    mcp.run()
