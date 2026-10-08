"""Security primitives (stdlib only)."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import secrets
import time
from typing import Final

DEFAULT_N: Final = 16384
DEFAULT_R: Final = 8
DEFAULT_P: Final = 1
KEY_LEN: Final = 64


class PasswordError(Exception):
    """Password validation failed."""


class TokenError(Exception):
    """A token was invalid or expired."""


def _b64url_encode_bytes(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode_bytes(s: str) -> bytes:
    padded = s + "=" * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))


def _b64url_encode_obj(obj: dict[str, object]) -> str:
    raw = json.dumps(obj, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode_obj(s: str) -> dict[str, object]:
    padded = s + "=" * (4 - len(s) % 4)
    raw = base64.urlsafe_b64decode(padded.encode("ascii"))
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise TokenError("malformed token") from exc


def hash_password(password: str) -> str:
    if not password:
        raise PasswordError("password must not be empty")
    salt = secrets.token_bytes(16)
    derived = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=DEFAULT_N,
        r=DEFAULT_R,
        p=DEFAULT_P,
        dklen=KEY_LEN,
    )
    return f"scrypt${DEFAULT_N}${DEFAULT_R}${DEFAULT_P}${_b64url_encode_bytes(salt)}${_b64url_encode_bytes(derived)}"


def verify_password(password: str, stored: str) -> bool:
    try:
        parts = stored.split("$")
        if len(parts) != 6 or parts[0] != "scrypt":
            return False
        n = int(parts[1])
        r = int(parts[2])
        p = int(parts[3])
        salt = _b64url_decode_bytes(parts[4])
        expected = _b64url_decode_bytes(parts[5])
        derived = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=n,
            r=r,
            p=p,
            dklen=len(expected),
        )
        return hmac.compare_digest(derived, expected)
    except (ValueError, TypeError, UnicodeError, binascii.Error, OSError):
        return False


def dummy_hash() -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.scrypt(b"dummy", salt=salt, n=DEFAULT_N, r=DEFAULT_R, p=DEFAULT_P, dklen=KEY_LEN)
    return f"scrypt${DEFAULT_N}${DEFAULT_R}${DEFAULT_P}${_b64url_encode_bytes(salt)}${_b64url_encode_bytes(derived)}"


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
    pstr = _b64url_encode_obj(payload)
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
    payload = _b64url_decode_obj(pstr)
    exp = payload.get("exp")
    ts = int(now) if now is not None else int(_now())
    if not isinstance(exp, int) or exp < ts:
        raise TokenError("token expired")
    for key in ("tenant_id", "user_id", "role"):
        if key not in payload:
            raise TokenError("invalid token")
    return payload
