"""Custom MCP browser automation — Playwright core."""

from browser.errors import BrowserError, ElementNotFoundError, NoSessionError
from browser.session import close_session, get_page, is_active, start_session

__all__ = [
    "BrowserError",
    "ElementNotFoundError",
    "NoSessionError",
    "close_session",
    "get_page",
    "is_active",
    "start_session",
]
