"""PostgreSQL chunk search: tenant isolation, revisions, codes, twin collapse.

Every test only touches documents whose doc_id starts with ``TEST-``.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace

import psycopg
import pytest

from src.application.ingest import ingest_file
from src.application.retrieval import keyword_terms, retrieve
from src.domain.documents import Chunk, DocumentMeta
from src.infrastructure.chunk_search import PostgresChunkSearch
from src.infrastructure.repository import PostgresDocumentRepository

ADMIN_URL = os.environ.get("ADMIN_DATABASE_URL")
APP_URL = os.environ.get("DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not (APP_URL and ADMIN_URL), reason="database URLs are not set"
)

ALPHA = "tenant-alpha"
BETA = "tenant-beta"
MODEL = "fake-embedder"
TEST_PREFIX = "TEST-%"

TESTS_ROOT = Path(__file__).resolve().parents[1]
if str(TESTS_ROOT) not in sys.path:
    sys.path.insert(0, str(TESTS_ROOT))

from fakes import FakeEmbedder

SETTINGS = SimpleNamespace(retrieval_min_similarity=0.55)


@pytest.fixture(autouse=True)
def clean_test_documents():
    """Delete every TEST- document before and after each test."""
    _purge()
    yield
    _purge()


def _purge() -> None:
    with psycopg.connect(ADMIN_URL, autocommit=True) as admin:
        admin.execute("DELETE FROM documents WHERE doc_id LIKE %s", (TEST_PREFIX,))


def write_document(
    folder: Path, tenant: str, doc_id: str, body: str, status: str = "current"
) -> Path:
    """Write one small synthetic Markdown file for a real tenant folder."""
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{doc_id.lower()}.md"
    text = (
        "---\n"
        f'tenant: "{tenant}"\n'
        f'doc_id: "{doc_id}"\n'
        f'title: "{doc_id} manual"\n'
        'revision: "Rev 1"\n'
        f'status: "{status}"\n'
        "---\n"
        "\n"
        f"# {doc_id} manual\n"
        "\n"
        "## Maintenance procedure\n"
        "\n"
        f"{body}\n"
    )
    path.write_bytes(text.encode("utf-8"))
    return path


def doc_ids(evidence) -> set[str]:
    return {item.doc_id for item in evidence}


def test_dense_and_keyword_search_do_not_cross_tenants(tmp_path: Path) -> None:
    repository = PostgresDocumentRepository()
    embedder = FakeEmbedder()
    ingest_file(
        write_document(
            tmp_path / ALPHA, ALPHA, "TEST-ALPHA-SEARCH", "alpha unique marker kubernetes."
        ),
        embedder,
        repository,
    )
    ingest_file(
        write_document(
            tmp_path / BETA, BETA, "TEST-BETA-SEARCH", "beta unique marker kubernetes."
        ),
        embedder,
        repository,
    )
    search = PostgresChunkSearch()
    vector = embedder.embed(["marker"])[0]

    alpha_dense = search.search_dense(ALPHA, vector, MODEL, False, 10)
    alpha_keyword = search.search_keyword(ALPHA, ["marker"], MODEL, False, 10)

    assert doc_ids(alpha_dense) == {"TEST-ALPHA-SEARCH"}
    assert doc_ids(alpha_keyword) == {"TEST-ALPHA-SEARCH"}


def test_current_only_hides_superseded_unless_asked(tmp_path: Path) -> None:
    repository = PostgresDocumentRepository()
    embedder = FakeEmbedder()
    ingest_file(
        write_document(
            tmp_path / ALPHA,
            ALPHA,
            "TEST-ALPHA-REVA",
            "The relief pressure was 240 bar.",
            status="superseded",
        ),
        embedder,
        repository,
    )
    ingest_file(
        write_document(
            tmp_path / ALPHA,
            ALPHA,
            "TEST-ALPHA-REVB",
            "The relief pressure is 210 bar.",
            status="current",
        ),
        embedder,
        repository,
    )
    search = PostgresChunkSearch()

    current = search.search_keyword(ALPHA, ["relief"], MODEL, False, 10)
    all_versions = search.search_keyword(ALPHA, ["relief"], MODEL, True, 10)

    assert doc_ids(current) == {"TEST-ALPHA-REVB"}
    assert doc_ids(all_versions) == {"TEST-ALPHA-REVA", "TEST-ALPHA-REVB"}


def test_keyword_search_finds_a_product_code(tmp_path: Path) -> None:
    repository = PostgresDocumentRepository()
    embedder = FakeEmbedder()
    ingest_file(
        write_document(
            tmp_path / ALPHA,
            ALPHA,
            "TEST-ALPHA-CODE",
            "Use AM-CO-100S synthetic compressor oil only.",
        ),
        embedder,
        repository,
    )

    hits = PostgresChunkSearch().search_keyword(
        ALPHA, keyword_terms("AM-CO-100S"), MODEL, False, 10
    )

    assert doc_ids(hits) == {"TEST-ALPHA-CODE"}


def test_retrieve_collapses_a_markdown_and_pdf_twin(tmp_path: Path) -> None:
    repository = PostgresDocumentRepository()
    embedder = FakeEmbedder()
    markdown = _chunk("The set point is 210 bar.")
    pdf = _chunk("The set point is 210 bar (pdf copy).")
    repository.replace_document(
        _meta("markdown", "corpus/tenant-alpha/twin.md"), [markdown],
        embedder.embed([markdown.text]), [], MODEL,
    )
    repository.replace_document(
        _meta("pdf", "corpus/tenant-alpha/twin.pdf"), [pdf],
        embedder.embed([pdf.text]), [], MODEL,
    )
    search = PostgresChunkSearch()
    vector = embedder.embed(["set point"])[0]

    raw = search.search_dense(ALPHA, vector, MODEL, False, 20)
    collapsed = retrieve("set point", ALPHA, embedder, search, SETTINGS)

    assert sum(1 for item in raw if item.doc_id == "TEST-ALPHA-TWIN") == 2
    assert sum(1 for item in collapsed if item.doc_id == "TEST-ALPHA-TWIN") == 1


def _meta(source_format: str, source_path: str) -> DocumentMeta:
    return DocumentMeta(
        tenant_id=ALPHA,
        doc_id="TEST-ALPHA-TWIN",
        title="TEST-ALPHA-TWIN manual",
        equipment=None,
        document_type=None,
        revision="Rev 1",
        status="current",
        source_format=source_format,
        source_path=source_path,
        content_sha256=source_format,
    )


def _chunk(text: str) -> Chunk:
    return Chunk(
        ordinal=0,
        section="Set point",
        page=None,
        revision="Rev 1",
        context="twin context",
        text=text,
    )