#!/usr/bin/env python3
"""
Simple Charter Schools JSONL Analysis Script

Analyzes the charter schools JSONL file to extract and analyze unique websites.
"""

import json
from collections import Counter
import re

def analyze_charter_jsonl(jsonl_file):
    """Analyze charter schools from JSONL file."""
    
    print(f"Loading charter schools from {jsonl_file}...")
    
    websites = []
    total_schools = 0
    
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                total_schools += 1
                data = json.loads(line)
                web_addr = data.get('web address', '').strip()
                
                # Clean up the web address
                if web_addr and web_addr != 'Information Not Available':
                    # Remove "Link opens new browser tab" suffix
                    clean_url = web_addr.replace(' Link opens new browser tab', '').strip()
                    if clean_url:
                        websites.append(clean_url)
    
    # Count unique websites
    website_counts = Counter(websites)
    
    print(f"\n=== CHARTER SCHOOLS ANALYSIS ===")
    print(f"Total schools: {total_schools}")
    print(f"Schools with websites: {len(websites)}")
    print(f"Schools without websites: {total_schools - len(websites)}")
    print(f"Unique websites: {len(website_counts)}")
    print()
    
    print("=== WEBSITE DISTRIBUTION ===")
    single_use = sum(1 for count in website_counts.values() if count == 1)
    multi_use = len(website_counts) - single_use
    
    print(f"Websites used by only 1 school: {single_use}")
    print(f"Websites used by multiple schools: {multi_use}")
    print()
    
    print("=== TOP 20 MOST COMMON WEBSITES ===")
    for i, (website, count) in enumerate(website_counts.most_common(20), 1):
        percentage = (count / len(websites)) * 100
        print(f"{i:2d}. {website:<50} ({count:2d} schools, {percentage:.1f}%)")
    
    return website_counts

if __name__ == "__main__":
    jsonl_file = "schools_charter_20250919_002920.jsonl"
    website_counts = analyze_charter_jsonl(jsonl_file)
    print("\nAnalysis complete!")
