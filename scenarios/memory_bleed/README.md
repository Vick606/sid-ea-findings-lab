# Scenario 02 — Cross-user memory bleed (SID)

**Class:** Sensitive Information Disclosure
**OWASP LLM:** LLM02:2025
**Finding ID:** SID-2026-002

## Summary

A stateful agent stores conversation memory keyed by `session_id`
only. The memory store does not bind entries to the user who wrote
them. Two users in the same tenant sharing one store can read each
other's memory by supplying the same `session_id`. The trust boundary
is **user-level within a tenant** — different from scenario 01, which
crossed a tenant boundary.

## Root cause

The control that matters here is **user binding**: every memory read
should verify that the requesting user owns the session. That control
is absent. The `session_id` is treated as the sole credential, but
session IDs are not secrets — they are identifiers. A user who knows
or guesses another user's session ID reads that user's memory.

## Variants

| Variant | Behavior |
|---|---|
| `vulnerable/` | Shared store, `load(session_id)` unfiltered |
| `fixed/` | Same store, `load` result filtered by `user_id` |
| `negative/` | Same unfiltered `load`, but the store is constructed per-user |

## Why the negative is not a finding

`negative/app.py` calls the same `store.load(session_id)` as the
vulnerable variant, without any user filter. The code shape looks
identical. It is safe because the store is constructed per-user: each
user's process only ever sees entries it wrote itself. Cross-user
bleed cannot occur because there is no cross-user store to bleed from.

This becomes a finding the moment the deployment serves more than one
user from a single store instance, which is exactly what the
vulnerable variant models.

## Verification
uv run python -m scenarios.memory_bleed.vulnerable.app

Expected: one LEAK line — Rasmus reads Noor's stored SSN.
