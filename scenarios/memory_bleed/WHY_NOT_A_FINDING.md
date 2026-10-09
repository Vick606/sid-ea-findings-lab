# Why the negative variant is not a finding

## What it looks like

`scenarios/memory_bleed/negative/app.py` contains this function:

```python
def agent_turn(
    session_id: str,
    user_id: str,
    tenant: str,
    store: MemoryStore,
    message: str,
) -> list[MemoryEntry]:
    history = store.load(session_id)
    store.append(session_id, user_id, tenant, message)
    return history
```

This is **identical** to `vulnerable/app.py:agent_turn()`. Byte for
byte.

The code pattern is the one the Semgrep rule
(`sast/sid_memory_no_user_binding.yaml`) targets. A code-review pass
that only reads `agent_turn()` would flag it. The rule fires on this
variant.

## Why it is not a finding

Because `main()` constructs a **per-user store**:

```python
noor_store = MemoryStore()
rasmus_store = MemoryStore()
```

Each user's process only ever sees the store it created. When
`agent_turn()` runs for `rasmus`, it calls `rasmus_store.load(...)`,
which returns entries written by `rasmus`. There is no cross-user
path: the two stores are not connected, so unfiltered load has
nothing foreign to return.

The user-binding control is not missing here. It is structurally
unnecessary, because the deployment guarantees that no store is ever
shared between users. The isolation is enforced by the process
boundary, not by code.

## Why this is a *hard* negative

A naïve non-finding would differ from the vulnerable case in an
obvious way — filtered load, distinct function name, an explicit
user check. This one shares the exact vulnerable function. The only
difference is deployment context: how stores are constructed and
who has access to them.

That difference is invisible to code-pattern matching. It is why the
Semgrep rule fires on this variant and we accept that as a documented
false positive. It is why the deterministic tests in
`scenarios/memory_bleed/tests/test_memory_bleed.py` exist: only they
can distinguish the two cases, by running them.

The contrast test
(`test_negative_function_leaks_against_shared_store`) makes the
distinction explicit. It takes the negative's *unmodified*
`agent_turn()` and runs it against a *shared* store. It leaks. This
proves the negative is safe because of store construction, not
because of the code. It also proves the Semgrep finding is a false
positive for a structural reason, not because the rule has a bug.

## The condition that would flip it into a finding

This negative becomes a genuine SID-2026-002 finding if:

1. The deployment is changed so a single store is shared across two
   or more users in the same tenant, **or**
2. A caller passes the shared store to a second user's `agent_turn()`
   (e.g., a process supervisor, a queue worker, or a request handler
   that caches stores), **or**
3. A refactor collapses `noor_store` and `rasmus_store` into one
   instance to save memory.

Any of these would place entries written by one user into the store
the other user reads from, at which point the identical
`agent_turn()` would leak.

## What this teaches

Same lesson as scenario 01, in a different pipeline stage: the
finding is not the code. The finding is the code *in a deployment
context where the code's assumptions are violated*. Static analysis
cannot see the deployment context. That is why the annotation —
actor, trust boundary, control scope — is the artifact, not the
rule.

## Verification

```
uv run python -m scenarios.memory_bleed.negative.app
```

Expected output (no LEAK line):

```
Rasmus resumes session 'shared-session' (per-user store):
  (no prior memory visible to rasmus)
```
