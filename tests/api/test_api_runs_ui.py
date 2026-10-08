from fastapi.testclient import TestClient

from src.api.main import app

SECRET = "x" * 32
client = TestClient(app)


def test_health_and_ready():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_ui_index_served():
    res = client.get("/")
    assert res.status_code == 200


def test_security_headers_and_csp_present():
    res = client.get("/health")
    assert "X-Correlation-ID" in res.headers
    assert res.headers["X-Content-Type-Options"] == "nosniff"
    assert res.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'self'" in res.headers["Content-Security-Policy"]


def test_unauthorized_runs_access():
    res = client.get("/runs")
    assert res.status_code == 401
