"""
Website Replicator — Crawler API
FastAPI server to control the Playwright browser agent.

Endpoints:
  POST /crawl/start      → Start a new crawl job
  GET  /crawl/status/{id} → Check job status  
  GET  /crawl/results/{id} → Get crawl results
  POST /crawl/stop/{id}   → Stop a running job
  GET  /health            → Health check
"""
import asyncio
import json
import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

app = FastAPI(
    title="Website Replicator — Crawler",
    description="Navigate websites like a human, extract everything.",
    version="2.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Models ───────────────────────────────────────────

class CrawlConfig(BaseModel):
    """Configuration for a crawl job"""
    site_url: str = Field(..., description="Target website URL")
    auth_type: str = Field("none", description="Auth type: none | form | api | cookie")
    username: str = ""
    password: str = ""
    login_url: str = Field("", description="Path to login page (for form auth)")
    api_login_endpoint: str = Field("", description="API login endpoint (e.g. api/Account/Login)")
    totp_secret: str = Field("", description="TOTP 2FA secret (if site uses it)")
    max_pages: int = Field(200, description="Max pages to crawl")
    headless: bool = Field(False, description="False = visible in noVNC, True = headless")
    capture_screenshots: bool = True
    capture_hover_states: bool = True
    capture_animations: bool = True
    record_har: bool = Field(True, description="Record ALL network traffic as HAR")
    download_assets: bool = True
    wait_after_nav_ms: int = Field(1500, description="Wait ms after each navigation")
    viewport_width: int = 1920
    viewport_height: int = 1080
    locale: str = "vi-VN"
    timezone: str = "Asia/Ho_Chi_Minh"


class CrawlStatus(BaseModel):
    job_id: str
    status: str  # queued | crawling | analyzing | generating | complete | error | stopped
    pages_crawled: int = 0
    total_routes: int = 0
    api_calls_captured: int = 0
    screenshots_taken: int = 0
    current_page: str = ""
    started_at: Optional[str] = None
    errors: list[str] = []


# ─── State ────────────────────────────────────────────

jobs: dict[str, CrawlStatus] = {}
active_tasks: dict[str, asyncio.Task] = {}


# ─── Endpoints ────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "crawler", "timestamp": datetime.now().isoformat()}


@app.post("/crawl/start", response_model=dict)
async def start_crawl(config: CrawlConfig, background_tasks: BackgroundTasks):
    """Start a new website crawl. Watch live at http://localhost:6080"""
    job_id = uuid.uuid4().hex[:8]
    
    status = CrawlStatus(
        job_id=job_id,
        status="queued",
        started_at=datetime.now().isoformat(),
    )
    jobs[job_id] = status
    
    # Run crawl in background
    background_tasks.add_task(_run_crawl_job, job_id, config)
    
    return {
        "job_id": job_id,
        "status": "queued",
        "vnc_url": "http://localhost:6080",
        "api_docs": "http://localhost:8001/docs",
        "message": f"Crawl started! Watch live at http://localhost:6080",
    }


@app.get("/crawl/status/{job_id}", response_model=CrawlStatus)
async def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(404, f"Job {job_id} not found")
    return jobs[job_id]


@app.get("/crawl/results/{job_id}")
async def get_results(job_id: str):
    """Get all crawl results — screenshots, API map, schema, tokens"""
    base = f"/app/data/{job_id}"
    if not os.path.exists(base):
        raise HTTPException(404, f"No results for job {job_id}")
    
    def load_json(path):
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return None
    
    screenshots = []
    ss_dir = f"{base}/screenshots"
    if os.path.exists(ss_dir):
        screenshots = sorted(os.listdir(ss_dir))
    
    return {
        "job_id": job_id,
        "screenshots": screenshots,
        "screenshot_base_url": f"/screenshots/{job_id}",
        "routes": load_json(f"{base}/routes.json") or [],
        "api_map": load_json(f"{base}/api_map.json") or {},
        "db_schema": load_json(f"{base}/db_schema.json") or {},
        "design_tokens": load_json(f"{base}/design_tokens.json") or {},
        "stats": load_json(f"{base}/stats.json") or {},
    }


@app.get("/screenshots/{job_id}/{filename}")
async def get_screenshot(job_id: str, filename: str):
    path = f"/app/data/{job_id}/screenshots/{filename}"
    if not os.path.exists(path):
        raise HTTPException(404, "Screenshot not found")
    return FileResponse(path, media_type="image/png")


@app.post("/crawl/stop/{job_id}")
async def stop_crawl(job_id: str):
    if job_id not in jobs:
        raise HTTPException(404, f"Job {job_id} not found")
    jobs[job_id].status = "stopped"
    if job_id in active_tasks:
        active_tasks[job_id].cancel()
    return {"status": "stopped", "job_id": job_id}


@app.get("/crawl/jobs")
async def list_jobs():
    return {"jobs": list(jobs.values())}


# ─── Background Task ─────────────────────────────────

async def _run_crawl_job(job_id: str, config: CrawlConfig):
    """Execute the crawl in background"""
    from crawl_engine import SiteReplicator
    
    status = jobs[job_id]
    status.status = "crawling"
    
    try:
        replicator = SiteReplicator(config, f"/app/data/{job_id}", status)
        await replicator.run()
        if status.status != "stopped":
            status.status = "complete"
    except asyncio.CancelledError:
        status.status = "stopped"
    except Exception as e:
        status.status = "error"
        status.errors.append(str(e))
        import traceback
        traceback.print_exc()
