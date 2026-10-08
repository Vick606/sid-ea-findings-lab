"""Shared retrieval primitives for the tenant-leak scenario.

Deterministic and dependency-light: embeddings are a bag-of-words
projection, the re-ranker is cosine similarity, and there is no network
or model download. The point is reproducible behavior for tests, not
semantic quality.
"""

import hashlib
from dataclasses import dataclass

import numpy as np

EMBED_DIM = 64


def embed(text: str) -> np.ndarray:
    """Deterministic bag-of-words embedding.

    Each token is hashed to one of EMBED_DIM buckets. The vector is
    L2-normalized so cosine similarity reduces to a dot product.
    """
    vec = np.zeros(EMBED_DIM, dtype=np.float32)
    for token in text.lower().split():
        bucket = int(hashlib.sha256(token.encode()).hexdigest(), 16) % EMBED_DIM
        vec[bucket] += 1.0
    norm = float(np.linalg.norm(vec))
    if norm > 0:
        vec /= norm
    return vec


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))


@dataclass(frozen=True)
class Document:
    id: str
    tenant: str
    text: str


class VectorStore:
    """In-memory vector store with tenant-aware search and unfiltered
    neighbor expansion.

    The neighbor index is deliberately tenant-agnostic. That is the sink
    of the scenario-01 vulnerability: the vulnerable caller expands the
    tenant-filtered candidate set with unfiltered neighbors.
    """

    def __init__(self, docs: list[Document], neighbor_k: int = 3) -> None:
        self._docs = {d.id: d for d in docs}
        self._embs = {d.id: embed(d.text) for d in docs}
        self._neighbor_k = neighbor_k
        self._neighbors = self._build_neighbors()

    def _build_neighbors(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for doc_id in self._docs:
            sims = [
                (other, cosine(self._embs[doc_id], self._embs[other]))
                for other in self._docs
                if other != doc_id
            ]
            sims.sort(key=lambda pair: pair[1], reverse=True)
            out[doc_id] = [i for i, _ in sims[: self._neighbor_k]]
        return out

    def search(self, query: str, tenant: str, top_k: int = 20) -> list[str]:
        """Tenant-filtered similarity search. Returns document IDs."""
        q = embed(query)
        sims = [(doc_id, cosine(q, emb)) for doc_id, emb in self._embs.items()]
        sims.sort(key=lambda pair: pair[1], reverse=True)
        return [i for i, _ in sims if self._docs[i].tenant == tenant][:top_k]

    def fetch(self, doc_id: str) -> Document:
        return self._docs[doc_id]

    def neighbors(self, doc_id: str) -> list[str]:
        """Nearest neighbors by embedding similarity.

        No tenant filter. This is intentional: the vulnerable variant
        relies on this gap, the fixed variant compensates for it, and
        the negative variant is safe because it runs against a
        per-tenant store.
        """
        return list(self._neighbors.get(doc_id, []))


def expand(store: VectorStore, ids: list[str]) -> list[str]:
    """Grow a candidate set with each document's nearest neighbors."""
    seen: set[str] = set(ids)
    for doc_id in ids:
        seen.update(store.neighbors(doc_id))
    return list(seen)


def rerank(query: str, docs: list[Document]) -> list[Document]:
    """Deterministic re-rank by query-document cosine similarity."""
    q = embed(query)
    scored = [(d, cosine(q, embed(d.text))) for d in docs]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return [d for d, _ in scored]


# Two tenants, four documents. tenant_a and tenant_b each have a
# "security policy" document, so a tenant_a query surfaces tenant_b's
# security policy as a nearest neighbor.
CORPUS: list[Document] = [
    Document(id="a-1", tenant="tenant_a", text="tenant a security policy overview"),
    Document(id="a-2", tenant="tenant_a", text="tenant a leave and travel handbook"),
    Document(
        id="b-1",
        tenant="tenant_b",
        text="tenant b security policy with incident response contacts",
    ),
    Document(id="b-2", tenant="tenant_b", text="tenant b confidential acquisition plan q3"),
]
