"""
Base Strategy Class

Abstract base class for all trading strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import date
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from stocksimulator.models.portfolio import Portfolio
from stocksimulator.models.market_data import MarketData


class BaseStrategy(ABC):
    """
    Abstract base class for trading strategies.

    All strategies must implement the calculate_allocation method which
    returns target portfolio allocations based on current market conditions.

    Attributes:
        name: Strategy name
        description: Strategy description
        parameters: Dictionary of strategy parameters
    """

    def __init__(self, name: str, description: str = "", parameters: Optional[Dict] = None):
        """
        Initialize strategy.

        Args:
            name: Strategy name
            description: Strategy description
            parameters: Dictionary of strategy-specific parameters
        """
        self.name = name
        self.description = description
        self.parameters = parameters or {}

    @abstractmethod
    def calculate_allocation(
        self,
        current_date: date,
        market_data: Dict[str, MarketData],
        portfolio: Portfolio,
        current_prices: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate target portfolio allocation.

        This is the core method that each strategy must implement.

        Args:
            current_date: Current simulation date
            market_data: Dictionary of symbol -> MarketData
            portfolio: Current portfolio state
            current_prices: Dictionary of symbol -> current price

        Returns:
            Dictionary of symbol -> target allocation percentage
            Must sum to <= 100.0 (remainder is cash)

        Example:
            {'SPY': 60.0, 'TLT': 40.0}  # 60% SPY, 40% TLT
            {'QQQ': 80.0}                # 80% QQQ, 20% cash
        """
        pass

    def validate_allocation(self, allocation: Dict[str, float]) -> bool:
        """
        Validate that allocation is valid.

        Args:
            allocation: Proposed allocation

        Returns:
            True if valid, False otherwise
        """
        if not allocation:
            return False

        total = sum(allocation.values())

        # Check total doesn't exceed 100%
        if total > 100.01:  # Small tolerance for floating point
            return False

        # Check all values are non-negative
        if any(v < 0 for v in allocation.values()):
            return False

        return True

    def get_lookback_data(
        self,
        market_data: MarketData,
        current_date: date,
        lookback_days: int
    ) -> List:
        """
        Get historical data for lookback period.

        Args:
            market_data: MarketData object
            current_date: Current date
            lookback_days: Number of days to look back

        Returns:
            List of OHLCV data points
        """
        all_data = sorted(market_data.data, key=lambda x: x.date)

        # Find current date index
        current_idx = None
        for i, d in enumerate(all_data):
            if d.date <= current_date:
                current_idx = i
            else:
                break

        if current_idx is None:
            return []

        start_idx = max(0, current_idx - lookback_days + 1)
        return all_data[start_idx:current_idx + 1]

    def calculate_moving_average(
        self,
        data: List,
        period: int,
        price_field: str = 'close'
    ) -> Optional[float]:
        """
        Calculate simple moving average.

        Args:
            data: List of OHLCV data points
            period: Moving average period
            price_field: Which price to use ('open', 'high', 'low', 'close')

        Returns:
            Moving average value or None if insufficient data
        """
        if len(data) < period:
            return None

        recent_data = data[-period:]
        prices = [getattr(d, price_field) for d in recent_data]

        return sum(prices) / len(prices)

    def calculate_returns(
        self,
        data: List,
        period: int = 1,
        price_field: str = 'close'
    ) -> List[float]:
        """
        Calculate period returns.

        Args:
            data: List of OHLCV data points
            period: Period for return calculation
            price_field: Which price to use

        Returns:
            List of returns
        """
        if len(data) < period + 1:
            return []

        returns = []
        for i in range(period, len(data)):
            current_price = getattr(data[i], price_field)
            previous_price = getattr(data[i - period], price_field)

            if previous_price > 0:
                ret = (current_price - previous_price) / previous_price
                returns.append(ret)

        return returns

    def calculate_volatility(
        self,
        returns: List[float],
        annualize: bool = True,
        periods_per_year: int = 252
    ) -> float:
        """
        Calculate volatility from returns.

        Args:
            returns: List of returns
            annualize: Whether to annualize
            periods_per_year: Periods per year for annualization

        Returns:
            Volatility (standard deviation)
        """
        if len(returns) < 2:
            return 0.0

        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
        std_dev = variance ** 0.5

        if annualize:
            return std_dev * (periods_per_year ** 0.5)

        return std_dev

    def __call__(
        self,
        current_date: date,
        market_data: Dict[str, MarketData],
        portfolio: Portfolio,
        current_prices: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Callable interface for strategy.

        Allows using strategy as a function in backtests.
        """
        return self.calculate_allocation(current_date, market_data, portfolio, current_prices)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"

    def __str__(self) -> str:
        return self.name
