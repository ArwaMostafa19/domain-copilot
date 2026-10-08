import pytest

from src.application.agents import (
    WorkOrderGenerator,
    WorkOrderGeneratorInput,
)
from src.application.orchestrator import WorkflowOrchestrator, WorkflowStartInput
from src.domain.rag import Evidence
from src.domain.workflow import (
    EquipmentMatch,
    RevisionResolution,
    Role,
    SafetyStepRecord,
    WorkflowError,
)
from src.infrastructure.providers.fake import FakeLLMProvider
from tests.fakes import (
    FakeChunkSearch,
    FakeEmbedder,
    InMemoryAuditLog,
    InMemoryRunRepository,
    InMemorySafetyRepository,
    InMemoryWorkOrderRepository,
)


def test_work_order_generator_json_repair_once():
    # First response malformed JSON, second response valid JSON
    fake_provider = FakeLLMProvider(
        script=["This is not JSON text!", '{"title": "Repaired Plan", "summary": "Success", "steps": ["Step 1"], "parts": []}']
    )
    generator = WorkOrderGenerator(fake_provider)

    res = generator.generate(
        WorkOrderGeneratorInput(
            "leaking motor",
            EquipmentMatch("EQ-001", ("DOC-001",), "Rev A", "current", (1,)),
            RevisionResolution("Rev A", False, "current"),
            (),
            (),
        )
    )

    assert res.degraded is False
    assert res.work_order["title"] == "Repaired Plan"


def test_work_order_generator_degrades_to_plain_rag():
    # Both calls return invalid JSON
    fake_provider = FakeLLMProvider(script=["Bad JSON 1", "Bad JSON 2"])
    generator = WorkOrderGenerator(fake_provider)

    res = generator.generate(
        WorkOrderGeneratorInput(
            "leaking motor",
            EquipmentMatch("EQ-001", ("DOC-001",), "Rev A", "current", (1,)),
            RevisionResolution("Rev A", False, "current"),
            (Evidence(chunk_id=1, doc_id="DOC-001", title="Manual", section="Safety", revision="Rev A", doc_status="current", page=None, text="Use safety goggles", dense_score=0.9, keyword_score=1.0),),
            (),
        )
    )

    assert res.degraded is True
    assert "Degraded Work Order" in str(res.work_order["title"])


def test_safety_prerequisites_are_included_even_when_model_omits_them():
    safety = SafetyStepRecord(id=81, step_no=1, text="Lock out the hydraulic supply")
    generator = WorkOrderGenerator(
        FakeLLMProvider(
            script=['{"title":"Safe plan","summary":"Plan","steps":["Inspect"],"parts":[]}']
        )
    )
    result = generator.generate(
        WorkOrderGeneratorInput(
            "pressure loss",
            EquipmentMatch("EQ-1", ("DOC-1",), "Rev B", "current", (7,)),
            RevisionResolution("Rev B", False, "current"),
            (Evidence(chunk_id=7, doc_id="DOC-1", title="Manual", section="Safety", revision="Rev B", doc_status="current", page=None, text="Lock out before service"),),
            (safety,),
        )
    )

    assert result.work_order["safety_prerequisites"] == [
        {"id": 81, "step_no": 1, "text": "Lock out the hydraulic supply"}
    ]


def test_orchestrator_runs_typed_flow_through_work_order():
    evidence = Evidence(
        chunk_id=7,
        doc_id="DOC-7",
        title="Press manual",
        section="Troubleshooting",
        revision="Rev B",
        doc_status="current",
        page=2,
        text="Check pressure after locking out the hydraulic supply.",
        dense_score=0.9,
        keyword_score=1.0,
    )
    safety = SafetyStepRecord(
        id=81, step_no=1, text="Lock out the hydraulic supply", doc_id="DOC-7"
    )
    run_repo = InMemoryRunRepository()
    order_repo = InMemoryWorkOrderRepository()
    orchestrator = WorkflowOrchestrator(
        run_repo=run_repo,
        work_order_repo=order_repo,
        audit_log=InMemoryAuditLog(),
        safety_repo=InMemorySafetyRepository([safety]),
        embedder=FakeEmbedder(),
        search=FakeChunkSearch(dense=[evidence], keyword=[evidence]),
        chain=FakeLLMProvider(
            script=['{"title":"Press repair","summary":"Check pressure","steps":["Inspect"],"parts":[]}']
        ),
        settings=type("Settings", (), {"retrieval_min_similarity": 0.55})(),
    )

    start = orchestrator.start_run(
        WorkflowStartInput("pressure loss", "Rev B", 5, "tenant-alpha")
    )
    while True:
        try:
            next(start)
        except StopIteration as stopped:
            start_result = stopped.value
            break

    generation = orchestrator.generate(
        start_result.run_id,
        user_id=5,
        tenant_id="tenant-alpha",
        acknowledged_step_ids=[81],
    )
    while True:
        try:
            next(generation)
        except StopIteration as stopped:
            generated = stopped.value
            break

    assert generated["safety_prerequisites"] == [
        {"id": 81, "step_no": 1, "text": "Lock out the hydraulic supply"}
    ]
    assert run_repo.get("tenant-alpha", start_result.run_id).status == "pending_approval"


def test_technician_cannot_approve():
    run_repo = InMemoryRunRepository()
    wo_repo = InMemoryWorkOrderRepository()
    audit_log = InMemoryAuditLog()
    safety_repo = InMemorySafetyRepository([SafetyStepRecord(id=101, step_no=1, text="Isolate valve", doc_id="DOC-001")])

    run_id = run_repo.create("tenant-alpha", 1, "symptoms")
    run_repo.set_status("tenant-alpha", run_id, "pending_approval")
    wo_repo.create_draft("tenant-alpha", run_id, {"title": "Draft WO"})

    orch = WorkflowOrchestrator(
        run_repo=run_repo,
        work_order_repo=wo_repo,
        audit_log=audit_log,
        safety_repo=safety_repo,
        embedder=None,
        search=None,
        chain=FakeLLMProvider(),
        settings=None,
    )

    with pytest.raises(WorkflowError, match="role technician may not 'approve'"):
        orch.approval(
            run_id=run_id,
            decision="approve",
            role=Role.TECHNICIAN,
            user_id=1,
            tenant_id="tenant-alpha",
        )
