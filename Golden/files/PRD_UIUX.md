# PRD UI/UX Loop: Pixel + Interaction Parity

## Project Overview
This loop closes visual and behavioral parity gaps so the replica renders and behaves like the original across all menu modules and all branch contexts.

## Tasks
- [x] U0.1 Capture baseline visual + interaction mismatch report for shell + high-impact pages.
- [x] U0.2 Prioritize defects by user-facing severity (layout break, wrong data widget, wrong behavior, minor token drift).
- [ ] U1.1 Fix sidebar/topbar shell pixel parity (sizes, spacing, iconography, typography, colors).
- [ ] U1.2 Fix sidebar collapsed/expanded/mobile interaction parity (hover, tooltip, focus, overlay close behavior).
- [ ] U1.3 Fix global search UX parity (Ctrl+K, F2, focus transfer, enter navigation, close behavior).
- [ ] U2.1 Ensure branch selector parity (label, dropdown states, persistence, keyboard).
- [ ] U2.2 Ensure branch switches refresh all branch-aware routes correctly for all locations.
- [ ] U3.1 Fix dashboard parity across all locations.
- [ ] U3.2 Fix customers parity across all locations.
- [ ] U3.3 Fix work/tasks parity across all locations.
- [ ] U3.4 Fix calendar parity across all locations.
- [ ] U3.5 Fix reports + cashbook parity across all locations.
- [ ] U4.1 Fix parity for secondary modules (labo, purchase, warehouse, salary family, payments, callcenter, commission, catalog, settings).
- [ ] U5.1 Validate all state variants: default/hover/focus/active/disabled/loading/empty/error.
- [ ] U5.2 Validate page + nested scroll behavior parity and sticky regions.
- [ ] U5.3 Validate nested popup chains for create/edit/delete flows.
- [ ] U6.1 Run final branch matrix + module audits + visual audit and close all REWORK.
- [ ] U6.2 Produce final UI/UX PASS evidence package.

## Required Commands
- `cd files && python3 audit_branch_matrix.py --base-url http://127.0.0.1:8899 --output evidence/2/report.json --write-task-evidence`
- `cd files && python3 audit_phase3_4.py --base-url http://127.0.0.1:8899 --output evidence/3-4/report.json --write-task-evidence`
- `cd files && python3 audit_live_playwright_parity.py --output evidence/live-parity/report.json`
- `cd backend && python3 tests/visual_parity_audit.py --base-url http://127.0.0.1:8899`
- `cd backend && python3 -m pytest tests -q`

## Definition of Done
1. Branch matrix passes all required cells.
2. Module/state/scroll/modal checks pass for core and secondary routes.
3. Visual parity audit has no unresolved review mismatches.
4. No UI regression in backend/frontend tests relevant to touched flows.

Output `<promise>COMPLETE</promise>` when ALL verified.
