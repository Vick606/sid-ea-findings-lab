"""Scenario 04, hard negative agent.

The agent is identical to the vulnerable variant: it collects read
instructions from the user message and from retrieved documents, then
passes the instruction's `user_id` to the tool. The agent is fooled.

The tool refuses because the per-user store has no foreign root. That
is the only difference from the vulnerable deployment.

Run this module directly to confirm the leak is gone:

    uv run python -m scenarios.mcp_confused_deputy.negative.agent
"""

from scenarios.mcp_confused_deputy.common import (
    BENIGN_DOC,
    MALICIOUS_DOC,
    PRINCIPAL_RASMUS,
    Document,
    ToolCall,
    extract_read_instruction,
)
from scenarios.mcp_confused_deputy.negative.server import (
    PER_USER_STORE,
    read_file_impl,
)


def agent_turn(
    user_message: str,
    docs: list[Document],
    principal,
) -> list[ToolCall]:
    """Run one agent turn against the negative MCP tool.

    Identical to the vulnerable agent. The `user_id` passed to the tool
    comes from the instruction, which may originate in a retrieved
    document. The tool is what stops the read here.
    """
    calls: list[ToolCall] = []

    instruction = extract_read_instruction(user_message, source="user_input")
    if instruction is not None:
        result = read_file_impl(principal, instruction.user_id, instruction.path, PER_USER_STORE)
        calls.append(
            ToolCall(
                tool="read_file",
                args={"user_id": instruction.user_id, "path": instruction.path},
                result=result,
            )
        )

    for doc in docs:
        instruction = extract_read_instruction(doc.text, source="retrieved_doc")
        if instruction is None:
            continue
        result = read_file_impl(principal, instruction.user_id, instruction.path, PER_USER_STORE)
        calls.append(
            ToolCall(
                tool="read_file",
                args={"user_id": instruction.user_id, "path": instruction.path},
                result=result,
            )
        )

    return calls


def main() -> None:
    calls = agent_turn(
        "Summarize the attached notes.",
        [BENIGN_DOC, MALICIOUS_DOC],
        PRINCIPAL_RASMUS,
    )

    print("Agent turn against the negative MCP server:")
    for call in calls:
        print(f"  read_file user_id={call.args['user_id']} path={call.args['path']}")
        print(f"    -> {call.result}")


if __name__ == "__main__":
    main()
