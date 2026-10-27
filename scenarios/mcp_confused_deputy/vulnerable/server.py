"""Scenario 04, vulnerable MCP server.

The server is bound to an authenticated principal at process start.
The `read_file` tool accepts `user_id` as a tool argument and uses it
to select the file root. The bound principal is never consulted for
authorization. An agent that passes `user_id="noor"` reads Noor's
files even though the server was started as rasmus.

Run the server over stdio:

    uv run python -m scenarios.mcp_confused_deputy.vulnerable.server
"""

from fastmcp import FastMCP

from scenarios.mcp_confused_deputy.common import (
    PRINCIPAL_RASMUS,
    STORE,
    FileStore,
    Principal,
)

mcp = FastMCP("confused-deputy-vulnerable")

# The authenticated identity this server process is bound to.
PRINCIPAL: Principal = PRINCIPAL_RASMUS


def read_file_impl(
    principal: Principal,
    user_id: str,
    path: str,
    store: FileStore,
) -> str:
    """Pure implementation, testable without an MCP runtime.

    Bug: `user_id` comes from the tool arguments. The server trusts it
    to select the root. `principal` is accepted but never used for the
    authorization decision.
    """
    content = store.read(user_id, path)
    if content is None:
        return f"not found: user={user_id} path={path}"
    return content


@mcp.tool
def read_file(user_id: str, path: str) -> str:
    """Read a file for `user_id`."""
    return read_file_impl(PRINCIPAL, user_id, path, STORE)


if __name__ == "__main__":
    mcp.run(transport="stdio")
