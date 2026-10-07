"""Retrieval: fusion, keyword extraction, revision policy, collapse, retrieve."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.application.retrieval import (
    collapse_duplicates,
    keyword_terms,
    retrieve,
    rrf_fuse,
    wants_superseded_revisions,
)
from src.domain.rag import Evidence

TESTS_ROOT = Path(__file__).resolve().parents[1]
if str(TESTS_ROOT) not in sys.path:
    sys.path.insert(0, str(TESTS_ROOT))

from fakes import FakeChunkSearch, FakeEmbedder

K = 60
SETTINGS = SimpleNamespace(retrieval_min_similarity=0.55)


def ev(
    chunk_id: int,
    doc_id: str = "DOC-1",
    section: str = "Section",
    *,
    dense: float = 0.0,
    keyword: float = 0.0,
    fused: float = 0.0,
) -> Evidence:
    return Evidence(
        chunk_id=chunk_id,
        doc_id=doc_id,
        title=f"{doc_id} title",
        section=section,
        revision="Rev 1",
        doc_status="current",
        page=None,
        text=f"text of chunk {chunk_id}",
        dense_score=dense,
        keyword_score=keyword,
        fused_score=fused,
    )


def test_rrf_sums_one_over_k_plus_rank_across_lists() -> None:
    dense = [ev(1, dense=0.9), ev(2, dense=0.8)]
    keyword = [ev(2, keyword=0.7), ev(3, keyword=0.6)]

    fused = rrf_fuse([dense, keyword], k=K)

    scores = {item.chunk_id: item.fused_score for item in fused}
    assert scores[1] == pytest.approx(1 / 61)
    assert scores[2] == pytest.approx(1 / 62 + 1 / 61)
    assert scores[3] == pytest.approx(1 / 62)
    assert [item.chunk_id for item in fused] == [2, 1, 3]


def test_rrf_keeps_the_two_raw_scores_of_a_merged_chunk() -> None:
    dense = [ev(7, dense=0.91)]
    keyword = [ev(7, keyword=0.42)]

    fused = rrf_fuse([dense, keyword], k=K)

    assert len(fused) == 1
    assert fused[0].dense_score == pytest.approx(0.91)
    assert fused[0].keyword_score == pytest.approx(0.42)


def test_rrf_breaks_ties_by_chunk_id() -> None:
    fused = rrf_fuse([[ev(2)], [ev(1)]], k=K)

    assert [item.chunk_id for item in fused] == [1, 2]


def test_rrf_of_nothing_is_empty() -> None:
    assert rrf_fuse([], k=K) == []
    assert rrf_fuse([[], []], k=K) == []


def test_rrf_respects_the_limit() -> None:
    fused = rrf_fuse([[ev(1), ev(2), ev(3)]], k=K, limit=2)

    assert [item.chunk_id for item in fused] == [1, 2]


def test_keyword_terms_keep_only_safe_words_and_codes() -> None:
    terms = keyword_terms("Rev A: what is the 300-h oil interval?")

    assert terms == sorted(terms)
    assert "300-h" in terms
    assert "interval" in terms
    assert "rev" in terms
    assert all(term == term.lower() for term in terms)


def test_keyword_terms_drop_injection_characters() -> None:
    terms = keyword_terms("'; DROP TABLE chunks; --")

    assert terms == ["chunks", "drop", "table"]
    assert all(term.isalnum() for term in terms)


def test_keyword_terms_drop_short_words_and_duplicates() -> None:
    assert keyword_terms("a of to interval interval") == ["interval"]


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        ("What was the value in Rev A?", True),
        ("What does revision A say?", True),
        ("What was the previous set point?", True),
        ("Show me the older manual.", True),
        ("What changed between Rev A and Rev B?", True),
        ("What is the difference between the two manuals?", True),
        ("What is the current relief set point?", False),
        ("How do I reverse the motor?", False),
        ("Please review the lubrication schedule.", False),
    ],
)
def test_wants_superseded_revisions(question: str, expected: bool) -> None:
    assert wants_superseded_revisions(question) is expected


def test_collapse_keeps_the_highest_scored_twin() -> None:
    markdown = ev(1, doc_id="DOC-1", section="Set point", fused=0.5)
    pdf = ev(2, doc_id="DOC-1", section="Set point", fused=0.7)
    other = ev(3, doc_id="DOC-1", section="Interval", fused=0.6)

    collapsed = collapse_duplicates([markdown, pdf, other])

    assert [item.chunk_id for item in collapsed] == [2, 3]


def test_collapse_breaks_score_ties_by_chunk_id() -> None:
    first = ev(4, doc_id="DOC-2", section="Safety", fused=0.3)
    second = ev(2, doc_id="DOC-2", section="Safety", fused=0.3)

    collapsed = collapse_duplicates([first, second])

    assert [item.chunk_id for item in collapsed] == [2]


def test_retrieve_fuses_the_two_searches_with_the_embedder_model() -> None:
    embedder = FakeEmbedder()
    search = FakeChunkSearch(dense=[ev(1, dense=0.9)], keyword=[ev(2, doc_id="DOC-2", keyword=0.8)])

    result = retrieve("pump interval", "tenant-alpha", embedder, search, SETTINGS)

    assert [item.chunk_id for item in result] == [1, 2]
    tenant, vector, model, include_superseded, limit = search.dense_calls[0]
    assert tenant == "tenant-alpha"
    assert len(vector) == embedder.dimension
    assert model == embedder.model_name
    assert include_superseded is False
    assert limit == 20
    assert search.keyword_calls[0][1] == keyword_terms("pump interval")


def test_retrieve_asks_for_superseded_revisions_when_the_question_does() -> None:
    search = FakeChunkSearch()

    retrieve("what did Rev A say", "tenant-alpha", FakeEmbedder(), search, SETTINGS)

    assert search.dense_calls[0][3] is True
    assert search.keyword_calls[0][3] is True