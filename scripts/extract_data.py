#!/usr/bin/env python3
"""
Script to extract charter school data from JSONL files.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from utils.extract_charter_data import main

if __name__ == "__main__":
    main()
