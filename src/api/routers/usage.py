from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from src.api.deps import get_current_user
from src.infrastructure.database import tenant_connection

router = APIRouter()


@router.get("/usage")
def get_usage(
    user: Annotated[dict[str, object], Depends(get_current_user)],
):
    tenant_id = str(user["tenant_id"])
    user_id = int(user["user_id"])
    role_str = str(user["role"])

    with tenant_connection(tenant_id) as conn:
        if role_str == "supervisor":
            ask_rows = conn.execute(
                """
                SELECT date_trunc('day', created_at) as day,
                       SUM(prompt_tokens) as prompt_tokens,
                       SUM(completion_tokens) as completion_tokens,
                       COUNT(*) as ask_count
                FROM ask_log
                GROUP BY day ORDER BY day DESC
                """
            ).fetchall()
            run_rows = conn.execute(
                """
                SELECT date_trunc('day', created_at) as day,
                       SUM(total_tokens) as total_tokens,
                       COUNT(*) as run_count
                FROM runs
                GROUP BY day ORDER BY day DESC
                """
            ).fetchall()
        else:
            ask_rows = conn.execute(
                """
                SELECT date_trunc('day', created_at) as day,
                       SUM(prompt_tokens) as prompt_tokens,
                       SUM(completion_tokens) as completion_tokens,
                       COUNT(*) as ask_count
                FROM ask_log WHERE user_id=%s
                GROUP BY day ORDER BY day DESC
                """,
                (user_id,),
            ).fetchall()
            run_rows = conn.execute(
                """
                SELECT date_trunc('day', created_at) as day,
                       SUM(total_tokens) as total_tokens,
                       COUNT(*) as run_count
                FROM runs WHERE user_id=%s
                GROUP BY day ORDER BY day DESC
                """,
                (user_id,),
            ).fetchall()

    daily_asks = [
        {
            "day": str(r[0])[:10] if r[0] else "",
            "prompt_tokens": r[1] or 0,
            "completion_tokens": r[2] or 0,
            "ask_count": r[3] or 0,
        }
        for r in ask_rows
    ]

    daily_runs = [
        {
            "day": str(r[0])[:10] if r[0] else "",
            "total_tokens": r[1] or 0,
            "run_count": r[2] or 0,
        }
        for r in run_rows
    ]

    return {
        "tenant_id": tenant_id,
        "role": role_str,
        "daily_asks": daily_asks,
        "daily_runs": daily_runs,
    }
