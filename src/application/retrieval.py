"""Retrieval: hybrid search over the chunks, fused with Reciprocal Rank Fusion.

Dense (vector) and keyword (full text) search each return a ranked list. The
two lists are combined with RRF, duplicates from the Markdown/PDF twins are
collapsed, and the best few hits are returned as evidence for answering.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import replace
from typing import Protocol

from src.application.ports import Embedder
from src.domain.rag import Evidence

# How many hits each search contributes before fusion, and how many survive.
DENSE_LIMIT = 20
KEYWORD_LIMIT = 20
TOP_RESULTS = 6
RRF_K = 60

# Words and codes only: letters, digits and hyphens, at least three characters.
TERM_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]*")
MIN_TERM_LENGTH = 3

# Phrases that mean the caller wants older revisions, not only current ones.
SUPERSEDED_PHRASES = (
    "revision",
    "previous",
    "older",
    "changed between",
    "difference between",
)
REVISION_LETTER = re.compile(r"\brev\.?\s*[a-z]\b", re.IGNORECASE)


class ChunkSearch(Protocol):
    """The two searches retrieval needs, already filtered to one tenant."""

    def search_dense(
        self,
        tenant_id: str,
        vector: Sequence[float],
        embedding_model: str,
        include_superseded: bool,
        limit: int,
    ) -> list[Evidence]: ...

    def search_keyword(
        self,
        tenant_id: str,
        terms: Sequence[str],
        embedding_model: str,
        include_superseded: bool,
        limit: int,
    ) -> list[Evidence]: ...


class RetrievalSettings(Protocol):
    """The settings retrieval and answering read (kept small on purpose)."""

    retrieval_min_similarity: float


def keyword_terms(question: str) -> list[str]:
    """The safe tsquery terms of a question: lowercased, de-duplicated, sorted.

    Only ``[A-Za-z0-9][A-Za-z0-9-]*`` tokens of at least three characters are
    kept, so no operator or punctuation from the user can reach ``to_tsquery``.
    A trailing hyphen is trimmed because it would be a tsquery syntax error.
    """
    terms = {
        match.rstrip("-")
        for match in TERM_PATTERN.findall(question.lower())
        if len(match) >= MIN_TERM_LENGTH
    }
    return sorted(term for term in terms if len(term) >= MIN_TERM_LENGTH)


def wants_superseded_revisions(question: str) -> bool:
    """True when the question asks about an older or a named revision.

    This is the whole revision policy: by default only ``current`` documents
    are searched, and a superseded revision is searched only when the question
    clearly asks for one. It is a known limitation: a question that needs an
    older revision without saying so is answered from current documents only.
    """
    if REVISION_LETTER.search(question):
        return True
    lowered = question.lower()
    return any(phrase in lowered for phrase in SUPERSEDED_PHRASES)


def rrf_fuse(
    lists: Sequence[Sequence[Evidence]],
    k: int = RRF_K,
    limit: int | None = None,
) -> list[Evidence]:
    """Reciprocal Rank Fusion of ranked evidence lists.

    Every list contributes ``1 / (k + rank)`` to a chunk, where ``rank`` starts
    at 1 for the first item of that list, and the fused score of a chunk is the
    sum over all lists it appears in. The same chunk is merged once, keeping the
    larger of its dense and keyword scores. Ties are broken by ``chunk_id`` so
    the order is deterministic.
    """
    scores: dict[int, float] = {}
    merged: dict[int, Evidence] = {}
    for evidence_list in lists:
        for rank, item in enumerate(evidence_list, start=1):
            scores[item.chunk_id] = scores.get(item.chunk_id, 0.0) + 1.0 / (k + rank)
            previous = merged.get(item.chunk_id)
            if previous is None:
                merged[item.chunk_id] = item
            else:
                merged[item.chunk_id] = replace(
                    previous,
                    dense_score=max(previous.dense_score, item.dense_score),
                    keyword_score=max(previous.keyword_score, item.keyword_score),
                )
    fused = [
        replace(item, fused_score=scores[item.chunk_id]) for item in merged.values()
    ]
    fused.sort(key=lambda item: (-item.fused_score, item.chunk_id))
    if limit is not None:
        fused = fused[:limit]
    return fused


def collapse_duplicates(evidence: Sequence[Evidence]) -> list[Evidence]:
    """Keep the best hit per ``(doc_id, section)``, the one with the top score.

    The same section is stored twice for the six documents that exist both as
    Markdown and as PDF, so without this step the evidence would repeat.
    """
    best: dict[tuple[str, str], Evidence] = {}
    for item in evidence:
        key = (item.doc_id, item.section)
        current = best.get(key)
        if current is None or _beats(item, current):
            best[key] = item
    collapsed = list(best.values())
    collapsed.sort(key=lambda item: (-item.fused_score, item.chunk_id))
    return collapsed


def _beats(candidate: Evidence, current: Evidence) -> bool:
    """True when candidate outranks current (higher score, then lower id)."""
    if candidate.fused_score != current.fused_score:
        return candidate.fused_score > current.fused_score
    return candidate.chunk_id < current.chunk_id


def retrieve(
    question: str,
    tenant_id: str,
    embedder: Embedder,
    search: ChunkSearch,
    settings: RetrievalSettings,
) -> list[Evidence]:
    """Embed the question, run both searches, fuse, collapse and take the top 6.

    The question is embedded with the same model as the index (the embedder is
    the GuardedEmbedder), so dense scores are comparable to the stored vectors.
    """
    vector = embedder.embed([question])[0]
    model = embedder.model_name
    include_superseded = wants_superseded_revisions(question)
    terms = keyword_terms(question)
    dense = search.search_dense(
        tenant_id, vector, model, include_superseded, DENSE_LIMIT
    )
    keyword = search.search_keyword(
        tenant_id, terms, model, include_superseded, KEYWORD_LIMIT
    )
    fused = rrf_fuse([dense, keyword], k=RRF_K, limit=None)
    return collapse_duplicates(fused)[:TOP_RESULTS]
