from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.api import schemas
from src.api.deps import get_current_user
from src.application.answering import AnswerDeps, answer_question
from src.application.embedding import GuardedEmbedder
from src.domain.llm import ConfigError, EmbeddingModelMismatchError, LLMError
from src.infrastructure.chunk_search import PostgresChunkSearch
from src.infrastructure.embedding_registry import PostgresEmbeddingIndexRegistry
from src.infrastructure.providers.factory import build_chain, build_embedding_stack

router = APIRouter()


@router.post("/ask", response_model=schemas.AskResponse)
def ask(
    body: schemas.AskRequest,
    request: Request,
    user: Annotated[dict[str, object], Depends(get_current_user)],
) -> schemas.AskResponse:
    """Answer from the authenticated user's tenant-scoped document corpus."""
    settings = request.app.state.settings
    try:
        provider, guard = build_embedding_stack(
            settings, PostgresEmbeddingIndexRegistry()
        )
        guard.ensure(settings.embedding_spec())
        dependencies = AnswerDeps(
            embedder=GuardedEmbedder(provider, guard, settings.embedding_spec()),
            search=PostgresChunkSearch(),
            chain=build_chain(settings),
            settings=settings,
        )
        answer = answer_question(str(body.question), str(user["tenant_id"]), dependencies)
    except (ConfigError, EmbeddingModelMismatchError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except LLMError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return schemas.AskResponse(
        text=answer.text,
        citations=[
            {
                "chunk_id": citation.chunk_id,
                "doc_id": citation.doc_id,
                "section": citation.section,
                "revision": citation.revision,
                "page": citation.page,
            }
            for citation in answer.citations
        ],
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
