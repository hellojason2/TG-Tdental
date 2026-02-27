# TDental Viewer & Scraper - Master Brain File

## Project Architecture Overview

This is a comprehensive tool suite for scraping, analyzing, and replicating the TDental dental clinic management system. The project consists of three main components:

### 1. TDental Viewer (Web App)
- **Tech Stack**: FastAPI (Python) + HTML/CSS/JS (Vanilla)
- **Purpose**: Local replica of TDental dashboard with full CRUD operations
- **Features**: Login, Dashboard, Customers, Appointments, Reports, Inventory, HR, Finance
- **Port**: 8899

### 2. Scraper (`app/services/scraper.py`)
- **Tech Stack**: Playwright (headless browser automation)
- **Purpose**: Reverse-engineer TDental SPA by capturing API traffic, DOM structure, and screenshots
- **Output**: Complete replication blueprint with database schema, API specs, and component tree

### 3. Sync Engine (`app/services/sync.py`)
- **Tech Stack**: Python + PostgreSQL + JWT auth
- **Purpose**: Middleware that polls TDental API and syncs data to Railway PostgreSQL
- **Flow**: TDental.vn → TDentalMiddle → Railway DB → KOL TG

## Current State of Every Module

### ✅ Working
- **Authentication System**: JWT-based login with session management
- **Customer CRUD**: Full create, read, update, delete operations
- **Appointment Management**: Calendar view and appointment CRUD
- **User Management**: Admin role with user creation and permission management
- **Database Schema**: Complete PostgreSQL schema with proper relationships
- **Scraper**: Automated SPA reverse engineering with Playwright
- **Analyzer**: LLM-powered analysis generating database schema and API specs

### 🔄 In-Progress
- **Deep Customer Sync**: Enriching customer data with treatments and appointments
- **Full Data Sync**: Remaining tables (SO, payments, receipts, etc.)
- **Frontend Replication**: Building complete Angular clone

### ❌ Known Issues
- **CORS**: API backend blocks requests from localhost (server-side issue)
- **Inventory Features**: Kho, Nhân sự, Kế toán, Cài đặt marked as "coming soon"
- **Chat Widget**: Stubbed with alert message

## Hard Rules (NEVER Touch These)

### Database Rules
- **NEVER** modify the `customers` table structure without updating all related foreign keys
- **NEVER** delete `app_users` records while sessions are active
- **NEVER** change UUID primary key formats across tables

### API Rules
- **NEVER** expose raw database queries in API responses
- **NEVER** bypass authentication middleware in any route
- **NEVER** modify JWT token structure without updating all clients

### Scraper Rules
- **NEVER** run scraper without proper login credentials
- **NEVER** overwrite existing scrape data without backup
- **NEVER** modify Playwright selectors without testing

## File Ownership Map

### Core Application Files
- `app/main.py` - FastAPI entry point and routing
- `app/api/routes.py` - Main API endpoints (40K+ lines)
- `app/api/auth.py` - Authentication logic
- `app/core/database.py` - Database connection and schema management
- `app/core/config.py` - Environment configuration
- `app/core/security.py` - Password hashing and verification
- `app/core/utils.py` - Helper functions and pagination

### Services
- `app/services/scraper.py` - SPA reverse engineering (949 lines)
- `app/services/sync.py` - Data synchronization (947 lines)
- `app/services/analyzer.py` - LLM analysis and blueprint generation (588 lines)

### Frontend
- `static/tdental.html` - Main application page (96K+ lines)
- `static/login.html` - Login page
- `static/css/style.css` - Main stylesheet (90K+ lines)
- `static/js/app.js` - Main JavaScript application (181K+ lines)
- `static/js/login.js` - Login page JavaScript

### Scripts
- `scripts/run_scraper.py` - TDental-specific scraper runner
- `scripts/migrate.py` - Data migration script
- `run.py` - Generic SPA scraper CLI

## Known Bugs and Root Causes

### Frontend Issues
1. **CORS Errors**: API backend blocks localhost requests
   - Root Cause: Server-side CORS configuration
   - Status: Cannot be fixed from frontend

2. **Missing Features**: Inventory, HR, Finance, Settings
   - Root Cause: Not yet implemented in original TDental
   - Status: Stubbed with "coming soon" alerts

### Backend Issues
1. **Session Token Expiry**: JWT tokens expire after 7 days
   - Root Cause: TDental API token policy
   - Status: Auto-refresh implemented in sync engine

2. **Database Connection**: Railway PostgreSQL connection string hardcoded
   - Root Cause: Development convenience
   - Status: Should be moved to environment variable

## Commands to Build, Test, and Verify

### Development Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python -m app.main

# Run scraper on TDental
python scripts/run_scraper.py

# Run generic scraper
python run.py <url> --username <user> --password <pass>

# Run sync engine (once)
python app/services/sync.py

# Run sync engine (continuous)
python app/services/sync.py --daemon
```

### Database Commands
```bash
# Ensure auth tables (run once)
python -c "from app.core.database import ensure_auth_tables; ensure_auth_tables()"

# Create admin user (if needed)
python -c "from app.core.database import get_conn, get_cursor; conn=get_conn(); cur=get_cursor(conn); cur.execute('INSERT INTO app_users (id, name, email, password, role, active) VALUES (%s, %s, %s, %s, 'admin', TRUE)', ('admin_001', 'Admin', 'admin@tdental.vn', 'admin123')); conn.commit(); conn.close()"
```

### Testing Commands
```bash
# Verify login works
curl -X POST http://localhost:8899/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@tdental.vn", "password": "admin123"}'

# Verify customer API
curl http://localhost:8899/api/customers \
  -H "Authorization: Bearer <token>"

# Verify appointment API
curl http://localhost:8899/api/appointments \
  -H "Authorization: Bearer <token>"
```

## Project Dependencies

### Core Dependencies
- **FastAPI**: Web framework
- **Playwright**: Browser automation
- **psycopg2**: PostgreSQL driver
- **requests**: HTTP client
- **pydantic**: Data validation

### Development Dependencies
- **uvicorn**: ASGI server
- **python-multipart**: Form data parsing
- **python-jose**: JWT handling

## Security Considerations

### Authentication
- JWT tokens with 30-day expiry for web sessions
- SHA-256 password hashing with salt
- Session management with token refresh

### Authorization
- Role-based access control (admin/viewer)
- Permission-based feature access
- API endpoint protection with middleware

## Performance Considerations

### Database
- Proper indexing on frequently queried columns
- Connection pooling for production
- Query optimization for large datasets

### Frontend
- Lazy loading for large pages
- Caching for static assets
- Efficient DOM manipulation

## Deployment Notes

### Docker Configuration
- Multi-stage build for optimization
- Environment variable configuration
- Health check endpoints

### Railway Deployment
- PostgreSQL add-on integration
- Environment variable management
- Automatic scaling configuration