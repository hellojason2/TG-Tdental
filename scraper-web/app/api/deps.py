from fastapi import Header, HTTPException
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
