"""Integration test with Playwright (requires chromium installed)."""

import pytest

from browser import actions
from browser.session import close_session, is_active, start_session


@pytest.mark.asyncio
async def test_navigate_and_get_state():
    if is_active():
        await close_session()

    start = await start_session(headless=True)
    assert start["success"] is True

    try:
        nav = await actions.navigate("https://example.com")
        assert nav["success"] is True
        assert "example.com" in nav["url"]

        from browser import state as page_state

        state = await page_state.get_state(force_refresh=True)
        assert state["element_count"] >= 0
        assert "Example" in state["title"] or "example" in state["url"]
    finally:
        await close_session()
        assert not is_active()
