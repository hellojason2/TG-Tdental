"""Password hashing and JWT token utilities for TDental authentication."""

from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from app.core.config import settings

# ---------------------------------------------------------------------------
# Config constants (derived from central Settings so there is one source)
# ---------------------------------------------------------------------------
SECRET_KEY: str = settings.SECRET_KEY
ALGORITHM: str = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_DAYS: int = settings.JWT_EXPIRE_DAYS

# ---------------------------------------------------------------------------
# Password hashing (bcrypt via passlib)
# ---------------------------------------------------------------------------
_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Return a bcrypt hash of *password*."""
    return _pwd_ctx.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Return ``True`` if *plain* matches *hashed*.

    Primary verification uses bcrypt. A minimal legacy fallback is kept so
    old plaintext/SHA-256 rows can be upgraded to bcrypt on successful login.
    """
    if not hashed:
        return False

    try:
        return _pwd_ctx.verify(plain, hashed)
    except (UnknownHashError, ValueError, TypeError):
        pass

    if hmac.compare_digest(hashed, plain):
        return True

    legacy_sha256 = hashlib.sha256(plain.encode("utf-8")).hexdigest()
    return hmac.compare_digest(hashed.lower(), legacy_sha256)


def is_bcrypt_hash(value: str) -> bool:
    """Return ``True`` when *value* is stored as a bcrypt digest."""
    return value.startswith(("$2a$", "$2b$", "$2y$"))


# ---------------------------------------------------------------------------
# JWT access tokens
# ---------------------------------------------------------------------------

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT containing *data*.

    The token payload always includes:
    - ``sub``   – user id
    - ``name``  – display name
    - ``email`` – user email
    - ``role``  – user role
    - ``exp``   – expiration timestamp

    Parameters
    ----------
    data:
        Must contain at least ``sub``.  ``name``, ``email``, and ``role``
        are copied through if present.
    expires_delta:
        Custom lifetime.  Defaults to ``ACCESS_TOKEN_EXPIRE_DAYS`` days.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT.

    Returns the payload dict on success.
    Raises ``jose.JWTError`` on any failure (expired, bad signature, etc.).
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
