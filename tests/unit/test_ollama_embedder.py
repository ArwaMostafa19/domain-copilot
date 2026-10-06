"""The Ollama embedder talks HTTP through an injectable mock transport."""

from __future__ import annotations

import json

import httpx
import pytest

from src.application.ports import ProviderError
from src.infrastructure.providers.ollama_embedder import OllamaEmbedder

BASE_URL = "http://ollama.test"
DIMENSION = 768


def make_embedder(handler, **kwargs) -> OllamaEmbedder:
    """An embedder whose requests are answered by ``handler``."""
    kwargs.setdefault("base_url", BASE_URL)
    return OllamaEmbedder(transport=httpx.MockTransport(handler), **kwargs)


def payload_of(request: httpx.Request) -> dict:
    """The decoded JSON body of one embed request."""
    return json.loads(request.read())


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

    embedder = make_embedder(handler, batch_size=16)
    texts = [f"text number {index}" for index in range(35)]

    vectors = embedder.embed(texts)

    assert [len(batch) for batch in batches] == [16, 16, 3]
    assert [text for batch in batches for text in batch] == texts
    assert paths == ["/api/embed", "/api/embed", "/api/embed"]
    assert models == [embedder.model_name] * 3
    assert len(vectors) == 35
    assert all(len(vector) == DIMENSION for vector in vectors)


def test_a_vector_with_the_wrong_dimension_is_rejected() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        body = payload_of(request)
        embeddings = [[0.0] * 4 for _ in body["input"]]
        return httpx.Response(200, json={"embeddings": embeddings})

    with pytest.raises(ProviderError, match="expected 768"):
        make_embedder(handler).embed(["one text"])


def test_a_500_answer_reports_status_and_a_200_character_body_snippet() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="E" * 500)

    with pytest.raises(ProviderError) as excinfo:
        make_embedder(handler).embed(["one text"])

    message = str(excinfo.value)
    assert "500" in message
    assert "E" * 200 in message
    assert "E" * 201 not in message


def test_a_connection_error_names_the_base_url() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    with pytest.raises(
        ProviderError, match="Ollama is not reachable at http://ollama.test"
    ):
        make_embedder(handler).embed(["one text"])


def test_empty_input_makes_no_request() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("no request should be made for empty input")

    assert make_embedder(handler).embed([]) == []


def test_a_response_without_embeddings_is_rejected() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"result": []})

    with pytest.raises(ProviderError, match="malformed"):
        make_embedder(handler).embed(["one text"])


def test_the_wrong_number_of_embeddings_is_rejected() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        embeddings = [[0.0] * DIMENSION, [0.0] * DIMENSION]
        return httpx.Response(200, json={"embeddings": embeddings})

    with pytest.raises(ProviderError, match="malformed"):
        make_embedder(handler).embed(["one text"])
