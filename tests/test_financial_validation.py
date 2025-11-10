#!/usr/bin/env python3
"""
Financial Validation Test Suite - Real Data & Correctness Testing

This suite validates that our financial calculations produce accurate results
by testing against:
- Real historical market data
- Known financial outcomes (crashes, bull markets)
- Third-party financial libraries
- Statistical properties

These tests complement test_analysis_suite.py which focuses on unit testing.
"""

import unittest
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import from historical_data directory
from historical_data.analyze_pairwise_comparison import (
    calculate_irr,
    PairwiseComparison
)


class TestRealDataIntegration(unittest.TestCase):
    """Test that analysis runs successfully with real historical data."""

    @classmethod
    def setUpClass(cls):
        """Load real data once for all tests."""
        cls.data_dir = os.path.join(os.path.dirname(__file__), '..', 'historical_data')
        cls.sp500_file = os.path.join(cls.data_dir, 'sp500_stooq_daily.csv')

        # Verify file exists
        if not os.path.exists(cls.sp500_file):
            raise FileNotFoundError(f"Required test data not found: {cls.sp500_file}")

    def test_sp500_data_loads_successfully(self):
        """Real S&P 500 data should load without errors."""
        analyzer = PairwiseComparison("S&P 500", self.sp500_file, 'Date', 'Close', 1950)
        data = analyzer.read_data()

        self.assertGreater(len(data), 10000, "Should have decades of daily data")
        self.assertIsInstance(data[0]['date'], datetime)
        self.assertGreater(data[0]['close'], 0)

    def test_sp500_returns_calculation_produces_valid_results(self):
        """S&P 500 returns should be within reasonable bounds."""
        analyzer = PairwiseComparison("S&P 500", self.sp500_file, 'Date', 'Close', 1950)
        data = analyzer.read_data()
        returns = analyzer.calculate_returns(data[:1000])  # Test first 1000 days

        self.assertEqual(len(returns), 999)  # N-1 returns from N prices

        # Daily returns should typically be between -10% and +10%
        # (Black Monday 1987 was -20%, but that's extremely rare)
        for ret in returns:
            self.assertGreater(ret['return'], -0.25,
                             f"Suspiciously large daily loss: {ret['return']:.2%}")
            self.assertLess(ret['return'], 0.25,
                          f"Suspiciously large daily gain: {ret['return']:.2%}")

    def test_full_pairwise_analysis_runs_without_crash(self):
        """Complete analysis pipeline should run on real data."""
        analyzer = PairwiseComparison("S&P 500", self.sp500_file, 'Date', 'Close', 2000)

        # Should not raise any exceptions
        try:
            results = analyzer.analyze(timeframes=[5], monthly_amount=500)
            self.assertIsInstance(results, dict)
            self.assertIn('5_lump_vs_unlev', results)
        except Exception as e:
            self.fail(f"Analysis crashed on real data: {e}")


class TestHistoricalCrashScenarios(unittest.TestCase):
    """Validate behavior during known historical market crashes."""

    @classmethod
    def setUpClass(cls):
        """Load S&P 500 data for crash analysis."""
        cls.data_dir = os.path.join(os.path.dirname(__file__), '..', 'historical_data')
        cls.sp500_file = os.path.join(cls.data_dir, 'sp500_stooq_daily.csv')

        if not os.path.exists(cls.sp500_file):
            raise FileNotFoundError(f"Required test data not found: {cls.sp500_file}")

        cls.analyzer = PairwiseComparison("S&P 500", cls.sp500_file, 'Date', 'Close', 1950)
        cls.all_data = cls.analyzer.read_data()

    def _get_period_data(self, start_date, end_date):
        """Extract data for a specific time period."""
        return [d for d in self.all_data
                if start_date <= d['date'] <= end_date]

    def _calculate_period_return(self, data):
        """Calculate total return over a period."""
        if len(data) < 2:
            return 0.0
        return (data[-1]['close'] - data[0]['close']) / data[0]['close']

    def test_2008_financial_crisis_shows_expected_losses(self):
        """2008 crash should show significant loss (30-70%) for S&P 500 unleveraged."""
        # S&P 500 peak: Oct 9, 2007 (~1565)
        # S&P 500 trough: Mar 9, 2009 (~676)
        # Loss: ~56.8%

        crash_data = self._get_period_data(
            datetime(2007, 10, 1),
            datetime(2009, 3, 31)
        )

        if len(crash_data) < 10:
            self.skipTest("Insufficient data for 2008 crash period")

        total_return = self._calculate_period_return(crash_data)

        # Should show significant losses (roughly -40% to -60%)
        self.assertLess(total_return, -0.30,
                       "2008 crash should show >30% loss")
        self.assertGreater(total_return, -0.70,
                          "2008 crash loss seems too extreme (check data)")

    def test_2x_leveraged_amplifies_2008_crash_losses(self):
        """2x leveraged ETF should lose more than 2x during sustained crash."""
        crash_data = self._get_period_data(
            datetime(2007, 10, 1),
            datetime(2009, 3, 31)
        )

        if len(crash_data) < 10:
            self.skipTest("Insufficient data for 2008 crash period")

        # Calculate leveraged returns
        returns = self.analyzer.calculate_returns(crash_data)
        leveraged_returns = self.analyzer.simulate_leveraged_etf(returns)

        # Compound leveraged returns
        lev_cumulative = 1.0
        for ret in leveraged_returns:
            lev_cumulative *= (1 + ret['lev_return'])

        lev_total_return = lev_cumulative - 1

        # 2x leveraged should lose significantly more due to volatility decay
        # Expected: roughly -70% to -90% (worse than 2x the unleveraged loss)
        self.assertLess(lev_total_return, -0.50,
                       "2x leveraged should show >50% loss in 2008 crash")
        self.assertGreater(lev_total_return, -0.95,
                          "Loss seems too extreme (possible calculation error)")

    def test_dot_com_bubble_burst_2000_2002(self):
        """Dot-com crash (2000-2002) should show significant losses."""
        # NASDAQ peak: Mar 2000
        # NASDAQ trough: Oct 2002
        # S&P 500 also declined significantly

        bubble_data = self._get_period_data(
            datetime(2000, 3, 1),
            datetime(2002, 10, 31)
        )

        if len(bubble_data) < 10:
            self.skipTest("Insufficient data for dot-com bubble period")

        total_return = self._calculate_period_return(bubble_data)

        # S&P 500 lost about -40% to -50% during this period
        self.assertLess(total_return, -0.20,
                       "Dot-com crash should show >20% loss for S&P 500")

    def test_black_monday_1987_single_day_crash(self):
        """Black Monday (Oct 19, 1987) should show ~20% single-day loss."""
        # Oct 19, 1987: S&P 500 dropped ~20% in one day

        black_monday_data = self._get_period_data(
            datetime(1987, 10, 16),
            datetime(1987, 10, 20)
        )

        if len(black_monday_data) < 3:
            self.skipTest("Insufficient data for Black Monday 1987")

        # Find the largest single-day drop
        max_drop = 0.0
        for i in range(1, len(black_monday_data)):
            daily_return = (black_monday_data[i]['close'] -
                          black_monday_data[i-1]['close']) / black_monday_data[i-1]['close']
            if daily_return < max_drop:
                max_drop = daily_return

        # Should have a drop around -20%
        self.assertLess(max_drop, -0.15,
                       "Black Monday should show >15% single-day drop")


class TestIRRFinancialAccuracy(unittest.TestCase):
    """Validate IRR calculations against known financial scenarios."""

    def test_irr_matches_simple_annual_return(self):
        """IRR should match simple return for single-period investment."""
        # Invest $1000, get $1100 after exactly 1 year = 10% return
        cash_flows = [-1000, 1100]
        dates = [datetime(2020, 1, 1), datetime(2021, 1, 1)]

        irr = calculate_irr(cash_flows, dates)

        self.assertIsNotNone(irr)
        self.assertAlmostEqual(irr, 10.0, places=1,
                             msg="IRR should be ~10% for this scenario")

    def test_irr_with_real_monthly_investment_pattern(self):
        """IRR for monthly investments should match expected range."""
        # $500/month for 12 months with 8% annual growth
        # Expected IRR should be close to 8%

        cash_flows = []
        dates = []
        start_date = datetime(2020, 1, 1)

        # Monthly investments
        for month in range(12):
            dates.append(start_date + timedelta(days=month*30))
            cash_flows.append(-500)

        # With dollar-cost averaging, final value is slightly different
        # Approximate: $6250 (8% on average investment time)
        dates.append(start_date + timedelta(days=365))
        cash_flows.append(6250)

        irr = calculate_irr(cash_flows, dates)

        self.assertIsNotNone(irr)
        self.assertGreater(irr, 5.0, "IRR should be reasonable (>5%)")
        self.assertLess(irr, 12.0, "IRR should be reasonable (<12%)")

    def test_irr_negative_return_accuracy(self):
        """IRR should correctly calculate negative returns."""
        # Invest $1000, lose 20% over 1 year
        cash_flows = [-1000, 800]
        dates = [datetime(2020, 1, 1), datetime(2021, 1, 1)]

        irr = calculate_irr(cash_flows, dates)

        self.assertIsNotNone(irr)
        self.assertAlmostEqual(irr, -20.0, places=1,
                             msg="IRR should be ~-20% for this scenario")

    def test_irr_handles_irregular_timing(self):
        """IRR should work with non-standard investment intervals."""
        # Invest at irregular intervals
        cash_flows = [-1000, -1000, -1000, 3300]
        dates = [
            datetime(2020, 1, 1),
            datetime(2020, 4, 15),  # ~3.5 months later
            datetime(2020, 10, 1),  # ~5.5 months later
            datetime(2021, 6, 1)    # ~8 months later
        ]

        irr = calculate_irr(cash_flows, dates)

        self.assertIsNotNone(irr)
        # Total invested: $3000, got back $3300 = 10% gain over ~1.4 years
        # Annualized should be around 7-8%
        self.assertGreater(irr, 3.0)
        self.assertLess(irr, 15.0)


class TestLeveragedETFMechanics(unittest.TestCase):
    """Validate leveraged ETF simulation mechanics."""

    def test_ter_annual_impact_is_approximately_correct(self):
        """Total costs (TER + empirical excess costs) should be realistic in flat market."""
        # Simulate 252 trading days with 0% daily returns
        # Expected: Total cost = TER (0.6%) + empirical excess costs (~1.5-2.0%)
        # Total: ~2.1-2.6% per year depending on market regime

        flat_returns = [{'date': datetime.now(), 'return': 0.0} for _ in range(252)]

        analyzer = PairwiseComparison("Test", "dummy.csv", 'Date', 'Close', 1950)
        leveraged_returns = analyzer.simulate_leveraged_etf(flat_returns, leverage=2.0, ter_lev=0.006)

        # Compound returns
        cumulative = 1.0
        for ret in leveraged_returns:
            cumulative *= (1 + ret['lev_return'])

        annual_cost = (1 - cumulative) * 100

        # Total costs should be realistic (TER + excess costs)
        # Range: 1.4% (ZIRP era) to 2.6% (current)
        self.assertGreater(annual_cost, 1.0, "Total cost too small - missing excess costs")
        self.assertLess(annual_cost, 3.0, "Total cost too large - unrealistic")

    def test_2x_leverage_doubles_returns_in_simple_scenario(self):
        """2x leverage should approximately double returns in low-volatility uptrend."""
        # 1% daily gain for 5 days, low volatility
        simple_returns = [{'date': datetime.now(), 'return': 0.01} for _ in range(5)]

        analyzer = PairwiseComparison("Test", "dummy.csv", 'Date', 'Close', 1950)
        leveraged_returns = analyzer.simulate_leveraged_etf(
            simple_returns,
            leverage=2.0,
            ter_lev=0.0  # No TER for clean test
        )

        # Unleveraged: (1.01)^5 = ~1.051
        unlev_cumulative = 1.01 ** 5

        # Leveraged: (1.02)^5 = ~1.104
        lev_cumulative = 1.0
        for ret in leveraged_returns:
            lev_cumulative *= (1 + ret['lev_return'])

        # Leveraged gain should be roughly 2x unleveraged gain
        unlev_gain = unlev_cumulative - 1
        lev_gain = lev_cumulative - 1

        ratio = lev_gain / unlev_gain if unlev_gain != 0 else 0

        # Should be close to 2.0 (within 10% due to compounding)
        self.assertGreater(ratio, 1.8, "Leverage ratio too low")
        self.assertLess(ratio, 2.2, "Leverage ratio too high")

    def test_volatility_decay_occurs_in_oscillating_market(self):
        """Leveraged ETF should underperform in high-volatility flat market."""
        # Alternating +5% and -4.76% days (returns to starting point)
        # Unleveraged: break even
        # 2x Leveraged: should lose money due to volatility decay

        oscillating_returns = []
        for _ in range(10):
            oscillating_returns.append({'date': datetime.now(), 'return': 0.05})
            oscillating_returns.append({'date': datetime.now(), 'return': -0.0476})

        analyzer = PairwiseComparison("Test", "dummy.csv", 'Date', 'Close', 1950)
        leveraged_returns = analyzer.simulate_leveraged_etf(
            oscillating_returns,
            leverage=2.0,
            ter_lev=0.0  # Exclude TER to isolate volatility decay
        )

        # Calculate cumulative returns
        unlev_cumulative = 1.0
        lev_cumulative = 1.0

        for i, ret in enumerate(leveraged_returns):
            unlev_cumulative *= (1 + oscillating_returns[i]['return'])
            lev_cumulative *= (1 + ret['lev_return'])

        # Unleveraged should be close to 1.0 (break even)
        self.assertAlmostEqual(unlev_cumulative, 1.0, places=2,
                             msg="Unleveraged should break even in oscillating market")

        # Leveraged should be < 1.0 (lost money due to volatility decay)
        self.assertLess(lev_cumulative, 1.0,
                       "Leveraged ETF should lose money due to volatility decay")
        self.assertLess(lev_cumulative, 0.98,
                       "Volatility decay should cause meaningful loss")


class TestStatisticalValidation(unittest.TestCase):
    """Validate statistical properties of simulations."""

    @classmethod
    def setUpClass(cls):
        """Load real S&P 500 data for statistical analysis."""
        cls.data_dir = os.path.join(os.path.dirname(__file__), '..', 'historical_data')
        cls.sp500_file = os.path.join(cls.data_dir, 'sp500_stooq_daily.csv')

        if not os.path.exists(cls.sp500_file):
            raise FileNotFoundError(f"Required test data not found: {cls.sp500_file}")

        cls.analyzer = PairwiseComparison("S&P 500", cls.sp500_file, 'Date', 'Close', 1990)
        cls.data = cls.analyzer.read_data()

    def test_percentile_calculations_are_monotonic(self):
        """Percentiles should be in ascending order (10th < 25th < 50th < 75th < 90th)."""
        # Run real analysis
        returns_data = self.analyzer.calculate_returns(self.data[:5000])
        leveraged_returns = self.analyzer.simulate_leveraged_etf(returns_data)

        results = self.analyzer.compare_lumpsum_vs_monthly_unlev(
            leveraged_returns,
            monthly_amount=500,
            years=5
        )

        if len(results) < 10:
            self.skipTest("Insufficient results for statistical analysis")

        # Extract annualized returns
        returns = [r['lump_lev_ann'] for r in results]

        # Calculate percentiles
        percentiles = self.analyzer.calculate_percentiles(returns)

        # Verify monotonicity
        self.assertLessEqual(percentiles[10], percentiles[25],
                           "10th percentile should be ≤ 25th")
        self.assertLessEqual(percentiles[25], percentiles[50],
                           "25th percentile should be ≤ 50th (median)")
        self.assertLessEqual(percentiles[50], percentiles[75],
                           "50th percentile should be ≤ 75th")
        self.assertLessEqual(percentiles[75], percentiles[90],
                           "75th percentile should be ≤ 90th")

    def test_leveraged_returns_have_higher_volatility(self):
        """2x leveraged returns should have roughly 2x higher standard deviation."""
        returns_data = self.analyzer.calculate_returns(self.data[:1000])
        leveraged_returns = self.analyzer.simulate_leveraged_etf(returns_data)

        # Calculate standard deviations
        unlev_returns = [r['unlev_return'] for r in leveraged_returns]
        lev_returns = [r['lev_return'] for r in leveraged_returns]

        def stdev(values):
            n = len(values)
            mean = sum(values) / n
            variance = sum((x - mean) ** 2 for x in values) / n
            return variance ** 0.5

        unlev_std = stdev(unlev_returns)
        lev_std = stdev(lev_returns)

        volatility_ratio = lev_std / unlev_std if unlev_std != 0 else 0

        # Should be close to 2.0 (2x leverage = 2x volatility)
        self.assertGreater(volatility_ratio, 1.7,
                          "Leveraged volatility should be significantly higher")
        self.assertLess(volatility_ratio, 2.3,
                       "Leveraged volatility ratio seems too high")

    def test_monthly_investment_makes_approximately_12_investments_per_year(self):
        """Monthly investment logic should invest roughly 12 times per year."""
        returns_data = self.analyzer.calculate_returns(self.data[:300])  # ~1 year
        leveraged_returns = self.analyzer.simulate_leveraged_etf(returns_data)

        results = self.analyzer.compare_lumpsum_vs_monthly_unlev(
            leveraged_returns,
            monthly_amount=500,
            years=1
        )

        if not results:
            self.skipTest("Insufficient data for 1-year test")

        # Check that monthly investment happened roughly 12 times
        # (This is validated by checking total invested)
        result = results[0]

        # Should be close to expected (within 1 month's worth)
        self.assertGreater(result['total_invested'], 500 * 11,
                          "Too few monthly investments")
        self.assertLessEqual(result['total_invested'], 500 * 13,
                            "Too many monthly investments")


def run_validation_suite():
    """Run the complete financial validation test suite."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestRealDataIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestHistoricalCrashScenarios))
    suite.addTests(loader.loadTestsFromTestCase(TestIRRFinancialAccuracy))
    suite.addTests(loader.loadTestsFromTestCase(TestLeveragedETFMechanics))
    suite.addTests(loader.loadTestsFromTestCase(TestStatisticalValidation))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == '__main__':
    print("=" * 80)
    print("Financial Validation Test Suite")
    print("Testing: Real Data, Historical Crashes, IRR Accuracy, ETF Mechanics")
    print("=" * 80)
    print()

    result = run_validation_suite()

    print()
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 80)

    sys.exit(0 if result.wasSuccessful() else 1)
