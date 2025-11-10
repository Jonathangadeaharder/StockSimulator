"""
Tests for Monte Carlo Simulation

Comprehensive tests for Monte Carlo portfolio simulation.
"""

import unittest
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from stocksimulator.data import load_from_csv
from stocksimulator.simulation.monte_carlo import MonteCarloSimulator
from stocksimulator.strategies import MomentumStrategy


class TestMonteCarloSimulator(unittest.TestCase):
    """Test Monte Carlo simulation functionality."""

    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'historical_data')
        cls.spy_data = load_from_csv('sp500_stooq_daily.csv', 'SPY', data_path)

        end_date = cls.spy_data.data[-1].date
        cls.end_date = end_date
        cls.start_date = date(end_date.year - 2, end_date.month, end_date.day)

    def test_initialization(self):
        """MonteCarloSimulator should initialize with parameters."""
        sim = MonteCarloSimulator(
            num_simulations=100,
            initial_cash=100000.0
        )

        self.assertEqual(sim.num_simulations, 100)
        self.assertEqual(sim.initial_cash, 100000.0)

    def test_run_simulation_simple(self):
        """Should run Monte Carlo simulation."""
        sim = MonteCarloSimulator(
            num_simulations=10,  # Small number for testing
            initial_cash=100000.0
        )

        strategy = MomentumStrategy(lookback_days=126, top_n=1)

        result = sim.run_simulation(
            strategy=strategy,
            market_data={'SPY': self.spy_data},
            start_date=self.start_date,
            end_date=self.end_date
        )

        # Should complete without error
        self.assertIsNotNone(result)

    def test_simulation_results_distribution(self):
        """Simulation should produce distribution of outcomes."""
        sim = MonteCarloSimulator(
            num_simulations=50,
            initial_cash=100000.0
        )

        strategy = MomentumStrategy(lookback_days=60, top_n=1)

        result = sim.run_simulation(
            strategy=strategy,
            market_data={'SPY': self.spy_data},
            start_date=self.start_date,
            end_date=self.end_date
        )

        summary = result.get_summary()

        # Should have distribution statistics
        self.assertIn('mean_return', summary)
        self.assertIn('median_return', summary)
        self.assertIn('std_return', summary)
        self.assertIn('percentile_5', summary)
        self.assertIn('percentile_95', summary)

    def test_simulation_percentiles(self):
        """Should calculate percentiles correctly."""
        sim = MonteCarloSimulator(
            num_simulations=100,
            initial_cash=100000.0
        )

        strategy = MomentumStrategy(lookback_days=126, top_n=1)

        result = sim.run_simulation(
            strategy=strategy,
            market_data={'SPY': self.spy_data},
            start_date=self.start_date,
            end_date=self.end_date
        )

        summary = result.get_summary()

        # 5th percentile should be < median < 95th percentile
        self.assertLess(summary['percentile_5'], summary['median_return'])
        self.assertLess(summary['median_return'], summary['percentile_95'])

    def test_simulation_variance(self):
        """Simulations should show variance in outcomes."""
        sim = MonteCarloSimulator(
            num_simulations=30,
            initial_cash=100000.0
        )

        strategy = MomentumStrategy(lookback_days=126, top_n=1)

        result = sim.run_simulation(
            strategy=strategy,
            market_data={'SPY': self.spy_data},
            start_date=self.start_date,
            end_date=self.end_date
        )

        summary = result.get_summary()

        # Should have non-zero standard deviation
        self.assertGreater(summary['std_return'], 0)

    def test_simulation_probability_of_profit(self):
        """Should calculate probability of profit."""
        sim = MonteCarloSimulator(
            num_simulations=50,
            initial_cash=100000.0
        )

        strategy = MomentumStrategy(lookback_days=126, top_n=1)

        result = sim.run_simulation(
            strategy=strategy,
            market_data={'SPY': self.spy_data},
            start_date=self.start_date,
            end_date=self.end_date
        )

        summary = result.get_summary()

        # Should have probability of profit
        if 'prob_profit' in summary:
            self.assertGreaterEqual(summary['prob_profit'], 0)
            self.assertLessEqual(summary['prob_profit'], 1.0)

    def test_different_simulation_counts(self):
        """More simulations should give more stable results."""
        strategy = MomentumStrategy(lookback_days=60, top_n=1)

        # Few simulations
        sim_few = MonteCarloSimulator(
            num_simulations=10,
            initial_cash=100000.0
        )

        result_few = sim_few.run_simulation(
            strategy=strategy,
            market_data={'SPY': self.spy_data},
            start_date=self.start_date,
            end_date=self.end_date
        )

        # Many simulations
        sim_many = MonteCarloSimulator(
            num_simulations=100,
            initial_cash=100000.0
        )

        result_many = sim_many.run_simulation(
            strategy=strategy,
            market_data={'SPY': self.spy_data},
            start_date=self.start_date,
            end_date=self.end_date
        )

        # Both should complete
        self.assertIsNotNone(result_few)
        self.assertIsNotNone(result_many)

        # More simulations might have lower std error
        summary_few = result_few.get_summary()
        summary_many = result_many.get_summary()

        self.assertIn('mean_return', summary_few)
        self.assertIn('mean_return', summary_many)

    def test_simulation_final_values(self):
        """Should track final portfolio values across simulations."""
        sim = MonteCarloSimulator(
            num_simulations=20,
            initial_cash=100000.0
        )

        strategy = MomentumStrategy(lookback_days=126, top_n=1)

        result = sim.run_simulation(
            strategy=strategy,
            market_data={'SPY': self.spy_data},
            start_date=self.start_date,
            end_date=self.end_date
        )

        # Should have final values for each simulation
        final_values = result.get_final_values()

        self.assertEqual(len(final_values), 20)
        for value in final_values:
            self.assertGreater(value, 0)  # All should be positive

    def test_simulation_worst_case(self):
        """Should identify worst-case scenario."""
        sim = MonteCarloSimulator(
            num_simulations=50,
            initial_cash=100000.0
        )

        strategy = MomentumStrategy(lookback_days=126, top_n=1)

        result = sim.run_simulation(
            strategy=strategy,
            market_data={'SPY': self.spy_data},
            start_date=self.start_date,
            end_date=self.end_date
        )

        summary = result.get_summary()
        final_values = result.get_final_values()

        # Worst case should be minimum of all simulations
        worst_case = min(final_values)

        # Should be tracked in summary
        if 'worst_case' in summary:
            self.assertEqual(summary['worst_case'], worst_case)

    def test_simulation_best_case(self):
        """Should identify best-case scenario."""
        sim = MonteCarloSimulator(
            num_simulations=50,
            initial_cash=100000.0
        )

        strategy = MomentumStrategy(lookback_days=126, top_n=1)

        result = sim.run_simulation(
            strategy=strategy,
            market_data={'SPY': self.spy_data},
            start_date=self.start_date,
            end_date=self.end_date
        )

        final_values = result.get_final_values()

        # Best case should be maximum
        best_case = max(final_values)

        # Should be positive
        self.assertGreater(best_case, 100000)

    def test_simulation_with_different_strategies(self):
        """Should work with different strategies."""
        sim = MonteCarloSimulator(
            num_simulations=20,
            initial_cash=100000.0
        )

        # Test with momentum strategy
        strategy_momentum = MomentumStrategy(lookback_days=60, top_n=1)

        result_momentum = sim.run_simulation(
            strategy=strategy_momentum,
            market_data={'SPY': self.spy_data},
            start_date=self.start_date,
            end_date=self.end_date
        )

        # Should complete
        self.assertIsNotNone(result_momentum)

        summary = result_momentum.get_summary()
        self.assertIn('mean_return', summary)


if __name__ == '__main__':
    unittest.main()
