"""Append-only audit log for browser actions."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from browser.config import get_settings


def log_event(action: str, detail: dict[str, Any] | None = None) -> None:
    settings = get_settings()
    if not settings.audit_enabled:
        return

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "detail": detail or {},
    }

    path: Path = settings.audit_log_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=str) + "\n")
