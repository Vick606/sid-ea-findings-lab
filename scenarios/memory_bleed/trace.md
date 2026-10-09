# Trace — SID-2026-002

Source-to-sink path for the cross-user memory bleed, with the
authorization context that makes it a finding.

## Actor

The actor is `rasmus`, a user in `tenant_a`. He is authenticated,
holds `memory:read` and `memory:write`, and his purpose is
`personal_assistant`. His `permitted_recipients` is `[rasmus]` — his
own memory, no one else's.

Two facts matter for this trace:

1. The actor is *authorized* for `memory:read`. This is not an
   unauthenticated request.
2. The actor is *not* authorized for memory written by `noor`, even
   though both share `tenant_a`. Memory isolation in this deployment
   is user-level, not tenant-level.

Any entry written by `noor` that reaches `rasmus` is a disclosure.

## Trust boundary crossed

`user_memory_isolation`. The boundary sits between two users inside
the same tenant, mediated by a shared memory store. The invariant
the boundary is supposed to preserve:

> A memory entry written by one user is never returned to a different
> user, regardless of session_id collision or reuse.

The vulnerable variant violates this invariant.

## Flow

### Source

`scenarios/memory_bleed/common.py:34` — the `MemoryStore` holds
entries keyed by `session_id`. Entries carry `user_id` and `tenant`
as metadata, but the store never uses them for filtering. A sensitive
entry written by `noor` sits in the store, addressable by session_id.

### Step 1 — Load without predicate

`scenarios/memory_bleed/vulnerable/app.py:30` — `agent_turn()` calls
`store.load(session_id)`. The load method returns every entry ever
appended for that `session_id`, regardless of which user wrote them.
The absence of a user predicate is the sink of the control.

The control that would prevent the leak — binding reads to the
requesting user — is not present anywhere in the pipeline.

### Step 2 — Return to caller

`scenarios/memory_bleed/vulnerable/app.py:31` — the unfiltered
history is returned. The caller places it in the model's context on
the next turn. `noor`'s SSN is now visible to `rasmus`.

### Sink

The model's context window. From there the memory entry can surface
in responses, be summarized into later memory, be forwarded to tools,
or be exfiltrated through any tool the agent can call. The sink is
the model, not the response — once the entry is in the context, the
disclosure is already complete.

## Authorization reasoning

The finding is not "memory has no user predicate." Plenty of caches
and stores are unfiltered by design, with the caller responsible for
authorization. The finding is that **the caller does not apply any
user predicate either**. Both layers assume the other enforces it.

The trust boundary here is **user-level**, not tenant-level. This is
worth stating explicitly because it is different from scenario 01.
Scenario 01 crossed a tenant boundary: the actor was `tenant_a` and
the data was `tenant_b`. Both variants are SID, but the boundary that
was violated is different, and the required control is different.

The correct control is **user binding on read**: the store or the
caller (or both) must verify that the requesting user owns the
session before returning entries.

## Why this is HIGH and not CRITICAL

- The actor is authenticated and shares a tenant with the target.
- The attacker must know or guess the target's `session_id`. That
  raises the bar somewhat, but session IDs are often visible in URLs,
  logs, and client state, so it is a weak barrier.
- The leak is bounded by what happens to be in the target's memory,
  not by arbitrary document access.

It would be CRITICAL if session IDs were predictable or enumerable,
if memory entries routinely carried long-lived credentials, or if
the agent could be induced to leak memory to external recipients
during the same turn. None of those conditions hold in this
scenario.

## What the fixed variant changes

One line at `scenarios/memory_bleed/fixed/app.py:31`:

    history = [e for e in history if e.user_id == user_id]

The fix re-applies the user predicate at the caller, where the actor
context is known. The store remains unfiltered by design; user
binding is an authorization concern, and authorization belongs where
the actor is identified.
