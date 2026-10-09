"""Deterministic tests for scenario 02.

The vulnerable, fixed, and negative variants share agent_turn() by
design. The tests pin the security-relevant behavior of each: what
leaks, what does not, and — critically — why the negative is safe
despite sharing the vulnerable function.

The fourth test is the contrast test. It runs the negative variant's
agent_turn() against a shared store and asserts it does leak. This
proves the negative is safe because of store construction, not code.
"""

from scenarios.memory_bleed.common import MemoryStore
from scenarios.memory_bleed.fixed import app as fixed_app
from scenarios.memory_bleed.negative import app as negative_app
from scenarios.memory_bleed.vulnerable import app as vulnerable_app

SESSION = "shared-session"
NOOR_SSN = "my SSN is 123-45-6789"


def _seed_shared_store() -> MemoryStore:
    store = MemoryStore()
    store.append(SESSION, "noor", "tenant_a", NOOR_SSN)
    return store


def _seed_per_user_store(user_id: str) -> MemoryStore:
    store = MemoryStore()
    if user_id == "noor":
        store.append(SESSION, "noor", "tenant_a", NOOR_SSN)
    return store


def test_vulnerable_leaks_noor_entry_to_rasmus() -> None:
    store = _seed_shared_store()
    history = vulnerable_app.agent_turn(SESSION, "rasmus", "tenant_a", store, "hello")
    assert any(e.user_id == "noor" for e in history), (
        "expected the vulnerable variant to expose noor's entry to rasmus"
    )


def test_fixed_does_not_leak() -> None:
    store = _seed_shared_store()
    history = fixed_app.agent_turn(SESSION, "rasmus", "tenant_a", store, "hello")
    assert all(e.user_id == "rasmus" for e in history), (
        "fixed variant returned another user's memory"
    )


def test_negative_does_not_leak() -> None:
    store = _seed_per_user_store("rasmus")
    history = negative_app.agent_turn(SESSION, "rasmus", "tenant_a", store, "hello")
    assert all(e.user_id == "rasmus" for e in history), (
        "negative variant returned memory from another user"
    )


def test_negative_function_leaks_against_shared_store() -> None:
    """Contrast test: the negative's agent_turn() is code-identical to
    the vulnerable one.

    Run it against a shared store and it leaks. This proves the
    negative is not a finding because of deployment context, not code.
    """
    store = _seed_shared_store()
    history = negative_app.agent_turn(SESSION, "rasmus", "tenant_a", store, "hello")
    assert any(e.user_id == "noor" for e in history), (
        "expected the negative's agent_turn() to leak against a shared store; "
        "if it does not, the negative is safe for the wrong reason"
    )
