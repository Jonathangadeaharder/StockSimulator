"""
Alpha Vantage Downloader

Download historical data from Alpha Vantage API.
"""

from datetime import date, datetime
from typing import Optional
import os
import time

from stocksimulator.models.market_data import MarketData, OHLCV
from stocksimulator.downloaders.base import DataDownloader


class AlphaVantageDownloader(DataDownloader):
    """
    Download historical data from Alpha Vantage.

    Requires API key (free tier: 5 requests/minute, 500/day).
    Get key at: https://www.alphavantage.co/support/#api-key
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Alpha Vantage downloader.

        Args:
            api_key: Alpha Vantage API key (or set ALPHAVANTAGE_API_KEY env var)
        """
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.environ.get('ALPHAVANTAGE_API_KEY')

        self._last_request_time = 0
        self._min_request_interval = 12  # 5 requests/minute = 12 sec/request

    def is_available(self) -> bool:
        """Check if Alpha Vantage is accessible."""
        return self.api_key is not None

    def download(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        output_size: str = 'full'
    ) -> MarketData:
        """
        Download historical data from Alpha Vantage.

        Args:
            symbol: Stock/ETF symbol
            start_date: Start date (for filtering)
            end_date: End date (for filtering)
            output_size: 'compact' (last 100 points) or 'full' (20+ years)

        Returns:
            MarketData object

        Example:
            >>> downloader = AlphaVantageDownloader(api_key='YOUR_KEY')
            >>> spy_data = downloader.download('SPY', output_size='full')
        """
        if not self.api_key:
            raise ValueError(
                "Alpha Vantage API key required. "
                "Set ALPHAVANTAGE_API_KEY environment variable or pass to constructor."
            )

        # Rate limiting
        self._rate_limit()

        # Build URL
        import urllib.request
        import json

        url = (
            f"https://www.alphavantage.co/query?"
            f"function=TIME_SERIES_DAILY&symbol={symbol}"
            f"&outputsize={output_size}&apikey={self.api_key}"
        )

        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read())

            # Check for errors
            if 'Error Message' in data:
                raise ValueError(f"Alpha Vantage error: {data['Error Message']}")
            if 'Note' in data:
                raise ValueError(f"API rate limit exceeded: {data['Note']}")
            if 'Time Series (Daily)' not in data:
                raise ValueError(f"Unexpected response format for {symbol}")

            # Parse time series
            time_series = data['Time Series (Daily)']
            data_points = []

            for date_str, values in time_series.items():
                dt = datetime.strptime(date_str, '%Y-%m-%d').date()

                # Filter by date range if provided
                if start_date and dt < start_date:
                    continue
                if end_date and dt > end_date:
                    continue

                ohlcv = OHLCV(
                    date=dt,
                    open=float(values['1. open']),
                    high=float(values['2. high']),
                    low=float(values['3. low']),
                    close=float(values['4. close']),
                    volume=int(values['5. volume']),
                    adjusted_close=float(values['4. close'])
                )
                data_points.append(ohlcv)

            # Sort by date
            data_points.sort(key=lambda x: x.date)

            if not data_points:
                raise ValueError(f"No data points for {symbol} in date range")

            return MarketData(
                symbol=symbol,
                data=data_points,
                metadata={
                    'source': 'alpha_vantage',
                    'output_size': output_size,
                    'start_date': data_points[0].date.isoformat(),
                    'end_date': data_points[-1].date.isoformat(),
                    'num_points': len(data_points)
                }
            )

        except urllib.error.HTTPError as e:
            raise ValueError(f"HTTP error downloading {symbol}: {e}")
        except Exception as e:
            raise ValueError(f"Failed to download {symbol} from Alpha Vantage: {e}")

    def _rate_limit(self):
        """Enforce rate limiting (5 requests/minute)."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time

        if time_since_last < self._min_request_interval:
            sleep_time = self._min_request_interval - time_since_last
            time.sleep(sleep_time)

        self._last_request_time = time.time()

    def download_multiple(
        self,
        symbols: list,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        output_size: str = 'full'
    ) -> dict:
        """
        Download data for multiple symbols.

        Args:
            symbols: List of symbols
            start_date: Start date
            end_date: End date
            output_size: 'compact' or 'full'

        Returns:
            Dictionary of symbol -> MarketData

        Example:
            >>> downloader = AlphaVantageDownloader(api_key='YOUR_KEY')
            >>> data = downloader.download_multiple(['SPY', 'TLT'])
        """
        result = {}
        total = len(symbols)

        for i, symbol in enumerate(symbols, 1):
            try:
                print(f"[{i}/{total}] Downloading {symbol}...")
                result[symbol] = self.download(symbol, start_date, end_date, output_size)
                print(f"  ✓ Downloaded {len(result[symbol].data)} points")
            except Exception as e:
                print(f"  ✗ Failed: {e}")

        return result
