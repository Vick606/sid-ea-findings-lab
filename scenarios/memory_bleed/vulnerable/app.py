"""Scenario 02, vulnerable variant.

Agent memory is keyed by session_id only. A second user in the same
tenant who supplies the first user's session_id reads the first
user's memory, including anything sensitive the first user stored.

Run this module directly to reproduce the leak:

    uv run python -m scenarios.memory_bleed.vulnerable.app
"""

from scenarios.memory_bleed.common import MemoryEntry, MemoryStore


def agent_turn(
    session_id: str,
    user_id: str,
    tenant: str,
    store: MemoryStore,
    message: str,
) -> list[MemoryEntry]:
    """Run one turn of a stateful agent.

    Loads the history for `session_id`, appends the new message, and
    returns the history that would be sent to the model.

    Bug: `store.load(session_id)` is keyed by session_id only. It does
    not verify that the requesting user owns the session. Two users in
    the same tenant sharing a store can read each other's memory by
    supplying the same session_id.
    """
    history = store.load(session_id)
    store.append(session_id, user_id, tenant, message)
    return history


def main() -> None:
    store = MemoryStore()
    session = "shared-session"

    # Noor stores sensitive memory.
    agent_turn(session, "noor", "tenant_a", store, "my SSN is 123-45-6789")

    # Rasmus resumes the same session_id.
    leaked = agent_turn(session, "rasmus", "tenant_a", store, "hello")

    print(f"Rasmus resumes session '{session}':")
    for entry in leaked:
        marker = "LEAK" if entry.user_id != "rasmus" else "ok"
        print(f"  [{marker}] {entry.user_id}: {entry.content}")


if __name__ == "__main__":
    main()
