"""
Validation utilities

Validators for portfolio allocations, parameters, and data.
"""

from typing import Dict, List, Optional, Any
from datetime import date


def validate_allocation(allocation: Dict[str, float], tolerance: float = 0.01) -> bool:
    """
    Validate that portfolio allocation is valid.

    Args:
        allocation: Dictionary of symbol -> allocation percentage
        tolerance: Tolerance for sum check (default: 0.01%)

    Returns:
        True if valid, False otherwise

    Example:
        >>> validate_allocation({'SPY': 60.0, 'TLT': 40.0})
        True
        >>> validate_allocation({'SPY': 60.0, 'TLT': 50.0})  # Sums to 110%
        False
    """
    if not allocation:
        return False

    # Check all values are non-negative
    if any(v < 0 for v in allocation.values()):
        return False

    # Check sum doesn't exceed 100% (with tolerance)
    total = sum(allocation.values())
    if total > 100.0 + tolerance:
        return False

    return True


def validate_portfolio(
    positions: Dict[str, float],
    cash: float,
    total_value: float,
    tolerance: float = 0.01
) -> bool:
    """
    Validate portfolio state consistency.

    Args:
        positions: Dictionary of symbol -> value
        cash: Cash balance
        total_value: Expected total portfolio value
        tolerance: Tolerance as percentage (default: 0.01%)

    Returns:
        True if valid
    """
    # Check cash is non-negative
    if cash < 0:
        return False

    # Check all position values are non-negative
    if any(v < 0 for v in positions.values()):
        return False

    # Check total value matches
    calculated_total = cash + sum(positions.values())
    diff_pct = abs(calculated_total - total_value) / total_value if total_value > 0 else 0

    if diff_pct > tolerance / 100:
        return False

    return True


def validate_price(price: float) -> bool:
    """
    Validate that price is valid.

    Args:
        price: Price to validate

    Returns:
        True if valid
    """
    return price > 0 and not (price != price)  # Positive and not NaN


def validate_date_range(start_date: date, end_date: date) -> bool:
    """
    Validate date range.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        True if start <= end
    """
    return start_date <= end_date


def validate_parameter(
    value: Any,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    allowed_values: Optional[List[Any]] = None
) -> bool:
    """
    Validate parameter value.

    Args:
        value: Value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        allowed_values: List of allowed values

    Returns:
        True if valid

    Example:
        >>> validate_parameter(50, min_value=0, max_value=100)
        True
        >>> validate_parameter('daily', allowed_values=['daily', 'weekly'])
        True
    """
    # Check allowed values
    if allowed_values is not None:
        return value in allowed_values

    # Check numeric range
    if isinstance(value, (int, float)):
        if min_value is not None and value < min_value:
            return False
        if max_value is not None and value > max_value:
            return False

    return True


def validate_returns(returns: List[float]) -> bool:
    """
    Validate return series.

    Args:
        returns: List of returns

    Returns:
        True if valid
    """
    if not returns:
        return False

    # Check for NaN or infinite values
    for r in returns:
        if r != r or abs(r) == float('inf'):  # NaN or Inf
            return False

    # Check returns are reasonable (not > 1000% or < -100%)
    for r in returns:
        if r > 10.0 or r < -1.0:
            return False

    return True


def validate_sharpe_ratio(sharpe: float) -> bool:
    """
    Validate Sharpe ratio is reasonable.

    Args:
        sharpe: Sharpe ratio

    Returns:
        True if reasonable (between -10 and 10)
    """
    return -10.0 <= sharpe <= 10.0


def validate_volatility(volatility: float) -> bool:
    """
    Validate volatility is reasonable.

    Args:
        volatility: Annual volatility

    Returns:
        True if reasonable (between 0% and 500%)
    """
    return 0.0 <= volatility <= 5.0


def validate_symbol(symbol: str) -> bool:
    """
    Validate stock symbol format.

    Args:
        symbol: Stock symbol

    Returns:
        True if valid format
    """
    if not symbol:
        return False

    # Should be uppercase letters, 1-5 characters
    if not (1 <= len(symbol) <= 5):
        return False

    if not symbol.isalpha():
        return False

    return True


def validate_transaction_cost(cost_bps: float) -> bool:
    """
    Validate transaction cost in basis points.

    Args:
        cost_bps: Transaction cost in bps

    Returns:
        True if reasonable (0-1000 bps = 0-10%)
    """
    return 0.0 <= cost_bps <= 1000.0


def check_data_quality(
    data: List[Any],
    min_length: Optional[int] = None,
    max_nan_pct: float = 0.05
) -> Dict[str, Any]:
    """
    Check data quality and return metrics.

    Args:
        data: Data to check
        min_length: Minimum required length
        max_nan_pct: Maximum allowed NaN percentage

    Returns:
        Dictionary with quality metrics

    Example:
        >>> check_data_quality([1, 2, None, 4, 5], min_length=3)
        {'is_valid': True, 'length': 5, 'nan_count': 1, 'nan_pct': 0.2}
    """
    length = len(data)

    # Count NaNs
    nan_count = sum(1 for x in data if x is None or (isinstance(x, float) and x != x))
    nan_pct = nan_count / length if length > 0 else 0

    is_valid = True
    if min_length is not None and length < min_length:
        is_valid = False
    if nan_pct > max_nan_pct:
        is_valid = False

    return {
        'is_valid': is_valid,
        'length': length,
        'nan_count': nan_count,
        'nan_pct': nan_pct
    }
