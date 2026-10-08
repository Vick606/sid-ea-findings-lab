"""Scenario 01, hard negative.

This variant uses the same `retrieve()` function as the vulnerable
variant: initial tenant-filtered search followed by unfiltered
neighbor expansion, no post-rerank ACL. That code pattern looks like
a finding and would be flagged by a naive rule.

It is not a finding here because the store is constructed per-tenant.
The deployment serves one tenant per store instance, so the neighbor
index contains only documents the actor is already authorized for.
Unfiltered expansion has no cross-tenant documents to introduce.

It becomes a finding the moment the deployment serves two tenants from
one store instance, which is exactly what the vulnerable variant
models.

Run this module directly to confirm no leak:

    uv run python -m scenarios.tenant_leak.negative.app
"""

from scenarios.tenant_leak.common import CORPUS, Document, VectorStore, expand, rerank


def retrieve(query: str, tenant: str, store: VectorStore) -> list[Document]:
    """Return the top-3 documents for a query.

    Identical to the vulnerable variant. The unfiltered neighbor
    expansion is safe here because the store only contains documents
    the actor is authorized for.
    """
    ids = store.search(query, tenant=tenant, top_k=20)
    expanded = expand(store, ids)
    docs = [store.fetch(doc_id) for doc_id in expanded]
    return rerank(query, docs)[:3]


def main() -> None:
    # The only functional difference from the vulnerable variant:
    # build a per-tenant store rather than a shared one.
    tenant_a_corpus = [d for d in CORPUS if d.tenant == "tenant_a"]
    store = VectorStore(tenant_a_corpus)
    results = retrieve("security policy", tenant="tenant_a", store=store)

    print("Query: 'security policy' (as tenant_a, per-tenant store)")
    for doc in results:
        marker = "LEAK" if doc.tenant != "tenant_a" else "ok"
        print(f"  [{marker}] {doc.tenant} {doc.id}: {doc.text}")


if __name__ == "__main__":
    main()
