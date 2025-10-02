# Charter Schools Website Scraper

This project provides a comprehensive solution for scraping charter school websites and preparing the data for vector embeddings.

## Overview

The scraper extracts data from charter school websites and saves it in multiple formats:
- **JSONL format**: Complete scraped data with metadata
- **CSV format**: Structured data for analysis
- **Embeddings format**: Clean text ready for vector embeddings

## Files Created

### Data Extraction
- `extract_charter_data.py` - Extracts school data from JSONL to CSV
- `charter_schools_for_scraping.csv` - CSV with unique school websites (894 schools)

### Scraper Components
- `charter_scraper/` - Scrapy project directory
  - `spiders/school_spider.py` - Main spider for scraping websites
  - `items.py` - Data structure definitions
  - `pipelines.py` - Data processing pipelines
  - `settings.py` - Scrapy configuration
  - `middlewares.py` - Custom middleware for user agents, delays, etc.

### Runner Scripts
- `run_charter_scraper.py` - Main script to run the scraper
- `test_scraper.py` - Test script with small dataset

## Quick Start

### 1. Setup Environment
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (already done)
pip install scrapy pandas
```

### 2. Extract School Data
```bash
# Extract unique schools from JSONL to CSV
python extract_charter_data.py
```

### 3. Run the Scraper

#### Test Mode (5 schools)
```bash
python test_scraper.py
```

#### Full Scraping
```bash
# Basic run
python run_charter_scraper.py

# With custom settings
python run_charter_scraper.py --concurrent-requests 16 --delay 2.0

# Help
python run_charter_scraper.py --help
```

## Configuration

### Parallel Processing
- **CONCURRENT_REQUESTS**: 32 (default) - Number of simultaneous requests
- **DOWNLOAD_DELAY**: 1 second - Delay between requests
- **RANDOMIZE_DOWNLOAD_DELAY**: True - Randomize delays to avoid detection

### Output Files
The scraper creates timestamped files:
- `scraped_schools_YYYYMMDD_HHMMSS.jsonl` - Complete data
- `scraped_schools_YYYYMMDD_HHMMSS.csv` - CSV format
- `school_texts_for_embeddings_YYYYMMDD_HHMMSS.jsonl` - For embeddings

## Data Structure

### School Item
```python
{
    'cds_code': '01100170130625',
    'school_name': 'Alternatives in Action',
    'county': 'Alameda',
    'district': 'Alameda County Office of Education',
    'email': 'dzarazua@alternativesinaction.org',
    'url': 'https://www.alternativesinaction.org',
    'domain': 'www.alternativesinaction.org',
    'status_code': 200,
    'title': 'Page Title',
    'description': 'Meta description',
    'text_content': 'Main page content',
    'clean_text': 'Processed text for embeddings',
    'scraped_at': '2025-01-19T10:30:00'
}
```

### Embeddings Format
```python
{
    'id': '01100170130625',
    'school_name': 'Alternatives in Action',
    'url': 'https://www.alternativesinaction.org',
    'text': 'Clean text content for vector embeddings',
    'metadata': {
        'county': 'Alameda',
        'district': 'Alameda County Office of Education',
        'email': 'dzarazua@alternativesinaction.org',
        'domain': 'www.alternativesinaction.org',
        'scraped_at': '2025-01-19T10:30:00',
        'status_code': 200,
        'title': 'Page Title',
        'description': 'Meta description'
    }
}
```

## Features

### Deduplication
- Automatically removes duplicate websites based on domain
- Reduced from 1,213 schools to 894 unique websites

### Error Handling
- Graceful handling of failed requests
- Retry mechanism for temporary failures
- Comprehensive logging

### Data Processing
- HTML cleaning and text extraction
- User agent rotation
- Rate limiting and delays
- Multiple output formats

### Parallel Processing
- Configurable concurrent requests
- Domain-based rate limiting
- Memory-efficient processing

## Usage Examples

### Basic Scraping
```bash
python run_charter_scraper.py
```

### High-Performance Scraping
```bash
python run_charter_scraper.py --concurrent-requests 64 --delay 0.5
```

### Conservative Scraping
```bash
python run_charter_scraper.py --concurrent-requests 8 --delay 3.0
```

### Custom Output Directory
```bash
python run_charter_scraper.py --output-dir ./scraped_data
```

## Monitoring

The scraper provides detailed logging:
- Request/response status
- Error handling
- Progress tracking
- Performance metrics

Check `scraping.log` for detailed logs.

## Next Steps

After scraping, you can:
1. **Create Vector Embeddings**: Use the `school_texts_for_embeddings_*.jsonl` file
2. **Analyze Data**: Use the CSV file for statistical analysis
3. **Search & Retrieval**: Build a search system using the embeddings
4. **School Comparison**: Compare schools based on scraped content

## Troubleshooting

### Common Issues
1. **CSV file not found**: Run `python extract_charter_data.py` first
2. **Permission errors**: Check file permissions and directory access
3. **Memory issues**: Reduce `CONCURRENT_REQUESTS` in settings
4. **Rate limiting**: Increase `DOWNLOAD_DELAY`

### Performance Tuning
- Adjust `CONCURRENT_REQUESTS` based on your system
- Modify `DOWNLOAD_DELAY` based on target server capacity
- Use `--test` mode for initial testing

## Data Quality

The scraper includes validation:
- Required field checking
- Text content length validation
- URL accessibility verification
- Duplicate detection

## Legal Considerations

- Respects robots.txt (can be disabled in settings)
- Implements rate limiting
- Uses appropriate delays
- Rotates user agents
- Handles errors gracefully

Always ensure compliance with website terms of service and applicable laws.
