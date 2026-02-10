import os
from fastapi import FastAPI, Request, Cookie
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

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(routes.router, prefix="/api", tags=["api"])

@app.on_event("startup")
async def startup_event():
    ensure_auth_tables()


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
    except Exception:
        return False


@app.get("/", response_class=HTMLResponse)
async def serve_viewer(request: Request):
    """Serve app only if user has a valid session cookie, otherwise redirect to /login."""
    token = request.cookies.get("tdental_session")
    if not token or not verify_session_cookie(token):
        return RedirectResponse(url="/login", status_code=302)
    
    html_path = os.path.join(static_dir, "tdental.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/login", response_class=HTMLResponse)
async def serve_login(request: Request):
    """Serve login page. If already logged in, redirect to /."""
    token = request.cookies.get("tdental_session")
    if token and verify_session_cookie(token):
        return RedirectResponse(url="/", status_code=302)
    
    html_path = os.path.join(static_dir, "login.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8899, reload=True)
