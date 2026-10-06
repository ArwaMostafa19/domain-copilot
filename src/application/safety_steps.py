"""Read the numbered safety prerequisites out of an extracted document."""

from __future__ import annotations

import re

from src.application.clean import clean_text
from src.domain.documents import ExtractedDocument, ExtractionError, SafetyStep

SAFETY_SECTION_TITLE = "Safety prerequisites"
BLOCK_SEPARATOR = "\n\n"
NUMBERED_ITEM = re.compile(r"^(\d+)\.[ \t]*(.*)$")


def extract_safety_steps(doc: ExtractedDocument) -> list[SafetyStep]:
    """Return the numbered steps of every ``Safety prerequisites`` section.

    Sections with a different title are ignored, and blocks that do not open
    with a numbered item, such as an introduction or a closing paragraph, are
    not steps.
    """
    steps: list[SafetyStep] = []
    for section in doc.sections:
        if section.title != SAFETY_SECTION_TITLE:
            continue
        steps.extend(_steps_of(clean_text(section.text)))
    _reject_duplicates(steps)
    return steps


def _steps_of(text: str) -> list[SafetyStep]:
    steps: list[SafetyStep] = []
    for block in text.split(BLOCK_SEPARATOR):
        number = 0
        body: list[str] = []
        for line in block.split("\n"):
            match = NUMBERED_ITEM.match(line)
            if match is not None:
                if body:
                    steps.append(SafetyStep(step_no=number, text=" ".join(body)))
                number = int(match.group(1))
                body = [match.group(2)]
            elif body and line.strip():
                body.append(line.strip())
        if body:
            steps.append(SafetyStep(step_no=number, text=" ".join(body)))
    return steps


def _reject_duplicates(steps: list[SafetyStep]) -> None:
    seen: set[int] = set()
    for step in steps:
        if step.step_no in seen:
            raise ExtractionError(f"duplicate safety step number {step.step_no}")
        seen.add(step.step_no)