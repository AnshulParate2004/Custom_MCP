"""Runtime guards for agent and MCP tool sequences."""

from browser.errors import BrowserError

_state_observed = False


def mark_state_observed() -> None:
    global _state_observed
    _state_observed = True


def invalidate_state_observed() -> None:
    global _state_observed
    _state_observed = False


def require_fresh_state() -> None:
    if not _state_observed:
        raise BrowserError(
            "Stale or missing page state. Call browser_get_state before browser_click or browser_type.",
            code="STALE_STATE",
        )
