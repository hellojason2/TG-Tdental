#!/usr/bin/env python3
"""
TDental Parity Capture Script

Captures screenshots of both local and live TDental for visual comparison.
Supports baseline capture and difference detection without relying on iframe embedding.

Usage:
    python scripts/parity_capture.py --route dashboard --capture baseline
    python scripts/parity_capture.py --route customers --capture diff
    python scripts/parity_capture.py --all --capture baseline
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from playwright.async_api import async_playwright, Browser, Page, Error as PlaywrightError
except ImportError:
    print("ERROR: playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)


class ParityCapture:
    """Handles screenshot capture for local vs live TDental comparison."""

    # Standard viewports for comparison
    VIEWPORTS = {
        "desktop": {"width": 1440, "height": 900},
        "tablet": {"width": 768, "height": 1024},
        "mobile": {"width": 375, "height": 667}
    }

    # Live TDental URL
    LIVE_BASE = "https://tamdentist.tdental.vn"
    LOCAL_BASE = "http://localhost:8899"

    # Route mapping (live hash route -> local hash route)
    ROUTE_MAP = {
        "dashboard": {"live": "#/dashboard", "local": "#dashboard"},
        "customers": {"live": "#/partners/customers", "local": "#customers"},
        "reception": {"live": "#/reception", "local": "#reception"},
        "calendar": {"live": "#/calendar", "local": "#calendar"},
        "treatments": {"live": "#/treatments", "local": "#treatments"},
        "sale-management": {"live": "#/sale-management", "local": "#purchase"},
        "stock": {"live": "#/stock", "local": "#inventory"},
        "hr/employees": {"live": "#/hr/employees", "local": "#salary"},
        "accounting": {"live": "#/accounting", "local": "#cashbook"},
        "callcenter": {"live": "#/callcenter", "local": "#callcenter"},
        "reports": {"live": "#/reports", "local": "#reports"},
        "categories": {"live": "#/categories", "local": "#categories"},
        "locations": {"live": "#/locations", "local": "#locations"},
        "users": {"live": "#/users", "local": "#users"},
        "settings": {"live": "#/settings", "local": "#settings"},
    }

    def __init__(self, output_dir: str = "parity_captures"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.browser: Optional[Browser] = None
        self.context: Optional[Browser] = None

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

    async def login_local(self, page: Page) -> bool:
        """Login to local TDental instance."""
        try:
            await page.goto(f"{self.LOCAL_BASE}/login", wait_until="networkidle")
            await page.fill('input[type="email"], input[name="email"]', "admin@tdental.vn")
            await page.fill('input[type="password"], input[name="password"]', "admin123")
            await page.click('button[type="submit"], button:has-text("Đăng nhập")')
            await page.wait_for_load_state("networkidle")
            return True
        except Exception as e:
            print(f"Local login failed: {e}")
            return False

    async def login_live(self, page: Page, username: str, password: str) -> bool:
        """Login to live TDental instance."""
        try:
            await page.goto(f"{self.LIVE_BASE}/login", wait_until="networkidle")
            await page.fill('input[type="email"], input[name="email"], input[type="text"]', username)
            await page.fill('input[type="password"]', password)
            await page.click('button[type="submit"], button:has-text("Đăng nhập")')
            await page.wait_for_load_state("networkidle", timeout=15000)
            return True
        except Exception as e:
            print(f"Live login failed: {e}")
            return False

    async def capture_screenshot(self, page: Page, url: str, route: str,
                                   target: str, viewport: str) -> Path:
        """Capture screenshot of a specific route."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{target}_{route}_{viewport}_{timestamp}.png"
        filepath = self.output_dir / filename

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            # Wait for app to fully render
            await page.wait_for_timeout(2000)
            await page.screenshot(path=str(filepath), full_page=True)
            print(f"  Captured: {filepath.name}")
            return filepath
        except Exception as e:
            print(f"  Failed to capture {route} on {target}: {e}")
            return None

    async def capture_route(self, route_key: str, viewport: str = "desktop",
                            login: bool = True, live_creds: tuple = None) -> dict:
        """Capture both local and live screenshots for a route."""
        if route_key not in self.ROUTE_MAP:
            print(f"Unknown route: {route_key}")
            return {}

        route_info = self.ROUTE_MAP[route_key]
        results = {
            "route": route_key,
            "viewport": viewport,
            "timestamp": datetime.now().isoformat(),
            "local": None,
            "live": None,
            "status": "pending"
        }

        playwright = await self.setup(viewport)

        try:
            # Capture local
            print(f"\n[{route_key}] Capturing local ({viewport})...")
            page = await self.context.new_page()

            if login:
                await self.login_local(page)

            local_url = f"{self.LOCAL_BASE}/{route_info['local']}"
            local_path = await self.capture_screenshot(
                page, local_url, route_key, "local", viewport
            )
            results["local"] = str(local_path) if local_path else None
            await page.close()

            # Capture live
            print(f"[{route_key}] Capturing live ({viewport})...")
            page = await self.context.new_page()

            if live_creds:
                await self.login_live(page, live_creds[0], live_creds[1])

            live_url = f"{self.LIVE_BASE}/{route_info['live']}"
            live_path = await self.capture_screenshot(
                page, live_url, route_key, "live", viewport
            )
            results["live"] = str(live_path) if live_path else None
            await page.close()

            results["status"] = "completed"

        except Exception as e:
            results["status"] = f"error: {str(e)}"
            print(f"Error capturing {route_key}: {e}")

        finally:
            await self.teardown(playwright)

        return results

    async def capture_all(self, viewport: str = "desktop", login: bool = True,
                          live_creds: tuple = None) -> list:
        """Capture all routes."""
        results = []
        for route_key in self.ROUTE_MAP.keys():
            result = await self.capture_route(route_key, viewport, login, live_creds)
            results.append(result)
        return results

    def generate_report(self, results: list) -> Path:
        """Generate JSON report of capture results."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "viewports": self.VIEWPORTS,
            "routes": self.ROUTE_MAP,
            "results": results
        }

        report_path = self.output_dir / f"capture_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\nReport saved to: {report_path}")
        return report_path


async def main():
    parser = argparse.ArgumentParser(
        description="TDental Parity Capture - Screenshot comparison tool"
    )
    parser.add_argument(
        "--route", "-r",
        help="Specific route to capture (e.g., dashboard, customers)"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Capture all routes"
    )
    parser.add_argument(
        "--viewport", "-v",
        choices=["desktop", "tablet", "mobile"],
        default="desktop",
        help="Viewport size for captures"
    )
    parser.add_argument(
        "--output", "-o",
        default="parity_captures",
        help="Output directory for screenshots"
    )
    parser.add_argument(
        "--capture", "-c",
        choices=["baseline", "diff"],
        default="baseline",
        help="Capture mode: baseline or diff"
    )
    parser.add_argument(
        "--live-user",
        help="Live TDental username (required for live captures)"
    )
    parser.add_argument(
        "--live-pass",
        help="Live TDental password (required for live captures)"
    )

    args = parser.parse_args()

    if not args.route and not args.all:
        parser.error("Either --route or --all is required")

    capture = ParityCapture(output_dir=args.output)

    live_creds = None
    if args.live_user and args.live_pass:
        live_creds = (args.live_user, args.live_pass)

    if args.all:
        print(f"Capturing all routes ({args.viewport})...")
        results = await capture.capture_all(
            viewport=args.viewport,
            login=True,
            live_creds=live_creds
        )
    else:
        print(f"Capturing route: {args.route} ({args.viewport})...")
        results = [await capture.capture_route(
            args.route,
            viewport=args.viewport,
            login=True,
            live_creds=live_creds
        )]

    # Generate report
    report_path = capture.generate_report(results)

    # Summary
    completed = sum(1 for r in results if r.get("status") == "completed")
    print(f"\n{'='*50}")
    print(f"Capture complete: {completed}/{len(results)} routes captured")
    print(f"Report: {report_path}")
    print(f"Screenshots: {args.output}/")


if __name__ == "__main__":
    asyncio.run(main())
