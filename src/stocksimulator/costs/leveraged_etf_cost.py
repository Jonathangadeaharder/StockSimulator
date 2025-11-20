"""
Leveraged ETF cost modeling with era-specific calibration.
"""

from typing import Dict
from datetime import date
from .base_cost import BaseCost


class LeveragedETFCost(BaseCost):
    """
    Models empirically-calibrated costs for leveraged ETFs.

    Leveraged ETFs incur costs beyond the stated Total Expense Ratio (TER):
    - TER (management fees): ~0.6% for 2x leveraged ETFs
    - Excess costs (swap financing, volatility drag, rebalancing): ~1.5% average

    Total costs vary by era based on interest rates and market conditions.
    This model uses StockSimulator's empirical calibration based on
    2016-2024 academic research.
    """

    def __init__(
        self,
        ter: float = 0.006,
        base_excess_cost: float = 0.015,
        leverage_multiplier: float = 2.0,
        era_adjustments: Dict[str, float] = None
    ):
        """
        Initialize leveraged ETF cost model.

        Args:
            ter: Total Expense Ratio (default: 0.006 = 0.6%)
            base_excess_cost: Base excess cost above TER (default: 0.015 = 1.5%)
            leverage_multiplier: Leverage multiplier (default: 2.0 for 2x ETFs)
            era_adjustments: Custom era-specific cost adjustments
        """
        self.ter = ter
        self.base_excess_cost = base_excess_cost
        self.leverage_multiplier = leverage_multiplier

        # Era-specific cost adjustments based on StockSimulator research
        self.era_adjustments = era_adjustments or {
            '1950-1979': 0.015,  # Pre-derivatives era (estimated)
            '1980-1989': 0.025,  # Volcker high-rate era
            '1990-2007': 0.015,  # Normal times
            '2008-2015': 0.008,  # ZIRP - lowest costs ever
            '2016-2021': 0.012,  # Normalized
            '2022-': 0.020       # Current high-rate environment
        }

        self.daily_ter = self.ter / 252

    def calculate(
        self,
        trades: Dict[str, float],
        positions: Dict[str, float],
        prices: Dict[str, float],
        current_date: date
    ) -> float:
        """
        Calculate leveraged ETF costs for all leveraged positions.

        Args:
            trades: Dictionary of symbol -> shares traded (not used)
            positions: Dictionary of symbol -> current shares held
            prices: Dictionary of symbol -> current price
            current_date: Current date (used for era-specific costs)

        Returns:
            Total leveraged ETF cost for this period
        """
        # Get era-specific excess cost
        excess_cost = self._get_excess_cost_for_date(current_date)
        daily_excess = excess_cost / 252

        # Calculate total cost for leveraged positions
        leveraged_value = 0.0

        for symbol, shares in positions.items():
            if abs(shares) < 1e-10:  # Skip negligible positions
                continue

            if not self._is_leveraged(symbol):
                continue

            if symbol not in prices or prices[symbol] <= 0:
                continue

            position_value = abs(shares * prices[symbol])
            leveraged_value += position_value

        # Total daily cost = TER + excess cost
        daily_rate = self.daily_ter + daily_excess
        return leveraged_value * daily_rate

    def _get_excess_cost_for_date(self, current_date: date) -> float:
        """
        Get era-specific excess cost for given date.

        Args:
            current_date: Date to determine era

        Returns:
            Annual excess cost for this era
        """
        year = current_date.year

        if year < 1980:
            return self.era_adjustments['1950-1979']
        elif year < 1990:
            return self.era_adjustments['1980-1989']
        elif year < 2008:
            return self.era_adjustments['1990-2007']
        elif year < 2016:
            return self.era_adjustments['2008-2015']
        elif year < 2022:
            return self.era_adjustments['2016-2021']
        else:
            return self.era_adjustments['2022-']

    def _is_leveraged(self, symbol: str) -> bool:
        """
        Detect if symbol represents a leveraged instrument.

        Args:
            symbol: Symbol to check

        Returns:
            True if symbol appears to be leveraged
        """
        # Common leveraged ETF patterns
        leveraged_patterns = [
            '_2X', '_3X',           # Explicit multiplier suffix
            'LEVERAGED', 'LEV',     # Contains leverage keyword
            'SSO', 'UPRO', 'TQQQ',  # Known leveraged ETF tickers
            'SPXL', 'TECL', 'UDOW', # More leveraged ETFs
            'QLD', 'DDM', 'MVV'     # 2x leveraged ETFs
        ]

        symbol_upper = symbol.upper()
        return any(pattern in symbol_upper for pattern in leveraged_patterns)

    def get_total_annual_cost(self, current_date: date) -> float:
        """
        Get total annual cost (TER + excess) for given date.

        Useful for reporting and analysis.

        Args:
            current_date: Date to determine era

        Returns:
            Total annual cost as a fraction
        """
        excess_cost = self._get_excess_cost_for_date(current_date)
        return self.ter + excess_cost

    def __repr__(self) -> str:
        return (f"LeveragedETFCost(ter={self.ter}, "
                f"base_excess={self.base_excess_cost}, "
                f"leverage={self.leverage_multiplier}x)")
