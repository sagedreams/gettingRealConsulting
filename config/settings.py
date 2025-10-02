"""
Project configuration settings.
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SCRAPED_DATA_DIR = DATA_DIR / "scraped"
ANALYZED_DATA_DIR = DATA_DIR / "analyzed"

# Source directories
SRC_DIR = PROJECT_ROOT / "src"
SCRAPERS_DIR = SRC_DIR / "scrapers"
ANALYZERS_DIR = SRC_DIR / "analyzers"
UTILS_DIR = SRC_DIR / "utils"

# Output directories
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, SCRAPED_DATA_DIR, 
                 ANALYZED_DATA_DIR, OUTPUT_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Scraping settings
DEFAULT_DELAY = 1.0
DEFAULT_MAX_PAGES = 10
DEFAULT_CONCURRENT_REQUESTS = 2

# Ollama settings
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llama3.2:3b"

# File patterns
CSV_PATTERN = "*.csv"
JSON_PATTERN = "*.json"
JSONL_PATTERN = "*.jsonl"
