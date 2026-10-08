from __future__ import annotations

import psycopg
from fastapi import APIRouter, HTTPException, Request, status

from src.infrastructure.database import app_connection
from src.infrastructure.providers.factory import build_chain

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness check; it does not depend on downstream services."""
    return {"status": "ok"}


@router.get("/ready")
def ready(request: Request) -> dict[str, str]:
    """Readiness requires the database and configured model endpoints."""
    try:
        with app_connection() as connection:
            connection.execute("SELECT 1")
    except (KeyError, psycopg.Error) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unavailable",
        ) from exc
    try:
        chain = build_chain(request.app.state.settings)
        if not chain.healthcheck():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="model provider unavailable",
            )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="model provider unavailable",
        ) from exc
    return {"status": "ready"}
