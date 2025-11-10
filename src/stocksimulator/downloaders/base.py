"""
Base Downloader

Abstract base class for data downloaders.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from stocksimulator.models.market_data import MarketData


class DataDownloader(ABC):
    """Base class for market data downloaders."""

    @abstractmethod
    def download(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> MarketData:
        """
        Download market data for a symbol.

        Args:
            symbol: Stock/ETF symbol
            start_date: Start date (None = earliest available)
            end_date: End date (None = today)

        Returns:
            MarketData object

        Raises:
            ValueError: If symbol is invalid or data unavailable
        """
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this data source is available.

        Returns:
            True if source can be accessed
        """
        raise NotImplementedError
