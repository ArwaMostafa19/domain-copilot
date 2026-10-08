"""Small deterministic PII redactor used at every model and embedding boundary."""

from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from dataclasses import replace

from src.domain.llm import CompletionRequest, StreamEvent

_PATTERNS = (
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(r"(?<!\w)(?:\+?\d[\d .()-]{7,}\d)(?!\w)"),
    re.compile(r"\b\d{14}\b"),
)


def redact_text(text: str) -> str:
    """Replace email, phone-like number and Egyptian national ID patterns."""
    redacted = text
    for index, pattern in enumerate(_PATTERNS, start=1):
        redacted = pattern.sub(f"[REDACTED_PII_{index}]", redacted)
    return redacted


class RedactingProvider:
    """Sanitize prompts and embeddings immediately before provider calls."""

    def __init__(self, provider):
        self._provider = provider
        self.name = provider.name

    def __getattr__(self, name: str):
        return getattr(self._provider, name)

    def complete(self, request: CompletionRequest):
        return self._provider.complete(_redact_request(request))

    def stream(self, request: CompletionRequest) -> Iterator[StreamEvent]:
        yield from self._provider.stream(_redact_request(request))

    def embed(self, texts: Sequence[str]):
        return self._provider.embed([redact_text(text) for text in texts])


def _redact_request(request: CompletionRequest) -> CompletionRequest:
    return replace(
        request,
        messages=tuple(
            replace(
                message,
                content=redact_text(message.content),
                tool_calls=tuple(
                    replace(call, arguments=_redact_value(call.arguments))
                    for call in message.tool_calls
                ),
            )
            for message in request.messages
        ),
    )


def _redact_value(value):
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _redact_value(item) for key, item in value.items()}
    return value
