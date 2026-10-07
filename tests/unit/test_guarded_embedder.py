"""GuardedEmbedder checks provider answers and feeds ingestion as an Embedder."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from src.application.embedding import GuardedEmbedder
from src.application.embedding_guard import EmbeddingGuard
from src.application.ingest import ingest_file
from src.domain.llm import (
    EmbeddingModelMismatchError,
    EmbeddingResult,
    EmbeddingSpec,
    TokenUsage,
)
from src.infrastructure.providers.fake import FakeLLMProvider

TESTS_ROOT = Path(__file__).resolve().parents[1]
if str(TESTS_ROOT) not in sys.path:
    sys.path.insert(0, str(TESTS_ROOT))

from fakes import InMemoryEmbeddingIndexRegistry, InMemoryRepository

SPEC = EmbeddingSpec("fake-embedding", 768)


class FixedUsageProvider:
    """A provider that embeds deterministically and reports fixed usage."""

    name = "fake"

    def __init__(self, estimated: bool = True, model: str = SPEC.model) -> None:
        self.estimated = estimated
        self.model = model
        self.calls = 0
        self.total_texts = 0

    def embed(self, texts):
        self.calls += 1
        self.total_texts += len(texts)
        vectors = tuple((0.25,) * SPEC.dimensions for _ in texts)
        return EmbeddingResult(
            vectors,
            self.model,
            SPEC.dimensions,
            TokenUsage(prompt_tokens=10, completion_tokens=2, estimated=self.estimated),
            self.name,
        )

    def complete(self, request):
        raise AssertionError("this test never completes a chat")

    def stream(self, request):
        raise AssertionError("this test never streams a chat")


def guarded(provider):
    """A GuardedEmbedder over an ensured guard."""
    guard = EmbeddingGuard(InMemoryEmbeddingIndexRegistry())
    guard.ensure(SPEC)
    return GuardedEmbedder(provider, guard, SPEC)


def test_empty_input_returns_empty_without_calling_the_provider() -> None:
    provider = FakeLLMProvider()
    embedder = guarded(provider)

    assert embedder.embed([]) == []
    assert provider.calls == []
    assert embedder.total_usage.total_tokens == 0


def test_the_output_type_matches_the_embedder_protocol() -> None:
    embedder = guarded(FakeLLMProvider())

    vectors = embedder.embed(["first", "second", "third"])

    assert embedder.model_name == SPEC.model
    assert embedder.dimension == SPEC.dimensions
    assert isinstance(vectors, list)
    assert all(isinstance(vector, list) for vector in vectors)
    assert len(vectors) == 3
    assert all(len(vector) == SPEC.dimensions for vector in vectors)


def test_usage_accumulates_across_batches() -> None:
    provider = FixedUsageProvider()
    embedder = guarded(provider)

    embedder.embed(["a", "b", "c"])
    embedder.embed(["d", "e"])

    usage = embedder.total_usage
    assert usage.prompt_tokens == 20
    assert usage.completion_tokens == 4
    assert usage.estimated is True
    assert provider.calls == 2
    assert provider.total_texts == 5


def test_usage_stays_not_estimated_while_every_batch_reports_real_usage() -> None:
    embedder = guarded(FixedUsageProvider(estimated=False))

    embedder.embed(["a"])

    assert embedder.total_usage.estimated is False


def test_usage_is_estimated_once_any_batch_was_estimated() -> None:
    provider = FixedUsageProvider(estimated=False)
    embedder = guarded(provider)
    embedder.embed(["a"])
    assert embedder.total_usage.estimated is False

    provider.estimated = True
    embedder.embed(["b"])

    assert embedder.total_usage.estimated is True


def test_a_provider_answering_with_the_wrong_model_is_rejected() -> None:
    with pytest.raises(EmbeddingModelMismatchError):
        guarded(FixedUsageProvider(model="other-model")).embed(["text"])


def test_ingest_file_works_end_to_end_with_a_guarded_embedder(tmp_path: Path) -> None:
    path = write_document(tmp_path, "TEST-GUARDED")
    spec = EmbeddingSpec("guarded-model", 768)
    guard = EmbeddingGuard(InMemoryEmbeddingIndexRegistry())
    guard.ensure(spec)
    provider = FakeLLMProvider(embedding_model=spec.model, embedding_dimensions=spec.dimensions)
    embedder = GuardedEmbedder(provider, guard, spec)
    repository = InMemoryRepository()

    result = ingest_file(path, embedder, repository)

    assert result.status == "ingested"
    row = repository.get("tenant-alpha", "TEST-GUARDED", "markdown")
    assert row is not None
    assert row["ingest_status"] == "ingested"
    assert row["embedding_model"] == "guarded-model"
    assert len(row["embeddings"]) == result.chunks
    assert embedder.total_usage.total_tokens > 0


def write_document(folder: Path, doc_id: str) -> Path:
    """One small synthetic Markdown file for the alpha tenant."""
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{doc_id.lower()}.md"
    text = (
        "---\n"
        'tenant: "tenant-alpha"\n'
        f'doc_id: "{doc_id}"\n'
        'title: "Test Press Manual"\n'
        'revision: "Rev 1"\n'
        'status: "current"\n'
        "---\n"
        "\n"
        "# Test Press Manual\n"
        "\n"
        "## Safety prerequisites\n"
        "\n"
        "1. Disconnect the main power.\n"
        "\n"
        "## Maintenance procedure\n"
        "\n"
        "Paragraph about oil changes and filter replacement.\n"
    )
    path.write_bytes(text.encode("utf-8"))
    return path