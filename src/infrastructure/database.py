"""Database access. Tenant queries run inside a tenant context."""

import os
from collections.abc import Iterator
from contextlib import contextmanager

import psycopg


@contextmanager
def tenant_connection(tenant_id: str, dsn: str | None = None) -> Iterator[psycopg.Connection]:
    with psycopg.connect(dsn or os.environ["DATABASE_URL"]) as conn, conn.transaction():
        conn.execute("SELECT set_config('app.tenant_id', %s, true)", (tenant_id,))
        yield conn


@contextmanager
def app_connection(dsn: str | None = None) -> Iterator[psycopg.Connection]:
    """A connection without a tenant context, for global tables that have no RLS."""
    with psycopg.connect(dsn or os.environ["DATABASE_URL"]) as conn, conn.transaction():
        yield conn