"""Pure workflow rules.

Nothing here calls a model, the database or the clock: the safety gate and the
state machine are deterministic, so the same inputs always produce the same
result no matter what the LLM said.
"""

from __future__ import annotations

from collections.abc import Sequence

from src.domain.rag import Evidence
from src.domain.workflow import (
    SUPERVISOR_EVENTS,
    TRANSITIONS,
    EquipmentMatch,
    GateResult,
    RevisionResolution,
    Role,
    RunStatus,
    WorkflowError,
)


def resolve_revision(
    match: EquipmentMatch, installed_revision: str | None
) -> RevisionResolution:
    """Choose the revision to work from.

    The revision the technician states is installed wins, even when it is an
    older one; otherwise the current revision from the match is used. A
    superseded choice is always flagged so the plan can say so.
    """
    if installed_revision:
        superseded = installed_revision != match.revision
        if superseded:
            note = (
                f"using the technician's installed revision {installed_revision} "
                f"instead of the current {match.revision}; this revision is superseded"
            )
        else:
            note = f"using the technician's installed revision {installed_revision}"
        return RevisionResolution(installed_revision, superseded, note)
    superseded = match.revision_status == "superseded"
    if superseded:
        note = f"using the matched revision {match.revision}, which is superseded"
    else:
        note = f"using the current revision {match.revision}"
    return RevisionResolution(match.revision, superseded, note)


def check_safety_gate(
    required_step_ids: tuple[int, ...] | list[int],
    acknowledged_step_ids: tuple[int, ...] | list[int],
) -> GateResult:
    """Succeed only when every required step id was acknowledged.

    Acknowledged ids that are not required are ignored. The result depends only
    on these two collections, so no LLM output can change it.
    """
    required = set(required_step_ids)
    acknowledged = set(acknowledged_step_ids)
    missing = tuple(sorted(required - acknowledged))
    return GateResult(ok=not missing, missing=missing)


def next_state(
    current: RunStatus | None,
    event: str,
    role: Role,
    *,
    gate_satisfied: bool = True,
) -> RunStatus:
    """Return the next status, or raise ``WorkflowError`` for a forbidden move."""
    if event in SUPERVISOR_EVENTS and role != Role.SUPERVISOR:
        raise WorkflowError(f"role {role.value} may not '{event}'")
    if event == "approve" and not gate_satisfied:
        raise WorkflowError("the safety gate must be satisfied again before approval")
    try:
        return TRANSITIONS[(current, event)]
    except KeyError:
        where = current.value if current is not None else "no run"
        raise WorkflowError(f"cannot '{event}' from {where}") from None


def parts_from_evidence(
    proposed: tuple[str, ...] | list[str], evidence: Sequence[Evidence]
) -> tuple[str, ...]:
    """Keep only the proposed parts (and values) that appear in the evidence.

    The work order generator may suggest parts, torque values or intervals, but
    anything the retrieved chunks do not contain is dropped, so the model can
    never invent one.
    """
    lowered = " ".join(item.text for item in evidence).lower()
    kept: list[str] = []
    seen: set[str] = set()
    for part in proposed:
        if not part or not part.strip():
            continue
        key = part.strip().lower()
        if key in seen:
            continue
        if key in lowered:
            kept.append(part.strip())
            seen.add(key)
    return tuple(kept)
