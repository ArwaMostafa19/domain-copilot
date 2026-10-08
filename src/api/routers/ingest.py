from __future__ import annotations

import json
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
        allowed_extensions = {".md", ".pdf"}
        max_bytes = request.app.state.settings.max_ingest_file_bytes
        files = [
            p for p in corpus_dir.rglob("*")
            if p.is_file()
            and p.suffix.lower() in allowed_extensions
            and p.stat().st_size <= max_bytes
        ]
        results = ingest_files(files, provider, doc_repo)
        for res in results:
            yield f"data: {json.dumps({'event': 'document', 'path': res.path, 'status': res.status, 'chunks': res.chunks, 'steps': res.steps, 'error': res.error})}\n\n"
        yield f"data: {json.dumps({'event': 'completed', 'tenant_id': tenant_id, 'total_files': len(results)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
