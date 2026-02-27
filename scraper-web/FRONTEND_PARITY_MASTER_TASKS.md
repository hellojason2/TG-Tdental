# TDental Frontend Parity Master Task List

Objective: achieve route-by-route visual and behavior parity with live TDental using existing local admin + data.

Ground-truth code for this plan:
- `/Users/thuanle/Documents/TamTMV/Tdental/scraper-web/static/tdental.html`
- `/Users/thuanle/Documents/TamTMV/Tdental/scraper-web/static/js/app.js`
- `/Users/thuanle/Documents/TamTMV/Tdental/scraper-web/static/css/style.css`
- `/Users/thuanle/Documents/TamTMV/Tdental/scraper-web/static/compare.html`
- `/Users/thuanle/Documents/TamTMV/Tdental/scraper-web/app/api/routes.py`

Execution rule:
- Complete tasks in order.
- Do not mark any task done until both visual parity and interaction parity pass.
- Every UI fix must include regression checks on dependent screens.

## Phase 0 - Parity Harness (Required Before UI Fixes)

- [x] `P0-01` Build a route parity matrix (live route -> local route -> required state/filter -> expected widgets).
- [x] `P0-02` Standardize comparison viewport and browser settings for all captures (desktop first, then mobile).
- [x] `P0-03` Fix compare tool defaults and state sync in `/static/compare.html` (input default `3020` vs iframe default `8899`, route/state mismatch handling).
- [x] `P0-04` Replace iframe-dependent live compare with Playwright screenshot capture flow (live often blocks iframe/X-Frame).
- [x] `P0-05` Save baseline artifacts per route: local screenshot, live screenshot, difference notes, timestamp.
- [x] `P0-06` Create mismatch severity rubric (`critical`, `high`, `medium`, `minor`) and acceptance thresholds.
- [x] `P0-07` Define exact parity done criteria per route (layout, typography, spacing, colors, states, interactions).

## Phase 1 - Global Shell Parity (Applies to All Routes)

- [x] `P1-01` Match sidebar shell (width, item spacing, icon sizing, active/hover styles, collapse behavior).
- [x] `P1-02` Match topbar shell (search box, branch selector, uptime chip, bell/avatar alignment).
- [x] `P1-03` Normalize global spacing and card system across pages (padding, gaps, border radius, shadows).
- [x] `P1-04` Normalize typography scale and weights to live (headings, table cells, labels, badges).
- [x] `P1-05` Standardize empty/loading/error states to mirror live behavior and tone.
- [x] `P1-06` Replace intrusive `alert()` UX with inline messages/toasts where live does not use blocking dialogs.
- [ ] `P1-07` Remove inline style drift in JS-rendered HTML snippets where it causes visual inconsistency.
- [x] `P1-08` Verify responsive behavior for shell at mobile and tablet breakpoints.

## Phase 2 - Route-by-Route UI Parity

- [ ] `P2-01` Dashboard (`#/dashboard`): panel layout, tab bars, card metrics, list blocks, and chart visuals.
- [ ] `P2-02` Dashboard interactions: tab switching, search/filter behavior, row click actions, quick-action buttons.
- [x] `P2-03` Customers (`#/partners/customers` <-> local `customers`): toolbar, tabs, table density, pagination, action icons. [DONE - see docs/parity/P2-03_P2-04_CUSTOMERS_PARITY_CHECKLIST.md]
- [ ] `P2-04` Customer detail drawer/modal parity: profile fields, linked data sections, close/open behavior. [PARTIAL - tabs content needs implementation]
- [ ] `P2-05` Reception (`#/reception`): queue cards/tables, status counters, refresh/add actions.
- [ ] `P2-06` Calendar (`#/calendar`): date nav, status filters, list/calendar rendering, appointment actions.
- [ ] `P2-07` Treatments (`#/treatments`): state tabs, table columns, status badges, row actions.
- [ ] `P2-08` Sale/Purchase route parity (`#/sale-management` <-> local `purchase`): list structure and totals.
- [ ] `P2-09` Inventory (`#/stock` <-> local `inventory`): summary, in/out/history tabs, totals row, filters.
- [ ] `P2-10` HR (`#/hr/employees` <-> local `salary`): employee table, filter/search, paging behavior.
- [ ] `P2-11` Accounting (`#/accounting` <-> local `cashbook`): payment table, amount formatting, state labels.
- [ ] `P2-12` Call center (`callcenter`) and commission sections: list UX and navigation consistency.
- [ ] `P2-13` Reports (`reports`): tab structure, date/filter controls, chart/table compositions.
- [ ] `P2-14` Categories (`categories`): left taxonomy nav + detail panel parity for all supported category types.
- [ ] `P2-15` Locations (`locations`): card/list visuals and add/edit flow parity.
- [ ] `P2-16` Users (`users`): list table + permission matrix visual and interaction parity.
- [ ] `P2-17` Settings (`settings`): tab nav, forms, save flow, export controls, and confirmation behavior.
- [ ] `P2-18` Login page parity (`/login`): structure, spacing, icons, validation UX, loading states.

## Phase 3 - Interaction and Workflow Parity

- [ ] `P3-01` Ensure all sidebar and sub-sidebar routes map correctly and no dead links remain.
- [ ] `P3-02` Ensure branch switching updates all active pages consistently.
- [ ] `P3-03` Ensure global search (`F2`) behavior and shortcuts match live expectations.
- [ ] `P3-04` Ensure modal workflows parity for create reception, create appointment, create customer.
- [ ] `P3-05` Ensure edit/delete flows parity for appointments, customers, and treatments where applicable.
- [ ] `P3-06` Replace placeholder actions still showing "Tính năng đang phát triển" where live supports the action.
- [ ] `P3-07` Keep placeholder actions explicit where live also does not provide the function.
- [ ] `P3-08` Ensure notification, chat, and utility actions follow live behavior or are intentionally gated.
- [ ] `P3-09` Ensure hash-route deep linking and page reload behavior preserves expected state.

## Phase 4 - Data Contract and API Parity (Backend + Frontend Coupling)

- [ ] `P4-01` Build endpoint mapping from captured live API spec to local API (`method`, `path`, `params`, response shape).
- [ ] `P4-02` Align query parameter semantics (`company`, `state`, `date ranges`, pagination names and defaults).
- [ ] `P4-03` Align status dictionaries and label text across appointments, sale orders, and payments.
- [ ] `P4-04` Replace silent `except: pass` blocks in `/app/api/routes.py` with explicit handling/logging.
- [ ] `P4-05` Expand category APIs to support all category keys used in `tdental.html` menu.
- [ ] `P4-06` Persist settings in DB or config store (current `/api/settings` update is non-persistent).
- [ ] `P4-07` Ensure export endpoints and UI triggers match live behavior (replace report export placeholder).
- [ ] `P4-08` Ensure authentication/session behavior is consistent between `/login`, `/`, API calls, and cookies.
- [ ] `P4-09` Verify company/branch filtering logic is consistent across all list endpoints.

## Phase 5 - Remove Known Gaps and Technical Debt Blocking Parity

- [ ] `P5-01` Fix compare tool limitations and route map coverage in `/static/compare.html`.
- [ ] `P5-02` Wire settings page "Áp dụng" button to real save flow instead of static alert.
- [ ] `P5-03` Replace remaining fallback demo snippets that diverge from real live behavior.
- [ ] `P5-04` Audit all `alert()` usage and keep only flows where blocking confirm is intentionally required.
- [ ] `P5-05` Audit all inline SVG/icon choices against live and replace mismatched assets.
- [ ] `P5-06` Audit localization consistency (Vietnamese labels, money/date formats, status text).

## Phase 6 - Automated Verification (Permanent Fix Guardrails)

- [x] `P6-01` Add Playwright parity script for screenshot capture on all target routes.
- [x] `P6-02` Add automated interaction checks per route (open page, filter, paginate, open modal, submit/cancel).
- [x] `P6-03` Add API contract smoke tests for critical endpoints used by visible UI blocks.
- [x] `P6-04` Add regression pack for shared components (sidebar, topbar, pagination, modal, tables).
- [x] `P6-05` Add pre-release checklist requiring green visual + interaction tests before deploy.

## Phase 7 - Final Readiness and Rollout

- [ ] `P7-01` Run full route walkthrough on local with admin account and verify no console errors.
- [ ] `P7-02` Run full route walkthrough with viewer role and verify permission gating matches design.
- [ ] `P7-03` Produce final parity report (before/after screenshots + list of intentional deviations).
- [ ] `P7-04` Execute deployment checklist and post-deploy smoke run on production target.

## First Execution Order (Start Here)

1. `P0-01` through `P0-07`
2. `P1-01` through `P1-08`
3. `P2-01` through `P2-04` (Dashboard + Customers first)
4. `P6-01` and `P6-02` immediately after first two routes are aligned
5. Continue remaining `P2`, then `P3`, `P4`, `P5`, `P6`, `P7`

