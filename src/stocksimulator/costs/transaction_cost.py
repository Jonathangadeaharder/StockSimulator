"""
Transaction cost modeling.
"""

from typing import Dict
from datetime import date
from .base_cost import BaseCost


class TransactionCost(BaseCost):
    """
    Models transaction costs including spread and market impact.

    Transaction costs are incurred when buying or selling securities.
    Includes:
    - Base transaction cost (brokerage fees, bid-ask spread)
    - Optional market impact cost (price impact for large trades)
    """

    def __init__(
        self,
        base_bps: float = 2.0,
        market_impact_factor: float = 0.0
    ):
        """
        Initialize transaction cost model.

        Args:
            base_bps: Base transaction cost in basis points (default: 2 bps)
            market_impact_factor: Market impact coefficient (0 = no impact)
                                 Market impact = factor * sqrt(trade_value)
        """
        self.base_bps = base_bps
        self.market_impact_factor = market_impact_factor

    def calculate(
        self,
        trades: Dict[str, float],
        positions: Dict[str, float],
        prices: Dict[str, float],
        current_date: date
    ) -> float:
        """
        Calculate transaction costs for all trades.

        Args:
            trades: Dictionary of symbol -> shares traded
            positions: Dictionary of symbol -> current shares (not used)
            prices: Dictionary of symbol -> current price
            current_date: Current date (not used)

        Returns:
            Total transaction cost
        """
        total_cost = 0.0

        for symbol, shares in trades.items():
            if abs(shares) < 1e-10:  # Skip negligible trades
                continue

            if symbol not in prices or prices[symbol] <= 0:
                continue

            trade_value = abs(shares * prices[symbol])

            # Base transaction cost
            base_cost = trade_value * (self.base_bps / 10000)
            total_cost += base_cost

            # Market impact (square root law)
            if self.market_impact_factor > 0:
                impact = self.market_impact_factor * (trade_value ** 0.5)
                total_cost += impact

        return total_cost

    def __repr__(self) -> str:
        return f"TransactionCost(base_bps={self.base_bps}, market_impact_factor={self.market_impact_factor})"
