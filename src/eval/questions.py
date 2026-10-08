"""Calibration and typed golden-set loading for evaluation commands."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

IN_CORPUS_KINDS = ("answerable", "revision")
OUT_OF_CORPUS_KIND = "out_of_corpus"
GOLDEN_PATH = Path(__file__).resolve().parents[2] / "eval" / "golden.jsonl"


@dataclass(frozen=True)
class CalibrationQuestion:
    """One question and whether its answer should exist in the corpus."""

    tenant: str
    question: str
    in_corpus: bool


# A small built-in list so the command works before eval/golden.jsonl exists.
DEFAULT_QUESTIONS: tuple[CalibrationQuestion, ...] = (
    CalibrationQuestion(
        "tenant-alpha", "What is the relief set point of the ALPHA-HP-200?", True
    ),
    CalibrationQuestion(
        "tenant-alpha", "What compressor lubricant does the ALPHA-AC-75 use?", True
    ),
    CalibrationQuestion(
        "tenant-alpha", "What interval does the press oil analysis use now?", True
    ),
    CalibrationQuestion(
        "tenant-beta", "What is the relief set point of the BETA-HP-200?", True
    ),
    CalibrationQuestion(
        "tenant-beta", "What alarm code means high head pressure on the chiller?", True
    ),
    CalibrationQuestion(
        "tenant-alpha", "What is the torque of the AM-MAN-HP210 tie rod?", False
    ),
    CalibrationQuestion(
        "tenant-alpha", "What is the gearbox ratio of the ALPHA-GM-99?", False
    ),
    CalibrationQuestion(
        "tenant-beta", "What is the grease quantity for the accumulator HP-200B?", False
    ),
    CalibrationQuestion(
        "tenant-beta", "What is the pre-charge of the P-100A accumulator?", False
    ),
)


def load_questions(path: Path) -> list[CalibrationQuestion]:
    """Read the golden questions, or [] when the file does not exist yet.

    Only ``answerable`` and ``revision`` questions count as in-corpus, and
    ``out_of_corpus`` as out-of-corpus; every other kind is skipped.
    """
    if not path.is_file():
        return []
    questions: list[CalibrationQuestion] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        data = json.loads(line)
        kind = data.get("kind")
        if kind == "out_of_corpus":
            in_corpus = False
        elif kind in ("answerable", "revision"):
            in_corpus = True
        else:
            continue
        questions.append(
            CalibrationQuestion(
                tenant=str(data["tenant"]),
                question=str(data["question"]),
                in_corpus=in_corpus,
            )
        )
    return questions


def load_golden_cases(path: Path = GOLDEN_PATH) -> list[dict[str, object]]:
    """Load and validate the full evaluation set before any database calls."""
    if not path.is_file():
        raise ValueError(f"golden set not found: {path}")
    cases: list[dict[str, object]] = []
    ids: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid JSON on {path}:{line_number}: {error.msg}") from error
        if not isinstance(raw, dict):
            raise TypeError(f"case on {path}:{line_number} must be a JSON object")
        required = {"id", "tenant", "kind", "question", "expected_answer", "evidence", "expected_facts", "should_refuse"}
        missing = required - raw.keys()
        if missing:
            raise ValueError(f"case on {path}:{line_number} missing {sorted(missing)}")
        case_id = raw["id"]
        if not isinstance(case_id, str) or not case_id or case_id in ids:
            raise ValueError(f"case on {path}:{line_number} has an empty or duplicate id")
        ids.add(case_id)
        if raw["tenant"] not in {"tenant-alpha", "tenant-beta"}:
            raise ValueError(f"case {case_id}: tenant must name a configured tenant")
        if raw["kind"] not in {
            "answerable", "revision", "ambiguous", "prompt_injection",
            "conflicting_sources", "out_of_corpus",
        }:
            raise ValueError(f"case {case_id}: unsupported kind {raw['kind']!r}")
        if not isinstance(raw["question"], str) or not raw["question"].strip():
            raise ValueError(f"case {case_id}: question must be non-empty text")
        if not isinstance(raw["expected_answer"], str) or not raw["expected_answer"].strip():
            raise ValueError(f"case {case_id}: expected_answer must be non-empty text")
        if not isinstance(raw["evidence"], list) or not all(
            isinstance(ref, dict)
            and isinstance(ref.get("doc_id"), str)
            and isinstance(ref.get("section"), str)
            for ref in raw["evidence"]
        ):
            raise ValueError(f"case {case_id}: evidence must be a list of doc_id/section objects")
        if not isinstance(raw["expected_facts"], list) or not all(
            isinstance(fact, str) and fact.strip() for fact in raw["expected_facts"]
        ):
            raise ValueError(f"case {case_id}: expected_facts must be non-empty strings")
        if not isinstance(raw["should_refuse"], bool):
            raise TypeError(f"case {case_id}: should_refuse must be boolean")
        cases.append(raw)

    adversarial = [case for case in cases if case.get("adversarial")]
    injections = [case for case in cases if str(case.get("adversarial", "")).endswith("prompt_injection")]
    injection_types = {case.get("adversarial") for case in injections}
    required_adversarial = {
        "out_of_corpus", "ambiguous", "conflicting_sources",
        "direct_prompt_injection", "indirect_prompt_injection",
    }
    missing_adversarial = required_adversarial - {
        case.get("adversarial") for case in adversarial
    }
    if len(cases) < 25:
        raise ValueError(f"golden set contains {len(cases)} cases; at least 25 are required")
    if len(adversarial) < 5:
        raise ValueError(f"golden set contains {len(adversarial)} adversarial cases; at least 5 are required")
    if len(injections) < 3 or not {
        "direct_prompt_injection", "indirect_prompt_injection"
    } <= injection_types:
        raise ValueError("golden set needs at least 3 direct/indirect prompt-injection cases")
    if missing_adversarial:
        raise ValueError(
            f"golden set is missing adversarial categories: {sorted(missing_adversarial)}"
        )
    return cases
