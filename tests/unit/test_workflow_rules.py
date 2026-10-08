from src.application import rules
from src.domain.workflow import (
    EquipmentMatch,
    Role,
    RunStatus,
    WorkflowError,
)


def test_resolve_revision_installed_wins():
    match = EquipmentMatch(
        equipment_id="EQ",
        doc_ids=("d1",),
        revision="Rev B",
        revision_status="current",
        evidence_ids=(1,),
    )
    res = rules.resolve_revision(match, installed_revision="Rev A")
    assert res.revision == "Rev A"
    assert res.superseded is True


def test_resolve_revision_default_current():
    match = EquipmentMatch(
        equipment_id="EQ",
        doc_ids=("d1",),
        revision="Rev A",
        revision_status="current",
        evidence_ids=(1,),
    )
    res = rules.resolve_revision(match, installed_revision=None)
    assert res.revision == "Rev A"
    assert res.superseded is False


def test_check_safety_gate_missing():
    gate = rules.check_safety_gate((1, 2, 3), (1,))
    assert gate.ok is False
    assert gate.missing == (2, 3)


def test_next_state_forbidden_technician_approve():
    try:
        rules.next_state(RunStatus.PENDING_APPROVAL, "approve", Role.TECHNICIAN)
        assert False
    except WorkflowError:
        pass


def test_next_state_approve_requires_gate():
    try:
        rules.next_state(RunStatus.PENDING_APPROVAL, "approve", Role.SUPERVISOR, gate_satisfied=False)
        assert False
    except WorkflowError:
        pass


def test_parts_from_evidence_filters_invented():
    class E:
        def __init__(self, t): self.text = t

    kept = rules.parts_from_evidence(("gasket", "invented-123"), [E("Replace the gasket")])
    assert kept == ("gasket",)
