"""Interfaces the application layer needs from the outside world.

The application layer only knows these shapes. Real implementations (Ollama,
PostgreSQL) live in src/infrastructure, and tests plug in fakes.
"""

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Protocol

from src.domain.documents import Chunk, DocumentMeta, SafetyStep
from src.domain.llm import (
    CompletionRequest,
    CompletionResult,
    EmbeddingResult,
    EmbeddingSpec,
    StreamEvent,
)
from src.domain.workflow import SafetyStepRecord


class Embedder(Protocol):
    """Turns texts into vectors. One model per index: never mix models."""

    model_name: str
    dimension: int

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one vector of length ``dimension`` for each text, in the same order."""
        ...


class LLMProvider(Protocol):
    """One interface for completion, streaming, tool calling (request.tools) and embeddings.

    Every result carries token usage. Adapters raise ProviderError subclasses only.
    A stream() adapter must check the HTTP status before yielding its first event.
    """

    name: str

    def complete(self, request: CompletionRequest) -> CompletionResult: ...

    def stream(self, request: CompletionRequest) -> Iterator[StreamEvent]: ...

    def embed(self, texts: Sequence[str]) -> EmbeddingResult: ...


class EmbeddingIndexRegistry(Protocol):
    """Remembers which embedding model built the index (one global row)."""

    def get(self) -> EmbeddingSpec | None: ...

    def register(self, spec: EmbeddingSpec) -> None:
        """Insert if empty. Must NOT overwrite an existing row (ON CONFLICT DO NOTHING)."""
        ...


class DocumentRepository(Protocol):
    """Stores ingested documents. Every call runs inside the document's own tenant."""

    def stored_fingerprint(self, meta: DocumentMeta) -> str | None:
        """Return the sha256 of the version that was ingested successfully, or None."""
        ...

    def replace_document(
        self,
        meta: DocumentMeta,
        chunks: list[Chunk],
        embeddings: list[list[float]],
        steps: list[SafetyStep],
        embedding_model: str,
    ) -> None:
        """Atomically replace everything stored for this document with the new version."""
        ...

    def mark_failed(self, meta: DocumentMeta, error: str) -> None:
        """Record that ingesting this document failed, without losing a good older version."""
        ...


@dataclass(frozen=True)
class IngestResult:
    """What happened to one file during ingestion."""

    path: str
    status: str
    chunks: int = 0
    steps: int = 0
    error: str | None = None


@dataclass(frozen=True)
class UserRecord:
    """One application user, as stored in the ``users`` table."""

    id: int
    tenant_id: str
    username: str
    role: str
    active: bool
    password_hash: str = ""


@dataclass(frozen=True)
class RunRecord:
    """One copilot run and its accumulated token usage."""

    id: str
    tenant_id: str
    user_id: int
    question: str
    status: str
    total_tokens: int
    estimated_tokens: bool


@dataclass(frozen=True)
class RunStepRecord:
    """One agent step. ``summary`` never contains a prompt or a raw completion."""

    ordinal: int
    agent: str
    tools_used: tuple[str, ...] = ()
    evidence_ids: tuple[int, ...] = ()
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated: bool = False
    duration_ms: int = 0
    outcome: str = ""
    summary: str | None = None


@dataclass(frozen=True)
class WorkOrderRecord:
    """A stored work order version. ``content`` is the draft as JSON."""

    id: str
    run_id: str
    version: int
    status: str
    content: dict[str, object]


class RunRepository(Protocol):
    """Persistence for runs and their steps, always inside one tenant."""

    def create(self, tenant_id: str, user_id: int, question: str) -> str: ...

    def get(self, tenant_id: str, run_id: str) -> RunRecord | None: ...

    def set_status(
        self,
        tenant_id: str,
        run_id: str,
        status: str,
        *,
        total_tokens: int | None = None,
        estimated_tokens: bool | None = None,
        finished: bool = False,
    ) -> None: ...

    def add_step(self, tenant_id: str, run_id: str, step: RunStepRecord) -> None: ...

    def steps(self, tenant_id: str, run_id: str) -> list[RunStepRecord]: ...

    def list_for_user(self, tenant_id: str, user_id: int) -> list[RunRecord]: ...

    def list_for_tenant(
        self, tenant_id: str, status: str | None = None
    ) -> list[RunRecord]: ...


class WorkOrderRepository(Protocol):
    """Persistence for work orders; a new draft always increments the version."""

    def create_draft(
        self, tenant_id: str, run_id: str, content: dict[str, object]
    ) -> dict[str, object]: ...

    def latest(self, tenant_id: str, run_id: str) -> WorkOrderRecord | None: ...

    def set_status(self, tenant_id: str, work_order_id: str, status: str) -> None: ...


class AuditLog(Protocol):
    """Append-only audit records."""

    def record(
        self,
        tenant_id: str,
        actor_user_id: int | None,
        action: str,
        subject_type: str,
        subject_id: str | None,
        detail: dict[str, object] | None = None,
    ) -> None: ...


class SafetyPrerequisiteRepository(Protocol):
    """Reads the ``safety_prerequisites`` table; the model never supplies these."""

    def required_for_documents(
        self, tenant_id: str, doc_ids: Sequence[str]
    ) -> list[SafetyStepRecord]: ...


class UserRepository(Protocol):
    """Reads application users (tenant-scoped)."""

    def get_by_username(self, tenant_id: str, username: str) -> UserRecord | None: ...

    def get(self, tenant_id: str, user_id: int) -> UserRecord | None: ...


@dataclass(frozen=True)
class AskLogRecord:
    """One user question and answer interaction log entry."""

    id: int | None
    tenant_id: str
    user_id: int | None
    correlation_id: str | None
    question: str
    answer_text: str
    refused: bool
    reason: str | None
    citations: Sequence[dict[str, object]]
    prompt_tokens: int
    completion_tokens: int
    estimated: bool
    created_at: str | None = None


class AskLogRepository(Protocol):
    """Persistence for user question ask history."""

    def save(self, tenant_id: str, record: AskLogRecord) -> int: ...

    def list_for_user(self, tenant_id: str, user_id: int) -> list[AskLogRecord]: ...

