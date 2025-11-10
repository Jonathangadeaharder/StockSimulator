"""
Tests for Risk Calculator

Comprehensive tests for all risk metrics and calculations.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from stocksimulator.core.risk_calculator import RiskCalculator


class TestRiskCalculator(unittest.TestCase):
    """Test RiskCalculator functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.calc = RiskCalculator(risk_free_rate=0.02)

    def test_initialization(self):
        """RiskCalculator should initialize with default risk-free rate."""
        calc = RiskCalculator()
        self.assertEqual(calc.risk_free_rate, 0.02)

        calc_custom = RiskCalculator(risk_free_rate=0.03)
        self.assertEqual(calc_custom.risk_free_rate, 0.03)

    def test_calculate_volatility_simple(self):
        """Should calculate volatility from returns."""
        # Simple returns with known volatility
        returns = [0.01, 0.02, -0.01, 0.03, -0.02]
        vol = self.calc.calculate_volatility(returns, annualize=False)
        self.assertGreater(vol, 0)
        self.assertLess(vol, 0.1)

    def test_calculate_volatility_annualized(self):
        """Should annualize volatility correctly."""
        returns = [0.01] * 252  # 252 trading days
        vol_daily = self.calc.calculate_volatility(returns, annualize=False)
        vol_annual = self.calc.calculate_volatility(returns, annualize=True)

        # Annualized should be ~sqrt(252) times daily
        self.assertGreater(vol_annual, vol_daily)

    def test_calculate_volatility_insufficient_data(self):
        """Should return 0 for insufficient data."""
        returns = [0.01]  # Only one return
        vol = self.calc.calculate_volatility(returns)
        self.assertEqual(vol, 0.0)

    def test_calculate_sharpe_ratio_positive(self):
        """Should calculate positive Sharpe ratio for good returns."""
        # Returns averaging 10% annually
        returns = [0.0004] * 252  # ~10% annual return
        sharpe = self.calc.calculate_sharpe_ratio(returns)
        self.assertGreater(sharpe, 0)

    def test_calculate_sharpe_ratio_negative(self):
        """Should calculate negative Sharpe ratio for poor returns."""
        # Negative returns
        returns = [-0.001] * 252
        sharpe = self.calc.calculate_sharpe_ratio(returns)
        self.assertLess(sharpe, 0)

    def test_calculate_sharpe_ratio_zero_volatility(self):
        """Should return 0 for zero volatility."""
        returns = [0.0] * 252  # No volatility
        sharpe = self.calc.calculate_sharpe_ratio(returns)
        self.assertEqual(sharpe, 0.0)

    def test_calculate_sharpe_ratio_custom_rfr(self):
        """Should use custom risk-free rate when provided."""
        returns = [0.001] * 252
        sharpe_default = self.calc.calculate_sharpe_ratio(returns)
        sharpe_custom = self.calc.calculate_sharpe_ratio(returns, risk_free_rate=0.05)

        # Higher RFR should reduce Sharpe ratio
        self.assertLess(sharpe_custom, sharpe_default)

    def test_calculate_sortino_ratio_positive(self):
        """Should calculate Sortino ratio for positive returns."""
        # Mix of positive and negative returns
        returns = [0.01, 0.02, -0.01, 0.03, -0.005, 0.015]
        sortino = self.calc.calculate_sortino_ratio(returns, periods_per_year=252)
        self.assertIsInstance(sortino, float)

    def test_calculate_sortino_ratio_no_downside(self):
        """Should return inf for no downside deviation."""
        # All positive returns
        returns = [0.01, 0.02, 0.03]
        sortino = self.calc.calculate_sortino_ratio(returns)
        self.assertEqual(sortino, float('inf'))

    def test_calculate_sortino_ratio_all_negative(self):
        """Should handle all negative returns."""
        returns = [-0.01, -0.02, -0.03]
        sortino = self.calc.calculate_sortino_ratio(returns)
        self.assertLess(sortino, 0)

    def test_calculate_max_drawdown_simple(self):
        """Should calculate maximum drawdown correctly."""
        # Portfolio goes from 100 to 120 to 90 to 110
        values = [100, 110, 120, 100, 90, 100, 110]
        max_dd = self.calc.calculate_max_drawdown(values)

        # Max drawdown is from 120 to 90 = 25%
        self.assertAlmostEqual(max_dd, 25.0, delta=1.0)

    def test_calculate_max_drawdown_no_drawdown(self):
        """Should return 0 for always-increasing portfolio."""
        values = [100, 110, 120, 130, 140]
        max_dd = self.calc.calculate_max_drawdown(values)
        self.assertEqual(max_dd, 0.0)

    def test_calculate_max_drawdown_continuous_decline(self):
        """Should calculate drawdown for continuous decline."""
        values = [100, 90, 80, 70, 60]
        max_dd = self.calc.calculate_max_drawdown(values)
        # 100 to 60 = 40% drawdown
        self.assertAlmostEqual(max_dd, 40.0, delta=0.1)

    def test_calculate_max_drawdown_empty(self):
        """Should return 0 for empty values."""
        max_dd = self.calc.calculate_max_drawdown([])
        self.assertEqual(max_dd, 0.0)

    def test_calculate_var_simple(self):
        """Should calculate Value at Risk."""
        # Normal distribution of returns
        returns = [0.01, 0.02, -0.01, -0.02, 0.03, -0.03, 0.00, 0.01]
        var = self.calc.calculate_var(returns, confidence_level=0.95, portfolio_value=100000)

        self.assertGreater(var, 0)
        self.assertLess(var, 10000)  # Should be reasonable

    def test_calculate_var_different_confidence(self):
        """Should calculate different VaR for different confidence levels."""
        returns = [0.01, 0.02, -0.01, -0.02, 0.03, -0.03, 0.00, 0.01] * 10

        var_95 = self.calc.calculate_var(returns, confidence_level=0.95)
        var_99 = self.calc.calculate_var(returns, confidence_level=0.99)

        # 99% VaR should be higher (more conservative)
        self.assertGreater(var_99, var_95)

    def test_calculate_var_empty(self):
        """Should return 0 for empty returns."""
        var = self.calc.calculate_var([])
        self.assertEqual(var, 0.0)

    def test_calculate_cvar_simple(self):
        """Should calculate Conditional VaR (Expected Shortfall)."""
        returns = [0.01, 0.02, -0.01, -0.02, 0.03, -0.03, 0.00, 0.01]
        cvar = self.calc.calculate_cvar(returns, confidence_level=0.95, portfolio_value=100000)

        self.assertGreater(cvar, 0)

        # CVaR should be >= VaR
        var = self.calc.calculate_var(returns, confidence_level=0.95, portfolio_value=100000)
        self.assertGreaterEqual(cvar, var * 0.5)  # At least half of VaR

    def test_calculate_cvar_empty(self):
        """Should return 0 for empty returns."""
        cvar = self.calc.calculate_cvar([])
        self.assertEqual(cvar, 0.0)

    def test_calculate_beta_simple(self):
        """Should calculate beta relative to market."""
        # Asset with same returns as market should have beta ~1
        market_returns = [0.01, 0.02, -0.01, 0.03, -0.02]
        asset_returns = [0.01, 0.02, -0.01, 0.03, -0.02]

        beta = self.calc.calculate_beta(asset_returns, market_returns)
        self.assertAlmostEqual(beta, 1.0, delta=0.1)

    def test_calculate_beta_amplified(self):
        """Should calculate beta > 1 for volatile asset."""
        market_returns = [0.01, 0.02, -0.01, 0.03, -0.02]
        # Asset with 2x returns
        asset_returns = [0.02, 0.04, -0.02, 0.06, -0.04]

        beta = self.calc.calculate_beta(asset_returns, market_returns)
        self.assertGreater(beta, 1.5)

    def test_calculate_beta_defensive(self):
        """Should calculate beta < 1 for defensive asset."""
        market_returns = [0.01, 0.02, -0.01, 0.03, -0.02]
        # Asset with 0.5x returns
        asset_returns = [0.005, 0.01, -0.005, 0.015, -0.01]

        beta = self.calc.calculate_beta(asset_returns, market_returns)
        self.assertLess(beta, 0.8)

    def test_calculate_beta_mismatched_length(self):
        """Should return 0 for mismatched lengths."""
        asset_returns = [0.01, 0.02]
        market_returns = [0.01, 0.02, 0.03]

        beta = self.calc.calculate_beta(asset_returns, market_returns)
        self.assertEqual(beta, 0.0)

    def test_calculate_beta_insufficient_data(self):
        """Should return 0 for insufficient data."""
        beta = self.calc.calculate_beta([0.01], [0.01])
        self.assertEqual(beta, 0.0)

    def test_calculate_information_ratio_outperformance(self):
        """Should calculate positive IR for outperforming portfolio."""
        benchmark_returns = [0.01, 0.02, -0.01, 0.03]
        # Portfolio slightly outperforms
        portfolio_returns = [0.015, 0.025, -0.005, 0.035]

        ir = self.calc.calculate_information_ratio(portfolio_returns, benchmark_returns)
        self.assertGreater(ir, 0)

    def test_calculate_information_ratio_underperformance(self):
        """Should calculate negative IR for underperforming portfolio."""
        benchmark_returns = [0.01, 0.02, -0.01, 0.03]
        portfolio_returns = [0.005, 0.015, -0.015, 0.025]

        ir = self.calc.calculate_information_ratio(portfolio_returns, benchmark_returns)
        self.assertLess(ir, 0)

    def test_calculate_information_ratio_identical(self):
        """Should calculate ~0 IR for identical performance."""
        returns = [0.01, 0.02, -0.01, 0.03]

        ir = self.calc.calculate_information_ratio(returns, returns)
        self.assertAlmostEqual(ir, 0.0, delta=0.01)

    def test_calculate_information_ratio_mismatched(self):
        """Should return 0 for mismatched lengths."""
        portfolio = [0.01, 0.02]
        benchmark = [0.01, 0.02, 0.03]

        ir = self.calc.calculate_information_ratio(portfolio, benchmark)
        self.assertEqual(ir, 0.0)

    def test_calculate_comprehensive_metrics(self):
        """Should calculate comprehensive set of metrics."""
        returns = [0.01, 0.02, -0.01, 0.03, -0.02, 0.01, 0.00, 0.02]
        values = [100, 101, 103, 102, 105, 103, 104, 104, 106]

        metrics = self.calc.calculate_comprehensive_metrics(returns, values)

        # Check all metrics are present
        self.assertIn('volatility', metrics)
        self.assertIn('sharpe_ratio', metrics)
        self.assertIn('sortino_ratio', metrics)
        self.assertIn('max_drawdown', metrics)
        self.assertIn('var_95', metrics)
        self.assertIn('cvar_95', metrics)

        # Check metrics are reasonable
        self.assertGreater(metrics['volatility'], 0)
        self.assertIsInstance(metrics['sharpe_ratio'], float)
        self.assertGreaterEqual(metrics['max_drawdown'], 0)

    def test_calculate_comprehensive_metrics_with_benchmark(self):
        """Should include beta and IR when benchmark provided."""
        returns = [0.01, 0.02, -0.01, 0.03]
        values = [100, 101, 103, 102, 105]
        benchmark_returns = [0.01, 0.015, -0.005, 0.025]

        metrics = self.calc.calculate_comprehensive_metrics(
            returns, values, benchmark_returns
        )

        # Should have benchmark metrics
        self.assertIn('beta', metrics)
        self.assertIn('information_ratio', metrics)
        self.assertIsInstance(metrics['beta'], float)
        self.assertIsInstance(metrics['information_ratio'], float)

    def test_repr(self):
        """Should have meaningful string representation."""
        repr_str = repr(self.calc)
        self.assertIn('RiskCalculator', repr_str)
        self.assertIn('0.02', repr_str)  # Risk-free rate


if __name__ == '__main__':
    unittest.main()
