from src.infrastructure.config import load_settings
from src.infrastructure.providers.factory import build_embedding_stack
from src.infrastructure.providers.ollama_provider import OllamaProvider


class _EmptyRegistry:
    def get(self):
        return None

    def register(self, spec):
        pass


def test_the_embedding_stack_does_not_build_the_chat_chain():
    settings = load_settings({}) 

    provider, _guard = build_embedding_stack(settings, _EmptyRegistry())

    assert isinstance(provider, OllamaProvider)