# Charter Schools Data Pipeline

A comprehensive data pipeline for scraping, processing, and analyzing charter school information using web scraping and local LLM analysis.

## 🏗️ Project Structure

```
gettingRealConsulting/
├── src/                          # Source code
│   ├── scrapers/                 # Web scraping modules
│   │   ├── enhanced_scraper.py   # Multi-page scraper
│   │   └── simple_scraper.py     # Basic scraper
│   ├── analyzers/                # Data analysis modules
│   │   ├── school_analyzer.py    # Full-featured analyzer
│   │   ├── simple_school_analyzer.py  # Simplified analyzer
│   │   ├── analyze_charter_schools.py # Charter school analysis
│   │   └── analyze_charter_jsonl.py   # JSONL analysis
│   └── utils/                    # Utility modules
│       ├── extract_charter_data.py    # Data extraction
│       ├── check_robots_compliance.py # Robots.txt checker
│       ├── monitor_scraping.py        # Scraping monitor
│       └── simple_monitor.py          # Simple monitor
├── scripts/                      # Executable scripts
│   ├── run_scraper.py           # Main scraper runner
│   ├── run_analyzer.py          # Main analyzer runner
│   ├── extract_data.py          # Data extraction runner
│   ├── test_scraper.py          # Test scraper
│   └── run_charter_scraper.py   # Legacy scraper runner
├── data/                         # Data storage
│   ├── raw/                      # Original data files
│   │   ├── schools_*.csv         # Raw school data
│   │   ├── schools_*.jsonl       # Raw JSONL data
│   │   └── schools_*.json        # Raw JSON data
│   ├── processed/                # Processed data
│   │   ├── charter_schools_for_scraping.csv
│   │   └── test_schools.csv
│   ├── scraped/                  # Scraped data
│   │   ├── test_scraped_data/    # Test scraping results
│   │   ├── *scraped*.csv         # Scraping summaries
│   │   └── scraper_log_*.txt     # Scraping logs
│   └── analyzed/                 # Analysis results
│       ├── *analysis*.json       # LLM analysis results
│       └── *school_analysis*.json # School insights
├── config/                       # Configuration
│   ├── settings.py               # Project settings
│   └── requirements.txt          # Dependencies
├── docs/                         # Documentation
│   ├── README_SCRAPER.md         # Scraper documentation
│   ├── ETHICAL_SCRAPING_GUIDE.md # Ethical guidelines
│   ├── ANTI_BLOCKING_AND_MONITORING.md # Technical docs
│   └── readme.md                 # Original readme
├── tests/                        # Test files
├── venv/                         # Virtual environment
└── README.md                     # This file
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r config/requirements.txt
```

### 2. Extract School Data

```bash
# Extract charter school data from JSONL
python scripts/extract_data.py --input data/raw/schools_charter_20250919_002920.jsonl
```

### 3. Scrape School Websites

```bash
# Run enhanced scraper (multi-page)
python scripts/run_scraper.py --csv-file data/processed/charter_schools_for_scraping.csv --delay 2.0 --max-pages 10

# Test with small dataset
python scripts/run_scraper.py --csv-file data/processed/test_schools.csv --limit 5 --delay 1.0
```

### 4. Analyze Scraped Data

```bash
# Run simple analyzer (recommended)
python scripts/run_analyzer.py --data-dir data/scraped --model llama3.2:3b

# Run full analyzer
python scripts/run_analyzer.py --data-dir data/scraped --model llama3.2:3b --output analysis_results.json
```

## 📊 Data Flow

1. **Raw Data** → `data/raw/` (Original CSV/JSONL files)
2. **Processing** → `data/processed/` (Cleaned, deduplicated data)
3. **Scraping** → `data/scraped/` (Website content)
4. **Analysis** → `data/analyzed/` (LLM insights)

## 🛠️ Key Components

### Scrapers
- **Enhanced Scraper**: Multi-page scraping with domain crawling
- **Simple Scraper**: Basic single-page scraping
- **Anti-blocking**: Rate limiting, user agent rotation, delays
- **Monitoring**: Progress tracking and error handling

### Analyzers
- **School Analyzer**: Comprehensive LLM analysis with structured output
- **Simple Analyzer**: Streamlined analysis for reliable results
- **Ollama Integration**: Local LLM processing

### Utilities
- **Data Extraction**: Clean and deduplicate school data
- **Robots Compliance**: Check robots.txt compliance
- **Monitoring**: Real-time scraping progress

## ⚙️ Configuration

### Scraping Settings
- **Delay**: 1-5 seconds between requests
- **Max Pages**: 5-50 pages per school
- **Concurrent**: 1-8 concurrent requests
- **User Agents**: Rotating user agent strings

### Analysis Settings
- **Ollama URL**: `http://localhost:11434`
- **Model**: `llama3.2:3b` (or your preferred model)
- **Temperature**: 0.1 (for consistent results)

## 📈 Usage Examples

### Full Pipeline
```bash
# 1. Extract data
python scripts/extract_data.py

# 2. Scrape websites
python scripts/run_scraper.py --delay 2.0 --max-pages 15

# 3. Analyze results
python scripts/run_analyzer.py --model llama3.2:3b
```

### Testing
```bash
# Test with small dataset
python scripts/run_scraper.py --csv-file data/processed/test_schools.csv --limit 3
python scripts/run_analyzer.py --data-dir data/scraped/test_scraped_data
```

### Monitoring
```bash
# Check robots compliance
python src/utils/check_robots_compliance.py

# Monitor scraping progress
python src/utils/monitor_scraping.py
```

## 🔧 Dependencies

- **Web Scraping**: `requests`, `beautifulsoup4`, `lxml`
- **Data Processing**: `pandas`, `numpy`
- **LLM Integration**: `requests` (for Ollama API)
- **Utilities**: `urllib3`, `certifi`

## 📝 Output Formats

### Scraped Data
- **JSON Files**: One per school with structured page data
- **CSV Summary**: Flat summary of all scraped pages
- **Logs**: Detailed scraping logs with timestamps

### Analysis Results
- **JSON**: Structured analysis with school insights
- **Text**: Human-readable analysis summaries
- **Metadata**: Processing statistics and model info

## 🚨 Ethical Considerations

- **Robots.txt Compliance**: Always checked before scraping
- **Rate Limiting**: Conservative delays between requests
- **Respectful Scraping**: No aggressive crawling
- **Data Privacy**: Only public information collected

## 🐛 Troubleshooting

### Common Issues
1. **Ollama Connection**: Ensure Ollama is running on localhost:11434
2. **Model Not Found**: Check available models with `ollama list`
3. **Permission Errors**: Ensure proper file permissions
4. **Memory Issues**: Reduce concurrent requests or max pages

### Debug Mode
```bash
# Enable verbose logging
python scripts/run_scraper.py --delay 3.0 --limit 1
python scripts/run_analyzer.py --data-dir data/scraped --model llama3.2:3b
```

## 📚 Documentation

- **Scraper Guide**: `docs/README_SCRAPER.md`
- **Ethical Guidelines**: `docs/ETHICAL_SCRAPING_GUIDE.md`
- **Technical Details**: `docs/ANTI_BLOCKING_AND_MONITORING.md`

## 🤝 Contributing

1. Follow the project structure
2. Add tests for new features
3. Update documentation
4. Ensure ethical scraping practices

## 📄 License

This project is for educational and research purposes. Please respect website terms of service and robots.txt files.
