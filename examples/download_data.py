"""
Example: Download Historical Data

Demonstrates how to download historical market data from various sources.
"""

import sys
import os
from datetime import date, timedelta

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from stocksimulator.downloaders import YahooFinanceDownloader, AlphaVantageDownloader


def example_yahoo_finance():
    """Example: Download data from Yahoo Finance."""
    print("=" * 80)
    print("YAHOO FINANCE DOWNLOADER")
    print("=" * 80)
    print()

    downloader = YahooFinanceDownloader()

    # Download single symbol
    print("Downloading SPY data...")
    spy_data = downloader.download(
        symbol='SPY',
        start_date=date(2020, 1, 1),
        end_date=date(2023, 12, 31)
    )

    print(f"✓ Downloaded {len(spy_data.data)} data points for {spy_data.symbol}")
    print(f"  Date range: {spy_data.data[0].date} to {spy_data.data[-1].date}")
    print(f"  First close: ${spy_data.data[0].close:.2f}")
    print(f"  Last close: ${spy_data.data[-1].close:.2f}")
    print()

    # Download multiple symbols
    print("Downloading multiple symbols...")
    symbols = ['SPY', 'TLT', 'GLD']
    all_data = downloader.download_multiple(
        symbols=symbols,
        start_date=date(2020, 1, 1),
        end_date=date(2023, 12, 31)
    )

    print()
    print(f"Successfully downloaded {len(all_data)} symbols")
    print()


def example_alpha_vantage():
    """Example: Download data from Alpha Vantage."""
    print("=" * 80)
    print("ALPHA VANTAGE DOWNLOADER")
    print("=" * 80)
    print()

    # Check if API key is set
    api_key = os.environ.get('ALPHAVANTAGE_API_KEY')
    if not api_key:
        print("⚠ ALPHAVANTAGE_API_KEY environment variable not set")
        print("  Get free API key at: https://www.alphavantage.co/support/#api-key")
        print("  Then set it: export ALPHAVANTAGE_API_KEY='your_key_here'")
        print()
        return

    downloader = AlphaVantageDownloader(api_key=api_key)

    # Download data
    print("Downloading SPY data from Alpha Vantage...")
    print("(This may take ~12 seconds due to rate limiting)")
    print()

    spy_data = downloader.download(
        symbol='SPY',
        output_size='compact'  # Last 100 data points
    )

    print(f"✓ Downloaded {len(spy_data.data)} data points for {spy_data.symbol}")
    print(f"  Date range: {spy_data.data[0].date} to {spy_data.data[-1].date}")
    print()


def example_save_to_csv():
    """Example: Download data and save to CSV."""
    print("=" * 80)
    print("DOWNLOAD AND SAVE TO CSV")
    print("=" * 80)
    print()

    downloader = YahooFinanceDownloader()

    # Download data
    print("Downloading QQQ data...")
    qqq_data = downloader.download(
        symbol='QQQ',
        start_date=date(2020, 1, 1),
        end_date=date.today()
    )

    # Save to CSV
    output_dir = 'historical_data'
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, 'qqq_downloaded.csv')

    import csv
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])

        for point in qqq_data.data:
            writer.writerow([
                point.date.isoformat(),
                point.open,
                point.high,
                point.low,
                point.close,
                point.volume
            ])

    print(f"✓ Saved {len(qqq_data.data)} data points to {output_file}")
    print()

    # Now you can load it back using CSVLoader
    from stocksimulator.data import load_from_csv

    loaded_data = load_from_csv('qqq_downloaded.csv', 'QQQ')
    print(f"✓ Loaded {len(loaded_data.data)} data points from CSV")
    print()


def main():
    """Run all examples."""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "DATA DOWNLOADER EXAMPLES" + " " * 34 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # Yahoo Finance (always available)
    example_yahoo_finance()

    # Alpha Vantage (requires API key)
    example_alpha_vantage()

    # Save to CSV
    example_save_to_csv()

    print("=" * 80)
    print("COMPLETE!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Use downloaded data with backtester")
    print("  2. Run strategy optimization")
    print("  3. Generate performance reports")
    print()


if __name__ == '__main__':
    main()
