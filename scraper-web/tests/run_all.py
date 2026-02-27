#!/usr/bin/env python3
"""
TDental Test Automation Suite - Master Runner

Combines all test automation scripts:
- P6-01: Screenshot Parity Capture
- P6-02: Interaction Tests
- P6-03: API Smoke Tests
- P6-04: Component Regression Tests
- P6-05: Pre-Release Checklist

Usage:
    # Run all tests
    python tests/run_all.py

    # Run pre-release checklist only
    python tests/run_all.py --checklist

    # Run specific test category
    python tests/run_all.py --screenshots
    python tests/run_all.py --interactions
    python tests/run_all.py --api
    python tests/run_all.py --components

    # CI mode
    python tests/run_all.py --all --ci
"""

import argparse
import asyncio
import sys
import subprocess
from pathlib import Path
from datetime import datetime


def run_command(cmd, description):
    """Run a command and return its exit code."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}\n")

    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="TDental Test Automation Suite - Master Runner"
    )

    # Test categories
    parser.add_argument(
        "--screenshots", "-s",
        action="store_true",
        help="Run screenshot parity tests (P6-01)"
    )
    parser.add_argument(
        "--interactions", "-i",
        action="store_true",
        help="Run interaction tests (P6-02)"
    )
    parser.add_argument(
        "--api", "-a",
        action="store_true",
        help="Run API smoke tests (P6-03)"
    )
    parser.add_argument(
        "--components", "-c",
        action="store_true",
        help="Run component regression tests (P6-04)"
    )
    parser.add_argument(
        "--checklist", "-k",
        action="store_true",
        help="Run pre-release checklist (P6-05)"
    )
    parser.add_argument(
        "--all", "-A",
        action="store_true",
        help="Run all tests"
    )

    # Options
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: exit with code based on pass/fail"
    )

    args = parser.parse_args()

    # If no specific test is selected, run all
    if not any([args.screenshots, args.interactions, args.api, args.components, args.checklist]):
        args.all = True

    # Track results
    results = {}

    print("=" * 60)
    print("TDENTAL TEST AUTOMATION SUITE")
    print(f"Started at: {datetime.now().strftime('%Y%m-%d %H:%M:%S')}")
    print("=" * 60)

    # P6-01: Screenshot Parity
    if args.all or args.screenshots:
        cmd = ["python", "tests/screenshot_parity.py", "--all"]
        if args.ci:
            cmd.append("--ci")
        results["screenshots"] = run_command(cmd, "Screenshot Parity Tests (P6-01)")

    # P6-02: Interaction Tests
    if args.all or args.interactions:
        cmd = ["python", "tests/interaction_tests.py", "--all"]
        if args.ci:
            cmd.append("--ci")
        results["interactions"] = run_command(cmd, "Interaction Tests (P6-02)")

    # P6-03: API Smoke Tests
    if args.all or args.api:
        cmd = ["python", "tests/api_smoke_tests.py", "--all"]
        if args.ci:
            cmd.append("--ci")
        results["api"] = run_command(cmd, "API Smoke Tests (P6-03)")

    # P6-04: Component Tests
    if args.all or args.components:
        cmd = ["python", "tests/component_tests.py", "--all"]
        if args.ci:
            cmd.append("--ci")
        results["components"] = run_command(cmd, "Component Regression Tests (P6-04)")

    # P6-05: Pre-release Checklist
    if args.all or args.checklist:
        cmd = ["python", "tests/pre_release_checklist.py"]
        if args.ci:
            cmd.append("--ci")
        results["checklist"] = run_command(cmd, "Pre-Release Checklist (P6-05)")

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUITE SUMMARY")
    print("=" * 60)

    for test_name, exit_code in results.items():
        status = "PASS" if exit_code == 0 else "FAIL"
        print(f"  [{status}] {test_name}")

    all_passed = all(code == 0 for code in results.values())

    print(f"\nOverall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")

    if args.ci:
        sys.exit(0 if all_passed else 1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
