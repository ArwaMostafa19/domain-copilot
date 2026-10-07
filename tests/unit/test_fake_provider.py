"""FakeLLMProvider is deterministic, scripted and fully offline."""

from __future__ import annotations

import math

import pytest

from src.domain.llm import (
    CompletionRequest,
    CompletionResult,
    Message,
    QuotaExceededError,
    TokenUsage,
)
from src.infrastructure.providers.fake import FakeLLMProvider

DIMENSIONS = 768


def request(content: str = "hello") -> CompletionRequest:
    return CompletionRequest(messages=(Message(role="user", content=content),))


def test_a_scripted_string_is_answered_in_order() -> None:
    provider = FakeLLMProvider(script=["first answer", "second answer"])

    assert provider.complete(request()).content == "first answer"
    assert provider.complete(request()).content == "second answer"


def test_an_exhausted_script_fabricates_a_deterministic_answer() -> None:
    provider = FakeLLMProvider(script=["only answer"])
    provider.complete(request())

    result = provider.complete(request("what is the interval"))

    assert result.content == "fake response to: what is the interval"


def test_an_empty_script_fabricates_from_the_last_user_message() -> None:
    provider = FakeLLMProvider()

    result = provider.complete(request("pump pressure"))

    assert result.content == "fake response to: pump pressure"
    assert result.usage.estimated is True


def test_a_scripted_exception_is_raised_before_any_yield() -> None:
    with pytest.raises(QuotaExceededError):
        FakeLLMProvider(script=[QuotaExceededError("fake", "out of quota")]).complete(
            request()
        )
    with pytest.raises(QuotaExceededError):
        list(
            FakeLLMProvider(
                script=[QuotaExceededError("fake", "out of quota")]
            ).stream(request())
        )


def test_a_scripted_completion_result_is_returned_as_is() -> None:
    canned = CompletionResult("canned", (), TokenUsage(1, 1), "fake", "fake")

    assert FakeLLMProvider(script=[canned]).complete(request()) is canned


def test_stream_yields_word_tokens_then_one_done_event() -> None:
    provider = FakeLLMProvider(script=["server reload complete"])

    events = list(provider.stream(request()))

    tokens = [event.text for event in events if event.kind == "token"]
    assert tokens == ["server ", "reload ", "complete"]
    assert "".join(tokens) == "server reload complete"
    done = events[-1]
    assert done.kind == "done"
    assert done.result is not None
    assert done.result.content == "server reload complete"
    assert done.result.usage.estimated is True


def test_calls_record_requests_and_embedding_batches() -> None:
    provider = FakeLLMProvider(script=["answer"])

    provider.complete(request())
    list(provider.stream(request()))
    provider.embed(["x"])

    assert [kind for kind, _ in provider.calls] == ["complete", "stream", "embed"]
    _, batch = provider.calls[2]
    assert batch == ["x"]


def test_embeddings_are_deterministic() -> None:
    provider = FakeLLMProvider()

    first = provider.embed(["same text", "other text"])
    second = provider.embed(["same text", "other text"])

    assert first == second


def test_embeddings_have_the_configured_dimension_and_unit_norm() -> None:
    provider = FakeLLMProvider()
    assert provider.embedding_dimensions == DIMENSIONS

    vectors = provider.embed(["pump overhaul", "conveyor belt"]).vectors

    assert len(vectors) == 2
    for vector in vectors:
        assert len(vector) == DIMENSIONS
        assert all(-1.0 <= value <= 1.0 for value in vector)
        norm = math.sqrt(sum(value * value for value in vector))
        assert norm == pytest.approx(1.0)
    assert provider.embedding_model == "fake-embedding"


def test_different_texts_get_different_vectors() -> None:
    provider = FakeLLMProvider()

    left, right = provider.embed(["first text", "second text"]).vectors

    assert left != right