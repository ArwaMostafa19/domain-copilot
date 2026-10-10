from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from src.api.deps import get_current_user
from src.application.ingest import ingest_files
from src.infrastructure.embedding_registry import PostgresEmbeddingIndexRegistry
from src.infrastructure.providers.factory import build_embedding_stack
from src.infrastructure.repository import PostgresDocumentRepository

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/ingest/corpus")
def trigger_ingest(
    request: Request,
    user: Annotated[dict[str, object], Depends(get_current_user)],
):
    role_str = str(user["role"])
    if role_str != "supervisor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="forbidden: supervisor role required for ingestion",
        )

    tenant_id = str(user["tenant_id"])
    settings = request.app.state.settings

    try:
        provider, guard = build_embedding_stack(settings, PostgresEmbeddingIndexRegistry())
        guard.ensure(settings.embedding_spec())
        doc_repo = PostgresDocumentRepository()
        corpus_dir = Path(__file__).resolve().parents[3] / "corpus" / tenant_id
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    def event_stream():
        yield f"data: {json.dumps({'event': 'started', 'tenant_id': tenant_id})}\n\n"
        try:
            if not corpus_dir.is_dir():
                raise FileNotFoundError(f"tenant corpus directory is missing: {corpus_dir}")
            allowed_extensions = {".md", ".pdf"}
            max_bytes = request.app.state.settings.max_ingest_file_bytes
            files = sorted(
                (
                    path
                    for path in corpus_dir.rglob("*")
                    if path.is_file()
                    and path.suffix.lower() in allowed_extensions
                    and path.stat().st_size <= max_bytes
                ),
                key=lambda path: path.as_posix(),
            )
            results = ingest_files(files, provider, doc_repo)
            for result in results:
                yield f"data: {json.dumps({'event': 'document', 'path': result.path, 'status': result.status, 'chunks': result.chunks, 'steps': result.steps, 'error': result.error})}\n\n"
            yield f"data: {json.dumps({'event': 'completed', 'tenant_id': tenant_id, 'total_files': len(results)})}\n\n"
        except (OSError, RuntimeError, ValueError) as exc:
            logger.exception("corpus ingestion failed for tenant %s", tenant_id)
            yield f"data: {json.dumps({'event': 'error', 'detail': f'{type(exc).__name__}: {exc}'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
