"""Shared memory primitives for the memory-bleed scenario.

A MemoryStore holds conversation memory for a stateful agent. Entries
are keyed by session_id, in the order they were appended. The store
does not enforce user binding: session_id is treated as the sole
credential. Callers that share a store across users must filter.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryEntry:
    session_id: str
    user_id: str
    tenant: str
    content: str


class MemoryStore:
    """Append-only memory indexed by session_id.

    The store is intentionally simple. It knows nothing about users,
    tenancy, or authorization. Those concerns belong to the caller.
    """

    def __init__(self) -> None:
        self._entries: dict[str, list[MemoryEntry]] = {}

    def append(self, session_id: str, user_id: str, tenant: str, content: str) -> None:
        entry = MemoryEntry(
            session_id=session_id,
            user_id=user_id,
            tenant=tenant,
            content=content,
        )
        self._entries.setdefault(session_id, []).append(entry)

    def load(self, session_id: str) -> list[MemoryEntry]:
        """Return every entry ever appended for this session_id.

        No user check. No tenant check. The session_id is the only
        selector. A caller that shares a store across users gets back
        entries written by other users.
        """
        return list(self._entries.get(session_id, []))
