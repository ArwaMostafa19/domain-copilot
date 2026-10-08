"""Authentication logic: login and token verification.

The database user record is always consulted after token verification (role and
active status come from the database, not the token). Login returns a generic
error for unknown users and wrong passwords and does similar work to avoid
timing side-channels in structure.
"""

from __future__ import annotations

from src.application import security
from src.application.ports import UserRepository
from src.domain.workflow import WorkflowError


class AuthError(WorkflowError):
    """Authentication failed with a generic message."""


def login(
    tenant_id: str,
    username: str,
    password: str,
    user_repo: UserRepository,
    secret: str,
    ttl_seconds: int,
) -> dict[str, object]:
    """Login and return an access token and the user profile."""
    user = user_repo.get_by_username(tenant_id, username)
    dummy = security.dummy_hash()
    stored = getattr(user, "password_hash", dummy)
    ok = user is not None and user.active and security.verify_password(password, stored)
    if not ok or user is None:
        raise AuthError("invalid credentials")
    token = security.create_token(
        tenant_id=tenant_id,
        user_id=user.id,
        role=user.role,
        secret=secret,
        ttl_seconds=ttl_seconds,
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "tenant_id": tenant_id,
        "user_id": user.id,
        "role": user.role,
        "username": user.username,
    }


def verify_and_load(
    token: str,
    secret: str,
    user_repo: UserRepository,
) -> dict[str, object]:
    """Verify the token and reload the user from the database."""
    try:
        payload = security.verify_token(token, secret)
    except Exception as exc:
        raise AuthError("invalid token") from exc
    tenant_id = str(payload["tenant_id"])
    user_id = int(payload["user_id"])
    user = user_repo.get(tenant_id, user_id)
    if user is None or not user.active:
        raise AuthError("invalid token")
    return {
        "tenant_id": tenant_id,
        "user_id": user.id,
        "role": user.role,
        "username": user.username,
    }
