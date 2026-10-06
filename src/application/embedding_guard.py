from __future__ import annotations

from src.application.ports import EmbeddingIndexRegistry
from src.domain.llm import (
    ConfigError,
    EmbeddingModelMismatchError,
    EmbeddingResult,
    EmbeddingSpec,
)


class EmbeddingGuard:
    """Makes sure one embedding model (name + size) is used for the whole index."""

    def __init__(self, registry: EmbeddingIndexRegistry) -> None:
        self._registry = registry
        self._spec: EmbeddingSpec | None = None

    def ensure(self, configured: EmbeddingSpec) -> None:
        recorded = self._registry.get()
        if recorded is None:
            self._registry.register(configured)
            recorded = self._registry.get()  
        if recorded != configured:
            raise EmbeddingModelMismatchError(
                f"index was built with {recorded.model} ({recorded.dimensions}d) but "
                f"configuration asks for {configured.model} ({configured.dimensions}d); "
                "restore the configuration or re-index everything"
            )
        self._spec = configured

    def verify(self, result: EmbeddingResult) -> None:
        if self._spec is None:
            raise ConfigError("EmbeddingGuard.ensure() must be called before verify()")
        spec = self._spec
        wrong_size = any(len(v) != spec.dimensions for v in result.vectors)
        if result.model != spec.model or result.dimensions != spec.dimensions or wrong_size:
            raise EmbeddingModelMismatchError(
                f"provider {result.provider} returned {result.model} ({result.dimensions}d), "
                f"expected {spec.model} ({spec.dimensions}d)"
            )