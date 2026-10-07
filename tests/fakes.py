"""Deterministic test doubles for the ingestion ports."""

from __future__ import annotations

import hashlib

from src.domain.documents import Chunk, DocumentMeta, SafetyStep
from src.domain.llm import EmbeddingSpec


class FakeEmbedder:
    """Vectors that depend only on the sha256 of each text."""

    def __init__(self, dimension: int = 768) -> None:
        self.dimension = dimension
        self.model_name = "fake-embedder"
        self.calls: list[list[str]] = []

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one deterministic vector per text, remembering every batch."""
        self.calls.append(list(texts))
        return [self._vector(text) for text in texts]

    def _vector(self, text: str) -> list[float]:
        """One vector of ``dimension`` values grown from the sha256 of text."""
        values: list[float] = []
        counter = 0
        while len(values) < self.dimension:
            block = hashlib.sha256(f"{text}:{counter}".encode()).digest()
            values.extend(byte / 255.0 for byte in block)
            counter += 1
        return values[: self.dimension]


class InMemoryRepository:
    """A DocumentRepository that keeps one dict per document, keyed like SQL."""

    def __init__(self) -> None:
        self.rows: dict[tuple[str, str, str], dict[str, object]] = {}
        self.failures: list[tuple[DocumentMeta, str]] = []

    def stored_fingerprint(self, meta: DocumentMeta) -> str | None:
        """The sha256 of the ingested version, or None when there is none."""
        row = self.rows.get(_key(meta))
        if row is None or row["ingest_status"] != "ingested":
            return None
        return str(row["content_sha256"])

    def replace_document(
        self,
        meta: DocumentMeta,
        chunks: list[Chunk],
        embeddings: list[list[float]],
        steps: list[SafetyStep],
        embedding_model: str,
    ) -> None:
        """Store the new version, replacing whatever the key held before."""
        self.rows[_key(meta)] = {
            "meta": meta,
            "content_sha256": meta.content_sha256,
            "ingest_status": "ingested",
            "ingest_error": None,
            "chunks": list(chunks),
            "embeddings": [list(vector) for vector in embeddings],
            "steps": list(steps),
            "embedding_model": embedding_model,
        }

    def mark_failed(self, meta: DocumentMeta, error: str) -> None:
        """Record the error, keeping an older good version intact."""
        self.failures.append((meta, error))
        row = self.rows.get(_key(meta))
        if row is None:
            self.rows[_key(meta)] = {
                "meta": meta,
                "content_sha256": meta.content_sha256,
                "ingest_status": "failed",
                "ingest_error": error,
                "chunks": [],
                "embeddings": [],
                "steps": [],
                "embedding_model": None,
            }
            return
        row["ingest_error"] = error

    def get(self, tenant_id: str, doc_id: str, source_format: str) -> dict[str, object] | None:
        """The stored row of one document, or None when it was never stored."""
        return self.rows.get((tenant_id, doc_id, source_format))


def _key(meta: DocumentMeta) -> tuple[str, str, str]:
    """The unique key documents carry in PostgreSQL."""
    return (meta.tenant_id, meta.doc_id, meta.source_format)


class InMemoryEmbeddingIndexRegistry:
    """An EmbeddingIndexRegistry that keeps the first registered spec."""

    def __init__(self) -> None:
        self.spec: EmbeddingSpec | None = None

    def get(self) -> EmbeddingSpec | None:
        return self.spec

    def register(self, spec: EmbeddingSpec) -> None:
        if self.spec is None:
            self.spec = spec
