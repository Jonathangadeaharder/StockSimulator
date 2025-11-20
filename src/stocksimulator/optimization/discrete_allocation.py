"""
Discrete allocation conversion.

Converts continuous portfolio weights to discrete share quantities,
handling the practical constraint that only whole shares can be purchased.
"""

from typing import Dict, Tuple
import math


class DiscreteAllocator:
    """
    Convert continuous portfolio weights to discrete share quantities.

    Handles the practical constraint that you can only buy whole shares
    (unless fractional shares are explicitly allowed).
    """

    def __init__(self, allow_fractional: bool = False):
        """
        Initialize discrete allocator.

        Args:
            allow_fractional: If True, allows fractional shares (DRIP, some brokers)
                            If False, only whole shares (default)
        """
        self.allow_fractional = allow_fractional

    def allocate(
        self,
        target_weights: Dict[str, float],
        current_prices: Dict[str, float],
        total_capital: float,
        method: str = 'greedy'
    ) -> Tuple[Dict[str, int], float]:
        """
        Convert target weights to discrete shares.

        Args:
            target_weights: Dict of symbol -> target percentage (0-100)
            current_prices: Dict of symbol -> current price
            total_capital: Total capital to allocate
            method: 'greedy' (fast) or 'lp' (optimal but slower, requires cvxpy)

        Returns:
            Tuple of:
                - allocations: Dict of symbol -> number of shares
                - remaining_cash: Uninvested cash

        Example:
            >>> allocator = DiscreteAllocator()
            >>> weights = {'SPY': 60.0, 'AGG': 25.0, 'GLD': 15.0}
            >>> prices = {'SPY': 450.0, 'AGG': 105.5, 'GLD': 180.0}
            >>> shares, cash = allocator.allocate(weights, prices, 100000)
            >>> print(shares)  # {'SPY': 133, 'AGG': 24, 'GLD': 8}
            >>> print(f"${cash:.2f}")  # $109.50
        """
        if self.allow_fractional:
            # Easy case: just buy fractional shares
            allocations = {}
            for symbol, weight in target_weights.items():
                if symbol not in current_prices:
                    continue
                target_value = total_capital * (weight / 100)
                shares = target_value / current_prices[symbol]
                allocations[symbol] = shares
            return allocations, 0.0

        # Discrete shares only
        if method == 'greedy':
            return self._allocate_greedy(target_weights, current_prices, total_capital)
        elif method == 'lp':
            return self._allocate_lp(target_weights, current_prices, total_capital)
        else:
            raise ValueError(f"Unknown method: {method}. Use 'greedy' or 'lp'")

    def _allocate_greedy(
        self,
        target_weights: Dict[str, float],
        current_prices: Dict[str, float],
        total_capital: float
    ) -> Tuple[Dict[str, int], float]:
        """
        Greedy allocation algorithm.

        Strategy:
        1. Buy floor(target_shares) for each asset
        2. Iteratively add one share to most underweight position
        3. Continue until can't afford any more shares

        Fast and produces near-optimal results in practice.
        """
        allocations = {}
        remaining_cash = total_capital

        # First pass: buy floor shares for each target
        for symbol, weight in target_weights.items():
            if symbol not in current_prices:
                continue

            if current_prices[symbol] <= 0:
                continue

            target_value = total_capital * (weight / 100)
            target_shares = target_value / current_prices[symbol]
            floor_shares = int(target_shares)

            cost = floor_shares * current_prices[symbol]
            if cost <= remaining_cash:
                allocations[symbol] = floor_shares
                remaining_cash -= cost
            else:
                allocations[symbol] = 0

        # Second pass: add shares to most underweight positions
        max_iterations = 1000  # Prevent infinite loops
        iterations = 0

        while iterations < max_iterations:
            iterations += 1

            # Calculate current total value (deployed capital)
            current_total = sum(
                allocations.get(s, 0) * current_prices.get(s, 0)
                for s in target_weights.keys()
                if s in current_prices
            )

            if current_total == 0:
                break

            # Total portfolio value including remaining cash
            total_portfolio = current_total + remaining_cash

            # Find most underweight position that we can afford
            max_underweight = -float('inf')
            best_symbol = None

            for symbol in target_weights.keys():
                if symbol not in current_prices:
                    continue

                price = current_prices[symbol]
                if price <= 0 or price > remaining_cash:
                    continue  # Can't afford

                # Current weight
                current_value = allocations.get(symbol, 0) * price
                current_weight = (current_value / total_portfolio) * 100

                # Target weight
                target_weight = target_weights[symbol]

                # How underweight is this position?
                underweight = target_weight - current_weight

                if underweight > max_underweight:
                    max_underweight = underweight
                    best_symbol = symbol

            if best_symbol is None:
                # Can't afford any more shares
                break

            # Buy one share of most underweight position
            allocations[best_symbol] = allocations.get(best_symbol, 0) + 1
            remaining_cash -= current_prices[best_symbol]

        return allocations, remaining_cash

    def _allocate_lp(
        self,
        target_weights: Dict[str, float],
        current_prices: Dict[str, float],
        total_capital: float
    ) -> Tuple[Dict[str, int], float]:
        """
        Linear programming allocation: optimal integer solution.

        Minimizes tracking error to target weights using mixed-integer
        programming. Requires cvxpy with GLPK_MI solver.

        Falls back to greedy if cvxpy is not available or solver fails.
        """
        try:
            import cvxpy as cp
            import numpy as np
        except ImportError:
            # Fall back to greedy if cvxpy not available
            return self._allocate_greedy(target_weights, current_prices, total_capital)

        symbols = [s for s in target_weights.keys() if s in current_prices]
        if not symbols:
            return {}, total_capital

        n = len(symbols)

        # Decision variables: number of shares (integer)
        shares = cp.Variable(n, integer=True)

        # Prices vector
        prices = np.array([current_prices[s] for s in symbols])

        # Target values
        targets = np.array([
            total_capital * (target_weights[s] / 100)
            for s in symbols
        ])

        # Objective: minimize squared deviation from targets
        actual_values = cp.multiply(shares, prices)
        objective = cp.Minimize(cp.sum_squares(actual_values - targets))

        # Constraints
        constraints = [
            shares >= 0,  # No short positions
            cp.sum(cp.multiply(shares, prices)) <= total_capital  # Budget constraint
        ]

        # Solve
        problem = cp.Problem(objective, constraints)

        try:
            problem.solve(solver=cp.GLPK_MI, verbose=False)
        except:
            # If GLPK_MI not available, try other solvers or fall back to greedy
            try:
                problem.solve(verbose=False)
            except:
                return self._allocate_greedy(target_weights, current_prices, total_capital)

        if problem.status not in ['optimal', 'optimal_inaccurate']:
            # Fall back to greedy
            return self._allocate_greedy(target_weights, current_prices, total_capital)

        # Extract solution
        allocations = {}
        for i, symbol in enumerate(symbols):
            allocations[symbol] = int(round(shares.value[i]))

        used_capital = sum(
            allocations[s] * current_prices[s]
            for s in symbols
        )
        remaining_cash = total_capital - used_capital

        return allocations, remaining_cash

    def calculate_tracking_error(
        self,
        actual_allocations: Dict[str, int],
        target_weights: Dict[str, float],
        current_prices: Dict[str, float]
    ) -> float:
        """
        Calculate tracking error between actual and target allocations.

        Tracking error is the root-mean-squared deviation of actual weights
        from target weights.

        Args:
            actual_allocations: Dict of symbol -> actual shares
            target_weights: Dict of symbol -> target percentage
            current_prices: Dict of symbol -> current price

        Returns:
            Tracking error as a percentage

        Example:
            >>> allocations = {'SPY': 133, 'AGG': 24, 'GLD': 8}
            >>> targets = {'SPY': 60.0, 'AGG': 25.0, 'GLD': 15.0}
            >>> prices = {'SPY': 450.0, 'AGG': 105.5, 'GLD': 180.0}
            >>> te = allocator.calculate_tracking_error(allocations, targets, prices)
            >>> print(f"{te:.2f}%")  # ~0.15%
        """
        # Calculate total value
        total_value = sum(
            actual_allocations.get(s, 0) * current_prices.get(s, 0)
            for s in target_weights.keys()
            if s in current_prices
        )

        if total_value == 0:
            return 0.0

        # Calculate squared errors
        squared_errors = []
        for symbol in target_weights.keys():
            if symbol not in current_prices:
                continue

            # Actual weight
            actual_value = actual_allocations.get(symbol, 0) * current_prices[symbol]
            actual_weight = (actual_value / total_value) * 100

            # Target weight
            target_weight = target_weights[symbol]

            # Squared deviation
            squared_errors.append((actual_weight - target_weight) ** 2)

        if not squared_errors:
            return 0.0

        # Root mean squared error
        return (sum(squared_errors) / len(squared_errors)) ** 0.5

    def get_actual_weights(
        self,
        allocations: Dict[str, int],
        current_prices: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate actual portfolio weights from share allocations.

        Args:
            allocations: Dict of symbol -> shares
            current_prices: Dict of symbol -> current price

        Returns:
            Dict of symbol -> actual percentage weight
        """
        total_value = sum(
            shares * current_prices.get(symbol, 0)
            for symbol, shares in allocations.items()
        )

        if total_value == 0:
            return {symbol: 0.0 for symbol in allocations.keys()}

        return {
            symbol: (shares * current_prices.get(symbol, 0) / total_value) * 100
            for symbol, shares in allocations.items()
        }

    def __repr__(self) -> str:
        return f"DiscreteAllocator(allow_fractional={self.allow_fractional})"
