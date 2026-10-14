"""Scenario 03, vulnerable variant.

The agent collects candidate instructions from the user message and
from every retrieved document, then executes them all. There is no
check on where each instruction came from. A retrieved document that
contains an injected 'forward ... to <email>' instruction triggers an
outbound send.

Run this module directly to reproduce:

    uv run python -m scenarios.agency_retrieved_doc.vulnerable.app
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

    Bug: instructions are collected from the user message AND from
    every retrieved document. Nothing downstream distinguishes a
    user instruction from one that came in through retrieval. Both
    reach the tool with the same authority.
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
    email = EmailTool()
    calls = agent_turn(
        USER_MESSAGE_SUMMARIZE,
        [BENIGN_DOC, MALICIOUS_DOC],
        email,
    )

    print("Agent turn with a retrieved doc containing an injected instruction:")
    for call in calls:
        marker = "LEAK" if call.args["to"] == ATTACKER_ADDRESS else "ok"
        print(f"  [{marker}] send_email to={call.args['to']}")


if __name__ == "__main__":
    main()
