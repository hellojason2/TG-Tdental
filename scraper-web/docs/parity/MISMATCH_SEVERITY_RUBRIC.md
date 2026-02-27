# TDental Parity Mismatch Severity Rubric

## Overview
This document defines the severity classification system for visual and behavioral mismatches between local TDental replica and live TDental.

## Severity Levels

### CRITICAL (P0)
**Definition**: Functionality-blocking issues that prevent core user workflows.

Examples:
- Login page not accessible or throws errors
- Dashboard fails to load any data
- Customer list returns empty/error
- Unable to create/edit/delete records
- Complete layout collapse
- JavaScript errors blocking interactions

**Acceptance Threshold**: MUST be zero critical issues before deployment.

---

### HIGH (P1)
**Definition**: Significant visual or functional deviations that impact daily operations but have workarounds.

Examples:
- Sidebar navigation broken or missing items
- Table columns misaligned or missing data
- Status badges showing wrong colors/labels
- Pagination not working correctly
- Search/filter returns incorrect results
- Modal/drawer opens but has layout issues

**Acceptance Threshold**: Maximum 2 HIGH issues per route.

---

### MEDIUM (P2)
**Definition**: Noticeable differences that don't block operations but reduce polish.

Examples:
- Typography scale mismatch (font sizes, weights)
- Icon sizes or colors slightly off
- Spacing/padding inconsistencies (< 8px variance)
- Border radius differences
- Hover states not matching
- Empty state messages differ

**Acceptance Threshold**: Maximum 5 MEDIUM issues per route.

---

### MINOR (P3)
**Definition**: Cosmetic differences only visible on close inspection.

Examples:
- Subtle color hex variations (< 5% difference)
- Micro-spacing differences (1-2px)
- Animation timing variations
- Tooltip text wording differences
- Date/time format variations

**Acceptance Threshold**: Maximum 10 MINOR issues per route.

---

## Acceptance Thresholds by Priority

### Critical Routes (Must Pass 100%)
Routes: Login, Dashboard, Customers, Calendar

| Severity | Threshold |
|----------|-----------|
| Critical | 0 |
| High | 0 |
| Medium | 2 |
| Minor | 5 |

### High Priority Routes
Routes: Reception, Treatments, Sale Orders

| Severity | Threshold |
|----------|-----------|
| Critical | 0 |
| High | 1 |
| Medium | 3 |
| Minor | 7 |

### Medium Priority Routes
Routes: Inventory, HR, Accounting, Call Center, Reports

| Severity | Threshold |
|----------|-----------|
| Critical | 0 |
| High | 2 |
| Medium | 5 |
| Minor | 10 |

### Low Priority Routes
Routes: Categories, Locations, Users, Settings

| Severity | Threshold |
|----------|-----------|
| Critical | 0 |
| High | 3 |
| Medium | 7 |
| Minor | 15 |

---

## Parity Check Categories

### 1. Layout Parity
- [ ] Container widths match
- [ ] Sidebar width and collapse behavior
- [ ] Header/topbar height and alignment
- [ ] Card padding and margins
- [ ] Grid/flex alignment

### 2. Typography Parity
- [ ] Font family (exact match required)
- [ ] Font sizes (exact match required)
- [ ] Font weights (exact match required)
- [ ] Line heights
- [ ] Text colors

### 3. Visual Parity
- [ ] Background colors
- [ ] Border colors and widths
- [ ] Border radius values
- [ ] Box shadows
- [ ] Icon sizes and colors

### 4. Interaction Parity
- [ ] Button hover states
- [ ] Link hover states
- [ ] Focus states
- [ ] Active/selected states
- [ ] Disabled states
- [ ] Loading states
- [ ] Error states

### 5. Component Parity
- [ ] Tables: columns, sorting, row height
- [ ] Forms: labels, inputs, validation
- [ ] Modals: size, animation, overlay
- [ ] Dropdowns: options, selection display
- [ ] Tabs: active indicator, content
- [ ] Cards: structure, content order
- [ ] Badges: colors, text

### 6. Behavioral Parity
- [ ] Navigation routing
- [ ] Form submission flow
- [ ] Data loading states
- [ ] Error handling
- [ ] Success feedback
- [ ] Confirmation dialogs

---

## Measurement Guidelines

### Visual Comparison
1. Use viewport: 1440x900 (desktop)
2. Disable browser extensions
3. Use consistent zoom level (100%)
4. Compare in same browser
5. Capture full page screenshots

### Interaction Testing
1. Test each route with admin account
2. Test critical flows:
   - Login -> Dashboard -> Customer List
   - Create new customer
   - Create new appointment
   - Filter and search
   - Pagination
   - Edit/Delete operations

---

## Reporting Format

### Per-Route Report Template
```json
{
  "route": "customers",
  "status": "PASS|FAIL|REVIEW",
  "issues": [
    {
      "id": "CUST-001",
      "severity": "CRITICAL|HIGH|MEDIUM|MINOR",
      "category": "layout|typography|visual|interaction|component|behavioral",
      "description": "Issue description",
      "location": "Element or region",
      "live_behavior": "What live shows",
      "local_behavior": "What local shows",
      "screenshot_ref": "screenshot file reference"
    }
  ],
  "tested_at": "2026-02-27T10:00:00Z",
  "tester": "username"
}
```

---

## Decision Tree

```
Is issue functionality blocking?
├─ YES -> CRITICAL
└─ NO -> Continue

Is issue visually obvious to average user?
├─ YES -> HIGH
└─ NO -> Continue

Does issue require close inspection to notice?
├─ YES -> MINOR
└─ NO -> MEDIUM
```
