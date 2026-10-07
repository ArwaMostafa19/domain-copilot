import pytest

from src.application.embedding_guard import EmbeddingGuard
from src.domain.llm import (
    ConfigError,
    EmbeddingModelMismatchError,
    EmbeddingResult,
    EmbeddingSpec,
    TokenUsage,
)

SPEC = EmbeddingSpec("nomic-embed-text", 768)


class MemoryRegistry:
    def __init__(self, spec=None):
        self.spec = spec

    def get(self):
        return self.spec

    def register(self, spec):
        if self.spec is None:
            self.spec = spec


def _result(model="nomic-embed-text", dims=768, vector_len=None):
    vector = (0.0,) * (vector_len or dims)
    return EmbeddingResult((vector,), model, dims, TokenUsage(1, 0), "p")


def test_first_run_records_the_model():
    registry = MemoryRegistry()
    EmbeddingGuard(registry).ensure(SPEC)
    assert registry.get() == SPEC


def test_same_model_is_accepted_again():
    EmbeddingGuard(MemoryRegistry(SPEC)).ensure(SPEC)


@pytest.mark.parametrize("other", [EmbeddingSpec("other-model", 768), EmbeddingSpec("nomic-embed-text", 1024)])
def test_different_model_or_size_is_rejected(other):
    with pytest.raises(EmbeddingModelMismatchError):
        EmbeddingGuard(MemoryRegistry(SPEC)).ensure(other)


def test_verify_rejects_results_from_a_different_model():
    guard = EmbeddingGuard(MemoryRegistry())
    guard.ensure(SPEC)
    with pytest.raises(EmbeddingModelMismatchError):
        guard.verify(_result(model="text-embedding-004"))


def test_verify_rejects_vectors_of_the_wrong_length():
    guard = EmbeddingGuard(MemoryRegistry())
    guard.ensure(SPEC)
    with pytest.raises(EmbeddingModelMismatchError):
        guard.verify(_result(vector_len=512))


def test_verify_before_ensure_is_a_programming_error():
    with pytest.raises(ConfigError):
        EmbeddingGuard(MemoryRegistry()).verify(_result())