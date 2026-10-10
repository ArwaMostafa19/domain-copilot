import pytest

from src.application.agents import (
    DiagnosticSafetyPlanner,
    DiagnosticSafetyPlannerInput,
    EquipmentNotFoundError,
    SymptomMatcher,
    SymptomMatcherInput,
    WorkflowInputError,
    WorkOrderGenerator,
    WorkOrderGeneratorInput,
)
from src.domain.llm import CompletionResult, TokenUsage
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


def test_symptom_matcher_rejects_unrelated_input_even_with_high_dense_score():
    evidence = Evidence(
        chunk_id=7,
        doc_id="DOC-7",
        title="Hydraulic press manual",
        section="Troubleshooting",
        revision="Rev B",
        doc_status="current",
        page=None,
        text="Inspect the hydraulic pump and accumulator.",
        dense_score=0.91,
    )

    class Embedder:
        model_name = "fake"
        def embed(self, texts):
            return [[0.1]]

    class Search:
        def search_dense(self, *args):
            return [evidence]
        def search_keyword(self, *args):
            return []

    class Settings:
        retrieval_min_similarity = 0.55

    matcher = SymptomMatcher(Embedder(), Search(), FakeLLMProvider(), Settings())
    with pytest.raises(WorkflowInputError, match="relevant maintenance evidence"):
        matcher.run(SymptomMatcherInput("how are you", "tenant-beta"))


def test_symptom_matcher_rejects_equipment_from_another_tenant():
    evidence = Evidence(
        chunk_id=7,
        doc_id="ALPHA-MAN-HP200-B",
        title="ALPHA-HP-200 manual",
        section="Technical data",
        revision="Rev B",
        doc_status="current",
        page=None,
        text="Hydraulic press operating limits.",
        dense_score=0.91,
        equipment="ALPHA-HP-200",
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
        retrieval_min_similarity = 0.55

    matcher = SymptomMatcher(Embedder(), Search(), FakeLLMProvider(), Settings())
    with pytest.raises(EquipmentNotFoundError, match="No maintenance information"):
        matcher.run(SymptomMatcherInput("What is the relief setting for BETA-HP-200?", "tenant-beta"))


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


def test_diagnostic_planner_does_not_mix_checklists_from_other_procedures():
    evidence = (
        Evidence(
            chunk_id=1,
            doc_id="BETA-DIA-P100-1",
            title="BETA-P-100 Hydraulic Power Unit Diagnostic Procedure",
            section="Safety prerequisites",
            revision="Rev 1",
            doc_status="current",
            page=None,
            text="The unstable pressure and accumulator pressure are checked using the hydraulic power unit procedure.",
            equipment="BETA-P-100",
        ),
        Evidence(
            chunk_id=2,
            doc_id="BETA-PM-HP200-B",
            title="BETA-HP-200 Hydraulic Press Preventive Maintenance",
            section="Safety prerequisites",
            revision="Rev B",
            doc_status="current",
            page=None,
            text="Preventive maintenance tasks and routine pressure checks.",
            equipment="BETA-HP-200",
        ),
    )
    steps = [
        SafetyStepRecord(id=i, step_no=i, text=f"Accumulator pressure prerequisite {i}", doc_id="BETA-DIA-P100-1")
        for i in range(1, 9)
    ] + [
        SafetyStepRecord(id=i + 8, step_no=i, text=f"Routine preventive task {i}", doc_id="BETA-PM-HP200-B")
        for i in range(1, 4)
    ]

    class Repository:
        def required_for_documents(self, tenant_id, doc_ids):
            assert tenant_id == "tenant-beta"
            assert "BETA-DIA-P100-1" in doc_ids
            assert "BETA-PM-HP200-B" in doc_ids
            return steps

    match = EquipmentMatch(
        "BETA-P-100", ("BETA-DIA-P100-1", "BETA-PM-HP200-B"), "Rev 1", "current", (1, 2)
    )
    plan = DiagnosticSafetyPlanner().run(
        DiagnosticSafetyPlannerInput(
            match,
            None,
            "tenant-beta",
            evidence,
            "The BETA-HP-200 hydraulic power unit has unstable pressure and the accumulator pressure is not holding.",
        ),
        Repository(),
    )

    assert len(plan.safety_steps) == 8
    assert {step.doc_id for step in plan.safety_steps} == {"BETA-DIA-P100-1"}
    assert [step.step_no for step in plan.safety_steps] == list(range(1, 9))


def test_work_order_generator_contract():
    chain = FakeLLMProvider(script=['{"title": "Test WO", "summary": "Sum", "steps": ["Inspect vibration source"], "parts": []}'])
    generator = WorkOrderGenerator(chain)
    match = EquipmentMatch("EQ-100", ("DOC-100",), "Rev B", "current", (1,))
    rev_res = RevisionResolution("Rev B", False, "current")

    res = generator.generate(WorkOrderGeneratorInput("vibration", match, rev_res, (), ()))
    assert isinstance(res.work_order, dict)
    assert res.work_order["title"] == "Test WO"
    assert res.degraded is False


def test_work_order_allows_total_usage_above_output_token_limit():
    chain = FakeLLMProvider(
        script=[
            CompletionResult(
                content='{"title":"Test WO","summary":"Sum","steps":["Inspect"],"parts":[]}',
                tool_calls=(),
                usage=TokenUsage(prompt_tokens=3000, completion_tokens=30),
                provider="groq",
                model="test-model",
            )
        ]
    )
    generator = WorkOrderGenerator(chain)
    match = EquipmentMatch("EQ-100", ("DOC-100",), "Rev B", "current", (1,))
    rev_res = RevisionResolution("Rev B", False, "current")

    result = generator.generate(
        WorkOrderGeneratorInput("vibration", match, rev_res, (), ())
    )

    assert result.work_order["title"] == "Test WO"
