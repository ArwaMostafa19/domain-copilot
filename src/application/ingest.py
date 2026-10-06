"""Read, embed and store one corpus file at a time."""

from __future__ import annotations

import collections
import importlib
from pathlib import Path

from src.application.chunk import DEFAULT_MAX_CHARS, chunk_document
from src.application.ports import (
    DocumentRepository,
    Embedder,
    IngestResult,
)
from src.application.safety_steps import extract_safety_steps
from src.domain.documents import (
    DomainError,
    ExtractedDocument,
    ExtractionError,
)
from src.domain.llm import ProviderResponseError


def ingest_file(
    path: Path,
    embedder: Embedder,
    repository: DocumentRepository,
    max_chars: int = DEFAULT_MAX_CHARS,
) -> IngestResult:
    """Extract, embed and store one file, or report why it was not stored."""
    try:
        document = _extract(path)
    except ExtractionError as error:
        return IngestResult(path=path.as_posix(), status="failed", error=str(error))
    meta = document.meta
    if repository.stored_fingerprint(meta) == meta.content_sha256:
        return IngestResult(path=path.as_posix(), status="skipped")
    try:
        chunks = chunk_document(document, max_chars=max_chars)
        steps = extract_safety_steps(document)
        vectors = embedder.embed(
            [f"{chunk.context}\n{chunk.text}" for chunk in chunks]
        )
        _check_vectors(vectors, len(chunks), embedder)
        repository.replace_document(meta, chunks, vectors, steps, embedder.model_name)
    except DomainError as error:
        repository.mark_failed(meta, str(error))
        return IngestResult(path=path.as_posix(), status="failed", error=str(error))
    return IngestResult(
        path=path.as_posix(),
        status="ingested",
        chunks=len(chunks),
        steps=len(steps),
    )


def ingest_files(
    paths: collections.abc.Iterable[Path],
    embedder: Embedder,
    repository: DocumentRepository,
    max_chars: int = DEFAULT_MAX_CHARS,
) -> list[IngestResult]:
    """Ingest every path in order; a failed file does not stop the run."""
    return [ingest_file(path, embedder, repository, max_chars) for path in paths]


def _extract(path: Path) -> ExtractedDocument:
    """Read the file through the extractor the application cannot import."""
    extractors = importlib.import_module("src.infrastructure.extractors")
    return extractors.extract(path)


def _check_vectors(
    vectors: list[list[float]], chunks: int, embedder: Embedder
) -> None:
    """Reject an embedding answer that does not match the chunks one by one."""
    if len(vectors) != chunks:
        raise ProviderResponseError(
            embedder.model_name,
            f"embedder {embedder.model_name!r} returned {len(vectors)} vectors "
            f"for {chunks} chunks",
        )
    for index, vector in enumerate(vectors):
        if len(vector) != embedder.dimension:
            raise ProviderResponseError(
                embedder.model_name,
                f"embedder {embedder.model_name!r} vector {index} has "
                f"{len(vector)} values, expected {embedder.dimension}",
            )