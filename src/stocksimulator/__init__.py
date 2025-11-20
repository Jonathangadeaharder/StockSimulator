"""
StockSimulator - A production-grade stock market simulation platform
"""

__version__ = "1.0.0"
__author__ = "StockSimulator Contributors"
__license__ = "MIT"

from .core import *
from .models import *

# Quick-start API (Phase 1 enhancement)
from .quick import quick_backtest, print_backtest, bt, pb
