"""Builds providers, the fallback chain and the embedding stack from Settings."""

from __future__ import annotations

from collections.abc import Mapping

import httpx

from src.application.embedding_guard import EmbeddingGuard
from src.application.llm_router import FallbackChain
from src.application.ports import EmbeddingIndexRegistry, LLMProvider
from src.domain.llm import ConfigError
from src.infrastructure.config import Settings
from src.infrastructure.providers.fake import FakeLLMProvider
from src.infrastructure.providers.ollama_provider import OllamaProvider
from src.infrastructure.providers.openai_compatible import OpenAICompatibleProvider

# The environment variables each chat provider needs set before it can run.
CHAT_VARIABLES: Mapping[str, tuple[str, ...]] = {
    "groq": ("GROQ_API_KEY", "GROQ_MODEL"),
    "gemini": ("GEMINI_API_KEY", "GEMINI_MODEL"),
    "ollama": ("OLLAMA_CHAT_MODEL",),
    "fake": (),
}

# The environment variables each embedding provider needs.
EMBEDDING_VARIABLES: Mapping[str, tuple[str, ...]] = {
    "ollama": (),
    "fake": (),
    "gemini": ("GEMINI_API_KEY",),
}

# The Settings attribute that holds the value of each environment variable.
VARIABLE_ATTRIBUTE: Mapping[str, str] = {
    "GROQ_API_KEY": "groq_api_key",
    "GROQ_MODEL": "groq_model",
    "GEMINI_API_KEY": "gemini_api_key",
    "GEMINI_MODEL": "gemini_model",
    "OLLAMA_CHAT_MODEL": "ollama_chat_model",
}


def build_providers(
    settings: Settings, client: httpx.Client | None = None
) -> dict[str, LLMProvider]:
    """One provider for every name the chain or the embedding stack needs."""
    wanted: list[str] = []
    for name in (*settings.llm_chain, settings.embedding_provider):
        if name not in wanted:
            wanted.append(name)
    return {name: _build_one(name, settings, client) for name in wanted}


def build_chain(
    settings: Settings, client: httpx.Client | None = None
) -> FallbackChain:
    """A chat chain in LLM_CHAIN order with the configured embedder and cooldown."""
    for name in settings.llm_chain:
        _require_variables(settings, name, CHAT_VARIABLES[name])
    providers = build_providers(settings, client=client)
    ordered = [providers[name] for name in settings.llm_chain]
    embedder = providers[settings.embedding_provider]
    return FallbackChain(
        ordered, embedder, cooldown_seconds=settings.llm_cooldown_seconds
    )


def build_embedding_stack(
    settings: Settings,
    registry: EmbeddingIndexRegistry,
    client: httpx.Client | None = None,
) -> tuple[LLMProvider, EmbeddingGuard]:
    """The provider used for embeddings and the guard that checks its model.

    Only the embedding provider is built: the chat chain is not needed to ingest.
    """
    required = EMBEDDING_VARIABLES.get(settings.embedding_provider, ())
    _require_variables(settings, settings.embedding_provider, required)
    provider = _build_one(settings.embedding_provider, settings, client)
    return provider, EmbeddingGuard(registry)


def _build_one(
    name: str, settings: Settings, client: httpx.Client | None
) -> LLMProvider:
    if name == "ollama":
        return OllamaProvider(
            base_url=settings.ollama_base_url,
            embedding_model=settings.embedding_model,
            embedding_dimensions=settings.embedding_dimensions,
            chat_model=settings.ollama_chat_model or None,
            timeout=settings.llm_timeout_seconds,
            client=client,
        )
    if name == "fake":
        return FakeLLMProvider(
            embedding_model=settings.embedding_model,
            embedding_dimensions=settings.embedding_dimensions,
        )
    if name == "groq":
        return OpenAICompatibleProvider(
            name="groq",
            base_url=settings.groq_base_url,
            api_key=settings.groq_api_key,
            model=settings.groq_model or None,
            timeout=settings.llm_timeout_seconds,
            client=client,
            stream_usage_option=settings.groq_stream_usage,
        )
    if name == "gemini":
        return OpenAICompatibleProvider(
            name="gemini",
            base_url=settings.gemini_base_url,
            api_key=settings.gemini_api_key,
            model=settings.gemini_model or None,
            embedding_model=(
                settings.embedding_model
                if settings.embedding_provider == "gemini"
                else None
            ),
            timeout=settings.llm_timeout_seconds,
            client=client,
            stream_usage_option=settings.gemini_stream_usage,
        )
    raise ConfigError(f"unknown provider {name!r}")


def _require_variables(
    settings: Settings, name: str, variables: tuple[str, ...]
) -> None:
    """Every needed variable must be set; the error names the missing one."""
    for variable in variables:
        attribute = VARIABLE_ATTRIBUTE[variable]
        if not getattr(settings, attribute):
            raise ConfigError(
                f"provider {name!r} needs {variable}, but it is not set"
            )