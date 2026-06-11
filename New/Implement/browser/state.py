"""Indexed DOM state extraction per DOM_EXTRACTOR_SPEC.md."""

from __future__ import annotations

import base64
import time
from typing import Any

from browser import guards as state_guards
from browser.config import get_settings
from browser.errors import ElementNotFoundError
from browser.session import get_page

DOM_EXTRACTOR_JS = """
([selectors, maxElements, maxTextLen]) => {
  const seen = new Set();
  const results = [];

  const isVisible = (el) => {
    const rect = el.getBoundingClientRect();
    if (rect.width <= 0 || rect.height <= 0) return false;
    const style = window.getComputedStyle(el);
    return style.visibility !== 'hidden' && style.display !== 'none';
  };

  const textOf = (el) => {
    const t = (el.innerText || el.textContent || el.value || '').trim();
    return t.slice(0, maxTextLen);
  };

  for (const sel of selectors) {
    for (const el of document.querySelectorAll(sel)) {
      if (seen.has(el) || !isVisible(el)) continue;
      seen.add(el);
      results.push({
        tag: el.tagName.toLowerCase(),
        type: el.getAttribute('type') || undefined,
        text: textOf(el),
        placeholder: el.getAttribute('placeholder') || undefined,
        ariaLabel: el.getAttribute('aria-label') || undefined,
        href: el.getAttribute('href') || undefined,
      });
      if (results.length >= maxElements) break;
    }
    if (results.length >= maxElements) break;
  }

  results.forEach((item, i) => { item.index = i; });
  return results;
}
"""

DEFAULT_SELECTORS = [
    "a[href]",
    "button:not([disabled])",
    "input:not([type=hidden]):not([disabled])",
    "textarea:not([disabled])",
    "select:not([disabled])",
    "[role=button]",
    "[role=link]",
    "[role=textbox]",
    "[contenteditable=true]",
]

_last_snapshot: dict[str, Any] | None = None
_cache_time: float = 0.0


def invalidate_cache() -> None:
    global _last_snapshot, _cache_time
    _last_snapshot = None
    _cache_time = 0.0
    state_guards.invalidate_state_observed()


async def get_state(
    include_screenshot: bool = False,
    force_refresh: bool = False,
) -> dict[str, Any]:
    global _last_snapshot, _cache_time

    settings = get_settings()
    now = time.time()

    if (
        not force_refresh
        and _last_snapshot is not None
        and (now - _cache_time) < settings.state_cache_ttl_seconds
        and not include_screenshot
    ):
        cached = dict(_last_snapshot)
        cached["from_cache"] = True
        cached["cache_age_seconds"] = round(now - _cache_time, 2)
        return cached

    page = await get_page()
    elements = await page.evaluate(
        DOM_EXTRACTOR_JS,
        [DEFAULT_SELECTORS, settings.max_elements, settings.max_text_per_element],
    )

    result: dict[str, Any] = {
        "url": page.url,
        "title": await page.title(),
        "element_count": len(elements),
        "interactive_elements": elements,
        "from_cache": False,
    }

    if include_screenshot:
        png = await page.screenshot(type="png")
        result["screenshot"] = base64.b64encode(png).decode("ascii")

    _last_snapshot = {
        "url": result["url"],
        "title": result["title"],
        "element_count": result["element_count"],
        "interactive_elements": list(elements),
    }
    _cache_time = now
    state_guards.mark_state_observed()

    return result


async def get_element_for_index(index: int):
    page = await get_page()
    settings = get_settings()

    handle = await page.evaluate_handle(
        """
        ([selectors, maxElements, targetIndex]) => {
          const seen = new Set();

          const isVisible = (el) => {
            const rect = el.getBoundingClientRect();
            if (rect.width <= 0 || rect.height <= 0) return false;
            const style = window.getComputedStyle(el);
            return style.visibility !== 'hidden' && style.display !== 'none';
          };

          let count = 0;
          for (const sel of selectors) {
            for (const el of document.querySelectorAll(sel)) {
              if (seen.has(el) || !isVisible(el)) continue;
              seen.add(el);
              if (count === targetIndex) return el;
              count++;
              if (count >= maxElements) return null;
            }
          }
          return null;
        }
        """,
        [DEFAULT_SELECTORS, settings.max_elements, index],
    )

    element = handle.as_element()
    if element is None:
        raise ElementNotFoundError(index)
    return element
