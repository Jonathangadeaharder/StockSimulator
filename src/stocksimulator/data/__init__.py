"""
Data loading and management

This module provides data loaders for:
- CSV files (historical data)
- Downloaded data (Yahoo Finance, Alpha Vantage)
- Data caching
"""

from .loaders import CSVLoader, load_from_csv, load_multiple_csv
from .cache import DataCache

# Note: Downloaders are in a separate module to avoid dependencies
# Import from stocksimulator.downloaders if you need them

__all__ = [
    'CSVLoader',
    'load_from_csv',
    'load_multiple_csv',
    'DataCache',
]
