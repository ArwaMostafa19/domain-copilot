"""Offline provider for tests and for running with no vendor installed."""

from __future__ import annotations

import hashlib
import math
from collections.abc import Iterator, Sequence

from src.domain.llm import (
    CompletionRequest,
    CompletionResult,
    EmbeddingResult,
    StreamEvent,
    TokenUsage,
    estimate_tokens,
    estimate_usage,
)

ScriptItem = str | CompletionResult | Exception


class FakeLLMProvider:
    """A deterministic provider: no network, no randomness, no time.

    ``script`` is consumed in order by ``complete()`` and ``stream()``: an
    ``str`` is the answer, a ``CompletionResult`` is returned as-is, and an
    ``Exception`` is raised. When the script is exhausted the provider answers
    with ``"fake response to: <last user message>"``.
    """

    def __init__(
        self,
        name: str = "fake",
        script: Sequence[ScriptItem] | None = None,
        embedding_model: str = "fake-embedding",
        embedding_dimensions: int = 768,
    ) -> None:
        self.name = name
        self.embedding_model = embedding_model
        self.embedding_dimensions = embedding_dimensions
        self._script: list[ScriptItem] = list(script or [])
        self.calls: list[tuple[str, object]] = []

    def complete(self, request: CompletionRequest) -> CompletionResult:
        item = self._next_item()
        self.calls.append(("complete", request))
        if isinstance(item, Exception):
            raise item
        if isinstance(item, CompletionResult):
            return item
        content = str(item) if item is not None else self._fabricate(request)
        return CompletionResult(
            content=content,
            tool_calls=(),
            usage=estimate_usage(request.prompt_text(), content),
            provider=self.name,
            model=self.name,
        )

    def stream(self, request: CompletionRequest) -> Iterator[StreamEvent]:
        item = self._next_item()
        self.calls.append(("stream", request))
        if isinstance(item, Exception):
            raise item
        content = (
            item.content
            if isinstance(item, CompletionResult)
            else (str(item) if item is not None else self._fabricate(request))
        )
        for token in _tokenize(content):
            yield StreamEvent(kind="token", text=token)
        if isinstance(item, CompletionResult):
            result = item
        else:
            result = CompletionResult(
                content=content,
                tool_calls=(),
                usage=estimate_usage(request.prompt_text(), content),
                provider=self.name,
                model=self.name,
            )
        yield StreamEvent(kind="done", result=result)

    def embed(self, texts: Sequence[str]) -> EmbeddingResult:
        batch = list(texts)
        self.calls.append(("embed", batch))
        prompt_tokens = sum(estimate_tokens(text) for text in batch)
        return EmbeddingResult(
            vectors=tuple(self._normalised_vector(text) for text in batch),
            model=self.embedding_model,
            dimensions=self.embedding_dimensions,
            usage=TokenUsage(
                prompt_tokens=prompt_tokens, completion_tokens=0, estimated=True
            ),
            provider=self.name,
        )

    def _next_item(self) -> ScriptItem | None:
        if not self._script:
            return None
        return self._script.pop(0)

    def _fabricate(self, request: CompletionRequest) -> str:
        last_user = next(
            (m.content for m in reversed(request.messages) if m.role == "user"), ""
        )
        return f"fake response to: {last_user}"

    def _normalised_vector(self, text: str) -> tuple[float, ...]:
        """One vector grown from the sha256 of text, then L2-normalised."""
        values: list[float] = []
        counter = 0
        while len(values) < self.embedding_dimensions:
            block = hashlib.sha256(f"{text}:{counter}".encode()).digest()
            values.extend(byte / 127.5 - 1.0 for byte in block)
            counter += 1
        values = values[: self.embedding_dimensions]
        norm = math.sqrt(sum(value * value for value in values))
        scale = norm if norm > 0 else 1.0
        return tuple(value / scale for value in values)


def _tokenize(content: str) -> list[str]:
    """Split an answer into word tokens that join back to the original text."""
    if not content:
        return []
    parts = content.split(" ")
    tokens = [part + " " for part in parts[:-1]]
    tokens.append(parts[-1])
    return tokens