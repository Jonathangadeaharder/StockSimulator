"""
Position Sizing

Methods for determining optimal position sizes.
"""

from typing import List, Optional
import math


class PositionSizer:
    """Base class for position sizing methods."""

    def calculate_position_size(self, account_value: float, **kwargs) -> float:
        """
        Calculate position size.

        Args:
            account_value: Current account value
            **kwargs: Additional parameters

        Returns:
            Position size in dollars
        """
        raise NotImplementedError


class KellyCriterion(PositionSizer):
    """
    Kelly Criterion position sizing.

    Maximizes long-term growth rate.

    Formula: f = (p * b - q) / b
    Where:
    - f = fraction of capital to bet
    - p = probability of winning
    - q = probability of losing (1 - p)
    - b = odds (avg_win / avg_loss)
    """

    def __init__(self, fraction: float = 0.5):
        """
        Initialize Kelly Criterion.

        Args:
            fraction: Fraction of Kelly to use (0.5 = half Kelly, safer)
        """
        self.fraction = fraction

    def calculate_position_size(
        self,
        account_value: float,
        win_rate: float,
        avg_win: float,
        avg_loss: float
    ) -> float:
        """
        Calculate Kelly position size.

        Args:
            account_value: Current account value
            win_rate: Win rate (0-1)
            avg_win: Average winning trade
            avg_loss: Average losing trade (positive number)

        Returns:
            Position size in dollars

        Example:
            >>> kelly = KellyCriterion(fraction=0.5)  # Half Kelly
            >>> position = kelly.calculate_position_size(
            ...     account_value=100000,
            ...     win_rate=0.60,
            ...     avg_win=0.05,
            ...     avg_loss=0.03
            ... )
            >>> print(f"Position size: ${position:,.2f}")
        """
        if avg_loss == 0:
            return 0.0

        p = win_rate
        q = 1 - win_rate
        b = avg_win / avg_loss

        # Kelly formula
        kelly_pct = (p * b - q) / b

        # Clamp to 0-100%
        kelly_pct = max(0.0, min(1.0, kelly_pct))

        # Apply fractional Kelly
        kelly_pct *= self.fraction

        return account_value * kelly_pct


class FixedFractional(PositionSizer):
    """
    Fixed Fractional position sizing.

    Risk fixed percentage of account on each trade.
    """

    def __init__(self, risk_pct: float = 0.02):
        """
        Initialize Fixed Fractional.

        Args:
            risk_pct: Percentage of account to risk per trade (default: 2%)
        """
        self.risk_pct = risk_pct

    def calculate_position_size(
        self,
        account_value: float,
        stop_loss_pct: Optional[float] = None,
        entry_price: Optional[float] = None,
        stop_price: Optional[float] = None
    ) -> float:
        """
        Calculate fixed fractional position size.

        Args:
            account_value: Current account value
            stop_loss_pct: Stop loss as percentage (e.g., 0.05 for 5%)
            entry_price: Entry price
            stop_price: Stop loss price

        Returns:
            Position size in dollars

        Example:
            >>> ff = FixedFractional(risk_pct=0.02)  # Risk 2% per trade
            >>> position = ff.calculate_position_size(
            ...     account_value=100000,
            ...     stop_loss_pct=0.05  # 5% stop loss
            ... )
            >>> print(f"Position size: ${position:,.2f}")
        """
        # Calculate risk per trade
        risk_amount = account_value * self.risk_pct

        # If stop loss percentage provided
        if stop_loss_pct:
            position_size = risk_amount / stop_loss_pct
            return position_size

        # If entry and stop prices provided
        if entry_price and stop_price:
            risk_per_share = abs(entry_price - stop_price)
            if risk_per_share > 0:
                shares = risk_amount / risk_per_share
                position_size = shares * entry_price
                return position_size

        # Default: use risk amount
        return risk_amount


