from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

from src.domain.documents import DomainError

Role = Literal["system", "user", "assistant", "tool"]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any]


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class Message:
    role: Role
    content: str = ""
    tool_calls: tuple[ToolCall, ...] = ()
    tool_call_id: str | None = None


@dataclass(frozen=True)
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated: bool = False

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass(frozen=True)
class CompletionRequest:
    messages: tuple[Message, ...]
    tools: tuple[ToolSpec, ...] = ()
    temperature: float = 0.0
    max_tokens: int | None = None
    correlation_id: str | None = None

    def prompt_text(self) -> str:
        return "\n".join(m.content for m in self.messages)


@dataclass(frozen=True)
class CompletionResult:
    content: str
    tool_calls: tuple[ToolCall, ...]
    usage: TokenUsage
    provider: str
    model: str
    finish_reason: str = "stop"


@dataclass(frozen=True)
class StreamEvent:
    """kind="token" carries text; kind="done" carries the final result (usage, tool calls)."""

    kind: Literal["token", "done"]
    text: str = ""
    result: CompletionResult | None = None


@dataclass(frozen=True)
class EmbeddingSpec:
    model: str
    dimensions: int


@dataclass(frozen=True)
class EmbeddingResult:
    vectors: tuple[tuple[float, ...], ...]
    model: str
    dimensions: int
    usage: TokenUsage
    provider: str


def estimate_tokens(text: str) -> int:
    """Rough fallback (~4 chars per token) for providers that report no usage."""
    return max(1, len(text) // 4) if text else 0


def estimate_usage(prompt_text: str, completion_text: str) -> TokenUsage:
    return TokenUsage(
        prompt_tokens=estimate_tokens(prompt_text),
        completion_tokens=estimate_tokens(completion_text),
        estimated=True,
    )


class LLMError(DomainError):
    """Base class for every error raised by the LLM layer."""


class ProviderError(LLMError):

    fallback_allowed: bool = True

    def __init__(self, provider: str, message: str) -> None:
        super().__init__(f"[{provider}] {message}")
        self.provider = provider


class ProviderUnavailableError(ProviderError):
    """Network failure, timeout or 5xx."""


class QuotaExceededError(ProviderError):
    """HTTP 429 or an exhausted free tier."""


class ProviderAuthError(ProviderError):
    """Missing or rejected API key (401/403)."""


class ProviderResponseError(ProviderError):
    """The provider answered, but the payload is malformed (e.g. invalid tool arguments)."""


class ProviderRequestError(ProviderError):
    """Our request is wrong (4xx). The next provider would fail the same way."""

    fallback_allowed = False


class AllProvidersFailedError(LLMError):
    def __init__(self, failures: Sequence[ProviderError]) -> None:
        summary = "; ".join(str(f) for f in failures) or "no provider configured"
        super().__init__(f"all providers failed: {summary}")
        self.failures = tuple(failures)


class EmbeddingModelMismatchError(LLMError):
    """The embedding model in use differs from the one the index was built with."""


class ConfigError(LLMError):
    """Invalid or missing LLM configuration."""
