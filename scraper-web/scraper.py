"""
SPA Web Scraper - Automated SPA reverse engineering tool
Uses Playwright headless browser to:
1. Login to SPAs
2. Discover all routes/navigation
3. Capture all API network traffic
4. Extract DOM structure per page
5. Capture screenshots of every page
"""

import asyncio
import json
import os
import re
import time
from datetime import datetime
from urllib.parse import urlparse, urljoin
from playwright.async_api import async_playwright, Page, BrowserContext

class SPAScraper:
    def __init__(self, config):
        self.config = config
        self.base_url = config['base_url']
        self.output_dir = config.get('output_dir', './scrape_output')
        self.api_calls = []
        self.discovered_routes = set()
        self.visited_routes = set()
        self.page_data = {}
        self.forms_found = []
        self.tables_found = []
        self.components_found = []
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/screenshots", exist_ok=True)
        os.makedirs(f"{self.output_dir}/api_responses", exist_ok=True)
        os.makedirs(f"{self.output_dir}/dom_snapshots", exist_ok=True)

    async def start(self):
        """Main entry point"""
        print(f"\n{'='*60}")
        print(f"  SPA SCRAPER - {self.base_url}")
        print(f"  Started: {datetime.now().isoformat()}")
        print(f"{'='*60}\n")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = await context.new_page()
            
            # Setup network interception
            await self._setup_network_capture(page)
            
            # Step 1: Login
            print("[1/5] Logging in...")
            logged_in = await self._login(page)
            if not logged_in:
                print("❌ Login failed!")
                await browser.close()
                return
            print("✅ Login successful!")
            
            # Step 2: Discover routes from navigation/sidebar
            print("\n[2/5] Discovering routes...")
            await self._discover_routes(page)
            print(f"✅ Found {len(self.discovered_routes)} routes")
            
            # Step 3: Visit each route and capture data
            print(f"\n[3/5] Visiting {len(self.discovered_routes)} routes...")
            await self._visit_all_routes(page)
            print(f"✅ Visited {len(self.visited_routes)} routes")
            
            # Step 4: Extract JavaScript source/bundles
            print("\n[4/5] Extracting JS bundles and source maps...")
            await self._extract_js_sources(page)
            
            # Step 5: Generate report
            print("\n[5/5] Generating report...")
            self._generate_report()
            
            await browser.close()
        
        print(f"\n{'='*60}")
        print(f"  SCRAPING COMPLETE")
        print(f"  Output: {self.output_dir}")
        print(f"  API calls captured: {len(self.api_calls)}")
        print(f"  Routes visited: {len(self.visited_routes)}")
        print(f"  Forms found: {len(self.forms_found)}")
        print(f"  Tables found: {len(self.tables_found)}")
        print(f"{'='*60}\n")

    async def _setup_network_capture(self, page: Page):
        """Intercept all network requests to capture API calls"""
        async def handle_response(response):
            url = response.url
            parsed = urlparse(url)
            
            # Skip static assets
            skip_extensions = ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.map']
            if any(parsed.path.endswith(ext) for ext in skip_extensions):
                return
            
            # Capture API calls (typically /api/, /v1/, or XHR/fetch requests)
            content_type = response.headers.get('content-type', '')
            if 'json' in content_type or '/api/' in url or '/v1/' in url or '/v2/' in url:
                try:
                    body = await response.text()
                    try:
                        body_json = json.loads(body)
                    except:
                        body_json = body[:2000] if len(body) > 2000 else body
                    
                    api_entry = {
                        'url': url,
                        'method': response.request.method,
                        'status': response.status,
                        'content_type': content_type,
                        'path': parsed.path,
                        'query': parsed.query,
                        'request_headers': dict(response.request.headers),
                        'response_headers': dict(response.headers),
                        'request_body': None,
                        'response_body': body_json,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Try to get request body
                    try:
                        post_data = response.request.post_data
                        if post_data:
                            try:
                                api_entry['request_body'] = json.loads(post_data)
                            except:
                                api_entry['request_body'] = post_data
                    except:
                        pass
                    
                    self.api_calls.append(api_entry)
                    
                    # Save individual API response
                    safe_path = parsed.path.replace('/', '_').strip('_') or 'root'
                    filename = f"{safe_path}_{response.request.method}_{len(self.api_calls)}.json"
                    with open(f"{self.output_dir}/api_responses/{filename}", 'w', encoding='utf-8') as f:
                        json.dump(api_entry, f, indent=2, ensure_ascii=False, default=str)
                        
                except Exception as e:
                    pass  # Some responses can't be read
        
        page.on("response", handle_response)

    async def _login(self, page: Page):
        """Login to the SPA using configured credentials"""
        login_config = self.config.get('login', {})
        
        try:
            # Use domcontentloaded for SPAs — networkidle may not fire correctly
            await page.goto(self.base_url, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(5000)  # Wait for Angular/React/Vue to bootstrap
            
            # Take screenshot of login page
            await page.screenshot(path=f"{self.output_dir}/screenshots/00_login_page.png")
            
            # Try configured selectors first
            if login_config.get('username_selector') and login_config.get('password_selector'):
                usel = login_config['username_selector']
                psel = login_config['password_selector']
                
                # Wait for the form element to actually render (Angular may take time)
                print(f"  Waiting for login form: {usel}")
                try:
                    await page.wait_for_selector(usel, state='visible', timeout=15000)
                except Exception:
                    print(f"  ⚠️ Selector {usel} not found, retrying with page reload...")
                    await page.reload(wait_until='domcontentloaded')
                    await page.wait_for_timeout(5000)
                    await page.wait_for_selector(usel, state='visible', timeout=15000)
                
                # Angular reactive forms require actual key events (fill() doesn't trigger ngModel)
                # Use click + clear + type to trigger Angular's change detection
                username_loc = page.locator(usel)
                await username_loc.click()
                await username_loc.fill('')  # clear first
                await username_loc.type(login_config['username'], delay=50)
                await page.wait_for_timeout(300)
                
                password_loc = page.locator(psel)
                await password_loc.click()
                await password_loc.fill('')
                await password_loc.type(login_config['password'], delay=50)
                await page.wait_for_timeout(500)
                
                # Screenshot right before clicking login
                await page.screenshot(path=f"{self.output_dir}/screenshots/00b_before_submit.png")
                
                if login_config.get('submit_selector'):
                    await page.locator(login_config['submit_selector']).click()
                else:
                    await page.press(psel, 'Enter')
            else:
                # Auto-detect login form
                print("  Auto-detecting login form...")
                
                # Common username field selectors
                username_selectors = [
                    'input[name="username"]', 'input[name="user"]', 'input[name="email"]',
                    'input[name="login"]', 'input[name="userName"]', 'input[name="account"]',
                    'input[type="text"]:first-of-type', 'input[type="email"]',
                    'input[placeholder*="user" i]', 'input[placeholder*="email" i]',
                    'input[placeholder*="tên" i]', 'input[placeholder*="đăng nhập" i]',
                    'input[placeholder*="tài khoản" i]',
                    '#username', '#user', '#email', '#login',
                ]
                
                password_selectors = [
                    'input[name="password"]', 'input[name="pass"]', 'input[name="pwd"]',
                    'input[type="password"]',
                    'input[placeholder*="password" i]', 'input[placeholder*="mật khẩu" i]',
                    '#password', '#pass',
                ]
                
                submit_selectors = [
                    'button[type="submit"]', 'input[type="submit"]',
                    'button:has-text("Login")', 'button:has-text("Sign in")',
                    'button:has-text("Đăng nhập")', 'button:has-text("Log in")',
                    '.login-button', '.btn-login', '.submit-btn',
                    'button.ant-btn-primary', 'button.el-button--primary',
                    'button.btn-primary',
                ]
                
                username_el = None
                for sel in username_selectors:
                    try:
                        el = page.locator(sel).first
                        if await el.is_visible(timeout=1000):
                            username_el = sel
                            break
                    except:
                        continue
                
                password_el = None
                for sel in password_selectors:
                    try:
                        el = page.locator(sel).first
                        if await el.is_visible(timeout=1000):
                            password_el = sel
                            break
                    except:
                        continue
                
                if username_el and password_el:
                    print(f"  Found: username={username_el}, password={password_el}")
                    await page.fill(username_el, login_config['username'])
                    await page.wait_for_timeout(500)
                    await page.fill(password_el, login_config['password'])
                    await page.wait_for_timeout(500)
                    
                    # Try submit button
                    submitted = False
                    for sel in submit_selectors:
                        try:
                            el = page.locator(sel).first
                            if await el.is_visible(timeout=1000):
                                await el.click()
                                submitted = True
                                break
                        except:
                            continue
                    
                    if not submitted:
                        await page.press(password_el, 'Enter')
                else:
                    print(f"  ❌ Could not find login form (username={username_el}, password={password_el})")
                    # Save page HTML for debugging
                    html = await page.content()
                    with open(f"{self.output_dir}/login_page_debug.html", 'w') as f:
                        f.write(html)
                    return False
            
            # Wait for navigation after login — Angular dashboard needs time to render
            await page.wait_for_timeout(8000)
            try:
                await page.wait_for_load_state('networkidle', timeout=30000)
            except Exception:
                pass  # networkidle may not fire on some SPAs
            
            # Check if login was successful
            current_url = page.url
            await page.screenshot(path=f"{self.output_dir}/screenshots/01_after_login.png")
            
            # Save cookies/auth tokens
            cookies = await page.context.cookies()
            with open(f"{self.output_dir}/cookies.json", 'w') as f:
                json.dump(cookies, f, indent=2)
            
            # Extract localStorage auth tokens
            storage = await page.evaluate("""() => {
                const data = {};
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    data[key] = localStorage.getItem(key);
                }
                return data;
            }""")
            with open(f"{self.output_dir}/local_storage.json", 'w') as f:
                json.dump(storage, f, indent=2, ensure_ascii=False)
            
            # Check for auth tokens in storage
            auth_keys = [k for k in storage.keys() if any(t in k.lower() for t in ['token', 'auth', 'session', 'jwt', 'user'])]
            if auth_keys:
                print(f"  Auth tokens found: {auth_keys}")
            
            return True
            
        except Exception as e:
            print(f"  Login error: {e}")
            await page.screenshot(path=f"{self.output_dir}/screenshots/login_error.png")
            return False

    async def _discover_routes(self, page: Page):
        """Discover all routes from navigation elements, sidebar, and JS source"""
        
        # Method 1: Extract routes from anchor tags and navigation
        routes = await page.evaluate("""() => {
            const routes = new Set();
            
            // All anchor links
            document.querySelectorAll('a[href]').forEach(a => {
                const href = a.getAttribute('href');
                if (href && (href.startsWith('#/') || href.startsWith('/'))) {
                    routes.add(href);
                }
            });
            
            // Router-link elements (Vue.js)
            document.querySelectorAll('[to], [data-to]').forEach(el => {
                const to = el.getAttribute('to') || el.getAttribute('data-to');
                if (to) routes.add(to);
            });
            
            // Sidebar/menu items with click handlers
            const menuSelectors = [
                '.sidebar a', '.nav a', '.menu a', '.ant-menu a', '.el-menu a',
                '[class*="sidebar"] a', '[class*="nav"] a', '[class*="menu"] a',
                '.ant-menu-item', '.el-menu-item', '.v-list-item',
                '[role="menuitem"]', '[role="navigation"] a'
            ];
            
            menuSelectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(el => {
                    const href = el.getAttribute('href');
                    if (href) routes.add(href);
                    // Check for data attributes
                    const path = el.getAttribute('data-path') || el.getAttribute('data-route');
                    if (path) routes.add(path);
                });
            });
            
            return Array.from(routes);
        }""")
        
        for route in routes:
            self.discovered_routes.add(route)
        
        # Method 2: Extract routes from Vue Router or React Router config in JS
        js_routes = await page.evaluate("""() => {
            const routes = [];
            
            // Vue Router
            if (window.__VUE_DEVTOOLS_GLOBAL_HOOK__) {
                try {
                    const app = window.__VUE_DEVTOOLS_GLOBAL_HOOK__.apps?.[0];
                    if (app && app.config?.globalProperties?.$router) {
                        const router = app.config.globalProperties.$router;
                        router.getRoutes().forEach(r => {
                            routes.push({path: r.path, name: r.name, meta: r.meta});
                        });
                    }
                } catch(e) {}
            }
            
            // Also try older Vue 2 style
            try {
                if (window.__vue_app__ && window.__vue_app__.$router) {
                    window.__vue_app__.$router.options.routes.forEach(r => {
                        routes.push({path: r.path, name: r.name});
                        if (r.children) {
                            r.children.forEach(c => {
                                routes.push({path: r.path + '/' + c.path, name: c.name});
                            });
                        }
                    });
                }
            } catch(e) {}
            
            return routes;
        }""")
        
        if js_routes:
            print(f"  Found {len(js_routes)} routes from router config")
            with open(f"{self.output_dir}/router_config.json", 'w') as f:
                json.dump(js_routes, f, indent=2, ensure_ascii=False)
            for r in js_routes:
                if r.get('path'):
                    self.discovered_routes.add('#' + r['path'] if not r['path'].startswith('#') else r['path'])
        
        # Method 3: Extract routes from page source/scripts
        html = await page.content()
        hash_routes = re.findall(r'["\']#/([\w\-/]+)["\']', html)
        path_routes = re.findall(r'path:\s*["\']/([\w\-/]+)["\']', html)
        
        for r in hash_routes:
            self.discovered_routes.add(f'#/{r}')
        for r in path_routes:
            self.discovered_routes.add(f'#/{r}')
        
        # Method 4: Expand sidebar/menu items that might be collapsed
        await self._expand_all_menus(page)
        
        # Re-extract after expanding
        more_routes = await page.evaluate("""() => {
            const routes = [];
            document.querySelectorAll('a[href*="#/"]').forEach(a => {
                routes.push(a.getAttribute('href'));
            });
            return routes;
        }""")
        for r in more_routes:
            self.discovered_routes.add(r)
        
        # Save discovered routes
        with open(f"{self.output_dir}/discovered_routes.json", 'w') as f:
            json.dump(sorted(list(self.discovered_routes)), f, indent=2)

    async def _expand_all_menus(self, page: Page):
        """Click on all expandable menu/submenu items"""
        expandable_selectors = [
            '.ant-menu-submenu-title', '.el-submenu__title',
            '[class*="submenu"]', '[class*="expandable"]',
            '.has-children > a', '.has-sub > a',
            '.ant-menu-submenu', '.el-submenu',
            '[aria-expanded="false"]',
            '.sidebar .parent', '.nav .dropdown-toggle',
        ]
        
        for sel in expandable_selectors:
            try:
                elements = page.locator(sel)
                count = await elements.count()
                for i in range(count):
                    try:
                        await elements.nth(i).click(timeout=1000)
                        await page.wait_for_timeout(500)
                    except:
                        continue
            except:
                continue

    async def _visit_all_routes(self, page: Page):
        """Visit each discovered route and capture data"""
        routes = sorted(list(self.discovered_routes))
        
        for idx, route in enumerate(routes):
            if route in self.visited_routes:
                continue
                
            print(f"  [{idx+1}/{len(routes)}] Visiting: {route}")
            
            try:
                # Navigate to route
                if route.startswith('#'):
                    full_url = self.base_url.split('#')[0] + route
                elif route.startswith('/'):
                    parsed = urlparse(self.base_url)
                    full_url = f"{parsed.scheme}://{parsed.netloc}{route}"
                else:
                    full_url = route
                
                await page.goto(full_url, wait_until='networkidle', timeout=15000)
                await page.wait_for_timeout(2000)
                
                # Capture screenshot
                safe_name = route.replace('#/', '').replace('/', '_') or 'root'
                await page.screenshot(path=f"{self.output_dir}/screenshots/{idx+2:02d}_{safe_name}.png")
                
                # Extract page structure
                page_info = await self._extract_page_structure(page, route)
                self.page_data[route] = page_info
                
                # Save DOM snapshot
                html = await page.content()
                with open(f"{self.output_dir}/dom_snapshots/{safe_name}.html", 'w', encoding='utf-8') as f:
                    f.write(html)
                
                self.visited_routes.add(route)
                
                # Check for any new routes discovered on this page
                new_routes = await page.evaluate("""() => {
                    const routes = [];
                    document.querySelectorAll('a[href*="#/"]').forEach(a => {
                        routes.push(a.getAttribute('href'));
                    });
                    return routes;
                }""")
                for r in new_routes:
                    if r not in self.visited_routes:
                        self.discovered_routes.add(r)
                
            except Exception as e:
                print(f"    ⚠️ Error: {e}")
                self.visited_routes.add(route)  # Mark as visited to avoid infinite retries

    async def _extract_page_structure(self, page: Page, route: str):
        """Extract forms, tables, components, and UI structure from current page"""
        
        structure = await page.evaluate("""() => {
            const result = {
                title: document.title,
                headings: [],
                forms: [],
                tables: [],
                buttons: [],
                inputs: [],
                selects: [],
                modals: [],
                cards: [],
                breadcrumbs: [],
                tabs: [],
            };
            
            // Headings
            document.querySelectorAll('h1, h2, h3, h4').forEach(h => {
                result.headings.push({tag: h.tagName, text: h.textContent.trim()});
            });
            
            // Forms
            document.querySelectorAll('form').forEach(form => {
                const fields = [];
                form.querySelectorAll('input, select, textarea').forEach(input => {
                    fields.push({
                        tag: input.tagName.toLowerCase(),
                        type: input.type || '',
                        name: input.name || '',
                        placeholder: input.placeholder || '',
                        label: input.labels?.[0]?.textContent?.trim() || '',
                        required: input.required,
                    });
                });
                result.forms.push({
                    action: form.action,
                    method: form.method,
                    fields: fields,
                });
            });
            
            // Also capture form-like structures (common in Vue/React)
            document.querySelectorAll('.ant-form, .el-form, [class*="form"]').forEach(form => {
                const fields = [];
                form.querySelectorAll('.ant-form-item, .el-form-item, [class*="form-item"], [class*="form-group"]').forEach(item => {
                    const label = item.querySelector('label, .ant-form-item-label, .el-form-item__label');
                    const input = item.querySelector('input, select, textarea, .ant-select, .el-select, .ant-picker, .el-date-editor');
                    if (label || input) {
                        fields.push({
                            label: label?.textContent?.trim() || '',
                            inputType: input?.type || input?.tagName?.toLowerCase() || 'unknown',
                            name: input?.getAttribute('name') || input?.getAttribute('id') || '',
                            placeholder: input?.getAttribute('placeholder') || '',
                            className: input?.className?.substring(0, 100) || '',
                        });
                    }
                });
                if (fields.length > 0) {
                    result.forms.push({type: 'component-form', fields: fields});
                }
            });
            
            // Tables
            document.querySelectorAll('table, .ant-table, .el-table, [class*="table"]').forEach(table => {
                const headers = [];
                table.querySelectorAll('th, .ant-table-thead th, .el-table__header th').forEach(th => {
                    headers.push(th.textContent.trim());
                });
                const rowCount = table.querySelectorAll('tr, .ant-table-row, .el-table__row').length;
                result.tables.push({
                    headers: headers,
                    rowCount: rowCount,
                    className: table.className?.substring(0, 100) || '',
                });
            });
            
            // Buttons
            document.querySelectorAll('button, .ant-btn, .el-button, [role="button"]').forEach(btn => {
                const text = btn.textContent.trim();
                if (text && text.length < 50) {
                    result.buttons.push({
                        text: text,
                        type: btn.type || '',
                        className: btn.className?.substring(0, 80) || '',
                    });
                }
            });
            
            // Input fields (outside forms)
            document.querySelectorAll('input:not(form input), .ant-input, .el-input').forEach(input => {
                result.inputs.push({
                    type: input.type || '',
                    name: input.name || '',
                    placeholder: input.placeholder || '',
                });
            });
            
            // Modals/Dialogs
            document.querySelectorAll('.ant-modal, .el-dialog, [class*="modal"], [role="dialog"]').forEach(modal => {
                const title = modal.querySelector('.ant-modal-title, .el-dialog__title, [class*="modal-title"]');
                result.modals.push({
                    title: title?.textContent?.trim() || '',
                    visible: modal.style.display !== 'none' && !modal.classList.contains('hidden'),
                });
            });
            
            // Tabs
            document.querySelectorAll('.ant-tabs-tab, .el-tabs__item, [role="tab"]').forEach(tab => {
                result.tabs.push(tab.textContent.trim());
            });
            
            return result;
        }""")
        
        # Track forms and tables globally
        for form in structure.get('forms', []):
            form['route'] = route
            self.forms_found.append(form)
        
        for table in structure.get('tables', []):
            table['route'] = route
            self.tables_found.append(table)
        
        return structure

    async def _extract_js_sources(self, page: Page):
        """Extract JavaScript bundles to find route definitions, API base URLs, etc."""
        
        # Get all script sources
        scripts = await page.evaluate("""() => {
            const scripts = [];
            document.querySelectorAll('script[src]').forEach(s => {
                scripts.push(s.src);
            });
            return scripts;
        }""")
        
        js_analysis = {
            'script_urls': scripts,
            'api_base_urls': [],
            'route_definitions': [],
            'store_modules': [],
            'component_names': [],
        }
        
        # Try to extract from inline scripts and loaded JS
        inline_analysis = await page.evaluate("""() => {
            const analysis = {
                vue_detected: !!window.__VUE_DEVTOOLS_GLOBAL_HOOK__,
                react_detected: !!window.__REACT_DEVTOOLS_GLOBAL_HOOK__,
                angular_detected: !!window.ng || !!window.getAllAngularRootElements,
                framework: 'unknown',
                api_base: null,
                store_type: null,
            };
            
            // Detect framework
            if (analysis.vue_detected) analysis.framework = 'Vue.js';
            else if (analysis.react_detected) analysis.framework = 'React';
            else if (analysis.angular_detected) analysis.framework = 'Angular';
            
            // Try to find API base URL from common patterns
            try {
                // Check for axios defaults
                if (window.axios?.defaults?.baseURL) {
                    analysis.api_base = window.axios.defaults.baseURL;
                }
            } catch(e) {}
            
            // Check for Vuex/Pinia
            try {
                if (window.__VUE_DEVTOOLS_GLOBAL_HOOK__?.apps?.[0]) {
                    const app = window.__VUE_DEVTOOLS_GLOBAL_HOOK__.apps[0];
                    if (app.config?.globalProperties?.$store) {
                        analysis.store_type = 'Vuex';
                    }
                    if (app.config?.globalProperties?.$pinia) {
                        analysis.store_type = 'Pinia';
                    }
                }
            } catch(e) {}
            
            return analysis;
        }""")
        
        js_analysis['framework_detection'] = inline_analysis
        
        # Extract route patterns from JS bundles
        for script_url in scripts[:5]:  # Limit to first 5 scripts
            try:
                response = await page.evaluate(f"""async () => {{
                    try {{
                        const resp = await fetch('{script_url}');
                        const text = await resp.text();
                        // Extract API URLs
                        const apiUrls = text.match(/["'](https?:\/\/[^"']+\/api[^"']*)['"]/g) || [];
                        const paths = text.match(/path:\s*["'](\/[^"']+)["']/g) || [];
                        const components = text.match(/component:\s*["']([^"']+)["']/g) || [];
                        return {{
                            size: text.length,
                            apiUrls: apiUrls.slice(0, 20),
                            paths: paths.slice(0, 50),
                            components: components.slice(0, 30),
                        }};
                    }} catch(e) {{
                        return {{error: e.message}};
                    }}
                }}""")
                
                if response and not response.get('error'):
                    js_analysis['route_definitions'].extend(response.get('paths', []))
                    js_analysis['api_base_urls'].extend(response.get('apiUrls', []))
                    js_analysis['component_names'].extend(response.get('components', []))
                    
            except Exception as e:
                pass
        
        with open(f"{self.output_dir}/js_analysis.json", 'w') as f:
            json.dump(js_analysis, f, indent=2, ensure_ascii=False)
        
        print(f"  Framework: {inline_analysis.get('framework', 'unknown')}")
        print(f"  Store: {inline_analysis.get('store_type', 'none')}")
        print(f"  API Base: {inline_analysis.get('api_base', 'not found')}")
        print(f"  Script bundles: {len(scripts)}")

    def _generate_report(self):
        """Generate comprehensive analysis report"""
        
        # Deduplicate and organize API calls
        api_endpoints = {}
        for call in self.api_calls:
            path = call['path']
            method = call['method']
            key = f"{method} {path}"
            
            if key not in api_endpoints:
                api_endpoints[key] = {
                    'method': method,
                    'path': path,
                    'url': call['url'],
                    'status_codes': set(),
                    'request_bodies': [],
                    'response_samples': [],
                    'call_count': 0,
                }
            
            api_endpoints[key]['status_codes'].add(call['status'])
            api_endpoints[key]['call_count'] += 1
            
            if call.get('request_body') and len(api_endpoints[key]['request_bodies']) < 3:
                api_endpoints[key]['request_bodies'].append(call['request_body'])
            
            if call.get('response_body') and len(api_endpoints[key]['response_samples']) < 2:
                resp = call['response_body']
                if isinstance(resp, dict) or isinstance(resp, list):
                    api_endpoints[key]['response_samples'].append(resp)
        
        # Convert sets for JSON serialization
        for key in api_endpoints:
            api_endpoints[key]['status_codes'] = list(api_endpoints[key]['status_codes'])
        
        # Infer database schema from API responses
        db_schema = self._infer_schema_from_apis(api_endpoints)
        
        report = {
            'metadata': {
                'target_url': self.base_url,
                'scraped_at': datetime.now().isoformat(),
                'total_routes': len(self.discovered_routes),
                'visited_routes': len(self.visited_routes),
                'total_api_calls': len(self.api_calls),
                'unique_endpoints': len(api_endpoints),
                'forms_found': len(self.forms_found),
                'tables_found': len(self.tables_found),
            },
            'routes': sorted(list(self.discovered_routes)),
            'api_endpoints': api_endpoints,
            'forms': self.forms_found,
            'tables': self.tables_found,
            'page_structures': self.page_data,
            'inferred_schema': db_schema,
        }
        
        with open(f"{self.output_dir}/full_report.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        # Generate human-readable summary
        summary = self._generate_summary(report)
        with open(f"{self.output_dir}/SUMMARY.md", 'w', encoding='utf-8') as f:
            f.write(summary)

    def _infer_schema_from_apis(self, api_endpoints):
        """Infer database tables/schema from API response structures"""
        schema = {}
        
        for key, endpoint in api_endpoints.items():
            for sample in endpoint.get('response_samples', []):
                if not isinstance(sample, (dict, list)):
                    continue
                
                # Try to find data arrays (lists of records)
                data = sample
                if isinstance(sample, dict):
                    # Common patterns: {data: [...]}, {results: [...]}, {items: [...]}, {list: [...]}
                    for data_key in ['data', 'results', 'items', 'list', 'records', 'rows', 'content']:
                        if data_key in sample and isinstance(sample[data_key], list):
                            data = sample[data_key]
                            break
                
                if isinstance(data, list) and len(data) > 0:
                    record = data[0] if isinstance(data[0], dict) else None
                    if record:
                        # Infer table name from API path
                        path_parts = endpoint['path'].strip('/').split('/')
                        table_name = path_parts[-1] if path_parts else 'unknown'
                        # Remove common prefixes
                        for prefix in ['api', 'v1', 'v2', 'rest']:
                            if table_name == prefix and len(path_parts) > 1:
                                table_name = path_parts[-2] if len(path_parts) > 2 else path_parts[-1]
                        
                        if table_name not in schema:
                            schema[table_name] = {
                                'source_endpoint': key,
                                'fields': {},
                                'sample_record': record,
                            }
                        
                        for field_name, value in record.items():
                            field_type = type(value).__name__
                            if value is None:
                                field_type = 'nullable'
                            elif isinstance(value, str):
                                # Try to detect dates, IDs, etc.
                                if re.match(r'\d{4}-\d{2}-\d{2}', value):
                                    field_type = 'datetime'
                                elif re.match(r'^[0-9a-f]{8}-', value):
                                    field_type = 'uuid'
                                elif len(value) > 200:
                                    field_type = 'text'
                                else:
                                    field_type = 'string'
                            elif isinstance(value, bool):
                                field_type = 'boolean'
                            elif isinstance(value, int):
                                field_type = 'integer'
                            elif isinstance(value, float):
                                field_type = 'decimal'
                            elif isinstance(value, list):
                                field_type = 'array/relation'
                            elif isinstance(value, dict):
                                field_type = 'object/relation'
                            
                            schema[table_name]['fields'][field_name] = {
                                'type': field_type,
                                'sample': str(value)[:100] if value else None,
                                'nullable': value is None,
                            }
                
                elif isinstance(data, dict) and endpoint['method'] == 'GET':
                    # Single record endpoint
                    path_parts = endpoint['path'].strip('/').split('/')
                    table_name = path_parts[-2] if len(path_parts) >= 2 else path_parts[-1]
                    
                    if table_name not in schema:
                        schema[table_name] = {
                            'source_endpoint': key,
                            'fields': {},
                            'sample_record': data,
                        }
                    
                    for field_name, value in data.items():
                        if field_name not in schema[table_name]['fields']:
                            schema[table_name]['fields'][field_name] = {
                                'type': type(value).__name__,
                                'sample': str(value)[:100] if value else None,
                            }
        
        return schema

    def _generate_summary(self, report):
        """Generate markdown summary"""
        md = f"""# SPA Scraping Report: {self.base_url}
**Scraped at:** {report['metadata']['scraped_at']}

## Overview
| Metric | Count |
|--------|-------|
| Routes Discovered | {report['metadata']['total_routes']} |
| Routes Visited | {report['metadata']['visited_routes']} |
| API Calls Captured | {report['metadata']['total_api_calls']} |
| Unique API Endpoints | {report['metadata']['unique_endpoints']} |
| Forms Found | {report['metadata']['forms_found']} |
| Tables Found | {report['metadata']['tables_found']} |

## Discovered Routes
"""
        for route in report['routes']:
            md += f"- `{route}`\n"
        
        md += "\n## API Endpoints\n"
        for key, endpoint in sorted(report['api_endpoints'].items()):
            md += f"\n### `{key}`\n"
            md += f"- Status codes: {endpoint['status_codes']}\n"
            md += f"- Call count: {endpoint['call_count']}\n"
            if endpoint.get('request_bodies'):
                md += f"- Has request body: Yes\n"
        
        md += "\n## Forms Found\n"
        for form in report['forms']:
            md += f"\n### Form on `{form.get('route', 'unknown')}`\n"
            for field in form.get('fields', []):
                label = field.get('label', field.get('name', 'unnamed'))
                ftype = field.get('type', field.get('inputType', ''))
                md += f"- {label} ({ftype})\n"
        
        md += "\n## Inferred Database Schema\n"
        for table, info in report.get('inferred_schema', {}).items():
            md += f"\n### Table: `{table}`\n"
            md += f"Source: `{info['source_endpoint']}`\n\n"
            md += "| Field | Type | Sample |\n|-------|------|--------|\n"
            for field, finfo in info.get('fields', {}).items():
                sample = (finfo.get('sample', '') or '')[:50]
                md += f"| {field} | {finfo['type']} | {sample} |\n"
        
        md += "\n## Tables Found in UI\n"
        for table in report['tables']:
            md += f"\n### Table on `{table.get('route', 'unknown')}`\n"
            md += f"Headers: {', '.join(table.get('headers', []))}\n"
            md += f"Row count: {table.get('rowCount', 0)}\n"
        
        return md
