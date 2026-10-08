"""load_settings checks syntax only; build_chain checks the needed variables."""

from __future__ import annotations

import pytest

from src.domain.llm import ConfigError, EmbeddingSpec
from src.infrastructure.config import load_settings
from src.infrastructure.providers.factory import build_chain


def test_defaults_when_nothing_is_set() -> None:
    settings = load_settings({})

    assert settings.llm_chain == ("groq", "gemini", "ollama")
    assert settings.embedding_provider == "ollama"
    assert settings.embedding_model == "nomic-embed-text"
    assert settings.embedding_dimensions == 768
    assert settings.llm_timeout_seconds == 180.0
    assert settings.llm_cooldown_seconds == 60.0
    assert settings.groq_base_url == "https://api.groq.com/openai/v1"
    assert settings.gemini_base_url == (
        "https://generativelanguage.googleapis.com/v1beta/openai"
    )
    assert settings.ollama_base_url == "http://localhost:11434"


def test_loading_settings_never_requires_a_key_or_model() -> None:
    settings = load_settings({"LLM_CHAIN": "groq,gemini,ollama"})

    assert settings.groq_api_key == ""
    assert settings.gemini_api_key == ""
    assert settings.ollama_chat_model == ""
    assert settings.groq_model == ""
    assert settings.gemini_model == ""


def test_the_chain_keeps_the_configured_order() -> None:
    settings = load_settings({"LLM_CHAIN": "fake,ollama,groq"})

    assert settings.llm_chain == ("fake", "ollama", "groq")


def test_an_unknown_provider_name_is_rejected_and_lists_the_allowed_names() -> None:
    with pytest.raises(ConfigError) as excinfo:
        load_settings({"LLM_CHAIN": "openai,ollama"})

    message = str(excinfo.value)
    assert "openai" in message
    for name in ("groq", "gemini", "ollama", "fake"):
        assert name in message


def test_an_empty_chain_is_rejected() -> None:
    with pytest.raises(ConfigError, match="LLM_CHAIN is empty"):
        load_settings({"LLM_CHAIN": ""})
    with pytest.raises(ConfigError, match="LLM_CHAIN is empty"):
        load_settings({"LLM_CHAIN": "   "})


def test_invalid_numbers_are_rejected() -> None:
    with pytest.raises(ConfigError, match="EMBEDDING_DIMENSIONS"):
        load_settings({"EMBEDDING_DIMENSIONS": "wide"})
    with pytest.raises(ConfigError, match="EMBEDDING_DIMENSIONS"):
        load_settings({"EMBEDDING_DIMENSIONS": "-3"})
    with pytest.raises(ConfigError, match="EMBEDDING_DIMENSIONS"):
        load_settings({"EMBEDDING_DIMENSIONS": "0"})
    with pytest.raises(ConfigError, match="LLM_TIMEOUT_SECONDS"):
        load_settings({"LLM_TIMEOUT_SECONDS": "fast"})
    with pytest.raises(ConfigError, match="LLM_TIMEOUT_SECONDS"):
        load_settings({"LLM_TIMEOUT_SECONDS": "0"})


def test_an_unknown_embedding_provider_is_rejected() -> None:
    with pytest.raises(ConfigError, match="EMBEDDING_PROVIDER"):
        load_settings({"EMBEDDING_PROVIDER": "openai"})


def test_repr_never_contains_an_api_key_value() -> None:
    settings = load_settings({"GROQ_API_KEY": "sk-very-secret-1234"})

    text = repr(settings)
    assert "sk-very-secret-1234" not in text
    assert "groq_api_key='***'" in text


def test_repr_shows_that_an_empty_key_is_empty() -> None:
    text = repr(load_settings({}))

    assert "groq_api_key=''" in text
    assert "gemini_api_key=''" in text


def test_embedding_spec_returns_the_configured_model_and_size() -> None:
    settings = load_settings({"EMBEDDING_MODEL": "bge-m3", "EMBEDDING_DIMENSIONS": "1024"})

    assert settings.embedding_spec() == EmbeddingSpec("bge-m3", 1024)


def test_a_missing_key_is_named_by_variable_but_no_value_is_leaked() -> None:
    env = {
        "LLM_CHAIN": "groq,fake",
        "GROQ_MODEL": "llama-3.3-70b-versatile",
        "GEMINI_API_KEY": "another-secret-5678",
        "EMBEDDING_PROVIDER": "fake",
    }
    settings = load_settings(env)

    with pytest.raises(ConfigError) as excinfo:
        build_chain(settings)

    message = str(excinfo.value)
    assert "GROQ_API_KEY" in message
    assert "llama-3.3-70b-versatile" not in message
    assert "another-secret-5678" not in message


def test_stream_usage_flags_default_to_true_and_accept_words() -> None:
    assert load_settings({}).groq_stream_usage is True
    assert load_settings({}).gemini_stream_usage is True
    assert load_settings({"GROQ_STREAM_USAGE": "false"}).groq_stream_usage is False
    assert load_settings({"GEMINI_STREAM_USAGE": "0"}).gemini_stream_usage is False
    assert load_settings({"GROQ_STREAM_USAGE": "TRUE"}).groq_stream_usage is True
    assert load_settings({"GEMINI_STREAM_USAGE": "1"}).gemini_stream_usage is True
    assert load_settings({"GROQ_STREAM_USAGE": ""}).groq_stream_usage is True


def test_an_invalid_stream_usage_flag_is_rejected() -> None:
    with pytest.raises(ConfigError, match="GROQ_STREAM_USAGE"):
        load_settings({"GROQ_STREAM_USAGE": "maybe"})
    with pytest.raises(ConfigError, match="GEMINI_STREAM_USAGE"):
        load_settings({"GEMINI_STREAM_USAGE": "yes"})
