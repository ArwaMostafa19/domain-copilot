"""Grounded answering: retrieve evidence, refuse when it is weak, then cite.

The model never gets to decide what is true: it only writes prose over evidence
blocks the system retrieved. Every citation is checked against those blocks
afterwards, and a refused answer never calls the model.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path

from src.application.ports import Embedder, LLMProvider
from src.application.retrieval import ChunkSearch, RetrievalSettings, retrieve
from src.domain.llm import CompletionRequest, Message, TokenUsage
from src.domain.rag import Answer, Citation, Evidence, RefusalReason

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
SYSTEM_PROMPT_PATH = REPO_ROOT / "prompts" / "answer_system.md"

REFUSAL_TEXT = "The information is not in the documents."
CANARY_TOKEN = "CANARY-7f3a9c"
INJECTION_MARKER = "UNTRUSTED EMBEDDED INSTRUCTION"

CITATION_PATTERN = re.compile(r"\[chunk:(\d+)\]")


@dataclass(frozen=True)
class AnswerDeps:
    """Everything ``answer_question`` needs, injected so tests stay offline."""

    embedder: Embedder
    search: ChunkSearch
    chain: LLMProvider
    settings: RetrievalSettings


def load_system_prompt(path: Path = SYSTEM_PROMPT_PATH) -> str:
    """Read the system prompt from its file (never inlined in the code)."""
    return path.read_text(encoding="utf-8")


def answer_question(question: str, tenant_id: str, deps: AnswerDeps) -> Answer:
    """Retrieve evidence and answer, or refuse before or after the model call."""
    evidence = retrieve(question, tenant_id, deps.embedder, deps.search, deps.settings)
    refusal = _refusal_gate(evidence, deps.settings.retrieval_min_similarity)
    if refusal is not None:
        return _refusal(refusal, evidence, TokenUsage())

    request = CompletionRequest(
        messages=(
            Message(role="system", content=load_system_prompt()),
            Message(role="user", content=_user_message(question, evidence)),
        )
    )
    result = deps.chain.complete(request)
    return _validate(result.content, result.usage, evidence)


def _refusal_gate(evidence: list[Evidence], min_similarity: float) -> str | None:
    """Refuse when there is no evidence, or when the best similarity is weak."""
    if not evidence:
        return RefusalReason.NO_EVIDENCE
    best_dense = max(item.dense_score for item in evidence)
    if best_dense < min_similarity:
        return RefusalReason.WEAK_EVIDENCE
    return None


def _user_message(question: str, evidence: list[Evidence]) -> str:
    """The evidence blocks, each wrapped as data, followed by the question."""
    blocks = "\n\n".join(_evidence_block(item) for item in evidence)
    return f"{blocks}\n\nQuestion: {question}"


def _evidence_block(item: Evidence) -> str:
    return (
        f"<<<EVIDENCE chunk={item.chunk_id} doc={item.doc_id} "
        f'section="{item.section}" revision={item.revision} '
        f"status={item.doc_status}>>>\n{item.text}\n<<<END EVIDENCE>>>"
    )


def _validate(content: str, usage: TokenUsage, evidence: list[Evidence]) -> Answer:
    """Check the citations of the model answer, or refuse and drop it."""
    if CANARY_TOKEN in content or INJECTION_MARKER in content:
        logger.warning("answer rejected: canary token or injection marker present")
        return _refusal(RefusalReason.INVALID_CITATION, evidence, usage)

    cited_ids = _cited_chunk_ids(content)
    allowed = {item.chunk_id: item for item in evidence}
    if not cited_ids or any(chunk_id not in allowed for chunk_id in cited_ids):
        return _refusal(RefusalReason.INVALID_CITATION, evidence, usage)

    citations = tuple(_citation(allowed[chunk_id]) for chunk_id in cited_ids)
    return Answer(
        text=content,
        citations=citations,
        refused=False,
        reason=None,
        usage=usage,
        evidence=tuple(evidence),
    )


def _cited_chunk_ids(content: str) -> list[int]:
    """The cited chunk ids, de-duplicated, in the order they appear."""
    ordered: dict[int, None] = {}
    for match in CITATION_PATTERN.finditer(content):
        ordered[int(match.group(1))] = None
    return list(ordered)


def _citation(item: Evidence) -> Citation:
    return Citation(
        chunk_id=item.chunk_id,
        doc_id=item.doc_id,
        section=item.section,
        revision=item.revision,
        page=item.page,
    )


def _refusal(reason: str, evidence: list[Evidence], usage: TokenUsage) -> Answer:
    return Answer(
        text=REFUSAL_TEXT,
        citations=(),
        refused=True,
        reason=reason,
        usage=usage,
        evidence=tuple(evidence),
    )
