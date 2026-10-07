"""Calibrate the retrieval similarity threshold against the real index.

    python -m src.eval.calibrate

It runs the dense search for a list of in-corpus and out-of-corpus questions,
prints the best-hit similarity of each, and suggests a threshold: the midpoint
between the lowest in-corpus best score and the highest out-of-corpus best
score, with a warning when the two ranges overlap. It changes no setting.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from src.application.embedding import GuardedEmbedder
from src.domain.llm import ConfigError, EmbeddingModelMismatchError
from src.eval.questions import DEFAULT_QUESTIONS, CalibrationQuestion, load_questions
from src.infrastructure.chunk_search import PostgresChunkSearch
from src.infrastructure.config import load_settings_from_environ
from src.infrastructure.embedding_registry import PostgresEmbeddingIndexRegistry
from src.infrastructure.providers.factory import build_embedding_stack

GOLDEN_PATH = Path(__file__).resolve().parents[2] / "eval" / "golden.jsonl"


@dataclass(frozen=True)
class CalibrationResult:
    """The suggested threshold and how much the two score ranges overlap."""

    suggested_threshold: float | None
    overlap: float


def suggest_threshold(
    in_corpus_scores: list[float], out_of_corpus_scores: list[float]
) -> CalibrationResult:
    """Midpoint of the two ranges, and their overlap (positive means overlap)."""
    if not in_corpus_scores or not out_of_corpus_scores:
        return CalibrationResult(None, 0.0)
    lowest_in_corpus = min(in_corpus_scores)
    highest_out_of_corpus = max(out_of_corpus_scores)
    threshold = (lowest_in_corpus + highest_out_of_corpus) / 2
    return CalibrationResult(threshold, highest_out_of_corpus - lowest_in_corpus)


def main(argv: list[str] | None = None) -> int:
    """Run the calibration and print the suggested threshold."""
    parser = argparse.ArgumentParser(description="Calibrate the retrieval threshold.")
    parser.add_argument("--golden", type=Path, default=GOLDEN_PATH)
    args = parser.parse_args(argv)
    try:
        settings = load_settings_from_environ()
        provider, guard = build_embedding_stack(
            settings, PostgresEmbeddingIndexRegistry()
        )
        guard.ensure(settings.embedding_spec())
    except (ConfigError, EmbeddingModelMismatchError) as error:
        print(f"error: {error}")
        return 2
    embedder = GuardedEmbedder(provider, guard, settings.embedding_spec())
    search = PostgresChunkSearch()
    questions = load_questions(args.golden) or list(DEFAULT_QUESTIONS)

    in_corpus: list[float] = []
    out_of_corpus: list[float] = []
    print("tenant        kind          score  question")
    for item in questions:
        score = _best_dense_score(search, embedder, item)
        bucket = in_corpus if item.in_corpus else out_of_corpus
        if score is not None:
            bucket.append(score)
        kind = "in-corpus" if item.in_corpus else "out-corpus"
        shown = f"{score:.3f}" if score is not None else "none"
        print(f"{item.tenant:<13} {kind:<12} {shown:>5}  {item.question}")
    _print_suggestion(suggest_threshold(in_corpus, out_of_corpus))
    print(f"current RETRIEVAL_MIN_SIMILARITY: {settings.retrieval_min_similarity}")
    return 0


def _best_dense_score(
    search: PostgresChunkSearch, embedder: GuardedEmbedder, item: CalibrationQuestion
) -> float | None:
    """The dense similarity of the best hit for one question, or None."""
    vector = embedder.embed([item.question])[0]
    hits = search.search_dense(
        item.tenant, vector, embedder.model_name, False, 1
    )
    return hits[0].dense_score if hits else None


def _print_suggestion(result: CalibrationResult) -> None:
    print()
    if result.suggested_threshold is None:
        print("not enough data to suggest a threshold")
        return
    print(f"overlap: {result.overlap:.3f}")
    if result.overlap > 0:
        print("warning: the in-corpus and out-of-corpus ranges overlap")
    print(f"suggested threshold: {result.suggested_threshold:.3f}")


if __name__ == "__main__":
    sys.exit(main())
