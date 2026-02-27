# TDental API Contract Mapping (P4 Tasks)

## Overview

This document maps the frontend API calls to backend endpoints and documents the alignment changes made for Phase 4 parity tasks (P4-01, P4-02, P4-03, P4-09).

## Changes Summary

### P4-01: Endpoint Mapping

| Frontend Function | Endpoint | Method | Query Params | Response Shape |
|-----------------|----------|--------|--------------|----------------|
| `loadCustomers()` | `/api/customers` | GET | `page, per_page, search, company, status, sort, order` | `{total, page, per_page, total_pages, items: [...]}` |
| `loadAppointments()` | `/api/appointments` | GET | `page, per_page, search, company, state, sort, order` | `{total, page, per_page, total_pages, items: [...]}` |
| `loadTreatments()` | `/api/sale-orders` | GET | `page, per_page, search, company, state, sort, order` | `{total, page, per_page, total_pages, items: [...]}` |
| `loadCashbook()` | `/api/payments` | GET | `page, per_page, search, company` | `{total, page, per_page, total_pages, items: [...]}` |
| `loadStockSummary()` | `/api/stock-moves/summary` | GET | `page, per_page, search, company` | `{total, page, per_page, total_pages, items: [...], totals: {...}}` |
| `loadStockHistory()` | `/api/stock-moves` | GET | `page, per_page, search, company` | `{total, page, per_page, total_pages, items: [...]}` |
| `loadStockPickings()` | `/api/stock-pickings` | GET | `page, per_page, search, company, picking_type` | `{total, page, per_page, total_pages, items: [...]}` |
| `loadSalary()` | `/api/employees` | GET | `page, per_page, search, company` | `{total, page, per_page, total_pages, items: [...]}` |
| `loadCallCenter()` | `/api/callcenter` | GET | `page, per_page, search, company` | `{total, page, per_page, total_pages, items: [...]}` |
| `loadProducts()` | `/api/products` | GET | `page, per_page, search, company` | `{total, page, per_page, total_pages, items: [...]}` |

### P4-02: Query Parameter Alignment

**Standardized Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Page number (1-indexed) |
| `per_page` | int | 50 (20 for some) | Items per page |
| `search` | string | "" | Search term for text filtering |
| `company` | string | "" | Company/branch UUID filter |
| `state` | string | "" | State/status filter (for appointments, sale-orders) |
| `sort` | string | varies | Sort column |
| `order` | string | "asc"/"desc" | Sort direction |
| `picking_type` | string | "" | For stock-pickings: "in", "out", or "" |

**Inconsistencies Fixed:**

1. **sale-orders** (`/api/sale-orders`)
   - Before: `company_name ILIKE %company%` (incorrect - filters by name)
   - After: `company_id = %company%` (correct - filters by UUID)
   - Added `company_id` to response

2. **products** (`/api/products`)
   - Before: `p.company_name ILIKE %company%` (incorrect)
   - After: `p.company_id = %company%` (correct)
   - Added `company_id` to response

3. **payments** (`/api/payments`)
   - Uses `journal_name ILIKE %company%` (legacy - kept for backward compatibility)
   - Note: account_payments table doesn't have company_id column

### P4-03: Status Dictionaries

**Appointment States:**

| State | Display | Badge Color |
|-------|---------|-------------|
| `draft` | Mới | gray |
| `confirmed` | Đã xác nhận | blue |
| `waiting` | Chờ | yellow |
| `done` | Hoàn thành | green |
| `cancel` | Hủy | red |

**Sale Order States:**

| State | Display | Badge Color |
|-------|---------|-------------|
| `draft` | Nháp | gray |
| `sale` | Đã xác nhận | green |
| `done` | Hoàn thành | blue |
| `cancel` | Hủy | red |
| Other | state_display | yellow |

**Customer Treatment Status:**

| Status | Display | Badge Color |
|--------|---------|-------------|
| `Đang điều trị` | Đang điều trị | blue |
| `Hoàn thành` | Hoàn thành | green |
| Other | Chưa phát sinh | gray |

**Payment States:**

| State | Display | Badge Color |
|-------|---------|-------------|
| `draft` | Nháp | yellow |
| `posted` | Đã đăng | green |
| Other | state | gray |

### P4-09: Company/Branch Filtering

**Filtering Logic (Unified):**

All list endpoints now use `company_id = %company%` for branch filtering (except payments which uses journal_name):

| Endpoint | Filter Column | Notes |
|----------|---------------|-------|
| `/api/customers` | company_id | Correct |
| `/api/appointments` | company_id | Correct |
| `/api/sale-orders` | company_id | Fixed |
| `/api/products` | company_id | Fixed |
| `/api/employees` | company_id | Correct |
| `/api/callcenter` | company_id | Correct |
| `/api/stock-pickings` | company_id | Correct |
| `/api/stock-moves` | company_id | Correct |
| `/api/stock-moves/summary` | company_id | Correct |
| `/api/payments` | journal_name | Legacy - uses journal_name ILIKE |

## Compatibility Notes

### Breaking Changes

1. **sale-orders endpoint**: Changed company filter from `company_name ILIKE` to `company_id =`
   - Frontend must now pass company UUID, not company name
   - Verified: Frontend passes `currentCompanyId` which is already a UUID

2. **products endpoint**: Changed company filter from `company_name ILIKE` to `company_id =`
   - Added `company_id` to response fields
   - Frontend should work without changes (already passes UUID)

### Non-Breaking Changes

1. Added `company_id` to sale-orders response (new field)
2. Added `company_id` to products response (new field)

### Frontend Verification Required

- Verify `loadTreatments()` - ensure company filter works with UUID
- Verify `loadProducts()` - ensure company filter works with UUID
- Check `currentCompanyId` is correctly populated in all pages

## Response Shape Standardization

All list endpoints now return consistent shape:

```json
{
  "total": 100,
  "page": 1,
  "per_page": 50,
  "total_pages": 2,
  "items": [
    {
      "id": "uuid",
      "company_id": "uuid",
      "company_name": "string",
      // ... other fields
    }
  ]
}
```

Stock summary endpoint returns additional `totals` object:

```json
{
  "total": 50,
  "page": 1,
  "per_page": 20,
  "total_pages": 3,
  "items": [...],
  "totals": {
    "total_qty_in": 100,
    "total_amt_in": 5000000,
    "total_qty_out": 80,
    "total_amt_out": 4000000
  }
}
```
