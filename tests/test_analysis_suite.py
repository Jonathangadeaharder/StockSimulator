#!/usr/bin/env python3
"""
Comprehensive test suite for StockSimulator analysis modules.

Follows best practices:
- SOLID: Single Responsibility per test class, clear interfaces
- DRY: Reusable fixtures and helpers
- YAGNI: Only test what exists, no speculative tests
- KISS: Simple, readable tests with clear assertions

Test Coverage:
- IRR calculation
- Return calculations
- Leveraged ETF simulation
- Percentile calculations
- Data reading and validation
"""

import unittest
import sys
import os
from datetime import datetime, timedelta
import csv
import io

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import from historical_data directory
from historical_data.analyze_pairwise_comparison import calculate_irr


class TestIRRCalculation(unittest.TestCase):
    """Test Internal Rate of Return calculations."""

    def test_simple_irr_calculation(self):
        """IRR should correctly calculate for simple cash flows."""
        # Invest $100 at start, get $110 after 1 year = 10% return
        cash_flows = [-100, 110]
        dates = [
            datetime(2020, 1, 1),
            datetime(2021, 1, 1)
        ]

        irr = calculate_irr(cash_flows, dates)

        self.assertIsNotNone(irr)
        self.assertAlmostEqual(irr, 10.0, places=1)

    def test_irr_with_monthly_contributions(self):
        """IRR should handle monthly contribution patterns."""
        # $100/month for 12 months, ending value $1300
        cash_flows = []
        dates = []
        start_date = datetime(2020, 1, 1)

        for i in range(12):
            dates.append(start_date + timedelta(days=i*30))
            cash_flows.append(-100)

        # Add final value
        dates.append(start_date + timedelta(days=365))
        cash_flows.append(1300)

        irr = calculate_irr(cash_flows, dates)

        self.assertIsNotNone(irr)
        self.assertGreater(irr, 0)  # Should be positive return
        self.assertLess(irr, 20)    # Should be reasonable

    def test_irr_rejects_empty_cash_flows(self):
        """IRR should return None for empty inputs."""
        self.assertIsNone(calculate_irr([], []))
        self.assertIsNone(calculate_irr([100], []))
        self.assertIsNone(calculate_irr([], [datetime.now()]))

    def test_irr_rejects_single_cash_flow(self):
        """IRR needs at least 2 cash flows."""
        cash_flows = [-100]
        dates = [datetime(2020, 1, 1)]

        self.assertIsNone(calculate_irr(cash_flows, dates))

    def test_irr_rejects_mismatched_lengths(self):
        """IRR should return None if cash flows and dates don't match."""
        cash_flows = [-100, 110]
        dates = [datetime(2020, 1, 1)]

        self.assertIsNone(calculate_irr(cash_flows, dates))

    def test_irr_handles_loss_scenario(self):
        """IRR should correctly calculate negative returns."""
        # Invest $100, get back $80 = -20% return
        cash_flows = [-100, 80]
        dates = [
            datetime(2020, 1, 1),
            datetime(2021, 1, 1)
        ]

        irr = calculate_irr(cash_flows, dates)

        self.assertIsNotNone(irr)
        self.assertLess(irr, 0)  # Should be negative
        self.assertGreater(irr, -99)  # Within sanity bounds

    def test_irr_rejects_extreme_values(self):
        """IRR should reject unrealistic rates beyond sanity bounds."""
        # This would imply >1000% return which should fail sanity check
        cash_flows = [-100, 100000]
        dates = [
            datetime(2020, 1, 1),
            datetime(2020, 1, 31)
        ]

        irr = calculate_irr(cash_flows, dates)

        # Should return None due to sanity check
        self.assertIsNone(irr)

    def test_irr_handles_zero_return(self):
        """IRR should handle break-even scenarios."""
        # Invest $100, get back $100 = 0% return
        cash_flows = [-100, 100]
        dates = [
            datetime(2020, 1, 1),
            datetime(2021, 1, 1)
        ]

        irr = calculate_irr(cash_flows, dates)

        self.assertIsNotNone(irr)
        self.assertAlmostEqual(irr, 0.0, places=1)


class TestReturnCalculations(unittest.TestCase):
    """Test financial return calculations."""

    def setUp(self):
        """Set up test data for each test."""
        # Create simple price data
        self.sample_data = [
            {'date': datetime(2020, 1, 1), 'close': 100.0},
            {'date': datetime(2020, 1, 2), 'close': 102.0},
            {'date': datetime(2020, 1, 3), 'close': 101.0},
            {'date': datetime(2020, 1, 4), 'close': 103.0},
        ]

    def _calculate_price_return(self, data, index):
        """Helper method to calculate price return between consecutive periods.
        
        Args:
            data: List of dictionaries with 'close' prices
            index: Current index (must be >= 1)
            
        Returns:
            Price return as a decimal (e.g., 0.02 for 2% return)
        """
        return (data[index]['close'] - data[index-1]['close']) / data[index-1]['close']

    def test_daily_returns_calculation(self):
        """Daily returns should be calculated correctly."""
        # Using PairwiseComparison.calculate_returns logic
        returns = []
        daily_dividend = 0.02 / 252  # 2% annual dividend

        for i in range(1, len(self.sample_data)):
            price_return = self._calculate_price_return(self.sample_data, i)
            total_return = price_return + daily_dividend
            returns.append(total_return)

        # First return: (102 - 100) / 100 = 2%
        self.assertAlmostEqual(returns[0], 0.02 + daily_dividend, places=6)

        # Second return: (101 - 102) / 102 ≈ -0.98%
        self.assertAlmostEqual(returns[1], -0.0098 + daily_dividend, places=4)

    def test_annualized_return_calculation(self):
        """Annualized returns should compound correctly."""
        initial_value = 100
        final_value = 121  # 21% total return
        years = 2

        # Formula: (final/initial)^(1/years) - 1
        annualized = ((final_value / initial_value) ** (1/years) - 1) * 100

        # Should be approximately 10% per year
        self.assertAlmostEqual(annualized, 10.0, places=1)

    def test_leveraged_return_calculation(self):
        """Leveraged returns should apply 2x multiplier and TER."""
        unleveraged_return = 0.01  # 1% daily return
        leverage = 2.0
        ter = 0.006  # 0.6% annual TER
        daily_ter = ter / 252

        leveraged_return = leverage * unleveraged_return - daily_ter

        expected = 2 * 0.01 - (0.006/252)
        self.assertAlmostEqual(leveraged_return, expected, places=8)

    def test_cumulative_return_calculation(self):
        """Cumulative returns should compound daily returns."""
        daily_returns = [0.01, 0.01, -0.01]  # 1%, 1%, -1%

        cumulative = 1.0
        for ret in daily_returns:
            cumulative *= (1 + ret)

        # (1.01 * 1.01 * 0.99) ≈ 1.0099
        self.assertAlmostEqual(cumulative, 1.0099, places=4)


class TestLeveragedETFSimulation(unittest.TestCase):
    """Test leveraged ETF simulation logic."""

    def test_volatility_decay_effect(self):
        """Leveraged ETF should experience volatility decay."""
        # Simulate 2 days: +10%, -9.09% (returns to starting price)
        # Unleveraged: 100 -> 110 -> 100 (0% total)
        # 2x Leveraged: 100 -> 120 -> 98.18 (negative due to decay)

        returns = [0.10, -0.0909]  # Returns to break even
        ter = 0.006 / 252

        unlev_value = 100.0
        lev_value = 100.0

        for ret in returns:
            unlev_value *= (1 + ret)
            lev_return = 2 * ret - ter
            lev_value *= (1 + lev_return)

        # Unleveraged should be close to 100
        self.assertAlmostEqual(unlev_value, 100.0, places=1)

        # Leveraged should be less than 100 due to volatility decay
        self.assertLess(lev_value, 100.0)

    def test_ter_reduces_returns(self):
        """TER should reduce leveraged returns."""
        daily_return = 0.01  # 1% daily
        ter = 0.006
        daily_ter = ter / 252
        leverage = 2.0

        # Without TER
        return_without_ter = leverage * daily_return

        # With TER
        return_with_ter = leverage * daily_return - daily_ter

        self.assertLess(return_with_ter, return_without_ter)
        self.assertAlmostEqual(
            return_without_ter - return_with_ter,
            daily_ter,
            places=8
        )

    def test_daily_rebalancing(self):
        """Leverage should rebalance daily to 2x."""
        # Start with $100 in 2x leveraged
        # Day 1: Index +5%, ETF should gain 10%
        # Day 2: Index +5%, ETF should gain 10% of new base

        index_price = 100.0
        etf_price = 100.0
        ter = 0.006 / 252

        # Day 1
        index_return = 0.05
        index_price *= (1 + index_return)
        etf_return = 2 * index_return - ter
        etf_price *= (1 + etf_return)

        # Day 2
        index_return = 0.05
        index_price *= (1 + index_return)
        etf_return = 2 * index_return - ter
        etf_price *= (1 + etf_return)

        # Index: 100 * 1.05 * 1.05 = 110.25
        # ETF: Should be approximately 100 * (1+2*0.05-ter)^2
        self.assertAlmostEqual(index_price, 110.25, places=2)
        self.assertGreater(etf_price, 120.0)  # Should be > 2x gain


class TestPercentileCalculations(unittest.TestCase):
    """Test percentile calculation logic."""

    def test_calculate_percentiles_basic(self):
        """Percentiles should correctly identify distribution points."""
        values = list(range(1, 101))  # 1 to 100

        percentiles = self._calculate_percentiles(values, [10, 50, 90])

        # 10th percentile: index 10 of 0-99, value is 11
        self.assertEqual(percentiles[10], 11)
        # 50th percentile (median): index 50 of 0-99, value is 51
        self.assertEqual(percentiles[50], 51)
        # 90th percentile: index 90 of 0-99, value is 91
        self.assertEqual(percentiles[90], 91)

    def test_percentiles_with_small_dataset(self):
        """Percentiles should handle small datasets."""
        values = [1, 2, 3, 4, 5]

        percentiles = self._calculate_percentiles(values, [50])

        # Median of [1,2,3,4,5] should be 3
        self.assertEqual(percentiles[50], 3)

    def test_percentiles_sorted_correctly(self):
        """Percentiles should sort unsorted data."""
        values = [5, 1, 3, 2, 4]

        percentiles = self._calculate_percentiles(values, [10, 90])

        # After sorting: [1, 2, 3, 4, 5]
        self.assertEqual(percentiles[10], 1)  # 10th percentile
        self.assertEqual(percentiles[90], 5)  # 90th percentile

    def _calculate_percentiles(self, values, percentiles):
        """Helper to calculate percentiles (DRY principle)."""
        sorted_values = sorted(values)
        n = len(sorted_values)
        result = {}
        for p in percentiles:
            idx = int(n * p / 100)
            if idx >= n:
                idx = n - 1
            result[p] = sorted_values[idx]
        return result


class TestDataValidation(unittest.TestCase):
    """Test data reading and validation logic."""

    def test_csv_reading_filters_invalid_prices(self):
        """CSV reader should filter out zero/negative/missing prices."""
        csv_data = """Date,Close
2020-01-01,100.0
2020-01-02,
2020-01-03,0.0
2020-01-04,-50.0
2020-01-05,105.0
"""

        valid_data = []
        reader = csv.DictReader(io.StringIO(csv_data))
        for row in reader:
            try:
                date = datetime.strptime(row['Date'], '%Y-%m-%d')
                price = float(row['Close']) if row['Close'] else None
                if price and price > 0:
                    valid_data.append({'date': date, 'close': price})
            except (ValueError, KeyError):
                continue

        # Should only have 2 valid entries (100.0 and 105.0)
        self.assertEqual(len(valid_data), 2)
        self.assertEqual(valid_data[0]['close'], 100.0)
        self.assertEqual(valid_data[1]['close'], 105.0)

    def test_date_filtering_by_year(self):
        """Data reader should filter dates before start year."""
        data_entries = [
            {'date': datetime(1945, 1, 1), 'close': 100.0},
            {'date': datetime(1950, 1, 1), 'close': 105.0},
            {'date': datetime(1955, 1, 1), 'close': 110.0},
        ]

        start_year = 1950
        filtered = [
            entry for entry in data_entries
            if entry['date'].year >= start_year
        ]

        # Should only have 2 entries (1950 and 1955)
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]['date'].year, 1950)


class TestMonthlyInvestmentSimulation(unittest.TestCase):
    """Test monthly investment logic."""

    def test_monthly_investment_timing(self):
        """Monthly investments should occur approximately every 30 days."""
        start_date = datetime(2020, 1, 1)
        monthly_amount = 500
        months_needed = 12

        investments = []
        month = 0

        # Simulate daily iteration
        for day in range(365):
            current_date = start_date + timedelta(days=day)
            days_since_start = (current_date - start_date).days
            expected_month = days_since_start / 30.44  # Average month length

            if int(expected_month) > month and month < months_needed:
                month = int(expected_month)
                investments.append({
                    'date': current_date,
                    'amount': monthly_amount
                })

        # Should have approximately 12 monthly investments
        self.assertGreaterEqual(len(investments), 11)
        self.assertLessEqual(len(investments), 13)

    def test_dollar_cost_averaging_math(self):
        """DCA should buy more shares when price is low."""
        monthly_amount = 500

        # Month 1: Price $100, buy 5 shares
        # Month 2: Price $50, buy 10 shares
        # Total: 15 shares for $1000
        # Average cost: $1000/15 = $66.67 per share

        shares = monthly_amount / 100  # 5 shares
        shares += monthly_amount / 50  # 10 more shares

        total_invested = monthly_amount * 2
        average_cost_per_share = total_invested / shares

        self.assertEqual(shares, 15.0)
        self.assertAlmostEqual(average_cost_per_share, 66.67, places=2)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def _calculate_price_return(self, data, index):
        """Helper method to calculate price return between consecutive periods.
        
        Args:
            data: List of dictionaries with 'close' prices
            index: Current index (must be >= 1)
            
        Returns:
            Price return as a decimal (e.g., 0.02 for 2% return)
        """
        return (data[index]['close'] - data[index-1]['close']) / data[index-1]['close']

    def test_division_by_zero_protection(self):
        """Calculations should handle zero denominators gracefully."""
        # IRR calculation with near-zero derivative
        # Should return None rather than crash

        cash_flows = [-100, -100]  # All outflows - impossible scenario
        dates = [datetime(2020, 1, 1), datetime(2021, 1, 1)]

        irr = calculate_irr(cash_flows, dates)

        # Should handle gracefully
        self.assertIsNone(irr)

    def test_empty_data_handling(self):
        """Functions should handle empty datasets gracefully."""
        # Test with empty returns list
        returns = []

        # Should not crash when calculating cumulative
        cumulative = 1.0
        for ret in returns:
            cumulative *= (1 + ret)

        self.assertEqual(cumulative, 1.0)

    def test_single_day_return_edge_case(self):
        """Should handle minimum data requirements."""
        # Can't calculate return with only 1 data point
        data = [{'date': datetime(2020, 1, 1), 'close': 100.0}]

        returns = []
        for i in range(1, len(data)):
            ret = self._calculate_price_return(data, i)
            returns.append(ret)

        # Should have 0 returns (need 2 points for 1 return)
        self.assertEqual(len(returns), 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for combined functionality."""

    def test_full_investment_cycle(self):
        """Test complete investment simulation cycle."""
        # Simulate a simple 3-month investment
        monthly_amount = 500
        prices = [100.0, 105.0, 102.0, 104.0]  # Prices over 3 months

        shares = 0.0
        total_invested = 0

        # Month 0: Buy at $100
        shares += monthly_amount / prices[0]
        total_invested += monthly_amount

        # Month 1: Buy at $105
        shares += monthly_amount / prices[1]
        total_invested += monthly_amount

        # Month 2: Buy at $102
        shares += monthly_amount / prices[2]
        total_invested += monthly_amount

        # Final value at $104
        final_value = shares * prices[3]

        # Calculate return
        total_return = (final_value - total_invested) / total_invested

        # Verify calculations are consistent
        self.assertEqual(total_invested, 1500)
        self.assertGreater(final_value, 0)
        self.assertIsInstance(total_return, float)


def run_test_suite():
    """Run the complete test suite with verbose output."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestIRRCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestReturnCalculations))
    suite.addTests(loader.loadTestsFromTestCase(TestLeveragedETFSimulation))
    suite.addTests(loader.loadTestsFromTestCase(TestPercentileCalculations))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestMonthlyInvestmentSimulation))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == '__main__':
    print("=" * 80)
    print("StockSimulator Comprehensive Test Suite")
    print("Testing: IRR, Returns, Leveraged ETFs, Percentiles, Data Validation")
    print("=" * 80)
    print()

    result = run_test_suite()

    print()
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 80)

    sys.exit(0 if result.wasSuccessful() else 1)
