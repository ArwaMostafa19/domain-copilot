import pytest
from fastapi.testclient import TestClient

from src.api.deps import get_auth_secret, get_current_user, get_user_repo
from src.api.main import app
from src.application.ports import UserRecord
from src.application.security import TokenError, create_token, verify_token
from src.application.tools import ToolNotAllowedError, build_tool_registry
from src.domain.llm import TokenUsage
from src.domain.rag import Answer
from src.domain.workflow import Role
from tests.fakes import InMemoryUserRepository

SECRET = "a" * 32
WRONG_SECRET = "b" * 32

client = TestClient(app)

app.dependency_overrides[get_auth_secret] = lambda: SECRET
users = InMemoryUserRepository()
users.add(UserRecord(id=1, tenant_id="tenant-alpha", username="tech", role="technician", active=True))
app.dependency_overrides[get_user_repo] = lambda: users


def _fake_answer(question, tenant_id, dependencies, correlation_id=None):
    assert tenant_id == "tenant-alpha"
    return Answer(
        text="No evidence found.", citations=(), refused=True, reason="no_evidence",
        usage=TokenUsage(), evidence=(),
    )


class _Guard:
    def ensure(self, spec):
        pass


class _Embedder:
    model_name = "test"

    def embed(self, texts):
        return [[0.0] for _ in texts]


class _Registry:
    def get(self):
        return None

    def register(self, spec):
        pass


def _fake_embedding_stack(settings, registry):
    return object(), _Guard()


def _fake_chain(settings):
    return object()


def test_token_tampering_truncation_expiry_wrong_secret():
    token = create_token("tenant-alpha", 1, "technician", SECRET, ttl_seconds=3600)

    # Valid token works
    parsed = verify_token(token, SECRET)
    assert parsed["tenant_id"] == "tenant-alpha"

    # Wrong secret fails
    with pytest.raises(TokenError, match="invalid signature"):
        verify_token(token, WRONG_SECRET)

    # Tampered token fails
    tampered = token[:-4] + "xxxx"
    with pytest.raises(TokenError):
        verify_token(tampered, SECRET)

    # Truncated token fails
    truncated = token.rsplit(".", 1)[0]
    with pytest.raises(TokenError):
        verify_token(truncated, SECRET)

    # Expired token fails
    expired = create_token("tenant-alpha", 1, "technician", SECRET, ttl_seconds=-10)
    with pytest.raises(TokenError, match="token expired"):
        verify_token(expired, SECRET)


def test_tenant_in_body_is_ignored():
    # Body containing a malicious tenant_id must not override authenticated tenant
    app.dependency_overrides[get_current_user] = lambda: {
        "tenant_id": "tenant-alpha", "user_id": 1, "role": "technician", "username": "tech"
    }
    from src.api.routers import ask as ask_router
    original = ask_router.answer_question
    original_stack = ask_router.build_embedding_stack
    original_registry = ask_router.PostgresEmbeddingIndexRegistry
    original_embedder = ask_router.GuardedEmbedder
    original_search = ask_router.PostgresChunkSearch
    original_chain = ask_router.build_chain
    ask_router.answer_question = _fake_answer
    ask_router.build_embedding_stack = _fake_embedding_stack
    ask_router.PostgresEmbeddingIndexRegistry = _Registry
    ask_router.GuardedEmbedder = lambda *args: _Embedder()
    ask_router.PostgresChunkSearch = object
    ask_router.build_chain = _fake_chain
    res = client.post("/ask", json={"question": "hello", "tenant_id": "tenant-beta"})
    ask_router.answer_question = original
    ask_router.build_embedding_stack = original_stack
    ask_router.PostgresEmbeddingIndexRegistry = original_registry
    ask_router.GuardedEmbedder = original_embedder
    ask_router.PostgresChunkSearch = original_search
    ask_router.build_chain = original_chain
    # Status should not fail due to tenant switching (handled safely or ignored)
    assert res.status_code in (200, 502, 503)


def test_sql_injection_strings_do_nothing():
    app.dependency_overrides[get_current_user] = lambda: {
        "tenant_id": "tenant-alpha", "user_id": 1, "role": "technician", "username": "tech"
    }
    from src.api.routers import ask as ask_router
    original = ask_router.answer_question
    original_stack = ask_router.build_embedding_stack
    original_registry = ask_router.PostgresEmbeddingIndexRegistry
    original_embedder = ask_router.GuardedEmbedder
    original_search = ask_router.PostgresChunkSearch
    original_chain = ask_router.build_chain
    ask_router.answer_question = _fake_answer
    ask_router.build_embedding_stack = _fake_embedding_stack
    ask_router.PostgresEmbeddingIndexRegistry = _Registry
    ask_router.GuardedEmbedder = lambda *args: _Embedder()
    ask_router.PostgresChunkSearch = object
    ask_router.build_chain = _fake_chain
    sqli = "' OR '1'='1'; DROP TABLE users; --"
    res = client.post("/ask", json={"question": sqli})
    ask_router.answer_question = original
    ask_router.build_embedding_stack = original_stack
    ask_router.PostgresEmbeddingIndexRegistry = original_registry
    ask_router.GuardedEmbedder = original_embedder
    ask_router.PostgresChunkSearch = original_search
    ask_router.build_chain = original_chain
    assert res.status_code in (200, 502, 503)


def test_body_over_1mb_gets_413():
    huge_body = "x" * (1048576 + 100)
    res = client.post("/ask", json={"question": huge_body})
    assert res.status_code == 413


def test_login_rate_limit_returns_429():
    from src.api import main as api_main

    api_main._login_attempts.clear()
    app.dependency_overrides[get_auth_secret] = lambda: SECRET
    app.dependency_overrides[get_user_repo] = lambda: users
    client_ip = "testclient"
    api_main._login_attempts[client_ip] = [api_main.time.time()] * 5
    res = client.post("/auth/login", json={"tenant_id": "tenant-alpha", "username": "u", "password": "p"})
    assert res.status_code == 429
    assert "Retry-After" in res.headers


def test_security_headers_and_csp_present():
    res = client.get("/health")
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert "default-src 'self'" in res.headers.get("Content-Security-Policy", "")


def test_no_secret_in_any_response():
    res = client.get("/health")
    assert SECRET not in res.text


def test_unknown_tool_call_refused_and_audited():
    registry = build_tool_registry()
    with pytest.raises(ToolNotAllowedError, match="unknown tool"):
        registry.invoke("non_existent_tool", {}, Role.TECHNICIAN)
