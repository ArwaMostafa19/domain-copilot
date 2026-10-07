"""The ask CLI: exit codes and the printed answer."""

from __future__ import annotations

import pytest

from src.cli import ask
from src.domain.llm import (
    AllProvidersFailedError,
    ConfigError,
    ProviderUnavailableError,
    TokenUsage,
)
from src.domain.rag import Answer, Citation


class _Settings:
    def embedding_spec(self) -> None:
        return None


class _Guard:
    def ensure(self, spec) -> None:
        return None


@pytest.fixture
def stub_dependencies(monkeypatch):
    monkeypatch.setattr(ask, "load_settings_from_environ", lambda: _Settings())
    monkeypatch.setattr(
        ask, "build_embedding_stack", lambda settings, registry: (object(), _Guard())
    )
    monkeypatch.setattr(ask, "GuardedEmbedder", lambda *args: object())
    monkeypatch.setattr(ask, "PostgresChunkSearch", object)
    monkeypatch.setattr(ask, "build_chain", lambda settings: object())


def test_provider_failure_returns_one(stub_dependencies, monkeypatch, capsys) -> None:
    def boom(question, tenant_id, deps):
        raise AllProvidersFailedError([ProviderUnavailableError("ollama", "down")])

    monkeypatch.setattr(ask, "answer_question", boom)

    code = ask.main(["--tenant", "tenant-alpha", "q"])

    assert code == 1
    assert capsys.readouterr().out.startswith("error:")


def test_a_configuration_error_returns_two(monkeypatch, capsys) -> None:
    def boom():
        raise ConfigError("no chain")

    monkeypatch.setattr(ask, "load_settings_from_environ", boom)

    code = ask.main(["--tenant", "tenant-alpha", "q"])

    assert code == 2
    assert capsys.readouterr().out.startswith("error:")


def test_a_grounded_answer_is_printed(stub_dependencies, monkeypatch, capsys) -> None:
    citation = Citation(
        chunk_id=7, doc_id="DOC-1", section="Set point", revision="Rev B", page=None
    )
    answer = Answer(
        text="The set point is 210 bar [chunk:7].",
        citations=(citation,),
        refused=False,
        reason=None,
        usage=TokenUsage(prompt_tokens=10, completion_tokens=5),
        evidence=(),
    )
    monkeypatch.setattr(ask, "answer_question", lambda *args: answer)

    code = ask.main(["--tenant", "tenant-alpha", "q"])

    out = capsys.readouterr().out
    assert code == 0
    assert "The set point is 210 bar [chunk:7]." in out
    assert "[chunk:7] DOC-1 Set point (Rev B)" in out
    assert "total=15" in out