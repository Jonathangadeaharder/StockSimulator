"""
Tax-Aware Backtesting

Calculate tax impact on investment returns.
"""

from .tax_calculator import TaxCalculator, TaxLot, CapitalGain

__all__ = [
    'TaxCalculator',
    'TaxLot',
    'CapitalGain',
]
