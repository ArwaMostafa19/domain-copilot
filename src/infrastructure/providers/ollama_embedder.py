"""HTTP client for the Ollama embeddings API."""

from __future__ import annotations

import os

import httpx

from src.application.ports import ProviderError

DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "nomic-embed-text"
DEFAULT_DIMENSION = 768
DEFAULT_TIMEOUT = 120.0
DEFAULT_BATCH_SIZE = 16
EMBED_ENDPOINT = "/api/embed"
BODY_SNIPPET_LENGTH = 200


class OllamaEmbedder:
    """Embeds texts through ``POST {base_url}/api/embed``, one batch at a time."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        dimension: int = DEFAULT_DIMENSION,
        timeout: float = DEFAULT_TIMEOUT,
        batch_size: int = DEFAULT_BATCH_SIZE,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.base_url = (
            base_url or os.environ.get("OLLAMA_BASE_URL") or DEFAULT_BASE_URL
        ).rstrip("/")
        self.model = model or os.environ.get("EMBEDDING_MODEL") or DEFAULT_MODEL
        self.dimension = dimension
        self.timeout = timeout
        self.batch_size = batch_size
        self.model_name = self.model
        self._transport = transport

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one vector of ``dimension`` values per text, in input order."""
        if not texts:
            return []
        vectors: list[list[float]] = []
        with httpx.Client(
            base_url=self.base_url, timeout=self.timeout, transport=self._transport
        ) as client:
            for start in range(0, len(texts), self.batch_size):
                batch = texts[start : start + self.batch_size]
                vectors.extend(self._embed_batch(client, batch))
        return vectors

    def _embed_batch(
        self, client: httpx.Client, batch: list[str]
    ) -> list[list[float]]:
        """Send one batch and return its validated embeddings."""
        try:
            response = client.post(
                EMBED_ENDPOINT, json={"model": self.model, "input": batch}
            )
        except httpx.HTTPError as error:
            raise ProviderError(f"Ollama is not reachable at {self.base_url}") from error
        if response.status_code != 200:
            raise ProviderError(
                f"Ollama at {self.base_url} returned HTTP {response.status_code}: "
                f"{response.text[:BODY_SNIPPET_LENGTH]}"
            )
        embeddings = self._read_embeddings(response, len(batch))
        for index, vector in enumerate(embeddings):
            if not isinstance(vector, list) or len(vector) != self.dimension:
                size = len(vector) if isinstance(vector, list) else "a non-list value"
                raise ProviderError(
                    f"Ollama at {self.base_url} returned {size} values for text "
                    f"{index}, expected {self.dimension}"
                )
        return embeddings

    def _read_embeddings(self, response: httpx.Response, expected: int) -> list:
        """Read and count-check the ``embeddings`` list of a 200 response."""
        try:
            payload = response.json()
        except ValueError as error:
            raise ProviderError(
                f"Ollama at {self.base_url} returned a malformed response: {error}"
            ) from error
        embeddings = payload.get("embeddings") if isinstance(payload, dict) else None
        if not isinstance(embeddings, list) or len(embeddings) != expected:
            found = len(embeddings) if isinstance(embeddings, list) else "no"
            raise ProviderError(
                f"Ollama at {self.base_url} returned a malformed response: "
                f"{found} embeddings for {expected} texts"
            )
        return embeddings
