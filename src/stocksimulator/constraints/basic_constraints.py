"""
Basic portfolio constraints.

Phase 2 Enhancement: Fundamental constraints for portfolio construction.
"""

from typing import List
import numpy as np

from .base_constraint import PortfolioConstraint, CVXPY_AVAILABLE

if CVXPY_AVAILABLE:
    import cvxpy as cp


class LongOnlyConstraint(PortfolioConstraint):
    """
    No short positions allowed (all weights >= 0).

    Phase 2 Enhancement: Most common constraint for long-only portfolios.

    Example:
        >>> constraint = LongOnlyConstraint()
        >>> # In optimization: weights >= 0
    """

    def apply(self, weights, **kwargs) -> List:
        """Apply long-only constraint."""
        if not CVXPY_AVAILABLE:
            raise ImportError("cvxpy required for optimization constraints")

        return [weights >= 0]

    def validate(self, weights: np.ndarray, **kwargs) -> bool:
        """Check all weights are non-negative."""
        return np.all(weights >= -1e-6)  # Small tolerance for numerical errors

    def __repr__(self) -> str:
        return "LongOnlyConstraint()"


class LeverageLimitConstraint(PortfolioConstraint):
    """
    Limit total portfolio leverage.

    Phase 2 Enhancement: Controls maximum gross exposure.

    The sum of absolute values of weights cannot exceed max_leverage.
    - max_leverage=1.0: No leverage (long-only with cash)
    - max_leverage=1.3: 130/30 portfolio (130% long, 30% short)
    - max_leverage=2.0: 2x leverage

    Example:
        >>> # No leverage allowed
        >>> constraint = LeverageLimitConstraint(max_leverage=1.0)
        >>>
        >>> # Allow 130/30
        >>> constraint = LeverageLimitConstraint(max_leverage=1.6)
    """

    def __init__(self, max_leverage: float = 1.0):
        """
        Initialize leverage limit constraint.

        Args:
            max_leverage: Maximum sum of absolute weights
        """
        self.max_leverage = max_leverage

    def apply(self, weights, **kwargs) -> List:
        """Apply leverage limit constraint."""
        if not CVXPY_AVAILABLE:
            raise ImportError("cvxpy required for optimization constraints")

        # Sum of absolute values <= max_leverage
        return [cp.sum(cp.abs(weights)) <= self.max_leverage]

    def validate(self, weights: np.ndarray, **kwargs) -> bool:
        """Check leverage is within limit."""
        actual_leverage = np.sum(np.abs(weights))
        return actual_leverage <= self.max_leverage + 1e-6

    def __repr__(self) -> str:
        return f"LeverageLimitConstraint(max_leverage={self.max_leverage})"


class FullInvestmentConstraint(PortfolioConstraint):
    """
    Require weights to sum to exactly 1 (no cash).

    Phase 2 Enhancement: Ensures full capital deployment.

    Example:
        >>> constraint = FullInvestmentConstraint()
        >>> # In optimization: sum(weights) == 1.0
    """

    def __init__(self, target_sum: float = 1.0, tolerance: float = 0.001):
        """
        Initialize full investment constraint.

        Args:
            target_sum: Target sum of weights (default: 1.0)
            tolerance: Tolerance for validation (default: 0.001)
        """
        self.target_sum = target_sum
        self.tolerance = tolerance

    def apply(self, weights, **kwargs) -> List:
        """Apply full investment constraint."""
        if not CVXPY_AVAILABLE:
            raise ImportError("cvxpy required for optimization constraints")

        return [cp.sum(weights) == self.target_sum]

    def validate(self, weights: np.ndarray, **kwargs) -> bool:
        """Check weights sum to target."""
        actual_sum = np.sum(weights)
        return abs(actual_sum - self.target_sum) <= self.tolerance

    def __repr__(self) -> str:
        return f"FullInvestmentConstraint(target_sum={self.target_sum})"
