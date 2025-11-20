"""
Base constraint class.

Phase 2 Enhancement: Abstract base class for portfolio constraints.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import numpy as np

# Try to import cvxpy for optimization constraints
try:
    import cvxpy as cp
    CVXPY_AVAILABLE = True
except ImportError:
    CVXPY_AVAILABLE = False


class PortfolioConstraint(ABC):
    """
    Abstract base class for portfolio constraints.

    Phase 2 Enhancement: Extensible constraint framework inspired by Riskfolio-Lib.

    Constraints restrict the feasible region of portfolio optimization
    problems. Each constraint implements an apply() method that returns
    a list of cvxpy constraint objects.

    Example:
        >>> # Define custom constraint
        >>> class MaxPositionConstraint(PortfolioConstraint):
        ...     def __init__(self, max_weight=0.3):
        ...         self.max_weight = max_weight
        ...
        ...     def apply(self, weights, **kwargs):
        ...         # Each position <= 30%
        ...         return [weights <= self.max_weight]
        >>>
        >>> # Use in optimization
        >>> optimizer = ConstrainedOptimizer(constraints=[
        ...     MaxPositionConstraint(max_weight=0.3),
        ...     LongOnlyConstraint()
        ... ])
    """

    @abstractmethod
    def apply(self, weights, **kwargs) -> List:
        """
        Apply constraint to optimization problem.

        Args:
            weights: CVXPY variable for portfolio weights (n_assets,)
            **kwargs: Additional context (prices, covariances, etc.)

        Returns:
            List of cvxpy constraint objects

        Example:
            >>> def apply(self, weights, **kwargs):
            ...     # Weights must sum to 1
            ...     return [cp.sum(weights) == 1]
        """
        pass

    def validate(self, weights: np.ndarray, **kwargs) -> bool:
        """
        Validate that weights satisfy constraint (post-optimization check).

        Phase 2 Enhancement: Optional validation for debugging.

        Args:
            weights: Numpy array of portfolio weights
            **kwargs: Additional context

        Returns:
            True if weights satisfy constraint, False otherwise
        """
        return True  # Default: assume valid

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
