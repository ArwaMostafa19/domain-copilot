"""PostgreSQL stores chunks, safety steps and failures, one tenant at a time.

Every test only touches documents whose doc_id starts with ``TEST-``, so a
database that already holds real corpus data is never modified.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg
import pytest

from src.application.chunk import chunk_document
from src.application.ingest import ingest_file
from src.domain.llm import ProviderUnavailableError
from src.infrastructure.database import tenant_connection
from src.infrastructure.extractors import extract
from src.infrastructure.repository import PostgresDocumentRepository

ADMIN_URL = os.environ.get("ADMIN_DATABASE_URL")
APP_URL = os.environ.get("DATABASE_URL")

pytestmark = pytest.mark.skipif(not (APP_URL and ADMIN_URL), reason="database URLs are not set")

ALPHA = "tenant-alpha"
BETA = "tenant-beta"
SOURCE_FORMAT = "markdown"
TEST_PREFIX = "TEST-%"
SAFETY_STEPS = [
    "Disconnect the main power.",
    "Wear safety glasses.",
    "Lock out the valve.",
]

TESTS_ROOT = Path(__file__).resolve().parents[1]
if str(TESTS_ROOT) not in sys.path:
    sys.path.insert(0, str(TESTS_ROOT))

from fakes import FakeEmbedder


class FailingEmbedder:
    """An embedder whose provider is down."""

    model_name = "failing-embedder"
    dimension = 768

    def embed(self, texts):
        raise ProviderUnavailableError("fake", "embedding service is down")


@pytest.fixture(autouse=True)
def clean_test_documents():
    """Delete every TEST- document before and after each test."""
    _purge()
    yield
    _purge()


def _purge() -> None:
    with psycopg.connect(ADMIN_URL, autocommit=True) as admin:
        admin.execute("DELETE FROM documents WHERE doc_id LIKE %s", (TEST_PREFIX,))


def write_document(folder: Path, tenant: str, doc_id: str, body: str) -> Path:
    """Write one small synthetic Markdown file for a real tenant folder."""
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{doc_id.lower()}.md"
    text = (
        "---\n"
        f'tenant: "{tenant}"\n'
        f'doc_id: "{doc_id}"\n'
        f'title: "{doc_id} manual"\n'
        'revision: "Rev 1"\n'
        'status: "current"\n'
        "---\n"
        "\n"
        f"# {doc_id} manual\n"
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


def chunk_rows(tenant: str, doc_id: str) -> list[tuple]:
    """The (id, ordinal, content, embedding_model) of a document's chunks."""
    with tenant_connection(tenant) as connection:
        return connection.execute(
            """
            SELECT c.id, c.ordinal, c.content, c.embedding_model
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE d.doc_id = %s
            ORDER BY c.ordinal
            """,
            (doc_id,),
        ).fetchall()


def step_rows(tenant: str, doc_id: str) -> list[tuple]:
    """The (step_no, step_text) of a document's safety steps."""
    with tenant_connection(tenant) as connection:
        return connection.execute(
            """
            SELECT s.step_no, s.step_text
            FROM safety_prerequisites s
            JOIN documents d ON d.id = s.document_id
            WHERE d.doc_id = %s
            ORDER BY s.step_no
            """,
            (doc_id,),
        ).fetchall()


def document_row(tenant: str, doc_id: str) -> tuple:
    """The (ingest_status, ingest_error) of a document row."""
    with tenant_connection(tenant) as connection:
        row = connection.execute(
            "SELECT ingest_status, ingest_error FROM documents WHERE doc_id = %s",
            (doc_id,),
        ).fetchone()
    assert row is not None, f"{doc_id} has no document row"
    return row


def test_chunks_and_safety_steps_are_stored(tmp_path: Path) -> None:
    alpha_path = write_document(
        tmp_path / ALPHA, ALPHA, "TEST-ALPHA-STORE", "Alpha pump lubrication procedure."
    )
    beta_path = write_document(
        tmp_path / BETA, BETA, "TEST-BETA-STORE", "Beta pump inspection procedure."
    )
    repository = PostgresDocumentRepository()

    alpha = ingest_file(alpha_path, FakeEmbedder(), repository)
    beta = ingest_file(beta_path, FakeEmbedder(), repository)

    assert (alpha.status, beta.status) == ("ingested", "ingested")
    for tenant, path, doc_id, result in (
        (ALPHA, alpha_path, "TEST-ALPHA-STORE", alpha),
        (BETA, beta_path, "TEST-BETA-STORE", beta),
    ):
        expected = chunk_document(extract(path))
        rows = chunk_rows(tenant, doc_id)
        assert result.chunks == len(expected) == len(rows)
        assert [row[1] for row in rows] == [chunk.ordinal for chunk in expected]
        assert [row[2] for row in rows] == [chunk.text for chunk in expected]
        assert result.steps == len(step_rows(tenant, doc_id)) == len(SAFETY_STEPS)


def test_a_second_run_is_skipped_and_changes_nothing(tmp_path: Path) -> None:
    doc_id = "TEST-ALPHA-SKIP"
    path = write_document(tmp_path / ALPHA, ALPHA, doc_id, "Original stored paragraph.")
    repository = PostgresDocumentRepository()
    first = ingest_file(path, FakeEmbedder(), repository)
    assert first.status == "ingested"
    chunks_before = chunk_rows(ALPHA, doc_id)
    steps_before = step_rows(ALPHA, doc_id)
    document_before = document_row(ALPHA, doc_id)

    second = ingest_file(path, FakeEmbedder(), repository)

    assert second.status == "skipped"
    assert chunk_rows(ALPHA, doc_id) == chunks_before
    assert step_rows(ALPHA, doc_id) == steps_before
    assert document_row(ALPHA, doc_id) == document_before


def test_edited_content_replaces_the_chunks_without_duplicates(tmp_path: Path) -> None:
    doc_id = "TEST-ALPHA-EDIT"
    path = write_document(
        tmp_path / ALPHA, ALPHA, doc_id, "Original paragraph carrying the old marker."
    )
    repository = PostgresDocumentRepository()
    ingest_file(path, FakeEmbedder(), repository)

    write_document(
        tmp_path / ALPHA, ALPHA, doc_id, "Edited paragraph carrying the new marker."
    )
    result = ingest_file(path, FakeEmbedder(), repository)

    assert result.status == "ingested"
    rows = chunk_rows(ALPHA, doc_id)
    contents = [row[2] for row in rows]
    assert len(rows) == result.chunks
    assert [row[1] for row in rows] == list(range(len(rows)))
    assert any("new marker" in content for content in contents)
    assert all("old marker" not in content for content in contents)
    assert len(step_rows(ALPHA, doc_id)) == len(SAFETY_STEPS)


def test_chunks_and_safety_steps_do_not_cross_tenants(tmp_path: Path) -> None:
    alpha_path = write_document(
        tmp_path / ALPHA, ALPHA, "TEST-ALPHA-VIEW", "Maintenance marker alpha only."
    )
    beta_path = write_document(
        tmp_path / BETA, BETA, "TEST-BETA-VIEW", "Maintenance marker beta only."
    )
    repository = PostgresDocumentRepository()
    assert ingest_file(alpha_path, FakeEmbedder(), repository).status == "ingested"
    assert ingest_file(beta_path, FakeEmbedder(), repository).status == "ingested"

    alpha_chunks = chunk_rows(ALPHA, "TEST-ALPHA-VIEW")
    assert alpha_chunks
    assert any("marker alpha" in row[2] for row in alpha_chunks)
    assert all("marker beta" not in row[2] for row in alpha_chunks)
    assert chunk_rows(ALPHA, "TEST-BETA-VIEW") == []
    assert step_rows(ALPHA, "TEST-BETA-VIEW") == []
    assert chunk_rows(BETA, "TEST-ALPHA-VIEW") == []
    assert step_rows(BETA, "TEST-ALPHA-VIEW") == []
    beta_chunks = chunk_rows(BETA, "TEST-BETA-VIEW")
    assert beta_chunks
    assert any("marker beta" in row[2] for row in beta_chunks)

    with tenant_connection(ALPHA) as connection:
        visible = [
            row[0]
            for row in connection.execute("SELECT doc_id FROM documents").fetchall()
        ]
        leaked = connection.execute(
            "SELECT count(*) FROM chunks WHERE content LIKE %s", ("%marker beta%",)
        ).fetchone()[0]
    assert "TEST-BETA-VIEW" not in visible
    assert "TEST-ALPHA-VIEW" in visible
    assert leaked == 0
    assert len(step_rows(ALPHA, "TEST-ALPHA-VIEW")) == len(SAFETY_STEPS)


def test_a_failing_embedder_records_a_failed_document(tmp_path: Path) -> None:
    doc_id = "TEST-ALPHA-FAILED"
    path = write_document(tmp_path / ALPHA, ALPHA, doc_id, "Paragraph never embedded.")

    result = ingest_file(path, FailingEmbedder(), PostgresDocumentRepository())

    assert result.status == "failed"
    assert result.error == "[fake] embedding service is down"
    assert document_row(ALPHA, doc_id) == ("failed", "[fake] embedding service is down")
    assert chunk_rows(ALPHA, doc_id) == []
    assert step_rows(ALPHA, doc_id) == []


def test_a_failed_reingestion_keeps_the_good_chunks(tmp_path: Path) -> None:
    doc_id = "TEST-ALPHA-REFAIL"
    path = write_document(
        tmp_path / ALPHA, ALPHA, doc_id, "Stored paragraph carrying the old marker."
    )
    repository = PostgresDocumentRepository()
    good = ingest_file(path, FakeEmbedder(), repository)
    assert good.status == "ingested"
    chunks_before = chunk_rows(ALPHA, doc_id)

    write_document(
        tmp_path / ALPHA, ALPHA, doc_id, "Edited paragraph carrying the newer marker."
    )
    bad = ingest_file(path, FailingEmbedder(), repository)

    assert bad.status == "failed"
    assert document_row(ALPHA, doc_id) == ("ingested", "[fake] embedding service is down")
    rows = chunk_rows(ALPHA, doc_id)
    assert rows == chunks_before
    assert any("old marker" in row[2] for row in rows)
    assert all("newer marker" not in row[2] for row in rows)
    assert len(step_rows(ALPHA, doc_id)) == len(SAFETY_STEPS)


def test_embedding_model_is_stored_on_every_chunk(tmp_path: Path) -> None:
    doc_id = "TEST-ALPHA-MODEL"
    path = write_document(
        tmp_path / ALPHA, ALPHA, doc_id, "Paragraph about stored embedding models."
    )
    embedder = FakeEmbedder()

    result = ingest_file(path, embedder, PostgresDocumentRepository())

    assert result.status == "ingested"
    rows = chunk_rows(ALPHA, doc_id)
    assert len(rows) == result.chunks > 0
    assert {row[3] for row in rows} == {embedder.model_name}
    assert document_row(ALPHA, doc_id)[0] == "ingested"
