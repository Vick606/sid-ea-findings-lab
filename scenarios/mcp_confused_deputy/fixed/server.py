"""Scenario 04, fixed MCP server.

The `read_file` tool takes only `path`. The user_id used for
authorization is the authenticated principal bound to the server, not
anything the caller can supply. The agent can still be steered by a
retrieved document into asking for another user's path, but the path
is resolved in the principal's root.

Run the server over stdio:

    uv run python -m scenarios.mcp_confused_deputy.fixed.server
"""

from fastmcp import FastMCP

from scenarios.mcp_confused_deputy.common import (
    PRINCIPAL_RASMUS,
    STORE,
    FileStore,
    Principal,
)

mcp = FastMCP("confused-deputy-fixed")

PRINCIPAL: Principal = PRINCIPAL_RASMUS


def read_file_impl(
    principal: Principal,
    path: str,
    store: FileStore,
) -> str:
    """Pure implementation.

    The user_id is taken from the principal. There is no argument by
    which a caller can select another user's root.
    """
    content = store.read(principal.user_id, path)
    if content is None:
        return f"not found: user={principal.user_id} path={path}"
    return content


@mcp.tool
def read_file(path: str) -> str:
    """Read a file for the authenticated principal."""
    return read_file_impl(PRINCIPAL, path, STORE)


if __name__ == "__main__":
    mcp.run(transport="stdio")
