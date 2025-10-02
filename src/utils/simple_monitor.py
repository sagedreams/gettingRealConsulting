#!/usr/bin/env python3
"""
Simple Progress Monitor for Charter Schools Scraper
"""

import time
import os
import json
from datetime import datetime


def monitor_progress():
    """Monitor scraping progress."""
    print("🔍 Simple Charter Schools Scraper Monitor")
    print("=" * 50)
    
    # Look for the most recent output files
    csv_files = [f for f in os.listdir('.') if f.startswith('scraped_schools_') and f.endswith('.csv')]
    if not csv_files:
        print("⏳ No scraping results found yet...")
        return
    
    latest_csv = max(csv_files)
    print(f"📄 Monitoring: {latest_csv}")
    
    try:
        with open(latest_csv, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) <= 1:  # Only header
            print("⏳ Scraping in progress...")
            return
        
        # Count results
        total_schools = len(lines) - 1  # Subtract header
        successful = sum(1 for line in lines[1:] if ',200,' in line)
        failed = total_schools - successful
        
        print(f"📊 Progress: {total_schools} schools processed")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        if total_schools > 0:
            print(f"📈 Success rate: {successful/total_schools*100:.1f}%")
        
        # Show latest school
        if lines:
            latest_school = lines[-1].split(',')[1]  # School name
            print(f"🔄 Latest: {latest_school}")
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")


def main():
    """Main function."""
    try:
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            monitor_progress()
            print("\nPress Ctrl+C to stop monitoring")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")


if __name__ == "__main__":
    main()
