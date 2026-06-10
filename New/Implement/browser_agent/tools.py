"""LangChain tools wrapping shared browser actions (Path B)."""

from __future__ import annotations

import json

from langchain_core.tools import StructuredTool

from browser import actions
from browser import state as page_state
from browser.session import close_session, start_session


def _dump(data: object) -> str:
    return json.dumps(data, default=str)


async def _tool_start(headless: bool = False) -> str:
    return _dump(await start_session(headless=headless))


async def _tool_close() -> str:
    return _dump(await close_session())


async def _tool_navigate(url: str, new_tab: bool = False) -> str:
    actions.ensure_session()
    return _dump(await actions.navigate(url, new_tab_flag=new_tab))


async def _tool_get_state(include_screenshot: bool = False, force_refresh: bool = True) -> str:
    actions.ensure_session()
    return _dump(
        await page_state.get_state(
            include_screenshot=include_screenshot,
            force_refresh=force_refresh,
        )
    )


async def _tool_get_content() -> str:
    actions.ensure_session()
    return _dump(await actions.get_text_content())


async def _tool_click(index: int) -> str:
    actions.ensure_session()
    return _dump(await actions.click(index))


async def _tool_type(index: int, text: str) -> str:
    actions.ensure_session()
    return _dump(await actions.type_text(index, text))


async def _tool_scroll(direction: str = "down", amount: int = 500) -> str:
    actions.ensure_session()
    return _dump(await actions.scroll(direction, amount))


async def _tool_evaluate(script: str) -> str:
    actions.ensure_session()
    return _dump(await actions.evaluate(script))


def get_browser_tools() -> list[StructuredTool]:
    return [
        StructuredTool.from_function(
            coroutine=_tool_start,
            name="browser_start",
            description="Start Playwright Chromium. Call before any other browser tool.",
        ),
        StructuredTool.from_function(
            coroutine=_tool_close,
            name="browser_close",
            description="Close the browser session when the task is complete.",
        ),
        StructuredTool.from_function(
            coroutine=_tool_navigate,
            name="browser_navigate",
            description="Navigate to a URL. Args: url (string), new_tab (bool, default false).",
        ),
        StructuredTool.from_function(
            coroutine=_tool_get_state,
            name="browser_get_state",
            description="Get indexed interactive elements. ALWAYS call before click or type.",
        ),
        StructuredTool.from_function(
            coroutine=_tool_get_content,
            name="browser_get_content",
            description="Get page text content without element indices.",
        ),
        StructuredTool.from_function(
            coroutine=_tool_click,
            name="browser_click",
            description="Click element by index from browser_get_state.",
        ),
        StructuredTool.from_function(
            coroutine=_tool_type,
            name="browser_type",
            description="Type text into element by index from browser_get_state.",
        ),
        StructuredTool.from_function(
            coroutine=_tool_scroll,
            name="browser_scroll",
            description="Scroll page. direction: up|down, amount: pixels.",
        ),
        StructuredTool.from_function(
            coroutine=_tool_evaluate,
            name="browser_execute_javascript",
            description="Run JavaScript on the page.",
        ),
    ]
