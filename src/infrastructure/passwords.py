"""Password hashing with scrypt and constant-time comparison.

No third-party dependencies. The stored format carries the scrypt parameters so
we can change them later if needed (format: ``scrypt$N$r$p$salt$hash``).
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import secrets
from typing import Final

DEFAULT_N: Final = 32768
DEFAULT_R: Final = 8
DEFAULT_P: Final = 1
KEY_LEN: Final = 64


class PasswordError(Exception):
    """Password validation failed."""


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64decode(s: str) -> bytes:
    padded = s + "=" * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))


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
    return f"scrypt${DEFAULT_N}${DEFAULT_R}${DEFAULT_P}${_b64encode(salt)}${_b64encode(derived)}"


def verify_password(password: str, stored: str) -> bool:
    try:
        parts = stored.split("$")
        if len(parts) != 6 or parts[0] != "scrypt":
            return False
        n = int(parts[1])
        r = int(parts[2])
        p = int(parts[3])
        salt = _b64decode(parts[4])
        expected = _b64decode(parts[5])
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
    return f"scrypt${DEFAULT_N}${DEFAULT_R}${DEFAULT_P}${_b64encode(salt)}${_b64encode(derived)}"
