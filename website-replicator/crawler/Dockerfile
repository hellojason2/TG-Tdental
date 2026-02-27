# ═══════════════════════════════════════════
# Website Replicator — Crawler Container
# Base: Official Microsoft Playwright Python image
# Includes: Chromium, Firefox, noVNC viewer, xvfb
# ═══════════════════════════════════════════
FROM mcr.microsoft.com/playwright/python:v1.50.0-noble

ENV DEBIAN_FRONTEND=noninteractive

# System deps for noVNC + virtual display
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    x11vnc \
    fluxbox \
    novnc \
    websockify \
    curl \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --break-system-packages --ignore-installed -r requirements.txt

# Install browsers (chromium already included, add firefox for backup)
RUN playwright install --with-deps chromium

# Copy application code
COPY . .

# Startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 6080 5900 8001

CMD ["/start.sh"]
