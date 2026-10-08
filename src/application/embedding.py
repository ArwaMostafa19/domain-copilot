"""GuardedEmbedder: the Embedder adapter that validates every provider answer."""

from __future__ import annotations

from src.application.embedding_guard import EmbeddingGuard
from src.application.ports import LLMProvider
from src.domain.llm import EmbeddingSpec, TokenUsage


class GuardedEmbedder:
    """An Embedder whose vectors must match the recorded embedding model.

    ``model_name`` and ``dimension`` are fixed by the configuration, so
    ingestion stores and validates against the same spec the guard checked.
    """

    def __init__(self, provider: LLMProvider, guard: EmbeddingGuard, spec: EmbeddingSpec) -> None:
        self._provider = provider
        self._guard = guard
        self.model_name = spec.model
        self.dimension = spec.dimensions
        self._total = TokenUsage()

    @property
    def total_usage(self) -> TokenUsage:
        """The token usage of every embedding batch seen so far."""
        return self._total

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed every text, or return an empty list without calling the provider."""
        if not texts:
            return []
        result = self._provider.embed(texts)
        self._guard.verify(result)
        self._total = TokenUsage(
            prompt_tokens=self._total.prompt_tokens + result.usage.prompt_tokens,
            completion_tokens=(
                self._total.completion_tokens + result.usage.completion_tokens
            ),
            estimated=self._total.estimated or result.usage.estimated,
        )
        return [list(vector) for vector in result.vectors]
