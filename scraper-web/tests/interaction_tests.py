#!/usr/bin/env python3
"""
P6-02: Automated Interaction Checks Per Route

Tests user interactions on each route: filter, paginate, open modal, submit/cancel.
Provides regression testing for UI interactions.

Usage:
    # Run all interaction tests
    python tests/interaction_tests.py --all

    # Test specific routes
    python tests/interaction_tests.py --routes customers calendar

    # CI mode
    python tests/interaction_tests.py --all --ci
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from playwright.async_api import async_playwright, Browser, Page
except ImportError:
    print("ERROR: playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)


class InteractionTester:
    """Automated interaction testing for TDental routes."""

    LOCAL_BASE = "http://localhost:8899"

    # Route configurations with their interaction tests
    ROUTE_CONFIGS = {
        "login": {
            "path": "/login",
            "interactions": [
                {"name": "login_form_present", "type": "check", "selector": "form"},
                {"name": "email_input", "type": "fill", "selector": '#loginEmail, input[type="email"]', "value": "admin@tdental.vn"},
                {"name": "password_input", "type": "fill", "selector": 'input[type="password"]', "value": "admin123"},
                {"name": "submit_button", "type": "click", "selector": 'button[type="submit"]'},
                {"name": "login_success", "type": "wait_url", "value": "/#dashboard", "timeout": 10000}
            ]
        },
        "dashboard": {
            "path": "/#dashboard",
            "interactions": [
                {"name": "page_load", "type": "wait_selector", "selector": ".sidebar, .dashboard"},
                {"name": "tab_switch", "type": "click", "selector": ".tab-item, .nav-item", "optional": True},
            ]
        },
        "customers": {
            "path": "/#customers",
            "interactions": [
                {"name": "page_load", "type": "wait_selector", "selector": ".toolbar, table, .customer-list"},
                {"name": "search_input", "type": "fill", "selector": 'input[placeholder*="Tìm"], input.search', "value": "test"},
                {"name": "search_trigger", "type": "click", "selector": 'button:has-text("Tìm"), .search-btn', "optional": True},
                {"name": "search_results", "type": "wait_timeout", "value": 1000},
                {"name": "clear_search", "type": "clear", "selector": 'input[placeholder*="Tìm"], input.search', "optional": True},
                {"name": "pagination", "type": "click", "selector": '.pagination .page-item:not(.disabled) a, .pagination button:not([disabled])', "optional": True},
                {"name": "add_customer_btn", "type": "click", "selector": 'button:has-text("Thêm"), .btn-add', "optional": True},
            ]
        },
        "calendar": {
            "path": "/#calendar",
            "interactions": [
                {"name": "page_load", "type": "wait_selector", "selector": ".calendar, .fc-view, .date-picker"},
                {"name": "date_navigation", "type": "click", "selector": '.btn-next, .btn-prev, .fc-next-button, .fc-prev-button', "optional": True},
                {"name": "view_toggle", "type": "click", "selector": '.fc-agendaWeek-button, .fc-agendaDay-button, .view-btn', "optional": True},
            ]
        },
        "reception": {
            "path": "/#reception",
            "interactions": [
                {"name": "page_load", "type": "wait_selector", "selector": ".queue-list, .reception-board, table"},
                {"name": "refresh_button", "type": "click", "selector": 'button:has-text("Làm mới"), .btn-refresh', "optional": True},
            ]
        },
        "treatments": {
            "path": "/#treatments",
            "interactions": [
                {"name": "page_load", "type": "wait_selector", "selector": "table, .treatment-list"},
                {"name": "filter_status", "type": "click", "selector": '.status-filter button, .filter-item', "optional": True},
            ]
        },
        "purchase": {
            "path": "/#purchase",
            "interactions": [
                {"name": "page_load", "type": "wait_selector", "selector": "table, .purchase-list"},
            ]
        },
        "inventory": {
            "path": "/#inventory",
            "interactions": [
                {"name": "page_load", "type": "wait_selector", "selector": "table, .inventory-list, .stock-summary"},
            ]
        },
        "reports": {
            "path": "/#reports",
            "interactions": [
                {"name": "page_load", "type": "wait_selector", "selector": ".report-container, .chart-area"},
                {"name": "date_filter", "type": "click", "selector": '.date-picker input, .filter-date', "optional": True},
            ]
        },
        "settings": {
            "path": "/#settings",
            "interactions": [
                {"name": "page_load", "type": "wait_selector", "selector": ".settings-form, .settings-panel"},
                {"name": "save_button", "type": "click", "selector": 'button:has-text("Lưu"), button:has-text("Áp dụng")', "optional": True},
            ]
        }
    }

    def __init__(self, output_dir: str = "tests/artifacts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir = self.output_dir / "interaction_results"
        self.results_dir.mkdir(exist_ok=True)
        self.browser: Optional[Browser] = None

    async def setup(self):
        """Initialize browser."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="vi-VN"
        )
        return playwright

    async def teardown(self, playwright):
        """Cleanup browser resources."""
        if self.browser:
            await self.browser.close()
        if playwright:
            await playwright.stop()

    async def login(self, page: Page) -> bool:
        """Login to the application."""
        try:
            await page.goto(f"{self.LOCAL_BASE}/login", wait_until="networkidle")
            await page.fill('#loginEmail', "admin@tdental.vn")
            await page.fill('input[type="password"]', "admin123")
            await page.click('button[type="submit"]')
            await page.wait_for_load_state("networkidle", timeout=10000)
            return True
        except Exception as e:
            print(f"    [WARN] Login failed: {e}")
            return False

    async def run_interaction(self, page: Page, interaction: Dict) -> Dict[str, Any]:
        """Run a single interaction test."""
        name = interaction.get("name", "unknown")
        i_type = interaction.get("type", "check")
        selector = interaction.get("selector", "")
        optional = interaction.get("optional", False)

        result = {
            "interaction": name,
            "type": i_type,
            "status": "pending",
            "error": None,
            "details": {}
        }

        try:
            if i_type == "check":
                # Just check if element exists
                if selector:
                    element = await page.query_selector(selector)
                    result["status"] = "pass" if element else "fail"
                    result["details"]["found"] = bool(element)

            elif i_type == "wait_selector":
                # Wait for element to appear
                if selector:
                    await page.wait_for_selector(selector, timeout=5000)
                    result["status"] = "pass"

            elif i_type == "wait_timeout":
                # Just wait
                await page.wait_for_timeout(interaction.get("value", 1000))
                result["status"] = "pass"

            elif i_type == "fill":
                # Fill input field
                if selector:
                    element = await page.query_selector(selector)
                    if element:
                        await element.fill(interaction.get("value", ""))
                        result["status"] = "pass"
                    elif optional:
                        result["status"] = "skipped"
                        result["details"]["reason"] = "element not found (optional)"
                    else:
                        result["status"] = "fail"

            elif i_type == "clear":
                # Clear input field
                if selector:
                    element = await page.query_selector(selector)
                    if element:
                        await element.fill("")
                        result["status"] = "pass"
                    elif optional:
                        result["status"] = "skipped"
                    else:
                        result["status"] = "fail"

            elif i_type == "click":
                # Click element
                if selector:
                    element = await page.query_selector(selector)
                    if element:
                        await element.click()
                        result["status"] = "pass"
                    elif optional:
                        result["status"] = "skipped"
                        result["details"]["reason"] = "element not found (optional)"
                    else:
                        result["status"] = "fail"

            elif i_type == "wait_url":
                # Wait for URL to contain value
                expected = interaction.get("value", "")
                await page.wait_for_url(f"**/{expected}", timeout=interaction.get("timeout", 5000))
                result["status"] = "pass"
                result["details"]["url"] = page.url

        except asyncio.TimeoutError:
            result["status"] = "timeout"
            result["error"] = f"Timeout waiting for {selector}"
        except Exception as e:
            if optional and "not found" in str(e).lower():
                result["status"] = "skipped"
                result["details"]["reason"] = "element not found (optional)"
            else:
                result["status"] = "error"
                result["error"] = str(e)

        return result

    async def test_route(self, route_key: str, config: Dict) -> Dict[str, Any]:
        """Test all interactions for a specific route."""
        result = {
            "route": route_key,
            "path": config["path"],
            "timestamp": datetime.now().isoformat(),
            "interactions": [],
            "summary": {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
        }

        playwright = await self.setup()
        page = await self.context.new_page()

        try:
            # Login first for routes requiring auth
            await self.login(page)

            # Navigate to route
            url = f"{self.LOCAL_BASE}{config['path']}"
            await page.goto(url, wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(2000)

            # Run each interaction
            for interaction in config.get("interactions", []):
                interaction_result = await self.run_interaction(page, interaction)
                result["interactions"].append(interaction_result)

                # Update summary
                result["summary"]["total"] += 1
                status = interaction_result.get("status", "unknown")
                if status == "pass":
                    result["summary"]["passed"] += 1
                elif status == "skipped":
                    result["summary"]["skipped"] += 1
                else:
                    result["summary"]["failed"] += 1

        except Exception as e:
            result["error"] = str(e)

        finally:
            await page.close()
            await self.teardown(playwright)

        return result

    async def test_all_routes(self, routes: List[str] = None) -> List[Dict]:
        """Test all configured routes."""
        if routes is None:
            routes = list(self.ROUTE_CONFIGS.keys())

        target_routes = {k: v for k, v in self.ROUTE_CONFIGS.items() if k in routes}

        print(f"\n{'='*60}")
        print(f"INTERACTION TESTS: {len(target_routes)} routes")
        print(f"{'='*60}")

        results = []
        for route_key, config in target_routes.items():
            print(f"\n[Testing] {route_key}...")
            result = await self.test_route(route_key, config)
            results.append(result)

            # Print route summary
            passed = result["summary"]["passed"]
            total = result["summary"]["total"]
            failed = result["summary"]["failed"]
            print(f"  -> Results: {passed}/{total} passed, {failed} failed")

        return results

    def generate_report(self, results: List[Dict]) -> Path:
        """Generate JSON report of test results."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_routes": len(results),
            "total_interactions": sum(r["summary"]["total"] for r in results),
            "total_passed": sum(r["summary"]["passed"] for r in results),
            "total_failed": sum(r["summary"]["failed"] for r in results),
            "total_skipped": sum(r["summary"]["skipped"] for r in results),
            "results": results
        }

        filename = f"interaction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.output_dir / filename

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return report_path


def print_summary(results: List[Dict], report_path: Path):
    """Print summary of test results."""
    print(f"\n{'='*60}")
    print("INTERACTION TEST SUMMARY")
    print(f"{'='*60}")

    total_passed = 0
    total_failed = 0

    for result in results:
        route = result.get("route", "unknown")
        summary = result.get("summary", {})
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        total = summary.get("total", 0)

        status = "PASS" if failed == 0 else "FAIL"
        print(f"  [{status}] {route}: {passed}/{total} passed, {failed} failed")

        total_passed += passed
        total_failed += failed

    print(f"\nOverall: {total_passed} passed, {total_failed} failed out of {total_passed + total_failed} tests")
    print(f"Report: {report_path}")


async def main():
    parser = argparse.ArgumentParser(
        description="TDental Interaction Tests - P6-02 Automation"
    )
    parser.add_argument(
        "--routes", "-r",
        nargs="+",
        help="Specific routes to test (e.g., customers calendar)"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Test all configured routes"
    )
    parser.add_argument(
        "--output", "-o",
        default="tests/artifacts",
        help="Output directory for test results"
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: exit with code based on pass/fail"
    )

    args = parser.parse_args()

    if not args.routes and not args.all:
        parser.error("Either --routes or --all is required")

    tester = InteractionTester(output_dir=args.output)
    routes_to_test = args.routes if args.routes else None

    results = await tester.test_all_routes(routes=routes_to_test)
    report_path = tester.generate_report(results)

    print_summary(results, report_path)

    if args.ci:
        total_failed = sum(r["summary"]["failed"] for r in results)
        if total_failed == 0:
            print("\n[CI] All interaction tests PASSED")
            sys.exit(0)
        else:
            print(f"\n[CI] {total_failed} interaction tests FAILED")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
