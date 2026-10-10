"""The real corpus must survive extraction, chunking and safety-step reading."""

from __future__ import annotations

import re
from pathlib import Path

from src.application.chunk import chunk_document
from src.application.clean import clean_text
from src.application.safety_steps import extract_safety_steps
from src.infrastructure.extractors import extract

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "corpus"
TENANTS = ("tenant-alpha", "tenant-beta")
SOURCE_SUFFIXES = (".md", ".pdf")
EXPECTED_FILES = 36
INJECTION_MARKER = "UNTRUSTED EMBEDDED INSTRUCTION"
COVERAGE_FLOOR = 0.90

EXPECTED_SAFETY_STEPS = {
    "tenant-alpha": {
        "air-compressor-preventive-maintenance": 4,
        "gearmotor-and-conveyor-maintenance": 6,
        "hydraulic-power-unit-diagnostic-procedure": 7,
        "hydraulic-press-preventive-maintenance-rev-a": 3,
        "hydraulic-press-preventive-maintenance-rev-b": 3,
        "machining-centre-lubrication-schedule": 5,
    },
    "tenant-beta": {
        "air-compressor-preventive-maintenance": 4,
        "gearmotor-and-conveyor-maintenance": 6,
        "hydraulic-power-unit-diagnostic-procedure": 8,
        "hydraulic-press-preventive-maintenance-rev-a": 3,
        "hydraulic-press-preventive-maintenance-rev-b": 3,
        "machining-centre-lubrication-schedule": 5,
    },
}

EXPECTED_INJECTION_FILES = {
    "tenant-alpha": (
        "chiller-alarm-troubleshooting-guide",
        "hydraulic-press-troubleshooting-guide",
    ),
    "tenant-beta": (
        "air-compressor-preventive-maintenance",
        "hydraulic-press-troubleshooting-guide",
    ),
}


def corpus_files() -> list[Path]:
    """Every Markdown and PDF of the real corpus, sorted."""
    files = [
        path
        for tenant in TENANTS
        for path in sorted((CORPUS / tenant).rglob("*"))
        if path.is_file() and path.suffix.lower() in SOURCE_SUFFIXES
    ]
    return sorted(files)


def normalise(text: str) -> str:
    """Collapse all whitespace so layout differences cannot fail an assertion."""
    return " ".join(text.split())


def significant_words(text: str) -> set[str]:
    """Lowercase alphanumeric tokens of three characters or more."""
    return set(re.findall(r"[a-z0-9]{3,}", text.lower()))


def test_the_corpus_has_the_expected_number_of_source_files() -> None:
    assert len(corpus_files()) == EXPECTED_FILES


def test_every_corpus_file_extracts_and_produces_non_empty_chunks() -> None:
    problems: list[str] = []
    for path in corpus_files():
        doc = extract(path)
        chunks = chunk_document(doc)
        if not chunks:
            problems.append(f"{path.name}: no chunk")
            continue
        if any(not chunk.text.strip() for chunk in chunks):
            problems.append(f"{path.name}: empty chunk text")
        if [chunk.ordinal for chunk in chunks] != list(range(len(chunks))):
            problems.append(f"{path.name}: ordinals are not contiguous")
    assert not problems, problems


def test_the_tenant_on_every_document_matches_its_folder() -> None:
    mismatches = [
        f"{path.name}: {extract(path).meta.tenant_id}"
        for path in corpus_files()
        if extract(path).meta.tenant_id != path.parent.name
    ]
    assert not mismatches, mismatches


def test_safety_step_counts_are_exact_for_the_procedures_that_carry_them() -> None:
    actual: dict[tuple[str, str], int] = {}
    for path in corpus_files():
        if path.suffix.lower() != ".md":
            continue
        actual[(path.parent.name, path.stem)] = len(extract_safety_steps(extract(path)))
    for tenant, expected in EXPECTED_SAFETY_STEPS.items():
        for stem, count in expected.items():
            key = (tenant, stem)
            assert key in actual, f"{key} is missing from the corpus"
            assert actual[key] == count, f"{key} has {actual[key]} steps, expected {count}"
    for key, count in sorted(actual.items()):
        if key in {(tenant, stem) for tenant, group in EXPECTED_SAFETY_STEPS.items() for stem in group}:
            continue
        assert count == 0, f"{key} unexpectedly has {count} safety steps"


def test_every_pdf_reports_no_safety_steps() -> None:
    pdfs = [path for path in corpus_files() if path.suffix.lower() == ".pdf"]
    assert len(pdfs) == 6, [path.as_posix() for path in pdfs]
    for path in pdfs:
        assert extract_safety_steps(extract(path)) == [], path.name


def test_chunking_loses_no_word_of_any_markdown_document() -> None:
    problems: list[str] = []
    for path in corpus_files():
        if path.suffix.lower() != ".md":
            continue
        doc = extract(path)
        sections = normalise(" ".join(clean_text(section.text) for section in doc.sections))
        chunks = normalise(" ".join(chunk.text for chunk in chunk_document(doc)))
        if sections != chunks:
            problems.append(path.as_posix())
    assert not problems, problems


def test_the_embedded_prompt_injection_text_survives_cleaning_and_chunking() -> None:
    for tenant, stems in EXPECTED_INJECTION_FILES.items():
        for stem in stems:
            path = CORPUS / tenant / f"{stem}.md"
            source = path.read_text(encoding="utf-8")
            assert INJECTION_MARKER in source, f"{path.name} no longer carries the marker"
            doc = extract(path)
            sections = " ".join(clean_text(section.text) for section in doc.sections)
            chunks = " ".join(chunk.text for chunk in chunk_document(doc))
            assert INJECTION_MARKER in sections, f"{path.name}: lost while cleaning"
            assert INJECTION_MARKER in chunks, f"{path.name}: lost while chunking"


def test_every_pdf_chunk_covers_the_words_of_its_markdown_twin() -> None:
    reports: list[str] = []
    for path in corpus_files():
        if path.suffix.lower() != ".pdf":
            continue
        markdown = extract(path.with_suffix(".md"))
        expected = significant_words(
            " ".join(clean_text(section.text) for section in markdown.sections)
        )
        pdf = extract(path)
        found = significant_words(" ".join(chunk.text for chunk in chunk_document(pdf)))
        covered = expected & found
        ratio = len(covered) / len(expected) if expected else 1.0
        reports.append(f"{path.as_posix()}: {ratio:.2%} of {len(expected)} words")
        assert ratio >= COVERAGE_FLOOR, (
            f"{path.as_posix()}: only {ratio:.2%} of the Markdown words appear in the PDF chunks"
        )
    assert len(reports) == 6, reports
