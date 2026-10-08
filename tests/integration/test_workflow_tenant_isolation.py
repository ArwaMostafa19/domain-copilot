import os

import psycopg
import pytest

from src.infrastructure.database import tenant_connection
from src.infrastructure.migrate import apply_migrations

DATABASE_URL = os.environ.get("DATABASE_URL")
ADMIN_DATABASE_URL = os.environ.get("ADMIN_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not (DATABASE_URL and ADMIN_DATABASE_URL),
    reason="Database URLs not set (requires live PostgreSQL server)",
)


def test_migration_005_is_idempotent():
    with psycopg.connect(ADMIN_DATABASE_URL) as conn:
        apply_migrations(conn)
        apply_migrations(conn)


def test_audit_log_cannot_be_updated_or_deleted():
    with tenant_connection("tenant-alpha") as conn:
        conn.execute(
            "INSERT INTO audit_log (tenant_id, action, subject_type) VALUES (%s, %s, %s)",
            ("tenant-alpha", "test_action", "test_subject"),
        )
        with pytest.raises(psycopg.Error):
            conn.execute("UPDATE audit_log SET action='hacked' WHERE action='test_action'")

        with pytest.raises(psycopg.Error):
            conn.execute("DELETE FROM audit_log WHERE action='test_action'")


def test_tenant_isolation_on_runs_and_ask_log():
    with tenant_connection("tenant-alpha") as conn:
        conn.execute(
            "INSERT INTO runs (tenant_id, user_id, question, status) VALUES (%s, %s, %s, %s)",
            ("tenant-alpha", 1, "alpha question", "running"),
        )
        conn.execute(
            "INSERT INTO ask_log (tenant_id, question, answer_text) VALUES (%s, %s, %s)",
            ("tenant-alpha", "alpha ask", "alpha answer"),
        )

    # In tenant-beta context, tenant-alpha records must not be visible
    with tenant_connection("tenant-beta") as conn:
        run_count = conn.execute("SELECT COUNT(*) FROM runs WHERE question='alpha question'").fetchone()[0]
        ask_count = conn.execute("SELECT COUNT(*) FROM ask_log WHERE question='alpha ask'").fetchone()[0]
        assert run_count == 0
        assert ask_count == 0
