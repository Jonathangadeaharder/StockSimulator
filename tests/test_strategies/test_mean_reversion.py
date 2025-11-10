"""
Tests for Mean Reversion Strategies

Comprehensive tests for Bollinger Bands and RSI mean reversion strategies.
"""

import unittest
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from stocksimulator.data import load_from_csv
from stocksimulator.strategies import (
    BollingerBandsStrategy,
    RSIMeanReversionStrategy,
    MeanReversionStrategy
)
from stocksimulator.core.backtester import Backtester


class TestMeanReversionStrategies(unittest.TestCase):
    """Test mean reversion strategy implementations."""

    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'historical_data')
        cls.spy_data = load_from_csv('sp500_stooq_daily.csv', 'SPY', data_path)
        cls.backtester = Backtester(initial_cash=100000.0)

        # Get date range
        end_date = cls.spy_data.data[-1].date
        cls.end_date = end_date
        cls.start_date = date(end_date.year - 2, end_date.month, end_date.day)

    def test_bollinger_bands_initialization(self):
        """BollingerBandsStrategy should initialize with parameters."""
        strategy = BollingerBandsStrategy(
            symbol='SPY',
            period=20,
            num_std=2.0
        )

        self.assertEqual(strategy.symbol, 'SPY')
        self.assertEqual(strategy.period, 20)
        self.assertEqual(strategy.num_std, 2.0)

    def test_bollinger_bands_backtest(self):
        """BollingerBandsStrategy should run backtest successfully."""
        strategy = BollingerBandsStrategy(
            symbol='SPY',
            period=20,
            num_std=2.0
        )

        result = self.backtester.run_backtest(
            strategy_name='Bollinger Bands Test',
            market_data={'SPY': self.spy_data},
            strategy_func=strategy.calculate_allocation,
            start_date=self.start_date,
            end_date=self.end_date,
            rebalance_frequency='daily'
        )

        self.assertIsNotNone(result)
        self.assertGreater(len(result.equity_curve), 0)
        self.assertGreater(len(result.transactions), 0)

    def test_bollinger_bands_oversold_buys(self):
        """BollingerBands should buy when price touches lower band."""
        strategy = BollingerBandsStrategy(
            symbol='SPY',
            period=20,
            num_std=2.0,
            oversold_pct=100.0  # Full allocation when oversold
        )

        result = self.backtester.run_backtest(
            strategy_name='BB Oversold Test',
            market_data={'SPY': self.spy_data},
            strategy_func=strategy.calculate_allocation,
            start_date=self.start_date,
            end_date=self.end_date,
            rebalance_frequency='daily'
        )

        summary = result.get_performance_summary()
        self.assertIn('num_transactions', summary)
        self.assertGreater(summary['num_transactions'], 0)

    def test_bollinger_bands_different_parameters(self):
        """BollingerBands should work with different parameters."""
        # Wider bands (3 std dev)
        strategy_wide = BollingerBandsStrategy(
            symbol='SPY',
            period=20,
            num_std=3.0
        )

        # Narrower bands (1 std dev)
        strategy_narrow = BollingerBandsStrategy(
            symbol='SPY',
            period=20,
            num_std=1.0
        )

        result_wide = self.backtester.run_backtest(
            strategy_name='BB Wide',
            market_data={'SPY': self.spy_data},
            strategy_func=strategy_wide.calculate_allocation,
            start_date=self.start_date,
            end_date=self.end_date,
            rebalance_frequency='weekly'
        )

        result_narrow = self.backtester.run_backtest(
            strategy_name='BB Narrow',
            market_data={'SPY': self.spy_data},
            strategy_func=strategy_narrow.calculate_allocation,
            start_date=self.start_date,
            end_date=self.end_date,
            rebalance_frequency='weekly'
        )

        # Narrow bands should trade more frequently
        self.assertGreater(
            len(result_narrow.transactions),
            len(result_wide.transactions)
        )

    def test_rsi_mean_reversion_initialization(self):
        """RSIMeanReversionStrategy should initialize with parameters."""
        strategy = RSIMeanReversionStrategy(
            symbol='SPY',
            rsi_period=14,
            oversold_threshold=30,
            overbought_threshold=70
        )

        self.assertEqual(strategy.symbol, 'SPY')
        self.assertEqual(strategy.rsi_period, 14)
        self.assertEqual(strategy.oversold_threshold, 30)
        self.assertEqual(strategy.overbought_threshold, 70)

    def test_rsi_mean_reversion_backtest(self):
        """RSIMeanReversionStrategy should run backtest successfully."""
        strategy = RSIMeanReversionStrategy(
            symbol='SPY',
            rsi_period=14,
            oversold_threshold=30,
            overbought_threshold=70
        )

        result = self.backtester.run_backtest(
            strategy_name='RSI Mean Reversion Test',
            market_data={'SPY': self.spy_data},
            strategy_func=strategy.calculate_allocation,
            start_date=self.start_date,
            end_date=self.end_date,
            rebalance_frequency='daily'
        )

        self.assertIsNotNone(result)
        self.assertGreater(len(result.equity_curve), 0)

    def test_rsi_oversold_buys(self):
        """RSI strategy should buy when oversold."""
        strategy = RSIMeanReversionStrategy(
            symbol='SPY',
            rsi_period=14,
            oversold_threshold=30,
            overbought_threshold=70,
            oversold_allocation=100.0
        )

        result = self.backtester.run_backtest(
            strategy_name='RSI Oversold',
            market_data={'SPY': self.spy_data},
            strategy_func=strategy.calculate_allocation,
            start_date=self.start_date,
            end_date=self.end_date,
            rebalance_frequency='daily'
        )

        # Should have made some trades
        self.assertGreater(len(result.transactions), 0)

    def test_rsi_different_thresholds(self):
        """RSI should behave differently with different thresholds."""
        # Aggressive (wider range)
        strategy_aggressive = RSIMeanReversionStrategy(
            symbol='SPY',
            oversold_threshold=40,
            overbought_threshold=60
        )

        # Conservative (narrower range)
        strategy_conservative = RSIMeanReversionStrategy(
            symbol='SPY',
            oversold_threshold=20,
            overbought_threshold=80
        )

        result_aggressive = self.backtester.run_backtest(
            strategy_name='RSI Aggressive',
            market_data={'SPY': self.spy_data},
            strategy_func=strategy_aggressive.calculate_allocation,
            start_date=self.start_date,
            end_date=self.end_date,
            rebalance_frequency='daily'
        )

        result_conservative = self.backtester.run_backtest(
            strategy_name='RSI Conservative',
            market_data={'SPY': self.spy_data},
            strategy_func=strategy_conservative.calculate_allocation,
            start_date=self.start_date,
            end_date=self.end_date,
            rebalance_frequency='daily'
        )

        # Aggressive should trade more
        self.assertGreater(
            len(result_aggressive.transactions),
            len(result_conservative.transactions)
        )

    def test_mean_reversion_base_initialization(self):
        """MeanReversionStrategy should initialize with parameters."""
        strategy = MeanReversionStrategy(
            symbol='SPY',
            lookback_period=20,
            entry_threshold=1.5,
            exit_threshold=0.5
        )

        self.assertEqual(strategy.symbol, 'SPY')
        self.assertEqual(strategy.lookback_period, 20)
        self.assertEqual(strategy.entry_threshold, 1.5)

    def test_mean_reversion_backtest(self):
        """MeanReversionStrategy should run backtest successfully."""
        strategy = MeanReversionStrategy(
            symbol='SPY',
            lookback_period=20,
            entry_threshold=1.5,
            exit_threshold=0.5
        )

        result = self.backtester.run_backtest(
            strategy_name='Mean Reversion',
            market_data={'SPY': self.spy_data},
            strategy_func=strategy.calculate_allocation,
            start_date=self.start_date,
            end_date=self.end_date,
            rebalance_frequency='daily'
        )

        self.assertIsNotNone(result)
        self.assertGreater(len(result.equity_curve), 0)

    def test_mean_reversion_performance(self):
        """Mean reversion strategies should produce reasonable results."""
        strategy = MeanReversionStrategy(
            symbol='SPY',
            lookback_period=20,
            entry_threshold=2.0
        )

        result = self.backtester.run_backtest(
            strategy_name='Mean Reversion Performance',
            market_data={'SPY': self.spy_data},
            strategy_func=strategy.calculate_allocation,
            start_date=self.start_date,
            end_date=self.end_date,
            rebalance_frequency='weekly'
        )

        summary = result.get_performance_summary()

        # Should have reasonable metrics
        self.assertIn('annualized_return', summary)
        self.assertIn('max_drawdown', summary)
        self.assertIn('sharpe_ratio', summary)

        # Returns should not be absurdly high or low
        self.assertGreater(summary['annualized_return'], -50)
        self.assertLess(summary['annualized_return'], 200)

    def test_bollinger_bands_with_cash_proxy(self):
        """BollingerBands should use cash proxy when overbought."""
        strategy = BollingerBandsStrategy(
            symbol='SPY',
            period=20,
            num_std=2.0,
            cash_proxy='SHY'
        )

        # Run short backtest
        short_end = date(self.start_date.year, self.start_date.month + 3, self.start_date.day)

        result = self.backtester.run_backtest(
            strategy_name='BB Cash Proxy',
            market_data={'SPY': self.spy_data},
            strategy_func=strategy.calculate_allocation,
            start_date=self.start_date,
            end_date=short_end,
            rebalance_frequency='weekly'
        )

        # Should complete without errors
        self.assertIsNotNone(result)

    def test_rsi_with_scaling(self):
        """RSI strategy should scale allocation based on RSI value."""
        strategy = RSIMeanReversionStrategy(
            symbol='SPY',
            rsi_period=14,
            oversold_threshold=30,
            oversold_allocation=100.0
        )

        result = self.backtester.run_backtest(
            strategy_name='RSI Scaling',
            market_data={'SPY': self.spy_data},
            strategy_func=strategy.calculate_allocation,
            start_date=self.start_date,
            end_date=self.end_date,
            rebalance_frequency='daily'
        )

        # Should have transactions
        self.assertGreater(len(result.transactions), 0)

        # Final value should be positive
        final_value = result.equity_curve[-1]['total_value']
        self.assertGreater(final_value, 0)


if __name__ == '__main__':
    unittest.main()
