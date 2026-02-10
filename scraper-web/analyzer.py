"""
LLM Analyzer - Takes scraper output and generates:
1. Complete database schema (SQL)
2. API specification (OpenAPI-like)
3. Frontend component tree
4. Replication blueprint

Supports: Groq (primary), OpenAI, Anthropic, or any OpenAI-compatible API.
Falls back to rule-based analysis if no API key is configured.
"""

import json
import os
import re
from pathlib import Path


# ── LLM Provider Configuration ──────────────────────────────────────────────
PROVIDERS = {
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "env_key": "GROQ_API_KEY",
        "default_model": "llama-3.3-70b-versatile",
        "header_style": "bearer",  # Authorization: Bearer <key>
    },
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "env_key": "OPENAI_API_KEY",
        "default_model": "gpt-4o-mini",
        "header_style": "bearer",
    },
    "anthropic": {
        "url": "https://api.anthropic.com/v1/messages",
        "env_key": "ANTHROPIC_API_KEY",
        "default_model": "claude-sonnet-4-20250514",
        "header_style": "anthropic",
    },
}


class LLMAnalyzer:
    def __init__(self, scrape_dir, api_key=None, api_url=None, model=None, provider=None):
        self.scrape_dir = scrape_dir
        self.report = None

        # ── Resolve provider ────────────────────────────────────────────
        # Priority: explicit arg → GROQ_API_KEY → OPENAI_API_KEY → ANTHROPIC → none
        self.provider_name = provider
        self.api_key = api_key

        if not self.api_key:
            for pname, pcfg in PROVIDERS.items():
                key = os.environ.get(pcfg["env_key"])
                if key:
                    self.api_key = key
                    self.provider_name = pname
                    break

        if self.provider_name and self.provider_name in PROVIDERS:
            pcfg = PROVIDERS[self.provider_name]
            self.api_url = api_url or pcfg["url"]
            self.model = model or pcfg["default_model"]
            self.header_style = pcfg["header_style"]
        else:
            # Fallback defaults (Groq)
            self.api_url = api_url or PROVIDERS["groq"]["url"]
            self.model = model or PROVIDERS["groq"]["default_model"]
            self.header_style = "bearer"
            self.provider_name = self.provider_name or "groq"

        if self.api_key:
            masked = self.api_key[:8] + "..." + self.api_key[-4:]
            print(f"  🔑 LLM Provider: {self.provider_name.upper()} | Model: {self.model} | Key: {masked}")
        else:
            print(f"  ⚠️  No LLM API key found. Set GROQ_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY.")
            print(f"      Falling back to rule-based analysis (still works, just less intelligent).")

    # ── Groq / OpenAI compatible chat call ───────────────────────────────
    def _call_llm(self, system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> str:
        """
        Call the configured LLM provider (Groq, OpenAI, etc.) using `requests`.
        Returns the assistant message content, or empty string on failure.
        """
        if not self.api_key:
            return ""

        try:
            import requests as _requests
        except ImportError:
            print("    ⚠️  `requests` library not installed. Run: pip install requests")
            return ""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3,
        }

        headers = {
            "Content-Type": "application/json",
        }

        if self.header_style == "anthropic":
            headers["x-api-key"] = self.api_key
            headers["anthropic-version"] = "2023-06-01"
            payload = {
                "model": self.model,
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
            }
        else:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            resp = _requests.post(self.api_url, json=payload, headers=headers, timeout=60)

            if not resp.ok:
                print(f"    ⚠️  LLM API error ({resp.status_code}): {resp.text[:200]}")
                return ""

            result = resp.json()

            # OpenAI / Groq format
            if "choices" in result:
                return result["choices"][0]["message"]["content"]
            # Anthropic format
            elif "content" in result:
                return result["content"][0]["text"]
            return ""
        except Exception as e:
            print(f"    ⚠️  LLM call failed: {e}")
            return ""
        
    def load_scrape_data(self):
        """Load all scraper output"""
        report_path = os.path.join(self.scrape_dir, 'full_report.json')
        if os.path.exists(report_path):
            with open(report_path) as f:
                self.report = json.load(f)
        
        # Load additional data
        self.local_storage = {}
        ls_path = os.path.join(self.scrape_dir, 'local_storage.json')
        if os.path.exists(ls_path):
            with open(ls_path) as f:
                self.local_storage = json.load(f)
        
        self.js_analysis = {}
        js_path = os.path.join(self.scrape_dir, 'js_analysis.json')
        if os.path.exists(js_path):
            with open(js_path) as f:
                self.js_analysis = json.load(f)
        
        # Load API response samples
        self.api_samples = {}
        api_dir = os.path.join(self.scrape_dir, 'api_responses')
        if os.path.exists(api_dir):
            for f in sorted(os.listdir(api_dir))[:100]:  # Limit
                with open(os.path.join(api_dir, f)) as fh:
                    try:
                        self.api_samples[f] = json.load(fh)
                    except:
                        pass
    
    def generate_database_schema(self):
        """Generate SQL schema from inferred data"""
        if not self.report:
            self.load_scrape_data()
        
        schema = self.report.get('inferred_schema', {})
        forms = self.report.get('forms', [])
        tables_ui = self.report.get('tables', [])
        
        sql_lines = []
        sql_lines.append("-- Auto-generated database schema from SPA scraping")
        sql_lines.append(f"-- Source: {self.report.get('metadata', {}).get('target_url', 'unknown')}")
        sql_lines.append(f"-- Generated from {len(schema)} inferred tables\n")
        
        for table_name, info in schema.items():
            # Clean table name
            clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', table_name).lower()
            
            sql_lines.append(f"\n-- Source endpoint: {info.get('source_endpoint', 'unknown')}")
            sql_lines.append(f"CREATE TABLE {clean_name} (")
            
            fields = info.get('fields', {})
            field_lines = []
            
            # Check if there's an ID field
            has_id = any(f.lower() in ['id', '_id', 'uuid'] for f in fields)
            if not has_id:
                field_lines.append("    id SERIAL PRIMARY KEY")
            
            for field_name, finfo in fields.items():
                col_name = re.sub(r'[^a-zA-Z0-9_]', '_', field_name).lower()
                col_type = self._map_to_sql_type(finfo['type'], field_name, finfo.get('sample'))
                nullable = "NULL" if finfo.get('nullable') else "NOT NULL"
                
                # Primary key detection
                pk = ""
                if field_name.lower() in ['id', '_id'] and finfo['type'] in ['integer', 'uuid', 'string']:
                    pk = " PRIMARY KEY"
                    nullable = "NOT NULL"
                
                field_lines.append(f"    {col_name} {col_type} {nullable}{pk}")
            
            # Add common fields if not present
            field_names_lower = [f.lower() for f in fields.keys()]
            if 'created_at' not in field_names_lower and 'createdat' not in field_names_lower:
                field_lines.append("    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            if 'updated_at' not in field_names_lower and 'updatedat' not in field_names_lower:
                field_lines.append("    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            
            sql_lines.append(",\n".join(field_lines))
            sql_lines.append(");\n")
        
        # Add indexes based on common patterns
        sql_lines.append("\n-- Suggested indexes")
        for table_name, info in schema.items():
            clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', table_name).lower()
            for field_name in info.get('fields', {}):
                if any(kw in field_name.lower() for kw in ['_id', 'email', 'phone', 'code', 'status', 'type']):
                    idx_name = f"idx_{clean_name}_{field_name.lower()}"
                    sql_lines.append(f"CREATE INDEX {idx_name} ON {clean_name}({field_name.lower()});")
        
        sql = "\n".join(sql_lines)
        
        # ── AI Enhancement: Ask Groq to improve the schema ──────────────
        ai_additions = self._ai_enhance_schema(sql)
        if ai_additions:
            sql += "\n\n" + ai_additions
        
        output_path = os.path.join(self.scrape_dir, 'database_schema.sql')
        with open(output_path, 'w') as f:
            f.write(sql)
        
        return sql
    
    def _ai_enhance_schema(self, base_sql: str) -> str:
        """Use Groq/LLM to identify missing relationships and suggest improvements."""
        if not self.api_key:
            return ""
        
        # Summarize API samples for context (limit size for token budget)
        api_summary = []
        for fname, data in list(self.api_samples.items())[:20]:
            entry = {
                "file": fname,
                "url": data.get("url", ""),
                "method": data.get("method", ""),
            }
            resp = data.get("response_body")
            if isinstance(resp, dict):
                entry["response_keys"] = list(resp.keys())[:15]
            elif isinstance(resp, list) and resp and isinstance(resp[0], dict):
                entry["response_keys"] = list(resp[0].keys())[:15]
            api_summary.append(entry)
        
        system = """You are a senior database architect. Given auto-generated SQL schema and API response samples from a web application scrape, suggest improvements:
1. Missing foreign key relationships (ALTER TABLE ... ADD CONSTRAINT)
2. Missing tables that are implied by the data
3. Better column types or constraints
4. Useful composite indexes

Output ONLY valid SQL statements. No markdown, no explanations. Each statement on its own line."""
        
        user = f"""Here is the auto-generated schema:
```sql
{base_sql[:3000]}
```

And here are some API response field summaries:
{json.dumps(api_summary[:15], indent=2, default=str)[:2000]}

Generate ONLY the additional SQL statements (ALTER TABLE, CREATE TABLE, CREATE INDEX) that would improve this schema."""
        
        print("    🤖 Asking Groq to enhance schema...")
        result = self._call_llm(system, user, max_tokens=2048)
        
        if result:
            # Wrap AI output in a clear block
            return f"""
-- ══════════════════════════════════════════════════════════════
-- AI-Enhanced Suggestions (via {self.provider_name.upper()} / {self.model})
-- ══════════════════════════════════════════════════════════════
{result.strip()}
"""
        return ""
    
    def generate_api_spec(self):
        """Generate API specification document"""
        if not self.report:
            self.load_scrape_data()
        
        endpoints = self.report.get('api_endpoints', {})
        
        spec = {
            "info": {
                "title": f"API Specification - {self.report.get('metadata', {}).get('target_url', '')}",
                "description": "Auto-generated from SPA scraping",
            },
            "endpoints": {}
        }
        
        for key, ep in endpoints.items():
            method = ep['method']
            path = ep['path']
            
            endpoint_spec = {
                "method": method,
                "path": path,
                "url": ep['url'],
                "status_codes": ep.get('status_codes', []),
                "call_count": ep.get('call_count', 0),
            }
            
            # Analyze request body structure
            if ep.get('request_bodies'):
                body = ep['request_bodies'][0]
                if isinstance(body, dict):
                    endpoint_spec['request_body'] = {
                        "type": "object",
                        "properties": {k: self._infer_json_type(v) for k, v in body.items()}
                    }
            
            # Analyze response structure
            if ep.get('response_samples'):
                sample = ep['response_samples'][0]
                if isinstance(sample, dict):
                    endpoint_spec['response_schema'] = self._describe_json_structure(sample)
                elif isinstance(sample, list) and sample:
                    endpoint_spec['response_schema'] = {
                        "type": "array",
                        "items": self._describe_json_structure(sample[0]) if isinstance(sample[0], dict) else {"type": type(sample[0]).__name__}
                    }
            
            spec['endpoints'][key] = endpoint_spec
        
        output_path = os.path.join(self.scrape_dir, 'api_specification.json')
        with open(output_path, 'w') as f:
            json.dump(spec, f, indent=2, ensure_ascii=False, default=str)
        
        return spec
    
    def generate_component_tree(self):
        """Generate frontend component hierarchy"""
        if not self.report:
            self.load_scrape_data()
        
        pages = self.report.get('page_structures', {})
        routes = self.report.get('routes', [])
        
        tree = {
            "framework": self.js_analysis.get('framework_detection', {}).get('framework', 'unknown'),
            "pages": {},
            "shared_components": [],
            "layout": {
                "has_sidebar": False,
                "has_topbar": False,
                "has_breadcrumbs": False,
            }
        }
        
        all_buttons = set()
        all_tabs = set()
        
        for route, page_info in pages.items():
            clean_route = route.replace('#/', '').replace('/', '_') or 'dashboard'
            
            page_spec = {
                "route": route,
                "component_name": self._route_to_component_name(route),
                "title": page_info.get('title', ''),
                "headings": page_info.get('headings', []),
                "has_form": len(page_info.get('forms', [])) > 0,
                "has_table": len(page_info.get('tables', [])) > 0,
                "has_tabs": len(page_info.get('tabs', [])) > 0,
                "buttons": [b['text'] for b in page_info.get('buttons', [])],
                "tabs": page_info.get('tabs', []),
                "form_fields": [],
                "table_headers": [],
            }
            
            for form in page_info.get('forms', []):
                for field in form.get('fields', []):
                    page_spec['form_fields'].append(field)
            
            for table in page_info.get('tables', []):
                page_spec['table_headers'].extend(table.get('headers', []))
            
            # Detect layout patterns
            if page_info.get('breadcrumbs'):
                tree['layout']['has_breadcrumbs'] = True
            
            for btn in page_info.get('buttons', []):
                all_buttons.add(btn.get('text', ''))
            for tab in page_info.get('tabs', []):
                all_tabs.add(tab)
            
            tree['pages'][route] = page_spec
        
        # Detect shared components based on repeated patterns
        button_texts = list(all_buttons)
        common_buttons = [b for b in button_texts if button_texts.count(b) > 1]
        tree['shared_components'].extend([
            {"type": "button", "text": b} for b in set(common_buttons)
        ])
        
        output_path = os.path.join(self.scrape_dir, 'component_tree.json')
        with open(output_path, 'w') as f:
            json.dump(tree, f, indent=2, ensure_ascii=False)
        
        return tree
    
    def generate_replication_blueprint(self):
        """Generate complete replication blueprint combining all analysis"""
        if not self.report:
            self.load_scrape_data()
        
        db_schema = self.generate_database_schema()
        api_spec = self.generate_api_spec()
        component_tree = self.generate_component_tree()
        
        blueprint = f"""# Replication Blueprint
## Source: {self.report.get('metadata', {}).get('target_url', '')}

## Tech Stack Recommendation
- **Frontend:** React + TypeScript + Ant Design (or Element UI if Vue detected)
- **Backend:** Node.js + Express (or FastAPI/Python)
- **Database:** PostgreSQL
- **Auth:** JWT-based (tokens found in localStorage)
- **Framework detected:** {self.js_analysis.get('framework_detection', {}).get('framework', 'unknown')}

## Architecture Overview

### Routes ({len(self.report.get('routes', []))})
"""
        for route in self.report.get('routes', []):
            comp_name = self._route_to_component_name(route)
            blueprint += f"- `{route}` → `{comp_name}`\n"
        
        blueprint += f"""
### API Endpoints ({len(self.report.get('api_endpoints', {}))})
"""
        for key, ep in sorted(self.report.get('api_endpoints', {}).items()):
            blueprint += f"- `{key}` (called {ep.get('call_count', 0)}x)\n"
        
        blueprint += f"""
### Database Tables ({len(self.report.get('inferred_schema', {}))})
"""
        for table, info in self.report.get('inferred_schema', {}).items():
            fields = list(info.get('fields', {}).keys())
            blueprint += f"- `{table}`: {', '.join(fields[:8])}{'...' if len(fields) > 8 else ''}\n"
        
        blueprint += f"""
### Frontend Pages
"""
        for route, page in component_tree.get('pages', {}).items():
            features = []
            if page.get('has_form'): features.append('📝 Form')
            if page.get('has_table'): features.append('📊 Table')
            if page.get('has_tabs'): features.append('📑 Tabs')
            blueprint += f"- `{route}`: {' | '.join(features) if features else '📄 Page'}\n"
            if page.get('table_headers'):
                blueprint += f"  - Table columns: {', '.join(page['table_headers'][:10])}\n"
            if page.get('form_fields'):
                labels = [f.get('label', f.get('name', '?')) for f in page['form_fields'][:8]]
                blueprint += f"  - Form fields: {', '.join(labels)}\n"
        
        blueprint += """
## Implementation Order
1. **Database:** Create tables from `database_schema.sql`
2. **Backend API:** Implement endpoints from `api_specification.json`
3. **Auth:** JWT login/logout based on captured auth flow
4. **Layout:** Sidebar + topbar + breadcrumbs shell
5. **CRUD Pages:** Implement each route with its forms/tables
6. **Advanced Features:** Modals, tabs, filters, search

## Files Generated
- `full_report.json` - Complete scrape data
- `database_schema.sql` - PostgreSQL schema
- `api_specification.json` - API endpoint specs
- `component_tree.json` - Frontend component hierarchy
- `screenshots/` - Visual reference for each page
- `api_responses/` - Sample API response data
- `dom_snapshots/` - HTML snapshots per route
"""
        
        output_path = os.path.join(self.scrape_dir, 'BLUEPRINT.md')
        with open(output_path, 'w') as f:
            f.write(blueprint)
        
        return blueprint
    
    # --- Helper methods ---
    
    def _map_to_sql_type(self, inferred_type, field_name, sample=None):
        """Map inferred type to SQL type"""
        type_map = {
            'string': 'VARCHAR(255)',
            'text': 'TEXT',
            'integer': 'INTEGER',
            'int': 'INTEGER',
            'decimal': 'DECIMAL(12,2)',
            'float': 'DECIMAL(12,2)',
            'boolean': 'BOOLEAN',
            'bool': 'BOOLEAN',
            'datetime': 'TIMESTAMP',
            'date': 'DATE',
            'uuid': 'UUID',
            'array/relation': 'JSONB',
            'object/relation': 'JSONB',
            'nullable': 'VARCHAR(255)',
            'NoneType': 'VARCHAR(255)',
            'list': 'JSONB',
            'dict': 'JSONB',
        }
        
        sql_type = type_map.get(inferred_type, 'VARCHAR(255)')
        
        # Refine based on field name patterns
        name_lower = field_name.lower()
        if 'price' in name_lower or 'amount' in name_lower or 'total' in name_lower or 'cost' in name_lower:
            sql_type = 'DECIMAL(12,2)'
        elif 'email' in name_lower:
            sql_type = 'VARCHAR(255)'
        elif 'phone' in name_lower:
            sql_type = 'VARCHAR(20)'
        elif 'description' in name_lower or 'note' in name_lower or 'content' in name_lower:
            sql_type = 'TEXT'
        elif 'image' in name_lower or 'url' in name_lower or 'avatar' in name_lower or 'path' in name_lower:
            sql_type = 'TEXT'
        elif 'is_' in name_lower or 'has_' in name_lower or name_lower.startswith('active') or name_lower.startswith('enabled'):
            sql_type = 'BOOLEAN'
        elif 'date' in name_lower or 'time' in name_lower or name_lower.endswith('_at'):
            sql_type = 'TIMESTAMP'
        elif name_lower == 'id' or name_lower == '_id':
            sql_type = 'SERIAL'
        
        return sql_type
    
    def _infer_json_type(self, value):
        """Infer JSON Schema type from a value"""
        if value is None:
            return {"type": "string", "nullable": True}
        elif isinstance(value, bool):
            return {"type": "boolean"}
        elif isinstance(value, int):
            return {"type": "integer"}
        elif isinstance(value, float):
            return {"type": "number"}
        elif isinstance(value, str):
            return {"type": "string", "example": value[:50]}
        elif isinstance(value, list):
            return {"type": "array"}
        elif isinstance(value, dict):
            return {"type": "object", "properties": {k: self._infer_json_type(v) for k, v in value.items()}}
        return {"type": "string"}
    
    def _describe_json_structure(self, obj, depth=0):
        """Describe JSON structure recursively"""
        if depth > 3:
            return {"type": "object"}
        
        if isinstance(obj, dict):
            return {
                "type": "object",
                "properties": {k: self._describe_json_structure(v, depth+1) for k, v in obj.items()}
            }
        elif isinstance(obj, list):
            if obj and isinstance(obj[0], dict):
                return {"type": "array", "items": self._describe_json_structure(obj[0], depth+1)}
            return {"type": "array"}
        else:
            return self._infer_json_type(obj)
    
    def _route_to_component_name(self, route):
        """Convert route path to component name"""
        clean = route.replace('#/', '').replace('/', ' ').strip()
        if not clean:
            return 'Dashboard'
        parts = clean.split()
        return ''.join(word.capitalize() for word in parts) + 'Page'
