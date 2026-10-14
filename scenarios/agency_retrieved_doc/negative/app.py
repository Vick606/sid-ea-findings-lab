"""Scenario 03, hard negative.

This variant uses the same agent_turn() function as the vulnerable
variant: instructions from retrieved documents reach the tool with
the same authority as user instructions. The code shape looks like a
finding and the Semgrep rule fires on it.

It is not a finding here because the EmailTool is constructed with an
allowed_recipients set that excludes the attacker. The agent is
fooled; the tool refuses. No email leaves the system, so the effect
that makes this excessive agency does not occur.

The safety lives in the tool configuration, not in the agent. Static
analysis cannot see how the tool was constructed at the call site.

It becomes a finding the moment the tool is configured without an
allowlist, or the allowlist is widened to include the attacker's
address. Both are what the vulnerable variant models.

Run this module directly to confirm no outbound send to the attacker:

    uv run python -m scenarios.agency_retrieved_doc.negative.app
"""

from scenarios.agency_retrieved_doc.common import (
    ATTACKER_ADDRESS,
    BENIGN_DOC,
    MALICIOUS_DOC,
    PARTNER_ADDRESS,
    USER_MESSAGE_SUMMARIZE,
    Document,
    EmailTool,
    ToolCall,
    extract_instructions,
)


def agent_turn(
    user_message: str,
    docs: list[Document],
    email: EmailTool,
) -> list[ToolCall]:
    """Run one agent turn.

    Identical to the vulnerable variant. Instructions from retrieved
    documents are collected and passed to the tool. The tool is what
    stops the outbound send here.
    """
    instructions = extract_instructions(user_message, source="user_input")
    for doc in docs:
        instructions.extend(extract_instructions(doc.text, source="retrieved_doc"))

    calls: list[ToolCall] = []
    for instruction in instructions:
        call = email.send(to=instruction.recipient, body="summary")
        if call is not None:
            calls.append(call)
    return calls


def main() -> None:
    # The only functional difference from the vulnerable variant:
    # the tool is constructed with an allowlist.
    email = EmailTool(allowed_recipients={PARTNER_ADDRESS})
    calls = agent_turn(
        USER_MESSAGE_SUMMARIZE,
        [BENIGN_DOC, MALICIOUS_DOC],
        email,
    )

    print("Agent turn with a retrieved doc containing an injected instruction:")
    if not calls:
        print("  (no outbound tool calls)")
    for call in calls:
        marker = "LEAK" if call.args["to"] == ATTACKER_ADDRESS else "ok"
        print(f"  [{marker}] send_email to={call.args['to']}")


if __name__ == "__main__":
    main()
