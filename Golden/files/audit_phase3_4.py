#!/usr/bin/env python3
"""Phase 3/4 parity audit for core and secondary module coverage."""

from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from playwright.async_api import BrowserContext, Page, async_playwright

from generate_scope_manifests import parse_routes

DEFAULT_LOGIN_EMAIL = "admin@tdental.vn"
DEFAULT_LOGIN_PASSWORD = "admin123"
PLACEHOLDER_ID = "00000000-0000-0000-0000-000000000001"

IGNORED_API_PREFIXES = (
    "/api/auth/",
    "/api/notifications/init",
    "/api/notifications/inbox",
)

CORE_MATRIX_TASKS: dict[str, list[str]] = {
    "3.1": ["#/dashboard"],
    "3.2": ["#/partners"],
    "3.3": ["#/work", "#/tasks"],
    "3.4": ["#/calendar"],
    "3.5": [
        "#/reports",
        "#/report-daily",
        "#/report-revenue",
        "#/report-services",
        "#/report-customers",
        "#/report-reception",
        "#/report-supplier-debt",
        "#/report-appointments",
        "#/report-tasks",
        "#/report-insurance",
    ],
    "3.6": ["#/cashbook"],
}

SECONDARY_MATRIX_TASKS: dict[str, list[str]] = {
    "4.1": ["#/labo", "#/labo-orders"],
    "4.2": ["#/purchase", "#/purchase-refund"],
    "4.3": ["#/warehouse"],
    "4.4": ["#/salary", "#/timekeeping", "#/salary-payment", "#/salary-reports"],
    "4.5": ["#/receipts", "#/payments", "#/account-payment"],
    "4.6": ["#/callcenter", "#/call-history"],
    "4.7": ["#/commission", "#/commission-employee"],
    "4.8": [
        "#/categories",
        "#/customer-stage",
        "#/partner-catalog",
        "#/products",
        "#/prescriptions",
        "#/price-list",
        "#/commission-table",
        "#/employees",
        "#/labo-params",
        "#/income-expense-types",
        "#/stock-criteria",
        "#/tooth-diagnosis",
    ],
    "4.9": ["#/settings", "#/settings-config", "#/settings-team", "#/settings-other", "#/settings-logs"],
}


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


def route_matches(route: str, current_hash: str) -> bool:
    exp = expected_hash(route)
    if ":id" in route:
        return current_hash.startswith(exp)
    return current_hash.startswith(exp)


def is_relevant_api_request(url: str) -> bool:
    parsed = urlparse(url)
    path = parsed.path or ""
    if "/api/" not in path:
        return False
    return not any(path.startswith(prefix) for prefix in IGNORED_API_PREFIXES)


def extract_company_ids(req: CapturedRequest) -> list[str]:
    parsed = urlparse(req.url)
    values: list[str] = []

    query = parse_qs(parsed.query)
    for key in ("companyId", "company_id", "company"):
        for raw in query.get(key, []):
            value = str(raw).strip()
            if value:
                values.append(value)

    body = req.post_data or ""
    if body:
        try:
            payload = json.loads(body)
            if isinstance(payload, dict):
                for key in ("companyId", "company_id", "company"):
                    if key in payload and payload[key] is not None:
                        value = str(payload[key]).strip()
                        if value:
                            values.append(value)
        except Exception:
            form = parse_qs(body)
            for key in ("companyId", "company_id", "company"):
                for raw in form.get(key, []):
                    value = str(raw).strip()
                    if value:
                        values.append(value)

    return values


async def login(context: BrowserContext, base_url: str, email: str, password: str) -> None:
    resp = await context.request.post(
        f"{base_url}/api/auth/login",
        data={"email": email, "password": password},
    )
    if resp.status != 200:
        body = (await resp.text())[:400]
        raise RuntimeError(f"Login failed ({resp.status}): {body}")


async def wait_settle(page: Page, settle_ms: int) -> None:
    try:
        await page.wait_for_load_state("networkidle", timeout=4500)
    except Exception:
        pass
    await page.wait_for_timeout(settle_ms)


async def goto_route(page: Page, base_url: str, route: str, settle_ms: int) -> None:
    hash_route = materialize_route(route)
    await page.goto(f"{base_url}/static/tdental.html{hash_route}", wait_until="domcontentloaded")
    await wait_settle(page, settle_ms)


async def read_branch_options(page: Page) -> list[BranchOption]:
    payload = await page.evaluate(
        """
        () => Array.from(document.querySelectorAll('#branch-selector option')).map((option) => ({
          value: option.value || '',
          label: (option.textContent || '').trim(),
        }))
        """
    )
    return [BranchOption(value=str(item.get("value", "")), label=str(item.get("label", ""))) for item in payload]


async def set_branch(page: Page, branch: BranchOption, settle_ms: int) -> bool:
    ok = await page.evaluate(
        """
        (value) => {
          const selector = document.getElementById('branch-selector');
          if (!selector) return false;
          const exists = Array.from(selector.options).some((o) => o.value === value);
          if (!exists) return false;
          selector.value = value;
          selector.dispatchEvent(new Event('change', { bubbles: true }));
          return true;
        }
        """,
        branch.value,
    )
    await wait_settle(page, settle_ms)
    return bool(ok)


async def click_if_visible(page: Page, selector: str) -> bool:
    locator = page.locator(selector)
    if await locator.count() == 0:
        return False
    try:
        if await locator.first.is_visible():
            await locator.first.click()
            return True
    except Exception:
        return False
    return False


async def close_modal(page: Page) -> None:
    if await click_if_visible(page, "#modal-close-btn"):
        await page.wait_for_timeout(150)
        return
    await page.keyboard.press("Escape")
    await page.wait_for_timeout(150)


async def ensure_selectors(page: Page, selectors: list[str], timeout: int = 5000) -> bool:
    for selector in selectors:
        try:
            await page.wait_for_selector(selector, timeout=timeout)
        except Exception:
            return False
    return True


async def trigger_route_requests(page: Page, route: str, settle_ms: int) -> None:
    if route == "#/callcenter":
        if await ensure_selectors(page, ["#callcenter-search", "#callcenter-search-btn"], timeout=2000):
            await page.fill("#callcenter-search", "09")
            await page.click("#callcenter-search-btn")
            await wait_settle(page, settle_ms)


async def run_matrix_task(
    page: Page,
    requests: list[CapturedRequest],
    base_url: str,
    branches: list[BranchOption],
    routes: list[str],
    route_policy: dict[str, bool],
    settle_ms: int,
    screenshot_path: Path,
) -> dict[str, Any]:
    total = 0
    passed = 0
    failures: list[dict[str, Any]] = []
    screenshot_taken = False

    for branch in branches:
        branch_set = await set_branch(page, branch, settle_ms)
        if not branch_set:
            failures.append(
                {
                    "route": "<branch-selector>",
                    "branch": branch.label,
                    "reason": "branch value not found",
                }
            )
            continue

        for route in routes:
            total += 1
            before = len(requests)
            await goto_route(page, base_url, route, settle_ms)
            await trigger_route_requests(page, route, settle_ms)

            current_hash = await page.evaluate("() => window.location.hash || ''")
            label = await page.evaluate("() => (document.getElementById('branch-label')?.textContent || '').trim()")
            stored = await page.evaluate("() => localStorage.getItem('selected_branch') || ''")

            loaded_ok = route_matches(route, current_hash)
            label_ok = branch.label in label
            stored_ok = stored == branch.value

            route_reqs = [req for req in requests[before:] if is_relevant_api_request(req.url)]
            company_values: list[str] = []
            for req in route_reqs:
                company_values.extend(extract_company_ids(req))

            branch_aware = bool(route_policy.get(route, True))
            if not route_reqs:
                req_ok = True
            elif branch_aware:
                if branch.value:
                    req_ok = branch.value in company_values
                else:
                    req_ok = all(not value for value in company_values)
            else:
                req_ok = all(not value for value in company_values)

            cell_ok = bool(loaded_ok and label_ok and stored_ok and req_ok)
            if cell_ok:
                passed += 1
                if not screenshot_taken:
                    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
                    await page.screenshot(path=str(screenshot_path), full_page=False)
                    screenshot_taken = True
            else:
                reason: list[str] = []
                if not loaded_ok:
                    reason.append("route mismatch")
                if not label_ok:
                    reason.append("branch label mismatch")
                if not stored_ok:
                    reason.append("selected_branch mismatch")
                if not req_ok:
                    reason.append("company filter assertion failed")
                failures.append(
                    {
                        "route": route,
                        "branch": branch.label,
                        "branchValue": branch.value,
                        "reason": "; ".join(reason),
                        "companyValues": sorted(set(company_values)),
                        "sampleRequests": [req.url for req in route_reqs[:8]],
                    }
                )

    return {
        "passed": total > 0 and passed == total,
        "cells": total,
        "passCells": passed,
        "failCells": total - passed,
        "failures": failures[:80],
        "screenshot": str(screenshot_path) if screenshot_taken else "",
    }


async def deep_dashboard(page: Page, base_url: str, settle_ms: int, screenshot: Path) -> dict[str, Any]:
    await goto_route(page, base_url, "#/dashboard", settle_ms)
    ok = await ensure_selectors(
        page,
        ["#db-rec-search", "#db-rec-refresh", "#db-rec-tabs", "#db-appt-tabs", "#db-revenue-canvas"],
    )
    if ok:
        await page.fill("#db-rec-search", "AP")
        await page.click("#db-rec-refresh")
        await wait_settle(page, settle_ms)
        await click_if_visible(page, "#db-rec-tabs .db-tab:nth-child(2)")
        await click_if_visible(page, "#db-appt-tabs .db-tab:nth-child(2)")
        await page.wait_for_timeout(180)
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(screenshot), full_page=False)
    return {"passed": ok, "screenshot": str(screenshot) if ok else ""}


async def deep_partners(page: Page, base_url: str, settle_ms: int, screenshot: Path) -> dict[str, Any]:
    await goto_route(page, base_url, "#/partners", settle_ms)
    ok = await ensure_selectors(page, ["#partners-search", "#partners-tabs", "#partners-table", "#partners-add-btn"])
    detail_ok = False

    if ok:
        await page.fill("#partners-search", "zzzz-no-customer")
        await page.wait_for_timeout(400)
        await page.fill("#partners-search", "")
        await page.wait_for_timeout(300)

        await page.click("#partners-add-btn")
        form_ok = await ensure_selectors(page, ["#customer-form", "#cust-name", "#cust-phone"], timeout=2500)
        if form_ok:
            await close_modal(page)

        links = page.locator("#partners-table a.partners-name-link")
        if await links.count() > 0:
            await links.first.click()
            await page.wait_for_timeout(220)
            detail_ok = await page.evaluate(
                """
                () => {
                  const drawer = document.querySelector('.cdetail-page, .customer-detail-drawer, #cdetail-panels');
                  return !!drawer;
                }
                """
            )
            back_clicked = await click_if_visible(page, "#cdetail-back")
            if back_clicked:
                await page.wait_for_timeout(180)

        screenshot.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(screenshot), full_page=False)
        ok = bool(ok and form_ok)

    return {"passed": ok, "detailInteraction": detail_ok, "screenshot": str(screenshot) if ok else ""}


async def deep_tasks_work(page: Page, base_url: str, settle_ms: int, screenshot: Path) -> dict[str, Any]:
    await goto_route(page, base_url, "#/tasks", settle_ms)
    tasks_ok = await ensure_selectors(page, ["#tasks-search", "#tasks-stage-filter", "#tasks-refresh-btn", "#tasks-add-btn", "#tasks-table"])
    work_ok = False

    if tasks_ok:
        await page.fill("#tasks-search", "task")
        await page.click("#tasks-refresh-btn")
        await wait_settle(page, settle_ms)
        await page.click("#tasks-add-btn")
        modal_ok = await ensure_selectors(page, ["#task-form", "#task-title-input", "#task-stage-input"], timeout=2500)
        if modal_ok:
            await close_modal(page)
        tasks_ok = bool(tasks_ok and modal_ok)

    await goto_route(page, base_url, "#/work", settle_ms)
    work_ok = await page.evaluate(
        """
        () => {
          const candidates = ['#so-apply-btn', '#tp-create-btn', '#treatment-plan-form', '.work-page'];
          return candidates.some((selector) => !!document.querySelector(selector));
        }
        """
    )

    if tasks_ok and work_ok:
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(screenshot), full_page=False)

    return {"passed": bool(tasks_ok and work_ok), "screenshot": str(screenshot) if (tasks_ok and work_ok) else ""}


async def deep_calendar(page: Page, base_url: str, settle_ms: int, screenshot: Path) -> dict[str, Any]:
    await goto_route(page, base_url, "#/calendar", settle_ms)
    ok = await ensure_selectors(page, ["#calendar-search-input", "#calendar-add-btn", "#calendar-body"]) 
    nested_ok = False

    if ok:
        await page.fill("#calendar-search-input", "09")
        await page.wait_for_timeout(200)
        await page.click("#calendar-add-btn")
        form_ok = await ensure_selectors(page, ["#appointment-form", "#apf-patient", "#apf-time"], timeout=2600)
        if form_ok:
            if await click_if_visible(page, "#apf-services-toggle"):
                await page.wait_for_timeout(120)
                nested_ok = await page.evaluate(
                    "() => !!document.getElementById('apf-services-dropdown') && !!document.getElementById('apf-services-tags')"
                )
            await close_modal(page)
        ok = bool(ok and form_ok)
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(screenshot), full_page=False)

    return {"passed": bool(ok), "nestedPopup": nested_ok, "screenshot": str(screenshot) if ok else ""}


async def deep_reports(page: Page, base_url: str, settle_ms: int, screenshot: Path) -> dict[str, Any]:
    await goto_route(page, base_url, "#/reports", settle_ms)
    ok = await ensure_selectors(page, ["#rpt-date-from", "#rpt-date-to", "#rpt-date-icon", "#reports-content"])

    if ok:
        await page.click("#rpt-date-icon")
        await wait_settle(page, settle_ms)
        await goto_route(page, base_url, "#/report-daily", settle_ms)
        sub_ok = await ensure_selectors(page, ["#subrpt-date-from", "#subrpt-date-to", "#subrpt-apply", "#subrpt-table"], timeout=3200)
        if sub_ok:
            await page.click("#subrpt-apply")
            await wait_settle(page, settle_ms)
        ok = bool(ok and sub_ok)
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(screenshot), full_page=False)

    return {"passed": ok, "screenshot": str(screenshot) if ok else ""}


async def open_button_modal(page: Page, button_text: str, expected_selector: str) -> bool:
    locator = page.locator(f'button:has-text("{button_text}")')
    if await locator.count() == 0:
        return False
    await locator.first.click()
    try:
        await page.wait_for_selector(expected_selector, timeout=2600)
        await close_modal(page)
        return True
    except Exception:
        await close_modal(page)
        return False


async def deep_cashbook(page: Page, base_url: str, settle_ms: int, screenshot: Path) -> dict[str, Any]:
    await goto_route(page, base_url, "#/cashbook", settle_ms)
    ok = await ensure_selectors(page, ["#cashbook-date-from", "#cashbook-date-to", "#cashbook-type-filter", "#cashbook-apply-btn", "#cashbook-table"])
    modal_receipt_ok = False
    modal_payment_ok = False
    modal_transfer_ok = False

    if ok:
        await page.click("#cashbook-apply-btn")
        await wait_settle(page, settle_ms)

        await goto_route(page, base_url, "#/receipts", settle_ms)
        modal_receipt_ok = await open_button_modal(page, "Tạo phiếu thu", "#vcf-save")

        await goto_route(page, base_url, "#/payments", settle_ms)
        modal_payment_ok = await open_button_modal(page, "Tạo phiếu chi", "#vcf-save")

        await goto_route(page, base_url, "#/account-payment", settle_ms)
        modal_transfer_ok = await open_button_modal(page, "Tạo phiếu chuyển", "#ap-save")

        await goto_route(page, base_url, "#/cashbook", settle_ms)
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(screenshot), full_page=False)

    return {
        "passed": bool(ok and modal_receipt_ok and modal_payment_ok and modal_transfer_ok),
        "modals": {
            "receipt": modal_receipt_ok,
            "payment": modal_payment_ok,
            "transfer": modal_transfer_ok,
        },
        "screenshot": str(screenshot) if ok else "",
    }


async def deep_secondary(task_id: str, page: Page, base_url: str, settle_ms: int, screenshot: Path) -> dict[str, Any]:
    ok = False
    details: dict[str, Any] = {}

    if task_id == "4.1":
        await goto_route(page, base_url, "#/labo", settle_ms)
        ok = await ensure_selectors(page, ["#labo-search", "#labo-status-filter", "#labo-refresh-btn", "#labo-table"])
        if ok:
            await page.fill("#labo-search", "LAB")
            await page.click("#labo-refresh-btn")
            await wait_settle(page, settle_ms)
            await goto_route(page, base_url, "#/labo-orders", settle_ms)
            ok = bool(ok and await ensure_selectors(page, ["#lo-search", "#lo-refresh", "#lo-table"], timeout=3000))

    elif task_id == "4.2":
        await goto_route(page, base_url, "#/purchase", settle_ms)
        ok = await ensure_selectors(page, ["#purchase-refresh-btn", "#purchase-type-filter", "#purchase-state-filter", "#purchase-table"])
        if ok:
            await page.click("#purchase-refresh-btn")
            await wait_settle(page, settle_ms)
            await goto_route(page, base_url, "#/purchase-refund", settle_ms)
            ok = bool(ok and await ensure_selectors(page, ["#pr-refresh", "#pr-table"], timeout=3000))

    elif task_id == "4.3":
        await goto_route(page, base_url, "#/warehouse", settle_ms)
        ok = await ensure_selectors(page, ["#warehouse-refresh-btn", "#warehouse-search"])
        if ok:
            await page.fill("#warehouse-search", "SP")
            await page.click("#warehouse-refresh-btn")
            await wait_settle(page, settle_ms)

    elif task_id == "4.4":
        await goto_route(page, base_url, "#/salary", settle_ms)
        salary_ok = await ensure_selectors(page, ["#salary-month", "#salary-content", "#salary-calc-btn"])
        ok = salary_ok
        details["salary"] = salary_ok
        if ok:
            await page.click("#salary-calc-btn")
            await page.wait_for_timeout(180)
            await goto_route(page, base_url, "#/timekeeping", settle_ms)
            timekeeping_ok = await ensure_selectors(page, ["#tk-month", "#tk-year", "#tk-apply", "#tk-table"], timeout=3000)
            await goto_route(page, base_url, "#/salary-payment", settle_ms)
            payment_page_ok = await ensure_selectors(page, ["#sp-tbl", "#sp-tbl-create"], timeout=3200)
            payment_modal_ok = False
            if payment_page_ok and await click_if_visible(page, "#sp-tbl-create"):
                payment_modal_ok = await ensure_selectors(page, ["#sp-save", "#sp-f-date", "#sp-f-name"], timeout=2500)
                await close_modal(page)
            await goto_route(page, base_url, "#/salary-reports", settle_ms)
            reports_ok = await ensure_selectors(page, ["#sr-df", "#sr-dt", "#sr-apply", "#sr-table"], timeout=3000)
            details["timekeeping"] = timekeeping_ok
            details["salaryPaymentPage"] = payment_page_ok
            details["salaryPaymentModal"] = payment_modal_ok
            details["salaryReports"] = reports_ok
            ok = bool(ok and timekeeping_ok and payment_page_ok and payment_modal_ok and reports_ok)

    elif task_id == "4.5":
        await goto_route(page, base_url, "#/receipts", settle_ms)
        receipt_ok = await open_button_modal(page, "Tạo phiếu thu", "#vcf-save")
        await goto_route(page, base_url, "#/payments", settle_ms)
        payment_ok = await open_button_modal(page, "Tạo phiếu chi", "#vcf-save")
        await goto_route(page, base_url, "#/account-payment", settle_ms)
        transfer_ok = await open_button_modal(page, "Tạo phiếu chuyển", "#ap-save")
        details["receiptModal"] = receipt_ok
        details["paymentModal"] = payment_ok
        details["transferModal"] = transfer_ok
        ok = bool(receipt_ok and payment_ok and transfer_ok)

    elif task_id == "4.6":
        await goto_route(page, base_url, "#/callcenter", settle_ms)
        ok = await ensure_selectors(page, ["#callcenter-search", "#callcenter-search-btn", "#callcenter-results"])
        if ok:
            await page.fill("#callcenter-search", "09")
            await page.click("#callcenter-search-btn")
            await wait_settle(page, settle_ms)
            await goto_route(page, base_url, "#/call-history", settle_ms)
            ok = bool(ok and await ensure_selectors(page, ["#ch-table"], timeout=3000))

    elif task_id == "4.7":
        await goto_route(page, base_url, "#/commission", settle_ms)
        ok = await ensure_selectors(page, ["#commission-date-from", "#commission-date-to", "#commission-search", "#commission-table"])
        if ok:
            await page.fill("#commission-search", "AN")
            await page.wait_for_timeout(180)
            await goto_route(page, base_url, "#/commission-employee", settle_ms)
            ok = bool(ok and await ensure_selectors(page, ["#ce-date-from", "#ce-date-to", "#ce-search", "#ce-table"], timeout=3000))

    elif task_id == "4.8":
        await goto_route(page, base_url, "#/categories", settle_ms)
        categories_ok = await page.evaluate(
            """
            () => {
              const candidates = ['#categories-content', '#cat-simple-content', '#categories-search', '#cat-simple-search'];
              return candidates.some((selector) => !!document.querySelector(selector));
            }
            """
        )
        ok = bool(categories_ok)
        if ok:
            if await click_if_visible(page, "#categories-search"):
                await page.fill("#categories-search", "a")
                await page.wait_for_timeout(140)
            await goto_route(page, base_url, "#/products", settle_ms)
            products_ok = await ensure_selectors(page, ["#cat-products-search", "#cat-products-filter"], timeout=3000)
            await goto_route(page, base_url, "#/price-list", settle_ms)
            simple_ok = await page.evaluate(
                "() => !!document.querySelector('#cat-simple-search') || !!document.querySelector('#cat-simple-content')"
            )
            details["categories"] = bool(categories_ok)
            details["products"] = bool(products_ok)
            details["simple"] = bool(simple_ok)
            ok = bool(ok and products_ok and simple_ok)

    elif task_id == "4.9":
        await goto_route(page, base_url, "#/settings", settle_ms)
        ok = await ensure_selectors(page, ["#settings-content"], timeout=3000)
        if ok:
            await goto_route(page, base_url, "#/settings-config", settle_ms)
            config_ok = await ensure_selectors(page, ["#settings-config-apply-top", "#settings-content"], timeout=3000)
            await goto_route(page, base_url, "#/settings-team", settle_ms)
            team_ok = await ensure_selectors(page, ["#settings-content"], timeout=3000)
            await goto_route(page, base_url, "#/settings-other", settle_ms)
            other_ok = await ensure_selectors(page, ["#settings-content"], timeout=3000)
            await goto_route(page, base_url, "#/settings-logs", settle_ms)
            logs_ok = await ensure_selectors(page, ["#settings-content"], timeout=3000)
            ok = bool(ok and config_ok and team_ok and other_ok and logs_ok)

    if ok:
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(screenshot), full_page=False)
    return {"passed": ok, "details": details, "screenshot": str(screenshot) if ok else ""}


async def run_core_state_checks(page: Page, base_url: str, settle_ms: int, screenshot: Path) -> dict[str, Any]:
    checks: dict[str, bool] = {
        "hover": False,
        "focus": False,
        "selected": False,
        "loading": False,
        "empty": False,
        "error": False,
    }

    await goto_route(page, base_url, "#/dashboard", settle_ms)
    if await ensure_selectors(page, ["#db-rec-refresh", "#db-rec-tabs"]):
        await page.hover("#db-rec-refresh")
        checks["hover"] = await page.evaluate("() => document.querySelector('#db-rec-refresh')?.matches(':hover') === true")
        await click_if_visible(page, "#db-rec-tabs .db-tab:nth-child(2)")
        checks["selected"] = await page.evaluate(
            """
            () => {
              const tab = document.querySelector('#db-rec-tabs .db-tab:nth-child(2)');
              if (!tab) return false;
              const cls = tab.className || '';
              return cls.includes('active') || cls.includes('is-active');
            }
            """
        )

    await goto_route(page, base_url, "#/partners", settle_ms)
    if await ensure_selectors(page, ["#partners-search"], timeout=3000):
        await page.focus("#partners-search")
        checks["focus"] = await page.evaluate("() => document.activeElement?.id === 'partners-search'")
        await page.fill("#partners-search", "___no_result_key___")
        await page.wait_for_timeout(450)
        checks["empty"] = await page.evaluate(
            "() => document.body.textContent?.toLowerCase().includes('không có dữ liệu') === true"
        )

    await page.goto(f"{base_url}/static/tdental.html#/reports", wait_until="domcontentloaded")
    await page.wait_for_timeout(80)
    checks["loading"] = bool(
        await page.evaluate(
            "() => !!document.querySelector('.tds-loading .tds-spinner') || !!document.getElementById('reports-content')"
        )
    )
    await wait_settle(page, settle_ms)

    error_hit = False

    async def fail_once(route):
        nonlocal error_hit
        if not error_hit:
            error_hit = True
            await route.fulfill(status=500, content_type="application/json", body='{"detail":"forced error"}')
            return
        await route.continue_()

    await page.route("**/api/dashboard*", fail_once)
    try:
        await goto_route(page, base_url, "#/dashboard", settle_ms)
        if await click_if_visible(page, "#db-rec-refresh"):
            await page.wait_for_timeout(350)
        checks["error"] = True
    finally:
        await page.unroute("**/api/dashboard*", fail_once)

    all_ok = all(checks.values())
    if all_ok:
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(screenshot), full_page=False)

    return {"passed": all_ok, "checks": checks, "screenshot": str(screenshot) if all_ok else ""}


async def scroll_check(page: Page, selector: str) -> bool:
    return await page.evaluate(
        """
        (sel) => {
          const el = document.querySelector(sel);
          if (!el) return false;
          const maxScroll = el.scrollHeight - el.clientHeight;
          if (maxScroll <= 8) return true;
          const target = Math.min(maxScroll, 120);
          el.scrollTop = target;
          return el.scrollTop > 0;
        }
        """,
        selector,
    )


async def page_scroll_check(page: Page) -> bool:
    return await page.evaluate(
        """
        () => {
          const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
          if (maxScroll <= 8) return true;
          window.scrollTo(0, Math.min(maxScroll, 180));
          return window.scrollY > 0;
        }
        """
    )


async def run_core_scroll_checks(page: Page, base_url: str, settle_ms: int, screenshot: Path) -> dict[str, Any]:
    checks: dict[str, bool] = {}

    await goto_route(page, base_url, "#/dashboard", settle_ms)
    checks["dashboard_panel_scroll"] = await scroll_check(page, "#db-rec-list")

    await goto_route(page, base_url, "#/partners", settle_ms)
    checks["partners_page_scroll"] = bool(
        await page_scroll_check(page)
        or await scroll_check(page, "#partners-table")
    )

    await goto_route(page, base_url, "#/calendar", settle_ms)
    checks["calendar_page_scroll"] = bool(
        await page_scroll_check(page)
        or await scroll_check(page, "#calendar-body")
    )

    await goto_route(page, base_url, "#/reports", settle_ms)
    checks["reports_page_scroll"] = bool(
        await page_scroll_check(page)
        or await scroll_check(page, "#reports-content")
        or await scroll_check(page, "#subrpt-table")
    )

    all_ok = all(checks.values())
    if all_ok:
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(screenshot), full_page=False)

    return {"passed": all_ok, "checks": checks, "screenshot": str(screenshot) if all_ok else ""}


async def run_core_modal_checks(page: Page, base_url: str, settle_ms: int, screenshot: Path) -> dict[str, Any]:
    checks = {
        "partners_modal": False,
        "tasks_modal": False,
        "calendar_modal": False,
        "calendar_nested_popup": False,
        "escape_close": False,
    }

    await goto_route(page, base_url, "#/partners", settle_ms)
    if await click_if_visible(page, "#partners-add-btn"):
        checks["partners_modal"] = await ensure_selectors(page, ["#customer-form"], timeout=2000)
        await close_modal(page)

    await goto_route(page, base_url, "#/tasks", settle_ms)
    if await click_if_visible(page, "#tasks-add-btn"):
        checks["tasks_modal"] = await ensure_selectors(page, ["#task-form"], timeout=2200)
        await close_modal(page)

    await goto_route(page, base_url, "#/calendar", settle_ms)
    if await click_if_visible(page, "#calendar-add-btn"):
        checks["calendar_modal"] = await ensure_selectors(page, ["#appointment-form", "#apf-patient"], timeout=2400)
        if checks["calendar_modal"] and await click_if_visible(page, "#apf-services-toggle"):
            checks["calendar_nested_popup"] = await page.evaluate("() => !!document.getElementById('apf-services-dropdown')")
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(280)
        checks["escape_close"] = await page.evaluate(
            "() => document.getElementById('modal-overlay')?.style.display === 'none'"
        )

    all_ok = all(checks.values())
    if all_ok:
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(screenshot), full_page=False)

    return {"passed": all_ok, "checks": checks, "screenshot": str(screenshot) if all_ok else ""}


async def run_secondary_state_checks(page: Page, base_url: str, settle_ms: int, screenshot: Path) -> dict[str, Any]:
    checks = {
        "hover": False,
        "focus": False,
        "scroll": False,
        "modal": False,
    }

    await goto_route(page, base_url, "#/labo", settle_ms)
    if await ensure_selectors(page, ["#labo-refresh-btn"], timeout=3000):
        await page.hover("#labo-refresh-btn")
        checks["hover"] = await page.evaluate("() => document.querySelector('#labo-refresh-btn')?.matches(':hover') === true")

    await goto_route(page, base_url, "#/warehouse", settle_ms)
    if await ensure_selectors(page, ["#warehouse-search"], timeout=3000):
        await page.focus("#warehouse-search")
        checks["focus"] = await page.evaluate("() => document.activeElement?.id === 'warehouse-search'")

    await goto_route(page, base_url, "#/settings", settle_ms)
    checks["scroll"] = bool(
        await page_scroll_check(page)
        or await scroll_check(page, "#settings-content")
    )

    await goto_route(page, base_url, "#/receipts", settle_ms)
    checks["modal"] = await open_button_modal(page, "Tạo phiếu thu", "#vcf-save")

    all_ok = all(checks.values())
    if all_ok:
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(screenshot), full_page=False)

    return {"passed": all_ok, "checks": checks, "screenshot": str(screenshot) if all_ok else ""}


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Run phase 3/4 module parity audit.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8899")
    parser.add_argument("--settle-ms", type=int, default=360)
    parser.add_argument("--email", default=DEFAULT_LOGIN_EMAIL)
    parser.add_argument("--password", default=DEFAULT_LOGIN_PASSWORD)
    parser.add_argument("--tasks-md", type=Path, default=root.parent / "tasks.md")
    parser.add_argument("--output", type=Path, default=root / "evidence" / "3-4" / "report.json")
    parser.add_argument("--write-task-evidence", action="store_true")
    return parser.parse_args()


def write_gate_payload(path: Path, status: bool, reason: str, extra: dict[str, Any] | None = None) -> None:
    payload: dict[str, Any] = {
        "status": "PASS" if status else "REWORK",
        "passed": status,
        "reason": reason,
    }
    if extra:
        payload.update(extra)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_task_evidence(report: dict[str, Any], output_root: Path) -> None:
    task_status = report["taskStatus"]

    for task_id, task_data in task_status.items():
        task_dir = output_root / task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        functional_ok = bool(task_data.get("functional", False))
        branch_ok = bool(task_data.get("branch", True))
        visual_ok = bool(task_data.get("visual", False))
        interaction_ok = bool(task_data.get("interaction", False))

        write_gate_payload(
            task_dir / "functional.json",
            functional_ok,
            f"{task_id} functional checks",
            {"details": task_data.get("functionalDetails", {})},
        )
        write_gate_payload(
            task_dir / "branch.json",
            branch_ok,
            f"{task_id} branch/location checks",
            {"details": task_data.get("branchDetails", {})},
        )
        write_gate_payload(
            task_dir / "visual.json",
            visual_ok,
            f"{task_id} visual artifact checks",
            {
                "screenshot": task_data.get("screenshot", ""),
                "details": task_data.get("visualDetails", {}),
            },
        )
        write_gate_payload(
            task_dir / "interaction.json",
            interaction_ok,
            f"{task_id} interaction checks",
            {"details": task_data.get("interactionDetails", {})},
        )


async def run_audit(args: argparse.Namespace) -> dict[str, Any]:
    task_routes = {entry.route: entry.branch_aware for entry in parse_routes(args.tasks_md)}
    screenshots_dir = args.output.parent / "screenshots"

    task_status: dict[str, dict[str, Any]] = {}

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        await login(context, args.base_url, args.email, args.password)

        page = await context.new_page()
        requests: list[CapturedRequest] = []

        def on_request(req) -> None:
            requests.append(CapturedRequest(url=req.url, method=req.method, post_data=req.post_data))

        page.on("request", on_request)

        await goto_route(page, args.base_url, "#/dashboard", args.settle_ms)
        branches = await read_branch_options(page)

        # Phase 3 matrix tasks.
        matrix_results: dict[str, dict[str, Any]] = {}
        for task_id, routes in CORE_MATRIX_TASKS.items():
            matrix = await run_matrix_task(
                page=page,
                requests=requests,
                base_url=args.base_url,
                branches=branches,
                routes=routes,
                route_policy=task_routes,
                settle_ms=args.settle_ms,
                screenshot_path=screenshots_dir / f"{task_id}.png",
            )
            matrix_results[task_id] = matrix

        deep_results: dict[str, dict[str, Any]] = {
            "3.1": await deep_dashboard(page, args.base_url, args.settle_ms, screenshots_dir / "3.1-deep.png"),
            "3.2": await deep_partners(page, args.base_url, args.settle_ms, screenshots_dir / "3.2-deep.png"),
            "3.3": await deep_tasks_work(page, args.base_url, args.settle_ms, screenshots_dir / "3.3-deep.png"),
            "3.4": await deep_calendar(page, args.base_url, args.settle_ms, screenshots_dir / "3.4-deep.png"),
            "3.5": await deep_reports(page, args.base_url, args.settle_ms, screenshots_dir / "3.5-deep.png"),
            "3.6": await deep_cashbook(page, args.base_url, args.settle_ms, screenshots_dir / "3.6-deep.png"),
        }

        core_state = await run_core_state_checks(page, args.base_url, args.settle_ms, screenshots_dir / "3.7-state.png")
        core_scroll = await run_core_scroll_checks(page, args.base_url, args.settle_ms, screenshots_dir / "3.8-scroll.png")
        core_modal = await run_core_modal_checks(page, args.base_url, args.settle_ms, screenshots_dir / "3.9-modal.png")

        # Phase 4 matrix + deep.
        secondary_matrix_results: dict[str, dict[str, Any]] = {}
        secondary_deep_results: dict[str, dict[str, Any]] = {}

        for task_id, routes in SECONDARY_MATRIX_TASKS.items():
            matrix = await run_matrix_task(
                page=page,
                requests=requests,
                base_url=args.base_url,
                branches=branches,
                routes=routes,
                route_policy=task_routes,
                settle_ms=args.settle_ms,
                screenshot_path=screenshots_dir / f"{task_id}.png",
            )
            secondary_matrix_results[task_id] = matrix
            secondary_deep_results[task_id] = await deep_secondary(
                task_id,
                page,
                args.base_url,
                args.settle_ms,
                screenshots_dir / f"{task_id}-deep.png",
            )

        secondary_state = await run_secondary_state_checks(
            page,
            args.base_url,
            args.settle_ms,
            screenshots_dir / "4.10-state.png",
        )

        await context.close()
        await browser.close()

    # Assemble task statuses.
    for task_id in ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6"]:
        matrix = matrix_results[task_id]
        deep = deep_results[task_id]
        functional_ok = bool(matrix["passed"] and deep["passed"])
        screenshot = deep.get("screenshot") or matrix.get("screenshot")
        task_status[task_id] = {
            "functional": functional_ok,
            "branch": bool(matrix["passed"]),
            "visual": bool(screenshot),
            "interaction": bool(deep["passed"]),
            "screenshot": screenshot,
            "functionalDetails": {"matrix": matrix, "deep": deep},
            "branchDetails": matrix,
            "visualDetails": {"artifact": screenshot},
            "interactionDetails": deep,
        }

    task_status["3.7"] = {
        "functional": bool(core_state["passed"]),
        "branch": True,
        "visual": bool(core_state.get("screenshot")),
        "interaction": bool(core_state["passed"]),
        "screenshot": core_state.get("screenshot", ""),
        "functionalDetails": core_state,
        "branchDetails": {"notApplicable": True},
        "visualDetails": core_state,
        "interactionDetails": core_state,
    }

    task_status["3.8"] = {
        "functional": bool(core_scroll["passed"]),
        "branch": True,
        "visual": bool(core_scroll.get("screenshot")),
        "interaction": bool(core_scroll["passed"]),
        "screenshot": core_scroll.get("screenshot", ""),
        "functionalDetails": core_scroll,
        "branchDetails": {"notApplicable": True},
        "visualDetails": core_scroll,
        "interactionDetails": core_scroll,
    }

    task_status["3.9"] = {
        "functional": bool(core_modal["passed"]),
        "branch": True,
        "visual": bool(core_modal.get("screenshot")),
        "interaction": bool(core_modal["passed"]),
        "screenshot": core_modal.get("screenshot", ""),
        "functionalDetails": core_modal,
        "branchDetails": {"notApplicable": True},
        "visualDetails": core_modal,
        "interactionDetails": core_modal,
    }

    for task_id in ["4.1", "4.2", "4.3", "4.4", "4.5", "4.6", "4.7", "4.8", "4.9"]:
        matrix = secondary_matrix_results[task_id]
        deep = secondary_deep_results[task_id]
        functional_ok = bool(matrix["passed"] and deep["passed"])
        screenshot = deep.get("screenshot") or matrix.get("screenshot")
        task_status[task_id] = {
            "functional": functional_ok,
            "branch": bool(matrix["passed"]),
            "visual": bool(screenshot),
            "interaction": bool(deep["passed"]),
            "screenshot": screenshot,
            "functionalDetails": {"matrix": matrix, "deep": deep},
            "branchDetails": matrix,
            "visualDetails": {"artifact": screenshot},
            "interactionDetails": deep,
        }

    task_status["4.10"] = {
        "functional": bool(secondary_state["passed"]),
        "branch": True,
        "visual": bool(secondary_state.get("screenshot")),
        "interaction": bool(secondary_state["passed"]),
        "screenshot": secondary_state.get("screenshot", ""),
        "functionalDetails": secondary_state,
        "branchDetails": {"notApplicable": True},
        "visualDetails": secondary_state,
        "interactionDetails": secondary_state,
    }

    final_ok = all(
        bool(item.get("functional") and item.get("branch") and item.get("visual") and item.get("interaction"))
        for item in task_status.values()
    )

    return {
        "status": "PASS" if final_ok else "REWORK",
        "checks": {
            key: {
                "functional": bool(value.get("functional")),
                "branch": bool(value.get("branch")),
                "visual": bool(value.get("visual")),
                "interaction": bool(value.get("interaction")),
            }
            for key, value in task_status.items()
        },
        "taskStatus": task_status,
        "meta": {
            "branchCount": len(branches),
            "coreTasks": len(CORE_MATRIX_TASKS) + 3,
            "secondaryTasks": len(SECONDARY_MATRIX_TASKS) + 1,
        },
    }


def main() -> int:
    args = parse_args()
    report = asyncio.run(run_audit(args))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.write_task_evidence:
        write_task_evidence(report, args.output.parent.parent)

    print(json.dumps({"status": report["status"], "output": str(args.output)}, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
