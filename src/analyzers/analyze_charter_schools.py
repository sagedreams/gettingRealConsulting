#!/usr/bin/env python3
"""
Charter Schools Website Analysis Script

This script analyzes the charter schools CSV data to extract and analyze
unique websites, providing statistics and insights about charter school
networks and website distribution.

Usage:
    python analyze_charter_schools.py

Requirements:
    - pandas
    - charter schools CSV file: schools_charter_20250919_002920.csv
"""

import pandas as pd
import re
from collections import Counter
import os

def load_and_clean_data(csv_file):
    """
    Load the charter schools CSV and clean the web address data.
    
    Args:
        csv_file (str): Path to the charter schools CSV file
        
    Returns:
        tuple: (full_dataframe, valid_websites_dataframe)
    """
    print(f"Loading charter schools data from {csv_file}...")
    
    # Load the CSV
    df = pd.read_csv(csv_file)
    
    # Clean up the web address column
    df['web_address_clean'] = df['web address'].str.replace(' Link opens new browser tab', '', regex=False)
    df['web_address_clean'] = df['web_address_clean'].str.strip()
    
    # Filter out invalid entries
    valid_websites = df[
        (df['web_address_clean'] != 'Information Not Available') & 
        (df['web_address_clean'].notna()) & 
        (df['web_address_clean'] != '') &
        (~df['web_address_clean'].str.startswith(' CA ')) &
        (~df['web_address_clean'].str.startswith('"'))
    ]
    
    return df, valid_websites

def analyze_website_distribution(valid_websites):
    """
    Analyze the distribution of websites across charter schools.
    
    Args:
        valid_websites (DataFrame): DataFrame with valid website data
        
    Returns:
        Series: Website frequency counts
    """
    website_counts = valid_websites['web_address_clean'].value_counts()
    
    print("=== WEBSITE DISTRIBUTION STATISTICS ===")
    print(f"Websites used by only 1 school: {(website_counts == 1).sum()}")
    print(f"Websites used by 2-5 schools: {((website_counts >= 2) & (website_counts <= 5)).sum()}")
    print(f"Websites used by 6+ schools: {(website_counts >= 6).sum()}")
    print()
    
    return website_counts

def analyze_top_websites(website_counts, valid_websites, top_n=20):
    """
    Display the top N most common websites.
    
    Args:
        website_counts (Series): Website frequency counts
        valid_websites (DataFrame): DataFrame with valid website data
        top_n (int): Number of top websites to display
    """
    print(f"=== TOP {top_n} MOST COMMON WEBSITES ===")
    top_websites = website_counts.head(top_n)
    
    for i, (website, count) in enumerate(top_websites.items(), 1):
        percentage = (count / len(valid_websites)) * 100
        print(f"{i:2d}. {website:<50} ({count:2d} schools, {percentage:.1f}%)")
    print()

def analyze_by_county(valid_websites, top_counties=10):
    """
    Analyze charter schools and websites by county.
    
    Args:
        valid_websites (DataFrame): DataFrame with valid website data
        top_counties (int): Number of top counties to analyze
    """
    print("=== TOP COUNTIES BY NUMBER OF CHARTER SCHOOLS ===")
    county_counts = valid_websites['county'].value_counts()
    print(county_counts.head(top_counties))
    print()
    
    print("=== WEBSITES BY TOP COUNTIES ===")
    top_counties_list = county_counts.head(5).index
    
    for county in top_counties_list:
        county_schools = valid_websites[valid_websites['county'] == county]
        county_websites = county_schools['web_address_clean'].value_counts()
        print(f"\n{county} County ({len(county_schools)} schools with websites):")
        print(county_websites.head(5))

def analyze_website_domains(website_counts):
    """
    Extract and analyze domain names from websites.
    
    Args:
        website_counts (Series): Website frequency counts
    """
    print("=== DOMAIN ANALYSIS ===")
    
    # Extract domains
    domains = []
    for website in website_counts.index:
        # Remove protocol if present
        domain = re.sub(r'^https?://', '', website)
        # Remove www. if present
        domain = re.sub(r'^www\.', '', domain)
        # Get just the domain part (before first slash)
        domain = domain.split('/')[0]
        domains.append(domain)
    
    domain_counts = Counter(domains)
    
    print("Top 15 unique domains:")
    for i, (domain, count) in enumerate(domain_counts.most_common(15), 1):
        print(f"{i:2d}. {domain:<40} ({count} schools)")
    print()

def save_analysis_results(df, valid_websites, website_counts, output_file="charter_analysis_results.txt"):
    """
    Save analysis results to a text file.
    
    Args:
        df (DataFrame): Full charter schools DataFrame
        valid_websites (DataFrame): Valid websites DataFrame
        website_counts (Series): Website frequency counts
        output_file (str): Output file name
    """
    with open(output_file, 'w') as f:
        f.write("CHARTER SCHOOLS WEBSITE ANALYSIS RESULTS\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Total charter schools: {len(df)}\n")
        f.write(f"Schools with valid websites: {len(valid_websites)}\n")
        f.write(f"Schools without websites: {len(df) - len(valid_websites)}\n")
        f.write(f"Unique websites: {valid_websites['web_address_clean'].nunique()}\n\n")
        
        f.write("TOP 30 WEBSITES:\n")
        f.write("-" * 30 + "\n")
        for i, (website, count) in enumerate(website_counts.head(30).items(), 1):
            percentage = (count / len(valid_websites)) * 100
            f.write(f"{i:2d}. {website:<50} ({count:2d} schools, {percentage:.1f}%)\n")
        
        f.write(f"\nAnalysis completed on: {pd.Timestamp.now()}\n")
    
    print(f"Analysis results saved to: {output_file}")

def main():
    """Main analysis function."""
    csv_file = "schools_charter_20250919_002920.csv"
    
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        print("Please ensure the charter schools CSV file is in the current directory.")
        return
    
    # Load and clean data
    df, valid_websites = load_and_clean_data(csv_file)
    
    # Basic statistics
    print("=== CHARTER SCHOOLS WEBSITE ANALYSIS ===")
    print(f"Total charter schools: {len(df)}")
    print(f"Schools with valid websites: {len(valid_websites)}")
    print(f"Schools without websites: {len(df) - len(valid_websites)}")
    print(f"Unique websites: {valid_websites['web_address_clean'].nunique()}")
    print()
    
    # Analyze website distribution
    website_counts = analyze_website_distribution(valid_websites)
    
    # Analyze top websites
    analyze_top_websites(website_counts, valid_websites, top_n=20)
    
    # Analyze by county
    analyze_by_county(valid_websites)
    
    # Analyze domains
    analyze_website_domains(website_counts)
    
    # Save results
    save_analysis_results(df, valid_websites, website_counts)
    
    print("Analysis complete!")

if __name__ == "__main__":
    main()
