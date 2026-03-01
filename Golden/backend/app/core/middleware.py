"""Authentication dependency helpers for FastAPI route protection."""

import logging
from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import Depends, HTTPException, Request
from jose import JWTError

from app.core.config import settings
from app.core.database import get_conn
from app.core.security import decode_access_token

logger = logging.getLogger(__name__)
_rate_limit_lock = Lock()
_login_failures: dict[str, deque[float]] = defaultdict(deque)


def extract_auth_token(request: Request) -> str | None:
    """Extract JWT from Authorization header or session cookie.

    Priority: `Authorization: Bearer ...` first, then `tdental_session` cookie.
    """
    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        token = auth_header[7:].strip()
        if token:
            return token

    cookie_token = request.cookies.get("tdental_session")
    if cookie_token:
        token = cookie_token.strip()
        if token:
            return token

    return None


def validate_token(token: str, require_session: bool = True) -> dict:
    """Decode token and optionally enforce an active DB session.

    Returns a normalized user dict with keys:
    ``id``, ``sub``, ``name``, ``email``, ``role``.
    """
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    required_claims = ("sub", "name", "email", "role")
    if not all(payload.get(claim) for claim in required_claims):
        raise HTTPException(status_code=401, detail="Token payload missing required claims")

    user = {
        "id": str(payload["sub"]),
        "sub": str(payload["sub"]),
        "name": payload["name"],
        "email": payload["email"],
        "role": payload["role"],
    }
    if not require_session:
        return user

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT u.id::text, u.name, u.email, u.role
                    FROM app_sessions s
                    JOIN app_users u ON u.id = s.user_id
                    WHERE s.token = %s
                      AND s.expires_at > NOW()
                      AND u.active = TRUE
                    LIMIT 1
                    """,
                    (token,),
                )
                row = cur.fetchone()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")
    except Exception:
        logger.exception("Failed to validate session token against database")
        raise HTTPException(status_code=503, detail="Could not validate user session")

    if row is None:
        raise HTTPException(status_code=401, detail="Session is invalid or expired")

    session_user = {
        "id": str(row[0]),
        "sub": str(row[0]),
        "name": row[1],
        "email": row[2],
        "role": row[3],
    }
    if session_user["id"] != user["id"]:
        raise HTTPException(status_code=401, detail="Session user mismatch")

    return session_user


def require_auth(request: Request) -> dict:
    """FastAPI dependency that enforces JWT authentication."""
    token = extract_auth_token(request)
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    return validate_token(token, require_session=True)


def require_admin(user: dict = Depends(require_auth)) -> dict:
    """FastAPI dependency that allows only admin users."""
    role = str(user.get("role") or "").strip().lower()
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def _client_ip(request: Request) -> str:
    """Best-effort client IP extraction for rate-limiting keys."""
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for.strip():
        return forwarded_for.split(",")[0].strip()

    if request.client and request.client.host:
        return request.client.host

    return "unknown"


def _login_key(request: Request, email: str) -> str:
    normalized_email = email.strip().lower()
    return f"{_client_ip(request)}::{normalized_email}"


def _prune_attempts(attempts: deque[float], now: float) -> None:
    window = float(settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS)
    while attempts and (now - attempts[0]) > window:
        attempts.popleft()


def assert_login_allowed(request: Request, email: str) -> None:
    """Reject login when the configured failure threshold has been exceeded."""
    if not settings.ENABLE_RATE_LIMIT:
        return

    now = monotonic()
    key = _login_key(request, email)
    with _rate_limit_lock:
        attempts = _login_failures[key]
        _prune_attempts(attempts, now)
        if len(attempts) >= settings.LOGIN_RATE_LIMIT_MAX_ATTEMPTS:
            raise HTTPException(
                status_code=429,
                detail="Too many login attempts. Please try again later.",
            )


def register_login_failure(request: Request, email: str) -> None:
    """Record one failed login attempt for the client/email key."""
    if not settings.ENABLE_RATE_LIMIT:
        return

    now = monotonic()
    key = _login_key(request, email)
    with _rate_limit_lock:
        attempts = _login_failures[key]
        _prune_attempts(attempts, now)
        attempts.append(now)


def reset_login_failures(request: Request, email: str) -> None:
    """Clear tracked failures after a successful login."""
    if not settings.ENABLE_RATE_LIMIT:
        return

    key = _login_key(request, email)
    with _rate_limit_lock:
        _login_failures.pop(key, None)


def reset_login_rate_limit_state() -> None:
    """Testing helper that clears all in-memory rate-limit counters."""
    with _rate_limit_lock:
        _login_failures.clear()
