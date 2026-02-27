#!/bin/bash
set -e

echo "╔══════════════════════════════════════════════════╗"
echo "║   🕷️  Website Replicator — Crawler Starting...   ║"
echo "╚══════════════════════════════════════════════════╝"

# Start virtual framebuffer (gives the browser a "screen")
echo "[1/5] Starting Xvfb virtual display..."
Xvfb :99 -screen 0 1920x1080x24 -ac &
sleep 1

# Start lightweight window manager
echo "[2/5] Starting Fluxbox window manager..."
DISPLAY=:99 fluxbox &
sleep 1

# Start VNC server (password-free for local Docker use)
echo "[3/5] Starting VNC server on :5900..."
x11vnc -display :99 -forever -nopw -rfbport 5900 -shared &
sleep 1

# Start noVNC web viewer
echo "[4/5] Starting noVNC web viewer on :6080..."
websockify --web /usr/share/novnc/ 6080 localhost:5900 &
sleep 1

echo "[5/5] Starting Crawler API server on :8001..."
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  🖥️  Live Browser:  http://localhost:6080        ║"
echo "║  📡  Crawler API:   http://localhost:8001/docs   ║"
echo "║  🔗  VNC Direct:    vnc://localhost:5900         ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Start the FastAPI crawler service
DISPLAY=:99 python -m uvicorn api:app --host 0.0.0.0 --port 8001 --reload
