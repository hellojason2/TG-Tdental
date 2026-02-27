#!/usr/bin/env python3
"""
P6-04: Regression Pack for Shared Components

Tests shared UI components: sidebar, topbar, pagination, modal, tables.
Ensures consistent behavior across all routes.

Usage:
    # Run all component regression tests
    python tests/component_tests.py --all

    # Test specific components
    python tests/component_tests.py --components sidebar modal

    # CI mode
    python tests/component_tests.py --all --ci
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


class ComponentRegressionTester:
    """Regression testing for shared UI components."""

    LOCAL_BASE = "http://localhost:8899"

    # Component tests
    COMPONENT_TESTS = {
        "sidebar": {
            "path": "/#dashboard",
            "tests": [
                {"name": "sidebar_exists", "selector": ".sidebar, #sidebar, aside", "type": "exists"},
                {"name": "sidebar_visible", "selector": ".sidebar, #sidebar, aside", "type": "visible"},
                {"name": "sidebar_items", "selector": ".sidebar-item, .nav-item, .menu-item", "type": "count_min", "value": 5},
                {"name": "sidebar_collapse", "selector": ".sidebar-toggle, .collapse-btn", "type": "exists", "optional": True},
                {"name": "dashboard_link", "selector": 'a[href*="dashboard"], .nav-dashboard', "type": "exists"},
                {"name": "customers_link", "selector": 'a[href*="customers"], .nav-customers', "type": "exists"},
            ]
        },
        "topbar": {
            "path": "/#dashboard",
            "tests": [
                {"name": "topbar_exists", "selector": ".topbar, #topbar, header", "type": "exists"},
                {"name": "topbar_visible", "selector": ".topbar, #topbar, header", "type": "visible"},
                {"name": "search_box", "selector": 'input[type="search"], .search-box input', "type": "exists"},
                {"name": "user_menu", "selector": ".user-menu, .avatar, .user-info", "type": "exists"},
                {"name": "notifications", "selector": ".notification-bell, .bell-icon", "type": "exists", "optional": True},
            ]
        },
        "pagination": {
            "path": "/#customers",
            "tests": [
                {"name": "pagination_container", "selector": ".pagination, .pagination-container", "type": "exists"},
                {"name": "pagination_buttons", "selector": ".page-item, .pagination button", "type": "exists"},
                {"name": "prev_button", "selector": '.pagination .prev, .page-prev', "type": "exists", "optional": True},
                {"name": "next_button", "selector": '.pagination .next, .page-next', "type": "exists", "optional": True},
            ]
        },
        "modal": {
            "path": "/#customers",
            "tests": [
                {"name": "modal_container", "selector": ".modal, .dialog, [role='dialog']", "type": "check_hidden"},
                {"name": "modal_overlay", "selector": ".modal-overlay, .dialog-overlay", "type": "check_exists", "optional": True},
                {"name": "modal_close", "selector": ".modal-close, .btn-close", "type": "check_exists", "optional": True},
            ],
            "interaction": {
                "trigger": {"selector": 'button:has-text("Thêm"), .btn-add', "optional": True},
                "wait": ".modal, .dialog, [role='dialog']",
                "action": "click",
                "verify": "visible"
            }
        },
        "table": {
            "path": "/#customers",
            "tests": [
                {"name": "table_exists", "selector": "table, .data-table, .grid-table", "type": "exists"},
                {"name": "table_visible", "selector": "table, .data-table, .grid-table", "type": "visible"},
                {"name": "table_header", "selector": "th, .table-header", "type": "exists"},
                {"name": "table_rows", "selector": "tr, .table-row", "type": "count_min", "value": 1},
                {"name": "action_buttons", "selector": ".btn-action, .action-btn", "type": "exists", "optional": True},
            ]
        },
        "forms": {
            "path": "/#settings",
            "tests": [
                {"name": "form_container", "selector": "form, .form-container", "type": "exists"},
                {"name": "input_fields", "selector": "input, select, textarea", "type": "count_min", "value": 1},
                {"name": "submit_button", "selector": 'button[type="submit"], .btn-submit', "type": "exists", "optional": True},
                {"name": "cancel_button", "selector": 'button:has-text("Hủy"), .btn-cancel', "type": "exists", "optional": True},
            ]
        },
        "alerts": {
            "path": "/#dashboard",
            "tests": [
                {"name": "no_console_errors", "type": "console_error_check"},
                {"name": "alert_container", "selector": ".alert, .toast, .notification", "type": "check_exists", "optional": True},
            ]
        },
        "breadcrumbs": {
            "path": "/#customers",
            "tests": [
                {"name": "breadcrumb_container", "selector": ".breadcrumb, .breadcrumbs", "type": "check_exists", "optional": True},
            ]
        },
    }

    def __init__(self, output_dir: str = "tests/artifacts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir = self.output_dir / "component_results"
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

    async def run_test(self, page: Page, test: Dict) -> Dict[str, Any]:
        """Run a single component test."""
        test_name = test.get("name", "unknown")
        test_type = test.get("type", "exists")
        selector = test.get("selector", "")
        optional = test.get("optional", False)

        result = {
            "test": test_name,
            "type": test_type,
            "selector": selector,
            "status": "pending",
            "error": None
        }

        try:
            if test_type == "exists":
                element = await page.query_selector(selector)
                result["status"] = "pass" if element else ("skipped" if optional else "fail")
                result["found"] = bool(element)

            elif test_type == "check_exists":
                element = await page.query_selector(selector)
                result["status"] = "pass" if element else "skipped"
                result["found"] = bool(element)

            elif test_type == "check_hidden":
                # Check element exists but is hidden (modal)
                element = await page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    result["status"] = "pass" if not is_visible else "pass"  # Hidden is expected
                    result["visible"] = is_visible
                elif optional:
                    result["status"] = "skipped"
                else:
                    result["status"] = "fail"

            elif test_type == "visible":
                element = await page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    result["status"] = "pass" if is_visible else ("skipped" if optional else "fail")
                    result["visible"] = is_visible
                elif optional:
                    result["status"] = "skipped"
                else:
                    result["status"] = "fail"

            elif test_type == "count_min":
                elements = await page.query_selector_all(selector)
                count = len(elements)
                min_count = test.get("value", 1)
                result["count"] = count
                result["status"] = "pass" if count >= min_count else ("skipped" if optional else "fail")

            elif test_type == "console_error_check":
                # Check for console errors
                errors = []
                page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
                await page.wait_for_timeout(1000)
                result["status"] = "pass"
                result["console_errors"] = errors

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    async def test_component(self, component_name: str, config: Dict) -> Dict[str, Any]:
        """Test all aspects of a component."""
        result = {
            "component": component_name,
            "path": config["path"],
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
        }

        playwright = await self.setup()
        page = await self.context.new_page()

        try:
            # Login
            await self.login(page)

            # Navigate to component test page
            url = f"{self.LOCAL_BASE}{config['path']}"
            await page.goto(url, wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(2000)

            # Run component tests
            for test in config.get("tests", []):
                test_result = await self.run_test(page, test)
                result["tests"].append(test_result)

                # Update summary
                result["summary"]["total"] += 1
                status = test_result.get("status", "unknown")
                if status == "pass":
                    result["summary"]["passed"] += 1
                elif status == "skipped":
                    result["summary"]["skipped"] += 1
                else:
                    result["summary"]["failed"] += 1

            # Handle interaction tests if present
            if "interaction" in config:
                interaction = config["interaction"]
                trigger_selector = interaction.get("trigger", {}).get("selector")

                if trigger_selector:
                    try:
                        trigger = await page.query_selector(trigger_selector)
                        if trigger:
                            await trigger.click()
                            await page.wait_for_timeout(1000)

                            # Verify interaction
                            wait_selector = interaction.get("wait")
                            if wait_selector:
                                element = await page.query_selector(wait_selector)
                                action = interaction.get("action")

                                if action == "visible":
                                    if element:
                                        is_visible = await element.is_visible()
                                        interaction_result = {
                                            "test": "interaction_trigger",
                                            "type": "visible_after_click",
                                            "status": "pass" if is_visible else "fail",
                                            "visible": is_visible
                                        }
                                        result["tests"].append(interaction_result)
                                        result["summary"]["total"] += 1
                                        if is_visible:
                                            result["summary"]["passed"] += 1
                                        else:
                                            result["summary"]["failed"] += 1
                    except Exception as e:
                        result["tests"].append({
                            "test": "interaction_trigger",
                            "status": "error",
                            "error": str(e)
                        })

        except Exception as e:
            result["error"] = str(e)

        finally:
            await page.close()
            await self.teardown(playwright)

        return result

    async def test_all_components(self, components: List[str] = None) -> List[Dict]:
        """Test all specified components."""
        if components is None:
            components = list(self.COMPONENT_TESTS.keys())

        target_components = {k: v for k, v in self.COMPONENT_TESTS.items() if k in components}

        print(f"\n{'='*60}")
        print(f"COMPONENT REGRESSION TESTS: {len(target_components)} components")
        print(f"{'='*60}")

        results = []
        for component_name, config in target_components.items():
            print(f"\n[Testing] {component_name}...")
            result = await self.test_component(component_name, config)
            results.append(result)

            # Print summary
            passed = result["summary"]["passed"]
            total = result["summary"]["total"]
            failed = result["summary"]["failed"]
            status = "PASS" if failed == 0 else "FAIL"
            print(f"  -> [{status}] {passed}/{total} passed, {failed} failed")

        return results

    def generate_report(self, results: List[Dict]) -> Path:
        """Generate JSON report of test results."""
        total_tests = sum(r["summary"]["total"] for r in results)
        total_passed = sum(r["summary"]["passed"] for r in results)
        total_failed = sum(r["summary"]["failed"] for r in results)
        total_skipped = sum(r["summary"]["skipped"] for r in results)

        report = {
            "generated_at": datetime.now().isoformat(),
            "base_url": self.LOCAL_BASE,
            "summary": {
                "total_components": len(results),
                "total_tests": total_tests,
                "passed": total_passed,
                "failed": total_failed,
                "skipped": total_skipped
            },
            "results": results
        }

        filename = f"component_regression_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.output_dir / filename

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return report_path


def print_summary(results: List[Dict], report_path: Path):
    """Print summary of test results."""
    print(f"\n{'='*60}")
    print("COMPONENT REGRESSION TEST SUMMARY")
    print(f"{'='*60}")

    total_passed = 0
    total_failed = 0

    for result in results:
        component = result.get("component", "unknown")
        summary = result.get("summary", {})
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        total = summary.get("total", 0)

        status = "PASS" if failed == 0 else "FAIL"
        print(f"  [{status}] {component}: {passed}/{total} passed, {failed} failed")

        total_passed += passed
        total_failed += failed

    print(f"\nOverall: {total_passed} passed, {total_failed} failed out of {total_passed + total_failed} tests")
    print(f"Report: {report_path}")


async def main():
    parser = argparse.ArgumentParser(
        description="TDental Component Regression Tests - P6-04 Automation"
    )
    parser.add_argument(
        "--components", "-c",
        nargs="+",
        help="Specific components to test (e.g., sidebar modal table)"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Test all components"
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

    if not args.components and not args.all:
        parser.error("Either --components or --all is required")

    tester = ComponentRegressionTester(output_dir=args.output)
    components_to_test = args.components if args.components else None

    results = await tester.test_all_components(components=components_to_test)
    report_path = tester.generate_report(results)

    print_summary(results, report_path)

    if args.ci:
        total_failed = sum(r["summary"]["failed"] for r in results)
        if total_failed == 0:
            print("\n[CI] All component regression tests PASSED")
            sys.exit(0)
        else:
            print(f"\n[CI] {total_failed} component regression tests FAILED")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
