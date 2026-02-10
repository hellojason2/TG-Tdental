import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from app.api import auth, routes
from app.core.database import ensure_auth_tables, get_conn, get_cursor

app = FastAPI(title="TDental Viewer")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve paths relative to the project root (where Dockerfile WORKDIR is /app)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # /app
STATIC_DIR = os.path.join(BASE_DIR, "static")
TDENTAL_HTML = os.path.join(STATIC_DIR, "tdental.html")
LOGIN_HTML = os.path.join(STATIC_DIR, "login.html")

# Fallback: if static/tdental.html not found, try root tdental.html
if not os.path.exists(TDENTAL_HTML):
    TDENTAL_HTML = os.path.join(BASE_DIR, "tdental.html")

print(f"[BOOT] BASE_DIR={BASE_DIR}")
print(f"[BOOT] STATIC_DIR={STATIC_DIR} exists={os.path.exists(STATIC_DIR)}")
print(f"[BOOT] TDENTAL_HTML={TDENTAL_HTML} exists={os.path.exists(TDENTAL_HTML)}")
print(f"[BOOT] LOGIN_HTML={LOGIN_HTML} exists={os.path.exists(LOGIN_HTML)}")

# Mount static files
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(routes.router, prefix="/api", tags=["api"])

@app.on_event("startup")
async def startup_event():
    try:
        ensure_auth_tables()
        print("[BOOT] Auth tables ready")
    except Exception as e:
        print(f"[BOOT] WARNING: ensure_auth_tables failed: {e}")


def verify_session_cookie(token: str) -> bool:
    """Check if a session token is valid in the database."""
    if not token:
        return False
    try:
        conn = get_conn()
        cur = get_cursor(conn)
        cur.execute(
            "SELECT 1 FROM app_sessions s JOIN app_users u ON s.user_id = u.id "
            "WHERE s.token = %s AND s.expires_at > CURRENT_TIMESTAMP AND u.active = TRUE",
            [token]
        )
        valid = cur.fetchone() is not None
        conn.close()
        return valid
    except Exception as e:
        print(f"[AUTH] verify_session_cookie error: {e}")
        return False


@app.get("/", response_class=HTMLResponse)
async def serve_viewer(request: Request):
    """Serve app only if user has a valid session cookie."""
    token = request.cookies.get("tdental_session")
    if not token or not verify_session_cookie(token):
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        with open(TDENTAL_HTML, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>Error: tdental.html not found</h1>", status_code=500)


@app.get("/login", response_class=HTMLResponse)
async def serve_login(request: Request):
    """Serve login page. If already logged in, redirect to /."""
    token = request.cookies.get("tdental_session")
    if token and verify_session_cookie(token):
        return RedirectResponse(url="/", status_code=302)
    
    try:
        with open(LOGIN_HTML, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>Error: login.html not found</h1>", status_code=500)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8899))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
