#!/usr/bin/env python3
"""Capture UI snapshots and compare replica pages against original baselines."""

from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageOps, ImageStat
from playwright.async_api import Page, async_playwright


ROUTES: tuple[tuple[str, str], ...] = (
    ("01-dashboard", "#/dashboard"),
    ("02-customers", "#/partners"),
    ("03-work", "#/work"),
    ("04-calendar", "#/calendar"),
    ("05-labo", "#/labo"),
    ("06-purchase", "#/purchase"),
    ("07-warehouse", "#/warehouse"),
    ("08-catalog", "#/categories"),
    ("09-commission", "#/commission"),
    ("10-salary", "#/salary"),
    ("11-cashbook", "#/cashbook"),
    ("12-callcenter", "#/callcenter"),
    ("13-reports", "#/reports"),
    ("14-settings", "#/settings"),
)

MOCK_BRANCHES = [
    {"id": "branch-q3", "name": "Tâm Dentist Quận 3"},
    {"id": "branch-q10", "name": "Tâm Dentist Quận 10"},
    {"id": "branch-phu-nhuan", "name": "Tâm Dentist Phú Nhuận"},
]


@dataclass
class DiffResult:
    route: str
    baseline_exists: bool
    overall_pct: float | None = None
    topbar_pct: float | None = None
    status: str = "SKIP"


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(
        description="Visual parity audit for TDental replica vs original captures."
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8899",
        help="Replica app base URL (default: %(default)s).",
    )
    parser.add_argument(
        "--original-dir",
        type=Path,
        default=root / "comparison" / "original",
        help="Directory containing original baseline images.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "output" / "parity",
        help="Directory where captured and diff images will be saved.",
    )
    parser.add_argument(
        "--wait-ms",
        type=int,
        default=1800,
        help="Wait time after navigation/clicks before capture.",
    )
    parser.add_argument(
        "--threshold-overall",
        type=float,
        default=22.0,
        help="Overall diff threshold percentage.",
    )
    parser.add_argument(
        "--threshold-topbar",
        type=float,
        default=12.0,
        help="Topbar diff threshold percentage.",
    )
    parser.add_argument(
        "--no-capture",
        action="store_true",
        help="Skip browser capture and only compare existing output images.",
    )
    return parser.parse_args()


def compare_images(
    baseline_path: Path, current_path: Path, diff_path: Path
) -> tuple[float, float]:
    with Image.open(baseline_path).convert("RGB") as baseline_img:
        with Image.open(current_path).convert("RGB") as current_img:
            if current_img.size != baseline_img.size:
                current_img = current_img.resize(
                    baseline_img.size, Image.Resampling.LANCZOS
                )

            diff = ImageChops.difference(baseline_img, current_img)
            diff_img = ImageOps.autocontrast(diff)
            diff_path.parent.mkdir(parents=True, exist_ok=True)
            diff_img.save(diff_path)

            overall = _mean_diff_pct(diff)

            top_h = min(110, baseline_img.height)
            baseline_top = baseline_img.crop((0, 0, baseline_img.width, top_h))
            current_top = current_img.crop((0, 0, current_img.width, top_h))
            top_diff = ImageChops.difference(baseline_top, current_top)
            topbar = _mean_diff_pct(top_diff)
            return overall, topbar


def _mean_diff_pct(diff_img: Image.Image) -> float:
    stat = ImageStat.Stat(diff_img)
    channel_mean = sum(stat.mean) / len(stat.mean)
    return round((channel_mean / 255.0) * 100.0, 2)


async def install_api_mocks(page: Page) -> None:
    async def mock_companies(route):
        await route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(MOCK_BRANCHES, ensure_ascii=False),
        )

    async def mock_session(route):
        await route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(
                {
                    "user": {
                        "id": "demo",
                        "name": "Admin",
                        "email": "admin@tdental.vn",
                        "role": "admin",
                    }
                }
            ),
        )

    await page.route("**/api/companies*", mock_companies)
    await page.route("**/api/auth/session*", mock_session)


async def capture_routes(base_url: str, output_dir: Path, wait_ms: int) -> tuple[bool, str]:
    capture_dir = output_dir / "current"
    capture_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()
        await install_api_mocks(page)

        for route_key, hash_route in ROUTES:
            await page.goto(f"{base_url}/static/tdental.html{hash_route}", wait_until="domcontentloaded")
            await page.wait_for_timeout(wait_ms)
            await page.screenshot(path=str(capture_dir / f"{route_key}.png"), full_page=False)

        # Dedicated branch-dropdown interaction capture and assertion.
        await page.goto(f"{base_url}/static/tdental.html#/dashboard", wait_until="domcontentloaded")
        await page.wait_for_timeout(wait_ms)
        await page.click("#branch-btn")
        await page.wait_for_timeout(180)
        await page.screenshot(path=str(capture_dir / "branch-dropdown-open.png"), full_page=False)
        await page.click('[data-branch-value="branch-q3"]')
        await page.wait_for_timeout(450)
        label = (await page.text_content("#branch-label") or "").strip()
        stored = await page.evaluate("() => localStorage.getItem('selected_branch')")
        await page.screenshot(path=str(capture_dir / "branch-dropdown-selected.png"), full_page=False)

        await context.close()
        await browser.close()

    is_ok = ("Quận 3" in label) and (stored == "branch-q3")
    return is_ok, f"{label} | selected_branch={stored}"


def run_diff(
    original_dir: Path,
    output_dir: Path,
    threshold_overall: float,
    threshold_topbar: float,
) -> list[DiffResult]:
    results: list[DiffResult] = []
    current_dir = output_dir / "current"
    diff_dir = output_dir / "diff"

    for route_key, _ in ROUTES:
        baseline = original_dir / f"{route_key}.png"
        current = current_dir / f"{route_key}.png"
        result = DiffResult(route=route_key, baseline_exists=baseline.exists())

        if not baseline.exists() or not current.exists():
            result.status = "MISSING"
            results.append(result)
            continue

        overall, topbar = compare_images(baseline, current, diff_dir / f"{route_key}-diff.png")
        result.overall_pct = overall
        result.topbar_pct = topbar
        if overall <= threshold_overall and topbar <= threshold_topbar:
            result.status = "PASS"
        else:
            result.status = "REVIEW"
        results.append(result)

    return results


def write_report(
    output_dir: Path,
    results: list[DiffResult],
    branch_label_ok: bool,
    branch_label_text: str,
    threshold_overall: float,
    threshold_topbar: float,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "report.md"

    lines = [
        "# UI Parity Audit",
        "",
        f"- Threshold overall: `{threshold_overall:.2f}%`",
        f"- Threshold topbar: `{threshold_topbar:.2f}%`",
        f"- Branch dropdown select check: `{'PASS' if branch_label_ok else 'REVIEW'}` (`{branch_label_text}`)",
        "",
        "| Route | Overall Diff % | Topbar Diff % | Status |",
        "| --- | ---: | ---: | --- |",
    ]
    for item in results:
        overall = f"{item.overall_pct:.2f}" if item.overall_pct is not None else "-"
        topbar = f"{item.topbar_pct:.2f}" if item.topbar_pct is not None else "-"
        lines.append(f"| {item.route} | {overall} | {topbar} | {item.status} |")

    lines.extend(
        [
            "",
            "Artifacts:",
            f"- Current captures: `{(output_dir / 'current').as_posix()}`",
            f"- Diff images: `{(output_dir / 'diff').as_posix()}`",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


async def main() -> int:
    args = parse_args()
    output_dir = args.output_dir
    branch_ok = False
    branch_text = ""

    if not args.no_capture:
        branch_ok, branch_text = await capture_routes(args.base_url, output_dir, args.wait_ms)

    results = run_diff(
        args.original_dir,
        output_dir,
        args.threshold_overall,
        args.threshold_topbar,
    )
    report_path = write_report(
        output_dir,
        results,
        branch_ok,
        branch_text,
        args.threshold_overall,
        args.threshold_topbar,
    )

    review_count = sum(1 for item in results if item.status == "REVIEW")
    missing_count = sum(1 for item in results if item.status == "MISSING")

    print(f"Report: {report_path}")
    print(f"Routes reviewed: {len(results)} | REVIEW: {review_count} | MISSING: {missing_count}")
    if not branch_ok:
        print("Branch dropdown interaction check requires review.")

    if review_count > 0 or not branch_ok:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
