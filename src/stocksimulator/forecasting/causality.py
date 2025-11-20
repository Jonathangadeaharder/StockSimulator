"""
Causality enforcement for backtesting.

Phase 2 Enhancement: Prevents look-ahead bias by restricting strategies
to only access historical data up to the current simulation date.

Inspired by CVXPortfolio's causality-safe forecasting callbacks.
"""

from typing import Dict, List, Optional
from datetime import date, timedelta
import pandas as pd

from stocksimulator.models.market_data import MarketData


class CausalityEnforcer:
    """
    Ensures strategies cannot access future data during backtesting.

    Phase 2 Enhancement: Critical for research validity.

    This class wraps market data and provides methods that only return
    historical data up to a specified date. Strategies receive filtered
    data instead of full market data, eliminating the possibility of
    look-ahead bias.

    Example:
        >>> # Setup
        >>> causality = CausalityEnforcer(full_market_data)
        >>>
        >>> # In backtest loop
        >>> for current_date in dates:
        ...     # Only historical data available
        ...     historical_data = causality.get_historical_data(
        ...         symbols=['SPY', 'AGG'],
        ...         end_date=current_date,
        ...         lookback_days=252
        ...     )
        ...     # Strategy cannot see future!
        ...     allocation = strategy(current_date, historical_data, ...)
    """

    def __init__(self, full_market_data: Dict[str, MarketData]):
        """
        Initialize causality enforcer.

        Args:
            full_market_data: Complete market data (all dates)
        """
        self.full_data = full_market_data
        self._cache = {}  # Cache for performance

    def get_historical_data(
        self,
        symbols: List[str],
        end_date: date,
        lookback_days: Optional[int] = None,
        start_date: Optional[date] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Get historical data up to end_date (causality-safe).

        Returns only data points with date <= end_date, ensuring
        no future information leaks into the strategy.

        Args:
            symbols: List of symbols to fetch
            end_date: Latest date to include (inclusive)
            lookback_days: Optional lookback window (from end_date)
            start_date: Optional explicit start date

        Returns:
            Dictionary mapping symbol -> DataFrame with OHLCV data
            Each DataFrame has columns: date, open, high, low, close, volume

        Example:
            >>> # Get last 252 trading days up to current_date
            >>> hist_data = enforcer.get_historical_data(
            ...     symbols=['SPY'],
            ...     end_date=current_date,
            ...     lookback_days=252
            ... )
            >>> spy_df = hist_data['SPY']
            >>> assert all(spy_df['date'] <= current_date)  # Guaranteed!
        """
        # Create cache key
        cache_key = (tuple(sorted(symbols)), end_date, lookback_days, start_date)

        # Check cache
        if cache_key in self._cache:
            return self._cache[cache_key].copy()

        historical = {}

        for symbol in symbols:
            if symbol not in self.full_data:
                # Symbol not available - return empty DataFrame
                historical[symbol] = pd.DataFrame(
                    columns=['date', 'open', 'high', 'low', 'close', 'volume']
                )
                continue

            # Get all data for symbol
            market_data = self.full_data[symbol]

            # Filter to only data <= end_date (CAUSALITY ENFORCEMENT!)
            historical_points = [
                d for d in market_data.data
                if d.date <= end_date
            ]

            if not historical_points:
                historical[symbol] = pd.DataFrame(
                    columns=['date', 'open', 'high', 'low', 'close', 'volume']
                )
                continue

            # Apply lookback window if specified
            if lookback_days is not None and lookback_days > 0:
                # Keep last lookback_days points
                historical_points = historical_points[-lookback_days:]

            # Apply start_date filter if specified
            if start_date is not None:
                historical_points = [
                    d for d in historical_points
                    if d.date >= start_date
                ]

            # Convert to DataFrame
            df = pd.DataFrame([
                {
                    'date': d.date,
                    'open': d.open,
                    'high': d.high,
                    'low': d.low,
                    'close': d.close,
                    'volume': d.volume
                }
                for d in historical_points
            ])

            historical[symbol] = df

        # Cache result
        self._cache[cache_key] = {k: v.copy() for k, v in historical.items()}

        return historical

    def get_available_dates(
        self,
        symbols: List[str],
        end_date: Optional[date] = None
    ) -> List[date]:
        """
        Get all available dates for given symbols (up to end_date).

        Args:
            symbols: List of symbols
            end_date: Latest date to include (None = all dates)

        Returns:
            Sorted list of dates with data for at least one symbol
        """
        all_dates = set()

        for symbol in symbols:
            if symbol not in self.full_data:
                continue

            for d in self.full_data[symbol].data:
                if end_date is None or d.date <= end_date:
                    all_dates.add(d.date)

        return sorted(all_dates)

    def validate_no_future_access(
        self,
        current_date: date,
        data_dict: Dict[str, pd.DataFrame]
    ) -> bool:
        """
        Validate that provided data contains no future information.

        Args:
            current_date: Current simulation date
            data_dict: Dictionary of symbol -> DataFrame to validate

        Returns:
            True if valid (no future data), False if future data detected

        Raises:
            ValueError: If future data is detected and strict validation is on
        """
        for symbol, df in data_dict.items():
            if df.empty:
                continue

            # Check all dates are <= current_date
            future_dates = df[df['date'] > current_date]

            if not future_dates.empty:
                raise ValueError(
                    f"CAUSALITY VIOLATION! Symbol '{symbol}' contains "
                    f"{len(future_dates)} data points from the future. "
                    f"Current date: {current_date}, "
                    f"Latest future date: {future_dates['date'].max()}"
                )

        return True

    def clear_cache(self) -> None:
        """Clear the internal cache."""
        self._cache.clear()

    def get_cache_size(self) -> int:
        """Get number of cached entries."""
        return len(self._cache)

    def __repr__(self) -> str:
        return (f"CausalityEnforcer("
                f"symbols={len(self.full_data)}, "
                f"cache_size={len(self._cache)})")
