#!/usr/bin/env python3
# @structurelint:no-test
"""Quick analysis of downloaded historical index data"""

import csv
from datetime import datetime
import os

def analyze_csv(filename, date_col='Date', value_col=None):
    """Analyze a CSV file and return basic stats"""
    if not os.path.exists(filename):
        return None

    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            return None

        # Detect date column
        if date_col not in rows[0]:
            date_col = list(rows[0].keys())[0]

        # Get first and last dates
        first_date = rows[0][date_col]
        last_date = rows[-1][date_col]

        # Try to parse dates
        try:
            first_dt = datetime.strptime(first_date, '%Y-%m-%d')
            last_dt = datetime.strptime(last_date, '%Y-%m-%d')
            years = (last_dt - first_dt).days / 365.25
        except Exception:
            years = None

        return {
            'filename': filename,
            'rows': len(rows),
            'first_date': first_date,
            'last_date': last_date,
            'years': round(years, 1) if years else 'N/A',
            'columns': list(rows[0].keys())
        }
    except Exception as e:
        print(f"Error analyzing {filename}: {e}")
        return None

# Analyze all CSV files
datasets = [
    ('S&P 500 (Stooq)', 'sp500_stooq_daily.csv', 'Date'),
    ('DJIA (Stooq)', 'djia_stooq_daily.csv', 'Date'),
    ('NASDAQ (FRED)', 'nasdaq_fred.csv', 'observation_date'),
    ('Nikkei 225 (FRED)', 'nikkei225_fred.csv', 'observation_date'),
    ('MSCI World ETF', 'msci_world_urth_stooq_daily.csv', 'Date'),
    ('MSCI ACWI ETF', 'msci_acwi_stooq_daily.csv', 'Date'),
    ('S&P 500 Monthly (GitHub)', 'sp500_github_monthly.csv', 'Date'),
    ('VIX Daily', 'vix_daily.csv', 'Date'),
]

print("=" * 100)
print("HISTORICAL INDEX DATA ANALYSIS")
print("=" * 100)
print()

results = []
for name, filename, date_col in datasets:
    stats = analyze_csv(filename, date_col)
    if stats:
        results.append((name, stats))

# Sort by years (descending)
results.sort(key=lambda x: x[1]['years'] if isinstance(x[1]['years'], (int, float)) else 0, reverse=True)

# Print results
print(f"{'Index':<30} {'From':<12} {'To':<12} {'Years':<8} {'Records':<10}")
print("-" * 100)

for name, stats in results:
    print(f"{name:<30} {stats['first_date']:<12} {stats['last_date']:<12} {str(stats['years']):<8} {stats['rows']:,}")

print()
print("=" * 100)
print("\nSUMMARY:")
print(f"  Total datasets: {len(results)}")
print(f"  Total records: {sum(s['rows'] for _, s in results):,}")
print(f"  Longest daily dataset: {results[0][0]} ({results[0][1]['years']} years)")
print(f"  Oldest start date: {min(s['first_date'] for _, s in results)}")
print()
print("All data files are ready for use in your StockSimulator project!")
print("See DATA_SUMMARY.md for detailed information about each dataset.")
print("=" * 100)
