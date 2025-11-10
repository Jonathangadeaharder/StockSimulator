"""
Strategy Parameter Optimization

Grid search and optimization tools for finding optimal strategy parameters.
"""

from typing import Dict, List, Any, Callable, Optional, Tuple
from datetime import date
import itertools

from stocksimulator.core.backtester import Backtester, BacktestResult
from stocksimulator.models.market_data import MarketData


class OptimizationResult:
    """Result from parameter optimization."""

    def __init__(
        self,
        parameters: Dict[str, Any],
        metric_value: float,
        backtest_result: BacktestResult
    ):
        """
        Initialize optimization result.

        Args:
            parameters: Parameter values used
            metric_value: Optimization metric value
            backtest_result: Full backtest result
        """
        self.parameters = parameters
        self.metric_value = metric_value
        self.backtest_result = backtest_result

    def __repr__(self) -> str:
        return f"OptimizationResult(metric={self.metric_value:.3f}, params={self.parameters})"


class StrategyOptimizer:
    """
    Base class for strategy parameter optimization.
    """

    def __init__(
        self,
        backtester: Optional[Backtester] = None,
        optimization_metric: str = 'sharpe_ratio'
    ):
        """
        Initialize optimizer.

        Args:
            backtester: Backtester instance (creates default if None)
            optimization_metric: Metric to optimize ('sharpe_ratio', 'annualized_return', etc.)
        """
        self.backtester = backtester or Backtester(initial_cash=100000.0)
        self.optimization_metric = optimization_metric

    def evaluate_parameters(
        self,
        strategy_class: type,
        parameters: Dict[str, Any],
        market_data: Dict[str, MarketData],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> OptimizationResult:
        """
        Evaluate a single parameter combination.

        Args:
            strategy_class: Strategy class to instantiate
            parameters: Parameter values
            market_data: Market data
            start_date: Backtest start date
            end_date: Backtest end date

        Returns:
            OptimizationResult
        """
        # Instantiate strategy with parameters
        strategy = strategy_class(**parameters)

        # Run backtest
        result = self.backtester.run_backtest(
            strategy_name=f"{strategy_class.__name__}_{parameters}",
            market_data=market_data,
            strategy_func=strategy,
            start_date=start_date,
            end_date=end_date
        )

        # Extract metric
        summary = result.get_performance_summary()
        metric_value = summary.get(self.optimization_metric, 0.0)

        return OptimizationResult(parameters, metric_value, result)


class GridSearchOptimizer(StrategyOptimizer):
    """
    Grid search optimization over parameter space.

    Tests all combinations of parameters to find optimal values.
    """

    def optimize(
        self,
        strategy_class: type,
        param_grid: Dict[str, List[Any]],
        market_data: Dict[str, MarketData],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        top_n: int = 5
    ) -> List[OptimizationResult]:
        """
        Perform grid search optimization.

        Args:
            strategy_class: Strategy class to optimize
            param_grid: Dictionary of parameter_name -> list of values to try
            market_data: Market data
            start_date: Backtest start date
            end_date: Backtest end date
            top_n: Number of top results to return

        Returns:
            List of top N optimization results

        Example:
            >>> optimizer = GridSearchOptimizer()
            >>> param_grid = {
            ...     'lookback_days': [60, 126, 252],
            ...     'top_n': [1, 2, 3],
            ...     'equal_weight': [True, False]
            ... }
            >>> results = optimizer.optimize(MomentumStrategy, param_grid, market_data)
            >>> best = results[0]
            >>> print(f"Best params: {best.parameters}, Sharpe: {best.metric_value:.3f}")
        """
        print(f"Starting grid search optimization...")
        print(f"  Strategy: {strategy_class.__name__}")
        print(f"  Parameters: {list(param_grid.keys())}")
        print(f"  Combinations: {self._count_combinations(param_grid)}")
        print(f"  Optimizing for: {self.optimization_metric}")
        print()

        # Generate all parameter combinations
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        combinations = list(itertools.product(*param_values))

        results = []
        total = len(combinations)

        for i, combination in enumerate(combinations, 1):
            # Create parameter dict
            params = dict(zip(param_names, combination))

            # Evaluate
            try:
                result = self.evaluate_parameters(
                    strategy_class,
                    params,
                    market_data,
                    start_date,
                    end_date
                )
                results.append(result)

                print(f"  [{i}/{total}] {params} → {self.optimization_metric}={result.metric_value:.3f}")

            except Exception as e:
                print(f"  [{i}/{total}] {params} → ERROR: {e}")

        # Sort by metric value (descending)
        results.sort(key=lambda r: r.metric_value, reverse=True)

        print()
        print("=" * 80)
        print(f"OPTIMIZATION COMPLETE - Top {min(top_n, len(results))} Results")
        print("=" * 80)

        for i, result in enumerate(results[:top_n], 1):
            print(f"\n{i}. {self.optimization_metric.upper()}: {result.metric_value:.3f}")
            print(f"   Parameters: {result.parameters}")

            summary = result.backtest_result.get_performance_summary()
            print(f"   Return: {summary['annualized_return']:.2f}%")
            print(f"   Max DD: {summary['max_drawdown']:.2f}%")

        return results[:top_n]

    def _count_combinations(self, param_grid: Dict[str, List[Any]]) -> int:
        """Count total number of parameter combinations."""
        count = 1
        for values in param_grid.values():
            count *= len(values)
        return count


