from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.api import schemas
from src.api.deps import get_auth_secret, get_current_user, get_user_repo
from src.application import auth
from src.application.auth import AuthError
from src.application.ports import UserRepository

router = APIRouter()


@router.post("/auth/login", response_model=schemas.LoginResponse)
def login(
    body: schemas.LoginRequest,
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    secret: Annotated[str, Depends(get_auth_secret)],
):
    try:
        return auth.login(
            tenant_id=body.tenant_id,
            username=body.username,
            password=body.password,
            user_repo=user_repo,
            secret=secret,
            ttl_seconds=28800,
        )
    except AuthError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials") from None


@router.get("/me", response_model=schemas.MeResponse)
def me(user: Annotated[dict[str, object], Depends(get_current_user)]):
    return {
        "tenant_id": user["tenant_id"],
        "user_id": user["user_id"],
        "role": user["role"],
        "username": user["username"],
    }
