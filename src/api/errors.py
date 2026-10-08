from __future__ import annotations

import logging

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def _json_error(request: Request, status: int, error: str, correlation_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"error": error, "correlation_id": correlation_id},
        headers={"X-Correlation-ID": correlation_id},
    )


async def not_found_handler(request: Request, exc: Exception) -> Response:
    cid = request.headers.get("x-correlation-id") or "cid-missing"
    return _json_error(request, 404, "not found", cid)


async def http_exception_handler(request: Request, exc: HTTPException) -> Response:
    status = exc.status_code
    detail = exc.detail
    cid = request.headers.get("x-correlation-id") or "cid-missing"
    return _json_error(request, status, detail if isinstance(detail, str) else "error", cid)


async def generic_exception_handler(request: Request, exc: Exception) -> Response:
    cid = request.headers.get("x-correlation-id") or "cid-missing"
    logger.exception("unhandled exception")
    return _json_error(request, 500, "internal error", cid)
