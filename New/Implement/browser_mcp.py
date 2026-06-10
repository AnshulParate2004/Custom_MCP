#!/usr/bin/env python3
"""MCP server — low-level Playwright browser tools for Cursor (Path A)."""

from __future__ import annotations

import json
from typing import Any

from fastmcp import FastMCP

from browser.errors import BrowserError, NoSessionError
from browser import actions
from browser.session import close_session, start_session

mcp = FastMCP("Browser_Automation")


def _json_result(data: Any) -> str:
    return json.dumps(data, default=str)


def _error_result(exc: Exception) -> str:
    code = getattr(exc, "code", "BROWSER_ERROR")
    return _json_result({"success": False, "error": str(exc), "code": code})


@mcp.tool()
async def browser_start(headless: bool = False) -> str:
    """Start a Playwright Chromium browser session."""
    try:
        return _json_result(await start_session(headless=headless))
    except Exception as exc:
        return _error_result(exc)


@mcp.tool()
async def browser_close() -> str:
    """Close the active browser session."""
    try:
        return _json_result(await close_session())
    except Exception as exc:
        return _error_result(exc)


@mcp.tool()
async def browser_navigate(url: str, new_tab: bool = False) -> str:
    """Navigate to a URL in the active tab or a new tab."""
    try:
        actions.ensure_session()
        return _json_result(await actions.navigate(url, new_tab_flag=new_tab))
    except Exception as exc:
        return _error_result(exc)


@mcp.tool()
async def browser_get_state(include_screenshot: bool = False, force_refresh: bool = False) -> str:
    """Get page URL, title, and indexed interactive elements."""
    try:
        actions.ensure_session()
        from browser import state as page_state

        return _json_result(
            await page_state.get_state(
                include_screenshot=include_screenshot,
                force_refresh=force_refresh,
            )
        )
    except Exception as exc:
        return _error_result(exc)


@mcp.tool()
async def browser_get_content() -> str:
    """Extract visible text content from the current page."""
    try:
        actions.ensure_session()
        return _json_result(await actions.get_text_content())
    except Exception as exc:
        return _error_result(exc)


@mcp.tool()
async def browser_click(index: int) -> str:
    """Click an interactive element by its index from browser_get_state."""
    try:
        actions.ensure_session()
        return _json_result(await actions.click(index))
    except Exception as exc:
        return _error_result(exc)


@mcp.tool()
async def browser_type(index: int, text: str) -> str:
    """Type text into an input element by index."""
    try:
        actions.ensure_session()
        return _json_result(await actions.type_text(index, text))
    except Exception as exc:
        return _error_result(exc)


@mcp.tool()
async def browser_scroll(direction: str = "down", amount: int = 500) -> str:
    """Scroll the page up or down."""
    try:
        actions.ensure_session()
        return _json_result(await actions.scroll(direction, amount))
    except Exception as exc:
        return _error_result(exc)


@mcp.tool()
async def browser_execute_javascript(script: str) -> str:
    """Execute JavaScript on the current page."""
    try:
        actions.ensure_session()
        return _json_result(await actions.evaluate(script))
    except Exception as exc:
        return _error_result(exc)


if __name__ == "__main__":
    mcp.run()


def main() -> None:
    mcp.run()
