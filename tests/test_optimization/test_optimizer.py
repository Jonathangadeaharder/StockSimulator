"""
Tests for Strategy Optimization

Comprehensive tests for GridSearchOptimizer, WalkForwardAnalyzer, and Position Sizing.
"""

import unittest
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from stocksimulator.data import load_from_csv
from stocksimulator.core.backtester import Backtester
from stocksimulator.strategies import MomentumStrategy
from stocksimulator.optimization import (
    GridSearchOptimizer,
    WalkForwardAnalyzer,
    KellyCriterion,
    FixedFractional
)


class TestGridSearchOptimizer(unittest.TestCase):
    """Test GridSearchOptimizer functionality."""

    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'historical_data')
        cls.spy_data = load_from_csv('sp500_stooq_daily.csv', 'SPY', data_path)

        end_date = cls.spy_data.data[-1].date
        cls.end_date = end_date
        cls.start_date = date(end_date.year - 2, end_date.month, end_date.day)

    def test_optimizer_initialization(self):
        """GridSearchOptimizer should initialize with backtester."""
        backtester = Backtester(initial_cash=100000.0)
        optimizer = GridSearchOptimizer(
            backtester=backtester,
            optimization_metric='sharpe_ratio'
        )

        self.assertEqual(optimizer.optimization_metric, 'sharpe_ratio')
        self.assertIsNotNone(optimizer.backtester)

    def test_optimize_simple_grid(self):
        """Should optimize strategy parameters with simple grid."""
        backtester = Backtester(initial_cash=100000.0)
        optimizer = GridSearchOptimizer(
            backtester=backtester,
            optimization_metric='sharpe_ratio'
        )

        # Simple parameter grid
        param_grid = {
            'lookback_days': [60, 126],
            'top_n': [1],
            'equal_weight': [True]
        }

        results = optimizer.optimize(
            strategy_class=MomentumStrategy,
            param_grid=param_grid,
            market_data={'SPY': self.spy_data},
            start_date=self.start_date,
            end_date=self.end_date,
            top_n=2
        )

        # Should return results
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)  # top_n=2

        # Results should be sorted by metric
        self.assertGreaterEqual(
            results[0].metric_value,
            results[1].metric_value
        )

    def test_optimize_multiple_parameters(self):
        """Should test all parameter combinations."""
        backtester = Backtester(initial_cash=100000.0)
        optimizer = GridSearchOptimizer(
            backtester=backtester,
            optimization_metric='annualized_return'
        )

        param_grid = {
            'lookback_days': [60, 126, 252],
            'top_n': [1, 2],
            'equal_weight': [True]
        }

        results = optimizer.optimize(
            strategy_class=MomentumStrategy,
            param_grid=param_grid,
            market_data={'SPY': self.spy_data},
            start_date=self.start_date,
            end_date=self.end_date,
            top_n=3
        )

        # Should test 3 x 2 = 6 combinations, return top 3
        self.assertEqual(len(results), 3)

        # Each result should have parameters and metric
        for result in results:
            self.assertIn('lookback_days', result.parameters)
            self.assertIn('top_n', result.parameters)
            self.assertIsNotNone(result.metric_value)
            self.assertIsNotNone(result.backtest_result)

    def test_optimize_different_metrics(self):
        """Should optimize for different metrics."""
        backtester = Backtester(initial_cash=100000.0)

        param_grid = {
            'lookback_days': [60, 126],
            'top_n': [1]
        }

        # Optimize for Sharpe
        opt_sharpe = GridSearchOptimizer(
            backtester=backtester,
            optimization_metric='sharpe_ratio'
        )

        results_sharpe = opt_sharpe.optimize(
            strategy_class=MomentumStrategy,
            param_grid=param_grid,
            market_data={'SPY': self.spy_data},
            start_date=self.start_date,
            end_date=self.end_date,
            top_n=1
        )

        # Optimize for return
        opt_return = GridSearchOptimizer(
            backtester=backtester,
            optimization_metric='annualized_return'
        )

        results_return = opt_return.optimize(
            strategy_class=MomentumStrategy,
            param_grid=param_grid,
            market_data={'SPY': self.spy_data},
            start_date=self.start_date,
            end_date=self.end_date,
            top_n=1
        )

        # Both should return results
        self.assertEqual(len(results_sharpe), 1)
        self.assertEqual(len(results_return), 1)

        # May select different parameters
        # (just verify they both work)
        self.assertIsNotNone(results_sharpe[0].metric_value)
        self.assertIsNotNone(results_return[0].metric_value)


class TestWalkForwardAnalyzer(unittest.TestCase):
    """Test WalkForwardAnalyzer functionality."""

    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'historical_data')
        cls.spy_data = load_from_csv('sp500_stooq_daily.csv', 'SPY', data_path)

    def test_walk_forward_initialization(self):
        """WalkForwardAnalyzer should initialize with backtester."""
        backtester = Backtester(initial_cash=100000.0)
        analyzer = WalkForwardAnalyzer(backtester=backtester)

        self.assertIsNotNone(analyzer.backtester)

    def test_walk_forward_analysis(self):
        """Should perform walk-forward analysis."""
        backtester = Backtester(initial_cash=100000.0)
        analyzer = WalkForwardAnalyzer(backtester=backtester)

        param_grid = {
            'lookback_days': [60, 126],
            'top_n': [1]
        }

        result = analyzer.analyze(
            strategy_class=MomentumStrategy,
            param_grid=param_grid,
            market_data={'SPY': self.spy_data},
            train_days=252,  # 1 year training
            test_days=63,    # 3 months testing
            step_days=63     # 3 months step
        )

        # Should complete without error
        self.assertIsNotNone(result)

    def test_walk_forward_summary(self):
        """Walk-forward should provide summary statistics."""
        backtester = Backtester(initial_cash=100000.0)
        analyzer = WalkForwardAnalyzer(backtester=backtester)

        param_grid = {
            'lookback_days': [60, 126]
        }

        result = analyzer.analyze(
            strategy_class=MomentumStrategy,
            param_grid=param_grid,
            market_data={'SPY': self.spy_data},
            train_days=252,
            test_days=126,
            step_days=126
        )

        summary = result.get_summary()

        # Should have summary metrics
        if summary:  # May be None if insufficient data
            self.assertIn('num_periods', summary)
            self.assertIn('avg_return', summary)
            self.assertIn('avg_sharpe', summary)


class TestPositionSizing(unittest.TestCase):
    """Test position sizing calculators."""

    def test_kelly_criterion_initialization(self):
        """KellyCriterion should initialize with fraction."""
        kelly = KellyCriterion(fraction=0.5)
        self.assertEqual(kelly.fraction, 0.5)

        kelly_full = KellyCriterion(fraction=1.0)
        self.assertEqual(kelly_full.fraction, 1.0)

    def test_kelly_criterion_calculation(self):
        """KellyCriterion should calculate position size."""
        kelly = KellyCriterion(fraction=0.5)

        position = kelly.calculate_position_size(
            account_value=100000,
            win_rate=0.60,
            avg_win=0.05,
            avg_loss=0.03
        )

        # Should return positive position size
        self.assertGreater(position, 0)
        self.assertLess(position, 100000)  # Should be less than account

    def test_kelly_criterion_high_win_rate(self):
        """Kelly should allocate more with higher win rate."""
        kelly = KellyCriterion(fraction=1.0)

        pos_low_wr = kelly.calculate_position_size(
            account_value=100000,
            win_rate=0.55,
            avg_win=0.05,
            avg_loss=0.03
        )

        pos_high_wr = kelly.calculate_position_size(
            account_value=100000,
            win_rate=0.70,
            avg_win=0.05,
            avg_loss=0.03
        )

        # Higher win rate should give larger position
        self.assertGreater(pos_high_wr, pos_low_wr)

    def test_kelly_criterion_negative_expectancy(self):
        """Kelly should return 0 for negative expectancy."""
        kelly = KellyCriterion(fraction=1.0)

        position = kelly.calculate_position_size(
            account_value=100000,
            win_rate=0.40,  # Low win rate
            avg_win=0.02,   # Small wins
            avg_loss=0.05   # Large losses
        )

        # Should be very small or 0
        self.assertLessEqual(position, 1000)

    def test_kelly_half_fraction(self):
        """Half-Kelly should be ~50% of full Kelly."""
        kelly_full = KellyCriterion(fraction=1.0)
        kelly_half = KellyCriterion(fraction=0.5)

        pos_full = kelly_full.calculate_position_size(
            account_value=100000,
            win_rate=0.60,
            avg_win=0.05,
            avg_loss=0.03
        )

        pos_half = kelly_half.calculate_position_size(
            account_value=100000,
            win_rate=0.60,
            avg_win=0.05,
            avg_loss=0.03
        )

        # Half-Kelly should be approximately half
        self.assertAlmostEqual(pos_half, pos_full * 0.5, delta=pos_full * 0.1)

    def test_fixed_fractional_initialization(self):
        """FixedFractional should initialize with risk percentage."""
        ff = FixedFractional(risk_pct=0.02)
        self.assertEqual(ff.risk_pct, 0.02)

    def test_fixed_fractional_calculation(self):
        """FixedFractional should calculate position size based on risk."""
        ff = FixedFractional(risk_pct=0.02)

        position = ff.calculate_position_size(
            account_value=100000,
            stop_loss_pct=0.05
        )

        # Risking 2% with 5% stop = 40% position size
        # $100k * 0.02 / 0.05 = $40k
        expected = 100000 * 0.02 / 0.05
        self.assertAlmostEqual(position, expected, delta=1000)

    def test_fixed_fractional_larger_stop(self):
        """FixedFractional should allocate less with larger stop loss."""
        ff = FixedFractional(risk_pct=0.02)

        pos_tight_stop = ff.calculate_position_size(
            account_value=100000,
            stop_loss_pct=0.02
        )

        pos_wide_stop = ff.calculate_position_size(
            account_value=100000,
            stop_loss_pct=0.10
        )

        # Tighter stop allows larger position
        self.assertGreater(pos_tight_stop, pos_wide_stop)

    def test_fixed_fractional_with_entry_and_stop(self):
        """FixedFractional should calculate with entry price and stop price."""
        ff = FixedFractional(risk_pct=0.02)

        position = ff.calculate_position_size(
            account_value=100000,
            entry_price=100,
            stop_price=95
        )

        # Risk = $100k * 0.02 = $2000
        # Risk per share = $100 - $95 = $5
        # Shares = $2000 / $5 = 400
        # Position = 400 * $100 = $40,000
        expected = 40000
        self.assertAlmostEqual(position, expected, delta=1000)

    def test_fixed_fractional_different_risk_levels(self):
        """FixedFractional should scale with risk percentage."""
        ff_conservative = FixedFractional(risk_pct=0.01)
        ff_aggressive = FixedFractional(risk_pct=0.05)

        pos_conservative = ff_conservative.calculate_position_size(
            account_value=100000,
            stop_loss_pct=0.05
        )

        pos_aggressive = ff_aggressive.calculate_position_size(
            account_value=100000,
            stop_loss_pct=0.05
        )

        # Aggressive should be 5x conservative
        self.assertAlmostEqual(pos_aggressive, pos_conservative * 5, delta=1000)


class TestOptimizationIntegration(unittest.TestCase):
    """Integration tests for optimization workflow."""

    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'historical_data')
        cls.spy_data = load_from_csv('sp500_stooq_daily.csv', 'SPY', data_path)

        end_date = cls.spy_data.data[-1].date
        cls.end_date = end_date
        cls.start_date = date(end_date.year - 1, end_date.month, end_date.day)

    def test_optimize_then_position_size(self):
        """Should optimize strategy then calculate position sizes."""
        # 1. Optimize strategy
        backtester = Backtester(initial_cash=100000.0)
        optimizer = GridSearchOptimizer(
            backtester=backtester,
            optimization_metric='sharpe_ratio'
        )

        param_grid = {
            'lookback_days': [60, 126],
            'top_n': [1]
        }

        results = optimizer.optimize(
            strategy_class=MomentumStrategy,
            param_grid=param_grid,
            market_data={'SPY': self.spy_data},
            start_date=self.start_date,
            end_date=self.end_date,
            top_n=1
        )

        best_params = results[0].parameters
        best_result = results[0].backtest_result

        # 2. Calculate position sizing based on results
        summary = best_result.get_performance_summary()

        # Estimate win rate and avg win/loss from transactions
        if len(best_result.transactions) > 0:
            kelly = KellyCriterion(fraction=0.5)

            # Rough estimates
            position = kelly.calculate_position_size(
                account_value=100000,
                win_rate=0.55,
                avg_win=0.05,
                avg_loss=0.03
            )

            self.assertGreater(position, 0)
            self.assertLess(position, 100000)


if __name__ == '__main__':
    unittest.main()
