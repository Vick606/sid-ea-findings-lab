"""Deterministic tests for scenario 01.

The vulnerable, fixed, and negative variants share code by design. The
tests pin the security-relevant behavior of each: what leaks, what does
not, and — critically — why the negative is safe despite sharing the
vulnerable `retrieve()` function.

The fourth test is the contrast test. It runs the negative variant's
`retrieve()` against the shared store and asserts it does leak. This
proves the negative is safe because of the store contents, not because
of the code. A code-pattern matcher cannot distinguish the two cases;
the deployment context is what matters.
"""

from scenarios.tenant_leak.common import CORPUS, VectorStore
from scenarios.tenant_leak.fixed import app as fixed_app
from scenarios.tenant_leak.negative import app as negative_app
from scenarios.tenant_leak.vulnerable import app as vulnerable_app


def _shared_store() -> VectorStore:
    """Shared index: tenant_a and tenant_b documents in one store."""
    return VectorStore(CORPUS)


def _tenant_a_store() -> VectorStore:
    """Per-tenant index: only tenant_a documents are present."""
    return VectorStore([d for d in CORPUS if d.tenant == "tenant_a"])


def test_vulnerable_leaks_tenant_b_doc() -> None:
    """Vulnerable retrieve() against the shared store returns a tenant_b doc."""
    results = vulnerable_app.retrieve("security policy", tenant="tenant_a", store=_shared_store())
    assert any(d.tenant == "tenant_b" for d in results), (
        "expected a cross-tenant document in the vulnerable result set"
    )


def test_fixed_does_not_leak() -> None:
    """Fixed retrieve() filters the expanded candidate set by tenant."""
    results = fixed_app.retrieve("security policy", tenant="tenant_a", store=_shared_store())
    assert all(d.tenant == "tenant_a" for d in results), (
        "fixed variant returned a cross-tenant document"
    )


def test_negative_does_not_leak() -> None:
    """Negative retrieve() against a per-tenant store cannot leak."""
    results = negative_app.retrieve("security policy", tenant="tenant_a", store=_tenant_a_store())
    assert all(d.tenant == "tenant_a" for d in results), (
        "negative variant returned a document from another tenant"
    )


def test_negative_function_leaks_against_shared_store() -> None:
    """Contrast test: the negative's retrieve() is code-identical to the
    vulnerable one.

    Run it against the shared store and it leaks. This proves the
    negative is not a finding because of deployment context, not
    because of the code. Any code-pattern-based finding on the negative
    is therefore a false positive.
    """
    results = negative_app.retrieve("security policy", tenant="tenant_a", store=_shared_store())
    assert any(d.tenant == "tenant_b" for d in results), (
        "expected the negative's retrieve() to leak when the store is shared; "
        "if it does not, the negative is safe for the wrong reason and the "
        "contrast test is no longer meaningful"
    )
