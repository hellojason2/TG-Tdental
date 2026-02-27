# Architectural Decisions - Why We Did Things This Way

## Overview

This document captures the rationale behind key architectural decisions in the TDental Viewer & Scraper project. Understanding why certain choices were made helps prevent unintended changes that could break existing functionality.

---

## 1. Database Schema Decisions

### Decision: Use UUIDs as Primary Keys

**Context**: All tables use UUID as primary keys instead of auto-incrementing integers.

**Reasoning**:
- UUIDs allow distributed data generation without collision
- Matches TDental's original schema (also uses UUIDs)
- Better for data merging from multiple sources
- Security through obscurity (non-guessable IDs)

**DO NOT Change**: Do not switch to auto-incrementing integers without migrating all related foreign keys.

### Decision: Store Raw JSON Data

**Context**: Each table has a `raw_data JSONB` column to store the complete API response.

**Reasoning**:
- Preserves data that might not fit into normalized columns
- Enables future schema changes without re-scraping
- Debugging purposes - can see exactly what TDental API returned

**DO NOT Remove**: The raw_data column is essential for data recovery and debugging.

### Decision: Separate Auth Tables

**Context**: Authentication uses separate `app_users` and `app_sessions` tables instead of TDental's `application_users`.

**Reasoning**:
- Security isolation - local users are independent of source system
- Flexibility to add/modify local users without affecting source
- Simpler permission model for local admin

**DO NOT Merge**: Keep app_users separate from application_users (TDental's table).

---

## 2. API Design Decisions

### Decision: JWT-Based Authentication

**Context**: Web sessions use JWT tokens stored in cookies.

**Reasoning**:
- Stateless - no server-side session storage needed
- 30-day expiry provides good UX while maintaining security
- Compatible with standard OAuth flows
- Tokens include all necessary user info

**DO NOT Change**: Token structure or expiry without updating all clients.

### Decision: Bearer Token in Header

**Context**: API authentication uses `Authorization: Bearer <token>` header.

**Reasoning**:
- Standard HTTP authentication pattern
- Works with curl, Postman, and frontend frameworks
- Easy to debug and test

**DO NOT Switch**: Do not change to query parameters or body-based auth.

### Decision: RESTful Endpoints with Pagination

**Context**: All list endpoints support `page`, `per_page`, `search`, `sort`, `order` parameters.

**Reasoning**:
- Handles large datasets (700K+ records) efficiently
- Consistent interface across all endpoints
- Search and sort essential for usability

**DO NOT Remove**: Pagination is critical for performance with large datasets.

---

## 3. Scraper Design Decisions

### Decision: Playwright Over Selenium

**Context**: Browser automation uses Playwright instead of Selenium.

**Reasoning**:
- Faster execution (headless by default)
- Better waiting mechanisms for SPAs
- Native support for modern JavaScript frameworks
- More reliable element detection

**DO NOT Switch**: Do not switch to Selenium without significant refactoring.

### Decision: Network Interception for API Capture

**Context**: Scraper intercepts network responses rather than parsing DOM.

**Reasoning**:
- Captures exact API structure used by frontend
- No need to reverse-engineer frontend JavaScript
- More reliable - works regardless of frontend changes
- Complete data including hidden fields

**DO NOT Change**: Network capture is the core scraping mechanism.

### Decision: Multiple Scrape Sessions

**Context**: Data is stored in timestamped folders (e.g., `tamdentist_tdental_vn_20260208_024318`).

**Reasoning**:
- Preserves historical data for comparison
- Enables rollback if issues found
- Allows analyzing changes over time

**DO NOT Overwrite**: Always create new folders, never replace existing data.

---

## 4. Sync Engine Decisions

### Decision: Polling Over Webhooks

**Context**: Sync uses periodic polling instead of TDental pushing updates.

**Reasoning**:
- TDental doesn't provide webhooks
- Polling is more resilient to temporary failures
- Simpler architecture than reverse-engineering push mechanisms
- Configurable interval (default 5 minutes)

**DO NOT Implement**: Do not try to implement push without TDental API support.

### Decision: Upsert Operations

**Context**: Sync uses INSERT ... ON CONFLICT UPDATE (upsert).

**Reasoning**:
- Handles both new records and updates
- Idempotent - safe to run multiple times
- Efficient - single query per record
- Prevents duplicates

**DO NOT Change**: Upsert pattern must be preserved for data integrity.

### Decision: 7-Day Token Expiry

**Context**: JWT tokens are assumed to expire after 7 days.

**Reasoning**- Matches TDental's actual token expiry
- Automatic re-authentication on expiry
- Balance between security and usability

**DO NOT Hardcode**: Token expiry should come from TDental response.

---

## 5. Frontend Decisions

### Decision: Vanilla JavaScript Over Framework

**Context**: Frontend uses plain JavaScript instead of React/Vue/Angular.

**Reasoning**:
- Simpler deployment (no build step needed)
- Extracted directly from TDental - less maintenance
- Single HTML file is easier to distribute
- Faster initial load for static deployment

**DO NOT Migrate**: Do not rewrite in React/Vue without complete project replanning.

### Decision: Modal-Based UI

**Context**: Forms use modal dialogs instead of separate pages.

**Reasoning**:
- Matches TDental's UX
- Faster user interaction
- Single-page feel
- Better for quick data entry

**DO NOT Change**: Modal pattern is integral to the user experience.

### Decision: Fallback Data for Demo

**Context**: Dashboard shows mock data when API is unavailable.

**Reasoning**:
- Enables demo mode without backend
- Shows UI is functional even without data
- Essential for development and presentations

**DO NOT Remove**: Fallback data is critical for offline demo and development.

---

## 6. Infrastructure Decisions

### Decision: Railway PostgreSQL

**Context**: Database is hosted on Railway.

**Reasoning**:
- Easy setup and management
- Automatic backups
- Good free tier for development
- Easy connection string management

**DO NOT Migrate**: Do not move to different database host without testing all connections.

### Decision: FastAPI Framework

**Context**: Backend uses FastAPI instead of Flask/Django.

**Reasoning**:
- Built-in OpenAPI documentation
- Async support for better performance
- Type validation with Pydantic
- Modern Python framework

**DO NOT Change**: FastAPI is the backend framework.

### Decision: Port 8899

**Context**: Application runs on port 8899.

**Reasoning**:
- Avoids conflicts with common ports (80, 443, 3000, 5000)
- Easy to remember
- Already configured in Dockerfile and config

**DO NOT Change**: Port should remain 8899 unless explicitly reconfigured.

---

## 7. Known Trade-offs

### Trade-off: Large Static Files
- **Acceptable Because**: Single-file distribution simplifies deployment
- **Impact**: Initial load time is longer
- **Mitigation**: Caching handled by browser

### Trade-off: No Real-time Updates
- **Acceptable Because**: Polling every 5 minutes is sufficient for most use cases
- **Impact**: Data may be up to 5 minutes old
- **Mitigation**: Users can manually refresh

### Trade-off: CORS Issues
- **Acceptable Because**: Development-only issue, fixed in production
- **Impact**: Can't test locally against production API
- **Mitigation**: Use local database for development

---

## Summary of "DO NOT" Rules

1. **DO NOT** change primary key types (UUID ↔ integer)
2. **DO NOT** remove raw_data JSONB columns
3. **DO NOT** merge app_users with application_users
4. **DO NOT** change authentication mechanism (Bearer token)
5. **DO NOT** remove pagination parameters
6. **DO NOT** switch from Playwright to Selenium
7. **DO NOT** change network capture approach
8. **DO NOT** overwrite existing scrape data
9. **DO NOT** implement webhooks (not supported by TDental)
10. **DO NOT** change upsert pattern
11. **DO NOT** rewrite frontend in React/Vue/Angular
12. **DO NOT** remove modal-based UI
13. **DO NOT** remove fallback data
14. **DO NOT** change database host (Railway)
15. **DO NOT** change backend framework (FastAPI)
16. **DO NOT** change default port (8899)

---

**Last Updated**: 2026-02-26
**Maintained By**: Project Maintainers