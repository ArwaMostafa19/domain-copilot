"""Run the retrieval and grounded-answer evaluation against the live index.

Examples::

    python -m src.eval.run
    python -m src.eval.run --with-answers

The default run is deterministic with respect to the configured index and
embedding provider. ``--with-answers`` also calls the configured chat provider.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.application.answering import AnswerDeps, _refusal_gate, answer_question
from src.application.embedding import GuardedEmbedder
from src.application.retrieval import retrieve
from src.domain.llm import ConfigError, EmbeddingModelMismatchError
from src.eval.questions import GOLDEN_PATH, load_golden_cases
from src.infrastructure.chunk_search import PostgresChunkSearch
from src.infrastructure.config import load_settings_from_environ
from src.infrastructure.embedding_registry import PostgresEmbeddingIndexRegistry
from src.infrastructure.providers.factory import build_chain, build_embedding_stack


@dataclass(frozen=True)
class CaseResult:
    case: dict[str, Any]
    retrieved: list[dict[str, Any]]
    evidence_hit: bool | None
    supported_facts: int
    expected_facts: int
    refused_by_gate: bool
    answer_grounded: bool | None = None
    refusal_correct: bool | None = None


class QuestionEmbedCache:
    """Answering and retrieval reuse precomputed eval-question vectors."""

    def __init__(self, model_name: str, vectors: dict[str, list[float]]) -> None:
        self.model_name = model_name
        self._vectors = vectors

    def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            return [self._vectors[text] for text in texts]
        except KeyError as error:
            raise ValueError("evaluation tried to embed an unregistered question") from error


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate retrieval and grounding.")
    parser.add_argument("--golden", type=Path, default=GOLDEN_PATH)
    parser.add_argument("--top-k", type=int, default=6)
    parser.add_argument(
        "--only-adversarial",
        action="store_true",
        help="score the adversarial subset only (the full golden set is still validated)",
    )
    parser.add_argument(
        "--with-answers",
        action="store_true",
        help="also call the configured chat model and score its citations and facts",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="write the full baseline report as JSON to this path",
    )
    args = parser.parse_args(argv)
    if args.top_k < 1:
        parser.error("--top-k must be positive")

    try:
        cases = load_golden_cases(args.golden)
        if len(cases) < 25:
            raise ValueError(f"golden set has {len(cases)} cases; expected at least 25")
        if args.only_adversarial:
            cases = [case for case in cases if case.get("adversarial")]
        settings = load_settings_from_environ()
        provider, guard = build_embedding_stack(
            settings, PostgresEmbeddingIndexRegistry()
        )
        guard.ensure(settings.embedding_spec())
        embedder = GuardedEmbedder(provider, guard, settings.embedding_spec())
        questions = list(dict.fromkeys(str(case["question"]) for case in cases))
        print(f"Embedding {len(questions)} evaluation questions in one batch...", flush=True)
        vectors = embedder.embed(questions)
        cached_embedder = QuestionEmbedCache(
            embedder.model_name, dict(zip(questions, vectors, strict=True))
        )
        search = PostgresChunkSearch()
        chain = build_chain(settings) if args.with_answers else None
    except (ConfigError, EmbeddingModelMismatchError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    results: list[CaseResult] = []
    for case in cases:
        evidence = retrieve(
            case["question"], case["tenant"], cached_embedder, search, settings
        )
        refs = case["evidence"]
        hit = all(
            any(item.doc_id == ref["doc_id"] and item.section == ref["section"] for item in evidence)
            for ref in refs
        ) if refs else None
        evidence_text = "\n".join(item.text for item in evidence).casefold()
        facts = case["expected_facts"]
        supported = sum(_normalise(fact) in _normalise(evidence_text) for fact in facts)
        refused = (
            _refusal_gate(evidence, settings.retrieval_min_similarity) is not None
        )

        grounded: bool | None = None
        refusal_correct: bool | None = None
        if chain is not None:
            answer = answer_question(
                case["question"],
                case["tenant"],
                AnswerDeps(cached_embedder, search, chain, settings),
            )
            citation_ids = {citation.chunk_id for citation in answer.citations}
            retrieved_ids = {item.chunk_id for item in evidence}
            expected_docs = {ref["doc_id"] for ref in refs}
            citation_matches_gold = bool(expected_docs) and any(
                citation.doc_id in expected_docs for citation in answer.citations
            )
            answer_facts_present = all(
                _normalise(fact) in _normalise(answer.text) for fact in facts
            )
            grounded = (
                not answer.refused
                and bool(citation_ids)
                and citation_ids <= retrieved_ids
                and citation_matches_gold
                and answer_facts_present
            ) if facts else (answer.refused if case["should_refuse"] else not answer.refused)
            refusal_correct = answer.refused == case["should_refuse"]

        results.append(
            CaseResult(
                case,
                [
                    {
                        "chunk_id": item.chunk_id,
                        "doc_id": item.doc_id,
                        "section": item.section,
                        "revision": item.revision,
                        "dense_score": item.dense_score,
                    }
                    for item in evidence
                ],
                hit,
                supported,
                len(facts),
                refused,
                grounded,
                refusal_correct,
            )
        )

    report = _print_report(results, args.top_k, args.with_answers)
    report.update(
        {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "embedding_model": settings.embedding_model,
            "retrieval_min_similarity": settings.retrieval_min_similarity,
            "with_answers": args.with_answers,
            "scope": "adversarial_only" if args.only_adversarial else "full_golden_set",
        }
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"baseline report written to {args.output}")
    return 0


def _normalise(value: str) -> str:
    return re.sub(r"\s+", " ", value.casefold()).strip()


def _rate(numerator: int, denominator: int) -> str:
    return f"{numerator / denominator:.1%}" if denominator else "n/a"


def _ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _print_report(
    results: list[CaseResult], top_k: int, with_answers: bool
) -> dict[str, Any]:
    hit_cases = [result for result in results if result.evidence_hit is not None]
    fact_total = sum(result.expected_facts for result in results)
    supported_total = sum(result.supported_facts for result in results)
    gate_correct = sum(
        result.refused_by_gate == result.case["should_refuse"] for result in results
    )
    expected_refusals = [result for result in results if result.case["should_refuse"]]
    correct_refusals = sum(result.refused_by_gate for result in expected_refusals)

    print(f"cases: {len(results)}")
    print(f"adversarial cases: {sum(bool(r.case.get('adversarial')) for r in results)}")
    print(
        f"retrieval hit-rate@{top_k}: "
        f"{_rate(sum(r.evidence_hit is True for r in hit_cases), len(hit_cases))} "
        f"({sum(r.evidence_hit is True for r in hit_cases)}/{len(hit_cases)} cases with expected evidence)"
    )
    print(
        "evidence groundedness (expected key facts present in retrieved chunks): "
        f"{_rate(supported_total, fact_total)} ({supported_total}/{fact_total} facts)"
    )
    print(
        "pre-generation refusal-gate accuracy: "
        f"{_rate(gate_correct, len(results))} ({gate_correct}/{len(results)} cases)"
    )
    print(
        "pre-generation refusal recall: "
        f"{_rate(correct_refusals, len(expected_refusals))} "
        f"({correct_refusals}/{len(expected_refusals)} expected refusals)"
    )
    if with_answers:
        grounded_count = sum(result.answer_grounded is True for result in results)
        refusal_count = sum(result.refusal_correct is True for result in results)
        print(
            "answer groundedness (expected facts + gold-source citation + retrieved chunk): "
            f"{_rate(grounded_count, len(results))} ({grounded_count}/{len(results)} cases)"
        )
        print(
            "end-to-end refusal correctness: "
            f"{_rate(refusal_count, len(results))} ({refusal_count}/{len(results)} cases)"
        )
    print("\ncase_id                         hit  gate_refuse  expected_refuse  facts")
    for result in results:
        case = result.case
        hit = "n/a" if result.evidence_hit is None else str(result.evidence_hit).lower()
        print(
            f"{case['id']:<31} {hit:<5} {str(result.refused_by_gate).lower():<12} "
            f"{str(case['should_refuse']).lower():<16} "
            f"{result.supported_facts}/{result.expected_facts}"
        )
        if result.evidence_hit is False:
            sources = ", ".join(
                f"{item['doc_id']} / {item['section']}" for item in result.retrieved
            )
            print(f"  retrieved: {sources or '(no chunks)'}")
    report: dict[str, Any] = {
        "cases": len(results),
        "adversarial_cases": sum(bool(r.case.get("adversarial")) for r in results),
        "top_k": top_k,
        "retrieval_hit_rate": {
            "numerator": sum(r.evidence_hit is True for r in hit_cases),
            "denominator": len(hit_cases),
            "rate": _ratio(sum(r.evidence_hit is True for r in hit_cases), len(hit_cases)),
        },
        "evidence_groundedness": {
            "numerator": supported_total,
            "denominator": fact_total,
            "rate": _ratio(supported_total, fact_total),
        },
        "pre_generation_refusal_gate_accuracy": {
            "numerator": gate_correct,
            "denominator": len(results),
            "rate": _ratio(gate_correct, len(results)),
        },
        "pre_generation_refusal_recall": {
            "numerator": correct_refusals,
            "denominator": len(expected_refusals),
            "rate": _ratio(correct_refusals, len(expected_refusals)),
        },
        "per_case": [
            {
                "id": result.case["id"],
                "kind": result.case["kind"],
                "adversarial": result.case.get("adversarial"),
                "retrieved": result.retrieved,
                "evidence_hit": result.evidence_hit,
                "expected_fact_coverage": {
                    "numerator": result.supported_facts,
                    "denominator": result.expected_facts,
                },
                "refused_by_gate": result.refused_by_gate,
                "should_refuse": result.case["should_refuse"],
                "answer_grounded": result.answer_grounded,
                "refusal_correct": result.refusal_correct,
            }
            for result in results
        ],
    }
    if with_answers:
        report["answer_groundedness"] = {
            "numerator": sum(r.answer_grounded is True for r in results),
            "denominator": len(results),
            "rate": _ratio(sum(r.answer_grounded is True for r in results), len(results)),
        }
        report["end_to_end_refusal_correctness"] = {
            "numerator": sum(r.refusal_correct is True for r in results),
            "denominator": len(results),
            "rate": _ratio(sum(r.refusal_correct is True for r in results), len(results)),
        }
    return report


if __name__ == "__main__":
    sys.exit(main())
