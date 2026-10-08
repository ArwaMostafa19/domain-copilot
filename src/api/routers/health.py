from __future__ import annotations

import psycopg
from fastapi import APIRouter, HTTPException, status

from src.infrastructure.database import app_connection

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness check; it does not depend on downstream services."""
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict[str, str]:
    """Readiness check; report ready only when the application DB is reachable."""
    try:
        with app_connection() as connection:
            connection.execute("SELECT 1")
    except (KeyError, psycopg.Error) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unavailable",
        ) from exc
    return {"status": "ready"}
