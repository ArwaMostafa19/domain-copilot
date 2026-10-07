"""Ask one question against the ingested corpus and print the grounded answer.

    python -m src.cli.ask --tenant tenant-alpha "what is the relief set point"

It builds the real dependencies from the environment: the guarded embedder over
the recorded index, the PostgreSQL chunk search and the chat fallback chain.
Exit code is 2 on a configuration error and 1 when every provider fails.
"""

from __future__ import annotations

import argparse
import sys

from src.application.answering import AnswerDeps, answer_question
from src.application.embedding import GuardedEmbedder
from src.domain.llm import ConfigError, EmbeddingModelMismatchError, LLMError
from src.domain.rag import Answer
from src.infrastructure.chunk_search import PostgresChunkSearch
from src.infrastructure.config import load_settings_from_environ
from src.infrastructure.embedding_registry import PostgresEmbeddingIndexRegistry
from src.infrastructure.providers.factory import build_chain, build_embedding_stack


def main(argv: list[str] | None = None) -> int:
    """Build the real dependencies, answer one question and print the result."""
    args = _parse(argv)
    try:
        settings = load_settings_from_environ()
        provider, guard = build_embedding_stack(
            settings, PostgresEmbeddingIndexRegistry()
        )
        guard.ensure(settings.embedding_spec())
        deps = AnswerDeps(
            embedder=GuardedEmbedder(provider, guard, settings.embedding_spec()),
            search=PostgresChunkSearch(),
            chain=build_chain(settings),
            settings=settings,
        )
        answer = answer_question(args.question, args.tenant, deps)
    except (ConfigError, EmbeddingModelMismatchError) as error:
        print(f"error: {error}")
        return 2
    except LLMError as error:
        print(f"error: {error}")
        return 1
    _print_answer(answer)
    return 0


def _parse(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ask one grounded question.")
    parser.add_argument("--tenant", required=True, help="tenant to search")
    parser.add_argument("question", help="the question to ask")
    return parser.parse_args(argv)


def _print_answer(answer: Answer) -> None:
    print(answer.text)
    if answer.refused:
        print(f"refused: {answer.reason}")
    else:
        print("citations:")
        for citation in answer.citations:
            print(
                f"  [chunk:{citation.chunk_id}] {citation.doc_id} "
                f"{citation.section} ({citation.revision})"
            )
    usage = answer.usage
    suffix = " (estimated)" if usage.estimated else ""
    print(
        f"tokens: prompt={usage.prompt_tokens} "
        f"completion={usage.completion_tokens} "
        f"total={usage.total_tokens}{suffix}"
    )


if __name__ == "__main__":
    sys.exit(main())
