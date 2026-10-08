from __future__ import annotations

import logging
import time
import uuid
from pathlib import Path

import psycopg
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api.routers.ask import router as ask_router
from src.api.routers.auth import router as auth_router
from src.api.routers.documents import router as documents_router
from src.api.routers.health import router as health_router
from src.api.routers.ingest import router as ingest_router
from src.api.routers.runs import router as runs_router
from src.api.routers.usage import router as usage_router
from src.domain.llm import (
    LLMError,
    ProviderError,
    ProviderUnavailableError,
    QuotaExceededError,
)
from src.infrastructure.config import load_settings_from_environ

# Standard JSON Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp":"%(asctime)s", "level":"%(levelname)s", "module":"%(module)s", "message":"%(message)s"}',
)
logger = logging.getLogger("copilot_api")

app = FastAPI(title="Domain Copilot")
app.state.settings = load_settings_from_environ()
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(app.state.settings.cors_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Correlation-ID"],
)

# Rate limit tracking for login attempts
_login_attempts: dict[str, list[float]] = {}


@app.middleware("http")
async def security_and_correlation_middleware(request: Request, call_next):
    # Correlation ID
    cid = request.headers.get("X-Correlation-ID") or uuid.uuid4().hex
    request.state.correlation_id = cid

    # Login Rate Limiting (5 attempts per 60s per client IP)
    if request.url.path == "/auth/login" and request.method == "POST":
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        attempts = [t for t in _login_attempts.get(client_ip, []) if now - t < 60]
        if len(attempts) >= 5:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "too many login attempts"},
                headers={"Retry-After": "60"},
            )
        attempts.append(now)
        _login_attempts[client_ip] = attempts

    # Payload Size Limit (1 MB = 1,048,576 bytes)
    content_length = request.headers.get("Content-Length")
    if content_length:
        try:
            payload_size = int(content_length)
        except ValueError:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "invalid Content-Length"},
            )
        if payload_size < 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "invalid Content-Length"},
            )
        if payload_size > 1048576:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": "payload too large"},
            )
    if len(await request.body()) > 1048576:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={"detail": "payload too large"},
        )

    response = await call_next(request)

    # Inject Security Headers & CSP
    response.headers["X-Correlation-ID"] = cid
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    if request.url.path == "/" or request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';"
    )
    return response


# Global Error Mappings
@app.exception_handler(ProviderError)
@app.exception_handler(ProviderUnavailableError)
@app.exception_handler(QuotaExceededError)
@app.exception_handler(LLMError)
async def provider_error_handler(request: Request, exc: Exception):
    logger.error("Provider failure mapped to 502: %s", type(exc).__name__)
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"detail": "provider unavailable"},
    )


@app.exception_handler(psycopg.Error)
async def database_error_handler(request: Request, exc: Exception):
    logger.error("Database failure mapped to 503: %s", type(exc).__name__)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "database service unavailable"},
    )


# Register Routers
app.include_router(auth_router)
app.include_router(ask_router)
app.include_router(runs_router)
app.include_router(ingest_router)
app.include_router(documents_router)
app.include_router(usage_router)
app.include_router(health_router)

# Mount Static Files & Serve index.html
STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"status": "ok", "message": "Domain Copilot API"}
