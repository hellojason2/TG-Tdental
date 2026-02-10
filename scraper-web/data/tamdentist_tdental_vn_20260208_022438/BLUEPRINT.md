# Replication Blueprint
## Source: https://tamdentist.tdental.vn/

## Tech Stack Recommendation
- **Frontend:** React + TypeScript + Ant Design (or Element UI if Vue detected)
- **Backend:** Node.js + Express (or FastAPI/Python)
- **Database:** PostgreSQL
- **Auth:** JWT-based (tokens found in localStorage)
- **Framework detected:** Angular

## Architecture Overview

### Routes (0)

### API Endpoints (1)
- `POST /api/Account/Login` (called 1x)

### Database Tables (0)

### Frontend Pages

## Implementation Order
1. **Database:** Create tables from `database_schema.sql`
2. **Backend API:** Implement endpoints from `api_specification.json`
3. **Auth:** JWT login/logout based on captured auth flow
4. **Layout:** Sidebar + topbar + breadcrumbs shell
5. **CRUD Pages:** Implement each route with its forms/tables
6. **Advanced Features:** Modals, tabs, filters, search

## Files Generated
- `full_report.json` - Complete scrape data
- `database_schema.sql` - PostgreSQL schema
- `api_specification.json` - API endpoint specs
- `component_tree.json` - Frontend component hierarchy
- `screenshots/` - Visual reference for each page
- `api_responses/` - Sample API response data
- `dom_snapshots/` - HTML snapshots per route
