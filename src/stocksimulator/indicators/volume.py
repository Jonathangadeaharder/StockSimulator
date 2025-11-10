"""
Volume Indicators
"""

from typing import List, Optional


class OBV:
    """On-Balance Volume."""

    def calculate(self, closes: List[float], volumes: List[int]) -> List[float]:
        """Calculate OBV."""
        if len(closes) < 2:
            return [0.0] * len(closes)

        obv_values = [0.0]
        obv = 0.0

        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                obv += volumes[i]
            elif closes[i] < closes[i-1]:
                obv -= volumes[i]

            obv_values.append(obv)

        return obv_values


class MFI:
    """Money Flow Index."""

    def __init__(self, period: int = 14):
        self.period = period

    def calculate(self, highs: List[float], lows: List[float], closes: List[float], volumes: List[int]) -> List[Optional[float]]:
        """Calculate MFI."""
        if len(closes) < self.period + 1:
            return [None] * len(closes)

        # Calculate typical price
        typical_prices = [(h + l + c) / 3 for h, l, c in zip(highs, lows, closes)]

        # Calculate money flow
        money_flow = [tp * v for tp, v in zip(typical_prices, volumes)]

        results = [None]

        for i in range(1, len(closes)):
            if i < self.period:
                results.append(None)
                continue

            positive_flow = 0.0
            negative_flow = 0.0

            for j in range(i - self.period + 1, i + 1):
                if typical_prices[j] > typical_prices[j-1]:
                    positive_flow += money_flow[j]
                elif typical_prices[j] < typical_prices[j-1]:
                    negative_flow += money_flow[j]

            if negative_flow == 0:
                mfi = 100.0
            else:
                money_ratio = positive_flow / negative_flow
                mfi = 100.0 - (100.0 / (1.0 + money_ratio))

            results.append(mfi)

        return results
