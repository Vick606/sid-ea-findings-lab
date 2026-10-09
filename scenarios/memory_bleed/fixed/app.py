"""Scenario 02, fixed variant.

Identical to the vulnerable variant except for one line in agent_turn:
the history returned by store.load(session_id) is filtered to the
requesting user before being returned. The store remains unfiltered by
design — user binding is an authorization concern and belongs at the
caller, where the actor context is known.

Run this module directly to confirm the leak is gone:

    uv run python -m scenarios.memory_bleed.fixed.app
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

    Fix: the loaded history is filtered to entries written by the
    requesting user before being returned. The session_id remains the
    storage key, but it is no longer the sole credential for reads.
    """
    history = store.load(session_id)
    history = [e for e in history if e.user_id == user_id]  # <-- the fix
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

    if not leaked:
        print("  (no prior memory visible to rasmus)")


if __name__ == "__main__":
    main()
