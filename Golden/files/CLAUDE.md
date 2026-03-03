# CLAUDE.md - TDental Golden 100% Parity Loop

## What This Project Is
This is an existing TDental replica in `Golden/` that must be corrected to match the original system exactly in data, API behavior, UI, and UX interactions. We are not rebuilding architecture. We are closing parity gaps with strict compare-and-remediate loops.

## Existing Infrastructure (DO NOT MODIFY)
- App root: `Golden/`
- Backend: `backend/` (FastAPI)
- Admin SPA: `backend/static/tdental.html`, `backend/static/js/app.js`, `backend/static/css/tdental.css`
- Source DB (reference): MSSQL `TDental` on `127.0.0.1:1433` (container `tdental-mssql-temp`)
- Replica DB (runtime): PostgreSQL `tdental` on `127.0.0.1:55433` (container `tdental-postgres-local`)
- Secondary Postgres container exists on `:5432` (`tdental-db`) and must not be touched unless task explicitly requires it.
- Local app URL: `http://127.0.0.1:8899`
- Original reference URL: `https://tamdentist.tdental.com`

## Current Verified Gaps (Start State)
- Source vs replica exact table-count audit found one real row-count mismatch: `dbo.accountpayments` (+3 rows in Postgres).
- Missing FK signatures in Postgres for 7 source `dbo` tables (plus 2 extra FKs on app-only `public` tables).
- UI parity is not exact: nav shell and dashboard/customer visual/interaction states still diverge from original.
- Previous “all tasks checked” status is invalid for 100% sign-off and must be reworked from this scope.

## Domain Rules
- Branch/location behavior is a hard gate: all discovered branches must propagate correct `companyId` on branch-aware routes.
- Data shown on replica must come from the migrated source-equivalent records for each selected branch.
- Pixel parity is strict for structure, spacing, typography, icon sizes, and component composition.
- Interaction parity is strict: hover/focus/active/scroll/edit/modal/nested popup behavior must match.

## Code Conventions
- Python 3.11+, type hints on non-trivial functions.
- Keep scripts deterministic and idempotent.
- Use JSON evidence artifacts under `files/evidence/`.
- Keep files <= 300 lines where practical; split by responsibility.

## Project Rules
1. ONE TASK PER ITERATION.
2. Read `CLAUDE.md` -> `PRD.md` -> `ONE_SHOT_SCOPE.md` -> `progress.txt` before coding.
3. Run required checks after each task:
   - `cd backend && python3 -m pytest tests -q`
4. For data tasks, run:
   - `cd files && python3 audit_data_parity.py --output evidence/data/report.json --write-task-evidence`
5. For UI/UX tasks, run:
   - `cd files && python3 audit_full_function_matrix.py --base-url http://127.0.0.1:8899 --output evidence/full-function/report.json --max-actions-per-page 12 --max-search-inputs 3`
   - `cd files && python3 audit_branch_matrix.py --base-url http://127.0.0.1:8899 --output evidence/2/report.json --write-task-evidence`
   - `cd files && python3 audit_phase3_4.py --base-url http://127.0.0.1:8899 --output evidence/3-4/report.json --write-task-evidence`
   - `cd files && python3 audit_live_playwright_parity.py --output evidence/live-parity/report.json`
   - `cd backend && python3 tests/visual_parity_audit.py --base-url http://127.0.0.1:8899`
6. Mandatory loop for current task: implement -> test -> compare -> if mismatch then remediate -> repeat until PASS.
7. Do not mark task complete while any gate file shows `REWORK`.
8. Update `progress.txt` for every completed or reworked task.
9. Never modify files outside `Golden/`.
10. Never hardcode secrets; use env/config.

## Known Gotchas
- `pg_stat_user_tables` counts can drift; use exact `COUNT(*)` for parity decisions.
- Branch switching can appear correct while stale cache serves old data.
- Visual capture timing causes false diffs; wait for settled UI before screenshot.
- Missing FK creation during import may hide migration defects even when row counts match.
- Global search input can exist in DOM while hidden; interaction audits must skip non-visible overlay inputs to avoid false failures/timeouts.
- Branch selector options can load asynchronously after first paint; audits must retry branch discovery instead of failing immediately when only the blank option is present.
- Generic modal-close selectors may exist while hidden; audit click helpers must check visibility and use short timeouts to avoid 30s Playwright hangs.
- If a new gotcha is discovered, ADD IT here in the same iteration.
