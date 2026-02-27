from fastapi import Header, HTTPException, Request
from app.core.database import get_conn, get_cursor
from app.core.utils import serialize


def get_current_user(authorization: str = Header(None)):
    """Validate session token and return user dict or None."""
    token = None
    if authorization and authorization.startswith('Bearer '):
        token = authorization[7:]

    if not token:
        return None

    conn = get_conn()
    try:
        cur = get_cursor(conn)
        cur.execute("""
            SELECT u.id, u.name, u.email, u.role, u.permissions, u.active
            FROM app_sessions s JOIN app_users u ON s.user_id = u.id
            WHERE s.token = %s AND s.expires_at > CURRENT_TIMESTAMP AND u.active = TRUE
        """, [token])
        user = cur.fetchone()
        return serialize(dict(user)) if user else None
    finally:
        conn.close()


def require_auth(request: Request):
    """Dependency that requires authentication for an endpoint."""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""

    if not token:
        # Also check cookie
        token = request.cookies.get("tdental_session", "")

    if not token:
        raise HTTPException(status_code=401, detail="Không có quyền truy cập")

    conn = get_conn()
    cur = get_cursor(conn)
    try:
        cur.execute(
            "SELECT u.* FROM app_sessions s JOIN app_users u ON s.user_id = u.id "
            "WHERE s.token = %s AND s.expires_at > CURRENT_TIMESTAMP AND u.active = TRUE",
            [token]
        )
        user = cur.fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="Phiên đã hết hạn")
        return dict(user)
    finally:
        conn.close()
