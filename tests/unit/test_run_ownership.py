from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from src.api.routers.runs import _owned_run


class _Repository:
    def __init__(self, run):
        self.run = run
        self.tenant = None

    def get(self, tenant_id, run_id):
        self.tenant = tenant_id
        return self.run if self.run.id == run_id else None


def test_technician_cannot_read_another_users_run(monkeypatch):
    repo = _Repository(SimpleNamespace(id="run-1", user_id=2))
    monkeypatch.setattr("src.api.routers.runs.PgRunRepository", lambda: repo)

    with pytest.raises(HTTPException) as error:
        _owned_run("tenant-alpha", "run-1", {"role": "technician", "user_id": 1})

    assert error.value.status_code == 404
    assert repo.tenant == "tenant-alpha"


def test_supervisor_can_read_tenant_run(monkeypatch):
    run = SimpleNamespace(id="run-1", user_id=2)
    monkeypatch.setattr("src.api.routers.runs.PgRunRepository", lambda: _Repository(run))
    assert _owned_run("tenant-alpha", "run-1", {"role": "supervisor", "user_id": 1}) is run
