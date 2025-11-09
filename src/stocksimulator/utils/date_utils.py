"""
Date utility functions

Utilities for working with dates in financial calculations.
"""

from datetime import date, datetime, timedelta
from typing import List, Optional


def parse_date(date_str: str) -> date:
    """
    Parse date string in various formats.

    Supports formats:
    - YYYY-MM-DD
    - YYYY/MM/DD
    - DD-MM-YYYY
    - DD/MM/YYYY
    - MM-DD-YYYY
    - MM/DD/YYYY

    Args:
        date_str: Date string to parse

    Returns:
        date object

    Raises:
        ValueError: If date string cannot be parsed

    Example:
        >>> parse_date("2024-01-15")
        date(2024, 1, 15)
    """
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m-%d-%Y",
        "%m/%d/%Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    raise ValueError(f"Unable to parse date: {date_str}")


def trading_days_between(start_date: date, end_date: date) -> int:
    """
    Calculate approximate number of trading days between two dates.

    Assumes 252 trading days per year.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        Approximate number of trading days

    Example:
        >>> trading_days_between(date(2024, 1, 1), date(2025, 1, 1))
        252
    """
    days = (end_date - start_date).days
    return int(days * 252 / 365.25)


def add_trading_days(start_date: date, trading_days: int) -> date:
    """
    Add trading days to a date.

    Approximates by converting trading days to calendar days.

    Args:
        start_date: Starting date
        trading_days: Number of trading days to add

    Returns:
        New date

    Example:
        >>> add_trading_days(date(2024, 1, 1), 252)
        date(2025, 1, 1)
    """
    calendar_days = int(trading_days * 365.25 / 252)
    return start_date + timedelta(days=calendar_days)


def get_year_from_date(d: date) -> int:
    """Get year from date."""
    return d.year


def get_month_from_date(d: date) -> int:
    """Get month from date."""
    return d.month


def get_day_from_date(d: date) -> int:
    """Get day from date."""
    return d.day


def is_weekend(d: date) -> bool:
    """
    Check if date is a weekend.

    Args:
        d: Date to check

    Returns:
        True if Saturday or Sunday
    """
    return d.weekday() >= 5


def next_business_day(d: date) -> date:
    """
    Get next business day (skip weekends).

    Args:
        d: Current date

    Returns:
        Next business day

    Example:
        >>> next_business_day(date(2024, 1, 5))  # Friday
        date(2024, 1, 8)  # Monday
    """
    next_day = d + timedelta(days=1)
    while is_weekend(next_day):
        next_day += timedelta(days=1)
    return next_day


def previous_business_day(d: date) -> date:
    """
    Get previous business day (skip weekends).

    Args:
        d: Current date

    Returns:
        Previous business day
    """
    prev_day = d - timedelta(days=1)
    while is_weekend(prev_day):
        prev_day -= timedelta(days=1)
    return prev_day


def generate_date_range(
    start_date: date,
    end_date: date,
    frequency: str = 'daily'
) -> List[date]:
    """
    Generate date range with specified frequency.

    Args:
        start_date: Start date
        end_date: End date
        frequency: 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'

    Returns:
        List of dates

    Example:
        >>> dates = generate_date_range(date(2024, 1, 1), date(2024, 3, 1), 'monthly')
        >>> len(dates)
        3
    """
    dates = []
    current = start_date

    if frequency == 'daily':
        step = timedelta(days=1)
    elif frequency == 'weekly':
        step = timedelta(days=7)
    elif frequency == 'monthly':
        step = timedelta(days=30)
    elif frequency == 'quarterly':
        step = timedelta(days=90)
    elif frequency == 'yearly':
        step = timedelta(days=365)
    else:
        raise ValueError(f"Unknown frequency: {frequency}")

    while current <= end_date:
        dates.append(current)
        current += step

    return dates


def get_quarter(d: date) -> int:
    """
    Get quarter number (1-4) for a date.

    Args:
        d: Date

    Returns:
        Quarter number (1, 2, 3, or 4)

    Example:
        >>> get_quarter(date(2024, 3, 15))
        1
    """
    return (d.month - 1) // 3 + 1


def get_year_start(d: date) -> date:
    """Get first day of year for given date."""
    return date(d.year, 1, 1)


def get_year_end(d: date) -> date:
    """Get last day of year for given date."""
    return date(d.year, 12, 31)


def days_in_year(year: int) -> int:
    """
    Get number of days in a year.

    Args:
        year: Year

    Returns:
        366 for leap years, 365 otherwise
    """
    return 366 if is_leap_year(year) else 365


def is_leap_year(year: int) -> bool:
    """
    Check if year is a leap year.

    Args:
        year: Year to check

    Returns:
        True if leap year
    """
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def format_date(d: date, format_str: str = "%Y-%m-%d") -> str:
    """
    Format date as string.

    Args:
        d: Date to format
        format_str: Format string (default: YYYY-MM-DD)

    Returns:
        Formatted date string

    Example:
        >>> format_date(date(2024, 1, 15))
        '2024-01-15'
    """
    return d.strftime(format_str)
