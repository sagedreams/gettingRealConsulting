#!/usr/bin/env python3
"""
Real-time Scraping Monitor

This script monitors the scraping progress in real-time by watching
the progress file and log files.
"""

import json
import time
import os
import sys
from datetime import datetime, timedelta
import subprocess


class ScrapingMonitor:
    """Monitor scraping progress in real-time."""
    
    def __init__(self, progress_file='scraping_progress.json', log_file='scraping.log'):
        self.progress_file = progress_file
        self.log_file = log_file
        self.last_size = 0
        self.start_time = None
        
    def load_progress(self):
        """Load progress data from file."""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        return {}
    
    def get_log_tail(self, lines=10):
        """Get the last N lines from the log file."""
        try:
            if os.path.exists(self.log_file):
                result = subprocess.run(
                    ['tail', '-n', str(lines), self.log_file],
                    capture_output=True, text=True
                )
                return result.stdout
        except:
            pass
        return ""
    
    def format_duration(self, seconds):
        """Format duration in human-readable format."""
        td = timedelta(seconds=int(seconds))
        hours, remainder = divmod(td.seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        
        if td.days > 0:
            return f"{td.days}d {hours:02d}h {minutes:02d}m {secs:02d}s"
        elif hours > 0:
            return f"{hours:02d}h {minutes:02d}m {secs:02d}s"
        else:
            return f"{minutes:02d}m {secs:02d}s"
    
    def display_progress(self, progress_data):
        """Display current progress."""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("🔍 CHARTER SCHOOLS SCRAPING MONITOR")
        print("=" * 60)
        
        if not progress_data:
            print("⏳ Waiting for scraping to start...")
            return
        
        # Basic stats
        start_time = progress_data.get('start_time', '')
        end_time = progress_data.get('end_time', '')
        total_items = progress_data.get('total_items', 0)
        completed_urls = len(progress_data.get('completed_urls', []))
        failed_urls = len(progress_data.get('failed_urls', []))
        
        print(f"📅 Started: {start_time}")
        if end_time:
            print(f"📅 Ended: {end_time}")
            print(f"📊 Status: COMPLETED")
        else:
            print(f"📊 Status: RUNNING")
        
        print(f"📄 Items scraped: {total_items}")
        print(f"✅ Successful: {completed_urls}")
        print(f"❌ Failed: {failed_urls}")
        
        # Calculate progress percentage (assuming 894 total schools)
        total_schools = 894
        if total_schools > 0:
            progress_percent = (completed_urls / total_schools) * 100
            print(f"📈 Progress: {completed_urls}/{total_schools} ({progress_percent:.1f}%)")
            
            # Progress bar
            bar_length = 40
            filled_length = int(bar_length * progress_percent / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            print(f"Progress: [{bar}] {progress_percent:.1f}%")
        
        # Time estimates
        if start_time and not end_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                elapsed = datetime.now() - start_dt.replace(tzinfo=None)
                
                print(f"⏱️  Elapsed time: {self.format_duration(elapsed.total_seconds())}")
                
                if completed_urls > 0:
                    rate = completed_urls / elapsed.total_seconds()
                    remaining = total_schools - completed_urls
                    if rate > 0:
                        eta_seconds = remaining / rate
                        eta = timedelta(seconds=int(eta_seconds))
                        print(f"⏰ ETA: {self.format_duration(eta_seconds)}")
                        print(f"⚡ Rate: {rate:.2f} schools/second")
            except:
                pass
        
        print("=" * 60)
        
        # Recent log entries
        print("📋 Recent Activity:")
        log_tail = self.get_log_tail(5)
        if log_tail:
            for line in log_tail.strip().split('\n')[-5:]:
                if line.strip():
                    print(f"   {line}")
        else:
            print("   No recent activity")
        
        print("=" * 60)
        print("Press Ctrl+C to stop monitoring")
    
    def monitor(self, refresh_interval=5):
        """Start monitoring the scraping progress."""
        print("🚀 Starting scraping monitor...")
        print(f"📁 Monitoring: {self.progress_file}")
        print(f"📋 Log file: {self.log_file}")
        print(f"🔄 Refresh interval: {refresh_interval} seconds")
        print()
        
        try:
            while True:
                progress_data = self.load_progress()
                self.display_progress(progress_data)
                
                # Check if scraping is complete
                if progress_data.get('end_time'):
                    print("\n🎉 Scraping completed!")
                    break
                
                time.sleep(refresh_interval)
                
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor Charter Schools Scraping Progress')
    parser.add_argument('--progress-file', default='scraping_progress.json',
                       help='Progress file to monitor (default: scraping_progress.json)')
    parser.add_argument('--log-file', default='scraping.log',
                       help='Log file to monitor (default: scraping.log)')
    parser.add_argument('--refresh', type=int, default=5,
                       help='Refresh interval in seconds (default: 5)')
    
    args = parser.parse_args()
    
    monitor = ScrapingMonitor(args.progress_file, args.log_file)
    monitor.monitor(args.refresh)


if __name__ == "__main__":
    main()
