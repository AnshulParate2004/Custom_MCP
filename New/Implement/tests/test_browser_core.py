"""Tests for browser core (no live browser required for imports)."""

import pytest

from browser.config import get_settings
from browser.errors import ElementNotFoundError, NoSessionError


def test_settings_defaults():
    settings = get_settings()
    assert settings.agent_max_steps == 25
    assert "gpt" in settings.litellm_model or "openai" in settings.litellm_model
    assert settings.block_localhost is True
    assert settings.audit_enabled is True


def test_no_session_error_code():
    err = NoSessionError()
    assert err.code == "NO_SESSION"


def test_element_not_found_code():
    err = ElementNotFoundError(5)
    assert err.code == "ELEMENT_NOT_FOUND"
    assert "5" in str(err)


@pytest.mark.asyncio
async def test_get_state_requires_session():
    from browser import state as page_state

    page_state.invalidate_cache()
    with pytest.raises(NoSessionError):
        await page_state.get_state()
