"""URL and script validation for safer automation."""

from __future__ import annotations

from urllib.parse import urlparse

from browser.config import get_settings
from browser.errors import BrowserError, NavigationError

BLOCKED_SCHEMES = frozenset({"file", "javascript", "data", "vbscript"})
BLOCKED_HOSTS = frozenset({"localhost", "127.0.0.1", "0.0.0.0", "::1"})


def validate_url(url: str) -> str:
    """Normalize and validate navigation URL."""
    url = (url or "").strip()
    if not url:
        raise NavigationError("URL is empty")

    parsed = urlparse(url)
    if not parsed.scheme:
        url = f"https://{url}"
        parsed = urlparse(url)

    if parsed.scheme.lower() not in {"http", "https"}:
        raise NavigationError(f"Blocked URL scheme: {parsed.scheme}")

    host = (parsed.hostname or "").lower()
    if host in BLOCKED_HOSTS and get_settings().block_localhost:
        raise NavigationError(f"Blocked host: {host}")

    allowlist = get_settings().allowed_hosts
    if allowlist and host not in allowlist:
        raise NavigationError(f"Host not in allowlist: {host}")

    return url


def validate_javascript(script: str) -> str:
    """Validate JS execution request."""
    script = (script or "").strip()
    if not script:
        raise BrowserError("Script is empty", code="INVALID_SCRIPT")

    settings = get_settings()
    if not settings.allow_javascript:
        raise BrowserError(
            "JavaScript execution disabled. Set BROWSER_ALLOW_JAVASCRIPT=true to enable.",
            code="JS_DISABLED",
        )

    if len(script) > settings.max_script_length:
        raise BrowserError(
            f"Script exceeds max length ({settings.max_script_length} chars)",
            code="SCRIPT_TOO_LONG",
        )

    lowered = script.lower()
    for pattern in ("eval(", "Function(", "document.cookie", "localStorage", "sessionStorage"):
        if pattern.lower() in lowered:
            raise BrowserError(f"Blocked pattern in script: {pattern}", code="SCRIPT_BLOCKED")

    return script
