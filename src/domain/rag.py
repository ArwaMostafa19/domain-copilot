"""Domain types for retrieval and grounded answers.

An answer is only trusted when every statement in it cites a chunk that was
actually retrieved, so :class:`Evidence` and :class:`Citation` keep the ids and
the revision metadata the rest of the system must check.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.llm import TokenUsage


class RefusalReason:
    """Why an :class:`Answer` was refused instead of answered."""

    NO_EVIDENCE = "no_evidence"
    WEAK_EVIDENCE = "weak_evidence"
    INVALID_CITATION = "invalid_citation"


@dataclass(frozen=True)
class Evidence:
    """One retrieved chunk, with the two raw scores and the fused score."""

    chunk_id: int
    doc_id: str
    title: str
    section: str
    revision: str
    doc_status: str
    page: int | None
    text: str
    dense_score: float = 0.0
    keyword_score: float = 0.0
    fused_score: float = 0.0


@dataclass(frozen=True)
class Citation:
    """The source of one statement: a retrieved chunk and its revision."""

    chunk_id: int
    doc_id: str
    section: str
    revision: str
    page: int | None


@dataclass(frozen=True)
class Answer:
    """A grounded answer, or a refusal with a :class:`RefusalReason`."""

    text: str
    citations: tuple[Citation, ...]
    refused: bool
    reason: str | None
    usage: TokenUsage
    evidence: tuple[Evidence, ...]
