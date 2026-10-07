"""OpenAICompatibleProvider talks HTTP through an injectable mock transport."""

from __future__ import annotations

import json
import logging

import httpx
import pytest

from src.domain.llm import (
    CompletionRequest,
    ConfigError,
    Message,
    ProviderAuthError,
    ProviderError,
    ProviderRequestError,
    ProviderResponseError,
    ProviderUnavailableError,
    QuotaExceededError,
    TokenUsage,
    ToolCall,
    ToolSpec,
)
from src.infrastructure.providers.openai_compatible import OpenAICompatibleProvider

BASE_URL = "https://hosted.test/v1"
API_KEY = "test-key-not-a-real-secret"
MODEL = "test-chat-model"
EMBEDDING_MODEL = "test-embedding-model"


def make_provider(handler, **kwargs) -> OpenAICompatibleProvider:
    """A hosted provider whose requests are answered by ``handler``."""
    kwargs.setdefault("name", "hosted")
    kwargs.setdefault("base_url", BASE_URL)
    kwargs.setdefault("api_key", API_KEY)
    kwargs.setdefault("model", MODEL)
    kwargs.setdefault("timeout", 5.0)
    client = httpx.Client(base_url=BASE_URL, transport=httpx.MockTransport(handler))
    return OpenAICompatibleProvider(client=client, **kwargs)


def payload_of(request: httpx.Request) -> dict:
    return json.loads(request.read())


def user_request(content: str = "hi", **extra) -> CompletionRequest:
    return CompletionRequest(messages=(Message(role="user", content=content),), **extra)


def completion_body(content, **extra) -> dict:
    body = {
        "model": "response-model",
        "choices": [
            {
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 3, "completion_tokens": 2},
    }
    body.update(extra)
    return body


def tool_body(tool_calls: list) -> dict:
    return {
        "model": "response-model",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": tool_calls,
                },
                "finish_reason": "tool_calls",
            }
        ],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1},
    }


def sse(*chunks: dict) -> str:
    lines = ["data: " + json.dumps(chunk) for chunk in chunks]
    lines.append("data: [DONE]")
    return "\n".join(lines) + "\n"


def run_stream(handler, **kwargs) -> list:
    return list(make_provider(handler, **kwargs).stream(user_request()))


def done_result(events):
    done = [event for event in events if event.kind == "done"]
    assert len(done) == 1
    assert done[0].result is not None
    return done[0].result


def test_complete_reads_content_usage_model_and_finish_reason() -> None:
    result = make_provider(
        lambda request: httpx.Response(200, json=completion_body("hello"))
    ).complete(user_request())

    assert result.content == "hello"
    assert result.usage == TokenUsage(prompt_tokens=3, completion_tokens=2)
    assert result.provider == "hosted"
    assert result.model == "response-model"
    assert result.finish_reason == "stop"


def test_complete_treats_null_content_as_empty() -> None:
    result = make_provider(
        lambda request: httpx.Response(200, json=completion_body(None))
    ).complete(user_request())

    assert result.content == ""


def test_complete_sends_the_expected_payload() -> None:
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers.get("authorization")
        seen["path"] = request.url.path
        seen["body"] = payload_of(request)
        return httpx.Response(200, json=completion_body("ok"))

    tool = ToolSpec("get_time", "Return the current time", {"type": "object"})
    make_provider(handler).complete(
        CompletionRequest(
            messages=(Message(role="user", content="hi"),),
            tools=(tool,),
            temperature=0.2,
            max_tokens=50,
        )
    )

    assert seen["auth"] == f"Bearer {API_KEY}"
    assert seen["path"] == "/v1/chat/completions"
    assert seen["body"]["model"] == MODEL
    assert seen["body"]["temperature"] == 0.2
    assert seen["body"]["max_tokens"] == 50
    assert seen["body"]["tools"] == [
        {
            "type": "function",
            "function": {
                "name": "get_time",
                "description": "Return the current time",
                "parameters": {"type": "object"},
            },
        }
    ]


def test_complete_omits_tools_max_tokens_and_stream_when_unset() -> None:
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["body"] = payload_of(request)
        return httpx.Response(200, json=completion_body("ok"))

    make_provider(handler).complete(user_request())

    assert "tools" not in seen["body"]
    assert "max_tokens" not in seen["body"]
    assert "stream" not in seen["body"]


def test_complete_maps_every_message_role() -> None:
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["body"] = payload_of(request)
        return httpx.Response(200, json=completion_body("ok"))

    request = CompletionRequest(
        messages=(
            Message(role="system", content="be helpful"),
            Message(
                role="assistant",
                content="previous",
                tool_calls=(ToolCall("call_1", "do_it", {"x": 1}),),
            ),
            Message(role="tool", content="result", tool_call_id="call_1"),
            Message(role="user", content="now"),
        )
    )
    make_provider(handler).complete(request)

    assert seen["body"]["messages"] == [
        {"role": "system", "content": "be helpful"},
        {
            "role": "assistant",
            "content": "previous",
            "tool_calls": [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "do_it",
                        "arguments": json.dumps({"x": 1}),
                    },
                }
            ],
        },
        {"role": "tool", "tool_call_id": "call_1", "content": "result"},
        {"role": "user", "content": "now"},
    ]


def test_complete_parses_tool_calls_with_argument_strings() -> None:
    calls = [
        {
            "id": "abc",
            "type": "function",
            "function": {"name": "get_time", "arguments": '{"timezone": "Cairo"}'},
        },
        {
            "id": "",
            "type": "function",
            "function": {"name": "noop", "arguments": ""},
        },
    ]
    result = make_provider(
        lambda request: httpx.Response(200, json=tool_body(calls))
    ).complete(user_request())

    assert result.tool_calls[0] == ToolCall("abc", "get_time", {"timezone": "Cairo"})
    assert result.tool_calls[1] == ToolCall("call_1", "noop", {})


def test_complete_generates_missing_tool_call_ids() -> None:
    calls = [
        {"type": "function", "function": {"name": "a", "arguments": "{}"}},
        {"id": "", "type": "function", "function": {"name": "b", "arguments": "{}"}},
    ]
    result = make_provider(
        lambda request: httpx.Response(200, json=tool_body(calls))
    ).complete(user_request())

    assert [call.id for call in result.tool_calls] == ["call_0", "call_1"]


def test_complete_rejects_invalid_tool_arguments() -> None:
    calls = [
        {"id": "x", "type": "function", "function": {"name": "bad", "arguments": "not json"}}
    ]
    with pytest.raises(ProviderResponseError):
        make_provider(
            lambda request: httpx.Response(200, json=tool_body(calls))
        ).complete(user_request())


def test_complete_rejects_arguments_that_are_not_an_object() -> None:
    calls = [
        {"id": "x", "type": "function", "function": {"name": "bad", "arguments": "[1, 2]"}}
    ]
    with pytest.raises(ProviderResponseError):
        make_provider(
            lambda request: httpx.Response(200, json=tool_body(calls))
        ).complete(user_request())


def test_complete_estimates_usage_when_the_body_reports_none() -> None:
    body = completion_body("hello")
    del body["usage"]

    result = make_provider(
        lambda request: httpx.Response(200, json=body)
    ).complete(user_request())

    assert result.usage.estimated is True
    assert result.usage.prompt_tokens > 0


def test_complete_rejects_a_body_without_choices() -> None:
    with pytest.raises(ProviderResponseError):
        make_provider(
            lambda request: httpx.Response(
                200, json={"model": "response-model", "choices": []}
            )
        ).complete(user_request())


def test_complete_rejects_a_non_json_body() -> None:
    with pytest.raises(ProviderResponseError):
        make_provider(
            lambda request: httpx.Response(200, text="<html>not json</html>")
        ).complete(user_request())


@pytest.mark.parametrize(
    "status, expected",
    [
        (429, QuotaExceededError),
        (401, ProviderAuthError),
        (403, ProviderAuthError),
        (408, ProviderUnavailableError),
        (500, ProviderUnavailableError),
        (503, ProviderUnavailableError),
        (400, ProviderRequestError),
        (404, ProviderRequestError),
    ],
)
def test_error_statuses_map_to_the_right_provider_error(status, expected) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json={"error": {"message": "boom"}})

    with pytest.raises(expected):
        make_provider(handler).complete(user_request())


def test_an_error_body_that_is_a_list_is_read() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json=[{"error": {"message": "list message"}}])

    with pytest.raises(ProviderRequestError, match="list message"):
        make_provider(handler).complete(user_request())


def test_a_non_json_error_body_is_read_as_text_and_cut_to_200_characters() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="E" * 500)

    with pytest.raises(ProviderUnavailableError) as excinfo:
        make_provider(handler).complete(user_request())

    message = str(excinfo.value)
    assert "500" in message
    assert "E" * 200 in message
    assert "E" * 201 not in message


def test_a_timeout_maps_to_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out")

    with pytest.raises(ProviderUnavailableError):
        make_provider(handler).complete(user_request())


def test_a_transport_error_maps_to_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    with pytest.raises(ProviderUnavailableError):
        make_provider(handler).complete(user_request())


def test_stream_yields_tokens_and_one_done_event_with_usage() -> None:
    chunks = [
        {"model": "response-model", "choices": [{"delta": {"content": "Hel"}}]},
        {"choices": [{"delta": {"content": "lo"}, "finish_reason": "stop"}]},
        {
            "choices": [],
            "usage": {"prompt_tokens": 4, "completion_tokens": 2},
        },
    ]

    events = run_stream(lambda request: httpx.Response(200, text=sse(*chunks)))
    result = done_result(events)

    assert [event.text for event in events if event.kind == "token"] == ["Hel", "lo"]
    assert result.content == "Hello"
    assert result.usage == TokenUsage(prompt_tokens=4, completion_tokens=2)
    assert result.model == "response-model"


def test_stream_reads_usage_under_x_groq() -> None:
    chunks = [
        {"choices": [{"delta": {"content": "hi"}, "finish_reason": "stop"}]},
        {
            "choices": [],
            "x_groq": {"usage": {"prompt_tokens": 5, "completion_tokens": 1}},
        },
    ]

    result = done_result(run_stream(lambda request: httpx.Response(200, text=sse(*chunks))))

    assert result.usage == TokenUsage(prompt_tokens=5, completion_tokens=1)


def test_stream_estimates_usage_when_it_never_arrives() -> None:
    chunks = [{"choices": [{"delta": {"content": "hi"}, "finish_reason": "stop"}]}]

    result = done_result(run_stream(lambda request: httpx.Response(200, text=sse(*chunks))))

    assert result.usage.estimated is True


def test_stream_assembles_fragmented_tool_calls_per_index() -> None:
    chunks = [
        {
            "choices": [
                {
                    "delta": {
                        "tool_calls": [
                            {
                                "index": 0,
                                "id": "call_abc",
                                "function": {"name": "get_time", "arguments": '{"time'},
                            }
                        ]
                    },
                    "finish_reason": None,
                }
            ]
        },
        {
            "choices": [
                {
                    "delta": {
                        "tool_calls": [
                            {"index": 0, "function": {"arguments": 'zone": "Cairo"}'}}
                        ]
                    },
                    "finish_reason": "tool_calls",
                }
            ]
        },
        {"choices": [], "usage": {"prompt_tokens": 1, "completion_tokens": 1}},
    ]

    result = done_result(run_stream(lambda request: httpx.Response(200, text=sse(*chunks))))

    assert result.tool_calls == (ToolCall("call_abc", "get_time", {"timezone": "Cairo"}),)


def test_stream_sends_stream_options_when_enabled() -> None:
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["body"] = payload_of(request)
        return httpx.Response(
            200,
            text=sse({"choices": [{"delta": {"content": "x"}, "finish_reason": "stop"}]}),
        )

    run_stream(handler)

    assert seen["body"]["stream"] is True
    assert seen["body"]["stream_options"] == {"include_usage": True}


def test_stream_omits_stream_options_when_disabled() -> None:
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["body"] = payload_of(request)
        return httpx.Response(
            200,
            text=sse({"choices": [{"delta": {"content": "x"}, "finish_reason": "stop"}]}),
        )

    run_stream(handler, stream_usage_option=False)

    assert "stream_options" not in seen["body"]


def test_stream_checks_the_status_before_the_first_event() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="boom")

    stream = make_provider(handler).stream(user_request())

    with pytest.raises(ProviderUnavailableError):
        next(stream)


def test_stream_rejects_a_malformed_chunk() -> None:
    with pytest.raises(ProviderResponseError):
        run_stream(lambda request: httpx.Response(200, text="data: not json\n"))


def test_embed_sorts_by_index_and_reads_usage() -> None:
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        seen["body"] = payload_of(request)
        return httpx.Response(
            200,
            json={
                "data": [
                    {"index": 1, "embedding": [3.0, 4.0]},
                    {"index": 0, "embedding": [1.0, 2.0]},
                ],
                "usage": {"prompt_tokens": 7},
            },
        )

    provider = make_provider(handler, model=None, embedding_model=EMBEDDING_MODEL)
    result = provider.embed(["a", "b"])

    assert seen["path"] == "/v1/embeddings"
    assert seen["body"] == {"model": EMBEDDING_MODEL, "input": ["a", "b"]}
    assert result.vectors == ((1.0, 2.0), (3.0, 4.0))
    assert result.dimensions == 2
    assert result.model == EMBEDDING_MODEL
    assert result.usage == TokenUsage(prompt_tokens=7, completion_tokens=0)
    assert result.provider == "hosted"


def test_embed_without_an_embedding_model_is_a_request_error() -> None:
    with pytest.raises(ProviderRequestError, match="embeddings are not configured"):
        make_provider(lambda request: httpx.Response(200, json={})).embed(["a"])


def test_embed_empty_input_makes_no_request() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("no request should be made for empty input")

    provider = make_provider(handler, model=None, embedding_model=EMBEDDING_MODEL)
    result = provider.embed([])

    assert result.vectors == ()
    assert result.usage.total_tokens == 0


def test_a_provider_without_a_chat_model_cannot_complete_or_stream() -> None:
    provider = make_provider(
        lambda request: httpx.Response(200, json={}),
        model=None,
        embedding_model=EMBEDDING_MODEL,
    )

    with pytest.raises(ConfigError, match="chat model is not set"):
        provider.complete(user_request())
    with pytest.raises(ConfigError, match="chat model is not set"):
        list(provider.stream(user_request()))


def test_a_trailing_slash_in_the_base_url_is_stripped() -> None:
    provider = make_provider(
        lambda request: httpx.Response(200, json={}), base_url=BASE_URL + "/"
    )

    assert provider.base_url == BASE_URL


def test_repr_shows_the_provider_but_never_the_key() -> None:
    provider = make_provider(lambda request: httpx.Response(200, json={}))

    text = repr(provider)

    assert "hosted" in text
    assert BASE_URL in text
    assert MODEL in text
    assert API_KEY not in text


def test_the_key_never_leaks_into_errors_or_logs(caplog) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    provider = make_provider(handler)

    with caplog.at_level(logging.DEBUG), pytest.raises(ProviderError) as excinfo:
        provider.complete(user_request())

    assert API_KEY not in str(excinfo.value)
    assert API_KEY not in repr(provider)
    assert all(API_KEY not in record.getMessage() for record in caplog.records)
