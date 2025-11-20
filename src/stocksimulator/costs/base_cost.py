"""
Base cost class for portfolio cost modeling.
"""

from abc import ABC, abstractmethod
from typing import Dict
from datetime import date


class BaseCost(ABC):
    """
    Abstract base class for portfolio costs.

    All cost components inherit from this class and implement
    the calculate() method to compute costs for a given period.
    """

    @abstractmethod
    def calculate(
        self,
        trades: Dict[str, float],
        positions: Dict[str, float],
        prices: Dict[str, float],
        current_date: date
    ) -> float:
        """
        Calculate cost for current period.

        Args:
            trades: Dictionary of symbol -> shares traded (positive = buy, negative = sell)
            positions: Dictionary of symbol -> current shares held
            prices: Dictionary of symbol -> current price
            current_date: Current date

        Returns:
            Total cost for this period (always positive)
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
