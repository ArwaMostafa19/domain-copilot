"""Signed tokens (HMAC-SHA256) for API authentication.

The token format is ``base64url(json) + "." + base64url(signature)``. No
third-party JWT library is used (stdlib only). Verification rejects bad
signatures, expired tokens and malformed input with generic errors.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time


class TokenError(Exception):
    """A token was invalid or expired."""


def _b64url_encode(obj: dict[str, object]) -> str:
    raw = json.dumps(obj, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(s: str) -> dict[str, object]:
    padded = s + "=" * (4 - len(s) % 4)
    raw = base64.urlsafe_b64decode(padded.encode("ascii"))
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise TokenError("malformed token") from exc


def _sign(payload: str, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def _now() -> float:
    return time.time()


def create_token(
    tenant_id: str,
    user_id: int,
    role: str,
    secret: str,
    ttl_seconds: int,
) -> str:
    if not secret or len(secret) < 32:
        raise TokenError("auth secret must be at least 32 characters")
    payload = {
        "tenant_id": tenant_id,
        "user_id": user_id,
        "role": role,
        "exp": int(_now() + ttl_seconds),
    }
    pstr = _b64url_encode(payload)
    return f"{pstr}.{_sign(pstr, secret)}"


def verify_token(token: str, secret: str, now: float | None = None) -> dict[str, object]:
    if not secret or len(secret) < 32:
        raise TokenError("auth secret must be at least 32 characters")
    if not token or "." not in token:
        raise TokenError("invalid token")
    try:
        pstr, sig = token.rsplit(".", 1)
    except ValueError:
        raise TokenError("invalid token") from None
    expected = _sign(pstr, secret)
    if not hmac.compare_digest(expected, sig):
        raise TokenError("invalid signature")
    payload = _b64url_decode(pstr)
    exp = payload.get("exp")
    ts = int(now) if now is not None else int(_now())
    if not isinstance(exp, int) or exp < ts:
        raise TokenError("token expired")
    for key in ("tenant_id", "user_id", "role"):
        if key not in payload:
            raise TokenError("invalid token")
    return payload
