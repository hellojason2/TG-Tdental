import secrets
import hashlib
from datetime import datetime, timedelta
from fastapi import APIRouter, Header, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.core.database import get_conn, get_cursor
from app.core.config import settings
from app.core.security import verify_password

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

def serialize(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

@router.post("/login")
async def auth_login(data: LoginRequest):
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
        return {
            "success": True,
            "token": token,
            "user": user_data
        }
    finally:
        conn.close()

@router.get("/me")
async def auth_me(authorization: str = Header(None)):
    token = None
    if authorization and authorization.startswith('Bearer '):
        token = authorization[7:]
    
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
            
        return {"user": user}
    finally:
        conn.close()
