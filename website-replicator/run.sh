#!/bin/bash
# ═══════════════════════════════════════════════════════
# Website Replicator — Full Pipeline Runner
#
# Usage:
#   ./run.sh crawl              # Step 1: Crawl TDental
#   ./run.sh generate <job_id>  # Step 2: Generate code from crawl
#   ./run.sh full               # Both steps, back to back
#   ./run.sh status <job_id>    # Check crawl status
#   ./run.sh list               # List all crawl jobs
# ═══════════════════════════════════════════════════════
set -euo pipefail

CRAWLER_URL="http://localhost:8001"
AI_URL="http://localhost:8002"

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

log() { echo -e "${CYAN}[$(date +%H:%M:%S)]${NC} $1"; }
ok()  { echo -e "${GREEN}✓${NC} $1"; }
err() { echo -e "${RED}✗${NC} $1" >&2; }

# ─── Commands ─────────────────────────────────────────

cmd_crawl() {
    log "Starting TDental crawl..."
    
    RESPONSE=$(curl -s -X POST "${CRAWLER_URL}/crawl/start" \
        -H "Content-Type: application/json" \
        -d '{
            "site_url": "https://tamdentist.tdental.vn",
            "auth_type": "api",
            "api_login_endpoint": "api/Account/Login",
            "username": "dataconnect",
            "password": "dataconnect@",
            "max_pages": 200,
            "headless": false,
            "capture_screenshots": true,
            "capture_hover_states": true,
            "capture_animations": true,
            "record_har": true,
            "locale": "vi-VN",
            "timezone": "Asia/Ho_Chi_Minh"
        }')
    
    JOB_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('job_id',''))" 2>/dev/null || echo "")
    
    if [ -z "$JOB_ID" ]; then
        err "Failed to start crawl. Response: $RESPONSE"
        err "Is the crawler running? Try: docker compose up -d"
        exit 1
    fi
    
    ok "Crawl started: ${BOLD}${JOB_ID}${NC}"
    log "Watch live: ${BOLD}http://localhost:6080${NC}"
    log "Check status: ${BOLD}./run.sh status ${JOB_ID}${NC}"
    echo ""
    echo "$JOB_ID"
}

cmd_status() {
    local JOB_ID="${1:-}"
    if [ -z "$JOB_ID" ]; then
        err "Usage: ./run.sh status <job_id>"
        exit 1
    fi
    
    curl -s "${CRAWLER_URL}/crawl/status/${JOB_ID}" | python3 -m json.tool
}

cmd_list() {
    log "Crawl data directories:"
    ls -la data/ 2>/dev/null || echo "  (none yet — run a crawl first)"
}

cmd_generate() {
    local JOB_ID="${1:-}"
    local MODEL="${2:-claude-sonnet-4-20250514}"
    local MAX_PAGES="${3:-0}"
    
    if [ -z "$JOB_ID" ]; then
        err "Usage: ./run.sh generate <job_id> [model] [max_pages]"
        err "  model: claude-sonnet-4-20250514 (default) | claude-opus-4-20250514"
        err "  max_pages: 0 for all (default)"
        exit 1
    fi
    
    CRAWL_DIR="data/${JOB_ID}"
    if [ ! -d "$CRAWL_DIR" ]; then
        err "Crawl directory not found: $CRAWL_DIR"
        err "Run a crawl first: ./run.sh crawl"
        exit 1
    fi
    
    log "Generating code from crawl: ${BOLD}${JOB_ID}${NC}"
    log "Model: ${MODEL}"
    log "Output: ${CRAWL_DIR}/generated/"
    echo ""
    
    # Run the pipeline inside the ai-engine container
    docker compose exec ai-engine python generate_pipeline.py \
        "/app/${CRAWL_DIR}" \
        --model "$MODEL" \
        --max-pages "$MAX_PAGES"
    
    ok "Generation complete!"
    log "Output: ${CRAWL_DIR}/generated/"
    log "To run the app:"
    echo "  cd ${CRAWL_DIR}/generated"
    echo "  npm install"
    echo "  npm run dev"
}

cmd_generate_local() {
    # Run pipeline locally (without Docker) — for dev/testing
    local JOB_ID="${1:-}"
    local MODEL="${2:-claude-sonnet-4-20250514}"
    local MAX_PAGES="${3:-0}"
    
    if [ -z "$JOB_ID" ]; then
        err "Usage: ./run.sh generate-local <job_id> [model] [max_pages]"
        exit 1
    fi
    
    CRAWL_DIR="data/${JOB_ID}"
    if [ ! -d "$CRAWL_DIR" ]; then
        err "Crawl directory not found: $CRAWL_DIR"
        exit 1
    fi
    
    log "Running pipeline locally..."
    cd ai-engine
    python generate_pipeline.py \
        "../${CRAWL_DIR}" \
        --model "$MODEL" \
        --max-pages "$MAX_PAGES"
}

cmd_prompt() {
    # Generate Cursor mega-prompt only (no AI API needed)
    local JOB_ID="${1:-}"
    
    if [ -z "$JOB_ID" ]; then
        err "Usage: ./run.sh prompt <job_id>"
        exit 1
    fi
    
    curl -s -X POST "${AI_URL}/generate/prompt" \
        -H "Content-Type: application/json" \
        -d "{\"job_id\": \"${JOB_ID}\"}" | python3 -m json.tool
}

cmd_full() {
    log "${BOLD}Full pipeline: Crawl → Wait → Generate${NC}"
    echo ""
    
    # Step 1: Start crawl
    JOB_ID=$(cmd_crawl | tail -1)
    
    # Step 2: Wait for crawl to complete
    log "Waiting for crawl to complete..."
    log "Watch live at http://localhost:6080"
    echo ""
    
    while true; do
        STATUS=$(curl -s "${CRAWLER_URL}/crawl/status/${JOB_ID}" 2>/dev/null || echo '{"status":"unknown"}')
        STATE=$(echo "$STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null || echo "unknown")
        PAGES=$(echo "$STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('pages_visited',0))" 2>/dev/null || echo "?")
        APIS=$(echo "$STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('api_calls_captured',0))" 2>/dev/null || echo "?")
        
        echo -ne "\r  Status: ${STATE} | Pages: ${PAGES} | APIs: ${APIS}    "
        
        if [ "$STATE" = "completed" ] || [ "$STATE" = "failed" ]; then
            echo ""
            break
        fi
        
        sleep 10
    done
    
    if [ "$STATE" = "failed" ]; then
        err "Crawl failed!"
        exit 1
    fi
    
    ok "Crawl complete!"
    echo ""
    
    # Step 3: Generate
    cmd_generate "$JOB_ID"
}

# ─── Main ─────────────────────────────────────────────

CMD="${1:-help}"
shift || true

case "$CMD" in
    crawl)          cmd_crawl ;;
    status)         cmd_status "$@" ;;
    list)           cmd_list ;;
    generate)       cmd_generate "$@" ;;
    generate-local) cmd_generate_local "$@" ;;
    prompt)         cmd_prompt "$@" ;;
    full)           cmd_full ;;
    up)             docker compose up -d --build ;;
    down)           docker compose down ;;
    logs)           docker compose logs -f "${1:-crawler}" ;;
    *)
        echo ""
        echo -e "${BOLD}Website Replicator${NC} — Universal website-to-code engine"
        echo ""
        echo "Commands:"
        echo "  ${CYAN}crawl${NC}              Start crawling TDental"
        echo "  ${CYAN}status <job_id>${NC}    Check crawl progress"
        echo "  ${CYAN}list${NC}               List all crawl jobs"
        echo "  ${CYAN}generate <job_id>${NC}  Generate code from crawl data"
        echo "  ${CYAN}generate <id> claude-opus-4-20250514${NC}  Use Opus for max quality"
        echo "  ${CYAN}prompt <job_id>${NC}    Generate Cursor mega-prompt (free)"
        echo "  ${CYAN}full${NC}               Crawl + wait + generate (one shot)"
        echo ""
        echo "Docker:"
        echo "  ${CYAN}up${NC}                 Start all services"
        echo "  ${CYAN}down${NC}               Stop all services"
        echo "  ${CYAN}logs [service]${NC}     View logs (crawler|ai-engine)"
        echo ""
        echo "Live browser: http://localhost:6080"
        echo "Crawler API:  http://localhost:8001/docs"
        echo "AI Engine:    http://localhost:8002/docs"
        echo ""
        ;;
esac
