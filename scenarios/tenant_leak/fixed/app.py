"""Scenario 01, fixed variant.

Identical to the vulnerable variant except for one line in `retrieve`:
the candidate set is filtered by tenant AFTER expansion, not only during
the initial search. This closes the re-ranker ACL bypass because the
neighbor index can no longer introduce cross-tenant documents into the
final result.

Run this module directly to confirm the leak is gone:

    uv run python -m scenarios.tenant_leak.fixed.app
"""

from scenarios.tenant_leak.common import CORPUS, Document, VectorStore, expand, rerank


def retrieve(query: str, tenant: str, store: VectorStore) -> list[Document]:
    """Return the top-3 documents for a query.

    Fix: filter the expanded candidate set by tenant before re-ranking.
    The initial search filter is not sufficient because `expand` pulls
    in neighbors from the shared index.
    """
    ids = store.search(query, tenant=tenant, top_k=20)
    expanded = expand(store, ids)
    docs = [store.fetch(doc_id) for doc_id in expanded]
    docs = [d for d in docs if d.tenant == tenant]  # <-- the fix
    return rerank(query, docs)[:3]


def main() -> None:
    store = VectorStore(CORPUS)
    results = retrieve("security policy", tenant="tenant_a", store=store)

    print("Query: 'security policy' (as tenant_a)")
    for doc in results:
        marker = "LEAK" if doc.tenant != "tenant_a" else "ok"
        print(f"  [{marker}] {doc.tenant} {doc.id}: {doc.text}")


if __name__ == "__main__":
    main()
