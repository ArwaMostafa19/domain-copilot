"""The smoke tool runs offline against the fake provider and a mock Ollama."""

from __future__ import annotations

import httpx
import pytest

from src.infrastructure.llm_smoke import main


def ollama_client(content: str = "from ollama") -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        body = {
            "message": {"role": "assistant", "content": content},
            "done": True,
            "done_reason": "stop",
            "prompt_eval_count": 3,
            "eval_count": 2,
        }
        return httpx.Response(200, json=body)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_stream_with_the_fake_provider_returns_zero(capsys) -> None:
    code = main(["--provider", "fake", "--stream"], environ={}, client=None)

    out = capsys.readouterr().out
    assert code == 0
    assert "provider: fake" in out


def test_fail_replaces_a_provider_and_the_chain_falls_back(capsys) -> None:
    env = {
        "LLM_CHAIN": "fake,ollama",
        "OLLAMA_BASE_URL": "http://ollama.test",
        "OLLAMA_CHAT_MODEL": "llama3",
        "EMBEDDING_PROVIDER": "ollama",
    }

    code = main(["--fail", "fake"], environ=env, client=ollama_client())

    out = capsys.readouterr().out
    assert code == 0
    assert "simulated failure of fake" in out
    assert "provider: ollama" in out


def test_a_missing_groq_key_returns_two_and_names_the_variable(capsys) -> None:
    env = {"LLM_CHAIN": "groq", "GROQ_MODEL": "some-private-model-name"}

    code = main([], environ=env, client=None)

    out = capsys.readouterr().out
    assert code == 2
    assert "GROQ_API_KEY" in out
    assert "some-private-model-name" not in out


def test_help_works_without_any_environment(capsys) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--help"], environ={}, client=None)

    assert excinfo.value.code == 0
