"""Authentication routes: login, session check, logout."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel

from app.core.config import settings
from app.core.database import get_conn
from app.core.middleware import (
    assert_login_allowed,
    extract_auth_token,
    register_login_failure,
    require_auth,
    reset_login_failures,
)
from app.core.security import (
    ACCESS_TOKEN_EXPIRE_DAYS,
    create_access_token,
    hash_password,
    is_bcrypt_hash,
    verify_password,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: str


class LoginResponse(BaseModel):
    token: str
    user: UserOut


# ---------------------------------------------------------------------------
# Table bootstrapping
# ---------------------------------------------------------------------------

_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS app_users (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'viewer',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS app_sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES app_users(id) ON DELETE CASCADE,
    token TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_app_sessions_user_id ON app_sessions(user_id);
DROP INDEX IF EXISTS idx_app_sessions_token;
CREATE INDEX IF NOT EXISTS idx_app_sessions_token ON app_sessions(token);
"""

_DEFAULT_ADMIN_EMAIL = "admin@tdental.vn"
_DEFAULT_ADMIN_PASSWORD = "admin123"


def _cookie_samesite() -> str:
    value = settings.COOKIE_SAMESITE.lower()
    if value not in {"lax", "strict", "none"}:
        return "lax"
    return value


def ensure_auth_tables(conn) -> None:
    """Create auth tables if they don't exist, then seed default admin."""
    with conn.cursor() as cur:
        cur.execute(_TABLES_SQL)

        # Seed default admin when the table is empty
        cur.execute("SELECT COUNT(*) FROM app_users")
        count = cur.fetchone()[0]
        if count == 0:
            hashed = hash_password(_DEFAULT_ADMIN_PASSWORD)
            cur.execute(
                """
                INSERT INTO app_users (id, name, email, password, role, active)
                VALUES (%s, %s, %s, %s, %s, TRUE)
                """,
                (str(uuid4()), "Admin", _DEFAULT_ADMIN_EMAIL, hashed, "admin"),
            )
            logger.info("Seeded default admin user: %s", _DEFAULT_ADMIN_EMAIL)


def bootstrap_auth_tables() -> None:
    """Ensure auth tables exist and default admin account is available."""
    with get_conn() as conn:
        ensure_auth_tables(conn)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, request: Request, response: Response):
    """Authenticate with email + password, return JWT and set session cookie."""
    normalized_email = body.email.strip().lower()
    assert_login_allowed(request, normalized_email)
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name, email, password, role, active "
                    "FROM app_users WHERE LOWER(email) = %s AND active = true",
                    (normalized_email,),
                )
                row = cur.fetchone()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")

    if row is None:
        register_login_failure(request, normalized_email)
        raise HTTPException(
            status_code=401,
            detail="Email hoặc mật khẩu không đúng",
        )

    user_id, name, email, hashed_pw, role, _active = row

    if not verify_password(body.password, hashed_pw):
        register_login_failure(request, normalized_email)
        raise HTTPException(
            status_code=401,
            detail="Email hoặc mật khẩu không đúng",
        )
    reset_login_failures(request, normalized_email)

    if not is_bcrypt_hash(hashed_pw):
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE app_users SET password = %s, updated_at = NOW() WHERE id = %s",
                        (hash_password(body.password), str(user_id)),
                    )
            logger.info("Upgraded legacy password hash to bcrypt for user %s", email)
        except Exception:
            logger.warning(
                "Failed to upgrade legacy password hash for user %s", email, exc_info=True
            )

    # Build JWT
    token = create_access_token(
        {
            "sub": str(user_id),
            "name": name,
            "email": email,
            "role": role,
        }
    )

    # Persist session row
    expires_at = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO app_sessions (id, user_id, token, expires_at) "
                    "VALUES (%s, %s, %s, %s)",
                    (str(uuid4()), str(user_id), token, expires_at),
                )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")

    # Set HttpOnly cookie
    max_age = ACCESS_TOKEN_EXPIRE_DAYS * 86400  # seconds
    response.set_cookie(
        key="tdental_session",
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=_cookie_samesite(),
        path="/",
        max_age=max_age,
    )

    return LoginResponse(
        token=token,
        user=UserOut(id=str(user_id), name=name, email=email, role=role),
    )


@router.get("/session")
async def session(user: dict = Depends(require_auth)):
    """Return the currently authenticated user."""
    return {
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
        }
    }


@router.post("/logout")
async def logout(request: Request, response: Response):
    """Clear session cookie and delete session record if possible."""
    token = extract_auth_token(request)

    # Attempt to remove session row from database
    if token:
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM app_sessions WHERE token = %s", (token,))
        except Exception:
            logger.warning("Failed to delete session record", exc_info=True)

    # Delete the cookie regardless
    response.delete_cookie(
        key="tdental_session",
        path="/",
        secure=settings.COOKIE_SECURE,
        httponly=True,
        samesite=_cookie_samesite(),
    )

    return {"message": "Đã đăng xuất"}
