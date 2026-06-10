# ADR-004: Indexed DOM, Not Vision (Phase 1)

**Status:** Accepted  
**Date:** 2026-06-11

## Context

Need reliable element targeting for click/type actions.

## Decision

Phase 1 uses **indexed interactive elements** from DOM scan. No screenshot+coordinate clicking.

## Rationale

- Deterministic, debuggable, matches existing MCP tool design
- Lower cost (no vision API per step)
- Sufficient for most automation tasks

## Consequences

- Must call `browser_get_state` before click/type
- Indexes invalidate on navigation
