"""
Website Replicator — Core Crawl Engine

Combines Playwright + stealth + HAR recording to:
1. Login to any website (form, API, cookie-based)
2. Discover all routes (JS bundle parsing + link crawling + menu clicking)
3. Visit every route and extract:
   - Full-page screenshots
   - DOM tree with computed styles
   - Hover state diffs
   - CSS animations & keyframes
   - API calls with full request/response bodies (via HAR)
4. Infer database schema from API responses
5. Extract design tokens (colors, typography, spacing)
"""
import asyncio
import json
import os
import re
from datetime import datetime
from typing import Optional

from playwright.async_api import async_playwright, Page, BrowserContext, Response
from rich.console import Console

console = Console()


class SiteReplicator:
    """The main brain — navigates websites and extracts everything."""

    def __init__(self, config, output_dir: str, status):
        self.config = config
        self.output_dir = output_dir
        self.status = status
        self.api_calls: list[dict] = []
        self.routes: set[str] = set()
        self.visited: set[str] = set()
        self.base_url = config.site_url.rstrip("/")

        # Create output directories
        for subdir in ["screenshots", "dom", "har", "assets", "hover", "animations"]:
            os.makedirs(f"{output_dir}/{subdir}", exist_ok=True)

    async def run(self):
        """Main execution flow"""
        console.print("[bold green]🚀 Starting Website Replicator...[/]")

        async with async_playwright() as pw:
            # Launch browser — VISIBLE via noVNC when headless=False
            browser = await pw.chromium.launch(
                headless=self.config.headless,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--window-size=1920,1080",
                ],
            )

            # Create context with HAR recording
            har_path = f"{self.output_dir}/har/full_recording.har"
            context = await browser.new_context(
                viewport={"width": self.config.viewport_width, "height": self.config.viewport_height},
                locale=self.config.locale,
                timezone_id=self.config.timezone,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                record_har_path=har_path if self.config.record_har else None,
                record_har_content="attach" if self.config.record_har else None,
                java_script_enabled=True,
                ignore_https_errors=True,
            )

            # Apply stealth
            await self._apply_stealth(context)

            # Intercept API responses in real-time
            context.on("response", self._on_response)

            page = await context.new_page()

            # ── PHASE 1: LOGIN ──
            console.print("\n[bold cyan]📋 Phase 1: Authentication[/]")
            self.status.current_page = "Logging in..."
            await self._login(page)
            console.print("[green]  ✓ Logged in successfully[/]")

            # ── PHASE 2: DISCOVER ROUTES ──
            console.print("\n[bold cyan]🔍 Phase 2: Route Discovery[/]")
            self.status.current_page = "Discovering routes..."
            await self._discover_routes(page)
            self.status.total_routes = len(self.routes)
            console.print(f"[green]  ✓ Found {len(self.routes)} routes[/]")

            # Save routes
            with open(f"{self.output_dir}/routes.json", "w") as f:
                json.dump(sorted(self.routes), f, indent=2)

            # ── PHASE 3: CRAWL EVERY ROUTE ──
            console.print(f"\n[bold cyan]🕷️  Phase 3: Crawling {len(self.routes)} pages[/]")
            for i, route in enumerate(sorted(self.routes)):
                if self.status.status == "stopped":
                    break
                if route in self.visited:
                    continue

                progress = f"[{i+1}/{len(self.routes)}]"
                self.status.current_page = route
                console.print(f"  {progress} {route}", end="")

                try:
                    await self._process_route(page, route)
                    self.visited.add(route)
                    self.status.pages_crawled += 1
                    console.print(" [green]✓[/]")
                except Exception as e:
                    self.status.errors.append(f"{route}: {str(e)}")
                    console.print(f" [red]✗ {e}[/]")

            # ── PHASE 4: POST-PROCESSING ──
            console.print("\n[bold cyan]🧠 Phase 4: Analysis[/]")

            self.status.current_page = "Analyzing API calls..."
            self._analyze_api_calls()
            console.print(f"[green]  ✓ Mapped {len(self.api_calls)} API calls[/]")

            self.status.current_page = "Extracting design tokens..."
            await self._extract_design_tokens(page)
            console.print("[green]  ✓ Design tokens extracted[/]")

            # Save stats
            stats = {
                "pages_crawled": self.status.pages_crawled,
                "total_routes": self.status.total_routes,
                "api_calls_captured": len(self.api_calls),
                "screenshots_taken": self.status.screenshots_taken,
                "errors": self.status.errors,
                "completed_at": datetime.now().isoformat(),
            }
            with open(f"{self.output_dir}/stats.json", "w") as f:
                json.dump(stats, f, indent=2)

            # Close context (flushes HAR to disk)
            await context.close()
            await browser.close()

            console.print(f"\n[bold green]🎉 Crawl complete! {self.status.pages_crawled} pages, {len(self.api_calls)} API calls captured.[/]")
            console.print(f"[dim]Results saved to {self.output_dir}[/]")

    # ════════════════════════════════════════════
    # STEALTH
    # ════════════════════════════════════════════

    async def _apply_stealth(self, context: BrowserContext):
        """Apply stealth patches to avoid bot detection"""
        await context.add_init_script("""
            // Remove webdriver flag
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            
            // Fake plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Fake languages  
            Object.defineProperty(navigator, 'languages', {
                get: () => ['vi-VN', 'vi', 'en-US', 'en'],
            });
            
            // Remove Chrome automation indicators
            window.chrome = { runtime: {} };
            
            // Permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) =>
                parameters.name === 'notifications'
                    ? Promise.resolve({ state: Notification.permission })
                    : originalQuery(parameters);
        """)

    # ════════════════════════════════════════════
    # AUTHENTICATION
    # ════════════════════════════════════════════

    async def _login(self, page: Page):
        """Handle login — supports API token, form-based, and cookie injection"""
        if self.config.auth_type == "none":
            await page.goto(self.base_url, wait_until="networkidle")
            return

        if self.config.auth_type == "api" and self.config.api_login_endpoint:
            await self._api_login(page)
        elif self.config.auth_type == "form":
            await self._form_login(page)
        elif self.config.auth_type == "cookie":
            # Cookie injection — user provides cookies in config
            await page.goto(self.base_url)
        
        # Wait for app to settle after login
        await page.wait_for_timeout(2000)

    async def _api_login(self, page: Page):
        """Login via API endpoint (JWT pattern — like TDental)"""
        endpoint = f"{self.base_url}/{self.config.api_login_endpoint.lstrip('/')}"
        console.print(f"  → API login: {endpoint}")

        # Make the API call
        response = await page.request.post(
            endpoint,
            data=json.dumps({
                "username": self.config.username,
                "password": self.config.password,
                "userName": self.config.username,   # Some APIs use camelCase
                "passWord": self.config.password,
            }),
            headers={"Content-Type": "application/json"},
        )

        data = await response.json()
        console.print(f"  → Login response status: {response.status}")

        # Navigate to site first
        await page.goto(self.base_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(1000)

        # Find token in response (check common keys)
        token = None
        for key in ["access_token", "accessToken", "token", "jwt", "Token", "AccessToken"]:
            if key in data:
                token = data[key]
                break
            if isinstance(data, dict) and "result" in data and isinstance(data["result"], dict):
                if key in data["result"]:
                    token = data["result"][key]
                    break

        if token:
            console.print(f"  → Token found, injecting into localStorage...")
            await page.evaluate(f"""() => {{
                localStorage.setItem('access_token', '{token}');
                localStorage.setItem('token', '{token}');
                localStorage.setItem('accessToken', '{token}');
                sessionStorage.setItem('access_token', '{token}');
                sessionStorage.setItem('token', '{token}');
            }}""")
            await page.reload(wait_until="networkidle")
        else:
            console.print("[yellow]  ⚠ No token found in response, trying cookie-based auth...[/]")

    async def _form_login(self, page: Page):
        """Login via HTML form (find inputs, fill, submit)"""
        login_url = f"{self.base_url}{self.config.login_url}" if self.config.login_url else self.base_url
        console.print(f"  → Form login: {login_url}")
        
        await page.goto(login_url, wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # Find username field
        username_selectors = [
            'input[type="email"]', 'input[type="text"]',
            'input[name*="user" i]', 'input[name*="login" i]',
            'input[name*="email" i]', 'input[id*="user" i]',
            'input[placeholder*="user" i]', 'input[placeholder*="email" i]',
            'input[placeholder*="tên" i]',  # Vietnamese
        ]
        for sel in username_selectors:
            field = await page.query_selector(sel)
            if field and await field.is_visible():
                await field.fill(self.config.username)
                break

        # Find password field
        pw_field = await page.query_selector('input[type="password"]')
        if pw_field:
            await pw_field.fill(self.config.password)

        # Find and click submit
        submit_selectors = [
            'button[type="submit"]', 'input[type="submit"]',
            'button:has-text("Login")', 'button:has-text("Sign in")',
            'button:has-text("Đăng nhập")', 'button:has-text("Log in")',
            '.login-button', '#login-btn',
        ]
        for sel in submit_selectors:
            btn = await page.query_selector(sel)
            if btn and await btn.is_visible():
                await btn.click()
                break

        await page.wait_for_load_state("networkidle")

    # ════════════════════════════════════════════
    # ROUTE DISCOVERY
    # ════════════════════════════════════════════

    async def _discover_routes(self, page: Page):
        """Find all navigable routes in the SPA"""
        # Method 1: Parse JS bundles for router configs
        js_routes = await page.evaluate("""() => {
            const routes = new Set();
            const html = document.documentElement.innerHTML;
            
            // Angular/React/Vue route patterns in JS
            const patterns = [
                /path\\s*:\\s*['"]([^'"]+)['"]/g,
                /routerLink\\s*=\\s*["']([^"']+)["']/g,
                /navigate\\s*\\(\\s*\\[\\s*['"]([^'"]+)/g,
                /to\\s*=\\s*["']([^"']+)["']/g,
                /href\\s*=\\s*["']#?\\/([^"']+)["']/g,
                /component\\s*:\\s*\\w+.*?path\\s*:\\s*['"]([^'"]+)/g,
            ];
            
            for (const pattern of patterns) {
                let match;
                while ((match = pattern.exec(html)) !== null) {
                    let route = match[1].trim();
                    if (route && !route.startsWith('http') && !route.startsWith('//') 
                        && !route.includes('{{') && route.length < 200) {
                        if (!route.startsWith('/') && !route.startsWith('#')) {
                            route = '/' + route;
                        }
                        routes.add(route);
                    }
                }
            }
            
            // Grab all visible links with hash routes
            document.querySelectorAll('a[href]').forEach(a => {
                const href = a.getAttribute('href');
                if (href && (href.includes('#/') || href.startsWith('/'))) {
                    routes.add(href);
                }
            });
            
            return [...routes].filter(r => r.length > 1);
        }""")
        self.routes.update(js_routes)
        console.print(f"  → JS parsing found {len(js_routes)} routes")

        # Method 2: Click through sidebar/menu to find more
        menu_selectors = [
            '.ant-menu-item', '.ant-menu-submenu-title',
            'nav a', '.sidebar a', '.menu a', '.nav-item a',
            '[routerlink]', '[ng-reflect-router-link]',
            '.tds-menu-item', 'li.menu-item a',
        ]
        
        before = len(self.routes)
        for sel in menu_selectors:
            items = await page.query_selector_all(sel)
            for item in items:
                try:
                    href = await item.get_attribute("href")
                    rlink = await item.get_attribute("routerlink") or await item.get_attribute("ng-reflect-router-link")
                    if href:
                        self.routes.add(href)
                    if rlink:
                        self.routes.add(f"/{rlink.lstrip('/')}")
                except:
                    pass
        console.print(f"  → Menu scanning found {len(self.routes) - before} more routes")

        # Method 3: Expand all collapsed submenus
        submenu_selectors = [
            '.ant-menu-submenu-title', '.submenu-toggle',
            '[data-toggle="collapse"]', '.menu-toggle',
            '.ant-menu-submenu:not(.ant-menu-submenu-open) > .ant-menu-submenu-title',
        ]
        for sel in submenu_selectors:
            items = await page.query_selector_all(sel)
            for item in items:
                try:
                    if await item.is_visible():
                        await item.click()
                        await page.wait_for_timeout(400)
                except:
                    pass
        
        # Re-scan after expanding
        after_expand = len(self.routes)
        all_links = await page.query_selector_all('a[href]')
        for link in all_links:
            try:
                href = await link.get_attribute("href")
                if href and (href.startswith("/") or href.startswith("#")):
                    self.routes.add(href)
            except:
                pass
        console.print(f"  → Submenu expansion found {len(self.routes) - after_expand} more routes")

        # Filter out garbage routes
        self.routes = {
            r for r in self.routes
            if not any(x in r.lower() for x in ["logout", "signout", ".js", ".css", ".png", ".jpg", "javascript:", "mailto:"])
            and len(r) < 300
        }

    # ════════════════════════════════════════════
    # PAGE PROCESSING
    # ════════════════════════════════════════════

    async def _process_route(self, page: Page, route: str):
        """Visit a route and extract everything"""
        # Navigate
        if route.startswith("http"):
            url = route
        elif route.startswith("#"):
            url = f"{self.base_url}/{route}"
        else:
            url = f"{self.base_url}{route}"

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
        except Exception:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

        await page.wait_for_timeout(self.config.wait_after_nav_ms)

        # Safe filename from route
        safe = re.sub(r'[^a-zA-Z0-9_-]', '_', route.strip('/').replace('#', ''))[:80] or "index"

        # 1. SCREENSHOT
        if self.config.capture_screenshots:
            try:
                await page.screenshot(
                    path=f"{self.output_dir}/screenshots/{safe}.png",
                    full_page=True,
                    timeout=15000,
                )
                self.status.screenshots_taken += 1
            except:
                pass

        # 2. DOM + COMPUTED STYLES
        dom = await self._extract_dom(page)
        with open(f"{self.output_dir}/dom/{safe}.json", "w") as f:
            json.dump(dom, f, indent=2, default=str)

        # 3. HOVER STATES
        if self.config.capture_hover_states:
            hovers = await self._capture_hover_states(page)
            if hovers:
                with open(f"{self.output_dir}/hover/{safe}.json", "w") as f:
                    json.dump(hovers, f, indent=2)

        # 4. ANIMATIONS
        if self.config.capture_animations:
            anims = await self._capture_animations(page)
            if anims and (anims.get("keyframes") or anims.get("animated_elements")):
                with open(f"{self.output_dir}/animations/{safe}.json", "w") as f:
                    json.dump(anims, f, indent=2)

    async def _extract_dom(self, page: Page) -> dict:
        """Extract complete DOM tree with computed styles"""
        return await page.evaluate("""() => {
            function extract(el, depth) {
                if (depth > 8) return null;
                const rect = el.getBoundingClientRect();
                if (rect.width === 0 && rect.height === 0) return null;
                
                const cs = window.getComputedStyle(el);
                const children = [];
                for (const child of el.children) {
                    const e = extract(child, depth + 1);
                    if (e) children.push(e);
                }
                
                return {
                    tag: el.tagName.toLowerCase(),
                    id: el.id || undefined,
                    cls: [...el.classList].join(' ') || undefined,
                    text: (el.childNodes.length === 1 && el.childNodes[0].nodeType === 3)
                        ? el.textContent.trim().substring(0, 200) : undefined,
                    rect: { x: Math.round(rect.x), y: Math.round(rect.y), 
                            w: Math.round(rect.width), h: Math.round(rect.height) },
                    attrs: Object.fromEntries(
                        [...el.attributes]
                            .filter(a => ['type','placeholder','role','aria-label','name','href','src','alt','for'].includes(a.name))
                            .map(a => [a.name, a.value])
                    ),
                    style: {
                        display: cs.display, position: cs.position,
                        flexDir: cs.flexDirection !== 'row' ? cs.flexDirection : undefined,
                        justify: cs.justifyContent !== 'normal' ? cs.justifyContent : undefined,
                        align: cs.alignItems !== 'normal' ? cs.alignItems : undefined,
                        gap: cs.gap !== 'normal' ? cs.gap : undefined,
                        grid: cs.gridTemplateColumns !== 'none' ? cs.gridTemplateColumns : undefined,
                        w: cs.width, h: cs.height,
                        p: cs.padding !== '0px' ? cs.padding : undefined,
                        m: cs.margin !== '0px' ? cs.margin : undefined,
                        bg: cs.backgroundColor !== 'rgba(0, 0, 0, 0)' ? cs.backgroundColor : undefined,
                        color: cs.color,
                        fontSize: cs.fontSize,
                        fontWeight: cs.fontWeight !== '400' ? cs.fontWeight : undefined,
                        fontFamily: cs.fontFamily.split(',')[0].trim().replace(/['"]/g,''),
                        radius: cs.borderRadius !== '0px' ? cs.borderRadius : undefined,
                        shadow: cs.boxShadow !== 'none' ? cs.boxShadow : undefined,
                        border: cs.border !== '0px none rgb(0, 0, 0)' ? cs.border : undefined,
                        overflow: cs.overflow !== 'visible' ? cs.overflow : undefined,
                        transition: cs.transition !== 'all 0s ease 0s' ? cs.transition : undefined,
                        cursor: cs.cursor !== 'auto' ? cs.cursor : undefined,
                    },
                    interactive: ['BUTTON','A','INPUT','SELECT','TEXTAREA'].includes(el.tagName),
                    children: children.length ? children : undefined,
                };
            }
            return {
                title: document.title,
                url: window.location.href,
                viewport: { w: window.innerWidth, h: window.innerHeight },
                body: extract(document.body, 0),
            };
        }""")

    async def _capture_hover_states(self, page: Page) -> list:
        """Detect style changes on hover for interactive elements"""
        return await page.evaluate("""async () => {
            const changes = [];
            const els = document.querySelectorAll(
                'button, a, tr, .card, [role="button"], .ant-btn, .ant-menu-item, .ant-table-row'
            );
            for (const el of [...els].slice(0, 40)) {
                try {
                    const before = window.getComputedStyle(el);
                    const snap1 = { bg: before.backgroundColor, color: before.color, 
                                    transform: before.transform, shadow: before.boxShadow };
                    
                    el.dispatchEvent(new MouseEvent('mouseenter', {bubbles:true}));
                    await new Promise(r => setTimeout(r, 200));
                    
                    const after = window.getComputedStyle(el);
                    const snap2 = { bg: after.backgroundColor, color: after.color,
                                    transform: after.transform, shadow: after.boxShadow };
                    
                    el.dispatchEvent(new MouseEvent('mouseleave', {bubbles:true}));
                    
                    if (JSON.stringify(snap1) !== JSON.stringify(snap2)) {
                        changes.push({
                            selector: el.tagName + (el.className ? '.' + [...el.classList].join('.') : ''),
                            text: el.textContent?.trim().substring(0, 50),
                            normal: snap1, hover: snap2,
                        });
                    }
                } catch(e) {}
            }
            return changes;
        }""")

    async def _capture_animations(self, page: Page) -> dict:
        """Extract CSS keyframes and animated elements"""
        return await page.evaluate("""() => {
            const result = { keyframes: [], animated_elements: [] };
            for (const sheet of document.styleSheets) {
                try {
                    for (const rule of sheet.cssRules) {
                        if (rule instanceof CSSKeyframesRule) {
                            const frames = [];
                            for (const kf of rule.cssRules) {
                                frames.push({ key: kf.keyText, css: kf.style.cssText });
                            }
                            result.keyframes.push({ name: rule.name, frames });
                        }
                    }
                } catch(e) {}
            }
            document.querySelectorAll('*').forEach(el => {
                const s = window.getComputedStyle(el);
                if ((s.animation && s.animation !== 'none') || 
                    (s.transition && s.transition !== 'all 0s ease 0s' && s.transition !== 'none 0s ease 0s')) {
                    result.animated_elements.push({
                        tag: el.tagName, cls: el.className?.toString().substring(0,100),
                        animation: s.animation !== 'none' ? s.animation : undefined,
                        transition: s.transition !== 'all 0s ease 0s' ? s.transition : undefined,
                    });
                }
            });
            return result;
        }""")

    # ════════════════════════════════════════════
    # API CAPTURE & ANALYSIS
    # ════════════════════════════════════════════

    async def _on_response(self, response: Response):
        """Capture API responses in real-time as the browser navigates"""
        url = response.url
        # Only capture API calls, not static assets
        if any(x in url for x in ["/api/", "/Web/", "/graphql", "/rest/", "/v1/", "/v2/"]):
            try:
                content_type = response.headers.get("content-type", "")
                if "json" in content_type or "text" in content_type:
                    body = await response.json()
                    self.api_calls.append({
                        "url": url,
                        "method": response.request.method,
                        "status": response.status,
                        "request_headers": dict(response.request.headers) if response.request.headers else {},
                        "response_body": body,
                        "timestamp": datetime.now().isoformat(),
                    })
                    self.status.api_calls_captured = len(self.api_calls)
            except:
                pass  # Binary or non-JSON response

    def _analyze_api_calls(self):
        """Group API calls by controller and infer database schema"""
        controllers = {}
        schemas = {}

        for call in self.api_calls:
            # Extract controller: "api/Partners/GetPaged" → "Partners"
            url = call["url"]
            path = ""
            for prefix in ["/api/", "/Web/", "/rest/", "/v1/", "/v2/"]:
                if prefix in url:
                    path = url.split(prefix)[-1].split("?")[0]
                    break
            
            parts = path.split("/")
            controller = parts[0] if parts else "unknown"
            action = "/".join(parts[1:]) if len(parts) > 1 else "index"

            if controller not in controllers:
                controllers[controller] = []

            controllers[controller].append({
                "method": call["method"],
                "action": action,
                "full_url": call["url"],
                "status": call["status"],
            })

            # Infer schema from response body
            body = call.get("response_body")
            if body and controller not in schemas:
                sample = None
                if isinstance(body, dict):
                    # Common patterns: {items: [...]}, {result: [...]}, {data: [...]}
                    for key in ["items", "result", "data", "records", "list", "results"]:
                        if key in body and isinstance(body[key], list) and body[key]:
                            if isinstance(body[key][0], dict):
                                sample = body[key][0]
                                break
                    if not sample and "id" in body:
                        sample = body
                elif isinstance(body, list) and body and isinstance(body[0], dict):
                    sample = body[0]

                if sample:
                    schemas[controller] = self._infer_schema(sample)

        with open(f"{self.output_dir}/api_map.json", "w") as f:
            json.dump(controllers, f, indent=2, default=str)

        with open(f"{self.output_dir}/db_schema.json", "w") as f:
            json.dump(schemas, f, indent=2)

        # Also save raw API calls for HAR→Swagger later
        with open(f"{self.output_dir}/api_calls_raw.json", "w") as f:
            json.dump(self.api_calls, f, indent=2, default=str)

    def _infer_schema(self, obj: dict, depth: int = 0) -> dict:
        """Infer field types from a JSON object"""
        if not isinstance(obj, dict) or depth > 3:
            return {"_type": "json"}

        schema = {}
        for key, val in obj.items():
            if val is None:
                schema[key] = "string?"
            elif isinstance(val, bool):
                schema[key] = "boolean"
            elif isinstance(val, int):
                schema[key] = "integer"
            elif isinstance(val, float):
                schema[key] = "decimal"
            elif isinstance(val, str):
                v = val.strip()
                if len(v) == 36 and v.count("-") == 4:
                    schema[key] = "uuid"
                elif re.match(r"\d{4}-\d{2}-\d{2}", v):
                    schema[key] = "datetime"
                elif "@" in v and "." in v:
                    schema[key] = "email"
                elif re.match(r"^\+?\d[\d\s-]{6,}$", v):
                    schema[key] = "phone"
                elif len(v) > 500:
                    schema[key] = "text"
                else:
                    schema[key] = "string"
            elif isinstance(val, list):
                if val and isinstance(val[0], dict):
                    schema[key] = {"_type": "array", "_items": self._infer_schema(val[0], depth + 1)}
                else:
                    schema[key] = "array"
            elif isinstance(val, dict):
                schema[key] = self._infer_schema(val, depth + 1)
        return schema

    # ════════════════════════════════════════════
    # DESIGN TOKENS
    # ════════════════════════════════════════════

    async def _extract_design_tokens(self, page: Page):
        """Extract color palette, typography, spacing system"""
        tokens = await page.evaluate("""() => {
            const colors = new Map();
            const fonts = new Set();
            const sizes = new Set();
            const spaces = new Set();
            const radii = new Set();
            const shadows = new Set();
            
            document.querySelectorAll('*').forEach(el => {
                const s = window.getComputedStyle(el);
                
                // Colors (with frequency count)
                [s.backgroundColor, s.color, s.borderColor].forEach(c => {
                    if (c && c !== 'rgba(0, 0, 0, 0)' && c !== 'transparent') {
                        colors.set(c, (colors.get(c) || 0) + 1);
                    }
                });
                
                // Fonts
                const font = s.fontFamily.split(',')[0].trim().replace(/['"]/g, '');
                if (font) fonts.add(font);
                
                // Font sizes
                sizes.add(s.fontSize);
                
                // Spacing
                ['padding', 'margin', 'gap'].forEach(prop => {
                    const v = s.getPropertyValue(prop);
                    if (v && v !== '0px' && v !== 'normal') spaces.add(v);
                });
                
                // Border radius
                if (s.borderRadius && s.borderRadius !== '0px') radii.add(s.borderRadius);
                
                // Box shadow
                if (s.boxShadow && s.boxShadow !== 'none') shadows.add(s.boxShadow);
            });
            
            // Sort colors by frequency
            const sortedColors = [...colors.entries()]
                .sort((a, b) => b[1] - a[1])
                .slice(0, 30)
                .map(([color, count]) => ({ color, count }));
            
            return {
                colors: sortedColors,
                fonts: [...fonts].slice(0, 10),
                fontSizes: [...sizes].sort(),
                spacing: [...spaces].sort().slice(0, 20),
                borderRadii: [...radii],
                boxShadows: [...shadows].slice(0, 10),
            };
        }""")

        with open(f"{self.output_dir}/design_tokens.json", "w") as f:
            json.dump(tokens, f, indent=2)
