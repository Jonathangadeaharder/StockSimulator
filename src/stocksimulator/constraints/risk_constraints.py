"""
Risk-related constraints.

Phase 2 Enhancement: Constraints targeting specific risk metrics.
"""

from typing import List
import numpy as np

from .base_constraint import PortfolioConstraint, CVXPY_AVAILABLE

if CVXPY_AVAILABLE:
    import cvxpy as cp


class VolatilityTargetConstraint(PortfolioConstraint):
    """
    Target specific portfolio volatility.

    Phase 2 Enhancement: Risk budgeting constraint.

    Constrains portfolio variance to match a target volatility level.
    Useful for risk parity or volatility targeting strategies.

    Example:
        >>> # Target 15% annual volatility
        >>> constraint = VolatilityTargetConstraint(target_volatility=0.15)
    """

    def __init__(self, target_volatility: float = 0.15, allow_lower: bool = True):
        """
        Initialize volatility target constraint.

        Args:
            target_volatility: Target annual volatility (0.15 = 15%)
            allow_lower: If True, allows volatility <= target
                        If False, requires volatility == target
        """
        self.target_volatility = target_volatility
        self.allow_lower = allow_lower

    def apply(self, weights, covariance_matrix: np.ndarray = None, **kwargs) -> List:
        """
        Apply volatility target constraint.

        Args:
            weights: CVXPY variable for portfolio weights
            covariance_matrix: Annualized covariance matrix (required!)
            **kwargs: Additional context

        Returns:
            List of cvxpy constraints

        Raises:
            ValueError: If covariance_matrix not provided
        """
        if not CVXPY_AVAILABLE:
            raise ImportError("cvxpy required for optimization constraints")

        if covariance_matrix is None:
            raise ValueError("VolatilityTargetConstraint requires covariance_matrix parameter")

        # Portfolio variance = w^T * Sigma * w
        portfolio_variance = cp.quad_form(weights, covariance_matrix)

        # Target variance
        target_variance = self.target_volatility ** 2

        if self.allow_lower:
            # Volatility <= target
            return [portfolio_variance <= target_variance]
        else:
            # Volatility == target (harder to satisfy)
            return [portfolio_variance == target_variance]

    def validate(
        self,
        weights: np.ndarray,
        covariance_matrix: np.ndarray = None,
        **kwargs
    ) -> bool:
        """Validate portfolio volatility matches target."""
        if covariance_matrix is None:
            return True  # Can't validate without covariance

        # Calculate portfolio variance
        portfolio_variance = weights @ covariance_matrix @ weights
        portfolio_volatility = np.sqrt(portfolio_variance)

        if self.allow_lower:
            return portfolio_volatility <= self.target_volatility + 1e-6
        else:
            return abs(portfolio_volatility - self.target_volatility) <= 1e-6

    def __repr__(self) -> str:
        operator = "<=" if self.allow_lower else "=="
        return f"VolatilityTargetConstraint(vol {operator} {self.target_volatility:.2%})"


class MaxDrawdownConstraint(PortfolioConstraint):
    """
    Limit expected maximum drawdown.

    Phase 2 Enhancement: Drawdown-aware portfolio construction.

    Note: Drawdown is a path-dependent metric, difficult to constrain
    directly in mean-variance optimization. This provides an approximation
    using volatility as a proxy.

    Example:
        >>> # Target max drawdown <= 20%
        >>> constraint = MaxDrawdownConstraint(max_drawdown=0.20)
    """

    def __init__(self, max_drawdown: float = 0.25):
        """
        Initialize max drawdown constraint.

        Args:
            max_drawdown: Maximum acceptable drawdown (0.25 = 25%)
        """
        self.max_drawdown = max_drawdown

    def apply(self, weights, covariance_matrix: np.ndarray = None, **kwargs) -> List:
        """
        Apply max drawdown constraint (via volatility proxy).

        Uses approximate relationship: Max DD ≈ 2 * volatility
        This is a rough heuristic, not exact.

        Args:
            weights: CVXPY variable for portfolio weights
            covariance_matrix: Annualized covariance matrix
            **kwargs: Additional context

        Returns:
            List of cvxpy constraints
        """
        if not CVXPY_AVAILABLE:
            raise ImportError("cvxpy required for optimization constraints")

        if covariance_matrix is None:
            # Can't apply without covariance - return empty
            return []

        # Approximate: Max DD ≈ 2 * volatility
        # So volatility <= max_drawdown / 2
        target_volatility = self.max_drawdown / 2.0

        # Portfolio variance
        portfolio_variance = cp.quad_form(weights, covariance_matrix)

        # Constrain variance
        return [portfolio_variance <= target_volatility ** 2]

    def validate(
        self,
        weights: np.ndarray,
        covariance_matrix: np.ndarray = None,
        **kwargs
    ) -> bool:
        """Validate using volatility proxy."""
        if covariance_matrix is None:
            return True

        portfolio_variance = weights @ covariance_matrix @ weights
        portfolio_volatility = np.sqrt(portfolio_variance)

        # Check if volatility suggests acceptable drawdown
        estimated_drawdown = portfolio_volatility * 2.0
        return estimated_drawdown <= self.max_drawdown + 0.05  # 5% tolerance

    def __repr__(self) -> str:
        return f"MaxDrawdownConstraint(max_drawdown={self.max_drawdown:.1%})"
