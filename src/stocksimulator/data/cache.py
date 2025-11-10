"""
Data Cache

Simple in-memory cache for loaded market data.
"""

from typing import Dict, Optional
from stocksimulator.models.market_data import MarketData


class DataCache:
    """
    Simple in-memory cache for market data.

    Avoids reloading the same CSV files multiple times.
    """

    def __init__(self):
        """Initialize empty cache."""
        self._cache: Dict[str, MarketData] = {}

    def get(self, symbol: str) -> Optional[MarketData]:
        """
        Get market data from cache.

        Args:
            symbol: Symbol to retrieve

        Returns:
            MarketData or None if not in cache
        """
        return self._cache.get(symbol)

    def set(self, symbol: str, data: MarketData) -> None:
        """
        Store market data in cache.

        Args:
            symbol: Symbol to store
            data: MarketData to cache
        """
        self._cache[symbol] = data

    def has(self, symbol: str) -> bool:
        """
        Check if symbol is in cache.

        Args:
            symbol: Symbol to check

        Returns:
            True if in cache
        """
        return symbol in self._cache

    def clear(self, symbol: Optional[str] = None) -> None:
        """
        Clear cache.

        Args:
            symbol: Symbol to clear (None = clear all)
        """
        if symbol is None:
            self._cache.clear()
        else:
            self._cache.pop(symbol, None)

    def size(self) -> int:
        """Get number of cached symbols."""
        return len(self._cache)

    def symbols(self) -> list:
        """Get list of cached symbols."""
        return list(self._cache.keys())
