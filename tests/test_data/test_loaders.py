"""
Test suite for data loaders.

Tests CSV loading functionality.
"""

import unittest
import sys
import os
from datetime import date

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from stocksimulator.data.loaders import CSVLoader, load_from_csv, load_multiple_csv, discover_csv_files
from stocksimulator.models.market_data import MarketData


class TestCSVLoader(unittest.TestCase):
    """Test the CSVLoader class."""

    @classmethod
    def setUpClass(cls):
        """Set up test data path."""
        cls.data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'historical_data')

    def setUp(self):
        """Create loader instance."""
        self.loader = CSVLoader()

    def test_loader_initialization(self):
        """Loader should initialize correctly."""
        self.assertIsNotNone(self.loader)

    def test_load_sp500_data(self):
        """Should load S&P 500 data successfully."""
        filepath = os.path.join(self.data_path, 'sp500_stooq_daily.csv')

        data = self.loader.load(filepath, symbol='SPY')

        self.assertIsInstance(data, MarketData)
        self.assertEqual(data.symbol, 'SPY')
        self.assertGreater(len(data.data), 1000)  # Should have substantial history

    def test_loaded_data_has_correct_fields(self):
        """Loaded data should have all OHLCV fields."""
        filepath = os.path.join(self.data_path, 'sp500_stooq_daily.csv')
        data = self.loader.load(filepath, symbol='SPY')

        # Check first data point
        first_point = data.data[0]

        self.assertIsInstance(first_point.date, date)
        self.assertIsInstance(first_point.open, float)
        self.assertIsInstance(first_point.high, float)
        self.assertIsInstance(first_point.low, float)
        self.assertIsInstance(first_point.close, float)
        self.assertIsInstance(first_point.volume, (int, float))

    def test_data_is_sorted_by_date(self):
        """Data should be sorted in chronological order."""
        filepath = os.path.join(self.data_path, 'sp500_stooq_daily.csv')
        data = self.loader.load(filepath, symbol='SPY')

        # Check dates are ascending
        for i in range(len(data.data) - 1):
            self.assertLessEqual(data.data[i].date, data.data[i + 1].date)

    def test_prices_are_positive(self):
        """All prices should be positive."""
        filepath = os.path.join(self.data_path, 'sp500_stooq_daily.csv')
        data = self.loader.load(filepath, symbol='SPY')

        for point in data.data[:100]:  # Check first 100 points
            self.assertGreater(point.open, 0)
            self.assertGreater(point.high, 0)
            self.assertGreater(point.low, 0)
            self.assertGreater(point.close, 0)

    def test_high_is_highest(self):
        """High should be >= open, close, low."""
        filepath = os.path.join(self.data_path, 'sp500_stooq_daily.csv')
        data = self.loader.load(filepath, symbol='SPY')

        for point in data.data[:100]:
            self.assertGreaterEqual(point.high, point.open)
            self.assertGreaterEqual(point.high, point.close)
            self.assertGreaterEqual(point.high, point.low)

    def test_low_is_lowest(self):
        """Low should be <= open, close, high."""
        filepath = os.path.join(self.data_path, 'sp500_stooq_daily.csv')
        data = self.loader.load(filepath, symbol='SPY')

        for point in data.data[:100]:
            self.assertLessEqual(point.low, point.open)
            self.assertLessEqual(point.low, point.close)
            self.assertLessEqual(point.low, point.high)


class TestHelperFunctions(unittest.TestCase):
    """Test helper functions for data loading."""

    @classmethod
    def setUpClass(cls):
        """Set up test data path."""
        cls.data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'historical_data')

    def test_load_from_csv_helper(self):
        """load_from_csv helper should work."""
        data = load_from_csv('sp500_stooq_daily.csv', 'SPY', self.data_path)

        self.assertIsInstance(data, MarketData)
        self.assertEqual(data.symbol, 'SPY')
        self.assertGreater(len(data.data), 0)

    def test_discover_csv_files(self):
        """discover_csv_files should find CSV files."""
        files = discover_csv_files(self.data_path)

        self.assertIsInstance(files, dict)
        self.assertGreater(len(files), 0)

        # Should include sp500 file
        found_sp500 = any('sp500' in key.lower() or 'sp500' in val.lower()
                          for key, val in files.items())
        self.assertTrue(found_sp500, "Should find S&P 500 data file")

    def test_load_multiple_csv(self):
        """load_multiple_csv should load multiple files."""
        # Try to load SP500
        files_to_load = {'SPY': 'sp500_stooq_daily.csv'}

        data = load_multiple_csv(files_to_load, self.data_path)

        self.assertIn('SPY', data)
        self.assertIsInstance(data['SPY'], MarketData)

    def test_invalid_file_raises_error(self):
        """Loading non-existent file should raise FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            load_from_csv('nonexistent_file.csv', 'TEST', self.data_path)


class TestMarketData(unittest.TestCase):
    """Test MarketData class methods."""

    @classmethod
    def setUpClass(cls):
        """Load test data."""
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'historical_data')
        cls.spy_data = load_from_csv('sp500_stooq_daily.csv', 'SPY', data_path)

    def test_get_date_range(self):
        """MarketData should report correct date range."""
        first_date = self.spy_data.data[0].date
        last_date = self.spy_data.data[-1].date

        self.assertIsInstance(first_date, date)
        self.assertIsInstance(last_date, date)
        self.assertLess(first_date, last_date)

    def test_data_length(self):
        """MarketData should have substantial history."""
        self.assertGreater(len(self.spy_data.data), 1000)

    def test_symbol_is_preserved(self):
        """Symbol should be preserved in MarketData."""
        self.assertEqual(self.spy_data.symbol, 'SPY')

    def test_metadata_exists(self):
        """MarketData should have metadata."""
        self.assertIsInstance(self.spy_data.metadata, dict)


if __name__ == '__main__':
    unittest.main()
