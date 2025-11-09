"""
Data loading and management

This module provides data loaders for:
- CSV files (historical data)
- Downloaded data (optional)
"""

from .loaders import CSVLoader, load_from_csv, load_multiple_csv
from .cache import DataCache

__all__ = [
    'CSVLoader',
    'load_from_csv',
    'load_multiple_csv',
    'DataCache',
]
