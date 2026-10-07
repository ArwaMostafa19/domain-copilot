"""Manual smoke tool for the real chat providers and the fallback chain.

The owner runs this by hand against Groq, Gemini or Ollama, with real keys in
the shell. It never loads a ``.env`` file itself. Load the environment first:

    set -a; source .env; set +a
    python -m src.infrastructure.llm_smoke --provider groq

Tests drive it with an explicit ``environ`` and an ``httpx`` mock client, so
no test and no CI run ever makes a network call.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Mapping

import httpx

from src.application.llm_router import FallbackChain
from src.domain.llm import (
    AllProvidersFailedError,
    CompletionRequest,
    CompletionResult,
    ConfigError,
    Message,
    ProviderError,
    QuotaExceededError,
    TokenUsage,
    ToolSpec,
)
from src.infrastructure.config import Settings, load_settings
from src.infrastructure.providers.factory import build_chain, build_providers
from src.infrastructure.providers.fake import FakeLLMProvider

DEFAULT_PROMPT = "Reply with the single word: pong"
TOOLS_PROMPT = "What time is it in Cairo? Use the tool."
EMBED_PROMPT = "maintenance interval"
GET_TIME_TOOL = ToolSpec(
    name="get_time",
    description="Return the current time",
    parameters={
        "type": "object",
        "properties": {"timezone": {"type": "string"}},
        "required": [],
    },
)


def main(
    argv: list[str] | None = None,
    environ: Mapping[str, str] | None = None,
    client: httpx.Client | None = None,
) -> int:
    """Run one smoke action and return the process exit code."""
    args = _parse(argv)
    env = dict(os.environ if environ is None else environ)
    try:
        if args.provider:
            env["LLM_CHAIN"] = args.provider
        settings = load_settings(env)
        if args.embed:
            return _run_embed(build_chain(settings, client=client))
        chain = _smoke_chain(settings, args.fail, client)
        request = _build_request(args.tools)
        result = _run_stream(chain, request) if args.stream else _run_once(chain, request)
        _print_chain(settings)
        if args.tools:
            _print_tool_calls(result)
        return 0
    except ConfigError as error:
        print(f"error: {error}")
        return 2
    except (AllProvidersFailedError, ProviderError) as error:
        print(f"{type(error).__name__}: {error}")
        return 1


def _parse(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke-test the configured LLM providers.")
    parser.add_argument("--provider", help="use only this provider in the chain")
    parser.add_argument("--stream", action="store_true", help="stream the answer token by token")
    parser.add_argument("--tools", action="store_true", help="send one tool and report the call")
    parser.add_argument("--embed", action="store_true", help="call the embedding provider once")
    parser.add_argument("--fail", help="simulate a quota failure of this provider")
    return parser.parse_args(argv)


def _smoke_chain(
    settings: Settings, fail: str | None, client: httpx.Client | None
) -> FallbackChain:
    """The chat chain, optionally with one provider replaced by a failing fake."""
    chain = build_chain(settings, client=client)
    if not fail:
        return chain
    if fail not in settings.llm_chain:
        raise ConfigError(f"cannot fail provider {fail!r}: it is not in LLM_CHAIN")
    providers = build_providers(settings, client=client)
    ordered = [
        _failing_provider(name) if name == fail else providers[name]
        for name in settings.llm_chain
    ]
    print(f"simulated failure of {fail}")
    return FallbackChain(
        ordered,
        providers[settings.embedding_provider],
        cooldown_seconds=settings.llm_cooldown_seconds,
    )


def _failing_provider(name: str) -> FakeLLMProvider:
    """A fake with the right name that reports an exhausted quota once."""
    return FakeLLMProvider(
        name=name, script=[QuotaExceededError(name, "simulated failure")]
    )


def _build_request(tools: bool) -> CompletionRequest:
    prompt = TOOLS_PROMPT if tools else DEFAULT_PROMPT
    message = Message(role="user", content=prompt)
    if tools:
        return CompletionRequest(messages=(message,), tools=(GET_TIME_TOOL,))
    return CompletionRequest(messages=(message,))


def _run_once(chain: FallbackChain, request: CompletionRequest) -> CompletionResult:
    result = chain.complete(request)
    _print_summary(result)
    print(f"answer: {result.content}")
    return result


def _run_stream(chain: FallbackChain, request: CompletionRequest) -> CompletionResult:
    result = CompletionResult("", (), TokenUsage(), chain.name, "")
    for event in chain.stream(request):
        if event.kind == "token":
            print(event.text, end="")
        elif event.kind == "done" and event.result is not None:
            result = event.result
    print()
    _print_summary(result)
    return result


def _run_embed(chain: FallbackChain) -> int:
    result = chain.embed([EMBED_PROMPT])
    print(f"provider: {result.provider}")
    print(f"model: {result.model}")
    print(f"dimensions: {result.dimensions}")
    _print_tokens(result.usage)
    return 0


def _print_summary(result: CompletionResult) -> None:
    print(f"provider: {result.provider}")
    print(f"model: {result.model}")
    _print_tokens(result.usage)


def _print_tokens(usage) -> None:
    suffix = " (estimated)" if usage.estimated else ""
    print(
        f"tokens: prompt={usage.prompt_tokens} "
        f"completion={usage.completion_tokens} "
        f"total={usage.total_tokens}{suffix}"
    )


def _print_chain(settings: Settings) -> None:
    print("chain: " + " > ".join(settings.llm_chain))


def _print_tool_calls(result: CompletionResult) -> None:
    if not result.tool_calls:
        print("no tool call returned")
        return
    for call in result.tool_calls:
        print(f"tool call: {call.name} {json.dumps(call.arguments)}")


if __name__ == "__main__":
    sys.exit(main())
