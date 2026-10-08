from src.application.agents import (
    DiagnosticSafetyPlanner,
    DiagnosticSafetyPlannerInput,
    SymptomMatcher,
    SymptomMatcherInput,
    WorkOrderGenerator,
    WorkOrderGeneratorInput,
)
from src.domain.rag import Evidence
from src.domain.workflow import EquipmentMatch, RevisionResolution, SafetyStepRecord
from src.infrastructure.providers.fake import FakeLLMProvider


class DummySafetyRepo:
    def required_for_documents(self, tenant_id: str, doc_ids):
        assert doc_ids == ["DOC-100"]
        return [SafetyStepRecord(id=1, step_no=1, text="Step 1 text", doc_id="DOC-1")]


def test_symptom_matcher_contract():
    evidence = Evidence(
        chunk_id=7,
        doc_id="DOC-7",
        title="Manual",
        section="Hydraulics",
        revision="Rev B",
        doc_status="current",
        page=None,
        text="High pressure troubleshooting",
    )

    class Embedder:
        model_name = "fake"
        def embed(self, texts):
            return [[0.1]]

    class Search:
        def search_dense(self, *args):
            return [evidence]
        def search_keyword(self, *args):
            return [evidence]

    class Settings:
        retrieval_min_similarity = 0.0

    matcher = SymptomMatcher(
        embedder=Embedder(), search=Search(), chain=FakeLLMProvider(), settings=Settings()
    )
    res = matcher.run(SymptomMatcherInput("high pressure reading", "tenant-alpha"))
    assert isinstance(res.match, EquipmentMatch)
    assert isinstance(res.evidence, tuple)
    assert res.match.doc_ids == ("DOC-7",)
    assert res.match.evidence_ids == (7,)


def test_diagnostic_safety_planner_contract():
    planner = DiagnosticSafetyPlanner()
    match = EquipmentMatch("EQ-100", ("DOC-100",), "Rev B", "current", (1,))
    plan = planner.run(
        DiagnosticSafetyPlannerInput(match, "Rev A", "tenant-alpha", ()),
        DummySafetyRepo(),
    )

    assert isinstance(plan.revision, RevisionResolution)
    assert plan.revision.revision == "Rev A"
    assert plan.revision.superseded is True
    assert len(plan.safety_steps) == 1
    assert plan.safety_steps[0].id == 1


def test_work_order_generator_contract():
    chain = FakeLLMProvider(script=['{"title": "Test WO", "summary": "Sum", "steps": ["Inspect vibration source"], "parts": []}'])
    generator = WorkOrderGenerator(chain)
    match = EquipmentMatch("EQ-100", ("DOC-100",), "Rev B", "current", (1,))
    rev_res = RevisionResolution("Rev B", False, "current")

    res = generator.generate(WorkOrderGeneratorInput("vibration", match, rev_res, (), ()))
    assert isinstance(res.work_order, dict)
    assert res.work_order["title"] == "Test WO"
    assert res.degraded is False
