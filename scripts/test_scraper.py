#!/usr/bin/env python3
"""
Test Charter Schools Scraper

This script tests the scraper with a small subset of schools.
"""

import os
import csv
import subprocess
import tempfile
from datetime import datetime


def create_test_csv():
    """Create a small test CSV with just a few schools."""
    
    # Read the full CSV
    full_csv = 'charter_schools_for_scraping.csv'
    test_csv = 'test_schools.csv'
    
    if not os.path.exists(full_csv):
        print(f"Error: {full_csv} not found!")
        return None
    
    # Create test CSV with first 5 schools
    with open(full_csv, 'r', encoding='utf-8') as infile, \
         open(test_csv, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        
        count = 0
        for row in reader:
            if count >= 5:  # Only take first 5 schools
                break
            writer.writerow(row)
            count += 1
    
    print(f"Created test CSV with {count} schools: {test_csv}")
    return test_csv


def run_test_scraper():
    """Run the scraper in test mode."""
    
    # Create test CSV
    test_csv = create_test_csv()
    if not test_csv:
        return False
    
    # Run scraper with test settings
    cmd = [
        'python', 'run_charter_scraper.py',
        '--csv-file', test_csv,
        '--concurrent-requests', '2',
        '--delay', '2.0',
        '--test'
    ]
    
    print("Running test scraper...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("-" * 50)
        print("✅ Test scraper completed successfully!")
        
        # Clean up test CSV
        if os.path.exists(test_csv):
            os.remove(test_csv)
            print(f"Cleaned up test file: {test_csv}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Test scraper failed: {e}")
        return False
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        return False


if __name__ == "__main__":
    print("Charter Schools Scraper Test")
    print("=" * 40)
    
    success = run_test_scraper()
    
    if success:
        print("\n🎉 Test passed! The scraper is ready to use.")
        print("\nTo run the full scraper:")
        print("python run_charter_scraper.py")
        print("\nFor help:")
        print("python run_charter_scraper.py --help")
    else:
        print("\n💥 Test failed! Please check the configuration.")
