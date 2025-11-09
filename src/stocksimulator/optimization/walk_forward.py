"""
Walk-Forward Analysis

Out-of-sample testing to avoid overfitting.
"""

from typing import Dict, List, Any, Optional
from datetime import date, timedelta
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from stocksimulator.core.backtester import Backtester
from stocksimulator.models.market_data import MarketData
from stocksimulator.optimization.optimizer import GridSearchOptimizer


class WalkForwardResult:
    """Result from walk-forward analysis."""

    def __init__(self, train_results: List, test_results: List):
        """
        Initialize walk-forward result.

        Args:
            train_results: Results from training periods
            test_results: Results from testing periods
        """
        self.train_results = train_results
        self.test_results = test_results

    def get_summary(self) -> Dict:
        """Get summary statistics."""
        if not self.test_results:
            return {}

        test_metrics = [r['summary'] for r in self.test_results]

        avg_return = sum(m['annualized_return'] for m in test_metrics) / len(test_metrics)
        avg_sharpe = sum(m['sharpe_ratio'] for m in test_metrics) / len(test_metrics)
        avg_dd = sum(m['max_drawdown'] for m in test_metrics) / len(test_metrics)

        return {
            'num_periods': len(self.test_results),
            'avg_return': avg_return,
            'avg_sharpe': avg_sharpe,
            'avg_max_drawdown': avg_dd,
            'test_results': test_metrics
        }


class WalkForwardAnalyzer:
    """
    Walk-Forward Analysis.

    Trains on one period, tests on next period, walks forward through time.
    Prevents overfitting by using out-of-sample testing.
    """

    def __init__(self, backtester: Optional[Backtester] = None):
        """
        Initialize walk-forward analyzer.

        Args:
            backtester: Backtester instance
        """
        self.backtester = backtester or Backtester(initial_cash=100000.0)

    def analyze(
        self,
        strategy_class: type,
        param_grid: Dict[str, List[Any]],
        market_data: Dict[str, MarketData],
        train_days: int = 756,  # ~3 years
        test_days: int = 252,   # ~1 year
        step_days: int = 63     # ~3 months
    ) -> WalkForwardResult:
        """
        Perform walk-forward analysis.

        Process:
        1. Train on first train_days to find optimal parameters
        2. Test on next test_days with those parameters
        3. Step forward by step_days and repeat

        Args:
            strategy_class: Strategy class to analyze
            param_grid: Parameter grid for optimization
            market_data: Market data
            train_days: Training period length
            test_days: Testing period length
            step_days: Step size between periods

        Returns:
            WalkForwardResult

        Example:
            >>> analyzer = WalkForwardAnalyzer()
            >>> param_grid = {'lookback_days': [60, 126, 252]}
            >>> result = analyzer.analyze(
            ...     MomentumStrategy,
            ...     param_grid,
            ...     market_data,
            ...     train_days=756,  # 3 years training
            ...     test_days=252     # 1 year testing
            ... )
            >>> summary = result.get_summary()
            >>> print(f"Avg Out-of-Sample Sharpe: {summary['avg_sharpe']:.3f}")
        """
        print("=" * 80)
        print("WALK-FORWARD ANALYSIS")
        print("=" * 80)
        print(f"Strategy: {strategy_class.__name__}")
        print(f"Train period: {train_days} days (~{train_days/252:.1f} years)")
        print(f"Test period: {test_days} days (~{test_days/252:.1f} years)")
        print(f"Step size: {step_days} days")
        print()

        # Get all dates from first symbol
        first_symbol = list(market_data.keys())[0]
        all_dates = sorted([d.date for d in market_data[first_symbol].data])

        train_results = []
        test_results = []

        period_num = 0
        current_idx = 0

        while current_idx + train_days + test_days < len(all_dates):
            period_num += 1

            # Define train and test periods
            train_start = all_dates[current_idx]
            train_end = all_dates[min(current_idx + train_days, len(all_dates) - 1)]
            test_start = all_dates[min(current_idx + train_days, len(all_dates) - 1)]
            test_end = all_dates[min(current_idx + train_days + test_days, len(all_dates) - 1)]

            print(f"Period {period_num}:")
            print(f"  Train: {train_start} to {train_end}")
            print(f"  Test:  {test_start} to {test_end}")

            # Optimize on training period
            optimizer = GridSearchOptimizer(
                backtester=self.backtester,
                optimization_metric='sharpe_ratio'
            )

            try:
                train_results_list = optimizer.optimize(
                    strategy_class=strategy_class,
                    param_grid=param_grid,
                    market_data=market_data,
                    start_date=train_start,
                    end_date=train_end,
                    top_n=1
                )

                if not train_results_list:
                    print("  No valid results in training period, skipping...")
                    current_idx += step_days
                    continue

                best_params = train_results_list[0].parameters
                train_metric = train_results_list[0].metric_value

                print(f"  Best params: {best_params} (Sharpe: {train_metric:.3f})")

                # Test on out-of-sample period
                test_result = optimizer.evaluate_parameters(
                    strategy_class=strategy_class,
                    parameters=best_params,
                    market_data=market_data,
                    start_date=test_start,
                    end_date=test_end
                )

                test_summary = test_result.backtest_result.get_performance_summary()

                print(f"  Out-of-sample: Sharpe={test_summary['sharpe_ratio']:.3f}, "
                      f"Return={test_summary['annualized_return']:.2f}%")
                print()

                train_results.append({
                    'period': period_num,
                    'start': train_start,
                    'end': train_end,
                    'parameters': best_params,
                    'sharpe': train_metric
                })

                test_results.append({
                    'period': period_num,
                    'start': test_start,
                    'end': test_end,
                    'parameters': best_params,
                    'summary': test_summary
                })

            except Exception as e:
                print(f"  Error in period {period_num}: {e}")

            # Step forward
            current_idx += step_days

        print("=" * 80)
        print("WALK-FORWARD SUMMARY")
        print("=" * 80)

        result = WalkForwardResult(train_results, test_results)
        summary = result.get_summary()

        if summary:
            print(f"Number of periods: {summary['num_periods']}")
            print(f"Average out-of-sample return: {summary['avg_return']:.2f}%")
            print(f"Average out-of-sample Sharpe: {summary['avg_sharpe']:.3f}")
            print(f"Average max drawdown: {summary['avg_max_drawdown']:.2f}%")

        return result
