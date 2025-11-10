"""
Test suite for core backtester module.

Tests the main backtesting engine with real historical data.
"""

import unittest
import sys
import os
from datetime import date

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from stocksimulator.core.backtester import Backtester
from stocksimulator.data import load_from_csv


class TestBacktester(unittest.TestCase):
    """Test the Backtester class."""

    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        # Load S&P 500 data
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'historical_data')
        cls.spy_data = load_from_csv('sp500_stooq_daily.csv', 'SPY', data_path)

    def setUp(self):
        """Set up test fixtures."""
        self.backtester = Backtester(initial_cash=100000.0, transaction_cost_bps=2.0)

    def test_backtester_initialization(self):
        """Backtester should initialize with correct parameters."""
        self.assertEqual(self.backtester.initial_cash, 100000.0)
        self.assertEqual(self.backtester.transaction_cost_bps, 2.0)

    def test_simple_buy_and_hold_strategy(self):
        """Buy and hold strategy should produce positive returns over long period."""
        def buy_hold(current_date, market_data, portfolio, current_prices):
            return {'SPY': 100.0}

        # Test 5-year period
        end_date = self.spy_data.data[-1].date
        start_date = date(end_date.year - 5, end_date.month, end_date.day)

        result = self.backtester.run_backtest(
            strategy_name='Buy & Hold',
            market_data={'SPY': self.spy_data},
            strategy_func=buy_hold,
            start_date=start_date,
            end_date=end_date,
            rebalance_frequency='monthly'
        )

        # Assertions
        self.assertIsNotNone(result)
        self.assertGreater(len(result.equity_curve), 0)
        self.assertEqual(result.strategy_name, 'Buy & Hold')

        # Should have reasonable final value
        final_value = result.equity_curve[-1].value
        self.assertGreater(final_value, 0)

    def test_backtest_produces_performance_summary(self):
        """Backtest should produce valid performance summary."""
        def buy_hold(current_date, market_data, portfolio, current_prices):
            return {'SPY': 100.0}

        end_date = self.spy_data.data[-1].date
        start_date = date(end_date.year - 3, end_date.month, end_date.day)

        result = self.backtester.run_backtest(
            'Test Strategy',
            {'SPY': self.spy_data},
            buy_hold,
            start_date,
            end_date
        )

        summary = result.get_performance_summary()

        # Check all required keys
        required_keys = [
            'total_return', 'annualized_return', 'sharpe_ratio',
            'max_drawdown', 'volatility', 'num_trades'
        ]
        for key in required_keys:
            self.assertIn(key, summary)

        # Check types
        self.assertIsInstance(summary['total_return'], float)
        self.assertIsInstance(summary['sharpe_ratio'], float)
        self.assertIsInstance(summary['num_trades'], int)

    def test_transaction_costs_reduce_returns(self):
        """Transaction costs should reduce returns."""
        def monthly_rebalance(current_date, market_data, portfolio, current_prices):
            return {'SPY': 100.0}

        end_date = self.spy_data.data[-1].date
        start_date = date(end_date.year - 2, end_date.month, end_date.day)

        # Backtest with no costs
        backtester_no_cost = Backtester(initial_cash=100000.0, transaction_cost_bps=0.0)
        result_no_cost = backtester_no_cost.run_backtest(
            'No Cost',
            {'SPY': self.spy_data},
            monthly_rebalance,
            start_date,
            end_date,
            rebalance_frequency='monthly'
        )

        # Backtest with costs
        backtester_with_cost = Backtester(initial_cash=100000.0, transaction_cost_bps=10.0)
        result_with_cost = backtester_with_cost.run_backtest(
            'With Cost',
            {'SPY': self.spy_data},
            monthly_rebalance,
            start_date,
            end_date,
            rebalance_frequency='monthly'
        )

        # Returns with costs should be lower
        summary_no_cost = result_no_cost.get_performance_summary()
        summary_with_cost = result_with_cost.get_performance_summary()

        self.assertGreater(
            summary_no_cost['total_return'],
            summary_with_cost['total_return'],
            "Returns without costs should be higher than with costs"
        )

    def test_different_rebalance_frequencies(self):
        """Different rebalance frequencies should produce different results."""
        def simple_strategy(current_date, market_data, portfolio, current_prices):
            return {'SPY': 100.0}

        end_date = self.spy_data.data[-1].date
        start_date = date(end_date.year - 2, end_date.month, end_date.day)

        # Daily rebalancing
        result_daily = self.backtester.run_backtest(
            'Daily',
            {'SPY': self.spy_data},
            simple_strategy,
            start_date,
            end_date,
            rebalance_frequency='daily'
        )

        # Monthly rebalancing
        result_monthly = self.backtester.run_backtest(
            'Monthly',
            {'SPY': self.spy_data},
            simple_strategy,
            start_date,
            end_date,
            rebalance_frequency='monthly'
        )

        # Should have different numbers of trades
        self.assertNotEqual(
            len(result_daily.trades),
            len(result_monthly.trades)
        )

        # Daily should have more trades
        self.assertGreater(len(result_daily.trades), len(result_monthly.trades))

    def test_equity_curve_starts_at_initial_cash(self):
        """Equity curve should start at initial cash value."""
        def simple_strategy(current_date, market_data, portfolio, current_prices):
            return {'SPY': 100.0}

        end_date = self.spy_data.data[-1].date
        start_date = date(end_date.year - 1, end_date.month, end_date.day)

        result = self.backtester.run_backtest(
            'Test',
            {'SPY': self.spy_data},
            simple_strategy,
            start_date,
            end_date
        )

        first_value = result.equity_curve[0].value
        self.assertAlmostEqual(first_value, 100000.0, places=0)

    def test_empty_strategy_keeps_cash(self):
        """Strategy that returns empty allocation should keep cash."""
        def empty_strategy(current_date, market_data, portfolio, current_prices):
            return {}  # No allocation

        end_date = self.spy_data.data[-1].date
        start_date = date(end_date.year - 1, end_date.month, end_date.day)

        result = self.backtester.run_backtest(
            'Empty',
            {'SPY': self.spy_data},
            empty_strategy,
            start_date,
            end_date
        )

        # Should maintain approximately initial cash
        final_value = result.equity_curve[-1].value
        self.assertAlmostEqual(final_value, 100000.0, delta=100)  # Allow small variation

        # Should have zero or minimal trades
        self.assertLess(len(result.trades), 5)


class TestBacktestResult(unittest.TestCase):
    """Test the BacktestResult class."""

    @classmethod
    def setUpClass(cls):
        """Load test data once."""
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'historical_data')
        cls.spy_data = load_from_csv('sp500_stooq_daily.csv', 'SPY', data_path)

    def setUp(self):
        """Run a simple backtest for testing."""
        backtester = Backtester(initial_cash=100000.0)

        def buy_hold(current_date, market_data, portfolio, current_prices):
            return {'SPY': 100.0}

        end_date = self.spy_data.data[-1].date
        start_date = date(end_date.year - 3, end_date.month, end_date.day)

        self.result = backtester.run_backtest(
            'Test',
            {'SPY': self.spy_data},
            buy_hold,
            start_date,
            end_date
        )

    def test_performance_summary_has_all_metrics(self):
        """Performance summary should include all key metrics."""
        summary = self.result.get_performance_summary()

        required_metrics = [
            'total_return',
            'annualized_return',
            'sharpe_ratio',
            'sortino_ratio',
            'max_drawdown',
            'volatility',
            'num_trades',
            'win_rate'
        ]

        for metric in required_metrics:
            self.assertIn(metric, summary, f"Missing metric: {metric}")

    def test_sharpe_ratio_calculation(self):
        """Sharpe ratio should be calculated correctly."""
        summary = self.result.get_performance_summary()
        sharpe = summary['sharpe_ratio']

        # Sharpe should be a reasonable number
        self.assertIsInstance(sharpe, float)
        self.assertGreater(sharpe, -5)  # Not absurdly negative
        self.assertLess(sharpe, 10)     # Not absurdly positive

    def test_max_drawdown_is_negative_or_zero(self):
        """Max drawdown should be negative or zero."""
        summary = self.result.get_performance_summary()
        max_dd = summary['max_drawdown']

        self.assertLessEqual(max_dd, 0)

    def test_win_rate_is_percentage(self):
        """Win rate should be between 0 and 100."""
        summary = self.result.get_performance_summary()
        win_rate = summary['win_rate']

        self.assertGreaterEqual(win_rate, 0)
        self.assertLessEqual(win_rate, 100)


if __name__ == '__main__':
    unittest.main()
