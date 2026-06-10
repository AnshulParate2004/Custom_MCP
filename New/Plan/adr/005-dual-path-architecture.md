# ADR-005: Dual-Path Architecture

**Status:** Accepted  
**Date:** 2026-06-11

## Context

Users want both Cursor-driven step-by-step control and autonomous task execution.

## Decision

**Path A:** MCP low-level tools (Cursor orchestrates).  
**Path B:** Custom agent MCP with `run_browser_task`.  
Both share `browser/` core module.

## Rationale

- Path A: visibility and correction mid-task
- Path B: provider choice, one-shot automation
- No duplicated Playwright logic

## Consequences

- Two MCP server entries in config.json
- Agent tools wrap same actions as MCP tools
