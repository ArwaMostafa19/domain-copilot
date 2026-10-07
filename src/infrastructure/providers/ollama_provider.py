"""HTTP client for Ollama: embeddings, chat completions and streaming."""

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
    ProviderRequestError,
    ProviderResponseError,
    ProviderUnavailableError,
    StreamEvent,
    TokenUsage,
    ToolCall,
    ToolSpec,
    estimate_usage,
)
from src.infrastructure.config import CONNECT_TIMEOUT_SECONDS

DEFAULT_TIMEOUT = 120.0
DEFAULT_BATCH_SIZE = 16
BODY_SNIPPET_LENGTH = 200
CHAT_ENDPOINT = "/api/chat"
EMBED_ENDPOINT = "/api/embed"


class OllamaProvider:
    """Talks to one Ollama server through ``/api/embed`` and ``/api/chat``."""

    def __init__(
        self,
        base_url: str,
        embedding_model: str,
        embedding_dimensions: int,
        chat_model: str | None = None,
        *,
        name: str = "ollama",
        timeout: float = DEFAULT_TIMEOUT,
        client: httpx.Client | None = None,
        embed_batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.embedding_model = embedding_model
        self.embedding_dimensions = embedding_dimensions
        self.chat_model = chat_model
        self.timeout = timeout
        self.embed_batch_size = embed_batch_size
        self._client = client

    def embed(self, texts: Sequence[str]) -> EmbeddingResult:
        """Embed every text, in batches, in the order the texts were given."""
        if not texts:
            return EmbeddingResult(
                vectors=(),
                model=self.embedding_model,
                dimensions=self.embedding_dimensions,
                usage=TokenUsage(),
                provider=self.name,
            )
        vectors: list[tuple[float, ...]] = []
        prompt_tokens = 0
        estimated = False
        with self._open_client() as client:
            for start in range(0, len(texts), self.embed_batch_size):
                batch = list(texts[start : start + self.embed_batch_size])
                response = self._post(
                    client,
                    EMBED_ENDPOINT,
                    {"model": self.embedding_model, "input": batch},
                    unreachable=f"Ollama is not reachable at {self.base_url}",
                )
                self._raise_for_status(response, self.embedding_model)
                body = self._read_object(response.text)
                embeddings = self._read_embeddings(body, len(batch))
                vectors.extend(
                    self._read_vector(vector, index)
                    for index, vector in enumerate(embeddings)
                )
                count = body.get("prompt_eval_count")
                if isinstance(count, int):
                    prompt_tokens += count
                else:
                    estimated = True
        return EmbeddingResult(
            vectors=tuple(vectors),
            model=self.embedding_model,
            dimensions=self.embedding_dimensions,
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=0,
                estimated=estimated,
            ),
            provider=self.name,
        )

    def complete(self, request: CompletionRequest) -> CompletionResult:
        """Answer one request in a single non-streaming HTTP call."""
        payload = self._chat_payload(request, stream=False)
        with self._open_client() as client:
            response = self._post(
                client,
                CHAT_ENDPOINT,
                payload,
                unreachable=self._unreachable_hint(),
            )
            self._raise_for_status(response, payload["model"])
            body = self._read_object(response.text)
        content, tool_calls = self._read_message(body)
        return CompletionResult(
            content=content,
            tool_calls=tool_calls,
            usage=self._read_usage(body, request, content),
            provider=self.name,
            model=payload["model"],
            finish_reason=self._read_finish_reason(body),
        )

    def stream(self, request: CompletionRequest) -> Iterator[StreamEvent]:
        """Answer one request token by token, then finish with one done event."""
        payload = self._chat_payload(request, stream=True)
        parts: list[str] = []
        functions: list[tuple[str, dict[str, Any]]] = []
        usage: TokenUsage | None = None
        finish_reason = "stop"
        with self._open_client() as client:
            try:
                with client.stream(
                    "POST",
                    f"{self.base_url}{CHAT_ENDPOINT}",
                    json=payload,
                    timeout=self._timeout(),
                ) as response:
                    if response.status_code != 200:
                        response.read()
                        self._raise_for_status(response, payload["model"])
                    for line in response.iter_lines():
                        line = line.strip()
                        if not line:
                            continue
                        body = self._read_object(line)
                        message = body.get("message")
                        if isinstance(message, dict):
                            content = message.get("content")
                            if isinstance(content, str) and content:
                                parts.append(content)
                                yield StreamEvent(kind="token", text=content)
                            functions.extend(
                                self._read_functions(message.get("tool_calls"))
                            )
                        if body.get("done") is True:
                            prompt = body.get("prompt_eval_count")
                            completion = body.get("eval_count")
                            if isinstance(prompt, int) and isinstance(completion, int):
                                usage = TokenUsage(
                                    prompt_tokens=prompt,
                                    completion_tokens=completion,
                                    estimated=False,
                                )
                            reason = body.get("done_reason")
                            if isinstance(reason, str) and reason:
                                finish_reason = reason
            except httpx.HTTPError as error:
                raise ProviderUnavailableError(
                    self.name, self._unreachable_hint()
                ) from error
        content = "".join(parts)
        if usage is None:
            usage = estimate_usage(request.prompt_text(), content)
        result = CompletionResult(
            content=content,
            tool_calls=tuple(
                ToolCall(id=f"call_{index}", name=name, arguments=arguments)
                for index, (name, arguments) in enumerate(functions)
            ),
            usage=usage,
            provider=self.name,
            model=payload["model"],
            finish_reason=finish_reason,
        )
        yield StreamEvent(kind="done", result=result)

    def _chat_payload(self, request: CompletionRequest, stream: bool) -> dict[str, Any]:
        """The JSON body Ollama expects for one chat request."""
        payload: dict[str, Any] = {
            "model": self._require_chat_model(),
            "messages": [self._to_ollama_message(m) for m in request.messages],
            "stream": stream,
        }
        if request.tools:
            payload["tools"] = [self._to_ollama_tool(tool) for tool in request.tools]
        options: dict[str, Any] = {"temperature": request.temperature}
        if request.max_tokens is not None:
            options["num_predict"] = request.max_tokens
        payload["options"] = options
        return payload

    def _require_chat_model(self) -> str:
        if not self.chat_model:
            raise ConfigError("OLLAMA_CHAT_MODEL is not set")
        return self.chat_model

    @staticmethod
    def _to_ollama_message(message: Message) -> dict[str, Any]:
        if message.role == "tool":
            return {"role": "tool", "content": message.content}
        payload: dict[str, Any] = {"role": message.role, "content": message.content}
        if message.tool_calls:
            payload["tool_calls"] = [
                {"function": {"name": call.name, "arguments": dict(call.arguments)}}
                for call in message.tool_calls
            ]
        return payload

    @staticmethod
    def _to_ollama_tool(tool: ToolSpec) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            },
        }

    def _read_message(self, body: dict[str, Any]) -> tuple[str, tuple[ToolCall, ...]]:
        message = body.get("message")
        if not isinstance(message, dict):
            raise ProviderResponseError(
                self.name,
                f"Ollama at {self.base_url} returned a malformed response: "
                "the body holds no message object",
            )
        content = message.get("content", "")
        if not isinstance(content, str):
            raise ProviderResponseError(
                self.name,
                f"Ollama at {self.base_url} returned a malformed response: "
                "the message content is not text",
            )
        return content, tuple(
            ToolCall(id=f"call_{index}", name=name, arguments=arguments)
            for index, (name, arguments) in enumerate(
                self._read_functions(message.get("tool_calls"))
            )
        )

    def _read_functions(self, raw: Any) -> list[tuple[str, dict[str, Any]]]:
        """The (name, arguments) of every tool call Ollama reported."""
        if raw is None:
            return []
        if not isinstance(raw, list):
            raise ProviderResponseError(
                self.name,
                f"Ollama at {self.base_url} returned a malformed response: "
                "tool_calls is not a list",
            )
        functions: list[tuple[str, dict[str, Any]]] = []
        for index, item in enumerate(raw):
            function = item.get("function") if isinstance(item, dict) else None
            name = function.get("name") if isinstance(function, dict) else None
            arguments = function.get("arguments") if isinstance(function, dict) else None
            if not isinstance(name, str) or not isinstance(arguments, dict):
                raise ProviderResponseError(
                    self.name,
                    f"Ollama at {self.base_url} returned a malformed response: "
                    f"tool call {index} is not a function with a name and "
                    "a dictionary of arguments",
                )
            functions.append((name, dict(arguments)))
        return functions

    @staticmethod
    def _read_usage(
        body: dict[str, Any], request: CompletionRequest, content: str
    ) -> TokenUsage:
        prompt = body.get("prompt_eval_count")
        completion = body.get("eval_count")
        if isinstance(prompt, int) and isinstance(completion, int):
            return TokenUsage(
                prompt_tokens=prompt, completion_tokens=completion, estimated=False
            )
        return estimate_usage(request.prompt_text(), content)

    @staticmethod
    def _read_finish_reason(body: dict[str, Any]) -> str:
        reason = body.get("done_reason")
        return reason if isinstance(reason, str) and reason else "stop"

    def _read_object(self, raw: str) -> dict[str, Any]:
        try:
            payload = json.loads(raw)
        except ValueError as error:
            raise ProviderResponseError(
                self.name,
                f"Ollama at {self.base_url} returned a malformed response: {error}",
            ) from error
        if not isinstance(payload, dict):
            raise ProviderResponseError(
                self.name,
                f"Ollama at {self.base_url} returned a malformed response: "
                "the body is not a JSON object",
            )
        return payload

    def _read_embeddings(self, body: dict[str, Any], expected: int) -> list[Any]:
        embeddings = body.get("embeddings")
        if not isinstance(embeddings, list) or len(embeddings) != expected:
            found = len(embeddings) if isinstance(embeddings, list) else "no"
            raise ProviderResponseError(
                self.name,
                f"Ollama at {self.base_url} returned a malformed response: "
                f"{found} embeddings for {expected} texts",
            )
        return embeddings

    def _read_vector(self, vector: Any, index: int) -> tuple[float, ...]:
        if not isinstance(vector, list) or len(vector) != self.embedding_dimensions:
            size = len(vector) if isinstance(vector, list) else "a non-list value"
            raise ProviderResponseError(
                self.name,
                f"Ollama at {self.base_url} returned {size} values for text "
                f"{index}, expected {self.embedding_dimensions}",
            )
        try:
            return tuple(float(value) for value in vector)
        except (TypeError, ValueError) as error:
            raise ProviderResponseError(
                self.name,
                f"Ollama at {self.base_url} returned a malformed response: {error}",
            ) from error

    def _raise_for_status(self, response: httpx.Response, model: str) -> None:
        """Map a non-2xx Ollama answer to the ProviderError subclass it means."""
        status = response.status_code
        if 200 <= status < 300:
            return
        detail = (
            f"Ollama at {self.base_url} returned HTTP {status}: "
            f"{response.text[:BODY_SNIPPET_LENGTH]}"
        )
        if status == 404:
            raise ProviderUnavailableError(
                self.name, f"{detail}; run: ollama pull {model}"
            )
        if status >= 500:
            raise ProviderUnavailableError(self.name, detail)
        raise ProviderRequestError(self.name, detail)

    def _post(
        self,
        client: httpx.Client,
        path: str,
        payload: dict[str, Any],
        *,
        unreachable: str,
    ) -> httpx.Response:
        try:
            return client.post(
                f"{self.base_url}{path}",
                json=payload,
                timeout=self._timeout(),
            )
        except httpx.HTTPError as error:
            raise ProviderUnavailableError(self.name, unreachable) from error

    def _unreachable_hint(self) -> str:
        return (
            f"could not reach Ollama at {self.base_url}; "
            f"is Ollama running at {self.base_url}?"
        )

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
