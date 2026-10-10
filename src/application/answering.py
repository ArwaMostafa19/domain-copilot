"""Grounded answering: retrieve evidence, refuse when it is weak, then cite.

The model never gets to decide what is true: it only writes prose over evidence
blocks the system retrieved. Every citation is checked against those blocks
afterwards, and a refused answer never calls the model.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterator
from dataclasses import dataclass, replace
from pathlib import Path

from src.application.ports import Embedder, LLMProvider
from src.application.retrieval import ChunkSearch, RetrievalSettings, retrieve
from src.domain.llm import CompletionRequest, Message, TokenUsage
from src.domain.rag import Answer, Citation, Evidence, RefusalReason

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
SYSTEM_PROMPT_PATH = REPO_ROOT / "prompts" / "answer_system.md"

REFUSAL_TEXT = "The information is not in the documents."
REFUSAL_MESSAGES = {
    RefusalReason.NO_EVIDENCE: (
        "I couldn't find relevant information for this question in the documents "
        "available to your tenant. Please check the controlled manual for the "
        "exact equipment and revision."
    ),
    RefusalReason.WEAK_EVIDENCE: (
        "The retrieved passages are not strong enough to support an answer to "
        "this question. Please check the controlled manual for the exact "
        "equipment and revision before acting."
    ),
    RefusalReason.OUT_OF_SCOPE: (
        "I couldn't find this topic in your tenant's maintenance documents."
    ),
    RefusalReason.EQUIPMENT_NOT_IN_TENANT: (
        "I couldn't find this equipment in the maintenance documents available "
        "to your tenant."
    ),
    RefusalReason.INVALID_CITATION: (
        "I couldn't verify that the answer was supported by the retrieved "
        "manual passages. Please check the controlled manual for the exact "
        "equipment and revision."
    ),
    RefusalReason.MISSING_CITATION: (
        "I found related information, but couldn't verify the answer from the "
        "available document references. Please check the maintenance manual."
    ),
    RefusalReason.UNSAFE_OUTPUT: (
        "I couldn't provide that response because it contained disallowed "
        "instruction or canary text. Please ask a question answerable from "
        "the controlled maintenance documents."
    ),
}
CANARY_TOKEN = "CANARY-7f3a9c"
INJECTION_MARKER = "UNTRUSTED EMBEDDED INSTRUCTION"
PROMPT_EXTRACTION_PATTERN = re.compile(
    r"(?:system\s+prompt|system\s+instructions|canary)", re.IGNORECASE
)
EQUIPMENT_REFERENCE_PATTERN = re.compile(
    r"\b(?:equipment|machine|device|manual|document|procedure|maintenance "
    r"reference|for|on|of|about)\b",
    re.IGNORECASE,
)
MEANINGFUL_STOP_WORDS = frozenset({
    "what", "which", "when", "where", "who", "whom", "whose", "why", "how",
    "does", "did", "do", "is", "are", "was", "were", "be", "been", "being",
    "the", "a", "an", "and", "or", "but", "if", "to", "of", "for", "in", "on",
    "at", "by", "with", "from", "into", "about", "as", "it", "this", "that",
    "these", "those", "me", "my", "please", "tell", "give", "show", "find",
    "according", "refer", "reference", "manual", "maintenance", "document",
    "documents", "procedure", "approved", "specified", "specification", "data",
    "information", "question", "answer", "untrusted", "compromised", "supplier",
})
WORD_PATTERN = re.compile(r"[a-z0-9]+", re.IGNORECASE)
EQUIPMENT_TENANT_PATTERN = re.compile(
    r"\b(ALPHA|BETA)-[A-Z]{2,5}-\d+[A-Z]?\b", re.IGNORECASE
)

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


def answer_question(question: str, tenant_id: str, deps: AnswerDeps, correlation_id: str | None = None) -> Answer:
    """Retrieve evidence and answer, or refuse before or after the model call."""
    if _equipment_is_outside_tenant(question, tenant_id):
        return _refusal(
            RefusalReason.EQUIPMENT_NOT_IN_TENANT, [], TokenUsage()
        )
    evidence = retrieve(question, tenant_id, deps.embedder, deps.search, deps.settings)
    if _is_prompt_extraction_request(question) or (
        evidence and not _has_topic_overlap(question, evidence)
    ):
        return _refusal(RefusalReason.OUT_OF_SCOPE, evidence, TokenUsage())
    refusal = _refusal_gate(evidence, deps.settings.retrieval_min_similarity)
    if refusal is not None:
        return _refusal(refusal, evidence, TokenUsage())

    request = CompletionRequest(
        messages=(
            Message(role="system", content=load_system_prompt()),
            Message(role="user", content=_user_message(question, evidence)),
        )
    )
    request = replace(request, max_tokens=2048, correlation_id=correlation_id)
    result = deps.chain.complete(request)
    answer = _validate(result.content, result.usage, evidence)
    if answer.reason not in {RefusalReason.MISSING_CITATION, RefusalReason.INVALID_CITATION}:
        return answer

    repair_request = CompletionRequest(
        messages=(
            Message(role="system", content=load_system_prompt()),
            Message(
                role="user",
                content=(
                    f"{_user_message(question, evidence)}\n\n"
                    "Your previous draft did not contain a valid citation. "
                    "Answer the original question again using only the evidence above. "
                    "Cite every factual statement with the exact [chunk:ID] marker "
                    "of a provided evidence block. Do not invent facts or chunk IDs. "
                    "If the evidence does not answer the question, reply exactly: "
                    f"{REFUSAL_TEXT}"
                ),
            ),
        )
    )
    repair_request = replace(repair_request, max_tokens=2048, correlation_id=correlation_id)
    repaired = deps.chain.complete(repair_request)
    combined_usage = TokenUsage(
        prompt_tokens=result.usage.prompt_tokens + repaired.usage.prompt_tokens,
        completion_tokens=result.usage.completion_tokens + repaired.usage.completion_tokens,
        estimated=result.usage.estimated or repaired.usage.estimated,
    )
    return _validate(repaired.content, combined_usage, evidence)


def stream_answer_question(question: str, tenant_id: str, deps: AnswerDeps, correlation_id: str | None = None) -> Iterator[dict[str, object]]:
    """Stream progress and model tokens, then emit the grounded final answer."""
    if _equipment_is_outside_tenant(question, tenant_id):
        answer = _refusal(
            RefusalReason.EQUIPMENT_NOT_IN_TENANT, [], TokenUsage()
        )
        yield {"event": "done", "answer": answer}
        return
    evidence = retrieve(question, tenant_id, deps.embedder, deps.search, deps.settings)
    if _is_prompt_extraction_request(question) or (
        evidence and not _has_topic_overlap(question, evidence)
    ):
        answer = _refusal(RefusalReason.OUT_OF_SCOPE, evidence, TokenUsage())
        yield {"event": "done", "answer": answer}
        return
    refusal = _refusal_gate(evidence, deps.settings.retrieval_min_similarity)
    if refusal is not None:
        answer = _refusal(refusal, evidence, TokenUsage())
        yield {"event": "done", "answer": answer}
        return
    yield {"event": "progress", "stage": "evidence_found", "count": len(evidence)}
    request = CompletionRequest(
        messages=(
            Message(role="system", content=load_system_prompt()),
            Message(role="user", content=_user_message(question, evidence)),
        )
    )
    request = replace(request, max_tokens=2048, correlation_id=correlation_id)
    content: list[str] = []
    usage = TokenUsage()
    for event in deps.chain.stream(request):
        if event.kind == "token":
            content.append(event.text)
            yield {"event": "token", "text": event.text}
        elif event.result is not None:
            usage = event.result.usage
            if not content:
                content.append(event.result.content)
    answer = _validate("".join(content), usage, evidence)
    if answer.reason in {RefusalReason.MISSING_CITATION, RefusalReason.INVALID_CITATION}:
        repair_request = CompletionRequest(
            messages=(
                Message(role="system", content=load_system_prompt()),
                Message(
                    role="user",
                    content=(
                        f"{_user_message(question, evidence)}\n\n"
                        "Your previous draft did not contain a valid citation. "
                        "Answer the original question again using only the evidence above. "
                        "Cite every factual statement with the exact [chunk:ID] marker "
                        "of a provided evidence block. Do not invent facts or chunk IDs. "
                        "If the evidence does not answer the question, reply exactly: "
                        f"{REFUSAL_TEXT}"
                    ),
                ),
            )
        )
        repair_request = replace(
            repair_request, max_tokens=2048, correlation_id=correlation_id
        )
        repaired = deps.chain.complete(repair_request)
        usage = TokenUsage(
            prompt_tokens=usage.prompt_tokens + repaired.usage.prompt_tokens,
            completion_tokens=usage.completion_tokens + repaired.usage.completion_tokens,
            estimated=usage.estimated or repaired.usage.estimated,
        )
        answer = _validate(repaired.content, usage, evidence)
    yield {"event": "done", "answer": answer}


def _refusal_gate(evidence: list[Evidence], min_similarity: float) -> str | None:
    """Refuse when there is no evidence, or when the best similarity is weak."""
    if not evidence:
        return RefusalReason.NO_EVIDENCE
    best_dense = max(item.dense_score for item in evidence)
    if best_dense < min_similarity:
        return RefusalReason.WEAK_EVIDENCE
    return None


def _has_topic_overlap(question: str, evidence: list[Evidence]) -> bool:
    """Reject unrelated questions before chat when evidence shares no topic terms.

    This is a coarse scope guard, not a semantic relevance proof. It prevents
    obviously unrelated requests from being answered from arbitrary nearest
    neighbors while leaving detailed support to citations and answer review.
    """
    question_terms = {
        term.casefold()
        for term in WORD_PATTERN.findall(question)
        if len(term) > 2 and term.casefold() not in MEANINGFUL_STOP_WORDS
    }
    if not question_terms:
        return False
    evidence_terms = {
        term.casefold()
        for item in evidence
        for term in WORD_PATTERN.findall(item.text)
    }
    overlap = question_terms & evidence_terms
    required_overlap = min(2, len(question_terms))
    return len(overlap) >= required_overlap


def _is_prompt_extraction_request(question: str) -> bool:
    """Keep explicit prompt/canary extraction requests out of maintenance RAG."""
    return bool(PROMPT_EXTRACTION_PATTERN.search(question))


def _equipment_is_outside_tenant(question: str, tenant_id: str) -> bool:
    """Refuse explicit Alpha/Beta equipment or manual IDs outside the tenant."""
    if not EQUIPMENT_REFERENCE_PATTERN.search(question):
        return False
    expected_brand = tenant_id.rsplit("-", 1)[-1].casefold()
    requested_brands = {
        match.casefold()
        for match in EQUIPMENT_TENANT_PATTERN.findall(question)
    }
    return any(brand != expected_brand for brand in requested_brands)


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
        return _refusal(RefusalReason.UNSAFE_OUTPUT, evidence, usage)

    cited_ids = _cited_chunk_ids(content)
    allowed = {item.chunk_id: item for item in evidence}
    if not cited_ids:
        return _refusal(RefusalReason.MISSING_CITATION, evidence, usage)
    if any(chunk_id not in allowed for chunk_id in cited_ids):
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
        text=REFUSAL_MESSAGES.get(reason, REFUSAL_TEXT),
        citations=(),
        refused=True,
        reason=reason,
        usage=usage,
        evidence=tuple(evidence),
    )
