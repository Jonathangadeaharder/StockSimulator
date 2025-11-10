"""
Market Data model

Represents historical and real-time market data for securities.
"""

from typing import List, Dict, Optional
from datetime import datetime, date
from dataclasses import dataclass


@dataclass
class OHLCV:
    """Open, High, Low, Close, Volume data point."""
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: Optional[float] = None


class MarketData:
    """
    Market data container for a security.

    Attributes:
        symbol: Stock ticker symbol
        data: List of OHLCV data points
        metadata: Additional metadata about the data source
    """

    def __init__(
        self,
        symbol: str,
        data: Optional[List[OHLCV]] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Initialize market data.

        Args:
            symbol: Stock ticker symbol
            data: List of OHLCV data points
            metadata: Optional metadata dictionary
        """
        self.symbol = symbol
        self.data = data or []
        self.metadata = metadata or {}

    def add_data_point(self, ohlcv: OHLCV) -> None:
        """Add a data point."""
        self.data.append(ohlcv)

    def get_data_range(
        self,
        start_date: date,
        end_date: date
    ) -> List[OHLCV]:
        """
        Get data within a date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of OHLCV data points within range
        """
        return [
            d for d in self.data
            if start_date <= d.date <= end_date
        ]

    def get_latest(self, n: int = 1) -> List[OHLCV]:
        """Get the latest n data points."""
        return sorted(self.data, key=lambda x: x.date, reverse=True)[:n]

    def get_price_on_date(self, target_date: date) -> Optional[float]:
        """
        Get closing price on a specific date.

        Args:
            target_date: Target date

        Returns:
            Closing price or None if not found
        """
        for d in self.data:
            if d.date == target_date:
                return d.adjusted_close or d.close
        return None

    def get_returns(self, period_days: int = 1) -> List[Dict]:
        """
        Calculate returns over specified period.

        Args:
            period_days: Number of days for return calculation

        Returns:
            List of dictionaries with date and return
        """
        sorted_data = sorted(self.data, key=lambda x: x.date)
        returns = []

        for i in range(period_days, len(sorted_data)):
            current = sorted_data[i]
            previous = sorted_data[i - period_days]

            current_price = current.adjusted_close or current.close
            previous_price = previous.adjusted_close or previous.close

            if previous_price > 0:
                ret = (current_price - previous_price) / previous_price
                returns.append({
                    'date': current.date,
                    'return': ret,
                    'price': current_price
                })

        return returns

    def get_volatility(self, window_days: int = 252) -> Optional[float]:
        """
        Calculate annualized volatility.

        Args:
            window_days: Rolling window size in days

        Returns:
            Annualized volatility or None if insufficient data
        """
        daily_returns = self.get_returns(period_days=1)

        if len(daily_returns) < window_days:
            return None

        # Use last window_days returns
        recent_returns = [r['return'] for r in daily_returns[-window_days:]]

        # Calculate standard deviation
        mean = sum(recent_returns) / len(recent_returns)
        variance = sum((r - mean) ** 2 for r in recent_returns) / (len(recent_returns) - 1)
        daily_vol = variance ** 0.5

        # Annualize
        annual_vol = daily_vol * (252 ** 0.5)

        return annual_vol

    def get_max_drawdown(self) -> Dict:
        """
        Calculate maximum drawdown.

        Returns:
            Dictionary with max_drawdown, peak_date, trough_date
        """
        sorted_data = sorted(self.data, key=lambda x: x.date)

        if not sorted_data:
            return {'max_drawdown': 0, 'peak_date': None, 'trough_date': None}

        peak = sorted_data[0].close
        peak_date = sorted_data[0].date
        max_dd = 0
        trough_date = None

        for d in sorted_data:
            price = d.adjusted_close or d.close

            if price > peak:
                peak = price
                peak_date = d.date

            drawdown = (peak - price) / peak if peak > 0 else 0

            if drawdown > max_dd:
                max_dd = drawdown
                trough_date = d.date

        return {
            'max_drawdown': max_dd * 100,  # As percentage
            'peak_date': peak_date,
            'trough_date': trough_date
        }

    def to_dict_list(self) -> List[Dict]:
        """Convert data to list of dictionaries."""
        return [
            {
                'date': d.date.isoformat(),
                'open': d.open,
                'high': d.high,
                'low': d.low,
                'close': d.close,
                'volume': d.volume,
                'adjusted_close': d.adjusted_close
            }
            for d in sorted(self.data, key=lambda x: x.date)
        ]

    def __repr__(self) -> str:
        return f"MarketData(symbol={self.symbol}, data_points={len(self.data)})"
