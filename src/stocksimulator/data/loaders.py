"""
Data Loaders

Load market data from various sources into MarketData objects.
"""

import csv
import os
from datetime import datetime, date
from typing import Dict, List, Optional

from stocksimulator.models.market_data import MarketData, OHLCV


class CSVLoader:
    """
    Load market data from CSV files.

    Supports various CSV formats including those from Stooq, Yahoo Finance, etc.
    """

    def __init__(self, base_path: str = 'historical_data'):
        """
        Initialize CSV loader.

        Args:
            base_path: Base directory for CSV files
        """
        self.base_path = base_path

    def load(
        self,
        filepath: str,
        symbol: Optional[str] = None,
        date_col: str = 'Date',
        open_col: str = 'Open',
        high_col: str = 'High',
        low_col: str = 'Low',
        close_col: str = 'Close',
        volume_col: str = 'Volume',
        date_format: str = '%Y-%m-%d'
    ) -> MarketData:
        """
        Load market data from CSV file.

        Args:
            filepath: Path to CSV file (relative to base_path or absolute)
            symbol: Symbol name (auto-detected from filename if None)
            date_col: Name of date column
            open_col: Name of open price column
            high_col: Name of high price column
            low_col: Name of low price column
            close_col: Name of close price column
            volume_col: Name of volume column
            date_format: Date format string

        Returns:
            MarketData object

        Example:
            >>> loader = CSVLoader('historical_data')
            >>> spy_data = loader.load('sp500_stooq_daily.csv', symbol='SPY')
        """
        # Build full path
        if not os.path.isabs(filepath):
            filepath = os.path.join(self.base_path, filepath)

        # Auto-detect symbol from filename if not provided
        if symbol is None:
            filename = os.path.basename(filepath)
            # Try to extract symbol from filename
            # e.g., "sp500_stooq_daily.csv" -> "SP500"
            symbol = filename.split('_')[0].upper()

        data_points = []

        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    # Parse date
                    date_str = row[date_col]
                    dt = datetime.strptime(date_str, date_format).date()

                    # Parse prices (use close if others not available)
                    close = float(row.get(close_col, 0))
                    open_price = float(row.get(open_col, close))
                    high = float(row.get(high_col, close))
                    low = float(row.get(low_col, close))

                    # Parse volume (default to 0 if not available)
                    volume_str = row.get(volume_col, '0')
                    volume = int(float(volume_str)) if volume_str and volume_str != '' else 0

                    # Create OHLCV
                    ohlcv = OHLCV(
                        date=dt,
                        open=open_price,
                        high=high,
                        low=low,
                        close=close,
                        volume=volume,
                        adjusted_close=close  # Use close as adjusted_close
                    )

                    data_points.append(ohlcv)

                except (ValueError, KeyError) as e:
                    # Skip rows with parsing errors
                    continue

        # Sort by date
        data_points.sort(key=lambda x: x.date)

        return MarketData(
            symbol=symbol,
            data=data_points,
            metadata={
                'source': 'csv',
                'filepath': filepath,
                'num_points': len(data_points),
                'start_date': data_points[0].date.isoformat() if data_points else None,
                'end_date': data_points[-1].date.isoformat() if data_points else None
            }
        )

    def load_stooq_format(self, filepath: str, symbol: Optional[str] = None) -> MarketData:
        """
        Load data in Stooq format (Date,Open,High,Low,Close,Volume).

        Args:
            filepath: Path to CSV file
            symbol: Symbol name

        Returns:
            MarketData object
        """
        return self.load(
            filepath=filepath,
            symbol=symbol,
            date_col='Date',
            open_col='Open',
            high_col='High',
            low_col='Low',
            close_col='Close',
            volume_col='Volume'
        )


def load_from_csv(
    filepath: str,
    symbol: Optional[str] = None,
    base_path: str = 'historical_data'
) -> MarketData:
    """
    Quick helper to load market data from CSV.

    Args:
        filepath: Path to CSV file
        symbol: Symbol name (auto-detected if None)
        base_path: Base directory for CSV files

    Returns:
        MarketData object

    Example:
        >>> spy_data = load_from_csv('sp500_stooq_daily.csv', 'SPY')
    """
    loader = CSVLoader(base_path=base_path)
    return loader.load(filepath, symbol=symbol)


def load_multiple_csv(
    filepaths: Dict[str, str],
    base_path: str = 'historical_data'
) -> Dict[str, MarketData]:
    """
    Load multiple CSV files at once.

    Args:
        filepaths: Dictionary of symbol -> filepath
        base_path: Base directory for CSV files

    Returns:
        Dictionary of symbol -> MarketData

    Example:
        >>> data = load_multiple_csv({
        ...     'SPY': 'sp500_stooq_daily.csv',
        ...     'TLT': 'tlt_data.csv'
        ... })
    """
    loader = CSVLoader(base_path=base_path)
    result = {}

    for symbol, filepath in filepaths.items():
        try:
            result[symbol] = loader.load(filepath, symbol=symbol)
        except Exception as e:
            print(f"Warning: Failed to load {symbol} from {filepath}: {e}")

    return result


def discover_csv_files(directory: str = 'historical_data') -> Dict[str, str]:
    """
    Auto-discover CSV files in a directory.

    Args:
        directory: Directory to search

    Returns:
        Dictionary of detected symbol -> filepath

    Example:
        >>> files = discover_csv_files('historical_data')
        >>> print(files)
        {'SP500': 'sp500_stooq_daily.csv', 'NASDAQ': 'nasdaq_data.csv'}
    """
    discovered = {}

    if not os.path.exists(directory):
        return discovered

    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            # Try to extract symbol from filename
            base_name = filename.replace('.csv', '')
            parts = base_name.split('_')

            # Use first part as symbol
            symbol = parts[0].upper()
            discovered[symbol] = filename

    return discovered


def load_all_available(base_path: str = 'historical_data') -> Dict[str, MarketData]:
    """
    Load all available CSV files from directory.

    Args:
        base_path: Directory to search

    Returns:
        Dictionary of symbol -> MarketData

    Example:
        >>> all_data = load_all_available('historical_data')
        >>> print(f"Loaded {len(all_data)} datasets")
    """
    files = discover_csv_files(base_path)
    return load_multiple_csv(files, base_path=base_path)


def get_available_symbols(base_path: str = 'historical_data') -> List[str]:
    """
    Get list of available symbols in CSV directory.

    Args:
        base_path: Directory to search

    Returns:
        List of available symbols

    Example:
        >>> symbols = get_available_symbols()
        >>> print(f"Available: {', '.join(symbols)}")
    """
    files = discover_csv_files(base_path)
    return sorted(files.keys())
