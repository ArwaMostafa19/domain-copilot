from __future__ import annotations

import json
import logging
import uuid
from typing import Annotated

import psycopg
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse

from src.api import schemas
from src.api.deps import get_current_user
from src.application.agents import EquipmentNotFoundError, WorkflowInputError
from src.application.orchestrator import (
    GateNotSatisfiedError,
    WorkflowOrchestrator,
    WorkflowStartInput,
)
from src.domain.workflow import Role, WorkflowError
from src.infrastructure.chunk_search import PostgresChunkSearch
from src.infrastructure.providers.factory import build_chain, build_embedding_stack
from src.infrastructure.workflow_repository import (
    PgAuditLog,
    PgRunRepository,
    PgSafetyPrerequisiteRepository,
    PgWorkOrderRepository,
)

router = APIRouter()
logger = logging.getLogger(__name__)


def _get_orchestrator(request: Request) -> WorkflowOrchestrator:
    settings = request.app.state.settings
    from src.infrastructure.embedding_registry import PostgresEmbeddingIndexRegistry
    provider, guard = build_embedding_stack(settings, PostgresEmbeddingIndexRegistry())
    from src.application.embedding import GuardedEmbedder
    guard.ensure(settings.embedding_spec())
    embedder = GuardedEmbedder(provider, guard, settings.embedding_spec())
    chain = build_chain(settings)

    return WorkflowOrchestrator(
        run_repo=PgRunRepository(),
        work_order_repo=PgWorkOrderRepository(),
        audit_log=PgAuditLog(),
        safety_repo=PgSafetyPrerequisiteRepository(),
        embedder=embedder,
        search=PostgresChunkSearch(),
        chain=chain,
        settings=settings,
        max_model_calls=settings.run_max_model_calls,
        token_budget=settings.run_token_budget,
        timeout_seconds=settings.run_timeout_seconds,
        step_timeout_seconds=settings.run_step_timeout_seconds,
    )


def _owned_run(tenant_id: str, run_id: str, user: dict[str, object]):
    """Return tenant-wide runs to supervisors and only owned runs to technicians."""
    run = PgRunRepository().get(tenant_id, run_id)
    if run is None or (
        str(user["role"]) != "supervisor" and run.user_id != int(user["user_id"])
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="run not found")
    return run


@router.post("/runs")
def create_run(
    body: schemas.RunStartRequest,
    request: Request,
    user: Annotated[dict[str, object], Depends(get_current_user)],
):
    orch = _get_orchestrator(request)
    cid = getattr(request.state, "correlation_id", uuid.uuid4().hex)

    def event_stream():
        current_run_id = None
        gen = orch.start_run(
            WorkflowStartInput(
                symptoms=body.symptoms,
                installed_revision=body.installed_revision,
                user_id=int(user["user_id"]),
                tenant_id=str(user["tenant_id"]),
            ),
            correlation_id=cid,
        )
        try:
            while True:
                item = next(gen)
                if item.get("run_id"):
                    current_run_id = str(item["run_id"])
                yield f"data: {json.dumps(item)}\n\n"
        except StopIteration as stop:
            result = stop.value
            safety_steps = orch.safety_repo.required_by_ids(
                str(user["tenant_id"]), result.required_safety_step_ids
            )
            yield f"data: {json.dumps({'event': 'done', 'run_id': result.run_id, 'required_safety_step_ids': result.required_safety_step_ids, 'required_safety_steps': [{'id': step.id, 'step_no': step.step_no, 'text': step.text, 'doc_id': step.doc_id} for step in safety_steps]})}\n\n"
        except Exception as exc:  # noqa: BLE001
            try:
                if current_run_id:
                    run_repo = PgRunRepository()
                    run = run_repo.get(str(user["tenant_id"]), current_run_id)
                    if run and run.status == "running":
                        run_repo.set_status(str(user["tenant_id"]), run.id, "failed", finished=True)
            except psycopg.Error as persistence_error:
                logger.error("could not persist failed workflow (%s)", type(persistence_error).__name__)
            logger.error("workflow start failed (%s)", type(exc).__name__, extra={"correlation_id": cid})
            detail = (
                str(exc)
                if isinstance(exc, (EquipmentNotFoundError, WorkflowInputError))
                else "workflow failed"
            )
            yield f"data: {json.dumps({'event': 'error', 'detail': detail})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/runs/{run_id}/acknowledge")
def acknowledge_run(
    run_id: str,
    body: schemas.AcknowledgeRequest,
    request: Request,
    user: Annotated[dict[str, object], Depends(get_current_user)],
):
    orch = _get_orchestrator(request)
    cid = getattr(request.state, "correlation_id", uuid.uuid4().hex)
    tenant_id = str(user["tenant_id"])
    user_id = int(user["user_id"])

    _owned_run(tenant_id, run_id, user)

    try:
        orch.acknowledge(run_id, body.step_ids, user_id, tenant_id, correlation_id=cid)
    except WorkflowError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    def event_stream():
        gen = orch.generate(run_id, user_id, tenant_id, acknowledged_step_ids=body.step_ids, correlation_id=cid)
        try:
            while True:
                item = next(gen)
                yield f"data: {json.dumps(item)}\n\n"
        except GateNotSatisfiedError:
            yield f"data: {json.dumps({'event': 'error', 'detail': 'safety acknowledgement required'})}\n\n"
        except StopIteration as stop:
            wo = stop.value
            yield f"data: {json.dumps({'event': 'done', 'work_order': wo})}\n\n"
        except Exception as exc:
            logger.exception(
                "workflow generation failed",
                extra={"correlation_id": cid, "run_id": run_id},
            )
            yield f"data: {json.dumps({'event': 'error', 'detail': f'Work order generation failed ({type(exc).__name__}). Reference: {cid}'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/runs/{run_id}/approval")
def approve_run(
    run_id: str,
    body: schemas.ApprovalRequest,
    request: Request,
    user: Annotated[dict[str, object], Depends(get_current_user)],
):
    orch = _get_orchestrator(request)
    cid = getattr(request.state, "correlation_id", uuid.uuid4().hex)
    tenant_id = str(user["tenant_id"])
    user_id = int(user["user_id"])
    role_str = str(user["role"])

    if role_str != "supervisor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden: technician cannot approve")

    # Supervisors may review all tenant runs; technicians see only their own.
    run = _owned_run(tenant_id, run_id, user)

    if run.status in ("running", "awaiting_acknowledgement"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="approval before acknowledgement is not permitted",
        )

    try:
        res = orch.approval(
            run_id=run_id,
            decision=body.decision,
            role=Role.SUPERVISOR,
            user_id=user_id,
            tenant_id=tenant_id,
            comment=body.comment or "",
            edited_content=body.edited_content,
            correlation_id=cid,
        )
        return res
    except WorkflowError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/runs/{run_id}/cancel")
def cancel_run(
    run_id: str,
    user: Annotated[dict[str, object], Depends(get_current_user)],
):
    tenant_id = str(user["tenant_id"])
    run_repo = PgRunRepository()
    run = _owned_run(tenant_id, run_id, user)
    if run.status in ("approved", "rejected", "cancelled", "completed", "failed"):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="run cannot be cancelled")

    run_repo.set_status(tenant_id, run_id, "cancelled", finished=True)
    return {"id": run_id, "status": "cancelled"}


@router.get("/runs")
def list_runs(
    user: Annotated[dict[str, object], Depends(get_current_user)],
    status: str | None = Query(None),
):
    tenant_id = str(user["tenant_id"])
    user_id = int(user["user_id"])
    role_str = str(user["role"])
    run_repo = PgRunRepository()

    if role_str == "supervisor":
        runs = run_repo.list_for_tenant(tenant_id, status=status)
    else:
        runs = run_repo.list_for_user(tenant_id, user_id)
        if status:
            runs = [r for r in runs if r.status == status]

    return [
        {
            "id": r.id,
            "tenant_id": r.tenant_id,
            "user_id": r.user_id,
            "question": r.question,
            "status": r.status,
            "total_tokens": r.total_tokens,
            "estimated_tokens": r.estimated_tokens,
        }
        for r in runs
    ]


@router.get("/runs/{run_id}")
def get_run(
    run_id: str,
    user: Annotated[dict[str, object], Depends(get_current_user)],
):
    tenant_id = str(user["tenant_id"])
    run_repo = PgRunRepository()
    wo_repo = PgWorkOrderRepository()

    run = _owned_run(tenant_id, run_id, user)

    steps = run_repo.steps(tenant_id, run_id)
    latest_wo = wo_repo.latest(tenant_id, run_id)

    return {
        "id": run.id,
        "tenant_id": run.tenant_id,
        "user_id": run.user_id,
        "question": run.question,
        "status": run.status,
        "total_tokens": run.total_tokens,
        "estimated_tokens": run.estimated_tokens,
        "steps": [
            {
                "ordinal": s.ordinal,
                "agent": s.agent,
                "tools_used": list(s.tools_used),
                "evidence_ids": list(s.evidence_ids),
                "prompt_tokens": s.prompt_tokens,
                "completion_tokens": s.completion_tokens,
                "estimated": s.estimated,
                "duration_ms": s.duration_ms,
                "outcome": s.outcome,
                "summary": s.summary,
            }
            for s in steps
        ],
        "work_order": {
            "id": latest_wo.id,
            "version": latest_wo.version,
            "status": latest_wo.status,
            "content": latest_wo.content,
        }
        if latest_wo
        else None,
    }
