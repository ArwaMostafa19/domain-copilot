"""The embedding registry keeps one global row that the app role never overwrites.

Every test works on the real table, so a fixture saves any row a developer
database already holds, empties the table, and restores the row afterwards.
"""

from __future__ import annotations

import os

import psycopg
import pytest

from src.domain.llm import EmbeddingSpec
from src.infrastructure.embedding_registry import PostgresEmbeddingIndexRegistry

ADMIN_URL = os.environ.get("ADMIN_DATABASE_URL")
APP_URL = os.environ.get("DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not (APP_URL and ADMIN_URL), reason="database URLs are not set"
)

TEST_SPEC = EmbeddingSpec("registry-test-model", 768)


@pytest.fixture(autouse=True)
def preserved_table():
    """Save the real registration, empty the table, restore it after the test."""
    with psycopg.connect(ADMIN_URL, autocommit=True) as admin:
        saved = admin.execute(
            "SELECT model, dimensions FROM embedding_index_meta"
        ).fetchone()
    _delete_all()
    yield
    _delete_all()
    if saved is not None:
        with psycopg.connect(ADMIN_URL, autocommit=True) as admin:
            admin.execute(
                "INSERT INTO embedding_index_meta (model, dimensions) VALUES (%s, %s)",
                (saved[0], saved[1]),
            )


def _delete_all() -> None:
    with psycopg.connect(ADMIN_URL, autocommit=True) as admin:
        admin.execute("DELETE FROM embedding_index_meta")


def test_an_empty_table_reports_none() -> None:
    assert PostgresEmbeddingIndexRegistry().get() is None


def test_register_then_get_returns_the_spec() -> None:
    registry = PostgresEmbeddingIndexRegistry()

    registry.register(TEST_SPEC)

    assert registry.get() == TEST_SPEC


def test_registering_twice_keeps_the_first_value() -> None:
    registry = PostgresEmbeddingIndexRegistry()
    registry.register(TEST_SPEC)

    registry.register(EmbeddingSpec("registry-second-model", 1024))

    assert registry.get() == TEST_SPEC


def test_the_application_role_can_insert_but_not_update_or_delete() -> None:
    with psycopg.connect(APP_URL, autocommit=True) as connection:
        connection.execute(
            "INSERT INTO embedding_index_meta (model, dimensions) VALUES (%s, %s)",
            ("registry-app-model", 768),
        )
    with psycopg.connect(APP_URL, autocommit=True) as connection:
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            connection.execute(
                "UPDATE embedding_index_meta SET model = %s", ("other-model",)
            )
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            connection.execute("DELETE FROM embedding_index_meta")