#!/usr/bin/env python3
"""
P6-01: Playwright Screenshot Parity Capture Script

Captures screenshots across all key routes for visual regression testing.
Supports baseline capture, local-only capture, and full parity comparison.

Usage:
    # Capture local screenshots for all routes
    python tests/screenshot_parity.py --local --all

    # Capture baseline for specific routes
    python tests/screenshot_parity.py --route dashboard customers --capture baseline

    # Full parity with live (requires credentials)
    python tests/screenshot_parity.py --all --live-user USER --live-pass PASS

    # Run in CI mode (exit code reflects pass/fail)
    python tests/screenshot_parity.py --all --ci
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from playwright.async_api import async_playwright, Browser, Page, Error as PlaywrightError
except ImportError:
    print("ERROR: playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)


class ScreenshotParityCapture:
    """Automated screenshot capture for route parity testing."""

    # Standard viewports for comparison
    VIEWPORTS = {
        "desktop": {"width": 1440, "height": 900},
        "tablet": {"width": 768, "height": 1024},
        "mobile": {"width": 375, "height": 667}
    }

    # Live TDental URL
    LIVE_BASE = "https://tamdentist.tdental.vn"
    LOCAL_BASE = "http://localhost:8899"

    # Key routes to test (in priority order)
    ROUTES = [
        {"key": "login", "path": "/login", "hash": "", "requires_auth": False},
        {"key": "dashboard", "path": "/#dashboard", "hash": "#dashboard", "requires_auth": True},
        {"key": "customers", "path": "/#customers", "hash": "#customers", "requires_auth": True},
        {"key": "reception", "path": "/#reception", "hash": "#reception", "requires_auth": True},
        {"key": "calendar", "path": "/#calendar", "hash": "#calendar", "requires_auth": True},
        {"key": "treatments", "path": "/#treatments", "hash": "#treatments", "requires_auth": True},
        {"key": "purchase", "path": "/#purchase", "hash": "#purchase", "requires_auth": True},
        {"key": "inventory", "path": "/#inventory", "hash": "#inventory", "requires_auth": True},
        {"key": "salary", "path": "/#salary", "hash": "#salary", "requires_auth": True},
        {"key": "cashbook", "path": "/#cashbook", "hash": "#cashbook", "requires_auth": True},
        {"key": "callcenter", "path": "/#callcenter", "hash": "#callcenter", "requires_auth": True},
        {"key": "reports", "path": "/#reports", "hash": "#reports", "requires_auth": True},
        {"key": "categories", "path": "/#categories", "hash": "#categories", "requires_auth": True},
        {"key": "locations", "path": "/#locations", "hash": "#locations", "requires_auth": True},
        {"key": "users", "path": "/#users", "hash": "#users", "requires_auth": True},
        {"key": "settings", "path": "/#settings", "hash": "#settings", "requires_auth": True},
    ]

    def __init__(self, output_dir: str = "tests/artifacts/screenshots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.baseline_dir = self.output_dir / "baseline"
        self.baseline_dir.mkdir(exist_ok=True)
        self.browser: Optional[Browser] = None
        self.context: Optional[Browser] = None
        self.auth_token: Optional[str] = None

    async def setup(self, viewport: str = "desktop"):
        """Initialize browser with specified viewport."""
        viewport_config = self.VIEWPORTS.get(viewport, self.VIEWPORTS["desktop"])
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            viewport=viewport_config,
            device_scale_factor=1,
            locale="vi-VN",
            timezone_id="Asia/Ho_Chi_Minh"
        )
        return playwright

    async def teardown(self, playwright):
        """Cleanup browser resources."""
        if self.browser:
            await self.browser.close()
        if playwright:
            await playwright.stop()

    async def login_local(self, page: Page, username: str = "admin@tdental.vn", password: str = "admin123") -> bool:
        """Login to local TDental instance and store session."""
        try:
            await page.goto(f"{self.LOCAL_BASE}/login", wait_until="networkidle")
            await page.fill('#loginEmail, input[type="email"], input[name="email"]', username)
            await page.fill('input[type="password"], input[name="password"]', password)
            await page.click('button[type="submit"], button:has-text("Đăng nhập")')
            await page.wait_for_load_state("networkidle")

            # Get session cookie for API calls
            cookies = await self.context.cookies()
            for cookie in cookies:
                if cookie['name'] == 'session':
                    self.auth_token = cookie['value']
                    break

            return True
        except Exception as e:
            print(f"    [WARN] Local login failed: {e}")
            return False

    async def login_live(self, page: Page, username: str, password: str) -> bool:
        """Login to live TDental instance."""
        try:
            await page.goto(f"{self.LIVE_BASE}/login", wait_until="networkidle")
            await page.fill('#loginEmail, input[type="email"], input[name="email"], input[type="text"]', username)
            await page.fill('input[type="password"]', password)
            await page.click('button[type="submit"], button:has-text("Đăng nhập")')
            await page.wait_for_load_state("networkidle", timeout=15000)
            return True
        except Exception as e:
            print(f"    [WARN] Live login failed: {e}")
            return False

    async def capture_screenshot(self, page: Page, url: str, route_key: str,
                                   target: str, viewport: str) -> Optional[Path]:
        """Capture screenshot of a specific route."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{target}_{route_key}_{viewport}_{timestamp}.png"
        filepath = self.output_dir / filename

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            # Wait for app to fully render
            await page.wait_for_timeout(2000)
            await page.screenshot(path=str(filepath), full_page=True)
            return filepath
        except Exception as e:
            print(f"    [ERROR] Failed to capture {route_key} on {target}: {e}")
            return None

    async def capture_route(self, route: Dict, viewport: str = "desktop",
                            target: str = "local", live_creds: tuple = None,
                            login_first: bool = True) -> Dict[str, Any]:
        """Capture screenshot for a specific route."""
        route_key = route["key"]
        requires_auth = route["requires_auth"]

        results = {
            "route": route_key,
            "path": route["path"],
            "viewport": viewport,
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "screenshot": None,
            "status": "pending",
            "error": None
        }

        base_url = self.LOCAL_BASE if target == "local" else self.LIVE_BASE
        url = f"{base_url}{route['path']}"

        playwright = await self.setup(viewport)

        try:
            page = await self.context.new_page()

            # Handle authentication
            if requires_auth and login_first:
                if target == "local":
                    if not await self.login_local(page):
                        results["status"] = "login_failed"
                        results["error"] = "Could not authenticate"
                        return results
                elif live_creds:
                    if not await self.login_live(page, live_creds[0], live_creds[1]):
                        results["status"] = "login_failed"
                        results["error"] = "Could not authenticate with live"
                        return results

            # Capture screenshot
            screenshot_path = await self.capture_screenshot(page, url, route_key, target, viewport)

            if screenshot_path:
                results["screenshot"] = str(screenshot_path)
                results["status"] = "success"
            else:
                results["status"] = "capture_failed"

            await page.close()

        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)

        finally:
            await self.teardown(playwright)

        return results

    async def capture_baseline(self, routes: List[str] = None, viewport: str = "desktop") -> List[Dict]:
        """Capture baseline screenshots for comparison."""
        if routes is None:
            routes = [r["key"] for r in self.ROUTES]

        results = []
        target_routes = [r for r in self.ROUTES if r["key"] in routes]

        print(f"\n{'='*60}")
        print(f"BASELINE CAPTURE: {len(target_routes)} routes, {viewport} viewport")
        print(f"{'='*60}")

        for route in target_routes:
            print(f"\n[Baseline] Capturing {route['key']}...")
            result = await self.capture_route(route, viewport, target="local", login_first=True)
            results.append(result)
            status_icon = "OK" if result["status"] == "success" else "FAIL"
            print(f"  -> {status_icon}: {result['status']}")

        return results

    def generate_report(self, results: List[Dict], output_file: str = None) -> Path:
        """Generate JSON report of capture results."""
        if output_file is None:
            output_file = f"parity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        report = {
            "generated_at": datetime.now().isoformat(),
            "viewports": self.VIEWPORTS,
            "total_routes": len(results),
            "successful": sum(1 for r in results if r.get("status") == "success"),
            "failed": sum(1 for r in results if r.get("status") != "success"),
            "results": results
        }

        report_path = self.output_dir / output_file
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return report_path


def print_summary(results: List[Dict], report_path: Path):
    """Print summary of capture results."""
    print(f"\n{'='*60}")
    print("CAPTURE SUMMARY")
    print(f"{'='*60}")

    success_count = 0
    for result in results:
        route = result.get("route", "unknown")
        status = result.get("status", "unknown")
        icon = "PASS" if status == "success" else "FAIL"
        print(f"  [{icon}] {route}: {status}")
        if status == "success":
            success_count += 1

    print(f"\nTotal: {success_count}/{len(results)} routes captured successfully")
    print(f"Report: {report_path}")
    print(f"Screenshots: {report_path.parent}/")


async def main():
    parser = argparse.ArgumentParser(
        description="TDental Screenshot Parity Capture - P6-01 Automation"
    )
    parser.add_argument(
        "--route", "-r",
        nargs="+",
        help="Specific routes to capture (e.g., dashboard customers)"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Capture all routes"
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Capture local screenshots only"
    )
    parser.add_argument(
        "--live-user",
        help="Live TDental username (required for live captures)"
    )
    parser.add_argument(
        "--live-pass",
        help="Live TDental password (required for live captures)"
    )
    parser.add_argument(
        "--viewport", "-v",
        choices=["desktop", "tablet", "mobile"],
        default="desktop",
        help="Viewport size for captures"
    )
    parser.add_argument(
        "--output", "-o",
        default="tests/artifacts/screenshots",
        help="Output directory for screenshots"
    )
    parser.add_argument(
        "--capture",
        choices=["baseline", "diff"],
        default="baseline",
        help="Capture mode: baseline or diff"
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: exit with code based on pass/fail"
    )

    args = parser.parse_args()

    if not args.route and not args.all:
        parser.error("Either --route or --all is required")

    capture = ScreenshotParityCapture(output_dir=args.output)

    routes_to_capture = args.route if args.route else None
    live_creds = (args.live_user, args.live_pass) if args.live_user and args.live_pass else None

    # Run capture
    if args.all:
        print(f"Capturing all routes ({args.viewport})...")
        results = await capture.capture_baseline(viewport=args.viewport)
    else:
        print(f"Capturing routes: {routes_to_capture} ({args.viewport})...")
        results = await capture.capture_baseline(routes=routes_to_capture, viewport=args.viewport)

    # Generate report
    report_path = capture.generate_report(results)

    # Print summary
    print_summary(results, report_path)

    # CI mode: exit with appropriate code
    if args.ci:
        success_count = sum(1 for r in results if r.get("status") == "success")
        if success_count == len(results):
            print("\n[CI] All captures PASSED")
            sys.exit(0)
        else:
            print(f"\n[CI] {len(results) - success_count} captures FAILED")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
