# Scenario 01 — Cross-tenant RAG leak (SID)

**Class:** Sensitive Information Disclosure
**OWASP LLM:** LLM02:2025
**Finding ID:** SID-2026-001

## Summary

Initial vector retrieval is tenant-filtered. The cross-encoder-style
re-ranker then expands the candidate set with each document's nearest
neighbors from a shared index. The neighbor index has no tenant
predicate, so a tenant_a query surfaces tenant_b documents as
high-similarity neighbors. Nothing downstream re-applies the tenant
filter, so the leak reaches the model context.

## Root cause

The tenant predicate is applied at one point (initial search) and
assumed to hold downstream. It does not: the re-ranker introduces new
document IDs from an unfiltered index. The control is scoped too
narrowly.

## Variants

| Variant | Behavior |
|---|---|
| `vulnerable/` | Unfiltered neighbor expansion, no post-rerank ACL |
| `fixed/` | Post-rerank tenant filter (one line) |
| `negative/` | Same code as vulnerable, but the store is per-tenant |

## Why the negative is not a finding

`negative/app.py` uses the **same `retrieve()` function** as the
vulnerable variant: tenant-filtered initial search, unfiltered neighbor
expansion, no post-rerank ACL. That code pattern looks like a finding
and a naive rule would flag it.

It is not a finding here because the deployment serves one tenant per
store instance. The neighbor index contains only documents the actor is
already authorized for, so unfiltered expansion has no cross-tenant
documents to introduce. The only functional difference from the
vulnerable variant is the store construction in `main()`.

This becomes a finding the moment the deployment serves two tenants
from one store instance — which is exactly what `vulnerable/app.py`
models.

## Verification

```
uv run python -m scenarios.tenant_leak.vulnerable.app
```

Expected: two `ok` lines and one `LEAK` line.
