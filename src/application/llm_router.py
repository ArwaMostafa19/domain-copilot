from __future__ import annotations

import logging
import time
from collections.abc import Callable, Iterator, Sequence

from src.application.ports import LLMProvider
from src.domain.llm import (
    AllProvidersFailedError,
    CompletionRequest,
    CompletionResult,
    ConfigError,
    EmbeddingResult,
    ProviderAuthError,
    ProviderError,
    QuotaExceededError,
    StreamEvent,
)

logger = logging.getLogger(__name__)

# Errors that will not fix themselves in seconds: skip the provider for a while.
_COOLDOWN_ERRORS = (QuotaExceededError, ProviderAuthError)


class FallbackChain:
    """Tries completion providers in order. Embeddings never fall back (one fixed model)."""

    name = "fallback-chain"

    def __init__(
        self,
        providers: Sequence[LLMProvider],
        embedder: LLMProvider,
        *,
        cooldown_seconds: float = 60.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if not providers:
            raise ConfigError("the fallback chain needs at least one completion provider")
        names = [p.name for p in providers]
        if len(set(names)) != len(names):
            raise ConfigError(f"duplicate provider names in chain: {names}")
        self._providers = tuple(providers)
        self._embedder = embedder
        self._cooldown = cooldown_seconds
        self._clock = clock
        self._blocked_until: dict[str, float] = {}

    def complete(self, request: CompletionRequest) -> CompletionResult:
        failures: list[ProviderError] = []
        for provider in self._candidates():
            try:
                return provider.complete(request)
            except ProviderError as exc:
                if not exc.fallback_allowed:
                    raise
                self._record_failure(provider, exc)
                failures.append(exc)
        raise AllProvidersFailedError(failures)

    def stream(self, request: CompletionRequest) -> Iterator[StreamEvent]:
        failures: list[ProviderError] = []
        for provider in self._candidates():
            started = False
            try:
                for event in provider.stream(request):
                    started = True
                    yield event
                return
            except ProviderError as exc:
                if started or not exc.fallback_allowed:
                    raise
                self._record_failure(provider, exc)
                failures.append(exc)
        raise AllProvidersFailedError(failures)

    def embed(self, texts: Sequence[str]) -> EmbeddingResult:
        return self._embedder.embed(texts)

    def _candidates(self) -> list[LLMProvider]:
        now = self._clock()
        ready = [p for p in self._providers if self._blocked_until.get(p.name, 0.0) <= now]
        return ready or list(self._providers)
    def _record_failure(self, provider: LLMProvider, exc: ProviderError) -> None:
        logger.warning("provider %s failed (%s); trying next", provider.name, type(exc).__name__)
        if isinstance(exc, _COOLDOWN_ERRORS):
            self._blocked_until[provider.name] = self._clock() + self._cooldown
