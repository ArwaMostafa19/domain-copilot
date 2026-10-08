import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from src.api import schemas
from src.api.deps import get_current_user
from src.application.answering import (
    AnswerDeps,
    answer_question,
    stream_answer_question,
)
from src.application.embedding import GuardedEmbedder
from src.application.ports import AskLogRecord
from src.domain.llm import ConfigError, EmbeddingModelMismatchError, LLMError
from src.infrastructure.chunk_search import PostgresChunkSearch
from src.infrastructure.embedding_registry import PostgresEmbeddingIndexRegistry
from src.infrastructure.providers.factory import build_chain, build_embedding_stack
from src.infrastructure.workflow_repository import PgAskLogRepository

logger = logging.getLogger(__name__)
router = APIRouter()


def _dependencies(settings) -> AnswerDeps:
    provider, guard = build_embedding_stack(settings, PostgresEmbeddingIndexRegistry())
    guard.ensure(settings.embedding_spec())
    return AnswerDeps(
        embedder=GuardedEmbedder(provider, guard, settings.embedding_spec()),
        search=PostgresChunkSearch(),
        chain=build_chain(settings),
        settings=settings,
    )


def _citations(answer):
    return [
        {"chunk_id": item.chunk_id, "doc_id": item.doc_id, "section": item.section,
         "revision": item.revision, "page": item.page}
        for item in answer.citations
    ]


@router.post("/ask", response_model=schemas.AskResponse)
def ask(
    body: schemas.AskRequest,
    request: Request,
    user: Annotated[dict[str, object], Depends(get_current_user)],
) -> schemas.AskResponse:
    """Answer from the authenticated user's tenant-scoped document corpus."""
    settings = request.app.state.settings
    cid = getattr(request.state, "correlation_id", uuid.uuid4().hex)
    tenant_id = str(user["tenant_id"])
    user_id = int(user["user_id"])

    try:
        dependencies = _dependencies(settings)
        answer = answer_question(str(body.question), tenant_id, dependencies, correlation_id=cid)
    except (ConfigError, EmbeddingModelMismatchError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="model configuration unavailable",
        ) from exc
    except LLMError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="provider unavailable",
        ) from exc

    citations_list = _citations(answer)

    # Save ask log entry
    try:
        ask_repo = PgAskLogRepository()
        rec = AskLogRecord(
            id=None,
            tenant_id=tenant_id,
            user_id=user_id,
            correlation_id=cid,
            question=str(body.question),
            answer_text=answer.text,
            refused=answer.refused,
            reason=answer.reason,
            citations=citations_list,
            prompt_tokens=answer.usage.prompt_tokens,
            completion_tokens=answer.usage.completion_tokens,
            estimated=answer.usage.estimated,
        )
        ask_repo.save(tenant_id, rec)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not save ask log entry: %s", type(exc).__name__)

    return schemas.AskResponse(
        text=answer.text,
        citations=citations_list,
        refused=answer.refused,
        reason=answer.reason,
        usage={
            "prompt_tokens": answer.usage.prompt_tokens,
            "completion_tokens": answer.usage.completion_tokens,
            "total_tokens": answer.usage.total_tokens,
            "estimated": answer.usage.estimated,
        },
        evidence=[
            {
                "chunk_id": item.chunk_id,
                "doc_id": item.doc_id,
                "title": item.title,
                "section": item.section,
                "revision": item.revision,
                "page": item.page,
                "text": item.text,
                "dense_score": item.dense_score,
                "keyword_score": item.keyword_score,
            }
            for item in answer.evidence
        ],
    )


@router.post("/ask/stream")
def ask_stream(
    body: schemas.AskRequest,
    request: Request,
    user: Annotated[dict[str, object], Depends(get_current_user)],
):
    settings = request.app.state.settings
    cid = getattr(request.state, "correlation_id", uuid.uuid4().hex)
    tenant_id = str(user["tenant_id"])
    user_id = int(user["user_id"])
    try:
        dependencies = _dependencies(settings)
    except (ConfigError, EmbeddingModelMismatchError) as exc:
        raise HTTPException(status_code=503, detail="model configuration unavailable") from exc

    def events():
        try:
            for item in stream_answer_question(str(body.question), tenant_id, dependencies, correlation_id=cid):
                if item["event"] != "done":
                    payload = item
                else:
                    answer = item["answer"]
                    citation_rows = _citations(answer)
                    try:
                        PgAskLogRepository().save(tenant_id, AskLogRecord(
                            id=None, tenant_id=tenant_id, user_id=user_id,
                            correlation_id=cid, question=str(body.question),
                            answer_text=answer.text, refused=answer.refused,
                            reason=answer.reason, citations=citation_rows,
                            prompt_tokens=answer.usage.prompt_tokens,
                            completion_tokens=answer.usage.completion_tokens,
                            estimated=answer.usage.estimated,
                        ))
                    except Exception as exc:  # noqa: BLE001
                        logger.warning("Could not save streamed ask: %s", type(exc).__name__)
                    payload = {
                        "event": "done", "text": answer.text,
                        "citations": citation_rows, "refused": answer.refused,
                        "reason": answer.reason,
                        "usage": {"prompt_tokens": answer.usage.prompt_tokens,
                                  "completion_tokens": answer.usage.completion_tokens,
                                  "total_tokens": answer.usage.total_tokens,
                                  "estimated": answer.usage.estimated},
                    }
                import json
                yield f"data: {json.dumps(payload)}\n\n"
        except LLMError:
            yield 'data: {"event":"error","detail":"provider unavailable"}\n\n'

    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})


@router.get("/asks")
def list_asks(
    user: Annotated[dict[str, object], Depends(get_current_user)],
):
    tenant_id = str(user["tenant_id"])
    user_id = int(user["user_id"])
    ask_repo = PgAskLogRepository()
    records = ask_repo.list_for_user(tenant_id, user_id)
    return [
        {
            "id": r.id,
            "correlation_id": r.correlation_id,
            "question": r.question,
            "answer_text": r.answer_text,
            "refused": r.refused,
            "reason": r.reason,
            "citations": r.citations,
            "prompt_tokens": r.prompt_tokens,
            "completion_tokens": r.completion_tokens,
            "estimated": r.estimated,
            "created_at": r.created_at,
        }
        for r in records
    ]
