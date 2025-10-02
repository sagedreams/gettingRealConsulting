#!/usr/bin/env python3
"""
Extract Charter Schools Data for Scraping

This script extracts cds_code, website, and email from the charter schools JSONL file
and creates a CSV file for the scraper to use.
"""

import json
import csv
import re
from urllib.parse import urlparse

def clean_website_url(web_addr):
    """Clean and normalize website URL."""
    if not web_addr or web_addr == 'Information Not Available':
        return None
    
    # Remove "Link opens new browser tab" suffix
    clean_url = web_addr.replace(' Link opens new browser tab', '').strip()
    
    if not clean_url:
        return None
    
    # Add protocol if missing
    if not clean_url.startswith(('http://', 'https://')):
        clean_url = 'https://' + clean_url
    
    return clean_url

def extract_domain(url):
    """Extract domain from URL for deduplication."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except:
        return None

def extract_charter_data(jsonl_file, output_csv):
    """Extract charter schools data from JSONL to CSV."""
    
    print(f"Extracting data from {jsonl_file}...")
    
    schools_data = []
    seen_domains = set()
    duplicate_count = 0
    
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if line.strip():
                try:
                    data = json.loads(line)
                    
                    cds_code = data.get('cds_code', '').strip()
                    email = data.get('email', '').strip()
                    web_addr = data.get('web address', '').strip()
                    
                    # Clean website URL
                    clean_url = clean_website_url(web_addr)
                    
                    if clean_url:
                        domain = extract_domain(clean_url)
                        
                        # Check for duplicates based on domain
                        if domain and domain in seen_domains:
                            duplicate_count += 1
                            print(f"Duplicate domain found: {domain} (line {line_num})")
                            continue
                        
                        if domain:
                            seen_domains.add(domain)
                        
                        schools_data.append({
                            'cds_code': cds_code,
                            'website': clean_url,
                            'email': email,
                            'domain': domain,
                            'school_name': data.get('school', '').strip(),
                            'county': data.get('county', '').strip(),
                            'district': data.get('district', '').strip()
                        })
                
                except json.JSONDecodeError as e:
                    print(f"Error parsing line {line_num}: {e}")
                    continue
    
    # Write to CSV
    print(f"Writing {len(schools_data)} unique schools to {output_csv}...")
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['cds_code', 'website', 'email', 'domain', 'school_name', 'county', 'district']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(schools_data)
    
    print(f"Extraction complete!")
    print(f"Total schools processed: {line_num}")
    print(f"Unique schools with websites: {len(schools_data)}")
    print(f"Duplicate domains skipped: {duplicate_count}")
    print(f"Output saved to: {output_csv}")
    
    return schools_data

if __name__ == "__main__":
    jsonl_file = "schools_charter_20250919_002920.jsonl"
    output_csv = "charter_schools_for_scraping.csv"
    
    schools_data = extract_charter_data(jsonl_file, output_csv)
