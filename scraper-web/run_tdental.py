#!/usr/bin/env python3
"""
Run scraper on TDental - Vietnamese dental clinic management system
"""

import asyncio
import sys
import os

os.environ.setdefault("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))

sys.path.insert(0, os.path.dirname(__file__))
from scraper import SPAScraper
from analyzer import LLMAnalyzer

CONFIG = {
    'base_url': 'https://tamdentist.tdental.vn/#/dashboard',
    'output_dir': './scrape_output/tdental',
    'login': {
        'username': 'dataconnect',
        'password': 'dataconnect@',
        # Auto-detect login form (leave selectors empty)
        'username_selector': None,
        'password_selector': None,
        'submit_selector': None,
    },
}

async def main():
    print("=" * 60)
    print("  TDental SPA Scraper")
    print("=" * 60)
    
    # Step 1: Scrape the site
    scraper = SPAScraper(CONFIG)
    await scraper.start()
    
    # Step 2: Analyze with LLM
    print("\n" + "=" * 60)
    print("  Running LLM Analysis")
    print("=" * 60)
    
    analyzer = LLMAnalyzer(CONFIG['output_dir'], provider='groq')
    analyzer.load_scrape_data()
    
    # Generate all artifacts
    print("\n[1/4] Generating database schema...")
    sql = analyzer.generate_database_schema()
    print(f"  ✅ Saved database_schema.sql")
    
    print("[2/4] Generating API specification...")
    spec = analyzer.generate_api_spec()
    print(f"  ✅ Saved api_specification.json ({len(spec.get('endpoints', {}))} endpoints)")
    
    print("[3/4] Generating component tree...")
    tree = analyzer.generate_component_tree()
    print(f"  ✅ Saved component_tree.json ({len(tree.get('pages', {}))} pages)")
    
    print("[4/4] Generating replication blueprint...")
    blueprint = analyzer.generate_replication_blueprint()
    print(f"  ✅ Saved BLUEPRINT.md")
    
    print("\n" + "=" * 60)
    print("  ALL DONE!")
    print(f"  Output directory: {CONFIG['output_dir']}")
    print("=" * 60)

if __name__ == '__main__':
    asyncio.run(main())
