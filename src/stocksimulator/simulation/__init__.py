"""
Monte Carlo Simulation Module

Tools for validating strategy robustness through randomized testing.
"""

from .random_entry_exit import (
    RandomEntryExitSimulator,
    RandomBacktestResult,
    print_monte_carlo_summary
)

__all__ = [
    'RandomEntryExitSimulator',
    'RandomBacktestResult',
    'print_monte_carlo_summary',
]
