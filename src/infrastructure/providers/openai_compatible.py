"""Hosted chat and embedding providers that speak the OpenAI HTTP protocol.

Groq and Gemini both expose an OpenAI-compatible API, so one adapter covers
both. Only ``httpx`` is used: no vendor SDK is imported anywhere.
"""

from __future__ import annotations

import json
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from typing import Any

import httpx

from src.domain.llm import (
    CompletionRequest,
    CompletionResult,
    ConfigError,
    EmbeddingResult,
    Message,
    ProviderAuthError,
    ProviderError,
    ProviderRequestError,
    ProviderResponseError,
    ProviderUnavailableError,
    QuotaExceededError,
    StreamEvent,
    TokenUsage,
    ToolCall,
    ToolSpec,
    estimate_usage,
)
from src.infrastructure.config import CONNECT_TIMEOUT_SECONDS

CHAT_ENDPOINT = "/chat/completions"
EMBED_ENDPOINT = "/embeddings"
BODY_SNIPPET_LENGTH = 200
DATA_PREFIX = "data:"
STREAM_DONE = "[DONE]"


class OpenAICompatibleProvider:
    """One hosted provider, reached through its OpenAI-compatible endpoints."""

    def __init__(
        self,
        name: str,
        base_url: str,
        api_key: str,
        model: str | None,
        *,
        embedding_model: str | None = None,
        timeout: float,
        client: httpx.Client | None = None,
        stream_usage_option: bool = True,
    ) -> None:
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.embedding_model = embedding_model
        self.timeout = timeout
        self.stream_usage_option = stream_usage_option
        self._api_key = api_key
        self._client = client

    def __repr__(self) -> str:
        """Show what this provider is, but never the API key."""
        return (
            f"OpenAICompatibleProvider(name={self.name!r}, "
            f"base_url={self.base_url!r}, model={self.model!r})"
        )

    def complete(self, request: CompletionRequest) -> CompletionResult:
        """Answer one request in a single non-streaming HTTP call."""
        model = self._require_model()
        payload = self._chat_payload(request, model, stream=False)
        with self._open_client() as client:
            try:
                response = client.post(
                    f"{self.base_url}{CHAT_ENDPOINT}",
                    json=payload,
                    headers=self._headers(request.correlation_id),
                    timeout=self._timeout(),
                )
            except httpx.TransportError as error:
                raise self._provider_error(error, None) from error
            if not 200 <= response.status_code < 300:
                raise self._provider_error(None, response)
            body = self._read_object(response.text)
        return self._completion_result(body, request, model)

    def stream(self, request: CompletionRequest) -> Iterator[StreamEvent]:
        """Answer one request token by token, then finish with one done event."""
        model = self._require_model()
        payload = self._chat_payload(request, model, stream=True)
        parts: list[str] = []
        fragments: dict[int, dict[str, str]] = {}
        usage: TokenUsage | None = None
        finish_reason = "stop"
        response_model = model
        with self._open_client() as client:
            try:
                with client.stream(
                    "POST",
                    f"{self.base_url}{CHAT_ENDPOINT}",
                    json=payload,
                    headers=self._headers(request.correlation_id),
                    timeout=self._timeout(),
                ) as response:
                    if not 200 <= response.status_code < 300:
                        response.read()
                        raise self._provider_error(None, response)
                    for line in response.iter_lines():
                        stripped = line.strip()
                        if not stripped or stripped.startswith(":"):
                            continue
                        if not stripped.startswith(DATA_PREFIX):
                            continue
                        data = stripped[len(DATA_PREFIX):].strip()
                        if data == STREAM_DONE:
                            break
                        chunk = self._read_chunk(data)
                        response_model = self._chunk_model(chunk, response_model)
                        yield from self._consume_chunk(chunk, parts, fragments)
                        reason = self._chunk_finish_reason(chunk)
                        if reason is not None:
                            finish_reason = reason
                        found = self._chunk_usage(chunk)
                        if found is not None:
                            usage = found
            except httpx.TransportError as error:
                raise self._provider_error(error, None) from error
        content = "".join(parts)
        if usage is None:
            usage = estimate_usage(request.prompt_text(), content)
        result = CompletionResult(
            content=content,
            tool_calls=self._finalise_tool_calls(fragments),
            usage=usage,
            provider=self.name,
            model=response_model,
            finish_reason=finish_reason,
        )
        yield StreamEvent(kind="done", result=result)

    def embed(self, texts: Sequence[str]) -> EmbeddingResult:
        """Embed every text, in the order the texts were given."""
        if self.embedding_model is None:
            raise ProviderRequestError(
                self.name, "embeddings are not configured for this provider"
            )
        if not texts:
            return EmbeddingResult(
                vectors=(),
                model=self.embedding_model,
                dimensions=0,
                usage=TokenUsage(),
                provider=self.name,
            )
        batch = list(texts)
        payload = {"model": self.embedding_model, "input": batch}
        with self._open_client() as client:
            try:
                response = client.post(
                    f"{self.base_url}{EMBED_ENDPOINT}",
                    json=payload,
                    headers=self._headers(),
                    timeout=self._timeout(),
                )
            except httpx.TransportError as error:
                raise self._provider_error(error, None) from error
            if not 200 <= response.status_code < 300:
                raise self._provider_error(None, response)
            body = self._read_object(response.text)
        vectors = self._read_vectors(body)
        return EmbeddingResult(
            vectors=vectors,
            model=self.embedding_model,
            dimensions=len(vectors[0]) if vectors else 0,
            usage=self._embedding_usage(body, batch),
            provider=self.name,
        )

    def healthcheck(self) -> bool:
        with self._open_client() as client:
            try:
                response = client.get(
                    f"{self.base_url}/models",
                    headers=self._headers(),
                    timeout=httpx.Timeout(min(self.timeout, 5.0), connect=CONNECT_TIMEOUT_SECONDS),
                )
            except httpx.TransportError:
                return False
        return 200 <= response.status_code < 300

    def _chat_payload(
        self, request: CompletionRequest, model: str, *, stream: bool
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "messages": [self._to_message(message) for message in request.messages],
            "temperature": request.temperature,
        }
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.tools:
            payload["tools"] = [self._to_tool(tool) for tool in request.tools]
        if stream:
            payload["stream"] = True
            if self.stream_usage_option:
                payload["stream_options"] = {"include_usage": True}
        return payload

    def _require_model(self) -> str:
        if not self.model:
            raise ConfigError(f"{self.name} chat model is not set")
        return self.model

    @staticmethod
    def _to_message(message: Message) -> dict[str, Any]:
        if message.role == "tool":
            return {
                "role": "tool",
                "tool_call_id": message.tool_call_id,
                "content": message.content,
            }
        payload: dict[str, Any] = {"role": message.role, "content": message.content}
        if message.tool_calls:
            payload["tool_calls"] = [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.name,
                        "arguments": json.dumps(call.arguments),
                    },
                }
                for call in message.tool_calls
            ]
        return payload

    @staticmethod
    def _to_tool(tool: ToolSpec) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            },
        }

    def _completion_result(
        self, body: dict[str, Any], request: CompletionRequest, model: str
    ) -> CompletionResult:
        choices = body.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ProviderResponseError(
                self.name, f"{self.name} returned a response with no choices"
            )
        first = choices[0]
        message = first.get("message") if isinstance(first, dict) else None
        if not isinstance(message, dict):
            raise ProviderResponseError(
                self.name, f"{self.name} returned a choice with no message object"
            )
        content = message.get("content")
        if content is None:
            content = ""
        if not isinstance(content, str):
            raise ProviderResponseError(
                self.name, f"{self.name} returned message content that is not text"
            )
        reason = first.get("finish_reason") if isinstance(first, dict) else None
        return CompletionResult(
            content=content,
            tool_calls=self._parse_tool_calls(message.get("tool_calls")),
            usage=self._read_usage(body.get("usage"), request, content),
            provider=self.name,
            model=self._response_model(body, model),
            finish_reason=reason if isinstance(reason, str) and reason else "stop",
        )

    def _read_usage(
        self, usage: Any, request: CompletionRequest, content: str
    ) -> TokenUsage:
        if isinstance(usage, dict):
            prompt = usage.get("prompt_tokens")
            completion = usage.get("completion_tokens")
            if isinstance(prompt, int) and isinstance(completion, int):
                return TokenUsage(
                    prompt_tokens=prompt,
                    completion_tokens=completion,
                    estimated=False,
                )
        return estimate_usage(request.prompt_text(), content)

    def _parse_tool_calls(self, raw: Any) -> tuple[ToolCall, ...]:
        if raw is None:
            return ()
        if not isinstance(raw, list):
            raise ProviderResponseError(
                self.name, f"{self.name} returned tool_calls that are not a list"
            )
        calls: list[ToolCall] = []
        for index, item in enumerate(raw):
            function = item.get("function") if isinstance(item, dict) else None
            name = function.get("name") if isinstance(function, dict) else None
            if not isinstance(name, str) or not name:
                raise ProviderResponseError(
                    self.name, f"{self.name} returned tool call {index} without a name"
                )
            arguments = function.get("arguments") if isinstance(function, dict) else None
            call_id = item.get("id") if isinstance(item, dict) else None
            calls.append(
                ToolCall(
                    id=call_id if isinstance(call_id, str) and call_id else f"call_{index}",
                    name=name,
                    arguments=self._parse_arguments(arguments),
                )
            )
        return tuple(calls)

    def _parse_arguments(self, raw: Any) -> dict[str, Any]:
        if raw is None or raw == "":
            return {}
        if not isinstance(raw, str):
            raise ProviderResponseError(
                self.name, f"{self.name} returned tool arguments that are not text"
            )
        try:
            parsed = json.loads(raw)
        except ValueError as error:
            raise ProviderResponseError(
                self.name, f"{self.name} returned invalid tool arguments: {error}"
            ) from error
        if not isinstance(parsed, dict):
            raise ProviderResponseError(
                self.name, f"{self.name} returned tool arguments that are not a JSON object"
            )
        return parsed

    def _accumulate_fragments(
        self, raw: Any, fragments: dict[int, dict[str, str]]
    ) -> None:
        if raw is None:
            return
        if not isinstance(raw, list):
            raise ProviderResponseError(
                self.name, f"{self.name} sent tool_calls that are not a list"
            )
        for item in raw:
            function = item.get("function") if isinstance(item, dict) else None
            index = item.get("index") if isinstance(item, dict) else None
            if not isinstance(index, int):
                index = 0
            entry = fragments.setdefault(index, {"id": "", "name": "", "arguments": ""})
            call_id = item.get("id") if isinstance(item, dict) else None
            if isinstance(call_id, str) and call_id:
                entry["id"] = call_id
            if isinstance(function, dict):
                name = function.get("name")
                if isinstance(name, str) and name:
                    entry["name"] = name
                arguments = function.get("arguments")
                if isinstance(arguments, str):
                    entry["arguments"] += arguments

    def _finalise_tool_calls(
        self, fragments: dict[int, dict[str, str]]
    ) -> tuple[ToolCall, ...]:
        calls: list[ToolCall] = []
        for index in sorted(fragments):
            entry = fragments[index]
            if not entry["name"]:
                raise ProviderResponseError(
                    self.name, f"{self.name} sent a tool call without a name"
                )
            calls.append(
                ToolCall(
                    id=entry["id"] or f"call_{index}",
                    name=entry["name"],
                    arguments=self._parse_arguments(entry["arguments"]),
                )
            )
        return tuple(calls)

    def _read_vectors(self, body: dict[str, Any]) -> tuple[tuple[float, ...], ...]:
        data = body.get("data")
        if not isinstance(data, list) or not data:
            raise ProviderResponseError(
                self.name, f"{self.name} returned no embeddings"
            )
        ordered = sorted(data, key=self._data_index)
        vectors: list[tuple[float, ...]] = []
        for item in ordered:
            embedding = item.get("embedding") if isinstance(item, dict) else None
            if not isinstance(embedding, list) or not embedding:
                raise ProviderResponseError(
                    self.name, f"{self.name} returned an embedding that is not a list"
                )
            try:
                vectors.append(tuple(float(value) for value in embedding))
            except (TypeError, ValueError) as error:
                raise ProviderResponseError(
                    self.name, f"{self.name} returned a malformed embedding: {error}"
                ) from error
        return tuple(vectors)

    @staticmethod
    def _data_index(item: Any) -> int:
        if isinstance(item, dict) and isinstance(item.get("index"), int):
            return item["index"]
        return 0

    def _embedding_usage(
        self, body: dict[str, Any], texts: list[str]
    ) -> TokenUsage:
        usage = body.get("usage")
        if isinstance(usage, dict) and isinstance(usage.get("prompt_tokens"), int):
            return TokenUsage(
                prompt_tokens=usage["prompt_tokens"],
                completion_tokens=0,
                estimated=False,
            )
        estimated = estimate_usage("\n".join(texts), "")
        return TokenUsage(
            prompt_tokens=estimated.prompt_tokens,
            completion_tokens=0,
            estimated=True,
        )

    def _consume_chunk(
        self,
        chunk: dict[str, Any],
        parts: list[str],
        fragments: dict[int, dict[str, str]],
    ) -> Iterator[StreamEvent]:
        choices = chunk.get("choices")
        if not isinstance(choices, list) or not choices:
            return
        first = choices[0]
        if not isinstance(first, dict):
            return
        delta = first.get("delta")
        if isinstance(delta, dict):
            content = delta.get("content")
            if isinstance(content, str) and content:
                parts.append(content)
                yield StreamEvent(kind="token", text=content)
            self._accumulate_fragments(delta.get("tool_calls"), fragments)

    @staticmethod
    def _chunk_finish_reason(chunk: dict[str, Any]) -> str | None:
        choices = chunk.get("choices")
        if not isinstance(choices, list) or not choices:
            return None
        first = choices[0]
        reason = first.get("finish_reason") if isinstance(first, dict) else None
        return reason if isinstance(reason, str) and reason else None

    @staticmethod
    def _chunk_model(chunk: dict[str, Any], fallback: str) -> str:
        model = chunk.get("model")
        return model if isinstance(model, str) and model else fallback

    def _chunk_usage(self, chunk: dict[str, Any]) -> TokenUsage | None:
        usage = chunk.get("usage")
        if usage is None:
            groq = chunk.get("x_groq")
            if isinstance(groq, dict):
                usage = groq.get("usage")
        if not isinstance(usage, dict):
            return None
        prompt = usage.get("prompt_tokens")
        completion = usage.get("completion_tokens")
        if isinstance(prompt, int) and isinstance(completion, int):
            return TokenUsage(
                prompt_tokens=prompt,
                completion_tokens=completion,
                estimated=False,
            )
        return None

    @staticmethod
    def _response_model(body: dict[str, Any], fallback: str) -> str:
        model = body.get("model")
        return model if isinstance(model, str) and model else fallback

    def _read_object(self, raw: str) -> dict[str, Any]:
        try:
            payload = json.loads(raw)
        except ValueError as error:
            raise ProviderResponseError(
                self.name, f"{self.name} returned a body that is not valid JSON"
            ) from error
        if not isinstance(payload, dict):
            raise ProviderResponseError(
                self.name, f"{self.name} returned a body that is not a JSON object"
            )
        return payload

    def _read_chunk(self, data: str) -> dict[str, Any]:
        try:
            payload = json.loads(data)
        except ValueError as error:
            raise ProviderResponseError(
                self.name, f"{self.name} sent a stream chunk that is not valid JSON"
            ) from error
        if not isinstance(payload, dict):
            raise ProviderResponseError(
                self.name, f"{self.name} sent a stream chunk that is not a JSON object"
            )
        return payload

    def _provider_error(
        self, error: httpx.TransportError | None, response: httpx.Response | None
    ) -> ProviderError:
        """Map one transport failure or error response to a ProviderError.

        The message carries the provider name, the HTTP status when there is
        one, and at most the first 200 characters of the error text. Headers,
        the request body and the API key are never included.
        """
        if error is not None:
            return ProviderUnavailableError(
                self.name, f"{self.name} could not be reached ({type(error).__name__})"
            )
        status = response.status_code
        detail = (
            f"{self.name} returned HTTP {status}: {self._error_snippet(response)}"
        )
        if status == 429:
            return QuotaExceededError(self.name, detail)
        if status in (401, 403):
            return ProviderAuthError(self.name, detail)
        # A 404 from a hosted model API commonly means that the configured
        # model is retired or unavailable to this account. The fallback chain
        # can still answer with another provider, so treat it as unavailable.
        if status in (404, 408) or status >= 500:
            return ProviderUnavailableError(self.name, detail)
        return ProviderRequestError(self.name, detail)

    def _error_snippet(self, response: httpx.Response) -> str:
        message = self._message_from_body(response)
        if message is None:
            message = response.text
        return message[:BODY_SNIPPET_LENGTH]

    @staticmethod
    def _message_from_body(response: httpx.Response) -> str | None:
        """The error message inside a JSON body, or None when there is none."""
        try:
            payload = response.json()
        except ValueError:
            return None
        candidate = payload
        if isinstance(candidate, list) and candidate:
            candidate = candidate[0]
        if isinstance(candidate, dict):
            error = candidate.get("error")
            if isinstance(error, dict) and isinstance(error.get("message"), str):
                return error["message"]
            if isinstance(error, str):
                return error
        return None

    def _headers(self, correlation_id: str | None = None) -> dict[str, str]:
        headers = {"Authorization": f"Bearer {self._api_key}"}
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id
        return headers

    def _timeout(self) -> httpx.Timeout:
        return httpx.Timeout(self.timeout, connect=CONNECT_TIMEOUT_SECONDS)

    @contextmanager
    def _open_client(self) -> Iterator[httpx.Client]:
        """Use the injected client when there is one, else build one per call."""
        if self._client is not None:
            yield self._client
            return
        with httpx.Client(timeout=self._timeout()) as client:
            yield client
