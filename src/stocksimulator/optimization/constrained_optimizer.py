"""
Constrained portfolio optimization.

Phase 2 Enhancement: Portfolio optimizer with flexible constraint system.
"""

from typing import List, Dict, Optional
import numpy as np

# Try to import cvxpy
try:
    import cvxpy as cp
    CVXPY_AVAILABLE = True
except ImportError:
    CVXPY_AVAILABLE = False

from stocksimulator.constraints import PortfolioConstraint


class ConstrainedOptimizer:
    """
    Portfolio optimizer with flexible constraint system.

    Phase 2 Enhancement: Inspired by Riskfolio-Lib's constraint handling.

    Optimizes portfolio weights while respecting multiple constraints.
    Constraints can limit leverage, sector exposure, turnover, volatility,
    and more.

    Example:
        >>> from stocksimulator.constraints import (
        ...     LongOnlyConstraint,
        ...     Turnover

Constraint,
        ...     VolatilityTargetConstraint
        ... )
        >>>
        >>> constraints = [
        ...     LongOnlyConstraint(),
        ...     TurnoverConstraint(max_turnover=0.15),
        ...     VolatilityTargetConstraint(target_volatility=0.12)
        ... ]
        >>>
        >>> optimizer = ConstrainedOptimizer(constraints=constraints)
        >>> optimal_weights = optimizer.optimize_sharpe_ratio(
        ...     expected_returns=expected_returns,
        ...     covariance_matrix=cov_matrix,
        ...     symbols=symbols,
        ...     current_weights=current_weights
        ... )
    """

    def __init__(
        self,
        constraints: Optional[List[PortfolioConstraint]] = None
    ):
        """
        Initialize constrained optimizer.

        Args:
            constraints: List of constraint objects to apply
                        If None, uses default (long-only, full investment)
        """
        if not CVXPY_AVAILABLE:
            raise ImportError(
                "cvxpy is required for constrained optimization. "
                "Install with: pip install cvxpy"
            )

        if constraints is None:
            # Default: long-only, fully invested
            from stocksimulator.constraints import (
                LongOnlyConstraint,
                FullInvestmentConstraint
            )
            constraints = [
                LongOnlyConstraint(),
                FullInvestmentConstraint()
            ]

        self.constraints = constraints

    def optimize_sharpe_ratio(
        self,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        symbols: List[str],
        current_weights: Optional[np.ndarray] = None,
        risk_free_rate: float = 0.02,
        risk_aversion: float = 1.0
    ) -> np.ndarray:
        """
        Optimize portfolio for maximum Sharpe ratio with constraints.

        Args:
            expected_returns: Expected annual return for each asset
            covariance_matrix: Annualized asset covariance matrix
            symbols: Asset symbols (for sector constraints)
            current_weights: Current portfolio weights (for turnover constraint)
            risk_free_rate: Annual risk-free rate
            risk_aversion: Risk aversion parameter for optimization

        Returns:
            Optimal weights (numpy array)

        Raises:
            ValueError: If optimization fails
        """
        n_assets = len(expected_returns)

        # Decision variable: portfolio weights
        weights = cp.Variable(n_assets)

        # Objective: Maximize risk-adjusted return
        # Using: maximize return - risk_aversion * variance
        # (Equivalent to maximizing Sharpe ratio for appropriate risk_aversion)
        portfolio_return = expected_returns @ weights
        portfolio_variance = cp.quad_form(weights, covariance_matrix)

        objective = cp.Maximize(
            portfolio_return - risk_aversion * portfolio_variance
        )

        # Apply all constraints
        constraint_list = []

        for constraint in self.constraints:
            try:
                constraint_cvxpy = constraint.apply(
                    weights,
                    covariance_matrix=covariance_matrix,
                    symbols=symbols,
                    current_weights=current_weights if current_weights is not None
                                   else np.zeros(n_assets)
                )
                constraint_list.extend(constraint_cvxpy)
            except Exception as e:
                print(f"Warning: Failed to apply {constraint}: {e}")

        # Solve optimization problem
        problem = cp.Problem(objective, constraint_list)

        try:
            problem.solve(solver=cp.ECOS, verbose=False)
        except:
            # Try alternative solver
            try:
                problem.solve(solver=cp.SCS, verbose=False)
            except:
                try:
                    problem.solve(verbose=False)  # Default solver
                except:
                    raise ValueError("Optimization failed with all solvers")

        if problem.status not in ['optimal', 'optimal_inaccurate']:
            raise ValueError(f"Optimization failed: {problem.status}")

        # Extract solution
        optimal_weights = weights.value

        if optimal_weights is None:
            raise ValueError("Optimization returned None")

        # Post-process: handle minimum position size if applicable
        for constraint in self.constraints:
            if hasattr(constraint, 'enforce_post_optimization'):
                optimal_weights = constraint.enforce_post_optimization(optimal_weights)

        return optimal_weights

    def optimize_minimum_volatility(
        self,
        covariance_matrix: np.ndarray,
        symbols: List[str],
        current_weights: Optional[np.ndarray] = None,
        target_return: Optional[float] = None
    ) -> np.ndarray:
        """
        Optimize for minimum volatility with constraints.

        Args:
            covariance_matrix: Annualized asset covariance matrix
            symbols: Asset symbols
            current_weights: Current portfolio weights
            target_return: Optional minimum target return

        Returns:
            Optimal weights (numpy array)
        """
        n_assets = covariance_matrix.shape[0]

        # Decision variable
        weights = cp.Variable(n_assets)

        # Objective: Minimize variance
        portfolio_variance = cp.quad_form(weights, covariance_matrix)
        objective = cp.Minimize(portfolio_variance)

        # Apply constraints
        constraint_list = []

        # Add target return constraint if specified
        if target_return is not None:
            # Approximate expected returns (equal for minimum variance)
            expected_returns = np.ones(n_assets) * target_return
            constraint_list.append(expected_returns @ weights >= target_return)

        for constraint in self.constraints:
            try:
                constraint_cvxpy = constraint.apply(
                    weights,
                    covariance_matrix=covariance_matrix,
                    symbols=symbols,
                    current_weights=current_weights if current_weights is not None
                                   else np.zeros(n_assets)
                )
                constraint_list.extend(constraint_cvxpy)
            except Exception as e:
                print(f"Warning: Failed to apply {constraint}: {e}")

        # Solve
        problem = cp.Problem(objective, constraint_list)

        try:
            problem.solve(verbose=False)
        except:
            raise ValueError("Optimization failed")

        if problem.status not in ['optimal', 'optimal_inaccurate']:
            raise ValueError(f"Optimization failed: {problem.status}")

        return weights.value

    def validate_weights(
        self,
        weights: np.ndarray,
        symbols: List[str],
        covariance_matrix: Optional[np.ndarray] = None,
        current_weights: Optional[np.ndarray] = None
    ) -> Dict[str, bool]:
        """
        Validate that weights satisfy all constraints.

        Args:
            weights: Portfolio weights to validate
            symbols: Asset symbols
            covariance_matrix: Optional covariance matrix
            current_weights: Optional current weights

        Returns:
            Dict mapping constraint name -> validation result (bool)
        """
        results = {}

        for constraint in self.constraints:
            try:
                is_valid = constraint.validate(
                    weights=weights,
                    symbols=symbols,
                    covariance_matrix=covariance_matrix,
                    current_weights=current_weights
                )
                results[str(constraint)] = is_valid
            except Exception as e:
                results[str(constraint)] = False
                print(f"Validation error for {constraint}: {e}")

        return results

    def __repr__(self) -> str:
        return f"ConstrainedOptimizer(constraints={len(self.constraints)})"
