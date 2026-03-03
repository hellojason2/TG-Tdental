"""Shared implementation for exhaustive page/function interaction audits."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playwright.async_api import BrowserContext, Page, async_playwright

from generate_scope_manifests import parse_routes

DEFAULT_LOGIN_EMAIL = "admin@tdental.vn"
DEFAULT_LOGIN_PASSWORD = "admin123"
PLACEHOLDER_ID = "00000000-0000-0000-0000-000000000001"
IGNORED_API_PREFIXES = ("/api/auth/", "/api/notifications/init", "/api/notifications/inbox")


@dataclass
class BranchOption:
    value: str
    label: str


@dataclass
class CapturedRequest:
    url: str
    method: str
    post_data: str | None


def materialize_route(route: str) -> str:
    return route.replace(":id", PLACEHOLDER_ID)


def expected_hash(route: str) -> str:
    return route.split(":id", 1)[0] if ":id" in route else route


def is_relevant_api_request(url: str) -> bool:
    path = urlparse(url).path or ""
    return "/api/" in path and not any(path.startswith(prefix) for prefix in IGNORED_API_PREFIXES)


def extract_company_ids(req: CapturedRequest) -> list[str]:
    values: list[str] = []
    query = parse_qs(urlparse(req.url).query)
    for key in ("companyId", "company_id", "company"):
        values.extend(str(raw).strip() for raw in query.get(key, []) if str(raw).strip())
    body = req.post_data or ""
    if body:
        try:
            payload = json.loads(body)
            if isinstance(payload, dict):
                for key in ("companyId", "company_id", "company"):
                    if payload.get(key) is not None:
                        val = str(payload[key]).strip()
                        if val:
                            values.append(val)
        except Exception:
            form = parse_qs(body)
            for key in ("companyId", "company_id", "company"):
                values.extend(str(raw).strip() for raw in form.get(key, []) if str(raw).strip())
    return values


async def login(context: BrowserContext, base_url: str, email: str, password: str) -> None:
    resp = await context.request.post(f"{base_url}/api/auth/login", data={"email": email, "password": password})
    if resp.status != 200:
        raise RuntimeError(f"Login failed ({resp.status}): {(await resp.text())[:400]}")


async def wait_settle(page: Page, settle_ms: int) -> None:
    try:
        await page.wait_for_load_state("networkidle", timeout=4500)
    except Exception:
        pass
    await page.wait_for_timeout(settle_ms)


async def read_branch_options(page: Page) -> list[BranchOption]:
    payload = await page.evaluate(
        "() => Array.from(document.querySelectorAll('#branch-selector option')).map((o) => ({value:o.value||'',label:(o.textContent||'').trim()}))"
    )
    return [BranchOption(value=str(p.get("value", "")), label=str(p.get("label", ""))) for p in payload if p.get("value")]


async def set_branch(page: Page, branch_value: str, settle_ms: int) -> bool:
    ok = await page.evaluate(
        """
        (value) => {
          const sel = document.getElementById('branch-selector');
          if (!sel) return false;
          if (!Array.from(sel.options).some((o) => o.value === value)) return false;
          sel.value = value;
          sel.dispatchEvent(new Event('change', { bubbles: true }));
          return true;
        }
        """,
        branch_value,
    )
    await wait_settle(page, settle_ms)
    return bool(ok)


async def discover_actions(page: Page, max_actions: int) -> list[dict]:
    return await page.evaluate(
        """
        (maxActions) => {
          const allow = ['tất cả','chờ','đang','hoàn','hủy','đã đến','lịch','lọc','filter','refresh','làm mới','tuần','tháng','ngày','hôm nay','chi tiết','sửa','edit','xem'];
          const deny = ['xóa','delete','lưu','save','cập nhật','thanh toán','duyệt','xác nhận xóa'];
          const out = [];
          const norm = (v) => (v || '').replace(/\\s+/g, ' ').trim();
          const visible = (el) => {
            const st = getComputedStyle(el);
            return st.visibility !== 'hidden' && st.display !== 'none' && el.offsetParent !== null;
          };
          let seq = 0;
          for (const el of document.querySelectorAll('button,[role="button"],a,.tab,.db-tab-btn,.tds-btn')) {
            if (out.length >= maxActions || !visible(el)) continue;
            if (el.closest('.sidebar,.tds-sidebar,#sidebar,nav.sidebar')) continue;
            const label = norm(el.getAttribute('aria-label') || el.getAttribute('title') || el.textContent);
            const lower = label.toLowerCase();
            const cls = String(el.className || '').toLowerCase();
            const attrs = [el.getAttribute('data-filter'),el.getAttribute('data-state'),el.getAttribute('data-status'),el.getAttribute('data-tab')].filter(Boolean).join(' ').toLowerCase();
            const likely = allow.some((k) => lower.includes(k)) || cls.includes('tab') || cls.includes('filter') || cls.includes('refresh') || attrs.length > 0;
            if (!likely || deny.some((k) => lower.includes(k))) continue;
            const id = `audit-action-${Date.now()}-${seq++}`;
            el.setAttribute('data-audit-action-id', id);
            out.push({ id, label: label || id });
          }
          return out;
        }
        """,
        max_actions,
    )


async def run_search_inputs(page: Page, settle_ms: int, max_inputs: int) -> list[dict]:
    inputs = await page.evaluate(
        """
        (maxInputs) => {
          const out = [];
          const norm = (v) => (v || '').replace(/\\s+/g, ' ').trim().toLowerCase();
          let idx = 0;
          for (const el of document.querySelectorAll('input[type="search"],input[type="text"]')) {
            if (out.length >= maxInputs || el.offsetParent === null) continue;
            if (el.id === 'global-search-input') continue;
            const ph = norm(el.getAttribute('placeholder'));
            if (!(ph.includes('tìm') || ph.includes('search') || ph.includes('lọc'))) continue;
            const id = `audit-search-${Date.now()}-${idx++}`;
            el.setAttribute('data-audit-search-id', id);
            out.push({ id, placeholder: ph || '' });
          }
          return out;
        }
        """,
        max_inputs,
    )
    results: list[dict] = []
    for item in inputs:
        loc = page.locator(f'[data-audit-search-id="{item["id"]}"]').first
        try:
            await close_transient(page)
            await loc.fill("audit")
            await page.keyboard.press("Enter")
            await wait_settle(page, settle_ms)
            if await loc.is_visible():
                await loc.fill("")
                await wait_settle(page, 120)
            results.append({"ok": True, "placeholder": item.get("placeholder", "")})
        except Exception as exc:
            results.append({"ok": False, "placeholder": item.get("placeholder", ""), "error": str(exc)})
    return results


async def close_transient(page: Page) -> None:
    for sel in (".swal2-cancel", ".swal2-close", "#modal-close-btn", ".modal .btn-close", ".tds-modal .btn-close"):
        loc = page.locator(sel)
        if await loc.count() > 0:
            try:
                await loc.first.click()
                await page.wait_for_timeout(120)
            except Exception:
                pass
    await page.keyboard.press("Escape")
    await page.wait_for_timeout(120)


async def run_tab_population_check(page: Page, settle_ms: int) -> list[dict]:
    groups = page.locator(".db-tabs,.tabs,[role='tablist'],.db-reception-tabs,.db-schedule-tabs")
    checks: list[dict] = []
    for i in range(min(await groups.count(), 3)):
        tabs = groups.nth(i).locator("button,[role='tab'],.db-tab-btn")
        rows: list[tuple[str, str, int | None]] = []
        for j in range(min(await tabs.count(), 6)):
            tab = tabs.nth(j)
            if not await tab.is_visible():
                continue
            label = (" ".join((await tab.inner_text()).split())).strip()
            try:
                await tab.click()
                await wait_settle(page, settle_ms)
                sig = await tab.evaluate(
                    """
                    (node) => {
                      const panel = node.closest('.db-panel,.panel,.card,section,.tds-card') || document.body;
                      const rows = panel.querySelectorAll('tbody tr,.db-reception-row,.db-schedule-item,.reception-card,.work-table-row,.work-kanban-card,li');
                      return Array.from(rows).slice(0, 8).map((r) => (r.textContent || '').replace(/\\s+/g, ' ').trim()).filter(Boolean).join('|').slice(0, 600);
                    }
                    """
                )
                digits = "".join(ch for ch in label if ch.isdigit())
                rows.append((label, sig, int(digits) if digits else None))
            except Exception:
                continue
        if len(rows) >= 2:
            suspicious = len({r[2] for r in rows if r[2] is not None}) > 1 and len({r[1] for r in rows if r[1]}) == 1
            checks.append({"suspicious": suspicious, "rows": [{"label": r[0], "count": r[2]} for r in rows]})
    return checks


async def run_full_audit(args) -> dict:
    routes = parse_routes(Path(args.tasks_md))
    if args.route_limit and args.route_limit > 0:
        routes = routes[: args.route_limit]
    output_path = Path(args.output)
    evidence_dir = output_path.parent / "cells"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    requests: list[CapturedRequest] = []
    page_errors: list[str] = []
    cells: list[dict] = []
    failures: list[dict] = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=not args.headed)
        context = await browser.new_context(viewport={"width": 1660, "height": 980}, ignore_https_errors=True)
        await login(context, args.base_url, args.email, args.password)
        page = await context.new_page()
        page.on("request", lambda req: requests.append(CapturedRequest(url=req.url, method=req.method, post_data=req.post_data)))
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))
        await page.goto(f"{args.base_url}/static/tdental.html#/dashboard", wait_until="domcontentloaded")
        await wait_settle(page, args.settle_ms)
        branches = await read_branch_options(page)
        if args.branch_limit and args.branch_limit > 0:
            branches = branches[: args.branch_limit]
        if not branches:
            raise RuntimeError("No branch options found in #branch-selector")
        for route_entry in routes:
            for branch in (branches if route_entry.branch_aware else branches[:1]):
                req_start, err_start = len(requests), len(page_errors)
                route = route_entry.route
                cell = {"route": route, "branch": branch.label, "branchValue": branch.value, "branchAware": route_entry.branch_aware, "ok": True, "actions": []}
                await page.goto(f"{args.base_url}/static/tdental.html{materialize_route(route)}", wait_until="domcontentloaded")
                await wait_settle(page, args.settle_ms)
                if route_entry.branch_aware and not await set_branch(page, branch.value, args.settle_ms):
                    cell["ok"] = False
                    cell["actions"].append({"type": "branch", "ok": False, "reason": "branch option not selectable"})
                req_start = len(requests)
                if not page.url.split("#", 1)[-1].startswith(expected_hash(route).lstrip("#")):
                    cell["ok"] = False
                    cell["actions"].append({"type": "navigation", "ok": False, "reason": f"hash mismatch: {page.url}"})

                for idx in range(args.max_actions_per_page):
                    actions = await discover_actions(page, args.max_actions_per_page + 6)
                    if idx >= len(actions):
                        break
                    action = actions[idx]
                    try:
                        await close_transient(page)
                        await page.locator(f'[data-audit-action-id="{action["id"]}"]').first.click(timeout=3000)
                        await wait_settle(page, args.settle_ms // 2)
                        await close_transient(page)
                        cell["actions"].append({"type": "control", "label": action["label"], "ok": True})
                    except Exception as exc:
                        cell["ok"] = False
                        cell["actions"].append({"type": "control", "label": action["label"], "ok": False, "reason": str(exc)})
                for item in await run_search_inputs(page, args.settle_ms // 2, args.max_search_inputs):
                    if not item.get("ok"):
                        cell["ok"] = False
                    cell["actions"].append({"type": "search", "ok": bool(item.get("ok")), "placeholder": item.get("placeholder", ""), "reason": item.get("error", "")})
                for tab_check in await run_tab_population_check(page, args.settle_ms // 2):
                    if tab_check.get("suspicious"):
                        cell["ok"] = False
                        cell["actions"].append({"type": "tab_population", "ok": False, "reason": "tab switched but content signatures did not change", "rows": tab_check["rows"]})
                relevant = [r for r in requests[req_start:] if is_relevant_api_request(r.url)]
                if route_entry.branch_aware and relevant:
                    bad = [{"url": r.url, "ids": ids} for r in relevant if (ids := extract_company_ids(r)) and branch.value not in ids]
                    if bad:
                        cell["ok"] = False
                        cell["actions"].append({"type": "branch_propagation", "ok": False, "reason": "companyId mismatch in API requests", "samples": bad[:5]})
                if page_errors[err_start:]:
                    cell["ok"] = False
                    cell["actions"].append({"type": "console_error", "ok": False, "reason": page_errors[err_start:err_start + 3]})
                shot = evidence_dir / f"{route.replace('#/', '').replace('/', '_').replace(':id', 'id')}--{branch.value[:8]}.png"
                await page.screenshot(path=str(shot), full_page=False)
                cell["screenshot"] = str(shot)
                if not cell["ok"]:
                    failures.append({"route": route, "branch": branch.label, "details": cell["actions"][-6:], "screenshot": str(shot)})
                cells.append(cell)
        await context.close()
        await browser.close()
    actions_total = sum(len(c["actions"]) for c in cells)
    actions_failed = sum(1 for c in cells for a in c["actions"] if not a.get("ok", True))
    cells_failed = sum(1 for c in cells if not c["ok"])
    return {
        "status": "PASS" if cells_failed == 0 and actions_failed == 0 else "REWORK",
        "summary": {"routes": len(routes), "branches": len({c["branchValue"] for c in cells}), "cells_total": len(cells), "cells_failed": cells_failed, "actions_total": actions_total, "actions_failed": actions_failed},
        "failures": failures[:500],
        "cells": cells,
    }
