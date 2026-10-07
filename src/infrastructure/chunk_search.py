"""PostgreSQL adapter for the two chunk searches.

Both queries run inside ``tenant_connection`` so Row-Level Security scopes the
rows to one tenant, and both filter on the embedding model the index was built
with. Values are always query parameters; the vector is passed as text.
"""

from __future__ import annotations

from collections.abc import Sequence

from src.domain.rag import Evidence
from src.infrastructure.database import tenant_connection

DENSE_SQL = """
    SELECT c.id, d.doc_id, d.title, c.section, c.revision, d.status, c.page,
           c.content, 1 - (c.embedding <=> %(q)s::vector) AS score
    FROM chunks c
    JOIN documents d ON d.id = c.document_id
    WHERE c.embedding_model = %(model)s
      AND d.ingest_status = 'ingested'
      AND (%(all)s OR d.status = 'current')
    ORDER BY c.embedding <=> %(q)s::vector
    LIMIT %(k)s
"""

KEYWORD_SQL = """
    SELECT c.id, d.doc_id, d.title, c.section, c.revision, d.status, c.page,
           c.content, ts_rank_cd(c.tsv, query) AS score
    FROM chunks c
    JOIN documents d ON d.id = c.document_id,
         to_tsquery('english', %(tsq)s) AS query
    WHERE c.embedding_model = %(model)s
      AND d.ingest_status = 'ingested'
      AND (%(all)s OR d.status = 'current')
      AND c.tsv @@ query
    ORDER BY score DESC
    LIMIT %(k)s
"""


class PostgresChunkSearch:
    """Dense and keyword search over the chunks of one tenant."""

    def search_dense(
        self,
        tenant_id: str,
        vector: Sequence[float],
        embedding_model: str,
        include_superseded: bool,
        limit: int,
    ) -> list[Evidence]:
        """The closest chunks by cosine distance, best first."""
        if limit <= 0:
            return []
        parameters = {
            "q": _vector_literal(vector),
            "model": embedding_model,
            "all": include_superseded,
            "k": limit,
        }
        with tenant_connection(tenant_id) as connection:
            rows = connection.execute(DENSE_SQL, parameters).fetchall()
        return [_dense_evidence(row) for row in rows]

    def search_keyword(
        self,
        tenant_id: str,
        terms: Sequence[str],
        embedding_model: str,
        include_superseded: bool,
        limit: int,
    ) -> list[Evidence]:
        """The best keyword matches of the terms, best first.

        An empty term list returns nothing without running a query at all.
        """
        if limit <= 0 or not terms:
            return []
        parameters = {
            "tsq": " | ".join(terms),
            "model": embedding_model,
            "all": include_superseded,
            "k": limit,
        }
        with tenant_connection(tenant_id) as connection:
            rows = connection.execute(KEYWORD_SQL, parameters).fetchall()
        return [_keyword_evidence(row) for row in rows]


def _dense_evidence(row: tuple) -> Evidence:
    return _evidence(row, dense_score=row[8])


def _keyword_evidence(row: tuple) -> Evidence:
    return _evidence(row, keyword_score=row[8])


def _evidence(
    row: tuple,
    *,
    dense_score: float = 0.0,
    keyword_score: float = 0.0,
) -> Evidence:
    chunk_id, doc_id, title, section, revision, status, page, content, _score = row
    return Evidence(
        chunk_id=chunk_id,
        doc_id=doc_id,
        title=title,
        section=section,
        revision=revision,
        doc_status=status,
        page=page,
        text=content,
        dense_score=dense_score,
        keyword_score=keyword_score,
    )


def _vector_literal(values: Sequence[float]) -> str:
    """Render one query vector as the ``[1.0,2.0]`` text pgvector expects."""
    return "[" + ",".join(repr(float(value)) for value in values) + "]"
