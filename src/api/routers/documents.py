from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.deps import get_current_user
from src.infrastructure.database import tenant_connection

router = APIRouter()


@router.get("/documents")
def list_documents(
    user: Annotated[dict[str, object], Depends(get_current_user)],
):
    tenant_id = str(user["tenant_id"])
    with tenant_connection(tenant_id) as conn:
        rows = conn.execute(
            """
            SELECT d.id, d.doc_id, d.title, d.equipment, d.revision, d.status,
                   d.content_sha256, d.ingest_error, COUNT(c.id) as chunk_count
            FROM documents d
            LEFT JOIN chunks c ON c.document_id = d.id
            GROUP BY d.id
            ORDER BY d.doc_id
            """
        ).fetchall()

    return [
        {
            "id": str(row[0]),
            "doc_id": row[1],
            "title": row[2],
            "equipment_id": row[3],
            "revision": row[4],
            "status": row[5],
            "fingerprint": row[6],
            "ingest_error": row[7],
            "chunk_count": row[8],
        }
        for row in rows
    ]


@router.get("/documents/{doc_id}")
def get_document(
    doc_id: str,
    user: Annotated[dict[str, object], Depends(get_current_user)],
):
    tenant_id = str(user["tenant_id"])
    with tenant_connection(tenant_id) as conn:
        row = conn.execute(
            """
            SELECT d.id, d.doc_id, d.title, d.equipment, d.revision, d.status,
                   d.content_sha256, d.ingest_error, COUNT(c.id) as chunk_count
            FROM documents d
            LEFT JOIN chunks c ON c.document_id = d.id
            WHERE d.doc_id = %s OR d.id::text = %s
            GROUP BY d.id
            """,
            (doc_id, doc_id),
        ).fetchone()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="document not found")

    return {
        "id": str(row[0]),
        "doc_id": row[1],
        "title": row[2],
        "equipment_id": row[3],
        "revision": row[4],
        "status": row[5],
        "fingerprint": row[6],
        "ingest_error": row[7],
        "chunk_count": row[8],
    }
