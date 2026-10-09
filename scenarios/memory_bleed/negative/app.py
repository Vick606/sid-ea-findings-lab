"""Scenario 02, hard negative.

This variant uses the same agent_turn() function as the vulnerable
variant: it calls store.load(session_id) without filtering by user.
That code shape looks like a finding and the Semgrep rule flags it.

It is not a finding here because each user operates on their own
MemoryStore instance. Cross-user bleed requires a shared store; there
is no shared store in this deployment. The unfiltered load has nothing
foreign to return.

It becomes a finding the moment the deployment serves more than one
user from a single store instance, which is exactly what the
vulnerable variant models.

Run this module directly to confirm no leak:

    uv run python -m scenarios.memory_bleed.negative.app
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

    Identical to the vulnerable variant. The unfiltered load is safe
    here because the store only contains entries the user wrote.
    """
    history = store.load(session_id)
    store.append(session_id, user_id, tenant, message)
    return history


def main() -> None:
    # The only functional difference from the vulnerable variant:
    # each user has their own store rather than sharing one.
    noor_store = MemoryStore()
    rasmus_store = MemoryStore()
    session = "shared-session"

    agent_turn(session, "noor", "tenant_a", noor_store, "my SSN is 123-45-6789")
    leaked = agent_turn(session, "rasmus", "tenant_a", rasmus_store, "hello")

    print(f"Rasmus resumes session '{session}' (per-user store):")
    for entry in leaked:
        marker = "LEAK" if entry.user_id != "rasmus" else "ok"
        print(f"  [{marker}] {entry.user_id}: {entry.content}")
    if not leaked:
        print("  (no prior memory visible to rasmus)")


if __name__ == "__main__":
    main()
