"""
Advanced Technical Indicators

Complex indicators like Ichimoku, VWAP, Supertrend.
"""

from typing import List, Optional
from dataclasses import dataclass

from stocksimulator.models.market_data import OHLCV


@dataclass
class IchimokuResult:
    """Result from Ichimoku Cloud calculation."""
    tenkan_sen: float     # Conversion Line
    kijun_sen: float      # Base Line
    senkou_span_a: float  # Leading Span A
    senkou_span_b: float  # Leading Span B
    chikou_span: float    # Lagging Span


class IchimokuCloud:
    """
    Ichimoku Cloud (Ichimoku Kinko Hyo).

    A comprehensive indicator showing support/resistance, trend, and momentum.
    """

    def __init__(
        self,
        tenkan_period: int = 9,
        kijun_period: int = 26,
        senkou_span_b_period: int = 52
    ):
        """
        Initialize Ichimoku Cloud.

        Args:
            tenkan_period: Conversion line period (default: 9)
            kijun_period: Base line period (default: 26)
            senkou_span_b_period: Leading Span B period (default: 52)
        """
        self.tenkan_period = tenkan_period
        self.kijun_period = kijun_period
        self.senkou_span_b_period = senkou_span_b_period

    def calculate(self, data: List[OHLCV], displacement: int = 26) -> IchimokuResult:
        """
        Calculate Ichimoku Cloud components.

        Args:
            data: List of OHLCV data
            displacement: Cloud displacement (default: 26)

        Returns:
            IchimokuResult
        """
        if len(data) < self.senkou_span_b_period:
            return IchimokuResult(0, 0, 0, 0, 0)

        # Tenkan-sen (Conversion Line): (9-period high + 9-period low) / 2
        tenkan_sen = self._midpoint(data[-self.tenkan_period:])

        # Kijun-sen (Base Line): (26-period high + 26-period low) / 2
        kijun_sen = self._midpoint(data[-self.kijun_period:])

        # Senkou Span A (Leading Span A): (Conversion Line + Base Line) / 2
        senkou_span_a = (tenkan_sen + kijun_sen) / 2

        # Senkou Span B (Leading Span B): (52-period high + 52-period low) / 2
        senkou_span_b = self._midpoint(data[-self.senkou_span_b_period:])

        # Chikou Span (Lagging Span): Current close, plotted 26 periods back
        chikou_span = data[-1].close if data else 0

        return IchimokuResult(
            tenkan_sen=tenkan_sen,
            kijun_sen=kijun_sen,
            senkou_span_a=senkou_span_a,
            senkou_span_b=senkou_span_b,
            chikou_span=chikou_span
        )

    def _midpoint(self, data: List[OHLCV]) -> float:
        """Calculate midpoint of high/low range."""
        if not data:
            return 0.0
        highs = [point.high for point in data]
        lows = [point.low for point in data]
        return (max(highs) + min(lows)) / 2

    def get_signal(self, data: List[OHLCV]) -> str:
        """
        Get trading signal from Ichimoku.

        Returns:
            'bullish', 'bearish', or 'neutral'
        """
        if len(data) < self.senkou_span_b_period:
            return 'neutral'

        result = self.calculate(data)
        current_price = data[-1].close

        # Price above cloud = bullish
        # Price below cloud = bearish
        cloud_top = max(result.senkou_span_a, result.senkou_span_b)
        cloud_bottom = min(result.senkou_span_a, result.senkou_span_b)

        if current_price > cloud_top and result.tenkan_sen > result.kijun_sen:
            return 'bullish'
        elif current_price < cloud_bottom and result.tenkan_sen < result.kijun_sen:
            return 'bearish'
        else:
            return 'neutral'


class VWAP:
    """
    Volume Weighted Average Price.

    Measures average price weighted by volume.
    """

    def calculate(self, data: List[OHLCV], period: Optional[int] = None) -> float:
        """
        Calculate VWAP.

        Args:
            data: List of OHLCV data
            period: Lookback period (None = all data)

        Returns:
            VWAP value
        """
        if not data:
            return 0.0

        # Use only specified period
        if period:
            data = data[-period:]

        total_volume = 0.0
        total_pv = 0.0

        for point in data:
            typical_price = (point.high + point.low + point.close) / 3
            pv = typical_price * point.volume
            total_pv += pv
            total_volume += point.volume

        if total_volume == 0:
            return 0.0

        return total_pv / total_volume

    def get_signal(self, data: List[OHLCV], period: Optional[int] = None) -> str:
        """
        Get trading signal from VWAP.

        Returns:
            'bullish' if price > VWAP, 'bearish' if price < VWAP
        """
        if not data:
            return 'neutral'

        vwap = self.calculate(data, period)
        current_price = data[-1].close

        if current_price > vwap:
            return 'bullish'
        elif current_price < vwap:
            return 'bearish'
        else:
            return 'neutral'


@dataclass
class SupertrendResult:
    """Result from Supertrend calculation."""
    supertrend: float
    direction: int  # 1 = uptrend, -1 = downtrend


class Supertrend:
    """
    Supertrend Indicator.

    Combines ATR and price to identify trend direction.
    """

    def __init__(self, period: int = 10, multiplier: float = 3.0):
        """
        Initialize Supertrend.

        Args:
            period: ATR period (default: 10)
            multiplier: ATR multiplier (default: 3.0)
        """
        self.period = period
        self.multiplier = multiplier

    def calculate(self, data: List[OHLCV]) -> SupertrendResult:
        """
        Calculate Supertrend.

        Args:
            data: List of OHLCV data

        Returns:
            SupertrendResult
        """
        if len(data) < self.period + 1:
            return SupertrendResult(0, 0)

        # Calculate ATR
        atr = self._calculate_atr(data)

        # Calculate basic upper and lower bands
        hl_avg = (data[-1].high + data[-1].low) / 2
        basic_ub = hl_avg + (self.multiplier * atr)
        basic_lb = hl_avg - (self.multiplier * atr)

        # Simplified Supertrend logic
        close = data[-1].close

        if close > basic_ub:
            supertrend = basic_lb
            direction = 1  # Uptrend
        elif close < basic_lb:
            supertrend = basic_ub
            direction = -1  # Downtrend
        else:
            # Maintain previous direction (simplified)
            supertrend = hl_avg
            direction = 1 if close > hl_avg else -1

        return SupertrendResult(supertrend=supertrend, direction=direction)

    def _calculate_atr(self, data: List[OHLCV]) -> float:
        """Calculate Average True Range."""
        if len(data) < 2:
            return 0.0

        trs = []
        for i in range(1, len(data)):
            high_low = data[i].high - data[i].low
            high_close = abs(data[i].high - data[i - 1].close)
            low_close = abs(data[i].low - data[i - 1].close)
            tr = max(high_low, high_close, low_close)
            trs.append(tr)

        # Average of last 'period' TRs
        recent_trs = trs[-self.period:]
        return sum(recent_trs) / len(recent_trs) if recent_trs else 0.0

    def get_signal(self, data: List[OHLCV]) -> str:
        """
        Get trading signal from Supertrend.

        Returns:
            'bullish', 'bearish', or 'neutral'
        """
        result = self.calculate(data)

        if result.direction == 1:
            return 'bullish'
        elif result.direction == -1:
            return 'bearish'
        else:
            return 'neutral'


@dataclass
class DonchianChannelsResult:
    """Result from Donchian Channels calculation."""
    upper: float
    middle: float
    lower: float


class DonchianChannels:
    """
    Donchian Channels.

    Plots highest high and lowest low over a period.
    """

    def __init__(self, period: int = 20):
        """
        Initialize Donchian Channels.

        Args:
            period: Lookback period (default: 20)
        """
        self.period = period

    def calculate(self, data: List[OHLCV]) -> DonchianChannelsResult:
        """
        Calculate Donchian Channels.

        Args:
            data: List of OHLCV data

        Returns:
            DonchianChannelsResult
        """
        if len(data) < self.period:
            return DonchianChannelsResult(0, 0, 0)

        recent_data = data[-self.period:]

        upper = max(point.high for point in recent_data)
        lower = min(point.low for point in recent_data)
        middle = (upper + lower) / 2

        return DonchianChannelsResult(upper=upper, middle=middle, lower=lower)

    def get_signal(self, data: List[OHLCV]) -> str:
        """
        Get trading signal from Donchian Channels.

        Returns:
            'bullish' if close > upper, 'bearish' if close < lower
        """
        if len(data) < self.period:
            return 'neutral'

        result = self.calculate(data)
        current_price = data[-1].close

        if current_price >= result.upper:
            return 'bullish'  # Breakout upward
        elif current_price <= result.lower:
            return 'bearish'  # Breakout downward
        else:
            return 'neutral'
