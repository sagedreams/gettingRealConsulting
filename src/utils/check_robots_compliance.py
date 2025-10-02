#!/usr/bin/env python3
"""
Robots.txt Compliance Checker

This script checks robots.txt compliance for all school websites
before starting the scraping process.
"""

import csv
import requests
from urllib.parse import urlparse, urljoin
import time
import sys


def get_robots_txt(domain):
    """Get robots.txt content for a domain."""
    try:
        robots_url = f"https://{domain}/robots.txt"
        response = requests.get(robots_url, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except Exception as e:
        return None


def check_robots_compliance(domain, user_agent="*"):
    """Check if a domain allows scraping for a user agent."""
    robots_content = get_robots_txt(domain)
    
    if not robots_content:
        return {
            'status': 'no_robots',
            'message': 'No robots.txt found or accessible',
            'allows_scraping': True  # Assume allowed if no robots.txt
        }
    
    lines = robots_content.lower().split('\n')
    current_user_agent = None
    disallowed_paths = []
    crawl_delay = None
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        if line.startswith('user-agent:'):
            current_user_agent = line.split(':', 1)[1].strip()
        elif line.startswith('disallow:'):
            if current_user_agent == user_agent or current_user_agent == '*':
                path = line.split(':', 1)[1].strip()
                if path:
                    disallowed_paths.append(path)
        elif line.startswith('crawl-delay:'):
            if current_user_agent == user_agent or current_user_agent == '*':
                try:
                    crawl_delay = int(line.split(':', 1)[1].strip())
                except ValueError:
                    pass
    
    # Check if root path is disallowed
    root_disallowed = any(path == '/' or path == '' for path in disallowed_paths)
    
    return {
        'status': 'checked',
        'message': f"Robots.txt found",
        'allows_scraping': not root_disallowed,
        'disallowed_paths': disallowed_paths,
        'crawl_delay': crawl_delay,
        'robots_content': robots_content
    }


def check_all_schools(csv_file):
    """Check robots.txt compliance for all schools."""
    print("🤖 Checking robots.txt compliance for all school websites...")
    print("=" * 60)
    
    results = []
    total_schools = 0
    compliant_schools = 0
    non_compliant_schools = 0
    no_robots_schools = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_schools += 1
            domain = row['domain']
            school_name = row['school_name']
            url = row['website']
            
            print(f"Checking {total_schools:3d}/894: {school_name[:40]:<40} ({domain})")
            
            compliance = check_robots_compliance(domain)
            results.append({
                'school_name': school_name,
                'domain': domain,
                'url': url,
                'compliance': compliance
            })
            
            if compliance['allows_scraping']:
                if compliance['status'] == 'no_robots':
                    no_robots_schools += 1
                    print(f"  ✅ No robots.txt - assuming allowed")
                else:
                    compliant_schools += 1
                    print(f"  ✅ Robots.txt allows scraping")
            else:
                non_compliant_schools += 1
                print(f"  ❌ Robots.txt disallows scraping")
                if compliance.get('disallowed_paths'):
                    print(f"      Disallowed paths: {compliance['disallowed_paths']}")
            
            # Be respectful - small delay between checks
            time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("📊 ROBOTS.TXT COMPLIANCE SUMMARY")
    print("=" * 60)
    print(f"Total schools checked: {total_schools}")
    print(f"✅ Compliant (allows scraping): {compliant_schools}")
    print(f"❌ Non-compliant (disallows scraping): {non_compliant_schools}")
    print(f"❓ No robots.txt found: {no_robots_schools}")
    print(f"📈 Compliance rate: {(compliant_schools + no_robots_schools) / total_schools * 100:.1f}%")
    
    # Show non-compliant schools
    if non_compliant_schools > 0:
        print("\n🚫 SCHOOLS THAT DISALLOW SCRAPING:")
        print("-" * 40)
        for result in results:
            if not result['compliance']['allows_scraping']:
                print(f"❌ {result['school_name']} ({result['domain']})")
                if result['compliance'].get('disallowed_paths'):
                    print(f"   Disallowed: {result['compliance']['disallowed_paths']}")
    
    # Show schools with crawl delays
    crawl_delay_schools = [r for r in results if r['compliance'].get('crawl_delay')]
    if crawl_delay_schools:
        print(f"\n⏰ SCHOOLS WITH CRAWL DELAYS:")
        print("-" * 40)
        for result in crawl_delay_schools:
            delay = result['compliance']['crawl_delay']
            print(f"⏰ {result['school_name']} ({result['domain']}) - {delay}s delay")
    
    return results


def main():
    """Main function."""
    csv_file = "charter_schools_for_scraping.csv"
    
    if not csv_file:
        print("❌ CSV file not found!")
        print("Please run: python extract_charter_data.py")
        sys.exit(1)
    
    try:
        results = check_all_schools(csv_file)
        
        print("\n" + "=" * 60)
        print("🎯 RECOMMENDATIONS")
        print("=" * 60)
        
        non_compliant_count = sum(1 for r in results if not r['compliance']['allows_scraping'])
        
        if non_compliant_count == 0:
            print("✅ All schools allow scraping! You can proceed safely.")
        elif non_compliant_count < 10:
            print(f"⚠️  {non_compliant_count} schools disallow scraping.")
            print("Consider excluding these schools or contacting them for permission.")
        else:
            print(f"❌ {non_compliant_count} schools disallow scraping.")
            print("You should review the non-compliant list and consider alternatives.")
        
        print("\n💡 To proceed with ethical scraping:")
        print("   python run_charter_scraper.py --safe-mode --monitor")
        
    except KeyboardInterrupt:
        print("\n\n👋 Compliance check interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during compliance check: {e}")


if __name__ == "__main__":
    main()
