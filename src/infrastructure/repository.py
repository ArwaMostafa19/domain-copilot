"""PostgreSQL storage for documents, their chunks and their safety steps."""

from __future__ import annotations

from src.domain.documents import Chunk, DocumentMeta, SafetyStep
from src.infrastructure.database import tenant_connection

MAX_ERROR_LENGTH = 500

FIND_INGESTED = """
    SELECT content_sha256
    FROM documents
    WHERE tenant_id = %s
      AND doc_id = %s
      AND source_format = %s
      AND ingest_status = 'ingested'
"""

UPSERT_DOCUMENT = """
    INSERT INTO documents
        (tenant_id, doc_id, title, equipment, document_type, revision, status,
         source_format, source_path, content_sha256, ingest_status, ingest_error)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'ingested', NULL)
    ON CONFLICT (tenant_id, doc_id, source_format) DO UPDATE SET
        title = EXCLUDED.title,
        equipment = EXCLUDED.equipment,
        document_type = EXCLUDED.document_type,
        revision = EXCLUDED.revision,
        status = EXCLUDED.status,
        source_path = EXCLUDED.source_path,
        content_sha256 = EXCLUDED.content_sha256,
        ingest_status = 'ingested',
        ingest_error = NULL
    RETURNING id
"""

INSERT_FAILED_DOCUMENT = """
    INSERT INTO documents
        (tenant_id, doc_id, title, equipment, document_type, revision, status,
         source_format, source_path, content_sha256, ingest_status, ingest_error)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'failed', %s)
"""

RECORD_ERROR = """
    UPDATE documents
    SET ingest_error = %s
    WHERE tenant_id = %s
      AND doc_id = %s
      AND source_format = %s
"""

DELETE_CHUNKS = "DELETE FROM chunks WHERE document_id = %s"
DELETE_STEPS = "DELETE FROM safety_prerequisites WHERE document_id = %s"

INSERT_CHUNK = """
    INSERT INTO chunks
        (tenant_id, document_id, ordinal, section, page, revision, context,
         content, embedding_model, embedding)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::vector)
"""

INSERT_STEP = """
    INSERT INTO safety_prerequisites
        (tenant_id, document_id, step_no, step_text)
    VALUES (%s, %s, %s, %s)
"""


class PostgresDocumentRepository:
    """Stores documents, chunks and safety steps, one tenant per connection."""

    def stored_fingerprint(self, meta: DocumentMeta) -> str | None:
        """Return the sha256 of the ingested version of this document, or None."""
        with tenant_connection(meta.tenant_id) as connection:
            row = connection.execute(
                FIND_INGESTED, (meta.tenant_id, meta.doc_id, meta.source_format)
            ).fetchone()
        return row[0] if row else None

    def replace_document(
        self,
        meta: DocumentMeta,
        chunks: list[Chunk],
        embeddings: list[list[float]],
        steps: list[SafetyStep],
        embedding_model: str,
    ) -> None:
        """Replace everything stored for this document, in one transaction."""
        with tenant_connection(meta.tenant_id) as connection:
            document_id = connection.execute(
                UPSERT_DOCUMENT, _document_values(meta)
            ).fetchone()[0]
            connection.execute(DELETE_CHUNKS, (document_id,))
            connection.execute(DELETE_STEPS, (document_id,))
            for chunk, embedding in zip(chunks, embeddings, strict=True):
                connection.execute(
                    INSERT_CHUNK,
                    (
                        meta.tenant_id,
                        document_id,
                        chunk.ordinal,
                        chunk.section,
                        chunk.page,
                        chunk.revision,
                        chunk.context,
                        chunk.text,
                        embedding_model,
                        _vector_literal(embedding),
                    ),
                )
            for step in steps:
                connection.execute(
                    INSERT_STEP, (meta.tenant_id, document_id, step.step_no, step.text)
                )

    def mark_failed(self, meta: DocumentMeta, error: str) -> None:
        """Record the error, keeping the status and chunks of an older version."""
        message = error[:MAX_ERROR_LENGTH]
        with tenant_connection(meta.tenant_id) as connection:
            updated = connection.execute(
                RECORD_ERROR, (message, meta.tenant_id, meta.doc_id, meta.source_format)
            ).rowcount
            if updated:
                return
            connection.execute(
                INSERT_FAILED_DOCUMENT, (*_document_values(meta), message)
            )


def _document_values(meta: DocumentMeta) -> tuple[str | None, ...]:
    """The document columns both inserts write, in statement order."""
    return (
        meta.tenant_id,
        meta.doc_id,
        meta.title,
        meta.equipment,
        meta.document_type,
        meta.revision,
        meta.status,
        meta.source_format,
        meta.source_path,
        meta.content_sha256,
    )


def _vector_literal(values: list[float]) -> str:
    """Render one embedding as the ``[1.0,2.0]`` text pgvector expects."""
    return "[" + ",".join(str(value) for value in values) + "]"
