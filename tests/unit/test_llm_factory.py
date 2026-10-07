"""The factory builds the chain and the embedding stack from configuration only."""

from __future__ import annotations

import sys
from pathlib import Path

import httpx
import pytest

from src.domain.llm import (
    CompletionRequest,
    ConfigError,
    Message,
)
from src.infrastructure.config import load_settings
from src.infrastructure.providers.factory import (
    build_chain,
    build_embedding_stack,
    build_providers,
)

TESTS_ROOT = Path(__file__).resolve().parents[1]
if str(TESTS_ROOT) not in sys.path:
    sys.path.insert(0, str(TESTS_ROOT))

from fakes import InMemoryEmbeddingIndexRegistry

OLLAMA_BASE_URL = "http://ollama.test"


def settings(**overrides):
    """One Settings snapshot with ollama and fake configured by default."""
    env = {
        "LLM_CHAIN": "ollama,fake",
        "OLLAMA_BASE_URL": OLLAMA_BASE_URL,
        "OLLAMA_CHAT_MODEL": "llama3",
        "EMBEDDING_PROVIDER": "fake",
        "EMBEDDING_MODEL": "nomic-embed-text",
        "EMBEDDING_DIMENSIONS": "768",
    }
    env.update(overrides)
    return load_settings(env)


def request(content: str = "what is the interval") -> CompletionRequest:
    return CompletionRequest(messages=(Message(role="user", content=content),))


def answering_client(content: str = "from ollama") -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        body = {
            "message": {"role": "assistant", "content": content},
            "done": True,
            "done_reason": "stop",
            "prompt_eval_count": 3,
            "eval_count": 2,
        }
        return httpx.Response(200, json=body)

    return httpx.Client(base_url=OLLAMA_BASE_URL, transport=httpx.MockTransport(handler))


def failing_client() -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    return httpx.Client(base_url=OLLAMA_BASE_URL, transport=httpx.MockTransport(handler))


def openai_answering_client(content: str = "from hosted") -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        body = {
            "model": "hosted-model",
            "choices": [
                {
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 2, "completion_tokens": 1},
        }
        return httpx.Response(200, json=body)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_the_chain_keeps_the_configured_order() -> None:
    ollama_first = build_chain(settings(), client=answering_client())
    assert ollama_first.complete(request()).provider == "ollama"

    fake_first = build_chain(settings(LLM_CHAIN="fake,ollama"), client=answering_client())
    fake_result = fake_first.complete(request("who are you"))
    assert fake_result.provider == "fake"
    assert fake_result.content == "fake response to: who are you"


def test_the_chain_falls_back_to_the_next_provider() -> None:
    chain = build_chain(settings(), client=failing_client())

    result = chain.complete(request("pump interval"))

    assert result.provider == "fake"
    assert result.content == "fake response to: pump interval"


def test_the_embedder_is_chosen_by_embedding_provider_not_by_the_chain() -> None:
    chain = build_chain(
        settings(LLM_CHAIN="ollama", EMBEDDING_PROVIDER="fake",
                 EMBEDDING_MODEL="bge-m3", EMBEDDING_DIMENSIONS="1024"),
        client=answering_client(),
    )

    result = chain.embed(["a text"])

    assert result.model == "bge-m3"
    assert result.dimensions == 1024
    assert result.provider == "fake"


def test_build_providers_builds_the_chain_and_the_embedder() -> None:
    providers = build_providers(settings(), client=answering_client())

    assert set(providers) == {"ollama", "fake"}


def test_a_missing_groq_api_key_names_the_variable_before_anything_else() -> None:
    built = settings(LLM_CHAIN="groq,fake", GROQ_MODEL="llama-3.3-70b-versatile")

    with pytest.raises(ConfigError) as excinfo:
        build_chain(built)

    message = str(excinfo.value)
    assert "GROQ_API_KEY" in message
    assert "not implemented" not in message


def test_groq_and_gemini_are_built_in_the_configured_order() -> None:
    built = settings(
        LLM_CHAIN="gemini,groq,fake",
        GEMINI_API_KEY="ai-fake",
        GEMINI_MODEL="gemini-2.0-flash",
        GROQ_API_KEY="gsk-fake",
        GROQ_MODEL="llama-3.3-70b-versatile",
    )

    chain = build_chain(built, client=openai_answering_client())

    result = chain.complete(request("hello"))

    assert result.provider == "gemini"
    assert result.content == "from hosted"
    assert result.model == "hosted-model"


def test_a_missing_gemini_model_names_the_variable() -> None:
    built = settings(LLM_CHAIN="gemini,fake", GEMINI_API_KEY="ai-fake")

    with pytest.raises(ConfigError) as excinfo:
        build_chain(built)

    assert "GEMINI_MODEL" in str(excinfo.value)


def test_gemini_embeddings_are_built_without_a_chat_model() -> None:
    built = settings(
        LLM_CHAIN="fake", EMBEDDING_PROVIDER="gemini", GEMINI_API_KEY="ai-fake"
    )

    provider, _guard = build_embedding_stack(built, InMemoryEmbeddingIndexRegistry())

    assert provider.name == "gemini"


def test_the_same_business_code_runs_under_two_configurations() -> None:
    def ask(env: dict, client: httpx.Client | None) -> str:
        chain = build_chain(settings(**env), client=client)
        return chain.complete(request()).provider

    with_ollama = ask({"LLM_CHAIN": "ollama,fake"}, answering_client())
    fake_only = ask({"LLM_CHAIN": "fake"}, None)

    assert with_ollama == "ollama"
    assert fake_only == "fake"