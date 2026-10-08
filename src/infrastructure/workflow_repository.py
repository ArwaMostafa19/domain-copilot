"""PostgreSQL repositories for workflow entities (CP2).

All calls run inside the tenant set via ``tenant_connection``, so Row-Level
Security enforces isolation. Every parameter is passed as a query parameter;
never string-interpolate values into SQL.
"""

from __future__ import annotations

import json
from collections.abc import Sequence

from src.application.ports import (
    AuditLog,
    RunRecord,
    RunRepository,
    RunStepRecord,
    SafetyPrerequisiteRepository,
    UserRecord,
    UserRepository,
    WorkOrderRecord,
    WorkOrderRepository,
)
from src.domain.workflow import SafetyStepRecord
from src.infrastructure.database import tenant_connection


class PgUserRepository(UserRepository):
    def get_by_username(self, tenant_id: str, username: str) -> UserRecord | None:
        with tenant_connection(tenant_id) as conn:
            row = conn.execute(
                "SELECT id, tenant_id, username, role, active, password_hash FROM users WHERE username=%s",
                (username,),
            ).fetchone()
        if not row:
            return None
        return UserRecord(
            id=row[0],
            tenant_id=row[1],
            username=row[2],
            role=row[3],
            active=row[4],
            password_hash=row[5] or "",
        )

    def get(self, tenant_id: str, user_id: int) -> UserRecord | None:
        with tenant_connection(tenant_id) as conn:
            row = conn.execute(
                "SELECT id, tenant_id, username, role, active, password_hash FROM users WHERE id=%s",
                (user_id,),
            ).fetchone()
        if not row:
            return None
        return UserRecord(
            id=row[0],
            tenant_id=row[1],
            username=row[2],
            role=row[3],
            active=row[4],
            password_hash=row[5] or "",
        )


class PgRunRepository(RunRepository):
    def create(self, tenant_id: str, user_id: int, question: str) -> str:
        with tenant_connection(tenant_id) as conn:
            row = conn.execute(
                """
                INSERT INTO runs (tenant_id, user_id, question, status)
                VALUES (%s, %s, %s, 'running')
                RETURNING id
                """,
                (tenant_id, user_id, question),
            ).fetchone()
            return str(row[0])

    def get(self, tenant_id: str, run_id: str) -> RunRecord | None:
        with tenant_connection(tenant_id) as conn:
            row = conn.execute(
                """
                SELECT id, tenant_id, user_id, question, status, total_tokens, estimated_tokens
                FROM runs WHERE id=%s
                """,
                (run_id,),
            ).fetchone()
        if not row:
            return None
        return RunRecord(
            id=str(row[0]),
            tenant_id=row[1],
            user_id=row[2],
            question=row[3],
            status=row[4],
            total_tokens=row[5] or 0,
            estimated_tokens=row[6] or False,
        )

    def set_status(
        self,
        tenant_id: str,
        run_id: str,
        status: str,
        *,
        total_tokens: int | None = None,
        estimated_tokens: bool | None = None,
        finished: bool = False,
    ) -> None:
        with tenant_connection(tenant_id) as conn:
            if total_tokens is not None or estimated_tokens is not None or finished:
                conn.execute(
                    """
                    UPDATE runs
                    SET status=%s,
                        total_tokens=COALESCE(%s, total_tokens),
                        estimated_tokens=COALESCE(%s, estimated_tokens),
                        finished_at=CASE WHEN %s THEN now() ELSE finished_at END
                    WHERE id=%s
                    """,
                    (status, total_tokens, estimated_tokens, finished, run_id),
                )
            else:
                conn.execute("UPDATE runs SET status=%s WHERE id=%s", (status, run_id))

    def add_step(self, tenant_id: str, run_id: str, step: RunStepRecord) -> None:
        with tenant_connection(tenant_id) as conn:
            conn.execute(
                """
                INSERT INTO run_steps
                    (tenant_id, run_id, ordinal, agent, tools_used, evidence_ids,
                     prompt_tokens, completion_tokens, estimated, duration_ms,
                     outcome, summary)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    tenant_id,
                    run_id,
                    step.ordinal,
                    step.agent,
                    list(step.tools_used),
                    list(step.evidence_ids),
                    step.prompt_tokens,
                    step.completion_tokens,
                    step.estimated,
                    step.duration_ms,
                    step.outcome,
                    step.summary,
                ),
            )

    def steps(self, tenant_id: str, run_id: str) -> list[RunStepRecord]:
        with tenant_connection(tenant_id) as conn:
            rows = conn.execute(
                """
                SELECT ordinal, agent, tools_used, evidence_ids, prompt_tokens,
                       completion_tokens, estimated, duration_ms, outcome, summary
                FROM run_steps
                WHERE run_id=%s
                ORDER BY ordinal
                """,
                (run_id,),
            ).fetchall()
        out: list[RunStepRecord] = []
        for row in rows:
            out.append(
                RunStepRecord(
                    ordinal=row[0],
                    agent=row[1],
                    tools_used=tuple(row[2] or []),
                    evidence_ids=tuple(row[3] or []),
                    prompt_tokens=row[4] or 0,
                    completion_tokens=row[5] or 0,
                    estimated=row[6] or False,
                    duration_ms=row[7] or 0,
                    outcome=row[8] or "",
                    summary=row[9],
                )
            )
        return out

    def list_for_user(self, tenant_id: str, user_id: int) -> list[RunRecord]:
        with tenant_connection(tenant_id) as conn:
            rows = conn.execute(
                """
                SELECT id, tenant_id, user_id, question, status, total_tokens, estimated_tokens
                FROM runs WHERE user_id=%s ORDER BY created_at DESC
                """,
                (user_id,),
            ).fetchall()
        out: list[RunRecord] = []
        for row in rows:
            out.append(
                RunRecord(
                    id=str(row[0]),
                    tenant_id=row[1],
                    user_id=row[2],
                    question=row[3],
                    status=row[4],
                    total_tokens=row[5] or 0,
                    estimated_tokens=row[6] or False,
                )
            )
        return out


class PgWorkOrderRepository(WorkOrderRepository):
    def create_draft(
        self, tenant_id: str, run_id: str, content: dict[str, object]
    ) -> dict[str, object]:
        with tenant_connection(tenant_id) as conn:
            row = conn.execute(
                """
                SELECT COALESCE(MAX(version), 0) + 1 FROM work_orders WHERE run_id=%s
                """,
                (run_id,),
            ).fetchone()
            version = row[0] if row else 1
            conn.execute(
                """
                INSERT INTO work_orders (tenant_id, run_id, version, status, content)
                VALUES (%s, %s, %s, 'draft', %s)
                """,
                (tenant_id, run_id, version, json.dumps(content)),
            )
        return content

    def latest(self, tenant_id: str, run_id: str) -> WorkOrderRecord | None:
        with tenant_connection(tenant_id) as conn:
            row = conn.execute(
                """
                SELECT id, run_id, version, status, content
                FROM work_orders
                WHERE run_id=%s
                ORDER BY version DESC
                LIMIT 1
                """,
                (run_id,),
            ).fetchone()
        if not row:
            return None
        return WorkOrderRecord(
            id=str(row[0]),
            run_id=str(row[1]),
            version=row[2],
            status=row[3],
            content=row[4] if isinstance(row[4], dict) else {},
        )

    def set_status(self, tenant_id: str, work_order_id: str, status: str) -> None:
        with tenant_connection(tenant_id) as conn:
            conn.execute(
                "UPDATE work_orders SET status=%s WHERE id=%s",
                (status, work_order_id),
            )


class PgAuditLog(AuditLog):
    def record(
        self,
        tenant_id: str,
        actor_user_id: int | None,
        action: str,
        subject_type: str,
        subject_id: str | None,
        detail: dict[str, object] | None = None,
    ) -> None:
        with tenant_connection(tenant_id) as conn:
            conn.execute(
                """
                INSERT INTO audit_log (tenant_id, actor_user_id, action, subject_type, subject_id, detail)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    tenant_id,
                    actor_user_id,
                    action,
                    subject_type,
                    subject_id,
                    json.dumps(detail) if detail is not None else None,
                ),
            )


class PgSafetyPrerequisiteRepository(SafetyPrerequisiteRepository):
    def required_for_documents(
        self, tenant_id: str, doc_ids: Sequence[str]
    ) -> list[SafetyStepRecord]:
        if not doc_ids:
            return []
        # Get document IDs in the system (by doc_id text) for the tenant
        with tenant_connection(tenant_id) as conn:
            rows = conn.execute(
                """
                SELECT sp.id, sp.step_no, sp.step_text, d.doc_id
                FROM safety_prerequisites sp
                JOIN documents d ON d.id = sp.document_id
                WHERE d.doc_id = ANY(%s)
                ORDER BY sp.step_no
                """,
                (list(doc_ids),),
            ).fetchall()
        out: list[SafetyStepRecord] = []
        for row in rows:
            out.append(SafetyStepRecord(id=row[0], step_no=row[1], text=row[2], doc_id=row[3]))
        return out
