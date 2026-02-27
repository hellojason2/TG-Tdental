"""
Website Replicator — AI Code Generation Engine

Takes crawl results (screenshots, DOM, API map, schema, design tokens)
and generates a complete Next.js + Ant Design codebase via Claude/GPT.

Endpoints:
  POST /generate          → Generate full codebase from crawl results
  POST /generate/page     → Generate a single page component
  POST /generate/schema   → Generate Prisma schema from API map
  POST /generate/prompt   → Generate Cursor mega-prompt (no AI key needed)
  GET  /health            → Health check
"""
import asyncio
import base64
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Website Replicator — AI Engine",
    description="Generate full-stack code from crawl data.",
    version="2.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ─── Models ───────────────────────────────────────────

class GenerateRequest(BaseModel):
    job_id: str = Field(..., description="Crawl job ID to generate from")
    provider: str = Field("anthropic", description="AI provider: anthropic | openai | kimi")
    model: str = Field("claude-sonnet-4-20250514", description="Model to use")
    framework: str = Field("nextjs", description="Output framework")
    ui_library: str = Field("antd", description="UI library: antd | shadcn | mui")
    css_framework: str = Field("tailwind", description="CSS: tailwind | css-modules")
    orm: str = Field("prisma", description="ORM: prisma | drizzle")
    locale: str = Field("vi-VN", description="Locale for i18n")


class PageGenRequest(BaseModel):
    job_id: str
    route: str = Field(..., description="Route to generate, e.g. /partners")
    provider: str = "anthropic"
    model: str = "claude-sonnet-4-20250514"


class PromptRequest(BaseModel):
    job_id: str


# ─── Helpers ──────────────────────────────────────────

def _load_crawl_data(job_id: str) -> dict:
    """Load all crawl artifacts for a job"""
    base = f"/app/data/{job_id}"
    if not os.path.exists(base):
        raise HTTPException(404, f"No crawl data found for job {job_id}. Run a crawl first.")

    def load_json(path):
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return None

    return {
        "routes": load_json(f"{base}/routes.json") or [],
        "api_map": load_json(f"{base}/api_map.json") or {},
        "db_schema": load_json(f"{base}/db_schema.json") or {},
        "design_tokens": load_json(f"{base}/design_tokens.json") or {},
        "stats": load_json(f"{base}/stats.json") or {},
        "dom_dir": f"{base}/dom",
        "screenshots_dir": f"{base}/screenshots",
    }


def _load_screenshot_b64(path: str) -> Optional[str]:
    """Load a screenshot as base64 for vision API"""
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


async def _call_anthropic(system: str, user_content: list, model: str = "claude-sonnet-4-20250514") -> str:
    """Call Anthropic Claude API"""
    import anthropic
    client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    response = await client.messages.create(
        model=model,
        max_tokens=8192,
        system=system,
        messages=[{"role": "user", "content": user_content}],
    )
    return response.content[0].text


async def _call_openai(system: str, user_content: list, model: str = "gpt-4o") -> str:
    """Call OpenAI API"""
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    messages = [{"role": "system", "content": system}]
    # Convert Anthropic-style content to OpenAI format
    oai_content = []
    for block in user_content:
        if isinstance(block, dict) and block.get("type") == "image":
            oai_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{block['source']['data']}"}
            })
        elif isinstance(block, dict) and block.get("type") == "text":
            oai_content.append({"type": "text", "text": block["text"]})
        elif isinstance(block, str):
            oai_content.append({"type": "text", "text": block})
    messages.append({"role": "user", "content": oai_content})
    response = await client.chat.completions.create(model=model, messages=messages, max_tokens=8192)
    return response.choices[0].message.content


async def _call_kimi(system: str, user_content: list, model: str = "kimi-2.5-flash") -> str:
    """Call Kimi (Moonshot AI) API"""
    from openai import AsyncOpenAI
    client = AsyncOpenAI(
        api_key=os.environ.get("KIMI_API_KEY"),
        base_url="https://api.moonshot.cn/v1"
    )
    messages = [{"role": "system", "content": system}]
    # Convert Anthropic-style content to OpenAI-compatible Kimi format
    oai_content = []
    for block in user_content:
        if isinstance(block, dict) and block.get("type") == "image":
            oai_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{block['source']['data']}"}
            })
        elif isinstance(block, dict) and block.get("type") == "text":
            oai_content.append({"type": "text", "text": block["text"]})
        elif isinstance(block, str):
            oai_content.append({"type": "text", "text": block})
    messages.append({"role": "user", "content": oai_content})
    response = await client.chat.completions.create(model=model, messages=messages, max_tokens=8192)
    return response.choices[0].message.content


async def _call_ai(provider: str, model: str, system: str, user_content: list) -> str:
    if provider == "anthropic":
        return await _call_anthropic(system, user_content, model)
    elif provider == "openai":
        return await _call_openai(system, user_content, model)
    elif provider == "kimi":
        return await _call_kimi(system, user_content, model)
    raise HTTPException(400, f"Unknown provider: {provider}")


# ─── Endpoints ────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai-engine", "timestamp": datetime.now().isoformat()}


@app.post("/generate/prompt")
async def generate_cursor_prompt(req: PromptRequest):
    """
    Generate a Cursor/Claude Code mega-prompt from crawl data.
    NO AI API KEY NEEDED — this just assembles the prompt text.
    """
    data = _load_crawl_data(req.job_id)

    prompt = f"""# Website Replication — Cursor Mega-Prompt
# Generated from crawl job: {req.job_id}
# Generated at: {datetime.now().isoformat()}

## MISSION
Recreate this website as a Next.js 14 App Router application with TypeScript,
Ant Design 5, and Tailwind CSS. Use Prisma ORM with PostgreSQL.

## ROUTES ({len(data['routes'])} discovered)
```json
{json.dumps(data['routes'][:50], indent=2)}
```

## API CONTROLLERS (grouped by domain)
```json
{json.dumps(data['api_map'], indent=2, default=str)[:8000]}
```

## DATABASE SCHEMA (inferred from API responses)
```json
{json.dumps(data['db_schema'], indent=2)[:6000]}
```

## DESIGN TOKENS
```json
{json.dumps(data['design_tokens'], indent=2)[:4000]}
```

## ARCHITECTURE RULES
1. App Router with route groups: (auth), (dashboard), (public)
2. Server Components by default, 'use client' only for interactivity
3. Ant Design ConfigProvider with Vietnamese locale
4. NextAuth.js for JWT authentication
5. Prisma schema matching the inferred DB schema above
6. Vietnamese text (DD/MM/YYYY dates, VND currency formatting)
7. Responsive sidebar layout matching the original design tokens
8. API routes under /api/[controller]/route.ts mirroring the captured API map

## FILE STRUCTURE
```
src/
├── app/
│   ├── (auth)/login/page.tsx
│   ├── (dashboard)/layout.tsx      # Sidebar + header
│   ├── (dashboard)/[module]/page.tsx
│   └── api/[...controller]/route.ts
├── components/
│   ├── layout/Sidebar.tsx
│   ├── layout/Header.tsx
│   └── shared/DataTable.tsx
├── lib/
│   ├── prisma.ts
│   ├── auth.ts
│   └── api-client.ts
├── prisma/schema.prisma
└── styles/globals.css
```

## GENERATE EACH ROUTE
For each route in the routes list, create a page.tsx that:
1. Matches the DOM structure from the crawl data
2. Uses the design tokens for styling
3. Calls the correct API endpoints from the API map
4. Handles Vietnamese locale formatting
"""

    # Save prompt to file
    output_path = f"/app/data/{req.job_id}/cursor_prompt.md"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(prompt)

    return {
        "prompt": prompt,
        "saved_to": output_path,
        "routes_count": len(data["routes"]),
        "controllers_count": len(data["api_map"]),
        "tables_count": len(data["db_schema"]),
    }


@app.post("/generate/schema")
async def generate_prisma_schema(req: GenerateRequest):
    """Generate Prisma schema from inferred DB schema"""
    data = _load_crawl_data(req.job_id)

    system = """You are a database architect. Convert the inferred JSON schema into a Prisma schema file.
Rules:
- Use UUID for all id fields
- Add createdAt/updatedAt timestamps
- Infer relations from field names (e.g. partnerId → Partner)
- Use Vietnamese-friendly field names where appropriate
- Add proper indexes on foreign keys and commonly queried fields
Output ONLY the prisma schema file content, no explanation."""

    user_content = [
        {"type": "text", "text": f"Inferred DB schema from API responses:\n```json\n{json.dumps(data['db_schema'], indent=2)}\n```\n\nAPI controllers:\n```json\n{json.dumps(list(data['api_map'].keys()))}\n```"}
    ]

    result = await _call_ai(req.provider, req.model, system, user_content)

    output_path = f"/app/data/{req.job_id}/generated/prisma/schema.prisma"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(result)

    return {"schema": result, "saved_to": output_path}


@app.post("/generate/page")
async def generate_single_page(req: PageGenRequest):
    """Generate a single page component from screenshot + DOM"""
    data = _load_crawl_data(req.job_id)
    import re
    safe = re.sub(r'[^a-zA-Z0-9_-]', '_', req.route.strip('/').replace('#', ''))[:80] or "index"

    # Load DOM for this route
    dom_path = f"{data['dom_dir']}/{safe}.json"
    dom = None
    if os.path.exists(dom_path):
        with open(dom_path) as f:
            dom = json.load(f)

    # Load screenshot
    ss_path = f"{data['screenshots_dir']}/{safe}.png"
    screenshot_b64 = _load_screenshot_b64(ss_path)

    system = """You are a senior React/Next.js developer. Generate a complete page component.
Rules:
- Next.js 14 App Router with TypeScript
- Ant Design 5 components (Table, Form, Button, Card, Modal, etc.)
- Tailwind CSS for custom styling
- Match the screenshot layout EXACTLY
- Use the DOM tree for structure reference
- Add proper TypeScript interfaces
- Include mock data that matches the API response structure
- Vietnamese locale (DD/MM/YYYY, VND currency)
Output ONLY the TSX code, no explanation."""

    user_content = []
    if screenshot_b64:
        user_content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": "image/png", "data": screenshot_b64},
        })
    user_content.append({
        "type": "text",
        "text": f"Route: {req.route}\n\nDOM structure:\n```json\n{json.dumps(dom, indent=2, default=str)[:6000] if dom else 'N/A'}\n```\n\nDesign tokens:\n```json\n{json.dumps(data.get('design_tokens', {}), indent=2)[:2000]}\n```\n\nAPI endpoints for this page:\n```json\n{json.dumps(data.get('api_map', {}).get(safe, []), indent=2, default=str)[:2000]}\n```"
    })

    result = await _call_ai(req.provider, req.model, system, user_content)

    output_path = f"/app/data/{req.job_id}/generated/pages/{safe}.tsx"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(result)

    return {"code": result, "saved_to": output_path, "route": req.route}


@app.post("/generate")
async def generate_full(req: GenerateRequest):
    """Generate the complete codebase — runs page-by-page"""
    data = _load_crawl_data(req.job_id)

    results = {
        "job_id": req.job_id,
        "pages_generated": 0,
        "errors": [],
        "files": [],
    }

    # 1. Generate Prisma schema
    try:
        schema_result = await generate_prisma_schema(req)
        results["files"].append(schema_result["saved_to"])
    except Exception as e:
        results["errors"].append(f"Schema: {e}")

    # 2. Generate Cursor prompt (always works, no AI needed)
    try:
        prompt_result = await generate_cursor_prompt(PromptRequest(job_id=req.job_id))
        results["files"].append(prompt_result["saved_to"])
    except Exception as e:
        results["errors"].append(f"Prompt: {e}")

    # 3. Generate each page (with rate limiting)
    for route in data["routes"][:30]:  # Cap at 30 pages per run
        try:
            page_req = PageGenRequest(
                job_id=req.job_id, route=route,
                provider=req.provider, model=req.model,
            )
            page_result = await generate_single_page(page_req)
            results["files"].append(page_result["saved_to"])
            results["pages_generated"] += 1
            await asyncio.sleep(1)  # Rate limit
        except Exception as e:
            results["errors"].append(f"{route}: {e}")

    return results
