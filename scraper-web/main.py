import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# ── Groq API Key ─────────────────────────────────────────────────────────────
os.environ.setdefault("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))

# Add current dir to path to import local scraper
sys.path.insert(0, os.path.dirname(__file__))
from scraper import SPAScraper
from analyzer import LLMAnalyzer

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Vantage AI - Scraper API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state to track active tasks
tasks = {}

@app.get("/")
async def get_frontend():
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))

class ScrapeRequest(BaseModel):
    base_url: str
    username: Optional[str] = None
    password: Optional[str] = None
    output_name: Optional[str] = "default"

class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: float
    logs: List[str]
    scraped_at: Optional[str] = None

class WebScraperWrapper(SPAScraper):
    """Extended scraper that reports logs to a list/socket"""
    def __init__(self, config, task_id):
        super().__init__(config)
        self.task_id = task_id
        self.logs = []
        
    def _print_to_logs(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {msg}"
        self.logs.append(formatted)
        print(formatted) # Also print to console

    # Override prints in base class (or wrap them)
    # Since scraper uses simple print(), we can mock sys.stdout or just wrap calls
    # For now, we'll manually add logic or let it be

async def run_scrape_task(task_id: str, request: ScrapeRequest):
    output_dir = f"./data/{request.output_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Detect TDental and use known Angular selectors
    is_tdental = 'tdental' in (request.base_url or '').lower()
    
    config = {
        'base_url': request.base_url,
        'output_dir': output_dir,
        'login': {
            # Hardcoded TDental credentials
            'username': 'dataconnect' if is_tdental else request.username,
            'password': 'dataconnect@' if is_tdental else request.password,
            # Angular formcontrolname selectors for TDental
            'username_selector': 'input[formcontrolname="userName"]' if is_tdental else None,
            'password_selector': 'input[formcontrolname="password"]' if is_tdental else None,
            'submit_selector': 'button[type="submit"]' if is_tdental else None,
        },
    }
    
    tasks[task_id] = {
        "status": "running",
        "progress": 0.1,
        "logs": [f"Starting scrape for {request.base_url}..."],
        "output_dir": output_dir
    }
    
    try:
        scraper = SPAScraper(config)
        tasks[task_id]["logs"].append("Launching Playwright...")
        if is_tdental:
            tasks[task_id]["logs"].append("Detected TDental (Angular) — using known selectors")
        await scraper.start()
        
        tasks[task_id]["progress"] = 0.8
        tasks[task_id]["logs"].append("Scraping complete. Running LLM Analysis...")
        
        analyzer = LLMAnalyzer(output_dir, provider='groq')
        analyzer.load_scrape_data()
        
        # Only run analysis if we actually got data
        if analyzer.report:
            analyzer.generate_database_schema()
            analyzer.generate_api_spec()
            analyzer.generate_replication_blueprint()
            tasks[task_id]["logs"].append("AI analysis complete.")
        else:
            tasks[task_id]["logs"].append("Warning: No report data found. Scrape may have partially failed.")
        
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 1.0
        tasks[task_id]["logs"].append("Project analysis finished.")
        tasks[task_id]["scraped_at"] = datetime.now().isoformat()
        
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["logs"].append(f"Error: {str(e)}")
        print(f"Task {task_id} failed: {e}")

@app.post("/api/scrape/start")
async def start_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks):
    task_id = f"task_{datetime.now().strftime('%M%S')}"
    background_tasks.add_task(run_scrape_task, task_id, request)
    return {"task_id": task_id, "message": "Scrape task started in background"}

@app.get("/api/scrape/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

@app.get("/api/reports/latest")
async def get_latest_report():
    # Find newest directory in data/
    if not os.path.exists("./data"):
        return {"error": "No data found"}
    
    dirs = [d for d in os.listdir("./data") if os.path.isdir(os.path.join("./data", d))]
    if not dirs:
        return {"error": "No reports found"}
    
    latest_dir = sorted(dirs)[-1]
    report_path = f"./data/{latest_dir}/full_report.json"
    blueprint_path = f"./data/{latest_dir}/BLUEPRINT.md"
    
    report = {}
    if os.path.exists(report_path):
        with open(report_path) as f:
            report = json.load(f)
            
    blueprint = ""
    if os.path.exists(blueprint_path):
        with open(blueprint_path) as f:
            blueprint = f.read()
            
    return {
        "report": report,
        "blueprint": blueprint,
        "project": latest_dir
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
