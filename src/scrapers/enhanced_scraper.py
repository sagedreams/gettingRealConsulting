#!/usr/bin/env python3
"""
Enhanced Charter Schools Scraper - Step 2: Multi-page Scraping

This version scrapes the home page AND all linked pages on the same domain.
"""

import requests
import csv
import json
import time
from datetime import datetime
from urllib.parse import urlparse, urljoin, urlunparse
from bs4 import BeautifulSoup
from collections import deque
import re


class SchoolScraper:
    def __init__(self, delay=2.0, max_pages_per_school=10):
        self.delay = delay
        self.max_pages_per_school = max_pages_per_school
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def get_domain(self, url):
        """Extract domain from URL."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def is_same_domain(self, url1, url2):
        """Check if two URLs are from the same domain."""
        return self.get_domain(url1) == self.get_domain(url2)
    
    def clean_url(self, url, base_url):
        """Clean and normalize URL."""
        # Handle relative URLs
        if url.startswith('/'):
            return urljoin(base_url, url)
        elif url.startswith('http'):
            return url
        else:
            return urljoin(base_url, url)
    
    def extract_links(self, soup, base_url, domain):
        """Extract all internal links from the page."""
        links = set()
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = self.clean_url(href, base_url)
            
            # Only include same-domain links
            if self.is_same_domain(full_url, base_url):
                # Remove fragments and query parameters for deduplication
                parsed = urlparse(full_url)
                clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
                links.add(clean_url)
        
        return list(links)
    
    def scrape_page(self, url):
        """Scrape a single page."""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic info
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            description = soup.find('meta', attrs={'name': 'description'})
            description_text = description.get('content', '').strip() if description else ""
            
            # Get main text content
            for script in soup(["script", "style"]):
                script.decompose()
            
            body = soup.find('body')
            text_content = body.get_text() if body else ""
            text_content = ' '.join(text_content.split())
            
            # Extract links for further crawling
            links = self.extract_links(soup, url, self.get_domain(url))
            
            return {
                'url': url,
                'status_code': response.status_code,
                'response_size': len(response.content),
                'title': title_text,
                'description': description_text,
                'text_content': text_content[:5000],  # Limit content
                'links_found': len(links),
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'url': url,
                'status_code': 0,
                'response_size': 0,
                'title': f"Error: {str(e)}",
                'description': "",
                'text_content': "",
                'links_found': 0,
                'scraped_at': datetime.now().isoformat()
            }
    
    def scrape_school_website(self, url, school_data):
        """Scrape a school website including all linked pages."""
        print(f"  🏠 Scraping home page: {url}")
        
        # Scrape home page
        home_page = self.scrape_page(url)
        home_page.update(school_data)
        home_page['page_type'] = 'home'
        
        all_pages = [home_page]
        visited_urls = {url}
        
        # Get links from home page
        if home_page['status_code'] == 200:
            try:
                response = self.session.get(url, timeout=30)
                soup = BeautifulSoup(response.content, 'html.parser')
                links = self.extract_links(soup, url, self.get_domain(url))
                
                print(f"  🔗 Found {len(links)} internal links")
                
                # Limit number of pages to scrape
                links_to_scrape = links[:self.max_pages_per_school - 1]  # -1 for home page
                
                for i, link in enumerate(links_to_scrape, 1):
                    if link not in visited_urls:
                        print(f"  📄 Scraping page {i+1}/{min(len(links_to_scrape)+1, self.max_pages_per_school)}: {link}")
                        
                        page_data = self.scrape_page(link)
                        page_data.update(school_data)
                        page_data['page_type'] = 'internal'
                        
                        all_pages.append(page_data)
                        visited_urls.add(link)
                        
                        # Be respectful - add delay between pages
                        time.sleep(self.delay)
                        
            except Exception as e:
                print(f"  ⚠️  Error extracting links: {e}")
        
        return all_pages
    
    def scrape_schools(self, schools):
        """Scrape multiple schools."""
        all_results = []
        
        for i, school in enumerate(schools, 1):
            print(f"Scraping {i}/{len(schools)}: {school['school_name']} ({school['domain']})")
            
            pages = self.scrape_school_website(school['website'], school)
            all_results.extend(pages)
            
            print(f"  ✅ Scraped {len(pages)} pages")
            
            # Be respectful - add delay between schools
            if i < len(schools):
                time.sleep(self.delay)
        
        return all_results


def load_schools_from_csv(csv_file):
    """Load school data from CSV."""
    schools = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['website']:
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


def save_results(results, output_dir="scraped_data"):
    """Save results in organized structure: separate JSON file per school."""
    import os
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Group results by school
    schools_data = {}
    for result in results:
        school_key = f"{result['cds_code']}_{result['school_name']}"
        if school_key not in schools_data:
            schools_data[school_key] = {
                'school_info': {
                    'cds_code': result['cds_code'],
                    'school_name': result['school_name'],
                    'county': result['county'],
                    'district': result['district'],
                    'email': result['email'],
                    'domain': result['domain'],
                    'website': result['website']
                },
                'pages': {}
            }
        
        # Add page data with URL as key
        schools_data[school_key]['pages'][result['url']] = {
            'title': result['title'],
            'description': result['description'],
            'text_content': result['text_content'],
            'status_code': result['status_code'],
            'response_size': result['response_size'],
            'links_found': result['links_found'],
            'page_type': result['page_type'],
            'scraped_at': result['scraped_at']
        }
    
    # Save each school as separate JSON file
    saved_files = []
    for school_key, school_data in schools_data.items():
        # Clean filename (remove special characters)
        safe_filename = re.sub(r'[^\w\s-]', '', school_key).strip()
        safe_filename = re.sub(r'[-\s]+', '_', safe_filename)
        
        json_file = os.path.join(output_dir, f"{safe_filename}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(school_data, f, ensure_ascii=False, indent=2)
        
        saved_files.append(json_file)
    
    # Also save a summary CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_csv = os.path.join(output_dir, f"scraping_summary_{timestamp}.csv")
    
    with open(summary_csv, 'w', newline='', encoding='utf-8') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    return saved_files, summary_csv


def main():
    """Main function."""
    import argparse
    from pathlib import Path
    
    # Set default paths based on project structure
    project_root = Path(__file__).parent.parent.parent
    default_csv = project_root / "data" / "processed" / "charter_schools_for_scraping.csv"
    default_output = project_root / "data" / "scraped"
    
    parser = argparse.ArgumentParser(description='Enhanced Charter Schools Scraper - Multi-page')
    parser.add_argument('--csv-file', default=str(default_csv),
                       help='CSV file with school data')
    parser.add_argument('--delay', type=float, default=2.0,
                       help='Delay between requests in seconds')
    parser.add_argument('--max-pages', type=int, default=10,
                       help='Maximum pages to scrape per school')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of schools to scrape (for testing)')
    parser.add_argument('--output-dir', default=str(default_output),
                       help='Output directory for scraped data')
    
    args = parser.parse_args()
    
    print("🚀 Enhanced Charter Schools Scraper - Multi-page")
    print(f"📁 CSV file: {args.csv_file}")
    print(f"⏱️  Delay: {args.delay} seconds")
    print(f"📄 Max pages per school: {args.max_pages}")
    if args.limit:
        print(f"🔢 Limit: {args.limit} schools")
    
    # Load schools
    schools = load_schools_from_csv(args.csv_file)
    if args.limit:
        schools = schools[:args.limit]
    
    print(f"📊 Total schools to scrape: {len(schools)}")
    
    # Create scraper
    scraper = SchoolScraper(delay=args.delay, max_pages_per_school=args.max_pages)
    
    # Scrape schools
    results = scraper.scrape_schools(schools)
    
    # Save results
    saved_files, summary_csv = save_results(results, args.output_dir)
    
    print(f"\n✅ Scraping completed!")
    print(f"📄 Results saved to:")
    print(f"   📁 Directory: {args.output_dir}")
    print(f"   📄 School files: {len(saved_files)} JSON files")
    print(f"   📄 Summary CSV: {summary_csv}")
    
    # Summary
    total_pages = len(results)
    successful_pages = sum(1 for r in results if r['status_code'] == 200)
    failed_pages = total_pages - successful_pages
    
    home_pages = sum(1 for r in results if r.get('page_type') == 'home')
    internal_pages = sum(1 for r in results if r.get('page_type') == 'internal')
    
    print(f"\n📊 Summary:")
    print(f"   🏠 Home pages: {home_pages}")
    print(f"   📄 Internal pages: {internal_pages}")
    print(f"   📊 Total pages: {total_pages}")
    print(f"   ✅ Successful: {successful_pages}")
    print(f"   ❌ Failed: {failed_pages}")
    print(f"   📈 Success rate: {successful_pages/total_pages*100:.1f}%")


if __name__ == "__main__":
    main()
