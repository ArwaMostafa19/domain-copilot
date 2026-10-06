"""The pipeline embeds, stores, skips and fails one file at a time."""

from __future__ import annotations

import sys
from pathlib import Path

from src.application.chunk import chunk_document
from src.application.ingest import ingest_file, ingest_files
from src.application.ports import ProviderError
from src.application.safety_steps import extract_safety_steps
from src.infrastructure.extractors import extract

TESTS_ROOT = Path(__file__).resolve().parents[1]
if str(TESTS_ROOT) not in sys.path:
    sys.path.insert(0, str(TESTS_ROOT))

from fakes import FakeEmbedder, InMemoryRepository

TENANT = "tenant-alpha"
DOC_ID = "TEST-INGEST-1"
SOURCE_FORMAT = "markdown"
ORIGINAL_BODY = "Original maintenance paragraph about the gearbox."
REPLACEMENT_BODY = "Replacement maintenance paragraph about the gearbox."
SAFETY_STEPS = [
    "Disconnect the main power.",
    "Wear safety glasses.",
    "Lock out the valve.",
]


class ExplodingEmbedder:
    """An embedder whose provider never answers."""

    model_name = "exploding-embedder"
    dimension = 768

    def embed(self, texts: list[str]) -> list[list[float]]:
        raise ProviderError("the provider is down")


class OneVectorShortEmbedder:
    """Returns one vector fewer than the number of texts."""

    model_name = "short-embedder"
    dimension = 768

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * self.dimension for _ in texts[:-1]]


class WrongDimensionEmbedder:
    """Returns vectors that are far too short."""

    model_name = "wrong-dimension-embedder"
    dimension = 768

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * 10 for _ in texts]


def write_document(folder: Path, body: str = ORIGINAL_BODY, doc_id: str = DOC_ID) -> Path:
    """Write one synthetic Markdown file the extractor accepts."""
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{doc_id.lower()}.md"
    text = (
        "---\n"
        f'tenant: "{TENANT}"\n'
        f'doc_id: "{doc_id}"\n'
        'title: "Test Press Manual"\n'
        'revision: "Rev 1"\n'
        'status: "current"\n'
        "---\n"
        "\n"
        "# Test Press Manual\n"
        "\n"
        "| Field | Value |\n"
        "| ----- | ----- |\n"
        "\n"
        "## Safety prerequisites\n"
        "\n"
        "1. Disconnect the main power.\n"
        "2. Wear safety glasses.\n"
        "3. Lock out the valve.\n"
        "\n"
        "## Maintenance procedure\n"
        "\n"
        f"{body}\n"
    )
    path.write_bytes(text.encode("utf-8"))
    return path


def stored_row(repository: InMemoryRepository) -> dict[str, object]:
    """The row of the test document, failing loudly when it is missing."""
    row = repository.get(TENANT, DOC_ID, SOURCE_FORMAT)
    assert row is not None, "the document was never stored"
    return row


def test_a_fresh_file_is_ingested_with_its_chunks_and_steps(tmp_path: Path) -> None:
    path = write_document(tmp_path)
    repository = InMemoryRepository()

    result = ingest_file(path, FakeEmbedder(), repository)

    assert result.status == "ingested"
    assert result.error is None
    assert result.chunks == len(chunk_document(extract(path)))
    assert result.steps == len(SAFETY_STEPS)
    row = stored_row(repository)
    assert row["ingest_status"] == "ingested"
    assert row["embedding_model"] == "fake-embedder"
    assert len(row["chunks"]) == result.chunks
    assert len(row["embeddings"]) == result.chunks
    assert repository.failures == []


def test_the_second_run_of_the_same_file_is_skipped(tmp_path: Path) -> None:
    path = write_document(tmp_path)
    embedder = FakeEmbedder()
    repository = InMemoryRepository()
    first = ingest_file(path, embedder, repository)
    before = stored_row(repository)

    second = ingest_file(path, embedder, repository)

    assert first.status == "ingested"
    assert second.status == "skipped"
    assert stored_row(repository) == before
    assert len(embedder.calls) == 1


def test_changed_content_replaces_the_stored_version(tmp_path: Path) -> None:
    path = write_document(tmp_path, body=ORIGINAL_BODY)
    repository = InMemoryRepository()
    ingest_file(path, FakeEmbedder(), repository)

    write_document(tmp_path, body=REPLACEMENT_BODY)
    result = ingest_file(path, FakeEmbedder(), repository)

    assert result.status == "ingested"
    row = stored_row(repository)
    chunks = row["chunks"]
    texts = [chunk.text for chunk in chunks]
    assert len(texts) == result.chunks
    assert len({chunk.ordinal for chunk in chunks}) == result.chunks
    assert any(REPLACEMENT_BODY in text for text in texts)
    assert all(ORIGINAL_BODY not in text for text in texts)
    assert repository.failures == []


def test_an_extraction_failure_leaves_the_repository_untouched(tmp_path: Path) -> None:
    path = tmp_path / "broken.md"
    path.write_bytes(b"no front matter at all\n## Section\n\nBody\n")
    embedder = FakeEmbedder()
    repository = InMemoryRepository()

    result = ingest_file(path, embedder, repository)

    assert result.status == "failed"
    assert result.error is not None and "front matter" in result.error
    assert repository.rows == {}
    assert repository.failures == []
    assert embedder.calls == []


def test_a_provider_error_marks_the_document_as_failed(tmp_path: Path) -> None:
    path = write_document(tmp_path)
    repository = InMemoryRepository()

    result = ingest_file(path, ExplodingEmbedder(), repository)

    assert result.status == "failed"
    assert result.error == "the provider is down"
    assert [message for _, message in repository.failures] == ["the provider is down"]
    row = stored_row(repository)
    assert row["ingest_status"] == "failed"
    assert row["ingest_error"] == "the provider is down"


def test_a_domain_error_after_extraction_also_marks_the_document_failed(
    tmp_path: Path,
) -> None:
    path = write_document(tmp_path, doc_id="TEST-DUPLICATE-STEPS")
    path.write_bytes(
        path.read_bytes().replace(
            b"3. Lock out the valve.", b"1. Lock out the valve."
        )
    )
    repository = InMemoryRepository()

    result = ingest_file(path, FakeEmbedder(), repository)

    assert result.status == "failed"
    assert result.error is not None and "duplicate" in result.error
    assert [error for _, error in repository.failures] == [result.error]
    row = repository.get(TENANT, "TEST-DUPLICATE-STEPS", SOURCE_FORMAT)
    assert row is not None
    assert row["ingest_status"] == "failed"
    assert row["chunks"] == []


def test_the_wrong_number_of_vectors_fails_the_file(tmp_path: Path) -> None:
    path = write_document(tmp_path)
    repository = InMemoryRepository()

    result = ingest_file(path, OneVectorShortEmbedder(), repository)

    assert result.status == "failed"
    assert result.error is not None and "vectors" in result.error
    row = stored_row(repository)
    assert row["ingest_status"] == "failed"
    assert row["chunks"] == []


def test_a_vector_of_the_wrong_length_fails_the_file(tmp_path: Path) -> None:
    path = write_document(tmp_path)
    repository = InMemoryRepository()

    result = ingest_file(path, WrongDimensionEmbedder(), repository)

    assert result.status == "failed"
    assert result.error is not None and "expected 768" in result.error
    row = stored_row(repository)
    assert row["ingest_status"] == "failed"


def test_ingest_files_keeps_going_after_a_failed_file(tmp_path: Path) -> None:
    broken = tmp_path / "broken.md"
    broken.write_bytes(b"no front matter at all\n")
    good = write_document(tmp_path)
    repository = InMemoryRepository()

    results = ingest_files([broken, good], FakeEmbedder(), repository)

    assert [result.status for result in results] == ["failed", "ingested"]
    assert stored_row(repository)["ingest_status"] == "ingested"


def test_the_embedded_text_is_context_then_newline_then_text(tmp_path: Path) -> None:
    path = write_document(tmp_path)
    embedder = FakeEmbedder()

    ingest_file(path, embedder, InMemoryRepository())

    chunks = chunk_document(extract(path))
    assert len(embedder.calls) == 1
    assert embedder.calls[0] == [f"{chunk.context}\n{chunk.text}" for chunk in chunks]


def test_the_safety_steps_are_passed_through(tmp_path: Path) -> None:
    path = write_document(tmp_path)
    repository = InMemoryRepository()

    ingest_file(path, FakeEmbedder(), repository)

    expected = extract_safety_steps(extract(path))
    row = stored_row(repository)
    assert [(step.step_no, step.text) for step in row["steps"]] == [
        (step.step_no, step.text) for step in expected
    ]
    assert [step.text for step in row["steps"]] == SAFETY_STEPS
