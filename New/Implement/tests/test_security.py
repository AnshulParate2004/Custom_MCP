"""Security and guard tests."""

import pytest

from browser import actions
from browser import guards
from browser import security
from browser import state as page_state
from browser.audit import log_event
from browser.errors import BrowserError, NavigationError
from browser.session import close_session, start_session


def test_validate_url_adds_https():
    assert security.validate_url("example.com").startswith("https://")


def test_validate_url_blocks_file_scheme():
    with pytest.raises(NavigationError):
        security.validate_url("file://C:/secret.txt")


def test_validate_url_blocks_localhost():
    with pytest.raises(NavigationError):
        security.validate_url("http://localhost:8080")


def test_validate_javascript_blocks_eval():
    with pytest.raises(BrowserError) as exc:
        security.validate_javascript("eval('alert(1)')")
    assert exc.value.code == "SCRIPT_BLOCKED"


@pytest.mark.asyncio
async def test_stale_state_guard_blocks_click():
    page_state.invalidate_cache()
    guards.invalidate_state_observed()
    with pytest.raises(BrowserError) as exc:
        await actions.click(0)
    assert exc.value.code == "STALE_STATE"


def test_audit_log_writes(tmp_path, monkeypatch):
    monkeypatch.setenv("BROWSER_DOWNLOADS_PATH", str(tmp_path))
    monkeypatch.setenv("BROWSER_AUDIT_ENABLED", "true")

    log_event("test_action", {"foo": "bar"})
    audit_file = tmp_path / "audit.jsonl"
    assert audit_file.exists()
    assert "test_action" in audit_file.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_get_state_marks_observed():
    await close_session()
    await start_session(headless=True)
    try:
        await actions.navigate("https://example.com")
        guards.invalidate_state_observed()
        await page_state.get_state(force_refresh=True)
        guards.require_fresh_state()
    finally:
        await close_session()
