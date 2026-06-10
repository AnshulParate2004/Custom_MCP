# ADR-001: Playwright as Browser Engine

**Status:** Accepted  
**Date:** 2026-06-11

## Context

Need a modern browser automation library for Python MCP servers.

## Decision

Use **Playwright** (`playwright.async_api`) instead of Selenium or browser-use wrapper.

## Rationale

- Auto-wait, fast startup, active maintenance
- Already familiar from browser-use under the hood
- No WebDriver binary management
- Strong async API for MCP servers

## Consequences

- Requires `python -m playwright install chromium` post-install
- Chromium-first (Firefox/WebKit optional later)
