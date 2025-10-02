#!/usr/bin/env python3
"""
Simple Charter Schools Scraper

A lean, straightforward scraper that just gets the job done.
"""

import requests
import csv
import json
import time
from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def scrape_school_website(url, school_data):
    """Scrape a single school website."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract basic info
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ""
        
        description = soup.find('meta', attrs={'name': 'description'})
        description_text = description.get('content', '').strip() if description else ""
        
        # Get main text content
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text from body
        body = soup.find('body')
        text_content = body.get_text() if body else ""
        
        # Clean up text
        text_content = ' '.join(text_content.split())
        
        return {
            'cds_code': school_data['cds_code'],
            'school_name': school_data['school_name'],
            'county': school_data['county'],
            'district': school_data['district'],
            'email': school_data['email'],
            'domain': school_data['domain'],
            'url': url,
            'status_code': response.status_code,
            'response_size': len(response.content),
            'scraped_at': datetime.now().isoformat(),
            'title': title_text,
            'description': description_text,
            'text_content': text_content[:5000],  # Limit to 5000 chars
            'clean_text': f"School: {school_data['school_name']}, County: {school_data['county']}, District: {school_data['district']}, Title: {title_text}, Description: {description_text}, Content: {text_content[:2000]}"
        }
        
    except Exception as e:
        return {
            'cds_code': school_data['cds_code'],
            'school_name': school_data['school_name'],
            'county': school_data['county'],
            'district': school_data['district'],
            'email': school_data['email'],
            'domain': school_data['domain'],
            'url': url,
            'status_code': 0,
            'response_size': 0,
            'scraped_at': datetime.now().isoformat(),
            'title': f"Error: {str(e)}",
            'description': "",
            'text_content': "",
            'clean_text': f"School: {school_data['school_name']}, URL: {url}, Error: {str(e)}"
        }


def load_schools_from_csv(csv_file):
    """Load school data from CSV."""
    schools = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['website']:  # Only process schools with websites
                schools.append({
                    'cds_code': row['cds_code'],
                    'school_name': row['school_name'],
                    'county': row['county'],
                    'district': row['district'],
                    'email': row['email'],
                    'domain': row['domain'],
                    'website': row['website']
                })
    return schools


def save_results(results, output_prefix):
    """Save results to CSV and JSONL."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save CSV
    csv_file = f"{output_prefix}_{timestamp}.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    # Save JSONL
    jsonl_file = f"{output_prefix}_{timestamp}.jsonl"
    with open(jsonl_file, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')
    
    return csv_file, jsonl_file


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple Charter Schools Scraper')
    parser.add_argument('--csv-file', default='charter_schools_for_scraping.csv',
                       help='CSV file with school data')
    parser.add_argument('--delay', type=float, default=2.0,
                       help='Delay between requests in seconds')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of schools to scrape (for testing)')
    parser.add_argument('--output-prefix', default='scraped_schools',
                       help='Output file prefix')
    
    args = parser.parse_args()
    
    print("🚀 Starting Simple Charter Schools Scraper")
    print(f"📁 CSV file: {args.csv_file}")
    print(f"⏱️  Delay: {args.delay} seconds")
    if args.limit:
        print(f"🔢 Limit: {args.limit} schools")
    
    # Load schools
    schools = load_schools_from_csv(args.csv_file)
    if args.limit:
        schools = schools[:args.limit]
    
    print(f"📊 Total schools to scrape: {len(schools)}")
    
    # Scrape schools
    results = []
    for i, school in enumerate(schools, 1):
        print(f"Scraping {i}/{len(schools)}: {school['school_name']} ({school['domain']})")
        
        result = scrape_school_website(school['website'], school)
        results.append(result)
        
        # Be respectful - add delay
        if i < len(schools):  # Don't delay after the last request
            time.sleep(args.delay)
    
    # Save results
    csv_file, jsonl_file = save_results(results, args.output_prefix)
    
    print(f"\n✅ Scraping completed!")
    print(f"📄 Results saved to:")
    print(f"   - {csv_file}")
    print(f"   - {jsonl_file}")
    
    # Summary
    successful = sum(1 for r in results if r['status_code'] == 200)
    failed = len(results) - successful
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success rate: {successful/len(results)*100:.1f}%")


if __name__ == "__main__":
    main()
