# TDental Replica: Roadmap from ~40% to 99% Parity

**Created:** 2026-02-27
**Goal:** Make the local TDental replica at `localhost:8899` visually and functionally identical to `tamdentist.tdental.vn`

---

## Current State: ~40% Parity

| Layer | Current | Target |
|-------|---------|--------|
| Frontend shell (sidebar, topbar) | 85% | 99% |
| Dashboard | 75% | 99% |
| Customer list + CRUD | 85% | 99% |
| Customer detail drawer | 25% (4/10 tabs) | 99% |
| Calendar (grid views) | 70% | 99% |
| Reception / Work | 60% | 99% |
| Labo / Treatments | 30% | 99% |
| Reports (10 sub-reports) | 40% | 99% |
| Purchase / Inventory / Salary | 10-65% | 99% |
| Cashbook / Finance | 60% | 99% |
| Call Center / Commission | 40-45% | 99% |
| Categories management | 50% | 99% |
| Settings | 60% | 99% |
| Data sync completeness | 15% | 99% |
| **Overall** | **~40%** | **99%** |

---

## Tools Available

| Tool | What It Does | Status |
|------|-------------|--------|
| **website-replicator** (VPS) | Playwright crawler + Claude AI code gen | Running on VPS, no crawl job run yet |
| **generate_pipeline.py** | Takes crawler output → generates Next.js page components | Ready, needs API key in `.env` |
| **files 10/deep-extract** | 16 pages already captured (DOM, screenshots, hover states, 937 elements) | Available locally |
| **files 10/ui-extract** | 17 page captures with full-page screenshots | Available locally |
| **.firecrawl/** | 31 screenshots of live TDental (modals, dropdowns, detail pages) | Available locally |
| **scraper-web/data/** | 34 API responses captured, 5 routes with DOM snapshots | Available locally |
| **scraper-web/docs/parity/** | 61 comparison files (live vs local screenshots, gap analysis) | Available locally |
| **sync.py** | Base data sync (customers, employees, products, companies) | Running as daemon |
| **deep_sync.py** | Customer enrichment + appointment history + sale order lines | Needs manual run |
| **full_sync.py** | All remaining tables (406K+ records) | Needs manual run |

---

## Phase 1: DATA FOUNDATION (Run First — Everything Else Depends On This)

**Why:** Most pages show empty states or fallback data because tables don't exist or are empty.

### 1.1 Run full_sync.py to populate all tables
```bash
cd /Users/thuanle/Documents/TamTMV/Tdental/scraper-web
python full_sync.py
```
**Expected:** 406K+ records across sale_orders (56K), customer_receipts (163K), account_payments (54K), sale_order_payments (50K), dot_khams (84K), stock_pickings, stock_moves, quotations, commissions

### 1.2 Run deep_sync.py to enrich customer data
```bash
python deep_sync.py
```
**Expected:** 31K customers enriched with 34 extra fields + customer_appointments populated (213K) + sale_order_lines (58K)

### 1.3 Fix the appointments table name mismatch
- `sync.py` writes to `appointments` table (today only)
- API routes read from `customer_appointments` table
- **Fix:** Change sync.py to write to `customer_appointments` OR add a view/alias

### 1.4 Add missing tables at startup (database.py)
Add `CREATE TABLE IF NOT EXISTS` for all tables referenced in routes.py that are currently only created by sync scripts:
- customer_appointments, employees, account_payments, stock_pickings, stock_moves, sale_order_lines, sale_order_payments, dashboard_reports, companies, products, product_categories, partner_categories, partner_sources, dot_khams, quotations, customer_receipts, commissions

---

## Phase 2: CRAWL THE ORIGINAL (Use the Website Replicator)

**Why:** We need pixel-perfect reference data for every page we haven't captured yet.

### 2.1 Run a full crawl of TDental via website-replicator
```bash
cd /path/to/website-replicator
# Set API key in .env
./run.sh crawl
# Watch live at http://localhost:6080
```
**Expected output:** Screenshots, DOM trees, hover states, API responses, design tokens for ALL 300 pages/routes

### 2.2 Generate reference code from crawl output
```bash
./run.sh generate <job_id>
```
**Expected output:** Next.js page components for every route — use these as reference for what each page should look like

### 2.3 Alternatively, generate from existing files 10/ data
```bash
cd /Users/thuanle/Documents/TamTMV/Tdental
python generate_pipeline.py "files 10/deep-extract" --model claude-sonnet-4-20250514
```
This uses the 16-page deep-extract data already captured (dashboard, calendar, partners, work, warehouse, 10 customer detail tabs)

### 2.4 Extract design tokens from crawl output
From `design_tokens.json` and the deep-extract CSS variables:
- Primary: `#1A6DE3` (already correct)
- Sidebar bg: `#0C1014` (already correct)
- Status badge "Chờ khám": orange `#F59E0B` (currently wrong — using light blue)
- Status badge "Đang khám": blue `#3B82F6` (currently wrong — using green)
- Button height: 34px, border-radius: 6px
- Card border-radius: 10px
- Sidebar width: 256px (currently 220px — wrong)

---

## Phase 3: FIX CRITICAL VISUAL MISMATCHES

These are the HIGH-severity visual diffs documented in `docs/parity/visual_diff_summary.md`.

### 3.1 Calendar — Convert from list to grid view (MAJOR)
- **Current:** Shows appointment list only
- **Original:** Full monthly calendar grid with time slots 06:00-23:00, "Sáng/Chiều/Tối" filters, doctor columns
- **Reference:** `.firecrawl/original-calendar-day-view.png`, `original-calendar-week-view.png`, `original-calendar-month-view.png`
- **Action:** Rebuild calendar rendering using reference screenshots + DOM from `files 10/deep-extract/calendar/`

### 3.2 Reception — Convert from table to card-based layout (MAJOR)
- **Current:** Table-based layout titled "Tiếp nhận"
- **Original:** Card-based patient history view "Lịch sử khám bệnh" with avatar, name, doctor, branch, services section
- **Reference:** `.firecrawl/tdental-work.png`, `files 10/deep-extract/work/`
- **Action:** Rebuild reception page as card layout matching the original

### 3.3 Status badge colors
- **Fix:** "Chờ khám" = orange/amber `#F59E0B`, "Đang khám" = blue `#3B82F6`
- Currently both are wrong colors

### 3.4 Sidebar width
- **Fix:** Change from 220px to 256px to match `--tds-layout-width-menu-side-default`

---

## Phase 4: CUSTOMER DETAIL DRAWER — Add Missing 6 Tabs

The customer detail panel currently has 4 tabs. The original has 10.

| Tab | Vietnamese | Status | Data Source |
|-----|-----------|--------|-------------|
| Hồ sơ (Profile) | Hồ sơ | DONE | customers table |
| Lịch hẹn (Appointments) | Lịch hẹn | Structure only, no data | customer_appointments |
| Phiếu điều trị (Treatment) | Phiếu điều trị | Structure only, no data | sale_orders + sale_order_lines |
| Đợt khám (Exam Sessions) | Đợt khám | Structure only, no data | dot_khams |
| Tình trạng răng (Teeth Map) | Tình trạng răng | MISSING | Custom SVG dental chart |
| Báo giá (Quotations) | Báo giá | MISSING | quotations |
| Labo | Labo | MISSING | sale_order_lines (labo type) |
| Hình ảnh (Images) | Hình ảnh | MISSING | No image storage yet |
| Tạm ứng (Advance Payments) | Tạm ứng | MISSING | customer_receipts |
| Sổ công nợ (Debt Ledger) | Sổ công nợ | MISSING | account_payments + sale_orders |

**Reference screenshots:** `files 10/deep-extract/customer-teeth-status/`, `customer-quotations/`, `customer-labo-orders/`, `customer-images-v2/`, `customer-advance/`, `customer-debt/`

---

## Phase 5: ADD MISSING API ENDPOINTS

### 5.1 Endpoints for existing data (tables exist, no route)
```
GET /api/dot-khams                    — 83,768 exam sessions
GET /api/dot-khams?partnerId={id}     — per-customer
GET /api/quotations                   — 75 quotations
GET /api/quotations?partnerId={id}    — per-customer
GET /api/customer-receipts            — 162,788 check-in records
GET /api/customer-receipts?partnerId={id} — per-customer
GET /api/commissions                  — 17 commission rules
```

### 5.2 Fix broken endpoints
- `GET /export/sale-orders` — change `ref` to `name` column
- `GET /export/products` — fix column names (`default_code`, `standard_price`, `list_price`)

### 5.3 Fix route ordering bug
Move `/appointments/states` and `/sale-orders/states/summary` ABOVE their parametric routes (`/{id}`)

### 5.4 Add /api/stats endpoint
Frontend calls this but it doesn't exist — returns 404. Create it from dashboard_reports data.

### 5.5 Enrich GET /customers/{id}
Join additional tables: customer_receipts, dot_khams, quotations, commissions

---

## Phase 6: COMPLETE REMAINING PAGES

### 6.1 Labo / Treatments page
- Currently fetches sale_orders instead of labo-specific data
- Need to filter for labo order lines and show the 18-column labo table
- Add "Tạo phiếu Labo" modal

### 6.2 Reports — 10 sub-reports
Currently one generic page. Need separate views for:
- Báo cáo ngày (Daily report)
- Báo cáo dịch vụ (Service report)
- Báo cáo khách hàng (Customer report)
- Báo cáo nguồn khách hàng (Source report)
- Báo cáo nhân viên (Staff report)
- Báo cáo chi nhánh (Branch report)
- Plus: fix chart data loading (currently shows "Đang tải...")

### 6.3 Salary / Lương
- Currently shows empty state only
- Need: API endpoint for salary calculations, table rendering with real data
- Reference: `files 10/deep-extract/` (no salary page captured — need crawler)

### 6.4 Purchase / Mua hàng
- Fix column mismatch (5 rendered vs 8 in header)
- Add "Tạo phiếu mua" modal
- Add Trả hàng (Return) sub-view

### 6.5 Partners / Đối tác page
- `page-partners` div doesn't exist in HTML
- Need to create the page entirely

### 6.6 Commission / Hoa hồng
- Define missing functions: `editReferral()`, `deleteReferral()`
- Implement `openModal('referral')` type

### 6.7 Call Center / Tổng đài
- Add Cấu hình tổng đài sub-view
- Wire call log data when available

---

## Phase 7: INTERACTION PARITY

### 7.1 Fix stub alert() calls (32 occurrences)
Replace all `alert('coming soon')` with actual implementations or proper toast notifications

### 7.2 Wire dead buttons
| Button | Current | Needed |
|--------|---------|--------|
| Reception "Edit" | alert stub | Open edit modal |
| Reception "View Profile" | alert stub | Navigate to customer detail |
| Customer detail "In hồ sơ" | no handler | Print PDF |
| Customer detail "Đặt lịch hẹn" | no handler | Open appointment modal |
| Customer detail "+ Thêm phiếu" | no handler | Open treatment modal |
| Calendar "Export Excel" | alert stub | Download XLSX |
| Dashboard reception filter tabs | no handler | Filter by status |
| Notification bell | alert stub | Show notification panel |
| Chat widget | alert stub | Show chat panel |

### 7.3 Fix undefined functions
- `editReferral()` — called but not defined (will throw ReferenceError)
- `deleteReferral()` — called but not defined

### 7.4 Settings persistence
- "Áp dụng" button currently does not persist to database
- Fix: wire to PUT /api/settings endpoint properly

---

## Phase 8: CSS & DESIGN POLISH

### 8.1 Apply exact design tokens from TDental
Using the 242 CSS variables captured in `files 10/deep-extract`:
- Sidebar width: 256px (not 220px)
- Font: Apply Inter font-family to body
- Card shadows matching TDS elevation hierarchy
- Status badge exact colors
- Button styles matching TDS component system

### 8.2 Fix inconsistent icon usage
- Cashbook stat cards use emoji (📊) instead of SVG icons
- Standardize all icons to match original TDental

### 8.3 Responsive breakpoints
- Calendar overflows on mobile
- Tables with many columns need horizontal scroll

---

## Phase 9: SECURITY (Before Going Live)

| Fix | Priority |
|-----|----------|
| Add auth middleware to ALL 33 unprotected endpoints | CRITICAL |
| Stop storing plaintext passwords in cookies | CRITICAL |
| Rotate hardcoded Railway DB password in config.py | CRITICAL |
| Move all credentials to .env | CRITICAL |
| Set session cookies as HttpOnly; Secure | CRITICAL |
| Fix CORS (specific origins, not `*`) | CRITICAL |
| Switch SHA-256 to bcrypt for password hashing | HIGH |
| Add try/finally for DB connection cleanup | HIGH |
| Add rate limiting on login | HIGH |
| Add connection pooling | HIGH |

---

## Execution Order (Recommended)

```
WEEK 1: Data Foundation
├── Phase 1.1: Run full_sync.py (populates 406K records)
├── Phase 1.2: Run deep_sync.py (enriches 31K customers)
├── Phase 1.3: Fix appointments table mismatch
├── Phase 1.4: Add CREATE TABLE IF NOT EXISTS for all tables
└── Phase 2.1: Run website-replicator crawl

WEEK 2: Critical Visual Fixes + Generated References
├── Phase 2.2: Generate reference code from crawl output
├── Phase 3.1: Rebuild calendar as grid view
├── Phase 3.2: Rebuild reception as card layout
├── Phase 3.3: Fix status badge colors
├── Phase 3.4: Fix sidebar width
└── Phase 5.3: Fix route ordering bug

WEEK 3: Customer Detail + Missing APIs
├── Phase 4: Add 6 missing customer detail tabs
├── Phase 5.1: Add missing API endpoints (dot_khams, quotations, receipts)
├── Phase 5.2: Fix broken export endpoints
├── Phase 5.4: Add /api/stats endpoint
└── Phase 5.5: Enrich customer detail API

WEEK 4: Remaining Pages
├── Phase 6.1: Fix Labo page
├── Phase 6.2: Build 10 report sub-views
├── Phase 6.3: Salary page
├── Phase 6.4: Fix Purchase page
├── Phase 6.5: Create Partners page
├── Phase 6.6: Fix Commission page
└── Phase 6.7: Wire Call Center

WEEK 5: Interactions + Polish
├── Phase 7: Wire all dead buttons and stubs
├── Phase 8: CSS design token alignment
└── Phase 9: Security fixes

Target: 99% parity
```

---

## Key Files to Reference

| What | Location |
|------|----------|
| Live TDental screenshots | `.firecrawl/original-*.png` (31 files) |
| Deep DOM + interaction data | `files 10/deep-extract/` (16 pages, 937 elements) |
| Design tokens (CSS vars) | `files 10/deep-extract/DEEP-UI-REPORT.md` (242 variables) |
| Captured API responses | `scraper-web/data/tamdentist_tdental_vn_20260208_024318/api_responses/` (34 files) |
| Side-by-side comparisons | `scraper-web/docs/parity/visual_capture/` (23 screenshots) |
| Before/after fixes | `scraper-web/docs/parity/fixes/` (27 screenshots) |
| UI interaction spec | `.firecrawl/INTERACTIONS.md` (446 lines) |
| Parity checklists | `scraper-web/FRONTEND_PARITY_MASTER_TASKS.md` (114 tasks) |
| API endpoint mapping | `scraper-web/docs/parity/P4_API_CONTRACT_MAPPING.md` |
| Generated code pipeline | `generate_pipeline.py` (feeds crawler output → Claude → Next.js code) |
