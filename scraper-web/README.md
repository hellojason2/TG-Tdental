# Vantage AI - Scraper Web Implementation

## Overview
A high-fidelity web interface for the `SPAScraper` engine, designed to reverse-engineer Single Page Applications (SPAs) and extract API definitions, database schemas, and architectural blueprints.

## Components
- **Dashboard Interface:** `index.html` (Tailwind, Lucide, Glassmorphism).
- **Orchestration Layer:** `main.py` (FastAPI).
- **Scanning Engine:** `scraper.py` (Playwright).
- **Intelligence Layer:** `analyzer.py` (Rule-based + LLM analysis).

## Usage
1. Start server: `python3 main.py` in `scraper-web/`.
2. Access: `http://localhost:8000`.
3. Input Target URL (e.g., Dental management portals).
4. Run Pipeline: Agent will login, traverse all routes, and map API traffic.
5. Review results in the 'API Map' and 'DB Schema' tabs.

## External Integration
The dashboard exposes a public endpoint at `/api/reports/latest` which returns the most recent scrape results in JSON format, allowing other websites to "pull back" live information discovered by the scraper.
