"""Browser configuration from environment."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class BrowserSettings:
    headless: bool
    timeout_ms: int
    navigation_timeout_ms: int
    state_cache_ttl_seconds: float
    wait_after_navigate_ms: int
    wait_after_click_ms: int
    max_elements: int
    max_text_per_element: int
    max_page_text_length: int
    downloads_path: Path
    agent_max_steps: int
    litellm_model: str
    litellm_temperature: float
    allowed_hosts: frozenset[str]
    block_localhost: bool
    allow_javascript: bool
    max_script_length: int
    audit_enabled: bool
    audit_log_path: Path
    navigate_retry_count: int


def _env_bool(key: str, default: bool) -> bool:
    raw = os.environ.get(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(key: str, default: int) -> int:
    raw = os.environ.get(key)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_float(key: str, default: float) -> float:
    raw = os.environ.get(key)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _parse_allowed_hosts(raw: str | None) -> frozenset[str]:
    if not raw or not raw.strip():
        return frozenset()
    return frozenset(h.strip().lower() for h in raw.split(",") if h.strip())


def get_settings() -> BrowserSettings:
    downloads = os.environ.get("BROWSER_DOWNLOADS_PATH", "~/Downloads/browser-mcp")
    audit_dir = Path(downloads).expanduser()
    return BrowserSettings(
        headless=_env_bool("BROWSER_HEADLESS", False),
        timeout_ms=_env_int("BROWSER_TIMEOUT_MS", 30_000),
        navigation_timeout_ms=_env_int("BROWSER_NAVIGATION_TIMEOUT_MS", 30_000),
        state_cache_ttl_seconds=_env_float("STATE_CACHE_TTL_SECONDS", 2.0),
        wait_after_navigate_ms=_env_int("BROWSER_WAIT_AFTER_NAVIGATE_MS", 500),
        wait_after_click_ms=_env_int("BROWSER_WAIT_AFTER_CLICK_MS", 200),
        max_elements=_env_int("BROWSER_MAX_ELEMENTS", 200),
        max_text_per_element=_env_int("BROWSER_MAX_TEXT_PER_ELEMENT", 50),
        max_page_text_length=_env_int("BROWSER_MAX_PAGE_TEXT", 10_000),
        downloads_path=audit_dir,
        agent_max_steps=_env_int("AGENT_MAX_STEPS", 25),
        litellm_model=os.environ.get("LITELLM_MODEL", "openai/gpt-4o"),
        litellm_temperature=_env_float("LITELLM_TEMPERATURE", 0.1),
        allowed_hosts=_parse_allowed_hosts(os.environ.get("BROWSER_ALLOWED_HOSTS")),
        block_localhost=_env_bool("BROWSER_BLOCK_LOCALHOST", True),
        allow_javascript=_env_bool("BROWSER_ALLOW_JAVASCRIPT", True),
        max_script_length=_env_int("BROWSER_MAX_SCRIPT_LENGTH", 5000),
        audit_enabled=_env_bool("BROWSER_AUDIT_ENABLED", True),
        audit_log_path=audit_dir / "audit.jsonl",
        navigate_retry_count=_env_int("BROWSER_NAVIGATE_RETRIES", 1),
    )
