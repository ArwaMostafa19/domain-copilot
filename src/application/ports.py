"""Interfaces the application layer needs from the outside world.

The application layer only knows these shapes. Real implementations (Ollama,
PostgreSQL) live in src/infrastructure, and tests plug in fakes.
"""

from dataclasses import dataclass
from typing import Protocol

from src.domain.documents import Chunk, DocumentMeta, DomainError, SafetyStep


class ProviderError(DomainError):
    """A language model or embedding provider could not answer."""


class Embedder(Protocol):
    """Turns texts into vectors. One model per index: never mix models."""

    model_name: str
    dimension: int

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one vector of length ``dimension`` for each text, in the same order."""
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
    status: str  # "ingested", "skipped" or "failed"
    chunks: int = 0
    steps: int = 0
    error: str | None = None