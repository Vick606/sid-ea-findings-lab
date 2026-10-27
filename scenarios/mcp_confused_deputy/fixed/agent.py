"""Scenario 04, fixed agent.

The agent still extracts a read instruction from the user message and
from retrieved documents. It no longer forwards the `user_id` from the
instruction to the tool. The tool has no `user_id` parameter; identity
comes from the server's bound principal.

Run this module directly to confirm the leak is gone:

    uv run python -m scenarios.mcp_confused_deputy.fixed.agent
"""

from scenarios.mcp_confused_deputy.common import (
    BENIGN_DOC,
    MALICIOUS_DOC,
    PRINCIPAL_RASMUS,
    STORE,
    Document,
    ToolCall,
    extract_read_instruction,
)
from scenarios.mcp_confused_deputy.fixed.server import read_file_impl


def agent_turn(
    user_message: str,
    docs: list[Document],
    principal,
) -> list[ToolCall]:
    """Run one agent turn against the fixed MCP tool.

    Fix: the tool call uses the bound principal. The `user_id` from the
    instruction is dropped on the floor.
    """
    calls: list[ToolCall] = []

    instruction = extract_read_instruction(user_message, source="user_input")
    if instruction is not None:
        result = read_file_impl(principal, instruction.path, STORE)
        calls.append(
            ToolCall(
                tool="read_file",
                args={"user_id": principal.user_id, "path": instruction.path},
                result=result,
            )
        )

    for doc in docs:
        instruction = extract_read_instruction(doc.text, source="retrieved_doc")
        if instruction is None:
            continue
        result = read_file_impl(principal, instruction.path, STORE)
        calls.append(
            ToolCall(
                tool="read_file",
                args={"user_id": principal.user_id, "path": instruction.path},
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

    print("Agent turn against the fixed MCP server:")
    for call in calls:
        print(f"  read_file user_id={call.args['user_id']} path={call.args['path']}")
        print(f"    -> {call.result}")


if __name__ == "__main__":
    main()
