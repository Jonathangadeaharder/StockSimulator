"""
Trading-related constraints.

Phase 2 Enhancement: Constraints on portfolio turnover and position sizing.
"""

from typing import List
import numpy as np

from .base_constraint import PortfolioConstraint, CVXPY_AVAILABLE

if CVXPY_AVAILABLE:
    import cvxpy as cp


class TurnoverConstraint(PortfolioConstraint):
    """
    Limit portfolio turnover from current allocation.

    Phase 2 Enhancement: Controls trading costs by limiting rebalancing.

    Turnover is the sum of absolute weight changes. Constraining turnover
    reduces transaction costs and can improve tax efficiency.

    Example:
        >>> # Allow maximum 20% turnover per rebalance
        >>> constraint = TurnoverConstraint(max_turnover=0.2)
        >>> # If current weights are [0.6, 0.4], new weights must satisfy:
        >>> # |new[0] - 0.6| + |new[1] - 0.4| <= 0.2
    """

    def __init__(self, max_turnover: float = 0.2):
        """
        Initialize turnover constraint.

        Args:
            max_turnover: Maximum turnover as fraction (0.2 = 20%)
        """
        self.max_turnover = max_turnover

    def apply(self, weights, current_weights: np.ndarray = None, **kwargs) -> List:
        """
        Apply turnover constraint.

        Args:
            weights: CVXPY variable for new weights
            current_weights: Current portfolio weights (required!)
            **kwargs: Additional context

        Returns:
            List of cvxpy constraints

        Raises:
            ValueError: If current_weights not provided
        """
        if not CVXPY_AVAILABLE:
            raise ImportError("cvxpy required for optimization constraints")

        if current_weights is None:
            raise ValueError("TurnoverConstraint requires current_weights parameter")

        # Sum of absolute weight changes
        turnover = cp.sum(cp.abs(weights - current_weights))
        return [turnover <= self.max_turnover]

    def validate(self, weights: np.ndarray, current_weights: np.ndarray = None, **kwargs) -> bool:
        """Validate turnover is within limit."""
        if current_weights is None:
            return True  # Can't validate without current weights

        actual_turnover = np.sum(np.abs(weights - current_weights))
        return actual_turnover <= self.max_turnover + 1e-6

    def __repr__(self) -> str:
        return f"TurnoverConstraint(max_turnover={self.max_turnover})"


class MinimumPositionSizeConstraint(PortfolioConstraint):
    """
    If holding a position, must be at least min_weight.

    Phase 2 Enhancement: Prevents dust positions.

    This constraint ensures that any non-zero position is meaningful.
    Helps avoid negligible positions that increase complexity without
    adding value.

    Note: This requires binary (integer) variables, making optimization
    harder. Consider using as a post-processing step instead.

    Example:
        >>> # Positions must be 0% or >= 2%
        >>> constraint = MinimumPositionSizeConstraint(min_weight=0.02)
    """

    def __init__(self, min_weight: float = 0.02):
        """
        Initialize minimum position size constraint.

        Args:
            min_weight: Minimum position size as fraction (0.02 = 2%)
        """
        self.min_weight = min_weight

    def apply(self, weights, **kwargs) -> List:
        """
        Apply minimum position size constraint.

        Note: This is challenging to implement with pure convex constraints.
        Returns empty list - recommend post-processing instead.
        """
        # TODO: Implement with binary variables for true constraint
        # For now, return empty (use validate() for post-processing)
        return []

    def validate(self, weights: np.ndarray, **kwargs) -> bool:
        """
        Validate positions are 0 or >= min_weight.

        Use this for post-processing optimization results.
        """
        for w in weights:
            if 0 < abs(w) < self.min_weight - 1e-6:
                return False  # Found dust position
        return True

    def enforce_post_optimization(self, weights: np.ndarray) -> np.ndarray:
        """
        Enforce constraint by zeroing out dust positions.

        Args:
            weights: Optimization result with potential dust positions

        Returns:
            Cleaned weights with dust removed and renormalized
        """
        cleaned = weights.copy()

        # Zero out positions below threshold
        cleaned[np.abs(cleaned) < self.min_weight] = 0

        # Renormalize if needed
        total = np.sum(cleaned)
        if total > 0 and abs(total - 1.0) > 1e-6:
            cleaned = cleaned / total

        return cleaned

    def __repr__(self) -> str:
        return f"MinimumPositionSizeConstraint(min_weight={self.min_weight})"
