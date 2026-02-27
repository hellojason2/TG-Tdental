# TDental Viewer & Scraper - Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [Database Schema](#database-schema)
6. [API Endpoints](#api-endpoints)
7. [Frontend Components](#frontend-components)

---

## System Overview

The TDental Viewer & Scraper is a comprehensive tool suite designed to scrape, analyze, and replicate the TDental dental clinic management system. The system operates in three main modes:

### Mode 1: Scraper
Reverse-engineers the TDental SPA by capturing:
- API traffic and responses
- DOM structure
- Screenshots
- Route navigation

### Mode 2: Sync Engine
Polls TDental API and syncs data to local PostgreSQL:
- Real-time data synchronization
- Customer enrichment
- Appointment tracking

### Mode 3: Viewer
Provides a local replica of the TDental dashboard:
- Full CRUD operations
- Authentication
- Reporting

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        TDental Viewer & Scraper                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐ │
│  │   TDental.vn    │────▸│  Sync Engine    │────▸│   Railway DB    │ │
│  │   (Source)      │     │  (Middleware)   │     │  (PostgreSQL)   │ │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘ │
│          │                       │                        │            │
│          │                       │                        │            │
│          ▼                       ▼                        ▼            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     FastAPI Backend (Port 8899)                │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐   │   │
│  │  │  /api/auth  │  │ /api/routes │  │   /api/customers    │   │   │
│  │  │  Login/Logout│  │  User Mgmt  │  │  /api/appointments │   │   │
│  │  └─────────────┘  └─────────────┘  └──────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Frontend (Static Files)                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │   │
│  │  │ tdental  │  │  login   │  │  app.js  │  │   style.css   │  │   │
│  │  │  .html   │  │  .html   │  │ (181KB)  │  │    (90KB)     │  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Scraper (`app/services/scraper.py`)

**Purpose**: Automated SPA reverse engineering tool

**Key Features**:
- Playwright headless browser automation
- Automatic login detection
- Route discovery from navigation
- API traffic capture
- DOM structure extraction
- Screenshot generation

**Configuration**:
```python
CONFIG = {
    'base_url': 'https://tamdentist.tdental.vn/#/dashboard',
    'output_dir': './data/tdental',
    'login': {
        'username': 'dataconnect',
        'password': 'dataconnect@',
    }
}
```

### 2. Sync Engine (`app/services/sync.py`)

**Purpose**: Middleware for data synchronization

**Key Features**:
- JWT token authentication
- Paginated API fetching
- PostgreSQL upsert operations
- Real-time sync capability
- Error handling and logging

**Data Flow**:
```
TDental API → TDentalClient → SyncDatabase → Railway PostgreSQL
```

### 3. Analyzer (`app/services/analyzer.py`)

**Purpose**: LLM-powered analysis and blueprint generation

**Key Features**:
- Database schema generation
- API specification creation
- Frontend component mapping
- Replication blueprint generation

**Supported Providers**:
- Groq (default)
- OpenAI
- Anthropic

### 4. FastAPI Backend (`app/main.py`)

**Purpose**: Web application backend

**Key Features**:
- JWT authentication
- Session management
- RESTful API endpoints
- CORS support
- Static file serving

**Port**: 8899

---

## Data Flow

### Authentication Flow
```
User Login → POST /api/auth/login → Verify credentials → 
Generate JWT token → Store session → Return token
```

### Customer Data Flow
```
TDental API → Sync Engine → PostgreSQL → 
API Route → Frontend Display
```

### Scraper Flow
```
Playwright Launch → Login → Discover Routes → 
Capture API → Extract DOM → Generate Report
```

---

## Database Schema

### Core Tables

| Table | Records | Purpose |
|-------|---------|---------|
| `customers` | 31,701 | Central entity |
| `customer_appointments` | 212,773 | Scheduling |
| `customer_receipts` | 162,788 | Check-in/reception |
| `dot_khams` | 83,768 | Exam sessions |
| `sale_order_lines` | 58,053 | Individual treatments |
| `sale_orders` | 56,340 | Treatment order headers |
| `account_payments` | 53,528 | Payment transactions |
| `sale_order_payments` | 49,895 | Payment-order links |
| `stock_moves` | 1,670 | Inventory movements |
| `products` | 443 | Services & materials |
| `employees` | 372 | Staff directory |
| `companies` | 7 | Branch offices |

### Authentication Tables

| Table | Purpose |
|-------|---------|
| `app_users` | User accounts |
| `app_sessions` | Active sessions |

---

## API Endpoints

### Authentication (`/api/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | User login |
| GET | `/api/auth/me` | Get current user |

### Users (`/api/users`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | List users |
| POST | `/api/users` | Create user |
| PUT | `/api/users/{id}` | Update user |
| DELETE | `/api/users/{id}` | Delete user |

### Customers (`/api/customers`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/customers` | List customers |
| GET | `/api/customers/{id}` | Get customer detail |
| POST | `/api/customers` | Create customer |
| PUT | `/api/customers/{id}` | Update customer |
| DELETE | `/api/customers/{id}` | Delete customer |

### Appointments (`/api/appointments`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/appointments` | List appointments |
| GET | `/api/appointments/calendar` | Calendar view |
| GET | `/api/appointments/states` | Appointment states |
| POST | `/api/appointments` | Create appointment |
| PUT | `/api/appointments/{id}` | Update appointment |
| PUT | `/api/appointments/{id}/state` | Change state |

---

## Frontend Components

### Pages
| Route | Component | Status |
|-------|-----------|--------|
| `/` | Dashboard | ✅ Working |
| `/customers` | Customer List | ✅ Working |
| `/reception` | Reception | ✅ Working |
| `/calendar` | Calendar | ✅ Working |
| `/treatments` | Treatments | ✅ Working |
| `/inventory` | Inventory | 🔧 Coming Soon |
| `/hr` | HR | 🔧 Coming Soon |
| `/finance` | Finance | 🔧 Coming Soon |
| `/reports` | Reports | ✅ Working |
| `/locations` | Locations | ✅ Working |

### Key Components
| Component | File | Size |
|-----------|------|------|
| Main App | `app.js` | 181KB |
| Styles | `style.css` | 90KB |
| Login | `login.js` | 1.8KB |

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | HTML, CSS, JavaScript (Vanilla) |
| Backend | FastAPI (Python) |
| Database | PostgreSQL (Railway) |
| Browser Automation | Playwright |
| LLM | Groq, OpenAI, Anthropic |

---

## Performance Considerations

### Database
- Proper indexing on frequently queried columns
- Connection pooling for production
- Query optimization for large datasets (700K+ records)

### Frontend
- Lazy loading for large pages
- Caching for static assets
- Efficient DOM manipulation

### Sync Engine
- Paginated API fetching (100 records/page)
- Batch upsert operations
- 5-minute sync interval (configurable)

---

## Security Considerations

### Authentication
- JWT tokens with 30-day expiry
- SHA-256 password hashing with salt
- Session management with token refresh

### Authorization
- Role-based access control (admin/viewer)
- Permission-based feature access
- API endpoint protection

### Data
- SQL injection prevention via parameterized queries
- XSS prevention in frontend
- CSRF protection via tokens

---

## Deployment

### Docker
- Multi-stage build for optimization
- Environment variable configuration
- Health check endpoints

### Railway
- PostgreSQL add-on integration
- Environment variable management
- Automatic scaling configuration

---

**Last Updated**: 2026-02-26
**Version**: 1.0.0