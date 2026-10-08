# Trace — SID-2026-001

Source-to-sink path for the cross-tenant RAG leak, with the
authorization context that makes it a finding.

## Actor

The actor is `tenant_a_user`. They are authenticated, hold the
`rag:read` scope, and their purpose is `answer_internal_query`. Their
`document_acl` permits documents tagged `tenant_a_only`. Their
`permitted_recipients` are members of `tenant_a`.

Two facts matter for this trace:

1. The actor is *authorized* for `rag:read`. This is not an
   unauthenticated request.
2. The actor is *not* authorized for anything tagged `tenant_b_only`.

Any document returned to this actor that carries a `tenant_b_only`
ACL is a disclosure.

## Trust boundary crossed

`tenant_isolation`. The boundary sits between the tenant's user
context and the shared vector index. The invariant the boundary is
supposed to preserve:

> No document tagged `tenant_b_only` is returned to a `tenant_a`
> actor under any code path.

The vulnerable variant violates this invariant.

## Flow

### Source

`scenarios/tenant_leak/vulnerable/app.py:24` — the user query enters
`retrieve()`. It is untrusted in the sense that it may shape which
documents are surfaced, but the leak does not depend on adversarial
input. An ordinary query reaches the vulnerable path.

### Step 1 — Embed

`scenarios/tenant_leak/common.py:19` — the query is embedded into a
64-dimensional bag-of-words vector. Deterministic. No security
significance on its own.

### Step 2 — Vector search (control applied)

`scenarios/tenant_leak/common.py:79` — `store.search(query, tenant=...)`
returns the top-K document IDs filtered by `tenant`. This is the
control. It works. The result set contains only `tenant_a` documents.

### Step 3 — Expand (the sink of the control)

`scenarios/tenant_leak/common.py:98` — `expand()` calls
`store.neighbors()` for each candidate. The neighbor index was built
over the entire shared store and carries no tenant predicate. Each
`tenant_a` document's nearest neighbor includes a `tenant_b` document
because both contain the phrase "security policy". The expanded set
therefore contains document IDs the actor is not authorized for.

The initial filter is not enough because it was applied at a different
stage. The control's scope does not cover this stage.

### Step 4 — Re-rank

`scenarios/tenant_leak/common.py:108` — the re-ranker scores the
expanded set by query similarity. The `tenant_b` "security policy"
document scores high because it shares vocabulary with the query. The
re-ranker has no authorization awareness and preserves the leak.

### Sink

`scenarios/tenant_leak/vulnerable/app.py:26` — the top-3 documents
are returned as the retrieval result. The caller (not shown here, but
implied by the signature) places these documents in the model's
prompt context. The `tenant_b` document is disclosed.

## Authorization reasoning

The finding is not "unfiltered retrieval is a bug." Unfiltered
retrieval is common and often correct. The finding is that the tenant
predicate is applied at one stage, assumed to hold for the whole
pipeline, and does not hold at a later stage that introduces new
document IDs from an unfiltered index.

The control is **present** and **bypassed**, not absent. That matters
for severity: the deployment believed it had tenant isolation.
Nothing in the response indicates otherwise. This is a silent
cross-tenant disclosure in a pipeline that was designed to prevent it.

## Why this is HIGH and not CRITICAL

- The actor is authenticated.
- The disclosure is bounded by the neighbor index (top-K nearest
  neighbors per candidate), not by arbitrary document access.
- The disclosure is silent but the volume is bounded per query.

It would be CRITICAL if the actor could enumerate the index directly,
if the leak scale were unbounded, or if the exposed documents carried
secrets with immediate operational value. None of those conditions
hold in this scenario.

## What the fixed variant changes

One line at `scenarios/tenant_leak/fixed/app.py:25`:

    docs = [d for d in docs if d.tenant == tenant]

The fix re-applies the tenant predicate *after* expansion. The
control now covers the stage that was previously outside its scope.
The initial search filter remains — defence in depth — but it is no
longer the only place the predicate is enforced.
