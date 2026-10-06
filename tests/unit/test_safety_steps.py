"""extract_safety_steps reads only the numbered prerequisites."""

from __future__ import annotations

import pytest

from src.application.safety_steps import extract_safety_steps
from src.domain.documents import (
    DocumentMeta,
    ExtractedDocument,
    ExtractionError,
    Section,
)

META = DocumentMeta(
    tenant_id="tenant-test",
    doc_id="TEST-1",
    title="Synthetic Procedure",
    revision="Rev 1",
    status="current",
    source_format="markdown",
    source_path="corpus/tenant-test/doc.md",
    content_sha256="0" * 64,
)

INTRO = "Before any work on the machine:"
CLOSING = "A diagnostic measurement is never a reason to work with the circuit charged."


def make_document(*sections: Section) -> ExtractedDocument:
    """Build a document from the given sections."""
    return ExtractedDocument(meta=META, sections=tuple(sections))


def test_an_introductory_sentence_is_not_a_step() -> None:
    doc = make_document(Section("Safety prerequisites", f"{INTRO}\n\n1. Stop the machine.\n"))
    steps = extract_safety_steps(doc)
    assert [step.step_no for step in steps] == [1]
    assert steps[0].text == "Stop the machine."


def test_a_closing_paragraph_is_not_a_step() -> None:
    doc = make_document(Section("Safety prerequisites", f"1. Stop the machine.\n\n{CLOSING}\n"))
    assert [step.step_no for step in extract_safety_steps(doc)] == [1]


def test_wrapped_lines_that_are_indented_are_joined_with_single_spaces() -> None:
    doc = make_document(
        Section(
            "Safety prerequisites",
            "1. Isolate the drive at panel MCC-7 breaker 5, locked\n   and tagged, then verify\n   zero energy at the pendant.\n",
        )
    )
    step = extract_safety_steps(doc)[0]
    assert step.text == (
        "Isolate the drive at panel MCC-7 breaker 5, locked and tagged, "
        "then verify zero energy at the pendant."
    )


def test_wrapped_lines_that_are_not_indented_are_joined_with_single_spaces() -> None:
    doc = make_document(
        Section(
            "Safety prerequisites",
            "1. Isolate the drive at panel MCC-7 breaker 5, locked\nand tagged, then verify\nzero energy at the pendant.\n",
        )
    )
    step = extract_safety_steps(doc)[0]
    assert step.text == (
        "Isolate the drive at panel MCC-7 breaker 5, locked and tagged, "
        "then verify zero energy at the pendant."
    )


def test_several_numbered_items_in_one_block_are_separate_steps() -> None:
    doc = make_document(
        Section(
            "Safety prerequisites",
            "1. First step.\ncontinued on the next line.\n2. Second step.\ncontinued too.\n",
        )
    )
    steps = extract_safety_steps(doc)
    assert [(step.step_no, step.text) for step in steps] == [
        (1, "First step. continued on the next line."),
        (2, "Second step. continued too."),
    ]


def test_a_document_without_a_safety_prerequisites_section_returns_nothing() -> None:
    doc = make_document(Section("Purpose", "1. Not a safety step."), Section("Notes", "Text."))
    assert extract_safety_steps(doc) == []


def test_a_bullet_only_section_returns_nothing() -> None:
    doc = make_document(
        Section("Safety prerequisites", "- Isolate the drive.\n- Lock and tag breaker 5.\n")
    )
    assert extract_safety_steps(doc) == []


def test_the_section_title_match_is_case_sensitive() -> None:
    doc = make_document(Section("Safety Prerequisites", "1. Isolate the drive.\n"))
    assert extract_safety_steps(doc) == []


def test_a_duplicate_step_number_is_rejected() -> None:
    doc = make_document(Section("Safety prerequisites", "1. One.\n\n1. Again.\n"))
    with pytest.raises(ExtractionError):
        extract_safety_steps(doc)


def test_the_step_number_is_the_number_written_in_the_text() -> None:
    doc = make_document(Section("Safety prerequisites", "4. Fourth written step.\n7. Seventh.\n"))
    assert [step.step_no for step in extract_safety_steps(doc)] == [4, 7]