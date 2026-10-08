"""Domain types for the maintenance workflow.

These types are the contracts between the agents, the rules and storage. Every
frozen dataclass validates itself in ``__post_init__`` and raises a
``WorkflowError`` with a clear message, so a malformed plan can never reach the
database or the model.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class WorkflowError(Exception):
    """A violated domain rule of the maintenance workflow."""


class Role(str, Enum):
    """The two roles of the product. Only a supervisor may approve."""

    TECHNICIAN = "technician"
    SUPERVISOR = "supervisor"


class RunStatus(str, Enum):
    """The lifecycle of one copilot run."""

    RUNNING = "running"
    AWAITING_ACKNOWLEDGEMENT = "awaiting_acknowledgement"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    FAILED = "failed"
    COMPLETED = "completed"


TERMINAL_RUN_STATUSES = frozenset(
    {
        RunStatus.APPROVED,
        RunStatus.REJECTED,
        RunStatus.CANCELLED,
        RunStatus.FAILED,
        RunStatus.COMPLETED,
    }
)

#: Every allowed transition, keyed by (current status, event). ``None`` as the
#: current status means "the run does not exist yet".
TRANSITIONS: dict[tuple[RunStatus | None, str], RunStatus] = {
    (None, "create_draft"): RunStatus.RUNNING,
    (RunStatus.RUNNING, "await_acknowledgement"): RunStatus.AWAITING_ACKNOWLEDGEMENT,
    (RunStatus.AWAITING_ACKNOWLEDGEMENT, "acknowledge"): RunStatus.RUNNING,
    (RunStatus.RUNNING, "draft_ready"): RunStatus.PENDING_APPROVAL,
    (RunStatus.PENDING_APPROVAL, "approve"): RunStatus.APPROVED,
    (RunStatus.PENDING_APPROVAL, "reject"): RunStatus.REJECTED,
    (RunStatus.PENDING_APPROVAL, "edit"): RunStatus.PENDING_APPROVAL,
    (RunStatus.APPROVED, "complete"): RunStatus.COMPLETED,
    (RunStatus.RUNNING, "cancel"): RunStatus.CANCELLED,
    (RunStatus.AWAITING_ACKNOWLEDGEMENT, "cancel"): RunStatus.CANCELLED,
    (RunStatus.PENDING_APPROVAL, "cancel"): RunStatus.CANCELLED,
    (RunStatus.RUNNING, "fail"): RunStatus.FAILED,
    (RunStatus.AWAITING_ACKNOWLEDGEMENT, "fail"): RunStatus.FAILED,
    (RunStatus.PENDING_APPROVAL, "fail"): RunStatus.FAILED,
}

#: Events only a supervisor may trigger.
SUPERVISOR_EVENTS = frozenset({"approve", "reject", "edit"})


@dataclass(frozen=True)
class SymptomReport:
    """What the technician reported, and the revision they say is installed."""

    symptoms: str
    installed_revision: str | None = None

    def __post_init__(self) -> None:
        if not self.symptoms or not self.symptoms.strip():
            raise WorkflowError("symptoms must not be empty")


@dataclass(frozen=True)
class EquipmentMatch:
    """The equipment a symptom points at, with the evidence that proves it."""

    equipment_id: str
    doc_ids: tuple[str, ...]
    revision: str
    revision_status: str
    evidence_ids: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.equipment_id:
            raise WorkflowError("equipment_id must not be empty")
        if not self.doc_ids:
            raise WorkflowError("equipment match needs at least one document")
        if not self.revision:
            raise WorkflowError("equipment match needs a revision")
        if self.revision_status not in ("current", "superseded"):
            raise WorkflowError(
                f"revision_status must be 'current' or 'superseded', got {self.revision_status!r}"
            )
        if not self.evidence_ids:
            raise WorkflowError("equipment match needs at least one evidence id")


@dataclass(frozen=True)
class ClarificationRequest:
    """Returned by the matcher when the equipment cannot be identified with evidence."""

    question: str

    def __post_init__(self) -> None:
        if not self.question or not self.question.strip():
            raise WorkflowError("a clarification request needs a question")


@dataclass(frozen=True)
class DiagnosticStep:
    """One diagnostic action, always tied to the chunks that justify it."""

    text: str
    chunk_ids: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.text or not self.text.strip():
            raise WorkflowError("a diagnostic step needs text")
        if not self.chunk_ids:
            raise WorkflowError("every diagnostic step must cite at least one chunk")


@dataclass(frozen=True)
class SafetyStepRecord:
    """One row of ``safety_prerequisites``, read from the database, not the model."""

    id: int
    step_no: int
    text: str
    doc_id: str | None = None

    def __post_init__(self) -> None:
        if not self.text or not self.text.strip():
            raise WorkflowError("a safety step needs text")


@dataclass(frozen=True)
class DiagnosticPlan:
    """The ordered diagnostic plan plus the safety steps that gate it."""

    revision: str
    steps: tuple[DiagnosticStep, ...]
    required_safety: tuple[SafetyStepRecord, ...]

    def __post_init__(self) -> None:
        if not self.revision:
            raise WorkflowError("a diagnostic plan needs a revision")
        if not self.steps:
            raise WorkflowError("a diagnostic plan needs at least one step")


@dataclass(frozen=True)
class WorkOrderDraft:
    """A draft work order. It is only a draft until a supervisor approves it."""

    title: str
    equipment_id: str
    revision: str
    symptoms: str
    diagnostic_steps: tuple[DiagnosticStep, ...]
    safety_step_ids: tuple[int, ...]
    parts: tuple[str, ...]
    citations: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise WorkflowError("a work order needs a title")
        if not self.equipment_id:
            raise WorkflowError("a work order needs an equipment_id")
        if not self.revision:
            raise WorkflowError("a work order needs a revision")
        if not self.symptoms.strip():
            raise WorkflowError("a work order needs the reported symptoms")
        if not self.diagnostic_steps:
            raise WorkflowError("a work order needs at least one diagnostic step")
        if not self.citations:
            raise WorkflowError("a work order needs at least one citation")


@dataclass(frozen=True)
class GateResult:
    """The outcome of the safety gate: which required steps are missing."""

    ok: bool
    missing: tuple[int, ...]


@dataclass(frozen=True)
class RevisionResolution:
    """Which revision to use, and whether it is a superseded one."""

    revision: str
    superseded: bool
    note: str
