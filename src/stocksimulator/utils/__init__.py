"""
Utility functions and helpers

This module provides utility functions for:
- Date operations (parsing, trading days, ranges)
- Mathematical calculations (percentiles, statistics, correlations)
- Validation (allocations, portfolios, parameters)
"""

# Date utilities
from .date_utils import (
    parse_date,
    trading_days_between,
    add_trading_days,
    is_weekend,
    next_business_day,
    generate_date_range,
    get_quarter,
    format_date
)

# Math utilities
from .math_utils import (
    calculate_percentile,
    calculate_mean,
    calculate_variance,
    calculate_std_dev,
    calculate_sharpe,
    calculate_correlation,
    calculate_covariance,
    compound_returns,
    annualize_return,
    calculate_drawdown,
    geometric_mean,
    linear_regression,
    moving_average,
    exponential_moving_average,
    clamp,
    normalize
)

# Validators
from .validators import (
    validate_allocation,
    validate_portfolio,
    validate_price,
    validate_date_range,
    validate_parameter,
    validate_returns,
    validate_symbol,
    validate_transaction_cost,
    check_data_quality
)

__all__ = [
    # Date utils
    'parse_date',
    'trading_days_between',
    'add_trading_days',
    'is_weekend',
    'next_business_day',
    'generate_date_range',
    'get_quarter',
    'format_date',

    # Math utils
    'calculate_percentile',
    'calculate_mean',
    'calculate_variance',
    'calculate_std_dev',
    'calculate_sharpe',
    'calculate_correlation',
    'calculate_covariance',
    'compound_returns',
    'annualize_return',
    'calculate_drawdown',
    'geometric_mean',
    'linear_regression',
    'moving_average',
    'exponential_moving_average',
    'clamp',
    'normalize',

    # Validators
    'validate_allocation',
    'validate_portfolio',
    'validate_price',
    'validate_date_range',
    'validate_parameter',
    'validate_returns',
    'validate_symbol',
    'validate_transaction_cost',
    'check_data_quality',
]
