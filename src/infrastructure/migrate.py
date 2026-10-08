import os
from pathlib import Path

import psycopg
from psycopg import sql

MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "migrations"
APP_ROLE = "copilot_app"


def ensure_app_role(conn: psycopg.Connection, password: str) -> None:
    exists = conn.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (APP_ROLE,)).fetchone()
    if not exists:
        conn.execute(sql.SQL("CREATE ROLE {} LOGIN").format(sql.Identifier(APP_ROLE)))
    conn.execute(
        sql.SQL("ALTER ROLE {} WITH PASSWORD {} NOSUPERUSER NOBYPASSRLS").format(
            sql.Identifier(APP_ROLE), sql.Literal(password)
        )
    )
    conn.commit()


def apply_migrations(conn: psycopg.Connection) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations ("
        "name text PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT now())"
    )
    conn.commit()
    done = {row[0] for row in conn.execute("SELECT name FROM schema_migrations")}
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        if path.name in done:
            continue
        conn.execute(path.read_text())
        conn.execute("INSERT INTO schema_migrations (name) VALUES (%s)", (path.name,))
        conn.commit()
        print(f"applied {path.name}")


def main() -> None:
    with psycopg.connect(os.environ["ADMIN_DATABASE_URL"]) as conn:
        ensure_app_role(conn, os.environ["APP_DB_PASSWORD"])
        apply_migrations(conn)


if __name__ == "__main__":
    main()
