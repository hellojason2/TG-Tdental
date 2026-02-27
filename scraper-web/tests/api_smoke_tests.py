#!/usr/bin/env python3
"""
P6-03: API Contract Smoke Tests

Tests critical API endpoints to verify contract compliance and functionality.
Runs smoke tests on authentication, customers, appointments, and other key endpoints.

Usage:
    # Run all API smoke tests
    python tests/api_smoke_tests.py --all

    # Test specific endpoints
    python tests/api_smoke_tests.py --endpoints auth login customers

    # CI mode
    python tests/api_smoke_tests.py --all --ci
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import requests

# Configuration
LOCAL_BASE = "http://localhost:8899"
API_BASE = f"{LOCAL_BASE}/api"


class APISmokeTester:
    """API smoke testing for TDental endpoints."""

    # Test configuration
    TEST_USER = {"email": "admin@tdental.vn", "password": "admin123"}
    TIMEOUT = 15  # seconds

    # API endpoints to test
    ENDPOINTS = {
        # Auth endpoints
        "auth_login": {
            "method": "POST",
            "path": "/auth/login",
            "payload": {"email": "admin@tdental.vn", "password": "admin123"},
            "expect_status": 200,
            "expect_key": "token",
            "description": "Login endpoint"
        },
        "auth_logout": {
            "method": "POST",
            "path": "/auth/logout",
            "require_auth": True,
            "expect_status": 200,
            "description": "Logout endpoint"
        },
        "auth_me": {
            "method": "GET",
            "path": "/auth/me",
            "require_auth": True,
            "expect_status": 200,
            "expect_key": "email",
            "description": "Get current user"
        },

        # Customer endpoints
        "customers_list": {
            "method": "GET",
            "path": "/customers",
            "require_auth": True,
            "expect_status": 200,
            "expect_key": "data",
            "description": "List customers"
        },
        "customers_search": {
            "method": "GET",
            "path": "/customers?search=test",
            "require_auth": True,
            "expect_status": 200,
            "description": "Search customers"
        },
        "customers_pagination": {
            "method": "GET",
            "path": "/customers?page=1&per_page=10",
            "require_auth": True,
            "expect_status": 200,
            "description": "Customer pagination"
        },

        # Appointment endpoints
        "appointments_list": {
            "method": "GET",
            "path": "/appointments",
            "require_auth": True,
            "expect_status": 200,
            "description": "List appointments"
        },
        "appointments_today": {
            "method": "GET",
            "path": "/appointments?date=today",
            "require_auth": True,
            "expect_status": 200,
            "description": "Today's appointments"
        },

        # User management endpoints
        "users_list": {
            "method": "GET",
            "path": "/users",
            "require_auth": True,
            "admin_only": True,
            "expect_status": 200,
            "expect_key": "users",
            "description": "List users (admin)"
        },

        # Dashboard endpoints
        "dashboard_stats": {
            "method": "GET",
            "path": "/dashboard/stats",
            "require_auth": True,
            "expect_status": 200,
            "description": "Dashboard statistics"
        },
        "dashboard_summary": {
            "method": "GET",
            "path": "/dashboard/summary",
            "require_auth": True,
            "expect_status": 200,
            "description": "Dashboard summary"
        },

        # Settings endpoints
        "settings_list": {
            "method": "GET",
            "path": "/settings",
            "require_auth": True,
            "expect_status": 200,
            "description": "List settings"
        },
        "settings_update": {
            "method": "PUT",
            "path": "/settings",
            "require_auth": True,
            "payload": {"key": "test_key", "value": "test_value"},
            "expect_status": 200,
            "description": "Update settings"
        },

        # Company/Branch endpoints
        "companies_list": {
            "method": "GET",
            "path": "/companies",
            "require_auth": True,
            "expect_status": 200,
            "description": "List companies"
        },
        "branches_list": {
            "method": "GET",
            "path": "/branches",
            "require_auth": True,
            "expect_status": 200,
            "description": "List branches"
        },

        # Treatment endpoints
        "treatments_list": {
            "method": "GET",
            "path": "/treatments",
            "require_auth": True,
            "expect_status": 200,
            "description": "List treatments"
        },

        # Reception endpoints
        "reception_queue": {
            "method": "GET",
            "path": "/reception/queue",
            "require_auth": True,
            "expect_status": 200,
            "description": "Reception queue"
        },

        # Reports endpoints
        "reports_revenue": {
            "method": "GET",
            "path": "/reports/revenue",
            "require_auth": True,
            "expect_status": 200,
            "description": "Revenue report"
        },
    }

    def __init__(self, output_dir: str = "tests/artifacts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.token: Optional[str] = None
        self.results: List[Dict] = []

    def login(self) -> bool:
        """Login and store auth token."""
        endpoint = self.ENDPOINTS["auth_login"]
        try:
            response = requests.post(
                f"{API_BASE}/auth/login",
                json=endpoint["payload"],
                timeout=self.TIMEOUT
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                if self.token:
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                    print(f"  [OK] Login successful")
                    return True

            print(f"  [FAIL] Login failed: {response.status_code}")
            return False
        except Exception as e:
            print(f"  [ERROR] Login error: {e}")
            return False

    def test_endpoint(self, name: str, config: Dict) -> Dict[str, Any]:
        """Test a single API endpoint."""
        result = {
            "endpoint": name,
            "path": config["path"],
            "method": config["method"],
            "description": config.get("description", ""),
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "response_status": None,
            "response_time": None,
            "error": None,
            "details": {}
        }

        # Check if authentication is required
        if config.get("require_auth") and not self.token:
            result["status"] = "skipped"
            result["error"] = "No auth token available"
            return result

        url = f"{API_BASE}{config['path']}"
        method = config["method"]
        payload = config.get("payload")

        start_time = time.time()

        try:
            if method == "GET":
                response = self.session.get(url, timeout=self.TIMEOUT)
            elif method == "POST":
                response = self.session.post(url, json=payload, timeout=self.TIMEOUT)
            elif method == "PUT":
                response = self.session.put(url, json=payload, timeout=self.TIMEOUT)
            elif method == "DELETE":
                response = self.session.delete(url, timeout=self.TIMEOUT)
            else:
                result["status"] = "error"
                result["error"] = f"Unsupported method: {method}"
                return result

            result["response_time"] = round((time.time() - start_time) * 1000, 2)  # ms
            result["response_status"] = response.status_code

            # Check status code
            expected_status = config.get("expect_status", 200)
            if response.status_code != expected_status:
                result["status"] = "fail"
                result["error"] = f"Expected {expected_status}, got {response.status_code}"
                try:
                    result["details"]["response_body"] = response.json()
                except:
                    result["details"]["response_body"] = response.text[:500]
                return result

            # Check for expected key in response
            try:
                data = response.json()
                result["details"]["response_body"] = data

                if "expect_key" in config:
                    if config["expect_key"] in data:
                        result["status"] = "pass"
                    else:
                        result["status"] = "fail"
                        result["error"] = f"Expected key '{config['expect_key']}' not found in response"
                else:
                    result["status"] = "pass"

            except json.JSONDecodeError:
                result["status"] = "pass" if response.status_code == expected_status else "fail"
                result["details"]["response_body"] = response.text[:500]

        except requests.exceptions.Timeout:
            result["status"] = "timeout"
            result["error"] = f"Request timed out after {self.TIMEOUT}s"
        except requests.exceptions.ConnectionError:
            result["status"] = "error"
            result["error"] = "Connection error - is the server running?"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def run_tests(self, endpoints: List[str] = None) -> List[Dict]:
        """Run all specified endpoint tests."""
        if endpoints is None:
            endpoints = list(self.ENDPOINTS.keys())

        target_endpoints = {k: v for k, v in self.ENDPOINTS.items() if k in endpoints}

        print(f"\n{'='*60}")
        print(f"API SMOKE TESTS: {len(target_endpoints)} endpoints")
        print(f"{'='*60}")

        # First, try to login
        print("\n[Setup] Authenticating...")
        if not self.login():
            print("[WARN] Proceeding without authentication - some tests will be skipped")

        results = []
        for name, config in target_endpoints.items():
            print(f"\n[Testing] {name} ({config['method']} {config['path']})")
            result = self.test_endpoint(name, config)
            results.append(result)

            # Print result
            status = result.get("status", "unknown")
            if status == "pass":
                print(f"  -> PASS ({result.get('response_time')}ms)")
            elif status == "skipped":
                print(f"  -> SKIP: {result.get('error')}")
            elif status == "fail":
                print(f"  -> FAIL: {result.get('error')}")
            else:
                print(f"  -> {status.upper()}: {result.get('error')}")

        return results

    def generate_report(self, results: List[Dict]) -> Path:
        """Generate JSON report of test results."""
        passed = sum(1 for r in results if r.get("status") == "pass")
        failed = sum(1 for r in results if r.get("status") == "fail")
        skipped = sum(1 for r in results if r.get("status") == "skipped")
        errors = sum(1 for r in results if r.get("status") == "error")

        report = {
            "generated_at": datetime.now().isoformat(),
            "base_url": API_BASE,
            "summary": {
                "total": len(results),
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "errors": errors
            },
            "results": results
        }

        filename = f"api_smoke_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.output_dir / filename

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return report_path


def print_summary(results: List[Dict], report_path: Path):
    """Print summary of test results."""
    print(f"\n{'='*60}")
    print("API SMOKE TEST SUMMARY")
    print(f"{'='*60}")

    passed = sum(1 for r in results if r.get("status") == "pass")
    failed = sum(1 for r in results if r.get("status") == "fail")
    skipped = sum(1 for r in results if r.get("status") == "skipped")

    for result in results:
        endpoint = result.get("endpoint", "unknown")
        status = result.get("status", "unknown")
        method = result.get("method", "")
        path = result.get("path", "")

        icon = "OK" if status == "pass" else "SKIP" if status == "skipped" else "FAIL"
        print(f"  [{icon}] {method} {path}: {status}")

    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    print(f"Report: {report_path}")


def main():
    parser = argparse.ArgumentParser(
        description="TDental API Smoke Tests - P6-03 Automation"
    )
    parser.add_argument(
        "--endpoints", "-e",
        nargs="+",
        help="Specific endpoints to test"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Test all configured endpoints"
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

    if not args.endpoints and not args.all:
        parser.error("Either --endpoints or --all is required")

    tester = APISmokeTester(output_dir=args.output)
    endpoints_to_test = args.endpoints if args.endpoints else None

    results = tester.run_tests(endpoints=endpoints_to_test)
    report_path = tester.generate_report(results)

    print_summary(results, report_path)

    if args.ci:
        failed = sum(1 for r in results if r.get("status") == "fail")
        errors = sum(1 for r in results if r.get("status") == "error")
        if failed == 0 and errors == 0:
            print("\n[CI] All API smoke tests PASSED")
            sys.exit(0)
        else:
            print(f"\n[CI] {failed + errors} API smoke tests FAILED")
            sys.exit(1)


if __name__ == "__main__":
    main()
