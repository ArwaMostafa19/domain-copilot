import pytest

from src.application.llm_router import FallbackChain
from src.domain.llm import (
    AllProvidersFailedError,
    CompletionRequest,
    CompletionResult,
    EmbeddingResult,
    Message,
    ProviderRequestError,
    ProviderUnavailableError,
    QuotaExceededError,
    StreamEvent,
    TokenUsage,
)


def _req() -> CompletionRequest:
    return CompletionRequest(messages=(Message(role="user", content="hi"),))


def _ok(provider: str) -> CompletionResult:
    return CompletionResult("ok", (), TokenUsage(1, 1), provider=provider, model="m")


class Stub:
    def __init__(self, name, *, error=None):
        self.name, self.error, self.calls = name, error, 0

    def complete(self, request):
        self.calls += 1
        if self.error:
            raise self.error
        return _ok(self.name)

    def stream(self, request):
        self.calls += 1
        if self.error:
            raise self.error
        yield StreamEvent(kind="token", text="a")
        yield StreamEvent(kind="token", text="b")
        yield StreamEvent(kind="done", result=_ok(self.name))

    def embed(self, texts):
        self.calls += 1
        if self.error:
            raise self.error
        vectors = tuple((0.0, 0.0, 0.0) for _ in texts)
        return EmbeddingResult(vectors, "m", 3, TokenUsage(1, 0), self.name)


class DropsMidStream(Stub):
    def stream(self, request):
        self.calls += 1
        yield StreamEvent(kind="token", text="a")
        raise ProviderUnavailableError(self.name, "connection dropped")


def _chain(*providers, embedder=None, **kw):
    return FallbackChain(list(providers), embedder or Stub("ollama-embed"), **kw)


def test_falls_back_when_first_provider_runs_out_of_quota():
    groq, gemini = Stub("groq", error=QuotaExceededError("groq", "429")), Stub("gemini")
    result = _chain(groq, gemini).complete(_req())
    assert result.provider == "gemini"


def test_request_errors_do_not_fall_back():
    groq = Stub("groq", error=ProviderRequestError("groq", "bad schema"))
    gemini = Stub("gemini")
    with pytest.raises(ProviderRequestError):
        _chain(groq, gemini).complete(_req())
    assert gemini.calls == 0


def test_all_providers_failing_reports_every_failure():
    chain = _chain(
        Stub("groq", error=ProviderUnavailableError("groq", "down")),
        Stub("gemini", error=QuotaExceededError("gemini", "429")),
    )
    with pytest.raises(AllProvidersFailedError) as info:
        chain.complete(_req())
    assert len(info.value.failures) == 2


def test_quota_cooldown_skips_provider_then_retries_after_expiry():
    now = [0.0]
    groq = Stub("groq", error=QuotaExceededError("groq", "429"))
    chain = _chain(groq, Stub("gemini"), cooldown_seconds=60, clock=lambda: now[0])
    chain.complete(_req())
    chain.complete(_req())
    assert groq.calls == 1 
    now[0] = 61.0
    chain.complete(_req())
    assert groq.calls == 2


def test_stream_falls_back_if_failure_happens_before_first_token():
    chain = _chain(Stub("groq", error=ProviderUnavailableError("groq", "down")), Stub("gemini"))
    events = list(chain.stream(_req()))
    assert [e.text for e in events if e.kind == "token"] == ["a", "b"]
    assert events[-1].result.provider == "gemini"


def test_stream_does_not_switch_provider_after_first_token():
    gemini = Stub("gemini")
    chain = _chain(DropsMidStream("groq"), gemini)
    seen = []
    with pytest.raises(ProviderUnavailableError):
        for event in chain.stream(_req()):
            seen.append(event.text)
    assert seen == ["a"]
    assert gemini.calls == 0


def test_embeddings_never_fall_back():
    completion = Stub("groq")
    chain = _chain(completion, embedder=Stub("ollama", error=ProviderUnavailableError("ollama", "down")))
    with pytest.raises(ProviderUnavailableError):
        chain.embed(["x"])
    assert completion.calls == 0