# Why the negative variant is not a finding

## What it looks like

`scenarios/mcp_confused_deputy/negative/server.py` contains this
function:

```python
def read_file_impl(
    principal: Principal,
    user_id: str,
    path: str,
    store: FileStore,
) -> str:
    """Pure implementation, identical to the vulnerable variant.

    `user_id` comes from the tool arguments and selects the root.
    `principal` is accepted but not consulted for authorization.
    """
    content = store.read(user_id, path)
    if content is None:
        return f"not found: user={user_id} path={path}"
    return content
```

This is **identical** to `vulnerable/server.py:read_file_impl()`.
Byte for byte.

The code pattern is the one the Semgrep rule
(`sast/ea_mcp_argument_trusted_identity.yaml`) targets. A
code-review pass that only reads `read_file_impl()` would flag it.
The rule fires on this variant.

## Why it is not a finding

Because the server is started with a **per-user store**:

```python
_OWN_ROOT = STORE.read(PRINCIPAL.user_id, "notes.md")
PER_USER_STORE = FileStore(
    {
        PRINCIPAL.user_id: {
            "notes.md": _OWN_ROOT or "",
        }
    }
)
```

The store contains only rasmus's root. When the agent passes
`user_id="noor"`, `store.read("noor", "comp.md")` returns `None`
because the store has no `noor` entry. The tool returns not found.

The confused-deputy pattern is present in the agent and in the tool
signature, but the effect the finding describes (a foreign file
returned to the caller) does not occur. The store has nothing foreign
to return.

## Why this is a *hard* negative

A naive non-finding would differ from the vulnerable case in an
obvious way: a `user_id == principal.user_id` check in
`read_file_impl`, a different signature, an explicit auth call. This
one keeps the vulnerable function verbatim. The only difference is
what store the server was started with.

That difference is invisible to code-pattern matching. It is why the
Semgrep rule fires on this variant and we accept that as a documented
false positive. The deterministic tests in
`scenarios/mcp_confused_deputy/tests/` are what distinguish the two
cases, by running them.

The contrast test
(`test_negative_function_leaks_against_shared_store`) takes the
negative's *unmodified* `read_file_impl()` and runs it against the
*shared* `STORE`. It leaks. This proves the negative is safe because
of store construction, not code.

## The condition that would flip it into a finding

This negative becomes a genuine EA-2026-002 finding if:

1. The server is constructed with the shared `STORE` instead of
   `PER_USER_STORE`, **or**
2. A second principal's root is added to `PER_USER_STORE` (for
   example, to support a service account or an admin mode), **or**
3. A future caller passes a different store into `read_file_impl()`
   without updating the per-user constraint.

Any of these would place a foreign root in the store the tool reads
from, at which point the identical `read_file_impl()` would return
cross-user content.

## What this teaches

This is the fourth instance of the same pattern in the corpus:

| Scenario | Vulnerable function | Negative is safe because |
|---|---|---|
| 01 | `retrieve()` | the store is per-tenant |
| 02 | `agent_turn()` (memory) | the store is per-user |
| 03 | `agent_turn()` (tool) | the tool has a recipient allowlist |
| 04 | `read_file_impl()` | the store has only the principal's root |

In every case the code shape is identical and the safety lives in
construction. Static analysis sees the function. The deployment is
what determines whether the function is dangerous.

Scenario 04 adds a new dimension: the fix in the *fixed* variant is
also structural, but it is applied at a different layer (the tool
schema) rather than at construction (the store). A reviewer reading
all three variants sees two acceptable controls and one missing
control. That is the judgment the corpus is trying to exercise.

## Verification

```
uv run python -m scenarios.mcp_confused_deputy.negative.agent
```

Expected output (no foreign file returned):

```
Agent turn against the negative MCP server:
  read_file user_id=noor path=comp.md
    -> not found: user=noor path=comp.md
```

And through the TypeScript client:

```
cd clients/ts
pnpm run negative
```

Expected: `not found: user=noor path=comp.md`.
