"""OllamaProvider talks HTTP through an injectable mock transport."""

from __future__ import annotations

import json

import httpx
import pytest

from src.domain.llm import (
    CompletionRequest,
    ConfigError,
    Message,
    ProviderError,
    ProviderRequestError,
    ProviderResponseError,
    ProviderUnavailableError,
    TokenUsage,
    ToolCall,
    ToolSpec,
)
from src.infrastructure.providers.ollama_provider import OllamaProvider

BASE_URL = "http://ollama.test"
EMBEDDING_MODEL = "nomic-embed-text"
CHAT_MODEL = "llama3"
DIMENSION = 768


def make_provider(handler, **kwargs) -> OllamaProvider:
    """A provider whose requests are answered by ``handler``."""
    kwargs.setdefault("embedding_model", EMBEDDING_MODEL)
    kwargs.setdefault("embedding_dimensions", DIMENSION)
    client = httpx.Client(base_url=BASE_URL, transport=httpx.MockTransport(handler))
    return OllamaProvider(base_url=BASE_URL, client=client, **kwargs)


def make_chat_provider(handler, **kwargs) -> OllamaProvider:
    """A chat-capable provider whose requests are answered by ``handler``."""
    kwargs.setdefault("chat_model", CHAT_MODEL)
    return make_provider(handler, **kwargs)


def payload_of(request: httpx.Request) -> dict:
    """The decoded JSON body of one request."""
    return json.loads(request.read())


def answer(message: dict, **extra) -> dict:
    """One valid /api/chat body around a message."""
    body = {"message": message, "done": True, "done_reason": "stop"}
    body.update(extra)
    return body


def user_request(**extra) -> CompletionRequest:
    """A tiny user request, open to extra keyword arguments."""
    return CompletionRequest(messages=(Message(role="user", content="hi"),), **extra)


def test_thirty_five_texts_are_posted_in_three_batches() -> None:
    batches: list[list[str]] = []
    models: list[str] = []
    paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = payload_of(request)
        batches.append(body["input"])
        models.append(body["model"])
        paths.append(request.url.path)
        embeddings = [[0.0] * DIMENSION for _ in body["input"]]
        return httpx.Response(200, json={"embeddings": embeddings})

    provider = make_provider(handler, embed_batch_size=16)
    texts = [f"text number {index}" for index in range(35)]

    result = provider.embed(texts)

    vectors = list(result.vectors)
    assert [len(batch) for batch in batches] == [16, 16, 3]
    assert [text for batch in batches for text in batch] == texts
    assert paths == ["/api/embed", "/api/embed", "/api/embed"]
    assert models == [EMBEDDING_MODEL] * 3
    assert len(vectors) == 35
    assert all(len(vector) == DIMENSION for vector in vectors)
    assert result.model == EMBEDDING_MODEL
    assert result.dimensions == DIMENSION
    assert result.provider == "ollama"


def test_a_vector_with_the_wrong_dimension_is_rejected() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        body = payload_of(request)
        embeddings = [[0.0] * 4 for _ in body["input"]]
        return httpx.Response(200, json={"embeddings": embeddings})

    with pytest.raises(ProviderError, match="expected 768") as excinfo:
        make_provider(handler).embed(["one text"])
    assert isinstance(excinfo.value, ProviderResponseError)


def test_a_500_answer_reports_status_and_a_200_character_body_snippet() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="E" * 500)

    with pytest.raises(ProviderError) as excinfo:
        make_provider(handler).embed(["one text"])

    message = str(excinfo.value)
    assert "500" in message
    assert "E" * 200 in message
    assert "E" * 201 not in message
    assert isinstance(excinfo.value, ProviderUnavailableError)


def test_a_connection_error_names_the_base_url() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    with pytest.raises(
        ProviderError, match="Ollama is not reachable at http://ollama.test"
    ) as excinfo:
        make_provider(handler).embed(["one text"])
    assert isinstance(excinfo.value, ProviderUnavailableError)


def test_empty_input_makes_no_request() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("no request should be made for empty input")

    result = make_provider(handler).embed([])
    assert result.vectors == ()
    assert result.usage.total_tokens == 0


def test_a_response_without_embeddings_is_rejected() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"result": []})

    with pytest.raises(ProviderError, match="malformed"):
        make_provider(handler).embed(["one text"])


def test_the_wrong_number_of_embeddings_is_rejected() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        embeddings = [[0.0] * DIMENSION, [0.0] * DIMENSION]
        return httpx.Response(200, json={"embeddings": embeddings})

    with pytest.raises(ProviderError, match="malformed"):
        make_provider(handler).embed(["one text"])


def test_usage_is_summed_over_the_batches() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        body = payload_of(request)
        embeddings = [[0.0] * DIMENSION for _ in body["input"]]
        return httpx.Response(
            200, json={"embeddings": embeddings, "prompt_eval_count": 7}
        )

    provider = make_provider(handler, embed_batch_size=2)
    result = provider.embed(["a", "b", "c"])
    assert result.usage.prompt_tokens == 14
    assert result.usage.estimated is False


def test_usage_is_estimated_when_prompt_eval_count_is_absent() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        body = payload_of(request)
        embeddings = [[0.0] * DIMENSION for _ in body["input"]]
        return httpx.Response(200, json={"embeddings": embeddings})

    provider = make_provider(handler)
    result = provider.embed(["a"])
    assert result.usage.estimated is True
    assert result.usage.prompt_tokens == 0


def test_complete_sends_tools_and_parses_the_answer() -> None:
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["body"] = payload_of(request)
        return httpx.Response(
            200,
            json=answer(
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "get_interval",
                                "arguments": {"equipment": "pump"},
                            }
                        },
                        {
                            "function": {
                                "name": "get_pressure",
                                "arguments": {"equipment": "pump"},
                            }
                        },
                    ],
                },
                done_reason="tool_calls",
                prompt_eval_count=12,
                eval_count=5,
            ),
        )

    tool = ToolSpec(
        "get_interval",
        "Return the service interval of a piece of equipment",
        {"type": "object"},
    )
    result = make_chat_provider(handler).complete(
        CompletionRequest(
            messages=(Message(role="user", content="interval of pump?"),),
            tools=(tool,),
            temperature=0.2,
            max_tokens=120,
        )
    )

    body = seen["body"]
    assert body["model"] == CHAT_MODEL
    assert body["stream"] is False
    assert body["tools"] == [
        {
            "type": "function",
            "function": {
                "name": "get_interval",
                "description": "Return the service interval of a piece of equipment",
                "parameters": {"type": "object"},
            },
        }
    ]
    assert body["options"] == {"temperature": 0.2, "num_predict": 120}
    assert [call.name for call in result.tool_calls] == [
        "get_interval",
        "get_pressure",
    ]
    assert [call.id for call in result.tool_calls] == ["call_0", "call_1"]
    assert result.tool_calls[0].arguments == {"equipment": "pump"}
    assert result.usage == TokenUsage(prompt_tokens=12, completion_tokens=5)
    assert result.finish_reason == "tool_calls"
    assert result.provider == "ollama"
    assert result.model == CHAT_MODEL


def test_incoming_assistant_tool_calls_and_tool_messages_are_rebuilt() -> None:
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["body"] = payload_of(request)
        return httpx.Response(200, json=answer({"role": "assistant", "content": "ok"}))

    request = CompletionRequest(
        messages=(
            Message(role="system", content="be helpful"),
            Message(
                role="assistant",
                content="previous step",
                tool_calls=(ToolCall("call_0", "do_something", {"x": 1}),),
            ),
            Message(role="tool", content="the tool result", tool_call_id="call_0"),
            Message(role="user", content="now what"),
        )
    )
    make_chat_provider(handler).complete(request)

    body = seen["body"]
    assert body["messages"] == [
        {"role": "system", "content": "be helpful"},
        {
            "role": "assistant",
            "content": "previous step",
            "tool_calls": [
                {"function": {"name": "do_something", "arguments": {"x": 1}}}
            ],
        },
        {"role": "tool", "content": "the tool result"},
        {"role": "user", "content": "now what"},
    ]


def test_complete_estimates_usage_when_the_model_reports_none() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=answer({"role": "assistant", "content": "ok"}))

    result = make_chat_provider(handler).complete(user_request())
    assert result.usage.estimated is True
    assert result.content == "ok"


def test_complete_without_a_chat_model_is_a_config_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=answer({"role": "assistant", "content": "ok"}))

    provider = make_provider(handler)
    with pytest.raises(ConfigError, match="OLLAMA_CHAT_MODEL is not set"):
        provider.complete(user_request())
    with pytest.raises(ConfigError, match="OLLAMA_CHAT_MODEL is not set"):
        list(provider.stream(user_request()))


def test_stream_yields_tokens_then_one_done_event_with_usage() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        body = payload_of(request)
        assert body["stream"] is True
        assert body["model"] == CHAT_MODEL
        lines = [
            '{"message":{"role":"assistant","content":"Hello"},"done":false}',
            '{"message":{"role":"assistant","content":" world"},"done":false}',
            (
                '{"message":{"role":"assistant","content":"",'
                '"tool_calls":[{"function":{"name":"get_interval",'
                '"arguments":{"equipment":"pump"}}}]},"done":true,'
                '"done_reason":"tool_calls","prompt_eval_count":20,"eval_count":9}'
            ),
        ]
        return httpx.Response(200, content=("\n".join(lines)).encode())

    provider = make_chat_provider(handler)
    events = list(provider.stream(user_request()))

    tokens = [event.text for event in events if event.kind == "token"]
    assert tokens == ["Hello", " world"]
    done = events[-1]
    assert done.kind == "done"
    assert done.result is not None
    assert done.result.content == "Hello world"
    assert done.result.tool_calls == (
        ToolCall("call_0", "get_interval", {"equipment": "pump"}),
    )
    assert done.result.usage == TokenUsage(prompt_tokens=20, completion_tokens=9)
    assert done.result.finish_reason == "tool_calls"
    assert done.result.provider == "ollama"
    assert done.result.model == CHAT_MODEL


def test_stream_estimates_usage_when_the_done_line_reports_none() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        lines = [
            '{"message":{"role":"assistant","content":"hello"},"done":false}',
            '{"message":{"role":"assistant","content":" there"},"done":true}',
        ]
        return httpx.Response(200, content=("\n".join(lines)).encode())

    events = list(make_chat_provider(handler).stream(user_request()))
    done = events[-1]
    assert done.result is not None
    assert done.result.content == "hello there"
    assert done.result.usage.estimated is True


def test_a_404_is_unavailable_with_the_pull_hint() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, text="model not found")

    with pytest.raises(ProviderError, match="ollama pull llama3") as excinfo:
        make_chat_provider(handler).complete(user_request())
    assert isinstance(excinfo.value, ProviderUnavailableError)


def test_a_chat_connection_error_hints_the_base_url() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    with pytest.raises(
        ProviderError, match="is Ollama running at http://ollama.test"
    ) as excinfo:
        make_chat_provider(handler).complete(user_request())
    assert isinstance(excinfo.value, ProviderUnavailableError)


def test_a_bad_request_is_a_provider_request_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, text="bad request body")

    with pytest.raises(ProviderError) as excinfo:
        make_chat_provider(handler).complete(user_request())
    assert isinstance(excinfo.value, ProviderRequestError)


def test_the_status_is_checked_before_the_first_stream_event() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="boom")

    stream = make_chat_provider(handler).stream(user_request())
    with pytest.raises(ProviderUnavailableError):
        next(stream)