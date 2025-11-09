"""
Momentum Indicators
"""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class StochasticResult:
    """Stochastic oscillator result."""
    k: float  # %K line
    d: float  # %D line (signal)


class RSI:
    """Relative Strength Index."""

    def __init__(self, period: int = 14):
        self.period = period

    def calculate(self, prices: List[float]) -> List[Optional[float]]:
        """Calculate RSI."""
        if len(prices) < self.period + 1:
            return [None] * len(prices)

        gains = []
        losses = []

        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            gains.append(max(change, 0))
            losses.append(abs(min(change, 0)))

        rsi_values = [None]  # First value

        for i in range(self.period - 1, len(gains)):
            avg_gain = sum(gains[i-self.period+1:i+1]) / self.period
            avg_loss = sum(losses[i-self.period+1:i+1]) / self.period

            if avg_loss == 0:
                rsi_values.append(100.0)
            else:
                rs = avg_gain / avg_loss
                rsi = 100.0 - (100.0 / (1.0 + rs))
                rsi_values.append(rsi)

        return rsi_values


class Stochastic:
    """Stochastic Oscillator."""

    def __init__(self, k_period: int = 14, d_period: int = 3):
        self.k_period = k_period
        self.d_period = d_period

    def calculate(self, highs: List[float], lows: List[float], closes: List[float]) -> List[Optional[StochasticResult]]:
        """Calculate Stochastic."""
        if len(closes) < self.k_period:
            return [None] * len(closes)

        k_values = []

        for i in range(self.k_period - 1, len(closes)):
            window_high = max(highs[i-self.k_period+1:i+1])
            window_low = min(lows[i-self.k_period+1:i+1])

            if window_high == window_low:
                k_values.append(50.0)
            else:
                k = 100 * (closes[i] - window_low) / (window_high - window_low)
                k_values.append(k)

        # %D is SMA of %K
        results = [None] * (self.k_period - 1)

        for i in range(len(k_values)):
            if i < self.d_period - 1:
                results.append(None)
            else:
                d = sum(k_values[i-self.d_period+1:i+1]) / self.d_period
                results.append(StochasticResult(k_values[i], d))

        return results


class WilliamsR:
    """Williams %R."""

    def __init__(self, period: int = 14):
        self.period = period

    def calculate(self, highs: List[float], lows: List[float], closes: List[float]) -> List[Optional[float]]:
        """Calculate Williams %R."""
        if len(closes) < self.period:
            return [None] * len(closes)

        results = [None] * (self.period - 1)

        for i in range(self.period - 1, len(closes)):
            window_high = max(highs[i-self.period+1:i+1])
            window_low = min(lows[i-self.period+1:i+1])

            if window_high == window_low:
                results.append(-50.0)
            else:
                wr = -100 * (window_high - closes[i]) / (window_high - window_low)
                results.append(wr)

        return results
