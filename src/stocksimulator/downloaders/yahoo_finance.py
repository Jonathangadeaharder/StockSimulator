"""
Yahoo Finance Downloader

Download historical data from Yahoo Finance.
"""

from datetime import date, datetime, timedelta
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from stocksimulator.models.market_data import MarketData, OHLCV
from stocksimulator.downloaders.base import DataDownloader


class YahooFinanceDownloader(DataDownloader):
    """
    Download historical data from Yahoo Finance.

    Can use yfinance library if available, or direct HTTP requests as fallback.
    """

    def __init__(self):
        """Initialize Yahoo Finance downloader."""
        self._yfinance_available = self._check_yfinance()

    def _check_yfinance(self) -> bool:
        """Check if yfinance library is available."""
        try:
            import yfinance
            return True
        except ImportError:
            return False

    def is_available(self) -> bool:
        """Check if Yahoo Finance is accessible."""
        return True  # Yahoo Finance is generally available

    def download(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> MarketData:
        """
        Download historical data from Yahoo Finance.

        Args:
            symbol: Stock/ETF symbol (e.g., 'SPY', 'AAPL')
            start_date: Start date (default: 10 years ago)
            end_date: End date (default: today)

        Returns:
            MarketData object

        Example:
            >>> downloader = YahooFinanceDownloader()
            >>> spy_data = downloader.download('SPY',
            ...     start_date=date(2020, 1, 1),
            ...     end_date=date(2023, 12, 31))
            >>> print(f"Downloaded {len(spy_data.data)} data points")
        """
        # Default date range
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=3650)  # 10 years

        if self._yfinance_available:
            return self._download_with_yfinance(symbol, start_date, end_date)
        else:
            return self._download_with_http(symbol, start_date, end_date)

    def _download_with_yfinance(
        self,
        symbol: str,
        start_date: date,
        end_date: date
    ) -> MarketData:
        """Download using yfinance library."""
        import yfinance as yf

        # Download data
        ticker = yf.Ticker(symbol)
        df = ticker.history(
            start=start_date.isoformat(),
            end=end_date.isoformat(),
            auto_adjust=False  # Keep unadjusted prices
        )

        if df.empty:
            raise ValueError(f"No data available for {symbol}")

        # Convert to OHLCV objects
        data_points = []
        for idx, row in df.iterrows():
            ohlcv = OHLCV(
                date=idx.date(),
                open=float(row['Open']),
                high=float(row['High']),
                low=float(row['Low']),
                close=float(row['Close']),
                volume=int(row['Volume']),
                adjusted_close=float(row['Close'])  # Use Close if Adj Close not available
            )
            data_points.append(ohlcv)

        return MarketData(
            symbol=symbol,
            data=data_points,
            metadata={
                'source': 'yahoo_finance',
                'method': 'yfinance_library',
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'num_points': len(data_points)
            }
        )

    def _download_with_http(
        self,
        symbol: str,
        start_date: date,
        end_date: date
    ) -> MarketData:
        """
        Download using direct HTTP requests.

        Note: This is a fallback method if yfinance is not available.
        Yahoo Finance API access without yfinance may be unreliable.
        """
        import urllib.request
        import json
        from time import mktime

        # Convert dates to Unix timestamps
        start_ts = int(mktime(start_date.timetuple()))
        end_ts = int(mktime(end_date.timetuple()))

        # Build URL
        url = (
            f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            f"?period1={start_ts}&period2={end_ts}&interval=1d"
        )

        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read())

            # Parse response
            result = data['chart']['result'][0]
            timestamps = result['timestamp']
            quotes = result['indicators']['quote'][0]

            # Convert to OHLCV objects
            data_points = []
            for i, ts in enumerate(timestamps):
                dt = datetime.fromtimestamp(ts).date()

                # Skip if any price is None
                if (quotes['open'][i] is None or
                    quotes['high'][i] is None or
                    quotes['low'][i] is None or
                    quotes['close'][i] is None):
                    continue

                ohlcv = OHLCV(
                    date=dt,
                    open=float(quotes['open'][i]),
                    high=float(quotes['high'][i]),
                    low=float(quotes['low'][i]),
                    close=float(quotes['close'][i]),
                    volume=int(quotes['volume'][i] or 0),
                    adjusted_close=float(quotes['close'][i])
                )
                data_points.append(ohlcv)

            if not data_points:
                raise ValueError(f"No valid data points for {symbol}")

            return MarketData(
                symbol=symbol,
                data=data_points,
                metadata={
                    'source': 'yahoo_finance',
                    'method': 'http_api',
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'num_points': len(data_points)
                }
            )

        except Exception as e:
            raise ValueError(f"Failed to download {symbol} from Yahoo Finance: {e}")

    def download_multiple(
        self,
        symbols: list,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """
        Download data for multiple symbols.

        Args:
            symbols: List of symbols to download
            start_date: Start date
            end_date: End date

        Returns:
            Dictionary of symbol -> MarketData

        Example:
            >>> downloader = YahooFinanceDownloader()
            >>> data = downloader.download_multiple(['SPY', 'TLT', 'GLD'])
        """
        result = {}
        for symbol in symbols:
            try:
                result[symbol] = self.download(symbol, start_date, end_date)
                print(f"✓ Downloaded {symbol}: {len(result[symbol].data)} points")
            except Exception as e:
                print(f"✗ Failed to download {symbol}: {e}")

        return result
