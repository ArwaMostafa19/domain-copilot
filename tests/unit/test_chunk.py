"""chunk_document keeps tables, numbered lists and bullet lists whole."""

from __future__ import annotations

from src.application.chunk import chunk_document
from src.application.clean import clean_text
from src.domain.documents import DocumentMeta, ExtractedDocument, Section

META = DocumentMeta(
    tenant_id="tenant-test",
    doc_id="TEST-1",
    title="Synthetic Press Manual",
    revision="Rev 2",
    status="current",
    source_format="markdown",
    source_path="corpus/tenant-test/doc.md",
    content_sha256="0" * 64,
)

TABLE = (
    "| Task | Interval |\n"
    "| --- | --- |\n"
    "| Oil change | Every 4000 running hours |\n"
    "| Filter change | Every 2000 running hours |"
)
NUMBERED = (
    "1. Stop the machine.\n"
    "   Verify zero energy at the pendant.\n"
    "2. Isolate the drive at MCC-7.\n"
    "   Lock and tag breaker 5."
)
BULLETS = (
    "- Floor and die area clean, no oil pooling.\n"
    "- Oil level between the marks.\n"
    "- No visible hose chafing.\n"
    "  Criterion: no chafing at the bend radius."
)
FILLER = "word " * 400


def make_document(*sections: Section) -> ExtractedDocument:
    """Build a one-tenant document from the given sections."""
    return ExtractedDocument(meta=META, sections=tuple(sections))


def blocks_of(text: str) -> list[str]:
    """The blank-line-separated blocks a chunk text is built from."""
    return text.split("\n\n")


def sized_block(size: int, filler: str = "lorem ipsum dolor sit amet ") -> str:
    """A block of exactly ``size`` characters, cut from prose so it has words."""
    return (filler * (size // len(filler) + 1))[:size]


def test_a_table_is_never_split_across_chunks() -> None:
    doc = make_document(Section("Interval summary", f"{TABLE}\n\n{FILLER}\n\n{TABLE}"))
    chunks = chunk_document(doc, max_chars=200)
    assert len(chunks) > 1
    texts = [chunk.text for chunk in chunks]
    assert TABLE in texts[0]
    assert TABLE in texts[-1]
    for chunk in chunks:
        assert len(blocks_of(chunk.text)) == 1 or TABLE not in chunk.text


def test_a_numbered_list_is_never_split_across_chunks() -> None:
    doc = make_document(Section("Safety prerequisites", NUMBERED, page=3))
    chunks = chunk_document(doc, max_chars=40)
    assert [chunk.text for chunk in chunks] == [NUMBERED]


def test_a_bullet_list_is_never_split_across_chunks() -> None:
    doc = make_document(Section("Task details", f"{BULLETS}\n\n{FILLER}\n\n{BULLETS}"))
    chunks = chunk_document(doc, max_chars=60)
    assert len(chunks) > 1
    assert BULLETS in [chunk.text for chunk in chunks]
    for chunk in chunks:
        if BULLETS in chunk.text:
            assert chunk.text == BULLETS


def test_an_oversize_block_becomes_its_own_chunk_and_may_exceed_the_limit() -> None:
    huge = "x" * 500
    doc = make_document(Section("Body", f"{FILLER}\n\n{huge}\n\n{FILLER}"))
    chunks = chunk_document(doc, max_chars=100)
    assert [chunk.text for chunk in chunks] == [FILLER.strip(), huge, FILLER.strip()]
    assert len(huge) > 100


def test_ordinals_are_contiguous_from_zero_across_the_document() -> None:
    doc = make_document(
        Section("First", f"{TABLE}\n\n{FILLER}"),
        Section("Second", NUMBERED),
        Section("Empty", "   \n\n"),
        Section("Third", BULLETS),
    )
    chunks = chunk_document(doc, max_chars=120)
    assert [chunk.ordinal for chunk in chunks] == list(range(len(chunks)))


def test_empty_sections_produce_no_chunks() -> None:
    doc = make_document(Section("Blank", ""), Section("Blank too", "\n\n\n"))
    assert chunk_document(doc) == []


def test_context_is_title_section_and_revision() -> None:
    doc = make_document(Section("Technical data", TABLE))
    chunk = chunk_document(doc)[0]
    assert chunk.context == "Synthetic Press Manual | Technical data | Rev 2"
    assert chunk.section == "Technical data"
    assert chunk.revision == "Rev 2"


def test_safety_prerequisites_is_always_one_chunk() -> None:
    long_enough = "\n\n".join(f"{number}. Step number {number}." for number in range(1, 200))
    doc = make_document(Section("Safety prerequisites", long_enough))
    chunks = chunk_document(doc, max_chars=50)
    assert len(chunks) == 1
    assert chunks[0].text == long_enough


def test_a_section_titled_safety_prerequisites_exactly_is_the_only_special_case() -> None:
    text = "\n\n".join(f"Paragraph {number}." for number in range(1, 120))
    doc = make_document(Section("safety prerequisites", text))
    assert len(chunk_document(doc, max_chars=50)) > 1


def test_page_is_taken_from_the_section() -> None:
    doc = make_document(Section("Purpose", "First page.", page=1), Section("Notes", "Second.", page=7))
    assert [chunk.page for chunk in chunk_document(doc)] == [1, 7]


def test_page_is_none_when_the_section_has_no_page() -> None:
    doc = make_document(Section("Purpose", "No page known."))
    assert [chunk.page for chunk in chunk_document(doc)] == [None]


def test_no_word_is_lost_or_invented() -> None:
    doc = make_document(
        Section("A", f"{TABLE}\n\n{NUMBERED}"),
        Section("B", f"{BULLETS}\n\n{FILLER}"),
    )
    chunks = chunk_document(doc, max_chars=90)
    assert " ".join(chunk.text for chunk in chunks).split() == (
        f"{TABLE}\n\n{NUMBERED}\n\n{BULLETS}\n\n{FILLER}"
    ).split()


def test_blocks_are_joined_by_a_single_blank_line() -> None:
    doc = make_document(Section("Body", "first\n\n\n\nsecond"))
    chunk = chunk_document(doc)[0]
    assert chunk.text == "first\n\nsecond"


def test_packing_is_greedy_for_four_equal_blocks() -> None:
    """Regression: four 40-character blocks must pack as [82, 82], not [82, 40, 40]."""
    block = "a" * 40
    doc = make_document(Section("Body", "\n\n".join([block] * 4)))
    chunks = chunk_document(doc, max_chars=100)
    assert len(chunks) == 2
    assert [len(chunk.text) for chunk in chunks] == [82, 82]


def test_packing_is_maximal_greedy_for_blocks_of_different_lengths() -> None:
    """No first block of a following chunk could fit greedily into its predecessor."""
    sizes = [30, 55, 10, 70, 25, 90, 15, 40]
    max_chars = 120
    doc = make_document(Section("Body", "\n\n".join(sized_block(size) for size in sizes)))
    chunks = chunk_document(doc, max_chars=max_chars)
    assert len(chunks) > 1
    assert len({chunk.section for chunk in chunks}) == 1
    for index in range(len(chunks) - 1):
        head = blocks_of(chunks[index + 1].text)[0]
        assert len(chunks[index].text) + 2 + len(head) > max_chars, (
            f"chunk {index} of {len(chunks[index].text)} chars could still greedily take "
            f"the first block of chunk {index + 1} ({len(head)} chars)"
        )


def test_chunk_sizes_stay_within_max_chars_and_no_word_is_lost_or_invented() -> None:
    sizes = [30, 55, 10, 70, 25, 90, 15, 40]
    max_chars = 120
    oversize = sized_block(500)
    section_text = "\n\n".join([*(sized_block(size) for size in sizes), oversize])
    cleaned = clean_text(section_text)
    chunks = chunk_document(make_document(Section("Body", section_text)), max_chars=max_chars)
    for chunk in chunks:
        if len(chunk.text) > max_chars:
            assert len(blocks_of(chunk.text)) == 1
        else:
            assert len(chunk.text) <= max_chars
    assert " ".join(chunk.text for chunk in chunks).split() == cleaned.split()