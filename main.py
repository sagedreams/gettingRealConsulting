#!/usr/bin/env python3
"""
CDE School Directory (Private, Active/Pending) scraper
- List pages (500 at a time): https://www.cde.ca.gov/SchoolDirectory/active-or-pending-schools/2/{page}/-11/500
- School details pages are linked from the "School" column (e.g. /SchoolDirectory/details?cdscode=30736506143259)

Outputs:
  - schools_full.csv   (wide table, one row per school)
  - schools_full.jsonl (newline-delimited JSON, one object per school)

Usage:
  python cde_private_schools_scraper.py
"""

import time
import json
import csv
import math
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE = "https://www.cde.ca.gov"

# URL patterns for different school types:
# 1. PRIVATE SCHOOLS (3,056 schools across 7 pages)
# LIST_URL = BASE + "/SchoolDirectory/active-or-pending-schools/2/{page}/-11/500"

# 2. PUBLIC CHARTER SCHOOLS (1,262 schools across 3 pages) - CURRENTLY ACTIVE
LIST_URL = BASE + "/SchoolDirectory/Results?title=California%20School%20Directory&search=1&status=1%2C2&types=0&nps=0&multilingual=0&charter=1&magnet=0&yearround=0&qdc=0&qsc=0&sax=True&tab=1&order=0&page={page}&items=500&hidecriteria=False&isstaticreport=False"

DETAILS_URL = BASE + "/SchoolDirectory/details?cdscode={cds}"

# Generate unique filenames with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# File naming patterns:
# PRIVATE SCHOOLS: schools_full_{timestamp}.csv, schools_checkpoint_{timestamp}.json
# PUBLIC CHARTER SCHOOLS: schools_charter_{timestamp}.csv, schools_charter_checkpoint_{timestamp}.json
OUT_CSV = Path(f"schools_charter_{timestamp}.csv")
OUT_JSONL = Path(f"schools_charter_{timestamp}.jsonl")
CHECKPOINT = Path(f"schools_charter_checkpoint_{timestamp}.json")

# ---- Settings you can tweak ----
# Page ranges for different school types:
# PRIVATE SCHOOLS: list(range(0, 7))  # 0..6 -> 7 pages, ~3,056 schools
# PUBLIC CHARTER SCHOOLS: list(range(0, 3))  # 0..2 -> 3 pages, ~1,262 schools
PAGES = list(range(0, 3))  # Currently set for charter schools
REQUESTS_TIMEOUT = 30
RETRY_TIMES = 4
SLEEP_BETWEEN = 2.0      # polite delay between requests (seconds)
SLEEP_BETWEEN_PAGES = 5  # extra pause per list page
MAX_WORKERS = 6          # used only if you enable parallel detail fetch (see comment below)
# --------------------------------

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Cache-Control": "max-age=0"
})

def fetch(url: str, allow_redirects=True) -> Optional[requests.Response]:
    """GET with basic retries and polite delay."""
    for i in range(RETRY_TIMES):
        try:
            resp = session.get(url, timeout=REQUESTS_TIMEOUT, allow_redirects=allow_redirects)
            # Treat 200 only as success
            if resp.status_code == 200:
                # Check for captcha page
                if "Radware Captcha Page" in resp.text or "We apologize for the inconvenience" in resp.text:
                    print(f"⚠️  CAPTCHA detected on {url}")
                    print("   Bot protection is active. Consider:")
                    print("   - Increasing delays between requests")
                    print("   - Using a different IP/VPN")
                    print("   - Running the script in smaller batches")
                    return None
                return resp
            # Some servers rate-limit with 429 or 503; short backoff helps
            backoff = 1.5 * (i + 1)
            print(f"   Retry {i+1}/{RETRY_TIMES} after {backoff}s (status: {resp.status_code})")
            time.sleep(backoff)
        except requests.RequestException as e:
            backoff = 1.5 * (i + 1)
            print(f"   Retry {i+1}/{RETRY_TIMES} after {backoff}s (error: {e})")
            time.sleep(backoff)
    return None

def normalize_key(txt: str) -> str:
    return (
        txt.strip()
           .replace(" ", " ")   # non-breaking space
           .replace("\xa0", " ")
           .replace("\n", " ")
           .replace("\r", " ")
           .replace("\t", " ")
           .strip(" :")
           .lower()
           .replace("/", "_")
           .replace("&", "and")
           .replace("(", "")
           .replace(")", "")
           .replace(".", "")
           .replace(",", "")
           .replace("-", "_")
           .replace("__", "_")
    )

def text_of(el) -> str:
    if not el:
        return ""
    return " ".join(el.get_text(" ", strip=True).split())

def parse_list_page(html: str) -> List[Dict]:
    """
    Returns a list of dicts with columns shown on the results table + the details URL.
    We rely on the header text to map columns robustly.
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        return []

    # Map headers -> index
    headers = [text_of(th) for th in table.select("thead th")]
    # Clean up headers (remove "Sort results by this header" text)
    clean_headers = []
    for h in headers:
        clean_h = h.replace("Sort results by this header", "").strip()
        clean_headers.append(clean_h)
    idx = {h: i for i, h in enumerate(clean_headers)}

    rows = []
    # Get all tr elements, but skip the header row (first one)
    all_trs = table.find_all("tr")
    for tr in all_trs[1:]:  # Skip header row
        tds = tr.find_all("td")
        if not tds or len(tds) < 5:
            continue

        # pull by names if present; fall back to positions
        def cell(name: str, pos_fallback: int) -> str:
            if name in idx and idx[name] < len(tds):
                return text_of(tds[idx[name]])
            return text_of(tds[pos_fallback]) if pos_fallback < len(tds) else ""

        cds_code = cell("CDS Code", 0)
        county = cell("County", 1)
        district = cell("District", 2)
        school_cell = tds[idx.get("School", 3)] if "School" in idx else (tds[3] if len(tds) > 3 else None)
        school_name = text_of(school_cell)
        details_href = None
        if school_cell:
            a = school_cell.find("a", href=True)
            if a and "SchoolDirectory/details" in a["href"]:
                details_href = a["href"]
        # Normalize details URL
        if details_href and not details_href.startswith("http"):
            details_url = BASE + details_href
        elif details_href:
            details_url = details_href
        else:
            # fallback: construct from CDS code if link not present (rare)
            details_url = DETAILS_URL.format(cds=cds_code)

        school_type = cell("School Type", 4)
        sector_type = cell("Sector Type", 5) if len(tds) > 5 else ""
        charter = cell("Charter", 6) if len(tds) > 6 else ""
        status = cell("Status", 7) if len(tds) > 7 else ""

        rows.append({
            "cds_code": cds_code,
            "county": county,
            "district": district,
            "school": school_name,
            "school_type": school_type,
            "sector_type": sector_type,
            "charter": charter,
            "status": status,
            "details_url": details_url
        })
    return rows

def parse_details_page(html: str) -> Dict[str, str]:
    """
    The details page tends to show several tables of label/value rows.
    We greedily collect any TH/TD or first/second TD pairs, plus DL/DT/DD pairs,
    and return a flat dict of normalized keys -> text values.
    """
    soup = BeautifulSoup(html, "html.parser")
    info: Dict[str, str] = {}

    # Grab mailto if present anywhere
    email_link = soup.select_one('a[href^="mailto:"]')
    if email_link:
        info["email"] = email_link.get("href", "").replace("mailto:", "").strip()

    # Tables with two-column label/value
    for tbl in soup.find_all("table"):
        # Prefer rows with th/td
        for tr in tbl.find_all("tr"):
            th = tr.find("th")
            tds = tr.find_all("td")
            if th and tds:
                key = normalize_key(text_of(th))
                val = text_of(tds[0]) if tds else ""
                if key and val and key not in info:
                    info[key] = val
            elif len(tds) >= 2:
                key = normalize_key(text_of(tds[0]))
                val = text_of(tds[1])
                # avoid swallowing the whole table header row
                if key and val and len(key) <= 80:
                    info.setdefault(key, val)

    # Definition lists, if present
    for dl in soup.find_all("dl"):
        dts = dl.find_all("dt")
        dds = dl.find_all("dd")
        for dt, dd in zip(dts, dds):
            key = normalize_key(text_of(dt))
            val = text_of(dd)
            if key and val:
                info.setdefault(key, val)

    # Some friendly aliases
    # If an "administrator" field appears, preserve it; also try to break out name/phone if shown
    for k in list(info.keys()):
        if "administrator" in k and "name" not in k and "phone" not in k:
            # If value looks like "Jane Doe (510) 555-1234", keep as-is
            pass

    return info

def load_checkpoint() -> Dict[str, Dict]:
    if CHECKPOINT.exists():
        try:
            return json.loads(CHECKPOINT.read_text())
        except Exception:
            return {}
    return {}

def save_checkpoint(done_map: Dict[str, Dict]):
    CHECKPOINT.write_text(json.dumps(done_map, indent=2))

def merge_dicts(base: Dict, extra: Dict) -> Dict:
    out = dict(base)
    for k, v in extra.items():
        # avoid collisions with list columns
        if k in out and out[k] != v:
            out[f"details_{k}"] = v
        else:
            out[k] = v
    return out

def main():
    print(f"🚀 Starting CDE Public Charter Schools Scraper")
    print(f"📁 Output files: {OUT_CSV.name}, {OUT_JSONL.name}")
    print(f"💾 Checkpoint file: {CHECKPOINT.name}")
    print(f"📊 Processing {len(PAGES)} pages (pages {PAGES[0]}-{PAGES[-1]})")
    print("=" * 60)
    
    print("📋 Fetching list pages…")
    all_rows: List[Dict] = []
    for i, p in enumerate(PAGES, 1):
        url = LIST_URL.format(page=p)
        print(f"   [{i}/{len(PAGES)}] Fetching page {p}...")
        resp = fetch(url)
        if not resp:
            print(f"   ❌ Failed list page {p}: {url}")
            continue
        rows = parse_list_page(resp.text)
        print(f"   ✅ Page {p}: found {len(rows)} schools")
        all_rows.extend(rows)
        time.sleep(SLEEP_BETWEEN_PAGES)

    if not all_rows:
        print("❌ No rows found. Exiting.")
        return

    # Deduplicate by CDS code (some rows could repeat across pages if filters change)
    dedup = {}
    for r in all_rows:
        key = r.get("cds_code") or r.get("details_url")
        dedup[key] = r
    rows = list(dedup.values())
    print(f"📊 Total unique schools: {len(rows)}")
    print("=" * 60)

    # Resume from checkpoint if present
    done_map = load_checkpoint()
    out_records: List[Dict] = []
    
    print("🔍 Fetching school details...")
    start_time = time.time()
    
    # Create a log file to track URLs being processed
    log_file = Path(f"scraper_log_charter_{timestamp}.txt")
    with log_file.open("w", encoding="utf-8") as log:
        log.write(f"CDE School Scraper Log - {datetime.now()}\n")
        log.write("=" * 60 + "\n\n")

    for i, row in enumerate(rows, 1):
        cds = row.get("cds_code", f"row_{i}")
        school_name = row.get("school", "Unknown")[:50]  # Truncate long names
        details_url = row["details_url"]
        
        # Log the URL being processed
        with log_file.open("a", encoding="utf-8") as log:
            log.write(f"[{i:4d}/{len(rows)}] Processing: {school_name}\n")
            log.write(f"  CDS Code: {cds}\n")
            log.write(f"  URL: {details_url}\n")
        
        if cds in done_map:
            merged = merge_dicts(row, done_map[cds])
            out_records.append(merged)
            print(f"   [{i:4d}/{len(rows)}] ⏭️  Skipped (cached): {school_name}")
            with log_file.open("a", encoding="utf-8") as log:
                log.write(f"  Status: SKIPPED (cached)\n\n")
            continue

        time.sleep(SLEEP_BETWEEN)
        resp = fetch(details_url)
        if not resp:
            print(f"   [{i:4d}/{len(rows)}] ❌ Failed: {school_name}")
            details = {}
            with log_file.open("a", encoding="utf-8") as log:
                log.write(f"  Status: FAILED\n\n")
            # If we hit captcha, save what we have and suggest stopping
            if i > 1 and i % 10 == 0:  # Check every 10 failures
                print(f"   ⚠️  Multiple failures detected. Consider stopping and resuming later.")
        else:
            details = parse_details_page(resp.text)
            print(f"   [{i:4d}/{len(rows)}] ✅ Fetched: {school_name}")
            with log_file.open("a", encoding="utf-8") as log:
                log.write(f"  Status: SUCCESS\n")
                log.write(f"  Details found: {len(details)} fields\n\n")

        done_map[cds] = details
        merged = merge_dicts(row, details)
        out_records.append(merged)

        # Save checkpoint every 25 (more frequent)
        if i % 25 == 0:
            save_checkpoint(done_map)
            elapsed = time.time() - start_time
            rate = i / elapsed if elapsed > 0 else 0
            eta = (len(rows) - i) / rate if rate > 0 else 0
            print(f"   💾 Checkpoint saved: {i}/{len(rows)} ({rate:.1f} schools/sec, ETA: {eta/60:.1f}min)")

    # Final checkpoint
    save_checkpoint(done_map)
    
    print("=" * 60)
    print("💾 Saving results...")

    # Normalize columns: put a few common details up front if present
    common_cols = [
        "cds_code","county","district","school","school_type","sector_type","charter","status","details_url",
        "website","email","administrator_name","administrator","administrator_phone","administrator_phone_ext",
        "phone","phone_number","fax_number","street_address","street_city","street_state","street_zip",
        "mailing_address","mailing_city","mailing_state","mailing_zip","low_grade","high_grade"
    ]
    # Build a full column set
    all_keys = set()
    for rec in out_records:
        all_keys.update(rec.keys())
    # preserve order: common first, then the rest sorted
    rest = [k for k in sorted(all_keys) if k not in common_cols]
    cols = [c for c in common_cols if c in all_keys] + rest

    # Write JSONL
    print(f"   📄 Writing JSONL: {OUT_JSONL.name}")
    with OUT_JSONL.open("w", encoding="utf-8") as f:
        for rec in out_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # Write CSV
    print(f"   📊 Writing CSV: {OUT_CSV.name}")
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        for rec in out_records:
            writer.writerow({k: rec.get(k, "") for k in cols})

    print("=" * 60)
    print(f"🎉 SUCCESS! Scraped {len(out_records)} schools")
    print(f"📁 Files saved:")
    print(f"   - {OUT_CSV.resolve()}")
    print(f"   - {OUT_JSONL.resolve()}")
    print(f"   - {CHECKPOINT.resolve()}")
    print(f"   - {log_file.resolve()}")
    
    # Show some stats
    total_time = time.time() - start_time
    print(f"⏱️  Total time: {total_time/60:.1f} minutes")
    print(f"📈 Average rate: {len(out_records)/total_time:.1f} schools/second")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
