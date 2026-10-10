"""Agent layer: SymptomMatcher, DiagnosticSafetyPlanner, WorkOrderGenerator.

Strict JSON response formatting, repair-once on malformed JSON, and fallback
degradation to plain RAG when JSON repair fails. Tracks degraded execution rate.
"""

from __future__ import annotations

import json
import logging
import re
import time
from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar, TypedDict

from src.application.ports import Embedder, LLMProvider, SafetyPrerequisiteRepository
from src.application.retrieval import ChunkSearch, RetrievalSettings, retrieve
from src.application.rules import parts_from_evidence, resolve_revision
from src.application.tools import AGENT_TOOL_ALLOWLISTS, ToolRegistry
from src.domain.llm import CompletionRequest, Message, TokenUsage
from src.domain.rag import Evidence
from src.domain.workflow import (
    EquipmentMatch,
    RevisionResolution,
    Role,
    SafetyStepRecord,
)

logger = logging.getLogger(__name__)

# Pattern to extract JSON codeblock if LLM wraps output in ```json ... ```
JSON_BLOCK_PATTERN = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)
EQUIPMENT_CODE_PATTERN = re.compile(
    r"\b(?:ALPHA|BETA)-[A-Z]{2,5}-\d+[A-Z]?\b", re.IGNORECASE
)


class EquipmentNotFoundError(ValueError):
    """The tenant has no retrieved manual for the explicitly named equipment."""


class WorkflowInputError(ValueError):
    """The supplied description cannot be matched to maintenance evidence."""


@dataclass
class AgentMetrics:
    total_calls: int = 0
    repaired_calls: int = 0
    degraded_calls: int = 0

    @property
    def degradation_rate(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return self.degraded_calls / self.total_calls


GLOBAL_METRICS = AgentMetrics()


def _parse_json_response(raw_text: str) -> dict[str, object] | None:
    text = raw_text.strip()
    match = JSON_BLOCK_PATTERN.search(text)
    if match:
        text = match.group(1).strip()
    elif text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 2 and lines[-1].startswith("```"):
            text = "\n".join(lines[1:-1]).strip()

    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, TypeError, ValueError):
        pass

    # Try finding first { and last }
    first_brace = raw_text.find("{")
    last_brace = raw_text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        snippet = raw_text[first_brace : last_brace + 1]
        try:
            data = json.loads(snippet)
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
    return None


def _valid_work_order_json(data: dict[str, object] | None) -> bool:
    if data is None:
        return False
    if not isinstance(data.get("title"), str) or not isinstance(data.get("summary"), str):
        return False
    if len(data["title"]) > 200 or len(data["summary"]) > 2000:
        return False
    steps = data.get("steps")
    parts = data.get("parts", [])
    return (
        isinstance(steps, list)
        and 1 <= len(steps) <= 30
        and all(isinstance(step, str) and 0 < len(step) <= 1000 for step in steps)
        and isinstance(parts, list)
        and len(parts) <= 50
        and all(isinstance(part, str) and len(part) <= 200 for part in parts)
    )


@dataclass(frozen=True)
class SymptomMatcherResult:
    match: EquipmentMatch
    evidence: tuple[Evidence, ...]
    usage: TokenUsage


@dataclass(frozen=True)
class SymptomMatcherInput:
    symptoms: str
    tenant_id: str


@dataclass(frozen=True)
class DiagnosticSafetyPlannerInput:
    match: EquipmentMatch
    installed_revision: str | None
    tenant_id: str
    evidence: tuple[Evidence, ...]
    symptoms: str = ""


@dataclass(frozen=True)
class DiagnosticSafetyPlannerResult:
    revision: RevisionResolution
    safety_steps: tuple[SafetyStepRecord, ...]


@dataclass(frozen=True)
class WorkOrderGeneratorInput:
    symptoms: str
    match: EquipmentMatch
    revision: RevisionResolution
    evidence: tuple[Evidence, ...]
    safety_steps: tuple[SafetyStepRecord, ...]


class WorkOrderData(TypedDict):
    title: str
    summary: str
    steps: list[str]
    parts: list[str]
    safety_prerequisites: list[dict[str, object]]
    degraded: bool


class AgentToolAccess:
    """Shared enforcement point for each agent's independent tool allow-list."""

    role: ClassVar[Role] = Role.TECHNICIAN
    allowed_tools: ClassVar[frozenset[str]]
    stop_condition: ClassVar[str]
    input_schema: ClassVar[type]
    output_schema: ClassVar[type]

    def invoke_tool(
        self,
        registry: ToolRegistry,
        name: str,
        args: dict[str, object],
    ) -> object:
        return registry.invoke_for_agent(
            type(self).__name__, name, args, self.role
        )


class SymptomMatcher(AgentToolAccess):
    """Matches symptom text to equipment manuals via search & LLM extraction."""

    allowed_tools = AGENT_TOOL_ALLOWLISTS["SymptomMatcher"]
    input_schema = SymptomMatcherInput
    output_schema = SymptomMatcherResult
    stop_condition = "Stop when evidence identifies a match, or return no-evidence failure."

    def __init__(self, embedder: Embedder, search: ChunkSearch, chain: LLMProvider, settings: RetrievalSettings):
        self.embedder = embedder
        self.search = search
        self.chain = chain
        self.settings = settings

    def run(self, request: SymptomMatcherInput, correlation_id: str | None = None) -> SymptomMatcherResult:
        if not request.symptoms.strip():
            raise WorkflowInputError("Describe the equipment and maintenance symptoms to start a workflow.")
        evidence = retrieve(request.symptoms, request.tenant_id, self.embedder, self.search, self.settings)
        if not evidence:
            raise WorkflowInputError("No maintenance evidence matched this description. Name the equipment or describe its symptoms.")

        requested_equipment = list(dict.fromkeys(
            code.upper() for code in EQUIPMENT_CODE_PATTERN.findall(request.symptoms)
        ))
        query_terms = {
            term for term in re.findall(r"[a-z0-9]+", request.symptoms.lower())
            if len(term) >= 4
        }
        stop_words = {
            "about", "after", "before", "could", "does", "from", "have", "hello",
            "here", "into", "just", "like", "need", "please", "show", "start",
            "that", "them", "there", "these", "they", "this", "those", "what",
            "when", "where", "which", "while", "with", "would", "workflow",
        }
        query_terms -= stop_words
        matched_terms = {
            term
            for item in evidence
            for term in re.findall(
                r"[a-z0-9]+",
                " ".join((item.equipment or "", item.title, item.section, item.text)).lower(),
            )
        }
        has_domain_overlap = bool(query_terms & matched_terms)
        if not requested_equipment and (
            max(item.dense_score for item in evidence) < self.settings.retrieval_min_similarity
            or not has_domain_overlap
        ):
            raise WorkflowInputError(
                "I could not find relevant maintenance evidence for this description. "
                "Name the equipment or describe its symptoms."
            )
        available_equipment = {
            item.equipment.upper()
            for item in evidence
            if item.equipment
        }
        missing_equipment = [
            code for code in requested_equipment if code not in available_equipment
        ]
        if missing_equipment:
            raise EquipmentNotFoundError(
                f"No maintenance information for {missing_equipment[0]} is available "
                "in this tenant's documents."
            )

        top = evidence[0]
        # Infer equipment and document details from evidence
        match = EquipmentMatch(
            equipment_id=top.equipment or top.title or "Unidentified equipment",
            doc_ids=tuple(dict.fromkeys(item.doc_id for item in evidence if item.doc_id)),
            revision=top.revision or "Rev A",
            revision_status="superseded" if "superseded" in (top.doc_status or "").lower() else "current",
            evidence_ids=tuple(item.chunk_id for item in evidence),
        )
        return SymptomMatcherResult(match=match, evidence=tuple(evidence), usage=TokenUsage())


class DiagnosticSafetyPlanner(AgentToolAccess):
    """Determines active revision and fetches safety prerequisites."""

    allowed_tools = AGENT_TOOL_ALLOWLISTS["DiagnosticSafetyPlanner"]
    input_schema = DiagnosticSafetyPlannerInput
    output_schema = DiagnosticSafetyPlannerResult
    stop_condition = "Stop after resolving one revision and loading prerequisites for matched documents."

    def run(
        self,
        request: DiagnosticSafetyPlannerInput,
        safety_repo: SafetyPrerequisiteRepository,
    ) -> DiagnosticSafetyPlannerResult:
        res = resolve_revision(request.match, request.installed_revision)
        doc_ids = list(dict.fromkeys(item.doc_id for item in request.evidence if item.doc_id))
        for doc_id in request.match.doc_ids:
            if doc_id not in doc_ids:
                doc_ids.append(doc_id)
        safety_steps = safety_repo.required_for_documents(request.tenant_id, doc_ids)
        if len(safety_steps) > 1 and request.symptoms:
            safety_steps = _most_relevant_safety_steps(
                request.symptoms, request.evidence, safety_steps
            )
        return DiagnosticSafetyPlannerResult(res, tuple(safety_steps))


def _most_relevant_safety_steps(
    symptoms: str,
    evidence: Sequence[Evidence],
    safety_steps: Sequence[SafetyStepRecord],
) -> list[SafetyStepRecord]:
    """Avoid combining checklists from unrelated procedures in one run.

    Several retrieved documents may describe the same equipment but different
    tasks (for example, diagnostics and preventive maintenance). Select the
    safety-bearing document(s) whose evidence and prerequisite wording best
    match the reported symptoms. Ties remain included for multi-document tasks.
    """
    ignored = {
        "about", "after", "before", "could", "does", "from", "have", "here",
        "into", "just", "like", "need", "please", "show", "start", "that",
        "them", "there", "these", "they", "this", "those", "what", "when",
        "where", "which", "while", "with", "would", "workflow", "safety",
        "steps", "maintenance", "work", "order", "must", "acknowledged",
        "drafting", "the", "and", "for", "unit", "has",
    }
    terms = {
        token
        for token in re.findall(r"[a-z0-9]+", symptoms.lower())
        if len(token) >= 4 and token not in ignored
    }
    if not terms:
        return list(safety_steps)

    text_by_doc: dict[str, list[str]] = {}
    for item in evidence:
        text_by_doc.setdefault(item.doc_id, []).append(
            " ".join((item.equipment or "", item.title, item.section, item.text))
        )
    for step in safety_steps:
        text_by_doc.setdefault(step.doc_id, []).append(step.text)

    scores: dict[str, int] = {}
    docs_with_steps = {step.doc_id for step in safety_steps}
    for doc_id in docs_with_steps:
        tokens = {
            token
            for token in re.findall(r"[a-z0-9]+", " ".join(text_by_doc.get(doc_id, [])).lower())
        }
        scores[doc_id] = len(terms & tokens)
    best_score = max(scores.values(), default=0)
    if best_score == 0:
        return list(safety_steps)
    selected_docs = {doc_id for doc_id, score in scores.items() if score == best_score}
    return [step for step in safety_steps if step.doc_id in selected_docs]


@dataclass(frozen=True)
class WorkOrderGeneratorResult:
    work_order: WorkOrderData
    usage: TokenUsage
    degraded: bool


class WorkOrderGenerator(AgentToolAccess):
    """Generates structured work order. Enforces strict-JSON, repair-once, fallback to plain RAG."""

    allowed_tools = AGENT_TOOL_ALLOWLISTS["WorkOrderGenerator"]
    input_schema = WorkOrderGeneratorInput
    output_schema = WorkOrderGeneratorResult
    stop_condition = "Stop after valid JSON, one repair attempt, or deterministic fallback."

    def __init__(self, chain: LLMProvider):
        self.chain = chain

    def generate(
        self,
        request: WorkOrderGeneratorInput,
        correlation_id: str | None = None,
        max_model_calls: int = 3,
        retry_backoff_seconds: float = 0.05,
        step_timeout_seconds: float = 45.0,
    ) -> WorkOrderGeneratorResult:
        GLOBAL_METRICS.total_calls += 1
        symptoms = request.symptoms
        match = request.match
        revision_res = request.revision
        evidence = request.evidence
        safety_steps = request.safety_steps

        prompt = (
            f"Generate a maintenance work order in strict JSON format.\n"
            f"Symptoms: {symptoms}\n"
            f"Equipment ID: {match.equipment_id}\n"
            f"Revision: {revision_res.revision}\n"
            f"Evidence snippets:\n"
            + "\n".join(f"- [{e.chunk_id}] {e.text}" for e in evidence[:5])
            + "\nRespond strictly in valid JSON with fields: 'title', 'summary', 'steps', 'parts'."
        )

        req = CompletionRequest(
            messages=(
                Message(role="system", content="You are a maintenance assistant. Output valid JSON only."),
                Message(role="user", content=prompt),
            ),
            max_tokens=2048,
            correlation_id=correlation_id,
        )

        started_at = time.monotonic()
        call_count = [0]
        res = self._complete(req, correlation_id, max_model_calls, retry_backoff_seconds, call_count)
        usage = res.usage
        parsed = _parse_json_response(res.content)

        if _valid_work_order_json(parsed):
            if time.monotonic() - started_at > step_timeout_seconds:
                raise TimeoutError("work-order generation step timed out")
            final_wo = self._build_work_order(parsed, evidence, safety_steps)
            return WorkOrderGeneratorResult(work_order=final_wo, usage=usage, degraded=False)

        # Repair once
        GLOBAL_METRICS.repaired_calls += 1
        logger.warning("[%s] Malformed JSON from model; attempting repair-once", correlation_id or "agent")
        repair_req = CompletionRequest(
            messages=(
                Message(role="system", content="Fix the invalid JSON text and output ONLY valid JSON."),
                Message(role="user", content=f"Fix this invalid JSON:\n{res.content}"),
            ),
            max_tokens=2048,
            correlation_id=correlation_id,
        )
        repair_res = self._complete(
            repair_req, correlation_id, max_model_calls, retry_backoff_seconds, call_count
        )
        usage = TokenUsage(
            prompt_tokens=usage.prompt_tokens + repair_res.usage.prompt_tokens,
            completion_tokens=usage.completion_tokens + repair_res.usage.completion_tokens,
            estimated=usage.estimated or repair_res.usage.estimated,
        )
        parsed_repaired = _parse_json_response(repair_res.content)

        if _valid_work_order_json(parsed_repaired):
            if time.monotonic() - started_at > step_timeout_seconds:
                raise TimeoutError("work-order generation step timed out")
            final_wo = self._build_work_order(parsed_repaired, evidence, safety_steps)
            return WorkOrderGeneratorResult(work_order=final_wo, usage=usage, degraded=False)

        # Degrade to plain RAG
        GLOBAL_METRICS.degraded_calls += 1
        logger.error("[%s] JSON repair failed; degrading to plain RAG", correlation_id or "agent")
        degraded_wo = self._fallback_plain_rag(symptoms, match, revision_res, evidence, safety_steps)
        if time.monotonic() - started_at > step_timeout_seconds:
            raise TimeoutError("work-order generation step timed out")
        return WorkOrderGeneratorResult(work_order=degraded_wo, usage=usage, degraded=True)

    def _complete(self, request, correlation_id, max_calls, backoff_seconds, call_count):
        """Retry transient provider errors with bounded exponential backoff."""
        from src.domain.llm import ProviderError

        last_error = None
        for attempt in range(max_calls - call_count[0]):
            try:
                call_count[0] += 1
                result = self.chain.complete(request)
                return result
            except ProviderError as exc:
                last_error = exc
                if not exc.fallback_allowed or call_count[0] >= max_calls:
                    raise
                time.sleep(backoff_seconds * (2**attempt))
        raise last_error or RuntimeError("model call failed")

    def _build_work_order(
        self,
        parsed: dict[str, object],
        evidence: Sequence[Evidence],
        safety_steps: Sequence[SafetyStepRecord],
    ) -> dict[str, object]:
        raw_parts = parsed.get("parts", [])
        proposed = tuple(raw_parts) if isinstance(raw_parts, list) else ()
        kept_parts = list(parts_from_evidence(proposed, evidence))

        raw_steps = parsed.get("steps", [])
        steps = list(raw_steps) if isinstance(raw_steps, list) else ["Follow standard diagnostic protocol"]

        return {
            "title": str(parsed.get("title", "Work Order Plan")),
            "summary": str(parsed.get("summary", "Generated diagnostic work order plan.")),
            "steps": steps,
            "parts": kept_parts,
            "safety_prerequisites": [
                {"id": step.id, "step_no": step.step_no, "text": step.text}
                for step in safety_steps
            ],
            "degraded": False,
        }

    def _fallback_plain_rag(
        self,
        symptoms: str,
        match: EquipmentMatch,
        revision_res: RevisionResolution,
        evidence: Sequence[Evidence],
        safety_steps: Sequence[SafetyStepRecord],
    ) -> dict[str, object]:
        snippet_summary = " ".join(e.text for e in evidence[:2])[:200]
        return {
            "title": f"Degraded Work Order for {match.equipment_id}",
            "summary": f"Plain RAG Fallback: {snippet_summary}",
            "steps": [f"Inspect equipment {match.equipment_id} per revision {revision_res.revision}"],
            "parts": [],
            "safety_prerequisites": [
                {"id": step.id, "step_no": step.step_no, "text": step.text}
                for step in safety_steps
            ],
            "degraded": True,
        }
