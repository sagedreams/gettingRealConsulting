#!/usr/bin/env python3
"""
Charter Schools Scraper Runner

This script runs the Scrapy spider to scrape charter school websites.
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime


def run_scraper(csv_file=None, concurrent_requests=32, delay=1, output_dir=None):
    """
    Run the charter schools scraper.
    
    Args:
        csv_file (str): Path to CSV file with school data
        concurrent_requests (int): Number of concurrent requests
        delay (int): Delay between requests in seconds
        output_dir (str): Output directory for scraped data
    """
    
    # Change to scraper directory
    scraper_dir = os.path.join(os.path.dirname(__file__), 'charter_scraper')
    
    if not os.path.exists(scraper_dir):
        print(f"Error: Scraper directory not found: {scraper_dir}")
        return False
    
    # Default CSV file
    if not csv_file:
        csv_file = os.path.join(os.path.dirname(__file__), 'charter_schools_for_scraping.csv')
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found: {csv_file}")
        return False
    
    # Create output directory if specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        os.chdir(output_dir)
    
    # Build scrapy command
    # Convert to absolute path for the spider
    abs_csv_file = os.path.abspath(csv_file)
    
    cmd = [
        'scrapy', 'crawl', 'school_spider',
        '-a', f'csv_file={abs_csv_file}',
        '-s', f'CONCURRENT_REQUESTS={concurrent_requests}',
        '-s', f'DOWNLOAD_DELAY={delay}',
        '-s', 'RANDOMIZE_DOWNLOAD_DELAY=1',
        '-L', 'INFO'
    ]
    
    print(f"Starting charter schools scraper...")
    print(f"CSV file: {csv_file}")
    print(f"Concurrent requests: {concurrent_requests}")
    print(f"Download delay: {delay} seconds")
    print(f"Output directory: {output_dir or 'current directory'}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        # Change to scraper directory and run
        original_dir = os.getcwd()
        os.chdir(scraper_dir)
        
        # Run the scraper
        result = subprocess.run(cmd, check=True, capture_output=False)
        
        print("-" * 50)
        print("Scraping completed successfully!")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error running scraper: {e}")
        return False
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        return False
    finally:
        os.chdir(original_dir)


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(description='Run Charter Schools Scraper')
    
    parser.add_argument(
        '--csv-file', 
        type=str, 
        help='Path to CSV file with school data (default: charter_schools_for_scraping.csv)'
    )
    
    parser.add_argument(
        '--concurrent-requests', 
        type=int, 
        default=8,
        help='Number of concurrent requests (default: 8 - ethical setting)'
    )
    
    parser.add_argument(
        '--delay', 
        type=float, 
        default=3.0,
        help='Delay between requests in seconds (default: 3.0 - ethical setting)'
    )
    
    parser.add_argument(
        '--output-dir', 
        type=str,
        help='Output directory for scraped data (default: current directory)'
    )
    
    parser.add_argument(
        '--test', 
        action='store_true',
        help='Run in test mode with reduced settings'
    )
    
    parser.add_argument(
        '--monitor', 
        action='store_true',
        help='Start monitoring in a separate terminal'
    )
    
    parser.add_argument(
        '--safe-mode', 
        action='store_true',
        help='Run in safe mode with very conservative settings'
    )
    
    args = parser.parse_args()
    
    # Test mode settings
    if args.test:
        args.concurrent_requests = 4
        args.delay = 2.0
        print("Running in TEST MODE with reduced settings")
    
    # Safe mode settings
    if args.safe_mode:
        args.concurrent_requests = 2
        args.delay = 5.0
        print("Running in SAFE MODE with very conservative ethical settings")
    
    # Start monitoring if requested
    if args.monitor:
        print("Starting monitoring in background...")
        try:
            subprocess.Popen([
                'python', 'monitor_scraping.py',
                '--refresh', '3'
            ])
            print("✅ Monitor started in background")
        except Exception as e:
            print(f"❌ Failed to start monitor: {e}")
    
    # Run the scraper
    success = run_scraper(
        csv_file=args.csv_file,
        concurrent_requests=args.concurrent_requests,
        delay=args.delay,
        output_dir=args.output_dir
    )
    
    if success:
        print("\n✅ Scraping completed successfully!")
        print("Check the output files for scraped data:")
        print("- scraped_schools_*.jsonl (full data)")
        print("- scraped_schools_*.csv (CSV format)")
        print("- school_texts_for_embeddings_*.jsonl (for vector embeddings)")
    else:
        print("\n❌ Scraping failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
