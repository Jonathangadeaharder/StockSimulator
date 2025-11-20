"""
Multi-Asset Class Data Loader

Provides access to diverse asset classes for portfolio construction:
- Equity Indices (S&P 500, World, Low Vol)
- Fixed Income (Long Treasuries, Short-Term Bonds)
- Alternatives (Managed Futures, Consumer Staples)
- Synthetic (Leveraged, Short positions)

Includes simulators for asset classes without direct historical data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from datetime import date, datetime
from dataclasses import dataclass


@dataclass
class AssetClassInfo:
    """Information about an asset class."""
    name: str
    ticker: str
    description: str
    data_source: str  # 'file', 'synthetic', 'simulated'
    file_path: Optional[str] = None
    volatility: Optional[float] = None  # Annualized volatility for synthetic assets
    correlation_with_market: Optional[float] = None


class AssetClassRegistry:
    """
    Registry of available asset classes with their data sources.

    Maps asset class names to their data sources and provides
    information about availability and quality.
    """

    # Asset class definitions
    ASSET_CLASSES = {
        # Equity Indices (Historical Data Available)
        'SP500': AssetClassInfo(
            name='S&P 500',
            ticker='SPY',
            description='U.S. Large Cap Equities',
            data_source='file',
            file_path='historical_data/sp500_stooq_daily.csv'
        ),

        'WORLD': AssetClassInfo(
            name='World Index',
            ticker='URTH',
            description='MSCI World Developed Markets',
            data_source='file',
            file_path='historical_data/msci_world_urth_stooq_daily.csv'
        ),

        'ACWI': AssetClassInfo(
            name='All Country World Index',
            ticker='ACWI',
            description='MSCI All Country World (Developed + Emerging)',
            data_source='file',
            file_path='historical_data/msci_acwi_stooq_daily.csv'
        ),

        # Leveraged & Short Positions (Synthetic)
        'SP500_2X': AssetClassInfo(
            name='2x S&P 500',
            ticker='SSO',
            description='2x Leveraged S&P 500',
            data_source='synthetic',
            volatility=0.32,  # ~2x the S&P vol
            correlation_with_market=0.99
        ),

        'SP500_3X': AssetClassInfo(
            name='3x S&P 500',
            ticker='UPRO',
            description='3x Leveraged S&P 500',
            data_source='synthetic',
            volatility=0.48,  # ~3x the S&P vol
            correlation_with_market=0.99
        ),

        'SP500_SHORT': AssetClassInfo(
            name='Short S&P 500',
            ticker='SH',
            description='Inverse S&P 500 (-1x)',
            data_source='synthetic',
            volatility=0.16,
            correlation_with_market=-0.99
        ),

        'WORLD_2X': AssetClassInfo(
            name='2x World Index',
            ticker='WORLD_2X',
            description='2x Leveraged World Index',
            data_source='synthetic',
            volatility=0.30,
            correlation_with_market=0.99
        ),

        'WORLD_SHORT': AssetClassInfo(
            name='Short World Index',
            ticker='WORLD_SHORT',
            description='Inverse World Index (-1x)',
            data_source='synthetic',
            volatility=0.15,
            correlation_with_market=-0.99
        ),

        # Fixed Income (Simulated based on research)
        'LONG_TREASURY': AssetClassInfo(
            name='Long-Term Treasuries',
            ticker='TLT',
            description='20+ Year U.S. Treasury Bonds',
            data_source='simulated',
            volatility=0.14,  # Historical long treasury vol
            correlation_with_market=-0.15  # Typically negative correlation
        ),

        'SHORT_BOND': AssetClassInfo(
            name='Short-Term Bonds',
            ticker='SHY',
            description='1-3 Year U.S. Treasury Bonds',
            data_source='simulated',
            volatility=0.02,  # Very low volatility
            correlation_with_market=0.05  # Near-zero correlation
        ),

        # Alternative Strategies (Simulated)
        'MANAGED_FUTURES': AssetClassInfo(
            name='Managed Futures',
            ticker='CTA',
            description='Trend-Following Commodity Trading Advisors',
            data_source='simulated',
            volatility=0.12,
            correlation_with_market=0.0  # Zero correlation by design
        ),

        # Sector Indices (Simulated)
        'CONSUMER_STAPLES': AssetClassInfo(
            name='Consumer Staples',
            ticker='XLP',
            description='Consumer Staples Sector (Defensive)',
            data_source='simulated',
            volatility=0.11,  # Lower vol than market
            correlation_with_market=0.65  # Moderate correlation
        ),

        'LOW_VOL': AssetClassInfo(
            name='Low Volatility',
            ticker='SPLV',
            description='S&P 500 Low Volatility Index',
            data_source='simulated',
            volatility=0.10,  # By definition, low vol
            correlation_with_market=0.75  # Still correlated but less volatile
        ),
    }

    @classmethod
    def get_available_assets(cls) -> List[str]:
        """Get list of all available asset class tickers."""
        return list(cls.ASSET_CLASSES.keys())

    @classmethod
    def get_info(cls, ticker: str) -> AssetClassInfo:
        """Get information about an asset class."""
        if ticker not in cls.ASSET_CLASSES:
            raise ValueError(f"Unknown asset class: {ticker}. "
                           f"Available: {cls.get_available_assets()}")
        return cls.ASSET_CLASSES[ticker]

    @classmethod
    def get_by_type(cls, data_source: str) -> List[str]:
        """Get asset classes by data source type."""
        return [ticker for ticker, info in cls.ASSET_CLASSES.items()
                if info.data_source == data_source]


class MultiAssetDataLoader:
    """
    Loads and manages multi-asset class data.

    Handles both historical data files and synthetic/simulated assets.
    """

    def __init__(self, base_path: str = '/home/user/StockSimulator'):
        """
        Initialize data loader.

        Args:
            base_path: Base path to StockSimulator directory
        """
        self.base_path = Path(base_path)
        self._cache = {}

    def load_asset(
        self,
        ticker: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """
        Load asset class data.

        Args:
            ticker: Asset class ticker (from AssetClassRegistry)
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            DataFrame with columns: Date, Open, High, Low, Close, Volume
        """
        info = AssetClassRegistry.get_info(ticker)

        # Check cache
        cache_key = f"{ticker}_{start_date}_{end_date}"
        if cache_key in self._cache:
            return self._cache[cache_key].copy()

        # Load based on data source
        if info.data_source == 'file':
            df = self._load_from_file(info)
        elif info.data_source == 'synthetic':
            df = self._create_synthetic(ticker, info)
        elif info.data_source == 'simulated':
            df = self._create_simulated(ticker, info)
        else:
            raise ValueError(f"Unknown data source: {info.data_source}")

        # Filter by date range
        if start_date or end_date:
            df = self._filter_dates(df, start_date, end_date)

        # Cache and return
        self._cache[cache_key] = df.copy()
        return df

    def load_multiple(
        self,
        tickers: List[str],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        align_dates: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        Load multiple asset classes.

        Args:
            tickers: List of asset class tickers
            start_date: Start date
            end_date: End date
            align_dates: If True, align all assets to common dates

        Returns:
            Dictionary mapping ticker -> DataFrame
        """
        data = {}
        for ticker in tickers:
            data[ticker] = self.load_asset(ticker, start_date, end_date)

        if align_dates and len(data) > 1:
            data = self._align_dates(data)

        return data

    def _load_from_file(self, info: AssetClassInfo) -> pd.DataFrame:
        """Load data from CSV file."""
        file_path = self.base_path / info.file_path

        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")

        df = pd.read_csv(file_path)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date').reset_index(drop=True)

        return df

    def _create_synthetic(self, ticker: str, info: AssetClassInfo) -> pd.DataFrame:
        """
        Create synthetic leveraged or short positions.

        Synthesizes from underlying index with leverage/short multiplier.
        """
        # Determine base index
        if 'SP500' in ticker:
            base_ticker = 'SP500'
        elif 'WORLD' in ticker:
            base_ticker = 'WORLD'
        else:
            raise ValueError(f"Cannot determine base index for {ticker}")

        # Load base index
        base_df = self.load_asset(base_ticker)

        # Determine multiplier
        if '2X' in ticker:
            multiplier = 2.0
        elif '3X' in ticker:
            multiplier = 3.0
        elif 'SHORT' in ticker:
            multiplier = -1.0
        else:
            multiplier = 1.0

        # Calculate leveraged returns
        df = base_df.copy()
        base_returns = df['Close'].pct_change()

        # Apply leverage with realistic costs
        if abs(multiplier) > 1:
            # Add financing costs for leverage (from Phase 1 knowledge)
            daily_cost = 0.015 / 252  # 1.5% annual excess cost
            leveraged_returns = base_returns * multiplier - daily_cost * abs(multiplier - 1)
        else:
            leveraged_returns = base_returns * multiplier

        # Reconstruct price series
        initial_price = 100.0
        df['Close'] = initial_price * (1 + leveraged_returns).cumprod()
        df['Close'] = df['Close'].fillna(initial_price)

        # Approximate OHLC from close
        daily_range = df['Close'] * 0.01  # 1% daily range approximation
        df['Open'] = df['Close']
        df['High'] = df['Close'] + daily_range / 2
        df['Low'] = df['Close'] - daily_range / 2
        df['Volume'] = 0  # Not applicable for synthetic

        return df

    def _create_simulated(self, ticker: str, info: AssetClassInfo) -> pd.DataFrame:
        """
        Create simulated asset class based on historical characteristics.

        Uses S&P 500 dates as template and simulates returns based on
        volatility and correlation parameters.
        """
        # Load S&P 500 as date template
        sp500 = self.load_asset('SP500')
        dates = sp500['Date'].values

        # Load market returns for correlation
        market_returns = sp500['Close'].pct_change().fillna(0).values

        # Simulate returns based on characteristics
        np.random.seed(42)  # Reproducible

        n_days = len(dates)
        daily_vol = info.volatility / np.sqrt(252)

        # Generate correlated returns
        if info.correlation_with_market is not None and info.correlation_with_market != 0:
            # Correlated component
            corr = info.correlation_with_market
            market_component = market_returns * corr

            # Independent component
            independent = np.random.normal(0, daily_vol * np.sqrt(1 - corr**2), n_days)

            simulated_returns = market_component + independent
        else:
            # Pure independent returns
            simulated_returns = np.random.normal(0, daily_vol, n_days)

        # Add asset-specific characteristics
        if ticker == 'MANAGED_FUTURES':
            # Managed futures: trend-following behavior
            # Positive during crises (2008, 2020) due to trend-following
            simulated_returns = self._add_crisis_alpha(simulated_returns, sp500['Date'].values, market_returns)

        elif ticker == 'LONG_TREASURY':
            # Long treasuries: flight to safety
            # Inverse correlation strengthens during crises
            crisis_mask = self._identify_crisis_periods(sp500['Date'].values)
            simulated_returns[crisis_mask] = -0.7 * market_returns[crisis_mask] + np.random.normal(0, daily_vol * 0.5, crisis_mask.sum())

        elif ticker == 'SHORT_BOND':
            # Short bonds: stable returns, low correlation
            # Essentially risk-free rate
            risk_free_daily = 0.02 / 252  # 2% annual
            simulated_returns = np.random.normal(risk_free_daily, daily_vol, n_days)

        elif ticker == 'CONSUMER_STAPLES':
            # Consumer staples: defensive, outperforms in downturns
            crisis_mask = self._identify_crisis_periods(sp500['Date'].values)
            simulated_returns[crisis_mask] = 0.5 * market_returns[crisis_mask]  # Half the drawdown

        elif ticker == 'LOW_VOL':
            # Low vol: lower beta, especially in downturns
            simulated_returns = 0.7 * market_returns + np.random.normal(0, daily_vol * 0.3, n_days)

        # Build price series
        initial_price = 100.0
        prices = initial_price * (1 + simulated_returns).cumprod()

        # Create DataFrame
        df = pd.DataFrame({
            'Date': dates,
            'Close': prices,
            'Open': prices,
            'High': prices * 1.005,
            'Low': prices * 0.995,
            'Volume': 0
        })

        return df

    def _add_crisis_alpha(
        self,
        returns: np.ndarray,
        dates: np.ndarray,
        market_returns: np.ndarray
    ) -> np.ndarray:
        """
        Add crisis alpha for managed futures.

        Managed futures historically provide positive returns during crises
        due to trend-following strategies.
        """
        crisis_mask = self._identify_crisis_periods(dates)

        # Add positive alpha during crises
        returns = returns.copy()
        returns[crisis_mask] += 0.02 / 252  # +2% annualized alpha during crisis

        return returns

    def _identify_crisis_periods(self, dates: np.ndarray) -> np.ndarray:
        """Identify major crisis periods."""
        dates_dt = pd.to_datetime(dates)

        crisis_periods = [
            ('2000-03-01', '2002-10-31'),  # Dot-com crash
            ('2007-10-01', '2009-03-31'),  # Financial crisis
            ('2020-02-01', '2020-04-30'),  # COVID crash
            ('2022-01-01', '2022-10-31'),  # 2022 bear market
        ]

        mask = np.zeros(len(dates), dtype=bool)

        for start, end in crisis_periods:
            start_dt = pd.to_datetime(start)
            end_dt = pd.to_datetime(end)
            mask |= (dates_dt >= start_dt) & (dates_dt <= end_dt)

        return mask

    def _filter_dates(
        self,
        df: pd.DataFrame,
        start_date: Optional[date],
        end_date: Optional[date]
    ) -> pd.DataFrame:
        """Filter DataFrame by date range."""
        df = df.copy()

        if start_date:
            df = df[df['Date'] >= pd.Timestamp(start_date)]

        if end_date:
            df = df[df['Date'] <= pd.Timestamp(end_date)]

        return df.reset_index(drop=True)

    def _align_dates(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Align all DataFrames to common date range."""
        # Find common dates
        all_dates = None
        for df in data.values():
            dates = set(df['Date'].values)
            if all_dates is None:
                all_dates = dates
            else:
                all_dates &= dates

        # Filter each DataFrame to common dates
        aligned = {}
        for ticker, df in data.items():
            aligned[ticker] = df[df['Date'].isin(all_dates)].reset_index(drop=True)

        return aligned


def print_asset_summary():
    """Print summary of all available asset classes."""
    print("\n" + "="*80)
    print("AVAILABLE ASSET CLASSES")
    print("="*80 + "\n")

    # Group by data source
    by_source = {
        'file': [],
        'synthetic': [],
        'simulated': []
    }

    for ticker, info in AssetClassRegistry.ASSET_CLASSES.items():
        by_source[info.data_source].append((ticker, info))

    for source in ['file', 'synthetic', 'simulated']:
        print(f"\n{source.upper()} DATA:")
        print("-" * 80)

        for ticker, info in by_source[source]:
            print(f"\n{ticker:20} {info.name}")
            print(f"{'':20} {info.description}")
            if info.volatility:
                print(f"{'':20} Vol: {info.volatility:.1%}, Corr: {info.correlation_with_market:.2f}")

    print("\n" + "="*80)


if __name__ == '__main__':
    # Demo
    print_asset_summary()

    loader = MultiAssetDataLoader()

    # Load a few assets
    print("\n\nLoading sample assets...")
    assets = loader.load_multiple(
        ['SP500', 'SP500_2X', 'LONG_TREASURY', 'MANAGED_FUTURES'],
        start_date=date(2000, 1, 1),
        end_date=date(2023, 12, 31)
    )

    for ticker, df in assets.items():
        print(f"\n{ticker}: {len(df)} days, {df['Date'].min()} to {df['Date'].max()}")
        returns = df['Close'].pct_change().dropna()
        print(f"  Return: {(df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100:.1f}%")
        print(f"  Volatility: {returns.std() * np.sqrt(252):.1%}")
