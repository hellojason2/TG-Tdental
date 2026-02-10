# TDental Local Replica — Architecture & Data Map
## Complete Entity Relationship Diagram

This document maps how every piece of data in TDental connects, serving as the
blueprint for building a local replica of the entire system.

---

## 📊 Database Overview (27 tables, ~711,000+ records)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        TDental Data Architecture                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │  CUSTOMERS   │────▸│ APPOINTMENTS │     │  COMPANIES   │            │
│  │   (31,701)   │     │  (212,773)   │     │    (7)       │            │
│  │              │     │              │     │ (= Branches) │            │
│  │ - ref (T###) │     │ - date/time  │     └──────┬───────┘            │
│  │ - name       │     │ - doctor     │            │                     │
│  │ - phone      │     │ - state      │      assigned to                │
│  │ - address    │     │ - note       │            │                     │
│  │ - source     │     └──────────────┘            ▼                     │
│  │ - company ───┼──────────────────────▸  branch/company_id            │
│  └──────┬───────┘                                                       │
│         │has many                                                       │
│         ▼                                                               │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │ SALE_ORDERS  │────▸│SALE_ORDER_   │     │  DOT_KHAMS   │            │
│  │  (56,340)    │     │   LINES      │     │  (83,768)    │            │
│  │              │     │  (58,053)    │     │ Exam Sessions │            │
│  │ = Treatment  │     │              │     │              │            │
│  │   Orders     │     │ = Individual │     │ - doctor     │            │
│  │ - SO#####    │     │   treatments │     │ - services   │            │
│  │ - total      │     │ - product    │     │ - reason     │            │
│  │ - paid       │     │ - teeth      │     │ - SO link    │            │
│  │ - residual   │     │ - amount     │     └──────────────┘            │
│  │ - doctor     │     │ - doctor     │                                  │
│  └──────┬───────┘     └──────────────┘                                  │
│         │                                                               │
│    paid via                                                             │
│         ▼                                                               │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │SALE_ORDER_   │────▸│  ACCOUNT_    │     │  CUSTOMER_   │            │
│  │  PAYMENTS    │     │  PAYMENTS    │     │  RECEIPTS    │            │
│  │  (49,895)    │     │  (53,528)    │     │  (162,788)   │            │
│  │              │     │              │     │              │            │
│  │ = Links SO   │     │ = Actual $   │     │ = Check-in   │            │
│  │   to payment │     │   movement   │     │   records    │            │
│  │ - order_id   │     │ - amount     │     │ - waiting    │            │
│  │ - amount     │     │ - journal    │     │ - examination│            │
│  │ - payments[] │     │ - type       │     │ - done       │            │
│  └──────────────┘     └──────────────┘     └──────────────┘            │
│                                                                         │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │  EMPLOYEES   │     │  PRODUCTS    │     │  QUOTATIONS  │            │
│  │   (372)      │     │   (443)      │     │    (75)      │            │
│  │              │     │              │     │              │            │
│  │ - name       │     │ = Services & │     │ - partner    │            │
│  │ - job title  │     │   materials  │     │ - employee   │            │
│  │ - company    │     │ - price      │     │ - total      │            │
│  │ - department │     │ - category   │     │ - validity   │            │
│  └──────────────┘     └──────────────┘     └──────────────┘            │
│                                                                         │
│  ┌──────────────┐     ┌──────────────┐                                  │
│  │STOCK_PICKINGS│     │ STOCK_MOVES  │     ┌─── Reference Tables ───┐  │
│  │   (58)       │────▸│  (1,670)     │     │ partner_sources  (11)  │  │
│  │              │     │              │     │ partner_titles    (5)  │  │
│  │ = Inventory  │     │ = Individual │     │ partner_categories(12) │  │
│  │   transfers  │     │   stock mvmt │     │ product_categories(1)  │  │
│  │ - warehouse  │     │ - product    │     │ application_users (70) │  │
│  │ - partner    │     │ - qty        │     │ application_roles (10) │  │
│  │ - total      │     │ - direction  │     │ res_groups       (35)  │  │
│  └──────────────┘     └──────────────┘     │ commissions      (17)  │  │
│                                             └────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔗 Entity Relationships (Foreign Keys)

### Customer → Everything (central entity)
```
customers.id ─────▸ sale_orders.partner_id
customers.id ─────▸ sale_order_lines.order_partner_id
customers.id ─────▸ customer_appointments.partner_id
customers.id ─────▸ customer_receipts.partner_id
customers.id ─────▸ dot_khams.partner_id
customers.id ─────▸ quotations.partner_id
customers.id ─────▸ account_payments.partner_name (via name match)
customers.company_id ─▸ companies.id
customers.source_id ──▸ partner_sources.id
customers.title_id ───▸ partner_titles.id
```

### Sale Order → Treatment Lifecycle
```
sale_orders.id ──────▸ sale_order_lines.order_id (1:many — individual treatments)
sale_orders.id ──────▸ sale_order_payments.order_id (1:many — payments for this order)
sale_orders.id ──────▸ dot_khams.sale_order_id (1:many — exam visits for this order)
sale_orders.partner_id ▸ customers.id
```

### Payment Flow
```
sale_order_payments.order_id ──▸ sale_orders.id
sale_order_payments.payments ──▸ account_payments.id (JSONB array, links to actual payment records)
account_payments.journal_id ───▸ (internal accounting journal)
```

### Clinical Flow
```
dot_khams.partner_id ──────▸ customers.id
dot_khams.sale_order_id ───▸ sale_orders.id
dot_khams.doctor_id ───────▸ employees.id (or application_users via userId)
sale_order_lines.employee_id ▸ employees.id (treating doctor)
customer_appointments.doctor_id ▸ employees.id
```

### Inventory Flow
```
stock_pickings.id ──▸ stock_moves.picking_id (1:many)
stock_pickings.partner_id ──▸ customers/suppliers
products.id ──▸ sale_order_lines.product_id
products.categ_id ──▸ product_categories.id
```

---

## 🖥️ Replication Plan — Building TDental Locally

### Phase 1: Data (CURRENT — in progress)
- [x] Customer list sync (sync_engine.py) — 31,087 done
- [🔄] Customer detail enrichment (deep_sync.py) — running now
- [ ] Full remaining data (full_sync.py) — ready to run after deep_sync
- [ ] Verify all data integrity and relationships

### Phase 2: API Server (Local Backend)
Build a FastAPI/Flask server that replicates TDental's API structure:
```
/api/Partners              → customers table
/api/Partners/{id}         → customer detail with joins
/api/SaleOrders            → sale_orders + sale_order_lines
/api/SaleOrderLines        → sale_order_lines
/api/Appointments          → customer_appointments
/api/DotKhams              → dot_khams
/api/CustomerReceipts      → customer_receipts
/api/AccountPayments       → account_payments
/api/SaleOrderPayments     → sale_order_payments
/api/Companies             → companies
/api/Employees             → employees
/api/Products              → products
/api/Quotations            → quotations
/api/StockPickings + Moves → stock tables
+ all reference table endpoints
```

### Phase 3: Frontend (Angular Clone)
The original TDental is built with Angular. Options:
1. **Angular Clone** — Most faithful to original, replicate component structure
2. **Next.js/React Rebuild** — Modern stack, faster development
3. **HTML/JS Progressive** — Start from viewer.html, expand page by page

Key pages to replicate:
```
/#/dashboard               → Overview stats, charts
/#/partners/customers      → Customer list (paginated, filterable, sortable)
/#/partners/customers/{id} → Customer detail (10 tabs)
    ├── Hồ sơ (Profile)
    ├── Lịch hẹn (Appointments)
    ├── Tình trạng răng (Teeth map)
    ├── Báo giá (Quotations)
    ├── Phiếu điều trị (Treatment records)
    ├── Đợt khám (Exam sessions)
    ├── Labo (Lab orders — empty)
    ├── Hình ảnh (Images)
    ├── Tạm ứng (Advance payments)
    └── Sổ công nợ (Debt ledger)
/#/sale-management         → Sale orders
/#/reception               → Customer receipts/check-in
/#/hr/employees            → Employee management
/#/stock                   → Inventory
/#/accounting              → Payments & accounting
```

### Phase 4: Features
- Authentication (local users, roles from res_groups)
- Real-time dashboard with aggregated stats
- Treatment timeline visualization
- Financial reporting
- Appointment calendar view
- Inventory tracking

---

## 📋 Sync Scripts Summary

| Script | Purpose | Records | Time |
|--------|---------|---------|------|
| `sync_engine.py` | Base customer list + companies/employees/products | ~32,500 | ~5 min |
| `deep_sync.py` | Enrich each customer + treatments + appointments | ~31,000 customers + related | ~2.5 hrs |
| `full_sync.py` | All remaining tables (SO, payments, receipts, etc.) | ~406,000 | ~30-45 min |

Run in order: `sync_engine.py` → `deep_sync.py` → `full_sync.py`

---

## 🔑 Data Volumes Summary

| Table | Records | Key For |
|-------|---------|---------|
| customers | 31,701 | Central entity |
| customer_appointments | 212,773 | Scheduling |
| customer_receipts | 162,788 | Check-in/reception |
| dot_khams | 83,768 | Exam sessions |
| sale_order_lines | 58,053 | Individual treatments |
| sale_orders | 56,340 | Treatment order headers |
| account_payments | 53,528 | Payment transactions |
| sale_order_payments | 49,895 | Payment-order links |
| stock_moves | 1,670 | Inventory movements |
| products | 443 | Services & materials |
| employees | 372 | Staff directory |
| quotations | 75 | Price quotes |
| application_users | 70 | System login accounts |
| stock_pickings | 58 | Inventory transfers |
| res_groups | 35 | Permission groups |
| commissions | 17 | Commission rules |
| partner_categories | 12 | Customer tags |
| partner_sources | 11 | Lead sources |
| application_roles | 10 | User roles |
| companies | 7 | Branch offices |
| partner_titles | 5 | Honorifics |
| product_categories | 1 | Product grouping |
| **TOTAL** | **~711,000+** | |
