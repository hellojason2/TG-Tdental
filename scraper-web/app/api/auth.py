import secrets
import time
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.core.database import get_conn, get_cursor
from app.core.config import settings
from app.core.security import verify_password

router = APIRouter()

# ── Rate limiting ──────────────────────────────────────────────────────────────
_login_attempts: dict = defaultdict(list)
_MAX_ATTEMPTS = 5
_WINDOW_SECONDS = 300  # 5 minutes


def _check_rate_limit(ip: str) -> bool:
    now = time.time()
    _login_attempts[ip] = [t for t in _login_attempts[ip] if now - t < _WINDOW_SECONDS]
    if len(_login_attempts[ip]) >= _MAX_ATTEMPTS:
        return False
    _login_attempts[ip].append(now)
    return True


# ── Session cleanup ────────────────────────────────────────────────────────────
def cleanup_expired_sessions():
    """Remove expired sessions from the database."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM app_sessions WHERE expires_at < CURRENT_TIMESTAMP")
        deleted = cur.rowcount
        conn.commit()
        conn.close()
        if deleted > 0:
            print(f"[AUTH] Cleaned up {deleted} expired sessions")
    except Exception:
        pass


def serialize(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
async def auth_login(data: LoginRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if not _check_rate_limit(client_ip):
        return JSONResponse(
            {"message": "Quá nhiều lần thử. Vui lòng đợi 5 phút."},
            status_code=429
        )

    email = data.email.strip().lower()
    password = data.password

    if not email or not password:
        return JSONResponse({"message": "Vui lòng nhập email và mật khẩu"}, status_code=400)

    conn = get_conn()
    try:
        cur = get_cursor(conn)
        cur.execute("SELECT * FROM app_users WHERE LOWER(email) = %s", [email])
        user = cur.fetchone()

        if not user or not verify_password(password, user['password']):
            return JSONResponse({"message": "Email hoặc mật khẩu không đúng"}, status_code=401)

        if not user['active']:
            return JSONResponse({"message": "Tài khoản đã bị vô hiệu hóa"}, status_code=403)

        # Create session token (30 day expiry)
        token = secrets.token_urlsafe(32)
        expires = datetime.now() + timedelta(days=30)
        cur.execute("INSERT INTO app_sessions (token, user_id, expires_at) VALUES (%s, %s, %s)",
                    [token, user['id'], expires])
        conn.commit()

        user_data = {
            "id": user['id'], "name": user['name'], "email": user['email'],
            "role": user['role'], "permissions": user['permissions'],
        }

        response = JSONResponse({
            "success": True,
            "token": token,
            "user": user_data
        })
        response.set_cookie(
            key="tdental_session",
            value=token,
            httponly=True,
            samesite="lax",
            max_age=30 * 24 * 3600,  # 30 days
            path="/"
        )
        return response
    finally:
        conn.close()


@router.post("/logout")
async def auth_logout(request: Request, authorization: str = Header(None)):
    token = None
    if authorization and authorization.startswith('Bearer '):
        token = authorization[7:]
    if not token:
        token = request.cookies.get("tdental_session", "")

    if token:
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("DELETE FROM app_sessions WHERE token = %s", [token])
            conn.commit()
            conn.close()
        except Exception:
            pass

    response = JSONResponse({"message": "Logged out"})
    response.delete_cookie("tdental_session", path="/")
    return response


@router.get("/me")
async def auth_me(request: Request, authorization: str = Header(None)):
    token = None
    if authorization and authorization.startswith('Bearer '):
        token = authorization[7:]
    if not token:
        token = request.cookies.get("tdental_session", "")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    conn = get_conn()
    try:
        cur = get_cursor(conn)
        cur.execute("""
            SELECT u.id, u.name, u.email, u.role, u.permissions, u.active
            FROM app_sessions s JOIN app_users u ON s.user_id = u.id
            WHERE s.token = %s AND s.expires_at > CURRENT_TIMESTAMP AND u.active = TRUE
        """, [token])
        user = cur.fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")

        return {"user": dict(user)}
    finally:
        conn.close()
