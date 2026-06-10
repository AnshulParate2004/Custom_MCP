"""Browser actions — thin Playwright wrappers."""

from __future__ import annotations

import asyncio
import base64
import json
from typing import Any

from browser.config import get_settings
from browser.errors import BrowserError, NavigationError, NoSessionError
from browser import state as page_state
from browser.session import get_page, is_active, new_tab


def ensure_session() -> None:
    if not is_active():
        raise NoSessionError()


async def navigate(url: str, new_tab_flag: bool = False) -> dict[str, Any]:
    if new_tab_flag:
        result = await new_tab(url)
        page_state.invalidate_cache()
        return {"success": True, "url": result.get("url", url), "new_tab": True}

    settings = get_settings()
    page = await get_page()

    try:
        await page.goto(url, timeout=settings.navigation_timeout_ms, wait_until="domcontentloaded")
        await asyncio.sleep(settings.wait_after_navigate_ms / 1000)
    except Exception as exc:
        raise NavigationError(f"Navigation failed: {exc}") from exc

    page_state.invalidate_cache()
    return {"success": True, "url": page.url}


async def click(index: int) -> dict[str, Any]:
    settings = get_settings()
    element = await page_state.get_element_for_index(index)

    try:
        await element.click(timeout=settings.timeout_ms)
        await asyncio.sleep(settings.wait_after_click_ms / 1000)
    except Exception as exc:
        raise BrowserError(f"Click failed on index {index}: {exc}") from exc

    page_state.invalidate_cache()
    return {"success": True, "index": index}


async def type_text(index: int, text: str) -> dict[str, Any]:
    settings = get_settings()
    element = await page_state.get_element_for_index(index)

    try:
        tag = await element.evaluate("el => el.tagName.toLowerCase()")
        if tag in {"input", "textarea"}:
            await element.fill(text, timeout=settings.timeout_ms)
        else:
            await element.click(timeout=settings.timeout_ms)
            await element.type(text, timeout=settings.timeout_ms)
    except Exception as exc:
        raise BrowserError(f"Type failed on index {index}: {exc}") from exc

    page_state.invalidate_cache()
    return {"success": True, "index": index}


async def scroll(direction: str = "down", amount: int = 500) -> dict[str, Any]:
    page = await get_page()
    delta = amount if direction == "down" else -amount
    await page.evaluate(f"window.scrollBy(0, {delta})")
    return {"success": True, "direction": direction, "amount": amount}


async def evaluate(script: str) -> dict[str, Any]:
    page = await get_page()
    result = await page.evaluate(script)
    return {"success": True, "result": result}


async def get_text_content() -> dict[str, Any]:
    settings = get_settings()
    page = await get_page()
    text = await page.inner_text("body")
    truncated = len(text) > settings.max_page_text_length
    if truncated:
        text = text[: settings.max_page_text_length]

    return {
        "url": page.url,
        "title": await page.title(),
        "text_content": text,
        "truncated": truncated,
    }


def to_json(data: Any) -> str:
    return json.dumps(data, default=str)
