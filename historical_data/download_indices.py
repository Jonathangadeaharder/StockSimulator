#!/usr/bin/env python3
"""Download historical index data from various sources"""

import urllib.request
import time
import sys

def download_file(url, filename, delay=2):
    """Download a file with retry logic"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        time.sleep(delay)  # Rate limiting
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
            with open(filename, 'wb') as f:
                f.write(data)
        print(f"✓ Downloaded {filename} ({len(data)} bytes)")
        return True
    except Exception as e:
        print(f"✗ Failed to download {filename}: {e}")
        return False

# FRED API downloads (CSV format)
downloads = [
    # NASDAQ Composite from FRED
    ('https://fred.stlouisfed.org/graph/fredgraph.csv?id=NASDAQCOM', 'nasdaq_fred.csv'),
    # Nikkei 225 from FRED
    ('https://fred.stlouisfed.org/graph/fredgraph.csv?id=NIKKEI225', 'nikkei225_fred.csv'),
    # FTSE 100 from FRED
    ('https://fred.stlouisfed.org/graph/fredgraph.csv?id=FTSE100', 'ftse100_fred.csv'),
]

print("Downloading index data from FRED...\n")
for url, filename in downloads:
    download_file(url, filename, delay=3)

print("\nDownload complete!")
