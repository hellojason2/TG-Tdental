import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.api import auth, routes
from app.core.database import ensure_auth_tables

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
print(f"DEBUG: static_dir = {static_dir}")
print(f"DEBUG: login.html exists? {os.path.exists(os.path.join(static_dir, 'login.html'))}")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(routes.router, prefix="/api", tags=["api"])

@app.on_event("startup")
async def startup_event():
    ensure_auth_tables()

@app.get("/", response_class=HTMLResponse)
async def serve_viewer():
    with open(os.path.join(static_dir, "tdental.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/login", response_class=HTMLResponse)
async def serve_login():
    with open(os.path.join(static_dir, "login.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8899, reload=True)
