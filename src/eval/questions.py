"""Calibration questions: read from the golden set, or a small built-in list."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

IN_CORPUS_KINDS = ("answerable", "revision")
OUT_OF_CORPUS_KIND = "out_of_corpus"


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
