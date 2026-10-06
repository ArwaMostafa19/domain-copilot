"""extract reads Markdown and PDF corpus files into extracted documents."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from pypdf import PdfWriter

from src.domain.documents import ExtractionError
from src.infrastructure.extractors import extract

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "corpus"
REAL_PDF = CORPUS / "tenant-alpha" / "hydraulic-press-lockout-tagout.pdf"

VALID_MARKDOWN = """---
tenant: "tenant-test"
doc_id: "TEST-1"
title: "Synthetic Press Manual"
revision: "Rev 1"
status: "current"
equipment: "TEST-HP-1"
document_type: "equipment-manual"
---

# Synthetic Press Manual

| Field | Value |
| --- | --- |
| Tenant | Test |
| Revision | Rev 1 |

## Purpose

This manual describes the press.

### Scope

The press only.

## Technical data

| Parameter | Value |
| --- | --- |
| System pressure | 240 bar |
"""


def write(path: Path, text: str) -> Path:
    """Write text to path as UTF-8 with LF endings."""
    path.write_text(text, encoding="utf-8")
    return path


def test_valid_markdown_is_extracted(tmp_path: Path) -> None:
    path = write(tmp_path / "manual.md", VALID_MARKDOWN)
    doc = extract(path)
    assert doc.meta.tenant_id == "tenant-test"
    assert doc.meta.doc_id == "TEST-1"
    assert doc.meta.title == "Synthetic Press Manual"
    assert doc.meta.revision == "Rev 1"
    assert doc.meta.status == "current"
    assert doc.meta.equipment == "TEST-HP-1"
    assert doc.meta.document_type == "equipment-manual"
    assert doc.meta.source_format == "markdown"
    assert doc.meta.content_sha256 == hashlib.sha256(path.read_bytes()).hexdigest()
    assert [section.title for section in doc.sections] == ["Purpose", "Technical data"]


def test_the_h1_and_the_field_table_are_dropped_and_h3_stays_in_its_section(tmp_path: Path) -> None:
    path = write(tmp_path / "manual.md", VALID_MARKDOWN)
    purpose = extract(path).sections[0]
    assert not purpose.text.lstrip().startswith("# ")
    assert "# Synthetic Press Manual" not in purpose.text
    assert "| Field | Value |" not in purpose.text
    assert "### Scope" in purpose.text
    assert "The press only." in purpose.text


def test_source_path_is_relative_to_the_repository_with_forward_slashes(tmp_path: Path) -> None:
    path = write(tmp_path / "manual.md", VALID_MARKDOWN)
    assert extract(path).meta.source_path.endswith("manual.md")
    assert "\\" not in extract(path).meta.source_path


def test_a_corpus_markdown_file_records_its_corpus_relative_path() -> None:
    doc = extract(CORPUS / "tenant-alpha" / "hydraulic-press-lockout-tagout.md")
    assert doc.meta.source_path == "corpus/tenant-alpha/hydraulic-press-lockout-tagout.md"


def test_text_before_the_first_h2_becomes_a_section_titled_with_the_document_title(
    tmp_path: Path,
) -> None:
    source = VALID_MARKDOWN.replace("## Purpose", "Loose introduction line.\n\n## Purpose")
    doc = extract(write(tmp_path / "manual.md", source))
    assert [section.title for section in doc.sections] == [
        "Synthetic Press Manual",
        "Purpose",
        "Technical data",
    ]
    assert doc.sections[0].text.strip() == "Loose introduction line."


def test_a_missing_required_key_is_rejected(tmp_path: Path) -> None:
    source = VALID_MARKDOWN.replace('revision: "Rev 1"\n', "")
    path = write(tmp_path / "manual.md", source)
    with pytest.raises(ExtractionError) as error:
        extract(path)
    assert "revision" in str(error.value)
    assert str(path) in str(error.value)


def test_an_unsupported_suffix_is_rejected(tmp_path: Path) -> None:
    path = write(tmp_path / "manual.txt", VALID_MARKDOWN)
    with pytest.raises(ExtractionError) as error:
        extract(path)
    assert str(path) in str(error.value)


def test_a_missing_file_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "absent.md"
    with pytest.raises(ExtractionError) as error:
        extract(path)
    assert str(path) in str(error.value)


def test_a_corrupt_pdf_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "broken.pdf"
    path.write_bytes(b"this is not a pdf, only garbage bytes")
    write(tmp_path / "broken.md", VALID_MARKDOWN)
    with pytest.raises(ExtractionError) as error:
        extract(path)
    assert str(path) in str(error.value)


def test_a_pdf_without_extractable_text_is_rejected(tmp_path: Path) -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    path = tmp_path / "blank.pdf"
    with path.open("wb") as handle:
        writer.write(handle)
    write(tmp_path / "blank.md", VALID_MARKDOWN)
    with pytest.raises(ExtractionError) as error:
        extract(path)
    assert "extractable text" in str(error.value)
    assert str(path) in str(error.value)


def test_a_pdf_without_a_sibling_markdown_file_is_rejected(tmp_path: Path) -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    path = tmp_path / "orphan.pdf"
    with path.open("wb") as handle:
        writer.write(handle)
    with pytest.raises(ExtractionError) as error:
        extract(path)
    assert "sibling" in str(error.value)
    assert str(path) in str(error.value)


def test_the_real_corpus_pdf_is_extracted_with_its_markdown_metadata() -> None:
    doc = extract(REAL_PDF)
    assert doc.meta.source_format == "pdf"
    assert doc.meta.tenant_id == "tenant-alpha"
    assert doc.meta.doc_id == "ALPHA-SAF-HP200-LOTO-1"
    assert doc.meta.revision == "Rev 1"
    assert doc.meta.status == "current"
    assert doc.meta.source_path.endswith("hydraulic-press-lockout-tagout.pdf")
    assert doc.meta.content_sha256 == hashlib.sha256(REAL_PDF.read_bytes()).hexdigest()


def test_the_real_corpus_pdf_sections_take_their_titles_and_pages_from_the_manifest() -> None:
    doc = extract(REAL_PDF)
    titles = [section.title for section in doc.sections]
    assert "Purpose and scope" in titles
    assert "Required sequence" in titles
    assert "Revision history" in titles
    pages = dict(zip(titles, [section.page for section in doc.sections], strict=True))
    assert pages["Purpose and scope"] == 1
    assert pages["Required sequence"] == 2
    assert all(page is not None for page in [section.page for section in doc.sections])


def test_the_real_corpus_pdf_keeps_its_adversarial_text() -> None:
    doc = extract(REAL_PDF)
    joined = "\n".join(section.text for section in doc.sections)
    assert "Attempt start" in joined