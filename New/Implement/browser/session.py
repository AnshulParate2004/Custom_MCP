"""Playwright browser session lifecycle."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from browser.audit import log_event
from browser.config import get_settings
from browser.errors import BrowserError, NoSessionError

if TYPE_CHECKING:
    from playwright.async_api import Browser, BrowserContext, Page, Playwright

_playwright: Playwright | None = None
_browser: Browser | None = None
_context: BrowserContext | None = None
_page: Page | None = None
_pages: list[Page] = []
_lock = asyncio.Lock()


def is_active() -> bool:
    return _page is not None and not _page.is_closed()


async def start_session(headless: bool | None = None) -> dict:
    global _playwright, _browser, _context, _page, _pages

    async with _lock:
        if is_active():
            return {"success": False, "error": "Browser already active", "code": "SESSION_EXISTS"}

        settings = get_settings()
        use_headless = settings.headless if headless is None else headless

        try:
            from playwright.async_api import async_playwright

            _playwright = await async_playwright().start()
            _browser = await _playwright.chromium.launch(headless=use_headless)
            _context = await _browser.new_context(
                viewport={"width": 1280, "height": 720},
                accept_downloads=True,
            )
            _context.set_default_timeout(settings.timeout_ms)
            _page = await _context.new_page()
            _pages = [_page]

            settings.downloads_path.mkdir(parents=True, exist_ok=True)
            log_event("session_start", {"headless": use_headless})

            return {
                "success": True,
                "message": "Browser started",
                "headless": use_headless,
            }
        except Exception as exc:
            await _cleanup()
            raise BrowserError(f"Failed to start browser: {exc}") from exc


async def close_session() -> dict:
    async with _lock:
        was_active = is_active()
        await _cleanup()
        if was_active:
            log_event("session_close", {})
        return {"success": True, "message": "Browser closed"}


async def _cleanup() -> None:
    global _playwright, _browser, _context, _page, _pages

    for page in list(_pages):
        try:
            if not page.is_closed():
                await page.close()
        except Exception:
            pass

    _pages = []
    _page = None

    if _context:
        try:
            await _context.close()
        except Exception:
            pass
        _context = None

    if _browser:
        try:
            await _browser.close()
        except Exception:
            pass
        _browser = None

    if _playwright:
        try:
            await _playwright.stop()
        except Exception:
            pass
        _playwright = None


async def get_page():
    if not is_active():
        raise NoSessionError()
    assert _page is not None
    return _page


async def new_tab(url: str | None = None) -> dict:
    global _page, _pages

    if _context is None:
        raise NoSessionError()

    page = await _context.new_page()
    _pages.append(page)
    _page = page

    if url:
        settings = get_settings()
        await page.goto(url, timeout=settings.navigation_timeout_ms, wait_until="domcontentloaded")
        await asyncio.sleep(settings.wait_after_navigate_ms / 1000)

    return {"success": True, "tab_index": len(_pages) - 1, "url": page.url}
