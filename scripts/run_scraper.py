#!/usr/bin/env python3
"""
Main script to run the enhanced scraper with proper project structure.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from scrapers.enhanced_scraper import main

if __name__ == "__main__":
    main()
