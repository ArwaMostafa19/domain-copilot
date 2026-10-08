from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application import auth
from src.application.auth import AuthError
from src.application.ports import UserRepository
from src.infrastructure.workflow_repository import PgUserRepository

bearer = HTTPBearer(auto_error=False)


def get_user_repo() -> UserRepository:
    return PgUserRepository()


def get_auth_secret(request: Request) -> str:
    settings = getattr(request.app.state, "settings", None)
    return getattr(settings, "auth_secret", "") if settings else ""


async def get_current_user(
    request: Request,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    secret: Annotated[str, Depends(get_auth_secret)],
) -> dict[str, object]:
    if creds is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
    try:
        user = auth.verify_and_load(creds.credentials, secret, user_repo)
    except AuthError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized") from None
    request.state.user = user
    return user


def require_role(required: str) -> Callable:
    def checker(
        user: Annotated[dict[str, object], Depends(get_current_user)],
    ) -> dict[str, object]:
        role = user.get("role")
        if role != required and not (required == "technician" and role == "supervisor"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
        return user

    return checker


def require_technician_or_supervisor(
    user: Annotated[dict[str, object], Depends(get_current_user)],
) -> dict[str, object]:
    role = user.get("role")
    if role not in ("technician", "supervisor"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    return user
