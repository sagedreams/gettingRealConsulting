# Anti-Blocking & Progress Monitoring Features

## 🛡️ **Anti-Blocking Measures**

### **1. Advanced User Agent Rotation**
- **12 different user agents** from Chrome, Firefox, Safari, and Edge
- **Latest browser versions** (Chrome 120, Firefox 120, etc.)
- **Multiple operating systems** (Windows, macOS, Linux)
- **Random header rotation** (Accept, Accept-Language, etc.)
- **Browser-like headers** (DNT, Sec-Fetch-*, Cache-Control)

### **2. Rate Limiting & Delays**
- **2-second minimum delay** between requests to same domain
- **Random delays** (0.5 to 4 seconds) to avoid patterns
- **Domain-based rate limiting** (max 4 concurrent requests per domain)
- **Automatic backoff** when rate limits detected

### **3. Intelligent Blocking Detection**
- **HTTP status monitoring** (429, 403, 503, 5xx)
- **Response body analysis** (detects "blocked" messages)
- **Automatic backoff periods** (15-60 seconds based on error type)
- **Domain blacklisting** for problematic sites

### **4. Request Management**
- **Reduced concurrency** (16 total, 4 per domain)
- **Increased timeouts** (45 seconds)
- **Enhanced retry logic** (5 attempts with exponential backoff)
- **DNS caching** for better performance

## 📊 **Progress Monitoring**

### **1. Real-Time Statistics**
- **Live progress updates** every 30 seconds
- **Success/failure rates** with percentages
- **Scraping speed** (items per minute)
- **Time estimates** (elapsed time, ETA)
- **Domain-specific tracking**

### **2. Progress File Tracking**
- **JSON progress file** (`scraping_progress.json`)
- **Resume capability** for interrupted scraping
- **Completed/failed URL tracking**
- **Timestamp logging** for analysis

### **3. Visual Monitoring**
- **Progress bars** with percentage completion
- **Color-coded status** (✅ success, ❌ failure, ⚠️ warning)
- **Real-time log tail** (last 5 log entries)
- **Clean terminal interface** with emojis

### **4. Monitoring Script**
```bash
# Start monitoring in separate terminal
python monitor_scraping.py

# Custom refresh interval
python monitor_scraping.py --refresh 3

# Monitor specific files
python monitor_scraping.py --progress-file custom_progress.json
```

## 🚀 **Usage Examples**

### **Conservative Scraping (Recommended)**
```bash
# Safe mode with monitoring
python run_charter_scraper.py --safe-mode --monitor

# Manual conservative settings
python run_charter_scraper.py --concurrent-requests 4 --delay 5.0
```

### **Balanced Scraping**
```bash
# Default settings with monitoring
python run_charter_scraper.py --monitor

# Custom balanced settings
python run_charter_scraper.py --concurrent-requests 8 --delay 2.0
```

### **High-Performance Scraping**
```bash
# Faster settings (use with caution)
python run_charter_scraper.py --concurrent-requests 16 --delay 1.0
```

### **Test Mode**
```bash
# Test with 5 schools
python test_scraper.py

# Test with monitoring
python run_charter_scraper.py --test --monitor
```

## 📈 **Monitoring Output Example**

```
🔍 CHARTER SCHOOLS SCRAPING MONITOR
============================================================
📅 Started: 2025-01-19T10:30:00
📊 Status: RUNNING
📄 Items scraped: 156
✅ Successful: 142
❌ Failed: 14
📈 Progress: 142/894 (15.9%)
Progress: [████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 15.9%
⏱️  Elapsed time: 12m 34s
⏰ ETA: 1h 2m 15s
⚡ Rate: 0.19 schools/second
============================================================
📋 Recent Activity:
   INFO: Scraped school: https://www.example-school.org
   WARNING: Rate limited by www.slow-school.edu (429)
   INFO: Domain www.slow-school.edu will be retried after 30s
   INFO: Scraped school: https://www.another-school.org
   INFO: Progress update: 142/894 (15.9%)
============================================================
Press Ctrl+C to stop monitoring
```

## 🛠️ **Configuration Options**

### **Anti-Blocking Settings**
```python
# In settings.py
DOWNLOAD_DELAY = 2  # Base delay between requests
RANDOMIZE_DOWNLOAD_DELAY = True  # Randomize delays
CONCURRENT_REQUESTS_PER_DOMAIN = 4  # Max requests per domain
CONCURRENT_REQUESTS = 16  # Total concurrent requests
RETRY_TIMES = 5  # Retry attempts
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429, 403]
```

### **Monitoring Settings**
```python
# In settings.py
PROGRESS_STATS_INTERVAL = 30  # Stats update interval
PROGRESS_FILE = 'scraping_progress.json'  # Progress file
LOG_LEVEL = 'INFO'  # Logging level
LOG_FILE = 'scraping.log'  # Log file
```

## 🔧 **Troubleshooting**

### **If You Get Blocked**
1. **Increase delays**: `--delay 10.0`
2. **Reduce concurrency**: `--concurrent-requests 2`
3. **Use safe mode**: `--safe-mode`
4. **Check progress file** for blocked domains

### **If Scraping is Too Slow**
1. **Increase concurrency** (carefully): `--concurrent-requests 8`
2. **Reduce delays**: `--delay 1.0`
3. **Monitor for errors** in real-time

### **If You Need to Resume**
1. **Check progress file**: `cat scraping_progress.json`
2. **Remove completed URLs** from CSV
3. **Restart scraper** with remaining URLs

## 📊 **Performance Metrics**

### **Expected Performance**
- **Conservative mode**: ~2-3 schools/minute
- **Balanced mode**: ~5-8 schools/minute  
- **High-performance mode**: ~10-15 schools/minute

### **Total Time Estimates**
- **894 schools in conservative mode**: ~5-7 hours
- **894 schools in balanced mode**: ~2-3 hours
- **894 schools in high-performance mode**: ~1-2 hours

## 🎯 **Best Practices**

1. **Start with test mode** to verify everything works
2. **Use monitoring** to track progress and catch issues early
3. **Begin with conservative settings** and increase gradually
4. **Monitor logs** for blocking indicators
5. **Save progress regularly** for resumability
6. **Respect website resources** - don't overwhelm servers

## 🚨 **Warning Signs**

Watch for these indicators of potential blocking:
- **429 (Too Many Requests)** responses
- **403 (Forbidden)** responses  
- **503 (Service Unavailable)** responses
- **"blocked"** text in response bodies
- **Sudden increase in failures**
- **Very slow response times**

If you see these, immediately reduce concurrency and increase delays!
