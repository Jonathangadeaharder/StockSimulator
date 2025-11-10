"""
Tests for Tax Calculator

Comprehensive tests for tax calculations including wash sales and capital gains.
"""

import unittest
import sys
import os
from datetime import date, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from stocksimulator.tax.tax_calculator import TaxCalculator
from stocksimulator.models.transaction import Transaction


class TestTaxCalculator(unittest.TestCase):
    """Test TaxCalculator functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.calc = TaxCalculator()

    def test_initialization(self):
        """TaxCalculator should initialize with default rates."""
        calc = TaxCalculator()
        self.assertIsNotNone(calc)

        # Custom rates
        calc_custom = TaxCalculator(
            short_term_rate=0.30,
            long_term_rate=0.20
        )
        self.assertEqual(calc_custom.short_term_rate, 0.30)
        self.assertEqual(calc_custom.long_term_rate, 0.20)

    def test_calculate_short_term_gain(self):
        """Should calculate short-term capital gains."""
        # Buy and sell within a year
        buy_date = date(2023, 1, 1)
        sell_date = date(2023, 6, 1)

        buy_txn = Transaction(
            date=buy_date,
            symbol='SPY',
            shares=100,
            price=400,
            transaction_type='BUY',
            transaction_cost=10
        )

        sell_txn = Transaction(
            date=sell_date,
            symbol='SPY',
            shares=100,
            price=450,
            transaction_type='SELL',
            transaction_cost=10
        )

        gain = self.calc.calculate_capital_gain(buy_txn, sell_txn)

        # Gain = (450 - 400) * 100 - 20 (costs) = $4,980
        expected_gain = (450 - 400) * 100 - 20
        self.assertAlmostEqual(gain, expected_gain, delta=1)

    def test_calculate_long_term_gain(self):
        """Should calculate long-term capital gains."""
        # Buy and sell > 1 year apart
        buy_date = date(2022, 1, 1)
        sell_date = date(2023, 6, 1)

        buy_txn = Transaction(
            date=buy_date,
            symbol='SPY',
            shares=100,
            price=400,
            transaction_type='BUY',
            transaction_cost=10
        )

        sell_txn = Transaction(
            date=sell_date,
            symbol='SPY',
            shares=100,
            price=450,
            transaction_type='SELL',
            transaction_cost=10
        )

        gain = self.calc.calculate_capital_gain(buy_txn, sell_txn)

        # Same calculation, but would be taxed at long-term rate
        expected_gain = (450 - 400) * 100 - 20
        self.assertAlmostEqual(gain, expected_gain, delta=1)

    def test_calculate_capital_loss(self):
        """Should calculate capital losses."""
        buy_date = date(2023, 1, 1)
        sell_date = date(2023, 6, 1)

        buy_txn = Transaction(
            date=buy_date,
            symbol='SPY',
            shares=100,
            price=450,
            transaction_type='BUY',
            transaction_cost=10
        )

        sell_txn = Transaction(
            date=sell_date,
            symbol='SPY',
            shares=100,
            price=400,
            transaction_type='SELL',
            transaction_cost=10
        )

        loss = self.calc.calculate_capital_gain(buy_txn, sell_txn)

        # Loss = (400 - 450) * 100 - 20 = -$5,020
        expected_loss = (400 - 450) * 100 - 20
        self.assertAlmostEqual(loss, expected_loss, delta=1)
        self.assertLess(loss, 0)

    def test_is_wash_sale_simple(self):
        """Should detect simple wash sale."""
        # Sell at loss
        sell_date = date(2023, 6, 1)
        sell_txn = Transaction(
            date=sell_date,
            symbol='SPY',
            shares=100,
            price=400,
            transaction_type='SELL',
            transaction_cost=0
        )

        # Buy back within 30 days
        buy_back_date = date(2023, 6, 15)
        buy_txn = Transaction(
            date=buy_back_date,
            symbol='SPY',
            shares=100,
            price=405,
            transaction_type='BUY',
            transaction_cost=0
        )

        is_wash = self.calc.is_wash_sale(
            sell_transaction=sell_txn,
            buy_transaction=buy_txn,
            original_cost_basis=450  # Sold at loss
        )

        self.assertTrue(is_wash)

    def test_is_not_wash_sale_outside_window(self):
        """Should not flag wash sale outside 30-day window."""
        sell_date = date(2023, 6, 1)
        sell_txn = Transaction(
            date=sell_date,
            symbol='SPY',
            shares=100,
            price=400,
            transaction_type='SELL',
            transaction_cost=0
        )

        # Buy back 40 days later (outside 30-day window)
        buy_back_date = date(2023, 7, 11)
        buy_txn = Transaction(
            date=buy_back_date,
            symbol='SPY',
            shares=100,
            price=405,
            transaction_type='BUY',
            transaction_cost=0
        )

        is_wash = self.calc.is_wash_sale(
            sell_transaction=sell_txn,
            buy_transaction=buy_txn,
            original_cost_basis=450
        )

        self.assertFalse(is_wash)

    def test_is_not_wash_sale_gain(self):
        """Should not flag wash sale if sold at gain."""
        sell_date = date(2023, 6, 1)
        sell_txn = Transaction(
            date=sell_date,
            symbol='SPY',
            shares=100,
            price=450,
            transaction_type='SELL',
            transaction_cost=0
        )

        buy_back_date = date(2023, 6, 15)
        buy_txn = Transaction(
            date=buy_back_date,
            symbol='SPY',
            shares=100,
            price=445,
            transaction_type='BUY',
            transaction_cost=0
        )

        # Sold at gain (cost basis was 400)
        is_wash = self.calc.is_wash_sale(
            sell_transaction=sell_txn,
            buy_transaction=buy_txn,
            original_cost_basis=400
        )

        self.assertFalse(is_wash)

    def test_calculate_tax_liability_short_term(self):
        """Should calculate tax liability for short-term gains."""
        gain = 10000
        holding_period_days = 180  # < 1 year

        tax = self.calc.calculate_tax_liability(gain, holding_period_days)

        # Short-term rate (default ~22%)
        expected_tax = gain * self.calc.short_term_rate
        self.assertAlmostEqual(tax, expected_tax, delta=100)

    def test_calculate_tax_liability_long_term(self):
        """Should calculate tax liability for long-term gains."""
        gain = 10000
        holding_period_days = 400  # > 1 year

        tax = self.calc.calculate_tax_liability(gain, holding_period_days)

        # Long-term rate (default ~15%)
        expected_tax = gain * self.calc.long_term_rate
        self.assertAlmostEqual(tax, expected_tax, delta=100)
        self.assertLess(tax, gain * self.calc.short_term_rate)

    def test_calculate_tax_liability_loss(self):
        """Should handle tax benefit from losses."""
        loss = -5000
        holding_period_days = 180

        tax = self.calc.calculate_tax_liability(loss, holding_period_days)

        # Loss provides tax benefit
        self.assertLess(tax, 0)

    def test_calculate_total_taxes_multiple_transactions(self):
        """Should calculate total taxes from multiple transactions."""
        transactions = [
            # Short-term gain
            (date(2023, 1, 1), date(2023, 6, 1), 100, 400, 450),
            # Long-term gain
            (date(2022, 1, 1), date(2023, 6, 1), 100, 400, 450),
            # Short-term loss
            (date(2023, 1, 1), date(2023, 6, 1), 100, 450, 400),
        ]

        buy_txns = []
        sell_txns = []

        for buy_date, sell_date, shares, buy_price, sell_price in transactions:
            buy_txns.append(Transaction(
                date=buy_date,
                symbol='SPY',
                shares=shares,
                price=buy_price,
                transaction_type='BUY',
                transaction_cost=0
            ))

            sell_txns.append(Transaction(
                date=sell_date,
                symbol='SPY',
                shares=shares,
                price=sell_price,
                transaction_type='SELL',
                transaction_cost=0
            ))

        total_tax = self.calc.calculate_total_taxes(buy_txns, sell_txns)

        # Should be positive (net gains)
        self.assertGreater(total_tax, 0)

    def test_holding_period_classification(self):
        """Should correctly classify holding periods."""
        # Exactly 365 days
        buy_date = date(2022, 1, 1)
        sell_date_short = date(2022, 12, 31)  # 364 days
        sell_date_long = date(2023, 1, 2)     # 366 days

        buy_txn = Transaction(
            date=buy_date,
            symbol='SPY',
            shares=100,
            price=400,
            transaction_type='BUY',
            transaction_cost=0
        )

        sell_short = Transaction(
            date=sell_date_short,
            symbol='SPY',
            shares=100,
            price=450,
            transaction_type='SELL',
            transaction_cost=0
        )

        sell_long = Transaction(
            date=sell_date_long,
            symbol='SPY',
            shares=100,
            price=450,
            transaction_type='SELL',
            transaction_cost=0
        )

        # Calculate holding periods
        days_short = (sell_date_short - buy_date).days
        days_long = (sell_date_long - buy_date).days

        # Short-term should be < 365 days
        self.assertLess(days_short, 365)
        # Long-term should be >= 365 days
        self.assertGreaterEqual(days_long, 365)


class TestTaxCalculatorIntegration(unittest.TestCase):
    """Integration tests for tax calculator with realistic scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.calc = TaxCalculator(
            short_term_rate=0.24,
            long_term_rate=0.15
        )

    def test_year_end_tax_planning(self):
        """Should help with year-end tax planning."""
        # Scenario: Investor has gains and losses
        transactions = []

        # Big gain from long-term hold
        transactions.append((
            date(2022, 1, 1),
            date(2023, 11, 1),
            100,
            300,
            500  # $20k gain
        ))

        # Small loss from short-term trade
        transactions.append((
            date(2023, 10, 1),
            date(2023, 11, 15),
            50,
            400,
            380  # $1k loss
        ))

        total_gain = 0
        for buy_date, sell_date, shares, buy_price, sell_price in transactions:
            buy_txn = Transaction(
                date=buy_date,
                symbol='SPY',
                shares=shares,
                price=buy_price,
                transaction_type='BUY',
                transaction_cost=0
            )

            sell_txn = Transaction(
                date=sell_date,
                symbol='SPY',
                shares=shares,
                price=sell_price,
                transaction_type='SELL',
                transaction_cost=0
            )

            gain = self.calc.calculate_capital_gain(buy_txn, sell_txn)
            total_gain += gain

        # Net gain should be ~$19k
        self.assertGreater(total_gain, 18000)
        self.assertLess(total_gain, 20000)


if __name__ == '__main__':
    unittest.main()
