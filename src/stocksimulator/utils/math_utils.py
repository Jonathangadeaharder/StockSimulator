"""
Mathematical utility functions

Common mathematical operations for financial calculations.
"""

from typing import List, Optional, Tuple
import math


def calculate_percentile(data: List[float], percentile: float) -> float:
    """
    Calculate percentile without numpy.

    Uses linear interpolation between data points.

    Args:
        data: List of values
        percentile: Percentile to calculate (0-100)

    Returns:
        Percentile value

    Example:
        >>> calculate_percentile([1, 2, 3, 4, 5], 50)
        3.0
    """
    if not data:
        return 0.0

    sorted_data = sorted(data)
    n = len(sorted_data)

    if n == 1:
        return sorted_data[0]

    k = (n - 1) * percentile / 100
    f = int(k)
    c = k - f

    if f + 1 < n:
        return sorted_data[f] + c * (sorted_data[f + 1] - sorted_data[f])
    else:
        return sorted_data[f]


def calculate_mean(data: List[float]) -> float:
    """
    Calculate arithmetic mean.

    Args:
        data: List of values

    Returns:
        Mean value
    """
    if not data:
        return 0.0
    return sum(data) / len(data)


def calculate_variance(data: List[float], sample: bool = True) -> float:
    """
    Calculate variance.

    Args:
        data: List of values
        sample: If True, use sample variance (n-1), else population variance (n)

    Returns:
        Variance
    """
    if len(data) < 2:
        return 0.0

    mean = calculate_mean(data)
    divisor = len(data) - 1 if sample else len(data)

    return sum((x - mean) ** 2 for x in data) / divisor


def calculate_std_dev(data: List[float], sample: bool = True) -> float:
    """
    Calculate standard deviation.

    Args:
        data: List of values
        sample: If True, use sample std dev (n-1), else population (n)

    Returns:
        Standard deviation
    """
    return math.sqrt(calculate_variance(data, sample=sample))


def calculate_sharpe(
    returns: List[float],
    risk_free_rate: float = 0.02,
    periods_per_year: int = 252
) -> float:
    """
    Calculate Sharpe ratio.

    Args:
        returns: List of period returns
        risk_free_rate: Annual risk-free rate
        periods_per_year: Periods per year (252 for daily)

    Returns:
        Sharpe ratio
    """
    if len(returns) < 2:
        return 0.0

    mean_return = calculate_mean(returns)
    annualized_return = (1 + mean_return) ** periods_per_year - 1

    std_dev = calculate_std_dev(returns, sample=True)
    annualized_vol = std_dev * math.sqrt(periods_per_year)

    if annualized_vol == 0:
        return 0.0

    return (annualized_return - risk_free_rate) / annualized_vol


def calculate_correlation(x: List[float], y: List[float]) -> float:
    """
    Calculate Pearson correlation coefficient.

    Args:
        x: First data series
        y: Second data series

    Returns:
        Correlation coefficient (-1 to 1)
    """
    if len(x) != len(y) or len(x) < 2:
        return 0.0

    mean_x = calculate_mean(x)
    mean_y = calculate_mean(y)

    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))

    var_x = sum((xi - mean_x) ** 2 for xi in x)
    var_y = sum((yi - mean_y) ** 2 for yi in y)

    denominator = math.sqrt(var_x * var_y)

    if denominator == 0:
        return 0.0

    corr = numerator / denominator
    return max(-1.0, min(1.0, corr))  # Clamp to [-1, 1]


def calculate_covariance(x: List[float], y: List[float], sample: bool = True) -> float:
    """
    Calculate covariance between two series.

    Args:
        x: First data series
        y: Second data series
        sample: If True, use sample covariance (n-1)

    Returns:
        Covariance
    """
    if len(x) != len(y) or len(x) < 2:
        return 0.0

    mean_x = calculate_mean(x)
    mean_y = calculate_mean(y)

    divisor = len(x) - 1 if sample else len(x)

    return sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y)) / divisor


def compound_returns(returns: List[float]) -> float:
    """
    Calculate compound return from series of returns.

    Args:
        returns: List of period returns

    Returns:
        Compound return

    Example:
        >>> compound_returns([0.10, 0.05, -0.03])
        0.1179  # (1.10 * 1.05 * 0.97) - 1
    """
    if not returns:
        return 0.0

    compound = 1.0
    for r in returns:
        compound *= (1 + r)

    return compound - 1.0


def annualize_return(total_return: float, years: float) -> float:
    """
    Annualize a total return.

    Args:
        total_return: Total return (e.g., 0.50 for 50%)
        years: Number of years

    Returns:
        Annualized return

    Example:
        >>> annualize_return(0.50, 2.0)
        0.2247  # ~22.47% annual
    """
    if years <= 0:
        return 0.0

    return (1 + total_return) ** (1 / years) - 1


def calculate_drawdown(values: List[float]) -> List[float]:
    """
    Calculate drawdown series.

    Args:
        values: Series of portfolio values

    Returns:
        List of drawdowns at each point

    Example:
        >>> calculate_drawdown([100, 110, 105, 115])
        [0.0, 0.0, 0.045, 0.0]  # -4.5% from peak of 110
    """
    if not values:
        return []

    drawdowns = []
    peak = values[0]

    for value in values:
        if value > peak:
            peak = value

        drawdown = (peak - value) / peak if peak > 0 else 0.0
        drawdowns.append(drawdown)

    return drawdowns


def max_consecutive(data: List[bool]) -> int:
    """
    Find maximum consecutive True values.

    Args:
        data: List of boolean values

    Returns:
        Maximum consecutive count

    Example:
        >>> max_consecutive([True, True, False, True, True, True])
        3
    """
    if not data:
        return 0

    max_count = 0
    current_count = 0

    for value in data:
        if value:
            current_count += 1
            max_count = max(max_count, current_count)
        else:
            current_count = 0

    return max_count


def geometric_mean(values: List[float]) -> float:
    """
    Calculate geometric mean.

    Args:
        values: List of positive values

    Returns:
        Geometric mean

    Example:
        >>> geometric_mean([2, 8])
        4.0
    """
    if not values or any(v <= 0 for v in values):
        return 0.0

    product = 1.0
    for v in values:
        product *= v

    return product ** (1.0 / len(values))


def linear_regression(x: List[float], y: List[float]) -> Tuple[float, float]:
    """
    Simple linear regression (y = mx + b).

    Args:
        x: Independent variable
        y: Dependent variable

    Returns:
        Tuple of (slope, intercept)

    Example:
        >>> linear_regression([1, 2, 3], [2, 4, 6])
        (2.0, 0.0)
    """
    if len(x) != len(y) or len(x) < 2:
        return (0.0, 0.0)

    n = len(x)
    mean_x = calculate_mean(x)
    mean_y = calculate_mean(y)

    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    denominator = sum((xi - mean_x) ** 2 for xi in x)

    if denominator == 0:
        return (0.0, mean_y)

    slope = numerator / denominator
    intercept = mean_y - slope * mean_x

    return (slope, intercept)


def moving_average(data: List[float], period: int) -> List[float]:
    """
    Calculate simple moving average.

    Args:
        data: Data series
        period: Moving average period

    Returns:
        List of moving averages (NaN for insufficient data)

    Example:
        >>> moving_average([1, 2, 3, 4, 5], 3)
        [nan, nan, 2.0, 3.0, 4.0]
    """
    if period <= 0:
        return []

    result = []

    for i in range(len(data)):
        if i < period - 1:
            result.append(float('nan'))
        else:
            window = data[i - period + 1:i + 1]
            result.append(calculate_mean(window))

    return result


def exponential_moving_average(data: List[float], period: int) -> List[float]:
    """
    Calculate exponential moving average.

    Args:
        data: Data series
        period: EMA period

    Returns:
        List of EMA values

    Example:
        >>> ema = exponential_moving_average([1, 2, 3, 4, 5], 3)
    """
    if not data or period <= 0:
        return []

    alpha = 2.0 / (period + 1)
    result = []
    ema = data[0]

    for value in data:
        ema = alpha * value + (1 - alpha) * ema
        result.append(ema)

    return result


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp value between min and max.

    Args:
        value: Value to clamp
        min_value: Minimum value
        max_value: Maximum value

    Returns:
        Clamped value
    """
    return max(min_value, min(max_value, value))


def normalize(data: List[float], target_min: float = 0.0, target_max: float = 1.0) -> List[float]:
    """
    Normalize data to target range.

    Args:
        data: Data to normalize
        target_min: Target minimum value
        target_max: Target maximum value

    Returns:
        Normalized data
    """
    if not data:
        return []

    data_min = min(data)
    data_max = max(data)

    if data_max == data_min:
        return [target_min] * len(data)

    range_data = data_max - data_min
    range_target = target_max - target_min

    return [
        target_min + (x - data_min) * range_target / range_data
        for x in data
    ]
