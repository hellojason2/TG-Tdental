# TDental Parity Documentation

## Overview
This directory contains the parity harness for comparing the local TDental replica against the live TDental application.

## Files

### Route Parity Matrix
- `route-parity-matrix.json` - Complete mapping of live routes to local routes with expected widgets

### Severity & Criteria
- `MISMATCH_SEVERITY_RUBRIC.md` - Classification system for visual/behavioral mismatches
- `PARITY_DONE_CRITERIA.md` - Exact acceptance criteria per route

### Capture Scripts
- `scripts/parity_capture.py` - Playwright-based screenshot capture for local and live

## Quick Start

### 1. Run Local Server
```bash
cd /Users/thuanle/Documents/TamTMV/Tdental/scraper-web
python -m app.main
```
Server runs on http://localhost:8899

### 2. Open Compare Tool
Navigate to: http://localhost:8899/compare.html

### 3. Login to Both
- Click "Auto Login" to login to local (admin@tdental.vn / admin123)
- Open live TDental in a separate tab and login manually

### 4. Compare Routes
Use the quick links to navigate both local and live to the same route.

## Capture Workflow

### Option 1: Manual Capture (Browser)
1. Open compare.html
2. Navigate to route on both sides
3. Use Screenshot button to capture comparison
4. Save screenshots for documentation

### Option 2: Automated Capture (Playwright)
```bash
# Install dependencies
pip install playwright
playwright install chromium

# Capture single route
python scripts/parity_capture.py --route dashboard --capture baseline

# Capture all routes
python scripts/parity_capture.py --all --capture baseline
```

## Route Mapping Reference

| Live Route | Local Route | Local Hash |
|------------|--------------|------------|
| #/dashboard | #dashboard | dashboard |
| #/partners/customers | #customers | customers |
| #/reception | #reception | reception |
| #/calendar | #calendar | calendar |
| #/treatments | #treatments | treatments |
| #/sale-management | #purchase | purchase |
| #/stock | #inventory | inventory |
| #/hr/employees | #salary | salary |
| #/accounting | #cashbook | cashbook |
| #/callcenter | #callcenter | callcenter |
| #/reports | #reports | reports |
| #/categories | #categories | categories |
| #/locations | #locations | locations |
| #/users | #users | users |
| #/settings | #settings | settings |

## Viewport Standards
- Desktop: 1440x900
- Tablet: 768x1024
- Mobile: 375x667

## Severity Thresholds

| Priority | Critical | High | Medium | Minor |
|----------|----------|------|--------|-------|
| Critical Routes | 0 | 0 | 2 | 5 |
| High Priority | 0 | 1 | 3 | 7 |
| Medium Priority | 0 | 2 | 5 | 10 |
| Low Priority | 0 | 3 | 7 | 15 |

## Issue Tracking

When logging issues, include:
1. Route affected
2. Severity level
3. Category (layout, typography, visual, interaction, component, behavioral)
4. Live behavior vs local behavior
5. Screenshot reference
6. Steps to reproduce
