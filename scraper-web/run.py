#!/usr/bin/env python3
"""
Generic SPA Scraper CLI - Scrape any SPA website
Usage: python run.py <url> <username> <password> [--output <dir>]
"""

import asyncio
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from scraper import SPAScraper
from analyzer import LLMAnalyzer

def main():
    parser = argparse.ArgumentParser(description='SPA Web Scraper - Reverse engineer any SPA')
    parser.add_argument('url', help='Target URL (e.g., https://app.example.com/#/dashboard)')
    parser.add_argument('--username', '-u', help='Login username')
    parser.add_argument('--password', '-p', help='Login password')
    parser.add_argument('--output', '-o', default='./scrape_output', help='Output directory')
    parser.add_argument('--no-login', action='store_true', help='Skip login (public site)')
    parser.add_argument('--analyze-only', action='store_true', help='Only run analysis on existing scrape data')
    
    args = parser.parse_args()
    
    config = {
        'base_url': args.url,
        'output_dir': args.output,
        'login': {
            'username': args.username or '',
            'password': args.password or '',
        },
    }
    
    if args.analyze_only:
        print("Running analysis on existing data...")
        analyzer = LLMAnalyzer(args.output)
        analyzer.load_scrape_data()
        analyzer.generate_replication_blueprint()
        print(f"Blueprint saved to {args.output}/BLUEPRINT.md")
        return
    
    async def run():
        scraper = SPAScraper(config)
        await scraper.start()
        
        analyzer = LLMAnalyzer(config['output_dir'])
        analyzer.load_scrape_data()
        analyzer.generate_replication_blueprint()
    
    asyncio.run(run())

if __name__ == '__main__':
    main()
