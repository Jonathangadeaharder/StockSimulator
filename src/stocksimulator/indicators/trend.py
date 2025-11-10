"""
Trend Indicators

Indicators for identifying market trends.
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MACDResult:
    """MACD indicator result."""
    macd_line: float
    signal_line: float
    histogram: float


class MACD:
    """
    Moving Average Convergence Divergence (MACD).

    Parameters:
        fast_period: Fast EMA period (default: 12)
        slow_period: Slow EMA period (default: 26)
        signal_period: Signal line EMA period (default: 9)
    """

    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def calculate(self, prices: List[float]) -> List[Optional[MACDResult]]:
        """Calculate MACD for price series."""
        if len(prices) < self.slow_period:
            return [None] * len(prices)

        # Calculate EMAs
        fast_ema = self._ema(prices, self.fast_period)
        slow_ema = self._ema(prices, self.slow_period)

        # MACD line = fast_ema - slow_ema
        macd_line = [f - s if f is not None and s is not None else None
                     for f, s in zip(fast_ema, slow_ema)]

        # Signal line = EMA of MACD line
        macd_values = [m for m in macd_line if m is not None]
        signal_line_values = self._ema(macd_values, self.signal_period)

        # Construct results
        results = []
        signal_idx = 0

        for i, macd in enumerate(macd_line):
            if macd is None or i < self.slow_period + self.signal_period - 2:
                results.append(None)
            else:
                signal = signal_line_values[signal_idx] if signal_idx < len(signal_line_values) else None
                if signal is not None:
                    histogram = macd - signal
                    results.append(MACDResult(macd, signal, histogram))
                    signal_idx += 1
                else:
                    results.append(None)

        return results

    def _ema(self, prices: List[float], period: int) -> List[Optional[float]]:
        """Calculate EMA."""
        if len(prices) < period:
            return [None] * len(prices)

        alpha = 2.0 / (period + 1)
        ema_values = []
        ema = sum(prices[:period]) / period  # Start with SMA

        for i, price in enumerate(prices):
            if i < period - 1:
                ema_values.append(None)
            else:
                if i == period - 1:
                    ema = sum(prices[:period]) / period
                else:
                    ema = alpha * price + (1 - alpha) * ema
                ema_values.append(ema)

        return ema_values


class ADX:
    """
    Average Directional Index (ADX).

    Measures trend strength (0-100).
    - ADX > 25: Strong trend
    - ADX < 20: Weak trend

    Parameters:
        period: ADX period (default: 14)
    """

    def __init__(self, period: int = 14):
        self.period = period

    def calculate(self, highs: List[float], lows: List[float], closes: List[float]) -> List[Optional[float]]:
        """Calculate ADX."""
        if len(highs) < self.period + 1:
            return [None] * len(highs)

        # Calculate True Range and Directional Movement
        tr_values = []
        plus_dm = []
        minus_dm = []

        for i in range(1, len(highs)):
            # True Range
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            )
            tr_values.append(tr)

            # Directional Movement
            up_move = highs[i] - highs[i-1]
            down_move = lows[i-1] - lows[i]

            plus_dm.append(up_move if up_move > down_move and up_move > 0 else 0)
            minus_dm.append(down_move if down_move > up_move and down_move > 0 else 0)

        # Smooth TR and DM
        atr = self._smooth(tr_values, self.period)
        plus_di = [(100 * self._smooth(plus_dm, self.period)[i] / atr[i]) if atr[i] > 0 else 0
                   for i in range(len(atr))]
        minus_di = [(100 * self._smooth(minus_dm, self.period)[i] / atr[i]) if atr[i] > 0 else 0
                    for i in range(len(atr))]

        # Calculate DX
        dx = []
        for i in range(len(plus_di)):
            if plus_di[i] + minus_di[i] > 0:
                dx.append(100 * abs(plus_di[i] - minus_di[i]) / (plus_di[i] + minus_di[i]))
            else:
                dx.append(0)

        # ADX = smoothed DX
        adx_values = self._smooth(dx, self.period)

        # Prepend None for initial values
        return [None] + adx_values

    def _smooth(self, values: List[float], period: int) -> List[float]:
        """Wilder's smoothing."""
        if len(values) < period:
            return []

        smoothed = []
        current = sum(values[:period]) / period
        smoothed.append(current)

        for i in range(period, len(values)):
            current = (current * (period - 1) + values[i]) / period
            smoothed.append(current)

        return smoothed


class ParabolicSAR:
    """
    Parabolic SAR (Stop and Reverse).

    Provides trailing stop levels.

    Parameters:
        acceleration: Acceleration factor (default: 0.02)
        maximum: Maximum acceleration (default: 0.2)
    """

    def __init__(self, acceleration: float = 0.02, maximum: float = 0.2):
        self.acceleration = acceleration
        self.maximum = maximum

    def calculate(self, highs: List[float], lows: List[float]) -> List[Optional[float]]:
        """Calculate Parabolic SAR."""
        if len(highs) < 2:
            return [None] * len(highs)

        sar_values = [None]  # First value is None

        # Initial values
        is_uptrend = highs[1] > highs[0]
        sar = lows[0] if is_uptrend else highs[0]
        ep = highs[1] if is_uptrend else lows[1]
        af = self.acceleration

        sar_values.append(sar)

        for i in range(2, len(highs)):
            # Update SAR
            sar = sar + af * (ep - sar)

            # Check for reversal
            if is_uptrend:
                if lows[i] < sar:
                    is_uptrend = False
                    sar = ep
                    ep = lows[i]
                    af = self.acceleration
                else:
                    if highs[i] > ep:
                        ep = highs[i]
                        af = min(af + self.acceleration, self.maximum)
            else:
                if highs[i] > sar:
                    is_uptrend = True
                    sar = ep
                    ep = highs[i]
                    af = self.acceleration
                else:
                    if lows[i] < ep:
                        ep = lows[i]
                        af = min(af + self.acceleration, self.maximum)

            sar_values.append(sar)

        return sar_values
