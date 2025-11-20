"""
Holding cost modeling.
"""

from typing import Dict
from datetime import date
from .base_cost import BaseCost


class HoldingCost(BaseCost):
    """
    Models costs of maintaining positions.

    Holding costs include:
    - Custody fees
    - Account maintenance fees
    - Borrowing costs for margin

    Typically small for long-only equity portfolios but can be
    significant for leveraged or short positions.
    """

    def __init__(self, annual_rate: float = 0.001):
        """
        Initialize holding cost model.

        Args:
            annual_rate: Annual holding cost as a fraction of portfolio value
                        (default: 0.001 = 0.1% per year)
        """
        self.annual_rate = annual_rate
        self.daily_rate = annual_rate / 252  # Convert to daily rate

    def calculate(
        self,
        trades: Dict[str, float],
        positions: Dict[str, float],
        prices: Dict[str, float],
        current_date: date
    ) -> float:
        """
        Calculate holding costs for all positions.

        Args:
            trades: Dictionary of symbol -> shares traded (not used)
            positions: Dictionary of symbol -> current shares held
            prices: Dictionary of symbol -> current price
            current_date: Current date (not used)

        Returns:
            Total holding cost for this period
        """
        total_value = 0.0

        for symbol, shares in positions.items():
            if abs(shares) < 1e-10:  # Skip negligible positions
                continue

            if symbol not in prices or prices[symbol] <= 0:
                continue

            position_value = abs(shares * prices[symbol])
            total_value += position_value

        # Apply daily holding cost rate
        return total_value * self.daily_rate

    def __repr__(self) -> str:
        return f"HoldingCost(annual_rate={self.annual_rate})"
