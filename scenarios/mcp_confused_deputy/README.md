# Scenario 04 — MCP confused deputy via argument-trusted identity (EA)

**Class:** Excessive Agency
**OWASP LLM:** LLM06:2025
**Finding ID:** EA-2026-002

## Summary

The MCP server is bound to an authenticated principal at process
start. Its `read_file` tool accepts `user_id` as a tool argument and
uses it to select the file root. The bound principal is never
consulted for the authorization decision. An agent steered by a
retrieved document passes `user_id="noor"` and reads Noor's
compensation file while the server is running as rasmus.

The trust boundary is **principal selection**: the server has the
authenticated identity available and reads it from the wrong place.

## Root cause

Tool arguments are treated as authoritative identity. The server
accepts `user_id` from the agent and uses it for authorization.
The authenticated principal bound to the process is present in the
server code but is not consulted. Any caller that can influence tool
arguments can select another user's root.

## Variants

| Variant | Behavior |
|---|---|
| `vulnerable/` | `read_file(user_id, path)` trusts the argument |
| `fixed/` | `read_file(path)` uses the bound principal, no `user_id` parameter |
| `negative/` | Same vulnerable signature, but the server is constructed with a per-user store |

## Why the negative is not a finding

`negative/server.py` uses the **same `read_file_impl()` function** as
the vulnerable variant: `user_id` comes from the tool arguments, the
principal is accepted but not consulted for authorization. A
code-pattern matcher cannot distinguish the two.

It is not a finding here because the `FileStore` passed to the tool is
constructed with only the principal's own root. When the agent passes
`user_id="noor"`, `store.read("noor", ...)` returns `None` because the
store has no entry for `noor`. There is no foreign root to read.

The safety lives in the store construction, not the tool. The only
functional difference from the vulnerable variant is what store the
server was started with.

This becomes a finding the moment the store is constructed with more
than one user's root, which is exactly what the vulnerable variant
models.

## CVE framing

CVE-2026-27124 is an OAuth consent-validation flaw in FastMCP's
OAuthProxy, fixed in 3.2.0. This scenario is a *tool-level* confused
deputy, distinct from the OAuth-layer issue. It is not a reproduction
of that CVE.

## Verification
uv run python -m scenarios.mcp_confused_deputy.vulnerable.agent

Expected: a `read_file` call with `user_id=noor` returning Noor's
compensation file while the principal is rasmus.
