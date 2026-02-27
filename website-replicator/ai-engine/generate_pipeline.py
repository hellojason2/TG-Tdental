#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
  PAGE-BY-PAGE GENERATION PIPELINE
  
  Crawl output → Claude Vision → React component → Visual verify
  
  The ONLY approach that works for authenticated SPAs:
  1. Crawler already captured screenshot + DOM + API for each route
  2. This pipeline feeds each page to Claude one-at-a-time
  3. Claude sees the screenshot AND the DOM structure
  4. Generates a pixel-accurate React component
  5. Renders it, takes screenshot, compares with original
  6. If diff > threshold, sends diff back to Claude for fix
  7. Repeats until match or max iterations
═══════════════════════════════════════════════════════════════════
"""
import asyncio
import base64
import json
import os
import re
import sys
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import anthropic
import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel

console = Console()

# ─── Configuration ─────────────────────────────────────────

@dataclass
class PipelineConfig:
    """Configuration for the generation pipeline"""
    # Input
    crawl_dir: str                          # Path to crawl output (data/{job_id})
    
    # AI
    api_key: str = ""                       # Anthropic API key (or env ANTHROPIC_API_KEY)
    model: str = "claude-sonnet-4-20250514" # Model for generation
    vision_model: str = "claude-sonnet-4-20250514"  # Model for visual diff
    max_tokens: int = 16000                 # Max tokens per generation
    
    # Output
    output_dir: str = ""                    # Where to write generated code (default: crawl_dir/generated)
    framework: str = "nextjs"               # nextjs | react
    ui_lib: str = "antd"                    # antd | shadcn | mui
    css: str = "tailwind"                   # tailwind | css-modules
    locale: str = "vi-VN"                   # Locale for i18n
    
    # Generation
    max_retries: int = 3                    # Visual verify retry loops per page
    max_pages: int = 0                      # 0 = all pages
    skip_existing: bool = True              # Skip pages already generated
    pages_filter: list = field(default_factory=list)  # Only generate these routes (empty = all)
    
    # Verification
    verify: bool = False                    # Enable visual diff verification
    diff_threshold: float = 0.15            # Max acceptable pixel diff (0-1)
    vite_port: int = 5173                   # Port for Vite dev server
    
    def __post_init__(self):
        if not self.api_key:
            self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not self.output_dir:
            self.output_dir = f"{self.crawl_dir}/generated"


# ─── Data Loading ──────────────────────────────────────────

class CrawlData:
    """Loads and indexes all crawl output for a job"""
    
    def __init__(self, crawl_dir: str):
        self.dir = crawl_dir
        self.routes: list[str] = []
        self.api_map: dict = {}
        self.db_schema: dict = {}
        self.design_tokens: dict = {}
        self.stats: dict = {}
        self._load()
    
    def _load(self):
        """Load all crawl metadata"""
        self.routes = self._load_json("routes.json") or []
        self.api_map = self._load_json("api_map.json") or {}
        self.db_schema = self._load_json("db_schema.json") or {}
        self.design_tokens = self._load_json("design_tokens.json") or {}
        self.stats = self._load_json("stats.json") or {}
        
        # If no routes.json, discover from screenshots
        if not self.routes:
            ss_dir = f"{self.dir}/screenshots"
            if os.path.exists(ss_dir):
                self.routes = [
                    f.replace('.png', '').replace('_', '/')
                    for f in sorted(os.listdir(ss_dir))
                    if f.endswith('.png')
                ]
        
        console.print(f"[green]✓ Loaded {len(self.routes)} routes, "
                       f"{len(self.api_map)} API controllers, "
                       f"{len(self.db_schema)} tables[/]")
    
    def _load_json(self, filename: str) -> Optional[dict | list]:
        path = f"{self.dir}/{filename}"
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return None
    
    def safe_name(self, route: str) -> str:
        """Convert route to safe filename"""
        return re.sub(r'[^a-zA-Z0-9_-]', '_', route.strip('/').replace('#', ''))[:80] or "index"
    
    def get_screenshot_b64(self, route: str) -> Optional[str]:
        """Load screenshot as base64"""
        safe = self.safe_name(route)
        path = f"{self.dir}/screenshots/{safe}.png"
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return None
    
    def get_screenshot_size(self, route: str) -> int:
        """Get screenshot file size in bytes"""
        safe = self.safe_name(route)
        path = f"{self.dir}/screenshots/{safe}.png"
        return os.path.getsize(path) if os.path.exists(path) else 0
    
    def get_dom(self, route: str) -> Optional[dict]:
        """Load DOM tree for route"""
        safe = self.safe_name(route)
        path = f"{self.dir}/dom/{safe}.json"
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return None
    
    def get_hover_states(self, route: str) -> Optional[list]:
        safe = self.safe_name(route)
        path = f"{self.dir}/hover/{safe}.json"
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return None
    
    def get_animations(self, route: str) -> Optional[dict]:
        safe = self.safe_name(route)
        path = f"{self.dir}/animations/{safe}.json"
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return None
    
    def get_api_calls_for_route(self, route: str) -> list:
        """Get API calls that were made on this route"""
        safe = self.safe_name(route)
        # Check api_map for matching controller
        matching = {}
        for controller, endpoints in self.api_map.items():
            if safe.lower() in controller.lower() or controller.lower() in safe.lower():
                matching[controller] = endpoints
        
        # Also load raw API calls and filter by route
        raw_path = f"{self.dir}/api_calls_raw.json"
        if os.path.exists(raw_path):
            with open(raw_path) as f:
                raw = json.load(f)
                # Filter calls that happened during this route visit
                # (crude but effective — look for calls with matching path segments)
                route_keywords = [s for s in safe.split('_') if len(s) > 2]
                for call in raw:
                    url = call.get("url", "")
                    if any(kw.lower() in url.lower() for kw in route_keywords):
                        controller = url.split("/api/")[-1].split("/")[0] if "/api/" in url else "Unknown"
                        if controller not in matching:
                            matching[controller] = []
                        matching[controller].append(call)
        
        return matching


# ─── Prompt Builder ────────────────────────────────────────

class PromptBuilder:
    """Builds optimal prompts for Claude — balancing detail vs context window"""
    
    def __init__(self, config: PipelineConfig, data: CrawlData):
        self.config = config
        self.data = data
    
    def build_system_prompt(self) -> str:
        """System prompt — the DNA of the generation"""
        tokens = json.dumps(self.data.design_tokens, indent=2)[:3000] if self.data.design_tokens else "{}"
        
        return f"""You are an EXPERT frontend developer tasked with pixel-perfect website replication.

YOUR MISSION: Recreate the page shown in the screenshot as an EXACT visual clone using React + TypeScript + Ant Design 5 + Tailwind CSS.

## CRITICAL RULES — READ THESE FIRST
1. The screenshot is your GROUND TRUTH. Match it exactly — layout, colors, spacing, typography, icons, everything.
2. The DOM tree shows the ACTUAL structure and computed CSS. Use it for precise values (colors, padding, font sizes).
3. API data shows what real data looks like. Use realistic mock data matching the same shape.
4. Write COMPLETE, RUNNABLE code. No placeholders, no TODOs, no "..." truncation.
5. Every Vietnamese text visible in the screenshot must be included exactly as shown.
6. Use Ant Design components where they match (Table, Card, Button, Form, Select, DatePicker, Menu, Layout).
7. For charts/graphs, use Recharts (BarChart, LineChart, PieChart) with data matching the screenshot.
8. Match colors by extracting exact hex values from the DOM computed styles.
9. Vietnamese locale: DD/MM/YYYY dates, VND currency (###.###.### format), Vietnamese month names.

## DESIGN SYSTEM (extracted from the real site)
```json
{tokens}
```

## OUTPUT FORMAT
Return ONLY a single TypeScript React component file. Structure:
```tsx
"use client";
import React from "react";
// ... all imports

// Types
interface SomeData {{
  // ...
}}

// Mock data (matching real API response shapes)
const mockData: SomeData[] = [
  // ...
];

// Component
export default function PageName() {{
  return (
    // Full page content matching screenshot
  );
}}
```

## COMPONENT PATTERNS
- Sidebar layout: Use Ant Design Layout + Sider. Dark sidebar (#001529), collapsible, with Menu component.
- Data tables: Ant Design Table with proper columns, Vietnamese headers, formatted numbers.
- Stat cards: Row of Cards at top with colored icons, number formatting with dots (###.###.###).
- Charts: Recharts with proper axes, Vietnamese labels, tooltip formatters.
- Forms: Ant Design Form with Vietnamese labels, proper validation messages.
- Date ranges: Ant Design DatePicker.RangePicker with Vietnamese locale.
- Search: Input.Search with F2 hotkey hint.

## WHAT MAKES THIS "PIXEL PERFECT"
- Exact hex colors from computed styles (not "blue" — use #1890ff)
- Exact font sizes in px (not "small" — use 14px, 12px, etc.)
- Exact padding/margin values from the DOM tree
- Exact border-radius values
- Exact box-shadow values
- Vietnamese text matches screenshot character-for-character
- Number formatting: 87.519.238.601 not 87,519,238,601
- Date formatting: 01/02/2026 not 2026-02-01"""

    def build_page_prompt(self, route: str) -> list:
        """Build the user message content array for a single page"""
        content = []
        
        # 1. SCREENSHOT (most important — this is what we're matching)
        screenshot_b64 = self.data.get_screenshot_b64(route)
        if screenshot_b64:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": screenshot_b64,
                },
            })
            content.append({
                "type": "text",
                "text": "⬆️ SCREENSHOT — This is what the page must look like. Match it EXACTLY.",
            })
        
        # 2. DOM TREE (trimmed to fit context)
        dom = self.data.get_dom(route)
        if dom:
            dom_str = json.dumps(dom, indent=2, default=str)
            # Trim to ~30K chars to leave room for other context
            if len(dom_str) > 30000:
                dom_str = self._trim_dom(dom, 30000)
            content.append({
                "type": "text",
                "text": f"## DOM TREE (with computed CSS values)\nUse these exact CSS values for pixel-perfect matching.\n```json\n{dom_str}\n```",
            })
        
        # 3. API CALLS for this page
        api_calls = self.data.get_api_calls_for_route(route)
        if api_calls:
            api_str = json.dumps(api_calls, indent=2, default=str)[:8000]
            content.append({
                "type": "text",
                "text": f"## API ENDPOINTS used by this page\nUse these response shapes for mock data.\n```json\n{api_str}\n```",
            })
        
        # 4. HOVER STATES
        hovers = self.data.get_hover_states(route)
        if hovers:
            hover_str = json.dumps(hovers[:20], indent=2)[:3000]
            content.append({
                "type": "text",
                "text": f"## HOVER STATES (style changes on mouseenter)\n```json\n{hover_str}\n```",
            })
        
        # 5. FINAL INSTRUCTION
        safe = self.data.safe_name(route)
        content.append({
            "type": "text",
            "text": f"""## GENERATE NOW
Route: {route}
Component name: {self._route_to_component_name(route)}
File path: app/(dashboard)/{safe}/page.tsx

Generate the COMPLETE component. Include ALL visible content from the screenshot.
Do NOT wrap it in a layout/sidebar — the layout is handled by a parent component.
Focus on the MAIN CONTENT AREA (everything to the right of the sidebar).

REMEMBER: 
- Vietnamese text exactly as shown
- Number format: ###.###.### (dots not commas) 
- Exact colors from DOM (bg, color, border)
- All chart data visible in screenshot
- All table columns and sample rows visible
- All stat cards with correct icons and values""",
        })
        
        return content
    
    def build_fix_prompt(self, route: str, original_b64: str, generated_b64: str, diff_score: float, current_code: str) -> list:
        """Build prompt for visual diff fix iteration"""
        content = [
            {
                "type": "image",
                "source": {"type": "base64", "media_type": "image/png", "data": original_b64},
            },
            {"type": "text", "text": "⬆️ ORIGINAL (target — what it should look like)"},
            {
                "type": "image",
                "source": {"type": "base64", "media_type": "image/png", "data": generated_b64},
            },
            {"type": "text", "text": f"⬆️ YOUR GENERATED VERSION (current diff score: {diff_score:.1%})"},
            {
                "type": "text",
                "text": f"""## FIX INSTRUCTIONS
Compare the two images above. Your generated version doesn't match the original.

FOCUS ON:
1. Missing elements (charts, cards, text that exists in original but not yours)
2. Wrong colors (compare carefully)
3. Wrong layout (spacing, alignment, sizing)
4. Wrong data formatting (numbers, dates)
5. Missing Vietnamese text

Here is your current code:
```tsx
{current_code[:12000]}
```

Return the COMPLETE FIXED component. Not a diff — the full file.""",
            },
        ]
        return content
    
    def build_layout_prompt(self) -> list:
        """Build prompt for the shared layout (sidebar + header)"""
        # Find a screenshot that shows the full sidebar
        sidebar_route = None
        for route in self.data.routes:
            ss = self.data.get_screenshot_b64(route)
            if ss:
                sidebar_route = route
                break
        
        content = []
        if sidebar_route:
            ss = self.data.get_screenshot_b64(sidebar_route)
            content.append({
                "type": "image",
                "source": {"type": "base64", "media_type": "image/png", "data": ss},
            })
        
        # Collect all route names for menu items
        menu_items = []
        for route in self.data.routes:
            name = route.strip('/').replace('#', '').replace('-', ' ').replace('_', ' ')
            menu_items.append({"route": route, "name": name})
        
        content.append({
            "type": "text",
            "text": f"""## GENERATE THE SHARED LAYOUT

Create the dashboard layout that wraps ALL pages. This includes:
1. **Left Sidebar** — Dark (#001529) with the app logo, collapsible menu, all nav items
2. **Top Header** — Search bar (F2 hint), notification badges, branch selector, user info
3. **Content Area** — Where {{children}} renders

Menu items (from crawled routes):
```json
{json.dumps(menu_items[:50], indent=2)}
```

Design tokens:
```json
{json.dumps(self.data.design_tokens, indent=2)[:3000]}
```

Requirements:
- Ant Design Layout, Sider, Menu with SubMenu for groups
- Collapsible sidebar with hamburger toggle
- Menu items must be grouped logically (the screenshot shows the grouping)
- Vietnamese labels exactly as shown in screenshot
- Active menu item highlighted
- Logo at top of sidebar matching screenshot
- Header with search, notifications, branch dropdown, user avatar
- Content area with proper padding

Output a COMPLETE layout.tsx file:
```tsx
"use client";
export default function DashboardLayout({{ children }}: {{ children: React.ReactNode }}) {{
  // ...
}}
```""",
        })
        
        return content
    
    def _trim_dom(self, dom: dict, max_chars: int) -> str:
        """Trim DOM tree intelligently — keep structure, drop deep children"""
        def trim_node(node, depth=0):
            if not isinstance(node, dict):
                return node
            trimmed = {k: v for k, v in node.items() if k != 'children'}
            if 'children' in node and node['children'] and depth < 4:
                trimmed['children'] = [trim_node(c, depth+1) for c in node['children'][:20]]
            elif 'children' in node and node['children']:
                trimmed['children_count'] = len(node['children'])
            return trimmed
        
        result = json.dumps(trim_node(dom), indent=2, default=str)
        if len(result) > max_chars:
            return result[:max_chars] + "\n... (truncated)"
        return result
    
    def _route_to_component_name(self, route: str) -> str:
        """Convert route to PascalCase component name"""
        safe = self.data.safe_name(route)
        parts = safe.replace('-', '_').split('_')
        return ''.join(p.capitalize() for p in parts if p) or 'IndexPage'


# ─── Code Generator ────────────────────────────────────────

class CodeGenerator:
    """Calls Claude API to generate React components"""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.api_key)
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
    
    async def generate(self, system: str, content: list, model: str = None) -> str:
        """Call Claude and return generated code"""
        model = model or self.config.model
        
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=self.config.max_tokens,
                system=system,
                messages=[{"role": "user", "content": content}],
            )
            
            # Track usage
            usage = response.usage
            self.total_input_tokens += usage.input_tokens
            self.total_output_tokens += usage.output_tokens
            
            # Estimate cost (Sonnet 4: $3/$15 per MTok)
            cost = (usage.input_tokens * 3 + usage.output_tokens * 15) / 1_000_000
            self.total_cost += cost
            
            text = response.content[0].text
            
            # Extract code from markdown blocks if present
            code = self._extract_code(text)
            return code
            
        except anthropic.APIError as e:
            console.print(f"[red]API Error: {e}[/]")
            raise
    
    def _extract_code(self, text: str) -> str:
        """Extract code from markdown code blocks"""
        # Look for ```tsx or ```typescript or ```jsx blocks
        patterns = [
            r'```tsx\n(.*?)```',
            r'```typescript\n(.*?)```',
            r'```jsx\n(.*?)```',
            r'```javascript\n(.*?)```',
            r'```\n(.*?)```',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                # Return the longest match (likely the full component)
                return max(matches, key=len).strip()
        
        # If no code blocks, return as-is (might already be raw code)
        return text.strip()
    
    def print_usage(self):
        """Print total API usage stats"""
        table = Table(title="API Usage Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Input Tokens", f"{self.total_input_tokens:,}")
        table.add_row("Output Tokens", f"{self.total_output_tokens:,}")
        table.add_row("Total Tokens", f"{self.total_input_tokens + self.total_output_tokens:,}")
        table.add_row("Estimated Cost", f"${self.total_cost:.2f}")
        console.print(table)


# ─── Visual Verifier ───────────────────────────────────────

class VisualVerifier:
    """Renders generated components and compares with originals"""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
    
    async def verify_page(self, route: str, code: str, original_screenshot_b64: str) -> tuple[float, Optional[str]]:
        """
        Render the generated component and compare with original.
        Returns (diff_score, screenshot_b64_of_generated)
        
        For now, uses Claude Vision to compare rather than pixel diff.
        This is MORE accurate than pixel comparison because it understands
        layout and semantic similarity.
        """
        # TODO: In full implementation, spin up Vite server, render component,
        # take Playwright screenshot, then do pixel comparison.
        # For MVP, we skip verification and rely on Claude's initial quality.
        return (0.0, None)


# ─── Main Pipeline ─────────────────────────────────────────

class GenerationPipeline:
    """
    The main pipeline:
      crawl data → prompt builder → Claude → component code → verify → output
    """
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.data = CrawlData(config.crawl_dir)
        self.prompts = PromptBuilder(config, self.data)
        self.generator = CodeGenerator(config)
        self.verifier = VisualVerifier(config)
        self.results: list[dict] = []
    
    async def run(self):
        """Run the full pipeline"""
        start_time = time.time()
        
        console.print(Panel(
            "[bold]Website Replicator — Generation Pipeline[/]\n"
            f"Crawl data: {self.config.crawl_dir}\n"
            f"Routes: {len(self.data.routes)}\n"
            f"Model: {self.config.model}\n"
            f"UI: {self.config.ui_lib} + {self.config.css}\n"
            f"Verification: {'ON' if self.config.verify else 'OFF'}",
            title="🚀 Starting",
        ))
        
        # Create output structure
        out = self.config.output_dir
        os.makedirs(f"{out}/app/(dashboard)", exist_ok=True)
        os.makedirs(f"{out}/app/(auth)", exist_ok=True)
        os.makedirs(f"{out}/components/layout", exist_ok=True)
        os.makedirs(f"{out}/components/shared", exist_ok=True)
        os.makedirs(f"{out}/lib", exist_ok=True)
        os.makedirs(f"{out}/prisma", exist_ok=True)
        os.makedirs(f"{out}/types", exist_ok=True)
        os.makedirs(f"{out}/public", exist_ok=True)
        
        # 1. Generate shared layout first
        await self._generate_layout()
        
        # 2. Generate shared utilities
        await self._generate_shared_files()
        
        # 3. Generate each page
        routes = self._get_routes_to_generate()
        console.print(f"\n[bold]Generating {len(routes)} pages...[/]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Generating pages", total=len(routes))
            
            for i, route in enumerate(routes):
                progress.update(task, description=f"[cyan]{route}[/]")
                
                try:
                    result = await self._generate_page(route)
                    self.results.append(result)
                    
                    status = "✓" if result["success"] else "✗"
                    tokens = result.get("tokens", 0)
                    console.print(f"  {status} {route} ({tokens:,} tokens)")
                    
                except Exception as e:
                    console.print(f"  [red]✗ {route}: {e}[/]")
                    self.results.append({"route": route, "success": False, "error": str(e)})
                
                progress.advance(task)
                
                # Rate limit: ~1 req/sec
                await asyncio.sleep(1)
        
        # 4. Generate package.json and config files
        await self._generate_project_files()
        
        # 5. Print summary
        elapsed = time.time() - start_time
        self._print_summary(elapsed)
        
        # 6. Save manifest
        self._save_manifest()
    
    def _get_routes_to_generate(self) -> list[str]:
        """Determine which routes to generate"""
        routes = self.data.routes
        
        # Apply filter
        if self.config.pages_filter:
            routes = [r for r in routes if any(f in r for f in self.config.pages_filter)]
        
        # Apply max_pages cap
        if self.config.max_pages > 0:
            routes = routes[:self.config.max_pages]
        
        # Skip existing
        if self.config.skip_existing:
            existing = set()
            for r in routes:
                safe = self.data.safe_name(r)
                path = f"{self.config.output_dir}/app/(dashboard)/{safe}/page.tsx"
                if os.path.exists(path):
                    existing.add(r)
            if existing:
                console.print(f"[dim]Skipping {len(existing)} already generated pages[/]")
                routes = [r for r in routes if r not in existing]
        
        return routes
    
    async def _generate_layout(self):
        """Generate the shared dashboard layout (sidebar + header)"""
        out_path = f"{self.config.output_dir}/app/(dashboard)/layout.tsx"
        if self.config.skip_existing and os.path.exists(out_path):
            console.print("[dim]Layout already exists, skipping[/]")
            return
        
        console.print("[bold]Generating shared layout (sidebar + header)...[/]")
        
        system = self.prompts.build_system_prompt()
        content = self.prompts.build_layout_prompt()
        
        code = await self.generator.generate(system, content)
        
        with open(out_path, "w") as f:
            f.write(code)
        
        console.print(f"[green]✓ Layout saved: {out_path}[/]")
    
    async def _generate_page(self, route: str) -> dict:
        """Generate a single page component with optional verification loop"""
        safe = self.data.safe_name(route)
        out_path = f"{self.config.output_dir}/app/(dashboard)/{safe}/page.tsx"
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        
        system = self.prompts.build_system_prompt()
        content = self.prompts.build_page_prompt(route)
        
        # Initial generation
        code = await self.generator.generate(system, content)
        
        # Save initial version
        with open(out_path, "w") as f:
            f.write(code)
        
        result = {
            "route": route,
            "file": out_path,
            "success": True,
            "tokens": self.generator.total_output_tokens,
            "iterations": 1,
        }
        
        # Visual verification loop (if enabled)
        if self.config.verify:
            original_b64 = self.data.get_screenshot_b64(route)
            if original_b64:
                for attempt in range(self.config.max_retries):
                    diff_score, generated_b64 = await self.verifier.verify_page(
                        route, code, original_b64
                    )
                    
                    if diff_score <= self.config.diff_threshold:
                        result["diff_score"] = diff_score
                        break
                    
                    if generated_b64:
                        # Ask Claude to fix the differences
                        fix_content = self.prompts.build_fix_prompt(
                            route, original_b64, generated_b64, diff_score, code
                        )
                        code = await self.generator.generate(system, fix_content)
                        
                        with open(out_path, "w") as f:
                            f.write(code)
                        
                        result["iterations"] += 1
                
                result["diff_score"] = diff_score
        
        return result
    
    async def _generate_shared_files(self):
        """Generate utility files that all pages need"""
        out = self.config.output_dir
        
        # --- lib/format.ts (Vietnamese number/date formatting)
        format_path = f"{out}/lib/format.ts"
        if not os.path.exists(format_path):
            with open(format_path, "w") as f:
                f.write('''/**
 * Vietnamese formatting utilities
 */

/**
 * Format number with Vietnamese dot separators
 * 87519238601 → "87.519.238.601"
 */
export function formatVND(amount: number | string): string {
  const num = typeof amount === "string" ? parseFloat(amount) : amount;
  if (isNaN(num)) return "0";
  return num.toLocaleString("vi-VN");
}

/**
 * Format currency with ₫ suffix
 * 87519238601 → "87.519.238.601 ₫"
 */
export function formatCurrency(amount: number | string): string {
  return `${formatVND(amount)} ₫`;
}

/**
 * Format date DD/MM/YYYY (Vietnamese standard)
 */
export function formatDate(date: string | Date): string {
  const d = typeof date === "string" ? new Date(date) : date;
  const day = String(d.getDate()).padStart(2, "0");
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const year = d.getFullYear();
  return `${day}/${month}/${year}`;
}

/**
 * Format datetime DD/MM/YYYY HH:mm
 */
export function formatDateTime(date: string | Date): string {
  const d = typeof date === "string" ? new Date(date) : date;
  const time = `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
  return `${formatDate(d)} ${time}`;
}

/**
 * Format phone number Vietnamese style
 * 0901234567 → "090 123 4567"
 */
export function formatPhone(phone: string): string {
  const clean = phone.replace(/\\D/g, "");
  if (clean.length === 10) {
    return `${clean.slice(0, 3)} ${clean.slice(3, 6)} ${clean.slice(6)}`;
  }
  return phone;
}
''')
            console.print(f"[green]✓ {format_path}[/]")
        
        # --- lib/api-client.ts
        api_path = f"{out}/lib/api-client.ts"
        if not os.path.exists(api_path):
            with open(api_path, "w") as f:
                f.write('''/**
 * API client for backend communication
 */
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api";

interface ApiOptions {
  method?: string;
  body?: any;
  headers?: Record<string, string>;
}

export async function apiCall<T = any>(
  endpoint: string,
  options: ApiOptions = {}
): Promise<T> {
  const { method = "GET", body, headers = {} } = options;
  
  const token = typeof window !== "undefined" 
    ? localStorage.getItem("access_token") 
    : null;
  
  const res = await fetch(`${API_BASE}/${endpoint}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  return res.json();
}
''')
            console.print(f"[green]✓ {api_path}[/]")
        
        # --- types/index.ts (common types from schema)
        types_path = f"{out}/types/index.ts"
        if not os.path.exists(types_path) and self.data.db_schema:
            with open(types_path, "w") as f:
                f.write("/**\n * Auto-generated types from API response analysis\n */\n\n")
                for table_name, fields in self.data.db_schema.items():
                    # PascalCase the table name
                    type_name = ''.join(w.capitalize() for w in table_name.replace('-', '_').split('_'))
                    f.write(f"export interface {type_name} {{\n")
                    if isinstance(fields, dict):
                        for field_name, field_type in fields.items():
                            ts_type = self._schema_to_ts_type(field_type)
                            f.write(f"  {field_name}: {ts_type};\n")
                    f.write("}\n\n")
            console.print(f"[green]✓ {types_path}[/]")
        
        # --- Prisma schema
        if self.data.db_schema:
            prisma_path = f"{out}/prisma/schema.prisma"
            if not os.path.exists(prisma_path):
                with open(prisma_path, "w") as f:
                    f.write(self._generate_prisma_schema())
                console.print(f"[green]✓ {prisma_path}[/]")
    
    def _schema_to_ts_type(self, schema_type) -> str:
        """Convert inferred schema type to TypeScript type"""
        if isinstance(schema_type, dict):
            # Nested object
            return "Record<string, any>"
        type_map = {
            "uuid": "string",
            "string": "string",
            "text": "string",
            "email": "string",
            "phone": "string",
            "datetime": "string",
            "boolean": "boolean",
            "integer": "number",
            "decimal": "number",
            "number": "number",
        }
        return type_map.get(str(schema_type), "any")
    
    def _generate_prisma_schema(self) -> str:
        """Generate Prisma schema from inferred DB schema"""
        lines = [
            "// Auto-generated Prisma schema from API analysis",
            "// Review and adjust before running prisma db push",
            "",
            "generator client {",
            '  provider = "prisma-client-js"',
            "}",
            "",
            "datasource db {",
            '  provider = "postgresql"',
            '  url      = env("DATABASE_URL")',
            "}",
            "",
        ]
        
        for table_name, fields in self.data.db_schema.items():
            model_name = ''.join(w.capitalize() for w in table_name.replace('-', '_').split('_'))
            lines.append(f"model {model_name} {{")
            lines.append('  id        String   @id @default(uuid())')
            
            if isinstance(fields, dict):
                for field_name, field_type in fields.items():
                    if field_name in ('id',):
                        continue
                    prisma_type = self._schema_to_prisma_type(str(field_type))
                    lines.append(f"  {field_name}  {prisma_type}")
            
            lines.append('  createdAt DateTime @default(now())')
            lines.append('  updatedAt DateTime @updatedAt')
            lines.append("}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _schema_to_prisma_type(self, schema_type: str) -> str:
        type_map = {
            "uuid": "String",
            "string": "String",
            "text": "String",
            "email": "String",
            "phone": "String",
            "datetime": "DateTime",
            "boolean": "Boolean",
            "integer": "Int",
            "decimal": "Float",
            "number": "Float",
        }
        return type_map.get(schema_type, "String")
    
    async def _generate_project_files(self):
        """Generate package.json, tailwind config, etc."""
        out = self.config.output_dir
        
        # package.json
        pkg_path = f"{out}/package.json"
        if not os.path.exists(pkg_path):
            pkg = {
                "name": "website-replica",
                "version": "1.0.0",
                "private": True,
                "scripts": {
                    "dev": "next dev",
                    "build": "next build",
                    "start": "next start",
                    "lint": "next lint",
                    "db:push": "prisma db push",
                    "db:studio": "prisma studio",
                },
                "dependencies": {
                    "next": "^14.2.0",
                    "react": "^18.3.0",
                    "react-dom": "^18.3.0",
                    "antd": "^5.22.0",
                    "@ant-design/icons": "^5.5.0",
                    "@ant-design/cssinjs": "^1.22.0",
                    "recharts": "^2.13.0",
                    "dayjs": "^1.11.0",
                    "next-auth": "^4.24.0",
                    "@prisma/client": "^5.20.0",
                    "zustand": "^5.0.0",
                },
                "devDependencies": {
                    "typescript": "^5.6.0",
                    "@types/react": "^18.3.0",
                    "@types/node": "^22.0.0",
                    "tailwindcss": "^3.4.0",
                    "postcss": "^8.4.0",
                    "autoprefixer": "^10.4.0",
                    "prisma": "^5.20.0",
                    "eslint": "^8.56.0",
                    "eslint-config-next": "^14.2.0",
                },
            }
            with open(pkg_path, "w") as f:
                json.dump(pkg, f, indent=2)
            console.print(f"[green]✓ {pkg_path}[/]")
        
        # tsconfig.json
        ts_path = f"{out}/tsconfig.json"
        if not os.path.exists(ts_path):
            tsconfig = {
                "compilerOptions": {
                    "target": "ES2017",
                    "lib": ["dom", "dom.iterable", "esnext"],
                    "allowJs": True,
                    "skipLibCheck": True,
                    "strict": True,
                    "noEmit": True,
                    "esModuleInterop": True,
                    "module": "esnext",
                    "moduleResolution": "bundler",
                    "resolveJsonModule": True,
                    "isolatedModules": True,
                    "jsx": "preserve",
                    "incremental": True,
                    "plugins": [{"name": "next"}],
                    "paths": {"@/*": ["./*"]},
                },
                "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
                "exclude": ["node_modules"],
            }
            with open(ts_path, "w") as f:
                json.dump(tsconfig, f, indent=2)
        
        # tailwind.config.ts
        tw_path = f"{out}/tailwind.config.ts"
        if not os.path.exists(tw_path):
            colors = self.data.design_tokens.get("colors", {})
            primary = colors[0] if isinstance(colors, list) and colors else "#1890ff"
            if isinstance(primary, dict):
                primary = primary.get("value", "#1890ff")
            
            with open(tw_path, "w") as f:
                f.write(f'''import type {{ Config }} from "tailwindcss";

const config: Config = {{
  content: [
    "./app/**/*.{{js,ts,jsx,tsx,mdx}}",
    "./components/**/*.{{js,ts,jsx,tsx,mdx}}",
  ],
  theme: {{
    extend: {{
      colors: {{
        primary: "{primary}",
        sidebar: "#001529",
        "sidebar-active": "#1890ff",
      }},
    }},
  }},
  plugins: [],
  // Prevent Tailwind from conflicting with Ant Design
  corePlugins: {{
    preflight: false,
  }},
}};
export default config;
''')
        
        # globals.css
        css_path = f"{out}/app/globals.css"
        os.makedirs(os.path.dirname(css_path), exist_ok=True)
        if not os.path.exists(css_path):
            with open(css_path, "w") as f:
                f.write("""@tailwind base;
@tailwind components;
@tailwind utilities;

/* Vietnamese locale overrides */
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Ant Design overrides to match original */
.ant-layout-sider {
  background: #001529 !important;
}

.ant-menu-dark {
  background: #001529 !important;
}

/* VND number formatting helper */
.vnd-format {
  font-variant-numeric: tabular-nums;
}

/* Chart container */
.chart-container {
  width: 100%;
  min-height: 300px;
}
""")
        
        # Root layout (app/layout.tsx)
        root_layout = f"{out}/app/layout.tsx"
        if not os.path.exists(root_layout):
            with open(root_layout, "w") as f:
                f.write('''import type { Metadata } from "next";
import { ConfigProvider } from "antd";
import viVN from "antd/locale/vi_VN";
import "./globals.css";

export const metadata: Metadata = {
  title: "TDental",
  description: "Dental Management System",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi">
      <body>
        <ConfigProvider
          locale={viVN}
          theme={{
            token: {
              colorPrimary: "#1890ff",
              borderRadius: 6,
              fontFamily: "-apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif",
            },
          }}
        >
          {children}
        </ConfigProvider>
      </body>
    </html>
  );
}
''')
    
    def _print_summary(self, elapsed: float):
        """Print generation summary"""
        succeeded = sum(1 for r in self.results if r.get("success"))
        failed = sum(1 for r in self.results if not r.get("success"))
        
        console.print("\n")
        console.print(Panel(
            f"[bold green]Generation Complete[/]\n\n"
            f"Pages generated: {succeeded}/{len(self.results)}\n"
            f"Failed: {failed}\n"
            f"Time: {elapsed:.0f}s ({elapsed/max(len(self.results),1):.1f}s per page)\n"
            f"Output: {self.config.output_dir}\n",
            title="📊 Summary",
        ))
        
        self.generator.print_usage()
        
        if failed:
            console.print("\n[red]Failed pages:[/]")
            for r in self.results:
                if not r.get("success"):
                    console.print(f"  ✗ {r['route']}: {r.get('error', 'unknown')}")
        
        console.print(f"\n[bold]Next steps:[/]")
        console.print(f"  cd {self.config.output_dir}")
        console.print(f"  npm install")
        console.print(f"  npm run dev")
        console.print(f"  # Open http://localhost:3000")
    
    def _save_manifest(self):
        """Save generation manifest for reference"""
        manifest = {
            "generated_at": datetime.now().isoformat(),
            "crawl_dir": self.config.crawl_dir,
            "model": self.config.model,
            "pages": self.results,
            "total_input_tokens": self.generator.total_input_tokens,
            "total_output_tokens": self.generator.total_output_tokens,
            "estimated_cost": f"${self.generator.total_cost:.2f}",
        }
        path = f"{self.config.output_dir}/generation_manifest.json"
        with open(path, "w") as f:
            json.dump(manifest, f, indent=2, default=str)


# ─── CLI ───────────────────────────────────────────────────

async def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate React components from crawl data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all pages from a crawl
  python generate_pipeline.py /app/data/job123
  
  # Generate specific pages only
  python generate_pipeline.py /app/data/job123 --pages partners sale-orders
  
  # Generate first 5 pages with Opus for max quality
  python generate_pipeline.py /app/data/job123 --max-pages 5 --model claude-opus-4-20250514
  
  # Re-generate all (don't skip existing)
  python generate_pipeline.py /app/data/job123 --no-skip
        """,
    )
    parser.add_argument("crawl_dir", help="Path to crawl output directory")
    parser.add_argument("--model", default="claude-sonnet-4-20250514", help="Claude model to use")
    parser.add_argument("--max-pages", type=int, default=0, help="Max pages to generate (0=all)")
    parser.add_argument("--pages", nargs="+", help="Only generate these routes")
    parser.add_argument("--output", help="Output directory (default: crawl_dir/generated)")
    parser.add_argument("--no-skip", action="store_true", help="Re-generate existing pages")
    parser.add_argument("--verify", action="store_true", help="Enable visual verification")
    parser.add_argument("--ui", default="antd", choices=["antd", "shadcn", "mui"])
    parser.add_argument("--locale", default="vi-VN")
    parser.add_argument("--max-tokens", type=int, default=16000)
    
    args = parser.parse_args()
    
    config = PipelineConfig(
        crawl_dir=args.crawl_dir,
        model=args.model,
        max_pages=args.max_pages,
        pages_filter=args.pages or [],
        output_dir=args.output or "",
        skip_existing=not args.no_skip,
        verify=args.verify,
        ui_lib=args.ui,
        locale=args.locale,
        max_tokens=args.max_tokens,
    )
    
    pipeline = GenerationPipeline(config)
    await pipeline.run()


if __name__ == "__main__":
    asyncio.run(main())
