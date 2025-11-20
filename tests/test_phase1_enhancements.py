"""
Tests for Phase 1 enhancements.

Tests the new components added in Phase 1:
- Modular cost components
- Discrete allocation converter
- Enhanced risk metrics (CDaR, Ulcer Index, Omega, Calmar)
"""

import unittest
from datetime import date, timedelta


class TestCostComponents(unittest.TestCase):
    """Test modular cost components."""

    def setUp(self):
        """Set up test fixtures."""
        try:
            from stocksimulator.costs import (
                TransactionCost,
                HoldingCost,
                LeveragedETFCost
            )
            self.costs_available = True
            self.TransactionCost = TransactionCost
            self.HoldingCost = HoldingCost
            self.LeveragedETFCost = LeveragedETFCost
        except ImportError:
            self.costs_available = False
            self.skipTest("Cost components not available")

    def test_transaction_cost_basic(self):
        """Test basic transaction cost calculation."""
        cost_model = self.TransactionCost(base_bps=2.0)

        # Buy 100 shares at $100
        trades = {'SPY': 100.0}
        positions = {}
        prices = {'SPY': 100.0}
        current_date = date.today()

        cost = cost_model.calculate(trades, positions, prices, current_date)

        # 100 shares * $100 = $10,000 trade value
        # 2 bps = 0.02% = $2
        self.assertAlmostEqual(cost, 2.0, places=2)

    def test_transaction_cost_market_impact(self):
        """Test transaction cost with market impact."""
        cost_model = self.TransactionCost(base_bps=2.0, market_impact_factor=0.1)

        trades = {'SPY': 1000.0}  # Larger trade
        positions = {}
        prices = {'SPY': 100.0}
        current_date = date.today()

        cost = cost_model.calculate(trades, positions, prices, current_date)

        # Base cost: 1000 * 100 * 0.0002 = $20
        # Market impact: 0.1 * sqrt(100000) = 0.1 * 316.23 = $31.62
        # Total: $51.62
        self.assertGreater(cost, 20.0)  # Should be more than base cost
        self.assertAlmostEqual(cost, 51.62, places=0)

    def test_holding_cost(self):
        """Test holding cost calculation."""
        cost_model = self.HoldingCost(annual_rate=0.001)  # 0.1% per year

        trades = {}
        positions = {'SPY': 100.0}  # Hold 100 shares
        prices = {'SPY': 100.0}
        current_date = date.today()

        cost = cost_model.calculate(trades, positions, prices, current_date)

        # Position value: 100 * $100 = $10,000
        # Daily rate: 0.001 / 252 = 0.000003968
        # Daily cost: $10,000 * 0.000003968 = $0.0397
        self.assertAlmostEqual(cost, 0.0397, places=3)

    def test_leveraged_etf_cost_detection(self):
        """Test leveraged ETF detection."""
        cost_model = self.LeveragedETFCost()

        # Test various leveraged symbols
        self.assertTrue(cost_model._is_leveraged('SPY_2X'))
        self.assertTrue(cost_model._is_leveraged('UPRO'))
        self.assertTrue(cost_model._is_leveraged('TQQQ'))
        self.assertTrue(cost_model._is_leveraged('SSO'))

        # Test non-leveraged symbols
        self.assertFalse(cost_model._is_leveraged('SPY'))
        self.assertFalse(cost_model._is_leveraged('QQQ'))
        self.assertFalse(cost_model._is_leveraged('AGG'))

    def test_leveraged_etf_cost_era_specific(self):
        """Test era-specific leveraged ETF costs."""
        cost_model = self.LeveragedETFCost(ter=0.006, base_excess_cost=0.015)

        # Test different eras
        # 2008 (ZIRP era) - should use 0.008 excess cost
        date_2008 = date(2008, 6, 1)
        excess_2008 = cost_model._get_excess_cost_for_date(date_2008)
        self.assertEqual(excess_2008, 0.008)

        # 2022 (high rate era) - should use 0.020 excess cost
        date_2022 = date(2022, 6, 1)
        excess_2022 = cost_model._get_excess_cost_for_date(date_2022)
        self.assertEqual(excess_2022, 0.020)

        # 1985 (Volcker era) - should use 0.025 excess cost
        date_1985 = date(1985, 6, 1)
        excess_1985 = cost_model._get_excess_cost_for_date(date_1985)
        self.assertEqual(excess_1985, 0.025)

    def test_leveraged_etf_cost_calculation(self):
        """Test leveraged ETF cost calculation."""
        cost_model = self.LeveragedETFCost(ter=0.006, base_excess_cost=0.015)

        trades = {}
        positions = {'UPRO': 100.0}  # Leveraged position
        prices = {'UPRO': 50.0}
        current_date = date(2020, 6, 1)  # 2016-2021 era (0.012 excess)

        cost = cost_model.calculate(trades, positions, prices, current_date)

        # Position value: 100 * $50 = $5,000
        # Total annual cost: 0.006 + 0.012 = 0.018 (1.8%)
        # Daily cost: 0.018 / 252 = 0.0000714
        # Daily cost in $: $5,000 * 0.0000714 = $0.357
        self.assertAlmostEqual(cost, 0.357, places=2)


class TestDiscreteAllocator(unittest.TestCase):
    """Test discrete allocation converter."""

    def setUp(self):
        """Set up test fixtures."""
        try:
            from stocksimulator.optimization.discrete_allocation import DiscreteAllocator
            self.DiscreteAllocator = DiscreteAllocator
            self.allocator_available = True
        except ImportError:
            self.allocator_available = False
            self.skipTest("DiscreteAllocator not available")

    def test_fractional_allocation(self):
        """Test fractional share allocation."""
        allocator = self.DiscreteAllocator(allow_fractional=True)

        target_weights = {'SPY': 60.0, 'AGG': 40.0}
        prices = {'SPY': 450.0, 'AGG': 105.0}
        capital = 100000.0

        shares, remaining = allocator.allocate(target_weights, prices, capital)

        # SPY: 60% of $100k = $60k / $450 = 133.33 shares
        # AGG: 40% of $100k = $40k / $105 = 380.95 shares
        self.assertAlmostEqual(shares['SPY'], 133.33, places=1)
        self.assertAlmostEqual(shares['AGG'], 380.95, places=1)
        self.assertAlmostEqual(remaining, 0.0, places=2)

    def test_discrete_greedy_allocation(self):
        """Test discrete (whole shares) allocation with greedy algorithm."""
        allocator = self.DiscreteAllocator(allow_fractional=False)

        target_weights = {'SPY': 60.0, 'AGG': 25.0, 'GLD': 15.0}
        prices = {'SPY': 450.0, 'AGG': 105.5, 'GLD': 180.0}
        capital = 100000.0

        shares, remaining = allocator.allocate(
            target_weights, prices, capital, method='greedy'
        )

        # Should get whole shares only
        for symbol, share_count in shares.items():
            self.assertEqual(share_count, int(share_count))

        # Should use most of the capital
        used_capital = sum(shares[s] * prices[s] for s in shares.keys())
        self.assertGreater(used_capital, capital * 0.98)  # At least 98% deployed

        # Remaining cash should be positive and small
        self.assertGreater(remaining, 0)
        self.assertLess(remaining, max(prices.values()))

    def test_tracking_error(self):
        """Test tracking error calculation."""
        allocator = self.DiscreteAllocator(allow_fractional=False)

        target_weights = {'SPY': 60.0, 'AGG': 40.0}
        prices = {'SPY': 450.0, 'AGG': 105.0}
        capital = 10000.0  # Smaller capital = more tracking error

        shares, _ = allocator.allocate(target_weights, prices, capital)

        tracking_error = allocator.calculate_tracking_error(
            shares, target_weights, prices
        )

        # With small capital, tracking error should be non-zero but reasonable
        self.assertGreater(tracking_error, 0)
        self.assertLess(tracking_error, 10)  # Should be < 10%

    def test_get_actual_weights(self):
        """Test actual weight calculation."""
        allocator = self.DiscreteAllocator()

        allocations = {'SPY': 100, 'AGG': 200}
        prices = {'SPY': 450.0, 'AGG': 105.0}

        # SPY: 100 * 450 = $45,000
        # AGG: 200 * 105 = $21,000
        # Total: $66,000
        # SPY weight: 45/66 = 68.18%
        # AGG weight: 21/66 = 31.82%

        weights = allocator.get_actual_weights(allocations, prices)

        self.assertAlmostEqual(weights['SPY'], 68.18, places=1)
        self.assertAlmostEqual(weights['AGG'], 31.82, places=1)


class TestEnhancedRiskMetrics(unittest.TestCase):
    """Test enhanced risk metrics."""

    def setUp(self):
        """Set up test fixtures."""
        from stocksimulator.core.risk_calculator import RiskCalculator
        self.calculator = RiskCalculator()

    def test_cdar_calculation(self):
        """Test CDaR (Conditional Drawdown at Risk) calculation."""
        # Create a portfolio with drawdowns
        values = [100, 105, 110, 95, 90, 85, 95, 100, 105, 98, 95, 100]

        cdar = self.calculator.calculate_cdar(values, confidence_level=0.95)

        # Should be positive (represents average of worst drawdowns)
        self.assertGreater(cdar, 0)
        # Should be less than max drawdown
        max_dd = self.calculator.calculate_max_drawdown(values)
        self.assertLessEqual(cdar, max_dd)

    def test_ulcer_index(self):
        """Test Ulcer Index calculation."""
        # Create portfolio with prolonged drawdown
        values = [100, 99, 98, 97, 96, 95, 96, 97, 98, 99, 100]

        ulcer = self.calculator.calculate_ulcer_index(values)

        # Should be positive
        self.assertGreater(ulcer, 0)
        # For shallow but prolonged drawdown, should be moderate
        self.assertLess(ulcer, 10)

    def test_omega_ratio(self):
        """Test Omega Ratio calculation."""
        # Create returns with more gains than losses
        returns = [0.01, 0.02, -0.005, 0.015, 0.01, -0.01, 0.02, 0.01]

        omega = self.calculator.calculate_omega_ratio(returns, threshold=0.0)

        # Should be > 1 for positive returns
        self.assertGreater(omega, 1.0)

        # Test with all positive returns
        positive_returns = [0.01, 0.02, 0.01, 0.015]
        omega_positive = self.calculator.calculate_omega_ratio(positive_returns)
        self.assertEqual(omega_positive, float('inf'))  # No losses

    def test_calmar_ratio(self):
        """Test Calmar Ratio calculation."""
        # Create returns and values
        returns = [0.001] * 252  # ~27% annual return (compounded)
        values = [100]
        for r in returns:
            values.append(values[-1] * (1 + r))

        # Induce a drawdown
        values[100:150] = [values[100] * 0.9] * 50  # 10% drawdown

        calmar = self.calculator.calculate_calmar_ratio(returns, values)

        # Should be positive
        self.assertGreater(calmar, 0)
        # Should be reasonable (return / max DD)
        self.assertLess(calmar, 100)

    def test_comprehensive_metrics_includes_new_metrics(self):
        """Test that comprehensive metrics includes Phase 1 enhancements."""
        returns = [0.001, -0.002, 0.003, -0.001, 0.002] * 50
        values = [100]
        for r in returns:
            values.append(values[-1] * (1 + r))

        metrics = self.calculator.calculate_comprehensive_metrics(returns, values)

        # Check that new metrics are included
        self.assertIn('cdar_95', metrics)
        self.assertIn('ulcer_index', metrics)
        self.assertIn('omega_ratio', metrics)
        self.assertIn('calmar_ratio', metrics)

        # Check that all are calculated (not None or 0)
        self.assertIsNotNone(metrics['cdar_95'])
        self.assertIsNotNone(metrics['ulcer_index'])
        self.assertIsNotNone(metrics['omega_ratio'])
        self.assertIsNotNone(metrics['calmar_ratio'])


class TestBacktesterWithModularCosts(unittest.TestCase):
    """Test Backtester with modular cost components."""

    def setUp(self):
        """Set up test fixtures."""
        from stocksimulator.core.backtester import Backtester

        try:
            from stocksimulator.costs import TransactionCost, LeveragedETFCost
            self.costs_available = True
            self.TransactionCost = TransactionCost
            self.LeveragedETFCost = LeveragedETFCost
        except ImportError:
            self.costs_available = False

        self.Backtester = Backtester

    def test_backtester_legacy_init(self):
        """Test backward compatibility with legacy initialization."""
        backtester = self.Backtester(
            initial_cash=100000,
            transaction_cost_bps=2.0
        )

        self.assertEqual(backtester.initial_cash, 100000)
        self.assertEqual(backtester.transaction_cost_bps, 2.0)

    def test_backtester_modular_costs_init(self):
        """Test initialization with modular costs."""
        if not self.costs_available:
            self.skipTest("Cost components not available")

        costs = [
            self.TransactionCost(base_bps=2.0),
            self.LeveragedETFCost()
        ]

        backtester = self.Backtester(
            initial_cash=100000,
            costs=costs
        )

        self.assertEqual(len(backtester.costs), 2)
        self.assertTrue(backtester.use_modular_costs)

    def test_calculate_costs_method(self):
        """Test cost calculation method."""
        if not self.costs_available:
            self.skipTest("Cost components not available")

        costs = [self.TransactionCost(base_bps=2.0)]
        backtester = self.Backtester(initial_cash=100000, costs=costs)

        trades = {'SPY': 100.0}
        positions = {}
        prices = {'SPY': 100.0}
        current_date = date.today()

        total_cost = backtester.calculate_costs(trades, positions, prices, current_date)

        # Should match TransactionCost calculation
        self.assertAlmostEqual(total_cost, 2.0, places=2)


if __name__ == '__main__':
    unittest.main()
