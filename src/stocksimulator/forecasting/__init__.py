"""
Forecasting and causality enforcement for backtesting.

Phase 2 Enhancement: Ensures strategies cannot access future data,
preventing look-ahead bias in research and backtesting.
"""

from .causality import CausalityEnforcer
from .base_forecaster import BaseForecastor, HistoricalMeanForecastor

__all__ = [
    'CausalityEnforcer',
    'BaseForecastor',
    'HistoricalMeanForecastor'
]
