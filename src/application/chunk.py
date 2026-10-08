"""Split extracted sections into chunks that can be searched and cited."""

from __future__ import annotations

from src.application.clean import clean_text
from src.domain.documents import Chunk, ExtractedDocument

SAFETY_SECTION_TITLE = "Safety prerequisites"
DEFAULT_MAX_CHARS = 1800
BLOCK_SEPARATOR = "\n\n"


def chunk_document(doc: ExtractedDocument, max_chars: int = DEFAULT_MAX_CHARS) -> list[Chunk]:
    """Split every non-empty section of the document into chunks.

    A chunk never starts or ends inside a table, a numbered list or a bullet
    list: blank-line-separated blocks are the smallest unit and are packed
    whole, so an oversized block may exceed ``max_chars`` on its own.
    """
    chunks: list[Chunk] = []
    for section in doc.sections:
        text = clean_text(section.text)
        if not text:
            continue
        for chunk_text in _pack(section.title, text, max_chars):
            chunks.append(
                Chunk(
                    ordinal=len(chunks),
                    section=section.title,
                    context=f"{doc.meta.title} | {section.title} | {doc.meta.revision}",
                    text=chunk_text,
                    revision=doc.meta.revision,
                    page=section.page,
                )
            )
    return chunks


def _pack(section_title: str, text: str, max_chars: int) -> list[str]:
    """Pack consecutive blocks up to ``max_chars``; one section, one chunk."""
    if section_title == SAFETY_SECTION_TITLE:
        return [text]
    packed: list[str] = []
    current: list[str] = []
    length = 0
    for block in text.split(BLOCK_SEPARATOR):
        addition = len(block) + (len(BLOCK_SEPARATOR) if current else 0)
        if current and length + addition > max_chars:
            packed.append(BLOCK_SEPARATOR.join(current))
            current = []
            length = 0
            addition = len(block)
        current.append(block)
        length += addition
    if current:
        packed.append(BLOCK_SEPARATOR.join(current))
    return packed
