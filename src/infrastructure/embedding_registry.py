"""The global record of which embedding model built the index."""

from __future__ import annotations

from src.domain.llm import EmbeddingSpec
from src.infrastructure.database import app_connection

SELECT_SPEC = "SELECT model, dimensions FROM embedding_index_meta"

REGISTER_SPEC = """
    INSERT INTO embedding_index_meta (model, dimensions)
    VALUES (%s, %s)
    ON CONFLICT (id) DO NOTHING
"""


class PostgresEmbeddingIndexRegistry:
    """Remembers the embedding model; one global row, never overwritten."""

    def get(self) -> EmbeddingSpec | None:
        """The recorded spec, or None while the table is still empty."""
        with app_connection() as connection:
            row = connection.execute(SELECT_SPEC).fetchone()
        return EmbeddingSpec(row[0], row[1]) if row else None

    def register(self, spec: EmbeddingSpec) -> None:
        """Insert when the table is empty; keep the first row otherwise."""
        with app_connection() as connection:
            connection.execute(REGISTER_SPEC, (spec.model, spec.dimensions))
