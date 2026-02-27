# 🕷️ Website Replicator v2

**Universal website-to-codebase engine.** Input: URL + credentials → Output: Complete working codebase.

Navigates websites like a human via Playwright, captures everything (screenshots, DOM, API calls, hover states, animations), then generates a full Next.js + Ant Design codebase via Claude/GPT.

## Quick Start

```bash
# 1. Clone and configure
cd website-replicator
cp .env.example .env
# Edit .env with your API keys (Anthropic and/or OpenAI)

# 2. Launch everything
docker compose up -d --build

# 3. Watch the bot crawl live
open http://localhost:6080          # noVNC — live browser view
open http://localhost:8001/docs     # Crawler API docs
open http://localhost:8002/docs     # AI Engine API docs
```

## Start a Crawl (TDental Example)

```bash
curl -X POST http://localhost:8001/crawl/start \
  -H "Content-Type: application/json" \
  -d '{
    "site_url": "https://tamdentist.tdental.vn",
    "auth_type": "api",
    "api_login_endpoint": "api/Account/Login",
    "username": "dataconnect",
    "password": "dataconnect@",
    "max_pages": 50,
    "headless": false,
    "capture_screenshots": true,
    "capture_hover_states": true,
    "record_har": true,
    "locale": "vi-VN",
    "timezone": "Asia/Ho_Chi_Minh"
  }'
```

Then open **http://localhost:6080** and watch the bot navigate!

## Check Status & Get Results

```bash
# Check progress
curl http://localhost:8001/crawl/status/{job_id}

# Get all results
curl http://localhost:8001/crawl/results/{job_id}

# List all jobs
curl http://localhost:8001/crawl/jobs
```

## Generate Code

```bash
# Option 1: Generate Cursor mega-prompt (NO AI key needed)
curl -X POST http://localhost:8002/generate/prompt \
  -H "Content-Type: application/json" \
  -d '{"job_id": "YOUR_JOB_ID"}'

# Option 2: Generate Prisma schema
curl -X POST http://localhost:8002/generate/schema \
  -H "Content-Type: application/json" \
  -d '{"job_id": "YOUR_JOB_ID", "provider": "anthropic"}'

# Option 3: Generate a single page
curl -X POST http://localhost:8002/generate/page \
  -H "Content-Type: application/json" \
  -d '{"job_id": "YOUR_JOB_ID", "route": "/partners"}'

# Option 4: Generate full codebase (all pages)
curl -X POST http://localhost:8002/generate \
  -H "Content-Type: application/json" \
  -d '{"job_id": "YOUR_JOB_ID", "provider": "anthropic"}'
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│                 docker compose                   │
├──────────────┬──────────────┬───────────────────┤
│   crawler    │   ai-engine  │   infrastructure  │
│              │              │                   │
│  Playwright  │  Claude/GPT  │  Redis            │
│  + stealth   │  + Vision    │  PostgreSQL       │
│  + HAR rec   │  + Jinja2    │                   │
│  + noVNC     │              │                   │
│              │              │                   │
│  :6080 vnc   │  :8002 api   │  :6379 redis      │
│  :8001 api   │              │  :5432 postgres   │
└──────────────┴──────────────┴───────────────────┘
```

## What Gets Captured

| Data | File | Description |
|------|------|-------------|
| Screenshots | `data/{job}/screenshots/*.png` | Full-page screenshot of every route |
| DOM Trees | `data/{job}/dom/*.json` | Complete DOM with computed styles |
| API Map | `data/{job}/api_map.json` | All API calls grouped by controller |
| DB Schema | `data/{job}/db_schema.json` | Inferred schema from API responses |
| Design Tokens | `data/{job}/design_tokens.json` | Colors, fonts, spacing, shadows |
| Hover States | `data/{job}/hover/*.json` | Style diffs on mouseenter/leave |
| Animations | `data/{job}/animations/*.json` | CSS keyframes + transitions |
| HAR Recording | `data/{job}/har/full_recording.har` | Complete network traffic log |
| Routes | `data/{job}/routes.json` | All discovered SPA routes |
| Raw API Calls | `data/{job}/api_calls_raw.json` | Every captured API response body |

## Supported Auth Methods

- **API Login** (JWT) — POST credentials, store token in localStorage
- **Form Login** — Auto-detect username/password fields, submit
- **Cookie Injection** — Provide session cookies directly
- **None** — Public sites, no auth needed

## Configuration

See `configs/tdental.yaml` for a full example. Key options:

- `max_pages` — Cap on pages to crawl (default 200)
- `headless` — `false` to watch via noVNC, `true` for speed
- `capture_hover_states` — Detect style changes on hover
- `record_har` — Record ALL network traffic as HAR file
- `wait_after_nav_ms` — Wait time after each navigation (for SPAs)

## Output Structure

```
data/{job_id}/
├── screenshots/           # Full-page PNGs
├── dom/                   # DOM trees with computed styles
├── hover/                 # Hover state diffs
├── animations/            # CSS keyframes
├── har/                   # Network traffic recording
├── generated/             # AI-generated code
│   ├── pages/             # React page components
│   └── prisma/            # Prisma schema
├── routes.json            # All SPA routes
├── api_map.json           # API endpoints by controller
├── db_schema.json         # Inferred database schema
├── design_tokens.json     # Color/font/spacing system
├── api_calls_raw.json     # Raw API response bodies
├── cursor_prompt.md       # Mega-prompt for Cursor/Claude Code
└── stats.json             # Crawl statistics
```
