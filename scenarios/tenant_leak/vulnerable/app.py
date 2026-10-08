"""Scenario 01, vulnerable variant.

Initial retrieval is tenant-filtered. The re-ranker expands the
candidate set with unfiltered nearest neighbors from a shared index,
which pulls in documents from other tenants. Nothing downstream
re-applies the tenant predicate.

Run this module directly to see the leak:

    uv run python -m scenarios.tenant_leak.vulnerable.app
"""

from scenarios.tenant_leak.common import CORPUS, Document, VectorStore, expand, rerank


def retrieve(query: str, tenant: str, store: VectorStore) -> list[Document]:
    """Return the top-3 documents for a query.

    Bug: `expand` adds each candidate's nearest neighbors from the
    shared index. The neighbor index has no tenant predicate, so
    tenant_b documents enter the candidate set and survive re-ranking.
    """
    ids = store.search(query, tenant=tenant, top_k=20)
    expanded = expand(store, ids)
    docs = [store.fetch(doc_id) for doc_id in expanded]
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
