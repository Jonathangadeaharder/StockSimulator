"""
Dollar-Cost Averaging (DCA) Strategy

Implements a simple DCA strategy that maintains fixed allocations and
rebalances periodically regardless of market conditions.
"""

from typing import Dict, Optional
from datetime import date

from stocksimulator.strategies.base_strategy import BaseStrategy
from stocksimulator.models.portfolio import Portfolio
from stocksimulator.models.market_data import MarketData


class DCAStrategy(BaseStrategy):
    """
    Dollar-Cost Averaging Strategy.

    Maintains a fixed target allocation regardless of market conditions.
    This is the classic "set it and forget it" approach.

    Parameters:
        target_allocation: Dictionary of symbol -> target percentage
        rebalance_threshold: Minimum deviation to trigger rebalance (default: 5%)

    Example:
        >>> strategy = DCAStrategy(
        ...     target_allocation={'SPY': 60.0, 'TLT': 40.0},
        ...     rebalance_threshold=5.0
        ... )
    """

    def __init__(
        self,
        target_allocation: Dict[str, float],
        rebalance_threshold: float = 5.0,
        name: str = "DCA Strategy"
    ):
        """
        Initialize DCA strategy.

        Args:
            target_allocation: Target allocation (e.g., {'SPY': 60, 'TLT': 40})
            rebalance_threshold: Rebalance when allocation drifts by this % (default: 5%)
            name: Strategy name
        """
        super().__init__(
            name=name,
            description="Dollar-Cost Averaging with fixed allocations",
            parameters={
                'target_allocation': target_allocation,
                'rebalance_threshold': rebalance_threshold
            }
        )

        # Validate target allocation
        if not self.validate_allocation(target_allocation):
            raise ValueError("Invalid target allocation")

        self.target_allocation = target_allocation
        self.rebalance_threshold = rebalance_threshold

    def calculate_allocation(
        self,
        current_date: date,
        market_data: Dict[str, MarketData],
        portfolio: Portfolio,
        current_prices: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate target allocation (always returns target_allocation).

        For DCA, we always return the same target allocation regardless
        of market conditions. The rebalancing logic handles when to
        actually trade based on drift.

        Args:
            current_date: Current date
            market_data: Market data
            portfolio: Current portfolio
            current_prices: Current prices

        Returns:
            Target allocation dictionary
        """
        # For DCA, always return the target allocation
        # The backtester/portfolio manager handles the actual rebalancing
        return self.target_allocation.copy()

    def should_rebalance(
        self,
        current_allocation: Dict[str, float],
        target_allocation: Dict[str, float]
    ) -> bool:
        """
        Check if portfolio has drifted enough to warrant rebalancing.

        Args:
            current_allocation: Current portfolio allocation
            target_allocation: Target allocation

        Returns:
            True if should rebalance, False otherwise
        """
        for symbol, target_pct in target_allocation.items():
            current_pct = current_allocation.get(symbol, 0.0)
            drift = abs(current_pct - target_pct)

            if drift > self.rebalance_threshold:
                return True

        return False


class FixedAllocationStrategy(DCAStrategy):
    """
    Alias for DCA Strategy with more descriptive name.

    This is the same as DCA but with a name that better describes
    the "fixed allocation" nature of the strategy.
    """

    def __init__(
        self,
        target_allocation: Dict[str, float],
        rebalance_threshold: float = 5.0
    ):
        super().__init__(
            target_allocation=target_allocation,
            rebalance_threshold=rebalance_threshold,
            name="Fixed Allocation Strategy"
        )


class Balanced6040Strategy(DCAStrategy):
    """
    Classic 60/40 balanced portfolio (60% stocks, 40% bonds).

    Pre-configured DCA strategy for the traditional balanced portfolio.

    Parameters:
        stock_symbol: Stock ETF symbol (default: 'SPY')
        bond_symbol: Bond ETF symbol (default: 'TLT')
        stock_allocation: Stock percentage (default: 60%)
        rebalance_threshold: Rebalance threshold (default: 5%)

    Example:
        >>> strategy = Balanced6040Strategy()
        >>> # Returns {'SPY': 60.0, 'TLT': 40.0}
    """

    def __init__(
        self,
        stock_symbol: str = 'SPY',
        bond_symbol: str = 'TLT',
        stock_allocation: float = 60.0,
        rebalance_threshold: float = 5.0
    ):
        """Initialize 60/40 balanced strategy."""
        bond_allocation = 100.0 - stock_allocation

        target_allocation = {
            stock_symbol: stock_allocation,
            bond_symbol: bond_allocation
        }

        super().__init__(
            target_allocation=target_allocation,
            rebalance_threshold=rebalance_threshold,
            name=f"{stock_allocation:.0f}/{bond_allocation:.0f} Balanced Portfolio"
        )


class AllWeatherStrategy(DCAStrategy):
    """
    Ray Dalio's All Weather Portfolio.

    A risk parity inspired allocation designed to perform well in
    all economic environments.

    Default allocation:
    - 30% Stocks (SPY)
    - 40% Long-term Bonds (TLT)
    - 15% Intermediate Bonds (IEF)
    - 7.5% Gold (GLD)
    - 7.5% Commodities (DBC)

    Example:
        >>> strategy = AllWeatherStrategy()
    """

    def __init__(
        self,
        symbols: Optional[Dict[str, str]] = None,
        rebalance_threshold: float = 5.0
    ):
        """
        Initialize All Weather strategy.

        Args:
            symbols: Optional custom symbols (default: SPY, TLT, IEF, GLD, DBC)
            rebalance_threshold: Rebalance threshold
        """
        if symbols is None:
            symbols = {
                'stocks': 'SPY',
                'long_bonds': 'TLT',
                'intermediate_bonds': 'IEF',
                'gold': 'GLD',
                'commodities': 'DBC'
            }

        target_allocation = {
            symbols['stocks']: 30.0,
            symbols['long_bonds']: 40.0,
            symbols['intermediate_bonds']: 15.0,
            symbols['gold']: 7.5,
            symbols['commodities']: 7.5
        }

        super().__init__(
            target_allocation=target_allocation,
            rebalance_threshold=rebalance_threshold,
            name="All Weather Portfolio"
        )
