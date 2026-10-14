"""Scenario 03, fixed variant.

Identical to the vulnerable variant except for one line in agent_turn:
instructions sourced from retrieved documents are dropped before tool
selection. The agent still collects them, but only user-sourced
instructions reach the tool.

This is the minimal fix for the scenario. A more granular fix would
attach a per-tool policy keyed on instruction source, permitting some
retrieved-doc actions while blocking outbound sends. That is noted in
trace.md but out of scope here.

Run this module directly to confirm no outbound send to the attacker:

    uv run python -m scenarios.agency_retrieved_doc.fixed.app
"""

from scenarios.agency_retrieved_doc.common import (
    ATTACKER_ADDRESS,
    BENIGN_DOC,
    MALICIOUS_DOC,
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

    Fix: instructions collected from retrieved documents are dropped
    before tool selection. Only instructions whose source is
    user_input reach the tool. The provenance tag that was present
    all along is now used.
    """
    instructions = extract_instructions(user_message, source="user_input")
    for doc in docs:
        instructions.extend(extract_instructions(doc.text, source="retrieved_doc"))

    instructions = [i for i in instructions if i.source == "user_input"]  # <-- the fix

    calls: list[ToolCall] = []
    for instruction in instructions:
        call = email.send(to=instruction.recipient, body="summary")
        if call is not None:
            calls.append(call)
    return calls


def main() -> None:
    email = EmailTool()
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
