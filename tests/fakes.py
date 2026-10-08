"""Deterministic test doubles for the ingestion ports."""

from __future__ import annotations

import hashlib

from src.domain.documents import Chunk, DocumentMeta, SafetyStep
from src.domain.llm import EmbeddingSpec
from src.domain.rag import Evidence


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


class FakeChunkSearch:
    """A ChunkSearch that returns pre-loaded evidence and records every call."""

    def __init__(
        self,
        dense: list[Evidence] | None = None,
        keyword: list[Evidence] | None = None,
    ) -> None:
        self.dense = list(dense or [])
        self.keyword = list(keyword or [])
        self.dense_calls: list[tuple] = []
        self.keyword_calls: list[tuple] = []

    def search_dense(self, tenant_id, vector, embedding_model, include_superseded, limit):
        self.dense_calls.append(
            (tenant_id, vector, embedding_model, include_superseded, limit)
        )
        return list(self.dense[:limit])

    def search_keyword(self, tenant_id, terms, embedding_model, include_superseded, limit):
        self.keyword_calls.append(
            (tenant_id, terms, embedding_model, include_superseded, limit)
        )
        return list(self.keyword[:limit])


class InMemoryUserRepository:
    def __init__(self) -> None:
        from src.application.ports import UserRecord

        self.users: dict[tuple[str, str], UserRecord] = {}
        self.by_id: dict[tuple[str, int], UserRecord] = {}

    def add(self, record) -> None:
        self.users[(record.tenant_id, record.username)] = record
        self.by_id[(record.tenant_id, record.id)] = record

    def get_by_username(self, tenant_id, username):
        return self.users.get((tenant_id, username))

    def get(self, tenant_id, user_id):
        return self.by_id.get((tenant_id, user_id))


class InMemoryRunRepository:
    def __init__(self) -> None:

        from src.application.ports import RunRecord, RunStepRecord

        self.runs: dict[tuple[str, str], RunRecord] = {}
        self.step_rows: dict[tuple[str, str], list[RunStepRecord]] = {}
        self._ids = []

    def create(self, tenant_id, user_id, question):
        import uuid

        rid = str(uuid.uuid4())
        rec = __import__("src.application.ports", fromlist=["RunRecord"]).RunRecord(
            id=rid,
            tenant_id=tenant_id,
            user_id=user_id,
            question=question,
            status="running",
            total_tokens=0,
            estimated_tokens=False,
        )
        self.runs[(tenant_id, rid)] = rec
        self.step_rows[(tenant_id, rid)] = []
        return rid

    def get(self, tenant_id, run_id):
        return self.runs.get((tenant_id, run_id))

    def set_status(self, tenant_id, run_id, status, total_tokens=None, estimated_tokens=None, finished=False):
        rec = self.runs.get((tenant_id, run_id))
        if rec:
            from dataclasses import replace

            self.runs[(tenant_id, run_id)] = replace(
                rec,
                status=status,
                total_tokens=total_tokens if total_tokens is not None else rec.total_tokens,
                estimated_tokens=estimated_tokens if estimated_tokens is not None else rec.estimated_tokens,
            )

    def add_step(self, tenant_id, run_id, step):
            self.step_rows.setdefault((tenant_id, run_id), []).append(step)

    def steps(self, tenant_id, run_id):
        return list(self.step_rows.get((tenant_id, run_id), []))

    def list_for_user(self, tenant_id, user_id):
        return [r for r in self.runs.values() if r.tenant_id == tenant_id and r.user_id == user_id]


class InMemoryWorkOrderRepository:
    def __init__(self) -> None:

        self.orders = []

    def create_draft(self, tenant_id, run_id, content):
        version = 1
        self.orders.append((tenant_id, run_id, version, content))
        return content

    def latest(self, tenant_id, run_id):
        from src.application.ports import WorkOrderRecord

        for o in reversed(self.orders):
            if o[0] == tenant_id and o[1] == run_id:
                return WorkOrderRecord(id="wo", run_id=run_id, version=o[2], status="draft", content=o[3])
        return None

    def set_status(self, tenant_id, work_order_id, status):
        pass


class InMemoryAuditLog:
    def __init__(self) -> None:
        self.events = []

    def record(self, tenant_id, actor_user_id, action, subject_type, subject_id, detail=None):
        self.events.append((tenant_id, actor_user_id, action, subject_type, subject_id, detail))


class InMemorySafetyRepository:
    def __init__(self, items=None) -> None:
        self.items = list(items or [])

    def required_for_documents(self, tenant_id, doc_ids):
        return list(self.items)
