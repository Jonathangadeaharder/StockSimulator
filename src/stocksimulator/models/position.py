"""
Position data model

Represents a single position (holding) in a portfolio.
"""

from typing import Optional
from datetime import datetime


class Position:
    """
    A position representing shares of a security.

    Attributes:
        symbol: Stock ticker symbol
        shares: Number of shares held (can be negative for short positions)
        cost_basis: Average cost per share
        opened_at: When position was first opened
        updated_at: Last update timestamp
    """

    def __init__(
        self,
        symbol: str,
        shares: float,
        cost_basis: float,
        opened_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialize a position.

        Args:
            symbol: Stock ticker symbol
            shares: Number of shares
            cost_basis: Average cost per share
            opened_at: Opening timestamp (default: now)
            updated_at: Last update timestamp (default: now)
        """
        self.symbol = symbol
        self.shares = shares
        self.cost_basis = cost_basis
        self.opened_at = opened_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def get_market_value(self, current_price: float) -> float:
        """Calculate current market value of position."""
        return self.shares * current_price

    def get_cost_value(self) -> float:
        """Calculate total cost basis of position."""
        return self.shares * self.cost_basis

    def get_unrealized_pnl(self, current_price: float) -> dict:
        """
        Calculate unrealized profit/loss.

        Args:
            current_price: Current market price

        Returns:
            Dictionary with dollar_pnl, percent_pnl, market_value, cost_value
        """
        market_value = self.get_market_value(current_price)
        cost_value = self.get_cost_value()
        dollar_pnl = market_value - cost_value
        percent_pnl = (dollar_pnl / cost_value * 100) if cost_value != 0 else 0

        return {
            'dollar_pnl': dollar_pnl,
            'percent_pnl': percent_pnl,
            'market_value': market_value,
            'cost_value': cost_value,
            'current_price': current_price,
            'cost_basis': self.cost_basis
        }

    def update_shares(self, additional_shares: float, price: float) -> None:
        """
        Update position with additional shares and recalculate cost basis.

        Args:
            additional_shares: Number of shares to add (negative to reduce)
            price: Price of the additional shares
        """
        if additional_shares == 0:
            return

        new_total_shares = self.shares + additional_shares

        if new_total_shares == 0:
            # Position closed
            self.shares = 0
            self.cost_basis = 0
        elif self.shares * additional_shares >= 0:
            # Same direction - update cost basis
            total_cost = self.shares * self.cost_basis + additional_shares * price
            self.shares = new_total_shares
            self.cost_basis = total_cost / new_total_shares
        else:
            # Opposite direction - reducing position
            self.shares = new_total_shares
            # Cost basis stays the same when reducing

        self.updated_at = datetime.utcnow()

    def is_long(self) -> bool:
        """Check if this is a long position."""
        return self.shares > 0

    def is_short(self) -> bool:
        """Check if this is a short position."""
        return self.shares < 0

    def is_closed(self) -> bool:
        """Check if position is closed."""
        return self.shares == 0

    def __repr__(self) -> str:
        return (f"Position(symbol={self.symbol}, shares={self.shares:.2f}, "
                f"cost_basis=${self.cost_basis:.2f})")
