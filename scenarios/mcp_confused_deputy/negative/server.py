"""Scenario 04, hard negative.

This variant uses the same read_file_impl as the vulnerable variant:
`user_id` comes from the tool arguments, the principal is accepted but
not consulted for authorization. The code shape looks like a finding
and the Semgrep rule fires on it.

It is not a finding here because the FileStore passed to the tool is
constructed with only the principal's own root. When the agent passes
`user_id="noor"`, store.read("noor", ...) returns None because this
store has no entry for "noor". The tool has no foreign root to read.

It becomes a finding the moment the store is constructed with more
than one user's root, which is exactly what the vulnerable variant
models.

Run the server over stdio:

    uv run python -m scenarios.mcp_confused_deputy.negative.server
"""

from fastmcp import FastMCP

from scenarios.mcp_confused_deputy.common import (
    PRINCIPAL_RASMUS,
    STORE,
    FileStore,
    Principal,
)

mcp = FastMCP("confused-deputy-negative")

PRINCIPAL: Principal = PRINCIPAL_RASMUS

# Per-user store: only the principal's root is loaded.
_OWN_ROOT = STORE.read(PRINCIPAL.user_id, "notes.md")
PER_USER_STORE = FileStore(
    {
        PRINCIPAL.user_id: {
            "notes.md": _OWN_ROOT or "",
        }
    }
)


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


@mcp.tool
def read_file(user_id: str, path: str) -> str:
    """Read a file for `user_id`."""
    return read_file_impl(PRINCIPAL, user_id, path, PER_USER_STORE)


if __name__ == "__main__":
    mcp.run(transport="stdio")
