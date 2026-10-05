import os

import psycopg
import pytest

from src.infrastructure.database import tenant_connection

ADMIN_URL = os.environ.get("ADMIN_DATABASE_URL")
APP_URL = os.environ.get("DATABASE_URL")

pytestmark = pytest.mark.skipif(not (ADMIN_URL and APP_URL), reason="database URLs are not set")

ALPHA = "tenant-alpha"
BETA = "tenant-beta"

INSERT_DOCUMENT = """
    INSERT INTO documents
        (tenant_id, doc_id, title, revision, status, source_format, source_path, content_sha256)
    VALUES (%s, %s, 'Original title', 'Rev 1', 'current', 'markdown', 'test.md', 'abc')
"""


@pytest.fixture
def two_documents():
    """One document per tenant, written by the admin user."""
    with psycopg.connect(ADMIN_URL, autocommit=True) as admin:
        admin.execute("DELETE FROM documents WHERE doc_id LIKE 'TEST-%'")
        admin.execute(INSERT_DOCUMENT, (ALPHA, "TEST-ALPHA"))
        admin.execute(INSERT_DOCUMENT, (BETA, "TEST-BETA"))
    yield
    with psycopg.connect(ADMIN_URL, autocommit=True) as admin:
        admin.execute("DELETE FROM documents WHERE doc_id LIKE 'TEST-%'")


@pytest.mark.parametrize("tenant", [ALPHA, BETA])
def test_each_tenant_sees_only_its_own_documents(two_documents, tenant):
    with tenant_connection(tenant) as conn:
        rows = conn.execute("SELECT DISTINCT tenant_id FROM documents").fetchall()
    assert rows == [(tenant,)]


def test_without_a_tenant_nothing_is_visible(two_documents):
    with psycopg.connect(APP_URL) as conn:
        count = conn.execute("SELECT count(*) FROM documents").fetchone()[0]
    assert count == 0


def test_writing_a_document_for_another_tenant_is_rejected(two_documents):
    with pytest.raises(psycopg.errors.InsufficientPrivilege), tenant_connection(ALPHA) as conn:
        conn.execute(INSERT_DOCUMENT, (BETA, "TEST-FORGED"))


def test_update_and_delete_cannot_touch_another_tenants_documents(two_documents):
    with tenant_connection(ALPHA) as conn:
        updated = conn.execute("UPDATE documents SET title = 'Hacked'").rowcount
        deleted = conn.execute("DELETE FROM documents WHERE doc_id = 'TEST-BETA'").rowcount
    assert (updated, deleted) == (1, 0)  # only alpha's own document was touched

    with psycopg.connect(ADMIN_URL) as admin:
        title = admin.execute(
            "SELECT title FROM documents WHERE doc_id = 'TEST-BETA'"
        ).fetchone()[0]
    assert title == "Original title"


def test_the_tenant_does_not_leak_into_the_next_transaction(two_documents):
    with psycopg.connect(APP_URL) as conn:
        with conn.transaction():
            conn.execute("SELECT set_config('app.tenant_id', %s, true)", (ALPHA,))
            inside = conn.execute("SELECT count(*) FROM documents").fetchone()[0]
        with conn.transaction():
            outside = conn.execute("SELECT count(*) FROM documents").fetchone()[0]
    assert (inside, outside) == (1, 0)


def test_the_application_user_cannot_bypass_row_level_security():
    with psycopg.connect(APP_URL) as conn:
        superuser, bypass = conn.execute(
            "SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user"
        ).fetchone()
    assert (superuser, bypass) == (False, False)


def test_every_table_with_a_tenant_column_has_row_level_security():
    with psycopg.connect(ADMIN_URL) as admin:
        rows = admin.execute(
            """
            SELECT c.relname, c.relrowsecurity
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public' AND c.relkind = 'r' AND c.relname IN (
                SELECT table_name FROM information_schema.columns
                WHERE table_schema = 'public' AND column_name = 'tenant_id')
            """
        ).fetchall()
    assert "documents" in {name for name, _ in rows}
    assert [name for name, enabled in rows if not enabled] == []