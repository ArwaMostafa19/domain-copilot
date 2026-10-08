"""Configuration of the LLM and embedding stack.

This is the only module of the project that reads API keys from the
environment. ``load_settings`` checks syntax only: it never requires a key,
so ingestion works without GROQ_API_KEY and GEMINI_API_KEY.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, fields

from src.domain.llm import ConfigError, EmbeddingSpec

CHAT_PROVIDERS = ("groq", "gemini", "ollama", "fake")
EMBEDDING_PROVIDERS = ("ollama", "gemini", "fake")

DEFAULT_LLM_CHAIN = "groq,gemini,ollama"
DEFAULT_GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai"
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_EMBEDDING_PROVIDER = "ollama"
DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"
DEFAULT_EMBEDDING_DIMENSIONS = 768
DEFAULT_LLM_TIMEOUT_SECONDS = 180.0
DEFAULT_LLM_COOLDOWN_SECONDS = 60.0
DEFAULT_RETRIEVAL_MIN_SIMILARITY = 0.55
DEFAULT_RUN_MAX_MODEL_CALLS = 6
DEFAULT_RUN_TOKEN_BUDGET = 20000
DEFAULT_RUN_TIMEOUT_SECONDS = 120.0
DEFAULT_RUN_STEP_TIMEOUT_SECONDS = 45.0
DEFAULT_TOKEN_TTL_SECONDS = 28800
DEFAULT_MAX_INGEST_FILE_BYTES = 10 * 1024 * 1024

# Fixed for every provider: opening the TCP connection never waits longer.
CONNECT_TIMEOUT_SECONDS = 5.0

SECRET_FIELDS = ("groq_api_key", "gemini_api_key", "auth_secret")


@dataclass(frozen=True, repr=False)
class Settings:
    """One immutable snapshot of every environment variable the LLM layer uses."""

    llm_chain: tuple[str, ...]
    groq_api_key: str
    groq_base_url: str
    groq_model: str
    gemini_api_key: str
    gemini_base_url: str
    gemini_model: str
    ollama_base_url: str
    ollama_chat_model: str
    embedding_provider: str
    embedding_model: str
    embedding_dimensions: int
    llm_timeout_seconds: float
    llm_cooldown_seconds: float
    groq_stream_usage: bool
    gemini_stream_usage: bool
    retrieval_min_similarity: float
    auth_secret: str
    run_max_model_calls: int = DEFAULT_RUN_MAX_MODEL_CALLS
    run_token_budget: int = DEFAULT_RUN_TOKEN_BUDGET
    run_timeout_seconds: float = DEFAULT_RUN_TIMEOUT_SECONDS
    run_step_timeout_seconds: float = DEFAULT_RUN_STEP_TIMEOUT_SECONDS
    token_ttl_seconds: int = DEFAULT_TOKEN_TTL_SECONDS
    cors_origins: tuple[str, ...] = ()
    max_ingest_file_bytes: int = DEFAULT_MAX_INGEST_FILE_BYTES

    def embedding_spec(self) -> EmbeddingSpec:
        """The model and size the embedding index must be built with."""
        return EmbeddingSpec(self.embedding_model, self.embedding_dimensions)

    def __repr__(self) -> str:
        """Every field, but the API keys are always hidden."""
        hidden = []
        for field in fields(self):
            value = getattr(self, field.name)
            if field.name in SECRET_FIELDS:
                value = "***" if value else ""
            hidden.append(f"{field.name}={value!r}")
        return f"Settings({', '.join(hidden)})"


def load_settings(environ: Mapping[str, str]) -> Settings:
    """Read and syntax-check the configuration. Raises ConfigError on bad syntax."""
    return Settings(
        llm_chain=_read_chain(environ),
        groq_api_key=_read(environ, "GROQ_API_KEY"),
        groq_base_url=_read(environ, "GROQ_BASE_URL", DEFAULT_GROQ_BASE_URL),
        groq_model=_read(environ, "GROQ_MODEL"),
        gemini_api_key=_read(environ, "GEMINI_API_KEY"),
        gemini_base_url=_read(environ, "GEMINI_BASE_URL", DEFAULT_GEMINI_BASE_URL),
        gemini_model=_read(environ, "GEMINI_MODEL"),
        ollama_base_url=_read(environ, "OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL),
        ollama_chat_model=_read(environ, "OLLAMA_CHAT_MODEL"),
        embedding_provider=_read_choice(
            environ,
            "EMBEDDING_PROVIDER",
            EMBEDDING_PROVIDERS,
            DEFAULT_EMBEDDING_PROVIDER,
        ),
        embedding_model=_read(environ, "EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL),
        embedding_dimensions=_read_positive_int(
            environ, "EMBEDDING_DIMENSIONS", DEFAULT_EMBEDDING_DIMENSIONS
        ),
        llm_timeout_seconds=_read_positive_float(
            environ, "LLM_TIMEOUT_SECONDS", DEFAULT_LLM_TIMEOUT_SECONDS
        ),
        llm_cooldown_seconds=_read_float(
            environ, "LLM_COOLDOWN_SECONDS", DEFAULT_LLM_COOLDOWN_SECONDS
        ),
        groq_stream_usage=_read_bool(environ, "GROQ_STREAM_USAGE", True),
        gemini_stream_usage=_read_bool(environ, "GEMINI_STREAM_USAGE", True),
        retrieval_min_similarity=_read_unit_float(
            environ, "RETRIEVAL_MIN_SIMILARITY", DEFAULT_RETRIEVAL_MIN_SIMILARITY
        ),
        auth_secret=_read(environ, "AUTH_SECRET"),
        run_max_model_calls=_read_positive_int(
            environ, "RUN_MAX_MODEL_CALLS", DEFAULT_RUN_MAX_MODEL_CALLS
        ),
        run_token_budget=_read_positive_int(
            environ, "RUN_TOKEN_BUDGET", DEFAULT_RUN_TOKEN_BUDGET
        ),
        run_timeout_seconds=_read_positive_float(
            environ, "RUN_TIMEOUT_SECONDS", DEFAULT_RUN_TIMEOUT_SECONDS
        ),
        run_step_timeout_seconds=_read_positive_float(
            environ, "RUN_STEP_TIMEOUT_SECONDS", DEFAULT_RUN_STEP_TIMEOUT_SECONDS
        ),
        token_ttl_seconds=_read_positive_int(
            environ, "TOKEN_TTL_SECONDS", DEFAULT_TOKEN_TTL_SECONDS
        ),
        cors_origins=tuple(
            origin.strip().rstrip("/")
            for origin in _read(environ, "CORS_ORIGINS").split(",")
            if origin.strip()
        ),
        max_ingest_file_bytes=_read_positive_int(
            environ, "MAX_INGEST_FILE_BYTES", DEFAULT_MAX_INGEST_FILE_BYTES
        ),
    )


def load_settings_from_environ() -> Settings:
    """Load the settings from the process environment.

    This is the single entry point for the command line tools, so they never
    read ``os.environ`` themselves.
    """
    return load_settings(os.environ)


def _read(environ: Mapping[str, str], name: str, default: str = "") -> str:
    """One variable; blank counts as unset and falls back to the default."""
    value = environ.get(name, "").strip()
    return value or default


def _read_chain(environ: Mapping[str, str]) -> tuple[str, ...]:
    """The ordered LLM_CHAIN; every name must be a known provider."""
    raw = environ.get("LLM_CHAIN", DEFAULT_LLM_CHAIN)
    if not raw.strip():
        raise ConfigError(
            "LLM_CHAIN is empty; allowed provider names are: "
            + ", ".join(CHAT_PROVIDERS)
        )
    names = [name.strip() for name in raw.split(",")]
    for name in names:
        if name not in CHAT_PROVIDERS:
            raise ConfigError(
                f"unknown provider {name!r} in LLM_CHAIN; allowed provider names are: "
                + ", ".join(CHAT_PROVIDERS)
            )
    return tuple(names)


def _read_choice(
    environ: Mapping[str, str], name: str, allowed: tuple[str, ...], default: str
) -> str:
    """One variable that must hold one of a fixed set of names."""
    value = _read(environ, name, default)
    if value not in allowed:
        raise ConfigError(f"{name} must be one of: " + ", ".join(allowed))
    return value


def _read_positive_int(environ: Mapping[str, str], name: str, default: int) -> int:
    """One variable that must be an integer greater than zero."""
    value = _read(environ, name, str(default))
    try:
        parsed = int(value)
    except ValueError:
        raise ConfigError(f"{name} must be an integer greater than 0") from None
    if parsed <= 0:
        raise ConfigError(f"{name} must be an integer greater than 0")
    return parsed


def _read_positive_float(environ: Mapping[str, str], name: str, default: float) -> float:
    """One variable that must be a number greater than zero."""
    value = _read(environ, name, repr(default))
    try:
        parsed = float(value)
    except ValueError:
        raise ConfigError(f"{name} must be a number greater than 0") from None
    if parsed <= 0:
        raise ConfigError(f"{name} must be a number greater than 0")
    return parsed


def _read_float(environ: Mapping[str, str], name: str, default: float) -> float:
    """One variable that must be a number, any sign."""
    value = _read(environ, name, repr(default))
    try:
        return float(value)
    except ValueError:
        raise ConfigError(f"{name} must be a number") from None


def _read_unit_float(environ: Mapping[str, str], name: str, default: float) -> float:
    """One variable that must be a number between 0 and 1 inclusive."""
    value = _read(environ, name, repr(default))
    try:
        parsed = float(value)
    except ValueError:
        raise ConfigError(f"{name} must be a number between 0 and 1") from None
    if not 0.0 <= parsed <= 1.0:
        raise ConfigError(f"{name} must be a number between 0 and 1")
    return parsed


def _read_bool(environ: Mapping[str, str], name: str, default: bool) -> bool:
    """One flag; blank means the default, anything else must be a known word."""
    value = environ.get(name, "").strip().lower()
    if not value:
        return default
    if value in ("true", "1"):
        return True
    if value in ("false", "0"):
        return False
    raise ConfigError(f"{name} must be true, false, 1 or 0")
