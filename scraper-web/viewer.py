from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import secrets

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
HTML_FILE = os.path.join(BASE_DIR, 'tdental.html')

# Mount static files
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

MOCK_USERS = [
    {
        "id": 1,
        "name": "Admin User",
        "email": "admin",
        "role": "admin",
        "permissions": {} 
    },
    {
        "id": 2,
        "name": "Test Viewer",
        "email": "viewer@tdental.vn",
        "role": "viewer",
        "permissions": {
            "dashboard": True,
            "customers": True,
            "reception": True,
            "calendar": True,
            # Restricted:
            "salary": False,
            "cashbook": False,
            "reports": False,
            "users": False,
            "settings": False
        }
    }
]

SESSIONS = {}

@app.get("/")
async def serve_index():
    if os.path.exists(HTML_FILE):
        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Error: tdental.html not found</h1>", status_code=500)

@app.post("/api/auth/login")
async def login(request: Request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    user = next((u for u in MOCK_USERS if u['email'] == email), None)
    
    if user and password == "123456":
        token = secrets.token_hex(16)
        SESSIONS[token] = user
        return JSONResponse(content={"token": token, "user": user})
    
    return JSONResponse(content={"message": "Invalid credentials"}, status_code=401)

@app.get("/api/auth/me")
async def check_session(request: Request):
    auth = request.headers.get('Authorization')
    if not auth or not auth.startswith('Bearer '):
        return JSONResponse(content={"message": "No token"}, status_code=401)
    
    token = auth.split(' ')[1]
    if token in SESSIONS:
        return JSONResponse(content={"user": SESSIONS[token]})
    
    return JSONResponse(content={"message": "Invalid token"}, status_code=401)

@app.post("/api/auth/logout")
async def logout(request: Request):
    auth = request.headers.get('Authorization')
    if auth:
        token = auth.split(' ')[1]
        if token in SESSIONS:
            del SESSIONS[token]
    return JSONResponse(content={"success": True})

# Mock Data Endpoints
@app.get("/api/companies")
async def get_companies():
    return JSONResponse(content={"items": [{"id": 1, "name": "Head Office"}]})

@app.get("/api/dashboard/summary")
async def get_dashboard():
    return JSONResponse(content={
        "revenue": 0,
        "customers": 0,
        "appointments": 0,
        "chart_data": []
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8899)
