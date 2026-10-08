"""Workflow Orchestrator: 4-phase resumable state machine backed by PostgreSQL.

Phases:
1. start_run: SymptomMatcher & DiagnosticSafetyPlanner -> awaiting_acknowledgement.
2. acknowledge: Safety step checklist -> audit log -> gate verification.
3. generate: WorkOrderGenerator -> SSE streaming -> pending_approval.
4. approval: Supervisor review -> approve/reject/edit -> completed/rejected state.
"""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Generator
from dataclasses import dataclass

from src.application.agents import (
    AgentToolAccess,
    DiagnosticSafetyPlanner,
    DiagnosticSafetyPlannerInput,
    SymptomMatcher,
    SymptomMatcherInput,
    WorkOrderGenerator,
    WorkOrderGeneratorInput,
)
from src.application.ports import (
    AuditLog,
    Embedder,
    LLMProvider,
    RunRepository,
    RunStepRecord,
    SafetyPrerequisiteRepository,
    WorkOrderRepository,
)
from src.application.retrieval import ChunkSearch, RetrievalSettings
from src.application.rules import check_safety_gate, next_state
from src.application.tools import AGENT_TOOL_ALLOWLISTS
from src.domain.workflow import Role, RunStatus, WorkflowError

logger = logging.getLogger(__name__)


class GateNotSatisfiedError(WorkflowError):
    """The safety gate has missing un-acknowledged steps."""


class WorkflowLimitError(WorkflowError):
    """A workflow exceeded its configured call, token, or time budget."""


class RunCancelledError(WorkflowError):
    """The run was cancelled before the current phase could continue."""


@dataclass(frozen=True)
class WorkflowStartInput:
    symptoms: str
    installed_revision: str | None
    user_id: int
    tenant_id: str


@dataclass(frozen=True)
class WorkflowStartOutput:
    run_id: str
    required_safety_step_ids: tuple[int, ...]


class WorkflowOrchestrator(AgentToolAccess):
    """Coordinates the typed agents and owns only safety acknowledgement tools."""

    role = Role.TECHNICIAN
    allowed_tools = AGENT_TOOL_ALLOWLISTS["WorkflowOrchestrator"]
    input_schema = WorkflowStartInput
    output_schema = WorkflowStartOutput
    stop_condition = "Stop after the run is awaiting acknowledgement or a phase raises a domain error."
    def __init__(
        self,
        run_repo: RunRepository,
        work_order_repo: WorkOrderRepository,
        audit_log: AuditLog,
        safety_repo: SafetyPrerequisiteRepository,
        embedder: Embedder,
        search: ChunkSearch,
        chain: LLMProvider,
        settings: RetrievalSettings,
        max_model_calls: int = 6,
        token_budget: int = 20000,
        timeout_seconds: float = 120.0,
        step_timeout_seconds: float = 45.0,
    ):
        self.run_repo = run_repo
        self.work_order_repo = work_order_repo
        self.audit_log = audit_log
        self.safety_repo = safety_repo
        self.matcher = SymptomMatcher(embedder, search, chain, settings)
        self.planner = DiagnosticSafetyPlanner()
        self.generator = WorkOrderGenerator(chain)
        self.max_model_calls = max_model_calls
        self.token_budget = token_budget
        self.timeout_seconds = timeout_seconds
        self.step_timeout_seconds = step_timeout_seconds

    def _check_run(self, tenant_id: str, run_id: str, started_at: float) -> None:
        run = self.run_repo.get(tenant_id, run_id)
        if run is None:
            raise WorkflowError("run not found")
        if run.status == "cancelled":
            raise RunCancelledError("run is cancelled")
        if time.monotonic() - started_at > self.timeout_seconds:
            self.run_repo.set_status(tenant_id, run_id, "failed", finished=True)
            raise WorkflowLimitError("workflow time budget exceeded")
        steps = self.run_repo.steps(tenant_id, run_id)
        model_steps = sum(step.agent == "WorkOrderGenerator" for step in steps)
        if model_steps >= self.max_model_calls:
            self.run_repo.set_status(tenant_id, run_id, "failed", finished=True)
            raise WorkflowLimitError("workflow model-call budget exceeded")
        total_tokens = sum(s.prompt_tokens + s.completion_tokens for s in steps)
        if total_tokens >= self.token_budget:
            self.run_repo.set_status(tenant_id, run_id, "failed", finished=True)
            raise WorkflowLimitError("workflow token budget exceeded")

    def start_run(
        self,
        request: WorkflowStartInput,
        correlation_id: str | None = None,
    ) -> Generator[dict[str, object], None, WorkflowStartOutput]:
        """Phase 1: start run, match symptoms, resolve revision & safety steps."""
        symptoms = request.symptoms
        installed_revision = request.installed_revision
        user_id = request.user_id
        tenant_id = request.tenant_id
        cid = correlation_id or "orchestrator-start"
        started_at = time.monotonic()
        logger.info(json.dumps({"event": "start_run", "correlation_id": cid, "tenant_id": tenant_id, "user_id": user_id}))

        run_id = self.run_repo.create(tenant_id, user_id, symptoms)
        yield {"event": "status", "run_id": run_id, "status": "running"}

        # Step 1: Symptom Matcher
        self._check_run(tenant_id, run_id, started_at)
        step_started = time.monotonic()
        match_res = self.matcher.run(
            SymptomMatcherInput(symptoms, tenant_id), correlation_id=cid
        )
        if time.monotonic() - step_started > self.step_timeout_seconds:
            self.run_repo.set_status(tenant_id, run_id, "failed", finished=True)
            raise WorkflowLimitError("symptom matching step timed out")
        step1 = RunStepRecord(
            ordinal=1,
            agent="SymptomMatcher",
            tools_used=("search_manuals",),
            evidence_ids=tuple(e.chunk_id for e in match_res.evidence),
            prompt_tokens=match_res.usage.prompt_tokens,
            completion_tokens=match_res.usage.completion_tokens,
            estimated=match_res.usage.estimated,
            duration_ms=int((time.monotonic() - step_started) * 1000),
            outcome="matched",
            summary=(
                f"Matched equipment {match_res.match.equipment_id} "
                f"revision {match_res.match.revision}"
            ),
        )
        self.run_repo.add_step(tenant_id, run_id, step1)
        yield {
            "event": "step",
            "run_id": run_id,
            "ordinal": 1,
            "agent": "SymptomMatcher",
            "summary": step1.summary,
        }

        # Step 2: Diagnostic Safety Planner
        self._check_run(tenant_id, run_id, started_at)
        step_started = time.monotonic()
        plan = self.planner.run(
            DiagnosticSafetyPlannerInput(
                match_res.match, installed_revision, tenant_id, match_res.evidence
            ),
            self.safety_repo,
        )
        if time.monotonic() - step_started > self.step_timeout_seconds:
            self.run_repo.set_status(tenant_id, run_id, "failed", finished=True)
            raise WorkflowLimitError("safety planning step timed out")
        step2 = RunStepRecord(
            ordinal=2,
            agent="DiagnosticSafetyPlanner",
            tools_used=("get_safety_prerequisites",),
            prompt_tokens=0,
            completion_tokens=0,
            estimated=False,
            duration_ms=int((time.monotonic() - step_started) * 1000),
            outcome="planned",
            summary=f"Selected revision {plan.revision.revision} with {len(plan.safety_steps)} safety prerequisites.",
        )
        self.run_repo.add_step(tenant_id, run_id, step2)
        yield {
            "event": "step",
            "run_id": run_id,
            "ordinal": 2,
            "agent": "DiagnosticSafetyPlanner",
            "summary": step2.summary,
        }

        # Update run status to awaiting_acknowledgement
        self.run_repo.set_status(tenant_id, run_id, "awaiting_acknowledgement")
        yield {"event": "status", "run_id": run_id, "status": "awaiting_acknowledgement"}

        self.audit_log.record(
            tenant_id,
            user_id,
            "start_run",
            "run",
            run_id,
            {"equipment_id": match_res.match.equipment_id, "correlation_id": cid},
        )

        req_ids = tuple(step.id for step in plan.safety_steps)
        return WorkflowStartOutput(run_id, req_ids)

    def acknowledge(
        self,
        run_id: str,
        acknowledged_step_ids: list[int],
        user_id: int,
        tenant_id: str,
        correlation_id: str | None = None,
    ) -> bool:
        """Phase 2: record safety step acknowledgements."""
        cid = correlation_id or "orchestrator-ack"
        logger.info(json.dumps({"event": "acknowledge", "correlation_id": cid, "run_id": run_id}))

        run = self.run_repo.get(tenant_id, run_id)
        if not run:
            raise WorkflowError(f"run {run_id} not found")

        # Record audit entry
        self.audit_log.record(
            tenant_id,
            user_id,
            "acknowledge_safety",
            "run",
            run_id,
            {"acknowledged_step_ids": acknowledged_step_ids, "correlation_id": cid},
        )
        return True

    def generate(
        self,
        run_id: str,
        user_id: int,
        tenant_id: str,
        acknowledged_step_ids: list[int] | None = None,
        correlation_id: str | None = None,
    ) -> Generator[dict[str, object], None, dict[str, object]]:
        """Phase 3: Verify safety gate & generate draft work order."""
        cid = correlation_id or "orchestrator-gen"
        started_at = time.monotonic()
        logger.info(json.dumps({"event": "generate", "correlation_id": cid, "run_id": run_id}))

        run = self.run_repo.get(tenant_id, run_id)
        if not run:
            raise WorkflowError(f"run {run_id} not found")

        self._check_run(tenant_id, run_id, started_at)

        # Resolve the same matched procedure used for both the gate and the draft.
        symptoms = run.question
        match_res = self.matcher.run(
            SymptomMatcherInput(symptoms, tenant_id), correlation_id=cid
        )
        plan = self.planner.run(
            DiagnosticSafetyPlannerInput(
                match_res.match, None, tenant_id, match_res.evidence
            ),
            self.safety_repo,
        )
        evidence = match_res.evidence
        required_ids = [step.id for step in plan.safety_steps]
        gate = check_safety_gate(required_ids, acknowledged_step_ids or [])
        if not gate.ok:
            raise GateNotSatisfiedError(f"missing safety step acknowledgements: {gate.missing}")
        self._check_run(tenant_id, run_id, started_at)
        step_started = time.monotonic()
        try:
            gen_res = self.generator.generate(
                WorkOrderGeneratorInput(
                    symptoms,
                    match_res.match,
                    plan.revision,
                    tuple(evidence),
                    plan.safety_steps,
                ),
                correlation_id=cid,
                max_model_calls=self.max_model_calls,
                step_timeout_seconds=self.step_timeout_seconds,
            )
        except Exception:
            self.run_repo.set_status(tenant_id, run_id, "failed", finished=True)
            raise
        if time.monotonic() - step_started > self.step_timeout_seconds:
            self.run_repo.set_status(tenant_id, run_id, "failed", finished=True)
            raise WorkflowLimitError("work-order generation step timed out")

        self._check_run(tenant_id, run_id, started_at)
        wo_content = dict(gen_res.work_order)
        self.work_order_repo.create_draft(tenant_id, run_id, wo_content)

        step3 = RunStepRecord(
            ordinal=3,
            agent="WorkOrderGenerator",
            tools_used=("create_work_order_draft",),
            prompt_tokens=gen_res.usage.prompt_tokens,
            completion_tokens=gen_res.usage.completion_tokens,
            estimated=gen_res.usage.estimated,
            duration_ms=int((time.monotonic() - step_started) * 1000),
            outcome="degraded" if gen_res.degraded else "generated",
            summary=f"Generated draft work order v1 ({'degraded RAG' if gen_res.degraded else 'JSON'})",
        )
        self.run_repo.add_step(tenant_id, run_id, step3)
        all_steps = self.run_repo.steps(tenant_id, run_id)
        total_tokens = sum(s.prompt_tokens + s.completion_tokens for s in all_steps)
        estimated_tokens = any(s.estimated for s in all_steps)
        if total_tokens > self.token_budget:
            self.run_repo.set_status(tenant_id, run_id, "failed", total_tokens=total_tokens, estimated_tokens=estimated_tokens, finished=True)
            raise WorkflowLimitError("workflow token budget exceeded")
        self.run_repo.set_status(tenant_id, run_id, "pending_approval", total_tokens=total_tokens, estimated_tokens=estimated_tokens)

        yield {"event": "work_order", "run_id": run_id, "content": wo_content}
        yield {"event": "status", "run_id": run_id, "status": "pending_approval"}

        self.audit_log.record(
            tenant_id,
            user_id,
            "generate_work_order",
            "run",
            run_id,
            {"degraded": gen_res.degraded, "correlation_id": cid},
        )
        return wo_content

    def approval(
        self,
        run_id: str,
        decision: str,
        role: Role,
        user_id: int,
        tenant_id: str,
        comment: str = "",
        edited_content: dict[str, object] | None = None,
        correlation_id: str | None = None,
    ) -> dict[str, object]:
        """Phase 4: Supervisor approval, rejection, or edit."""
        cid = correlation_id or "orchestrator-approval"
        logger.info(json.dumps({"event": "approval", "correlation_id": cid, "run_id": run_id, "decision": decision}))

        if role != Role.SUPERVISOR:
            raise WorkflowError("role technician may not 'approve'")

        run = self.run_repo.get(tenant_id, run_id)
        if not run:
            raise WorkflowError(f"run {run_id} not found")

        current_status = RunStatus(run.status)
        target_status = next_state(current_status, decision, role)

        latest_wo = self.work_order_repo.latest(tenant_id, run_id)
        if not latest_wo:
            raise WorkflowError("no work order found for run")

        prior_content = dict(latest_wo.content)
        if edited_content:
            self.work_order_repo.create_draft(tenant_id, run_id, edited_content)
            latest_wo = self.work_order_repo.latest(tenant_id, run_id)

        wo_status = "approved" if decision == "approve" else ("rejected" if decision == "reject" else "draft")
        if latest_wo:
            self.work_order_repo.set_status(tenant_id, latest_wo.id, wo_status)

        self.run_repo.set_status(tenant_id, run_id, target_status.value, finished=True)

        self.audit_log.record(
            tenant_id,
            user_id,
            f"approval_{decision}",
            "run",
            run_id,
            {
                "decision": decision,
                "comment": comment,
                "correlation_id": cid,
                "before": prior_content,
                "after": dict(latest_wo.content) if latest_wo else None,
            },
        )
        return {"run_id": run_id, "status": target_status.value, "decision": decision}
