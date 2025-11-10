"""
Tests for Volume Indicators

Comprehensive tests for OBV, VWAP, and other volume indicators.
"""

import unittest
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from stocksimulator.indicators.volume import OBV, VWAP, VolumeWeightedRSI
from stocksimulator.data import load_from_csv


class TestVolumeIndicators(unittest.TestCase):
    """Test volume indicator calculations."""

    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'historical_data')
        cls.spy_data = load_from_csv('sp500_stooq_daily.csv', 'SPY', data_path)

    def test_obv_initialization(self):
        """OBV should initialize correctly."""
        obv = OBV()
        self.assertIsNotNone(obv)

    def test_obv_calculation_simple(self):
        """OBV should calculate on-balance volume."""
        obv = OBV()

        # Use real data
        recent_data = self.spy_data.data[-100:]
        closes = [d.close for d in recent_data]
        volumes = [d.volume for d in recent_data]

        obv_values = obv.calculate(closes, volumes)

        # Should return list of values
        self.assertIsInstance(obv_values, list)
        self.assertEqual(len(obv_values), len(closes))

        # First value should be first volume
        self.assertEqual(obv_values[0], volumes[0])

        # Values should be cumulative
        for i in range(1, len(obv_values)):
            if obv_values[i] is not None:
                self.assertIsInstance(obv_values[i], (int, float))

    def test_obv_uptrend(self):
        """OBV should increase in uptrend."""
        obv = OBV()

        # Simulate uptrend
        closes = [100, 101, 102, 103, 104]
        volumes = [1000, 1000, 1000, 1000, 1000]

        obv_values = obv.calculate(closes, volumes)

        # OBV should be increasing
        for i in range(1, len(obv_values)):
            self.assertGreater(obv_values[i], obv_values[i-1])

    def test_obv_downtrend(self):
        """OBV should decrease in downtrend."""
        obv = OBV()

        # Simulate downtrend
        closes = [104, 103, 102, 101, 100]
        volumes = [1000, 1000, 1000, 1000, 1000]

        obv_values = obv.calculate(closes, volumes)

        # OBV should be decreasing
        for i in range(1, len(obv_values)):
            self.assertLess(obv_values[i], obv_values[i-1])

    def test_obv_unchanged_price(self):
        """OBV should not change when price is unchanged."""
        obv = OBV()

        closes = [100, 100, 100]
        volumes = [1000, 1000, 1000]

        obv_values = obv.calculate(closes, volumes)

        # OBV should stay same when price unchanged
        self.assertEqual(obv_values[0], obv_values[1])
        self.assertEqual(obv_values[1], obv_values[2])

    def test_obv_real_data(self):
        """OBV should work with real market data."""
        obv = OBV()

        recent_data = self.spy_data.data[-252:]  # 1 year
        closes = [d.close for d in recent_data]
        volumes = [d.volume for d in recent_data]

        obv_values = obv.calculate(closes, volumes)

        # Should have values
        self.assertEqual(len(obv_values), len(closes))
        self.assertIsNotNone(obv_values[-1])

        # All values should be numbers
        for val in obv_values:
            self.assertIsInstance(val, (int, float))

    def test_vwap_initialization(self):
        """VWAP should initialize with period."""
        vwap = VWAP(period=20)
        self.assertEqual(vwap.period, 20)

    def test_vwap_calculation_simple(self):
        """VWAP should calculate volume-weighted average price."""
        vwap = VWAP(period=5)

        # Simple test data
        highs = [101, 102, 103, 104, 105]
        lows = [99, 100, 101, 102, 103]
        closes = [100, 101, 102, 103, 104]
        volumes = [1000, 1000, 1000, 1000, 1000]

        vwap_values = vwap.calculate(highs, lows, closes, volumes)

        # Should return list
        self.assertIsInstance(vwap_values, list)
        self.assertEqual(len(vwap_values), len(closes))

        # First values should be None (warmup period)
        self.assertIsNone(vwap_values[0])

        # Later values should be calculated
        self.assertIsNotNone(vwap_values[-1])

    def test_vwap_typical_price(self):
        """VWAP should use typical price (H+L+C)/3."""
        vwap = VWAP(period=3)

        highs = [10, 10, 10]
        lows = [8, 8, 8]
        closes = [9, 9, 9]
        volumes = [100, 100, 100]

        vwap_values = vwap.calculate(highs, lows, closes, volumes)

        # Typical price = (10+8+9)/3 = 9
        # VWAP should be 9 (since all equal weight)
        last_vwap = [v for v in vwap_values if v is not None][-1]
        self.assertAlmostEqual(last_vwap, 9.0, delta=0.01)

    def test_vwap_real_data(self):
        """VWAP should work with real market data."""
        vwap = VWAP(period=20)

        recent_data = self.spy_data.data[-100:]
        highs = [d.high for d in recent_data]
        lows = [d.low for d in recent_data]
        closes = [d.close for d in recent_data]
        volumes = [d.volume for d in recent_data]

        vwap_values = vwap.calculate(highs, lows, closes, volumes)

        # Should have values after warmup
        valid_values = [v for v in vwap_values if v is not None]
        self.assertGreater(len(valid_values), 50)

        # VWAP should be close to typical price
        for i in range(len(recent_data)):
            if vwap_values[i] is not None:
                typical = (recent_data[i].high + recent_data[i].low + recent_data[i].close) / 3
                # VWAP should be within reasonable range of typical price
                self.assertLess(abs(vwap_values[i] - typical), typical * 0.1)

    def test_vwap_different_periods(self):
        """VWAP should behave differently with different periods."""
        recent_data = self.spy_data.data[-100:]
        highs = [d.high for d in recent_data]
        lows = [d.low for d in recent_data]
        closes = [d.close for d in recent_data]
        volumes = [d.volume for d in recent_data]

        vwap_short = VWAP(period=5)
        vwap_long = VWAP(period=20)

        values_short = vwap_short.calculate(highs, lows, closes, volumes)
        values_long = vwap_long.calculate(highs, lows, closes, volumes)

        # Short period should have more non-None values
        short_count = sum(1 for v in values_short if v is not None)
        long_count = sum(1 for v in values_long if v is not None)
        self.assertGreater(short_count, long_count)

    def test_volume_weighted_rsi_initialization(self):
        """VolumeWeightedRSI should initialize with period."""
        vwrsi = VolumeWeightedRSI(period=14)
        self.assertEqual(vwrsi.period, 14)

    def test_volume_weighted_rsi_calculation(self):
        """VolumeWeightedRSI should calculate volume-weighted RSI."""
        vwrsi = VolumeWeightedRSI(period=14)

        recent_data = self.spy_data.data[-100:]
        closes = [d.close for d in recent_data]
        volumes = [d.volume for d in recent_data]

        rsi_values = vwrsi.calculate(closes, volumes)

        # Should return list
        self.assertIsInstance(rsi_values, list)
        self.assertEqual(len(rsi_values), len(closes))

        # Should have some valid values
        valid_values = [v for v in rsi_values if v is not None]
        self.assertGreater(len(valid_values), 50)

    def test_volume_weighted_rsi_bounds(self):
        """VolumeWeightedRSI should stay between 0 and 100."""
        vwrsi = VolumeWeightedRSI(period=14)

        recent_data = self.spy_data.data[-252:]
        closes = [d.close for d in recent_data]
        volumes = [d.volume for d in recent_data]

        rsi_values = vwrsi.calculate(closes, volumes)

        # All non-None values should be 0-100
        for val in rsi_values:
            if val is not None:
                self.assertGreaterEqual(val, 0)
                self.assertLessEqual(val, 100)

    def test_volume_weighted_rsi_uptrend(self):
        """VolumeWeightedRSI should be high in strong uptrend with volume."""
        vwrsi = VolumeWeightedRSI(period=14)

        # Strong uptrend with increasing volume
        closes = list(range(100, 130))
        volumes = [1000 * (i + 1) for i in range(len(closes))]

        rsi_values = vwrsi.calculate(closes, volumes)

        # Last value should be high
        last_value = [v for v in rsi_values if v is not None][-1]
        self.assertGreater(last_value, 50)

    def test_volume_weighted_rsi_downtrend(self):
        """VolumeWeightedRSI should be low in strong downtrend with volume."""
        vwrsi = VolumeWeightedRSI(period=14)

        # Strong downtrend with increasing volume
        closes = list(range(130, 100, -1))
        volumes = [1000 * (i + 1) for i in range(len(closes))]

        rsi_values = vwrsi.calculate(closes, volumes)

        # Last value should be low
        last_value = [v for v in rsi_values if v is not None][-1]
        self.assertLess(last_value, 50)

    def test_obv_mismatched_lengths(self):
        """OBV should handle mismatched input lengths gracefully."""
        obv = OBV()

        closes = [100, 101, 102]
        volumes = [1000, 1000]  # One fewer

        # Should handle gracefully (implementation dependent)
        try:
            result = obv.calculate(closes, volumes)
            # If it doesn't raise error, check result makes sense
            self.assertIsInstance(result, list)
        except (ValueError, IndexError):
            # Also acceptable to raise error
            pass

    def test_vwap_insufficient_data(self):
        """VWAP should return None for insufficient data."""
        vwap = VWAP(period=20)

        highs = [100, 101]
        lows = [99, 100]
        closes = [100, 101]
        volumes = [1000, 1000]

        vwap_values = vwap.calculate(highs, lows, closes, volumes)

        # All should be None (not enough data)
        self.assertTrue(all(v is None for v in vwap_values))


if __name__ == '__main__':
    unittest.main()
