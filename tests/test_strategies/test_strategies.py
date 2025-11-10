"""
Test suite for trading strategies.

Tests various strategy implementations.
"""

import unittest
import sys
import os
from datetime import date

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from stocksimulator.data import load_from_csv
from stocksimulator.core.backtester import Backtester
from stocksimulator.strategies import (
    DCAStrategy, FixedAllocationStrategy, Balanced6040Strategy,
    MomentumStrategy, RiskParityStrategy
)


class TestDCAStrategies(unittest.TestCase):
    """Test dollar-cost averaging strategies."""

    @classmethod
    def setUpClass(cls):
        """Load test data."""
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'historical_data')
        cls.spy_data = load_from_csv('sp500_stooq_daily.csv', 'SPY', data_path)

    def test_dca_strategy_initialization(self):
        """DCA strategy should initialize correctly."""
        strategy = DCAStrategy(symbols=['SPY'], equal_weight=True)
        self.assertIsNotNone(strategy)
        self.assertEqual(strategy.symbols, ['SPY'])

    def test_dca_produces_valid_allocation(self):
        """DCA should produce valid allocation."""
        strategy = DCAStrategy(symbols=['SPY'])

        # Get allocation
        allocation = strategy(
            current_date=self.spy_data.data[-1].date,
            market_data={'SPY': self.spy_data},
            portfolio=None,
            current_prices={'SPY': 100.0}
        )

        self.assertIsInstance(allocation, dict)
        self.assertIn('SPY', allocation)
        self.assertAlmostEqual(allocation['SPY'], 100.0, places=1)

    def test_fixed_allocation_strategy(self):
        """Fixed allocation should maintain target weights."""
        strategy = FixedAllocationStrategy(allocation={'SPY': 100.0})

        allocation = strategy(
            current_date=self.spy_data.data[-1].date,
            market_data={'SPY': self.spy_data},
            portfolio=None,
            current_prices={'SPY': 100.0}
        )

        self.assertEqual(allocation['SPY'], 100.0)

    def test_balanced_60_40_strategy(self):
        """Balanced 60/40 should allocate 60/40."""
        # Try to load TLT data
        try:
            data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'historical_data')
            tlt_data = load_from_csv('tlt_stooq_daily.csv', 'TLT', data_path)

            strategy = Balanced6040Strategy()

            allocation = strategy(
                current_date=self.spy_data.data[-1].date,
                market_data={'SPY': self.spy_data, 'TLT': tlt_data},
                portfolio=None,
                current_prices={'SPY': 100.0, 'TLT': 50.0}
            )

            self.assertAlmostEqual(allocation.get('SPY', 0), 60.0, places=1)
            self.assertAlmostEqual(allocation.get('TLT', 0), 40.0, places=1)

        except FileNotFoundError:
            self.skipTest("TLT data not available")


class TestMomentumStrategy(unittest.TestCase):
    """Test momentum-based strategies."""

    @classmethod
    def setUpClass(cls):
        """Load test data."""
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'historical_data')
        cls.spy_data = load_from_csv('sp500_stooq_daily.csv', 'SPY', data_path)

    def test_momentum_strategy_initialization(self):
        """Momentum strategy should initialize with parameters."""
        strategy = MomentumStrategy(lookback_days=126, top_n=1)

        self.assertEqual(strategy.lookback_days, 126)
        self.assertEqual(strategy.top_n, 1)

    def test_momentum_strategy_produces_allocation(self):
        """Momentum should produce valid allocation."""
        strategy = MomentumStrategy(lookback_days=126, top_n=1)

        # Need enough history
        end_date = self.spy_data.data[-1].date
        start_date = self.spy_data.data[-200].date  # Use data with sufficient history

        allocation = strategy(
            current_date=end_date,
            market_data={'SPY': self.spy_data},
            portfolio=None,
            current_prices={'SPY': self.spy_data.data[-1].close}
        )

        self.assertIsInstance(allocation, dict)
        # Should either hold SPY or be empty
        if 'SPY' in allocation:
            self.assertGreater(allocation['SPY'], 0)
            self.assertLessEqual(allocation['SPY'], 100.0)

    def test_momentum_with_backtest(self):
        """Momentum strategy should work in backtest."""
        strategy = MomentumStrategy(lookback_days=60, top_n=1)
        backtester = Backtester(initial_cash=100000.0)

        end_date = self.spy_data.data[-1].date
        start_date = date(end_date.year - 2, end_date.month, end_date.day)

        result = backtester.run_backtest(
            'Momentum',
            {'SPY': self.spy_data},
            strategy,
            start_date,
            end_date
        )

        self.assertIsNotNone(result)
        self.assertGreater(len(result.equity_curve), 0)


class TestRiskParityStrategy(unittest.TestCase):
    """Test risk parity strategies."""

    @classmethod
    def setUpClass(cls):
        """Load test data."""
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'historical_data')
        cls.spy_data = load_from_csv('sp500_stooq_daily.csv', 'SPY', data_path)

    def test_risk_parity_initialization(self):
        """Risk parity should initialize with lookback period."""
        strategy = RiskParityStrategy(lookback_days=60)
        self.assertEqual(strategy.lookback_days, 60)

    def test_risk_parity_produces_allocation(self):
        """Risk parity should produce valid allocation."""
        strategy = RiskParityStrategy(lookback_days=60)

        end_date = self.spy_data.data[-1].date

        allocation = strategy(
            current_date=end_date,
            market_data={'SPY': self.spy_data},
            portfolio=None,
            current_prices={'SPY': self.spy_data.data[-1].close}
        )

        self.assertIsInstance(allocation, dict)

        # If allocation exists, should sum to ~100
        if allocation:
            total = sum(allocation.values())
            self.assertAlmostEqual(total, 100.0, places=0)


class TestStrategyIntegration(unittest.TestCase):
    """Integration tests for strategies with backtester."""

    @classmethod
    def setUpClass(cls):
        """Load test data."""
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'historical_data')
        cls.spy_data = load_from_csv('sp500_stooq_daily.csv', 'SPY', data_path)

    def test_multiple_strategies_comparison(self):
        """Should be able to compare multiple strategies."""
        backtester = Backtester(initial_cash=100000.0)

        end_date = self.spy_data.data[-1].date
        start_date = date(end_date.year - 2, end_date.month, end_date.day)

        strategies = {
            'DCA': DCAStrategy(symbols=['SPY']),
            'Momentum': MomentumStrategy(lookback_days=126, top_n=1),
        }

        results = {}
        for name, strategy in strategies.items():
            result = backtester.run_backtest(
                name,
                {'SPY': self.spy_data},
                strategy,
                start_date,
                end_date
            )
            results[name] = result

        # All should complete successfully
        self.assertEqual(len(results), 2)

        # All should have positive final values
        for name, result in results.items():
            final_value = result.equity_curve[-1].value
            self.assertGreater(final_value, 0, f"{name} should have positive final value")

    def test_strategy_with_transaction_costs(self):
        """Strategies should work with transaction costs."""
        strategy = DCAStrategy(symbols=['SPY'])
        backtester = Backtester(initial_cash=100000.0, transaction_cost_bps=10.0)

        end_date = self.spy_data.data[-1].date
        start_date = date(end_date.year - 1, end_date.month, end_date.day)

        result = backtester.run_backtest(
            'DCA with costs',
            {'SPY': self.spy_data},
            strategy,
            start_date,
            end_date
        )

        # Should complete and have trades
        self.assertIsNotNone(result)
        self.assertGreater(len(result.trades), 0)


if __name__ == '__main__':
    unittest.main()
