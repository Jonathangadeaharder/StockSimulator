"""
Volatility Indicators
"""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class BollingerBandsResult:
    """Bollinger Bands result."""
    upper: float
    middle: float
    lower: float


class ATR:
    """Average True Range."""

    def __init__(self, period: int = 14):
        self.period = period

    def calculate(self, highs: List[float], lows: List[float], closes: List[float]) -> List[Optional[float]]:
        """Calculate ATR."""
        if len(closes) < 2:
            return [None] * len(closes)

        tr_values = [None]

        for i in range(1, len(closes)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            )
            tr_values.append(tr)

        # Smooth TR
        atr_values = [None] * self.period

        if len(tr_values) >= self.period + 1:
            atr = sum([t for t in tr_values[1:self.period+1] if t is not None]) / self.period
            atr_values.append(atr)

            for i in range(self.period + 1, len(tr_values)):
                atr = (atr * (self.period - 1) + tr_values[i]) / self.period
                atr_values.append(atr)

        return atr_values


class BollingerBands:
    """Bollinger Bands."""

    def __init__(self, period: int = 20, num_std: float = 2.0):
        self.period = period
        self.num_std = num_std

    def calculate(self, prices: List[float]) -> List[Optional[BollingerBandsResult]]:
        """Calculate Bollinger Bands."""
        if len(prices) < self.period:
            return [None] * len(prices)

        results = [None] * (self.period - 1)

        for i in range(self.period - 1, len(prices)):
            window = prices[i-self.period+1:i+1]
            middle = sum(window) / len(window)

            variance = sum((p - middle) ** 2 for p in window) / len(window)
            std_dev = variance ** 0.5

            upper = middle + self.num_std * std_dev
            lower = middle - self.num_std * std_dev

            results.append(BollingerBandsResult(upper, middle, lower))

        return results


class KeltnerChannels:
    """Keltner Channels."""

    def __init__(self, ema_period: int = 20, atr_period: int = 10, multiplier: float = 2.0):
        self.ema_period = ema_period
        self.atr_period = atr_period
        self.multiplier = multiplier

    def calculate(self, highs: List[float], lows: List[float], closes: List[float]) -> List[Optional[BollingerBandsResult]]:
        """Calculate Keltner Channels."""
        if len(closes) < max(self.ema_period, self.atr_period):
            return [None] * len(closes)

        # Calculate EMA of closes
        ema = self._ema(closes, self.ema_period)

        # Calculate ATR
        atr_calc = ATR(self.atr_period)
        atr = atr_calc.calculate(highs, lows, closes)

        # Calculate channels
        results = []
        for i in range(len(closes)):
            if ema[i] is None or atr[i] is None:
                results.append(None)
            else:
                upper = ema[i] + self.multiplier * atr[i]
                lower = ema[i] - self.multiplier * atr[i]
                results.append(BollingerBandsResult(upper, ema[i], lower))

        return results

    def _ema(self, prices: List[float], period: int) -> List[Optional[float]]:
        """Calculate EMA."""
        if len(prices) < period:
            return [None] * len(prices)

        alpha = 2.0 / (period + 1)
        ema_values = [None] * (period - 1)
        ema = sum(prices[:period]) / period
        ema_values.append(ema)

        for price in prices[period:]:
            ema = alpha * price + (1 - alpha) * ema
            ema_values.append(ema)

        return ema_values
