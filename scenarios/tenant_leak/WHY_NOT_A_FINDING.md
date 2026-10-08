# Why the negative variant is not a finding

## What it looks like

`scenarios/tenant_leak/negative/app.py` contains this function:

```python
def retrieve(query: str, tenant: str, store: VectorStore) -> list[Document]:
    ids = store.search(query, tenant=tenant, top_k=20)
    expanded = expand(store, ids)
    docs = [store.fetch(doc_id) for doc_id in expanded]
    return rerank(query, docs)[:3]
