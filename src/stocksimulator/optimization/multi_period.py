"""
Multi-Period Portfolio Optimization

Optimizes portfolio allocation considering future rebalancing decisions
and transaction costs. Unlike single-period optimization, multi-period
optimization accounts for the fact that today's allocation affects
future rebalancing costs.

Reference:
CVXPortfolio framework and model predictive control for portfolio management.
"""

import cvxpy as cp
import numpy as np
from typing import Dict, Optional, List
from enum import Enum


class ObjectiveType(Enum):
    """Type of optimization objective."""
    SHARPE = "sharpe"  # Maximize risk-adjusted return
    RETURN = "return"  # Maximize expected return
    RISK = "risk"  # Minimize risk
    UTILITY = "utility"  # Maximize utility (return - risk_aversion * risk)


class MultiPeriodOptimizer:
    """
    Multi-period portfolio optimization considering future rebalancing costs.

    Uses model predictive control (MPC) approach:
    1. Optimize over T future periods
    2. Execute only the first period's allocation
    3. Re-optimize at next period with updated information

    Benefits:
    - Reduces turnover by anticipating future rebalancing
    - Accounts for transaction costs in allocation decisions
    - More realistic than myopic single-period optimization
    """

    def __init__(
        self,
        forecast_horizon: int = 5,
        risk_aversion: float = 1.0,
        transaction_cost_bps: float = 2.0,
        solver: str = 'ECOS'
    ):
        """
        Initialize multi-period optimizer.

        Args:
            forecast_horizon: Number of periods to look ahead
            risk_aversion: Risk aversion parameter (higher = more conservative)
            transaction_cost_bps: Transaction cost in basis points (per trade)
            solver: CVXPY solver to use ('ECOS', 'SCS', 'OSQP')
        """
        self.T = forecast_horizon
        self.gamma = risk_aversion
        self.tc_bps = transaction_cost_bps
        self.solver = solver

    def optimize(
        self,
        current_weights: np.ndarray,
        expected_returns: np.ndarray,  # Shape: (T, n_assets) or (n_assets,)
        covariance_matrix: np.ndarray,  # Shape: (n_assets, n_assets)
        constraints: Optional[List] = None,
        objective_type: ObjectiveType = ObjectiveType.UTILITY
    ) -> np.ndarray:
        """
        Optimize portfolio allocation over multiple periods.

        Args:
            current_weights: Current portfolio weights (sums to 1)
            expected_returns: Expected returns for each period and asset
                Can be 1D (same for all periods) or 2D (different per period)
            covariance_matrix: Covariance matrix of returns
            constraints: Additional CVXPY constraints
            objective_type: Type of objective to optimize

        Returns:
            Optimal weights for current period (first period of horizon)

        Example:
            >>> optimizer = MultiPeriodOptimizer(forecast_horizon=5, risk_aversion=2.0)
            >>> current_w = np.array([0.6, 0.4])  # 60/40 portfolio
            >>> expected_r = np.array([0.08, 0.03])  # Annual returns
            >>> cov = np.array([[0.04, 0.01], [0.01, 0.02]])
            >>> optimal_w = optimizer.optimize(current_w, expected_r, cov)
        """
        n_assets = len(current_weights)

        # Handle both 1D and 2D expected returns
        if expected_returns.ndim == 1:
            # Same expected returns for all periods
            expected_returns = np.tile(expected_returns, (self.T, 1))
        elif expected_returns.shape[0] != self.T:
            raise ValueError(f"Expected returns must have {self.T} periods")

        # Decision variables: weights for each period
        w = cp.Variable((self.T, n_assets))

        # Build objective based on type
        if objective_type == ObjectiveType.UTILITY:
            objective = self._build_utility_objective(
                w, expected_returns, covariance_matrix, current_weights
            )
        elif objective_type == ObjectiveType.RETURN:
            objective = self._build_return_objective(
                w, expected_returns, current_weights
            )
        elif objective_type == ObjectiveType.RISK:
            objective = self._build_risk_objective(
                w, covariance_matrix, current_weights
            )
        elif objective_type == ObjectiveType.SHARPE:
            # Sharpe ratio optimization is non-convex in multi-period case
            # Fall back to utility maximization
            objective = self._build_utility_objective(
                w, expected_returns, covariance_matrix, current_weights
            )
        else:
            raise ValueError(f"Unknown objective type: {objective_type}")

        # Build constraints
        constraints_list = self._build_standard_constraints(w)

        # Add custom constraints if provided
        if constraints:
            constraints_list.extend(constraints)

        # Solve optimization problem
        problem = cp.Problem(objective, constraints_list)

        try:
            problem.solve(solver=self.solver)
        except cp.error.SolverError:
            # Try alternative solver if primary fails
            try:
                problem.solve(solver='SCS')
            except:
                # Last resort: use ECOS
                problem.solve(solver='ECOS')

        if problem.status not in ['optimal', 'optimal_inaccurate']:
            raise ValueError(f"Optimization failed with status: {problem.status}")

        # Return optimal weights for first period only
        # (Model Predictive Control: re-optimize next period)
        return w[0].value

    def _build_utility_objective(
        self,
        w: cp.Variable,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        current_weights: np.ndarray
    ) -> cp.Maximize:
        """Build utility maximization objective: E[R] - gamma * Var[R] - TC."""

        # Expected return across all periods
        total_return = cp.sum([
            expected_returns[t] @ w[t] for t in range(self.T)
        ])

        # Risk (variance) across all periods
        total_risk = cp.sum([
            cp.quad_form(w[t], covariance_matrix) for t in range(self.T)
        ])

        # Transaction costs
        transaction_costs = self._compute_transaction_costs(w, current_weights)

        # Utility = Return - RiskAversion * Risk - TransactionCosts
        utility = total_return - self.gamma * total_risk - transaction_costs

        return cp.Maximize(utility)

    def _build_return_objective(
        self,
        w: cp.Variable,
        expected_returns: np.ndarray,
        current_weights: np.ndarray
    ) -> cp.Maximize:
        """Build return maximization objective (with transaction costs)."""

        total_return = cp.sum([
            expected_returns[t] @ w[t] for t in range(self.T)
        ])

        transaction_costs = self._compute_transaction_costs(w, current_weights)

        return cp.Maximize(total_return - transaction_costs)

    def _build_risk_objective(
        self,
        w: cp.Variable,
        covariance_matrix: np.ndarray,
        current_weights: np.ndarray
    ) -> cp.Minimize:
        """Build risk minimization objective (with transaction costs)."""

        total_risk = cp.sum([
            cp.quad_form(w[t], covariance_matrix) for t in range(self.T)
        ])

        transaction_costs = self._compute_transaction_costs(w, current_weights)

        # Minimize risk + transaction costs (converted to risk units)
        return cp.Minimize(total_risk + transaction_costs / self.gamma)

    def _compute_transaction_costs(
        self,
        w: cp.Variable,
        current_weights: np.ndarray
    ) -> cp.Expression:
        """
        Compute transaction costs across all periods.

        Cost = sum of absolute changes in weights * transaction cost rate
        """
        transaction_costs = 0

        for t in range(self.T):
            if t == 0:
                # Cost from current weights to first period
                trades = cp.abs(w[0] - current_weights)
            else:
                # Cost between periods
                trades = cp.abs(w[t] - w[t-1])

            # Convert basis points to decimal
            transaction_costs += cp.sum(trades) * (self.tc_bps / 10000)

        return transaction_costs

    def _build_standard_constraints(self, w: cp.Variable) -> List:
        """Build standard portfolio constraints for all periods."""
        constraints = []

        for t in range(self.T):
            # Weights sum to 1 (fully invested)
            constraints.append(cp.sum(w[t]) == 1)

            # Long-only (no short selling)
            constraints.append(w[t] >= 0)

        return constraints


class AdaptiveMultiPeriodOptimizer(MultiPeriodOptimizer):
    """
    Adaptive multi-period optimizer with time-varying parameters.

    Allows different expected returns and risk aversion for each period,
    enabling more sophisticated scenarios like:
    - Declining expected returns over time
    - Increasing risk aversion near retirement
    - Time-varying transaction costs
    """

    def optimize_adaptive(
        self,
        current_weights: np.ndarray,
        expected_returns: np.ndarray,  # Shape: (T, n_assets)
        covariance_matrices: np.ndarray,  # Shape: (T, n_assets, n_assets)
        risk_aversion_schedule: Optional[np.ndarray] = None,  # Shape: (T,)
        constraints: Optional[List] = None
    ) -> np.ndarray:
        """
        Optimize with time-varying parameters.

        Args:
            current_weights: Current portfolio weights
            expected_returns: Expected returns for each period (T x n_assets)
            covariance_matrices: Covariance matrix for each period (T x n x n)
            risk_aversion_schedule: Risk aversion for each period (optional)
            constraints: Additional constraints

        Returns:
            Optimal weights for current period
        """
        n_assets = len(current_weights)

        if expected_returns.shape[0] != self.T:
            raise ValueError(f"Expected returns must have {self.T} periods")

        if covariance_matrices.shape[0] != self.T:
            raise ValueError(f"Covariance matrices must have {self.T} periods")

        if risk_aversion_schedule is None:
            risk_aversion_schedule = np.full(self.T, self.gamma)
        elif len(risk_aversion_schedule) != self.T:
            raise ValueError(f"Risk aversion schedule must have {self.T} periods")

        # Decision variables
        w = cp.Variable((self.T, n_assets))

        # Build time-varying objective
        total_utility = 0
        for t in range(self.T):
            period_return = expected_returns[t] @ w[t]
            period_risk = cp.quad_form(w[t], covariance_matrices[t])
            total_utility += period_return - risk_aversion_schedule[t] * period_risk

        # Transaction costs
        transaction_costs = self._compute_transaction_costs(w, current_weights)

        objective = cp.Maximize(total_utility - transaction_costs)

        # Constraints
        constraints_list = self._build_standard_constraints(w)
        if constraints:
            constraints_list.extend(constraints)

        # Solve
        problem = cp.Problem(objective, constraints_list)

        try:
            problem.solve(solver=self.solver)
        except cp.error.SolverError:
            problem.solve(solver='SCS')

        if problem.status not in ['optimal', 'optimal_inaccurate']:
            raise ValueError(f"Optimization failed with status: {problem.status}")

        return w[0].value


def compare_single_vs_multi_period(
    current_weights: np.ndarray,
    expected_returns: np.ndarray,
    covariance_matrix: np.ndarray,
    transaction_cost_bps: float = 2.0,
    horizon: int = 5
) -> Dict:
    """
    Compare single-period vs multi-period optimization.

    Useful for understanding the impact of multi-period planning.

    Args:
        current_weights: Current portfolio weights
        expected_returns: Expected returns
        covariance_matrix: Covariance matrix
        transaction_cost_bps: Transaction costs
        horizon: Planning horizon

    Returns:
        Dictionary with comparison results

    Example:
        >>> comparison = compare_single_vs_multi_period(
        ...     current_weights=np.array([0.6, 0.4]),
        ...     expected_returns=np.array([0.08, 0.03]),
        ...     covariance_matrix=cov_matrix
        ... )
        >>> print(f"Turnover reduction: {comparison['turnover_reduction']:.1%}")
    """
    # Single-period optimization (myopic)
    n_assets = len(current_weights)
    w_single = cp.Variable(n_assets)

    ret_single = expected_returns @ w_single
    risk_single = cp.quad_form(w_single, covariance_matrix)
    tc_single = cp.sum(cp.abs(w_single - current_weights)) * (transaction_cost_bps / 10000)

    obj_single = cp.Maximize(ret_single - risk_single - tc_single)
    constraints_single = [cp.sum(w_single) == 1, w_single >= 0]

    prob_single = cp.Problem(obj_single, constraints_single)
    prob_single.solve()

    # Multi-period optimization
    optimizer_multi = MultiPeriodOptimizer(
        forecast_horizon=horizon,
        risk_aversion=1.0,
        transaction_cost_bps=transaction_cost_bps
    )
    w_multi = optimizer_multi.optimize(
        current_weights, expected_returns, covariance_matrix
    )

    # Calculate turnover
    turnover_single = np.sum(np.abs(w_single.value - current_weights))
    turnover_multi = np.sum(np.abs(w_multi - current_weights))

    return {
        'single_period_weights': w_single.value,
        'multi_period_weights': w_multi,
        'turnover_single': turnover_single,
        'turnover_multi': turnover_multi,
        'turnover_reduction': (turnover_single - turnover_multi) / turnover_single,
        'tc_saved_bps': (turnover_single - turnover_multi) * transaction_cost_bps
    }
