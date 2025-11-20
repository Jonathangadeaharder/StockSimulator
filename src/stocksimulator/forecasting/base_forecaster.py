"""
Base forecaster classes for return and risk forecasting.

Phase 2 Enhancement: Provides abstract interface for forecasters
that work with causality-safe data.
"""

from abc import ABC, abstractmethod
from typing import Dict
from datetime import date
import pandas as pd
import numpy as np


class BaseForecastor(ABC):
    """
    Abstract base class for return/risk forecasters.

    Phase 2 Enhancement: Inspired by CVXPortfolio's forecaster pattern.

    Forecasters take historical data and produce forecasts for expected
    returns and covariance matrices. All forecasters must work with
    causality-safe data only.
    """

    @abstractmethod
    def forecast_returns(
        self,
        historical_data: Dict[str, pd.DataFrame],
        current_date: date
    ) -> Dict[str, float]:
        """
        Forecast expected returns using only historical data.

        Args:
            historical_data: Dict of symbol -> historical DataFrame
                            (causality-safe, no future data)
            current_date: Current date (for context, not for data access)

        Returns:
            Dict of symbol -> expected annual return

        Example:
            >>> forecaster = HistoricalMeanForecastor(lookback_days=252)
            >>> expected_returns = forecaster.forecast_returns(hist_data, date.today())
            >>> # {'SPY': 0.10, 'AGG': 0.04}  # 10% and 4% annual returns
        """
        pass

    @abstractmethod
    def forecast_covariance(
        self,
        historical_data: Dict[str, pd.DataFrame],
        current_date: date
    ) -> pd.DataFrame:
        """
        Forecast covariance matrix using only historical data.

        Args:
            historical_data: Dict of symbol -> historical DataFrame
            current_date: Current date

        Returns:
            DataFrame with annualized covariance matrix
            Rows and columns are symbols

        Example:
            >>> cov_matrix = forecaster.forecast_covariance(hist_data, date.today())
            >>> # DataFrame with symbols as both index and columns
            >>> #         SPY      AGG
            >>> # SPY   0.0256   0.0012
            >>> # AGG   0.0012   0.0016
        """
        pass


class HistoricalMeanForecastor(BaseForecastor):
    """
    Simple forecaster using historical mean returns and sample covariance.

    Phase 2 Enhancement: Reference implementation of BaseForecastor.

    This is the simplest forecaster - uses sample statistics from
    historical data. More sophisticated forecasters can implement
    exponential weighting, shrinkage, factor models, etc.
    """

    def __init__(self, lookback_days: int = 252, min_data_points: int = 30):
        """
        Initialize historical mean forecaster.

        Args:
            lookback_days: Number of days to use for estimates
            min_data_points: Minimum data points required for valid forecast
        """
        self.lookback_days = lookback_days
        self.min_data_points = min_data_points

    def forecast_returns(
        self,
        historical_data: Dict[str, pd.DataFrame],
        current_date: date
    ) -> Dict[str, float]:
        """
        Forecast returns using historical mean.

        Calculates arithmetic mean of historical returns and annualizes.
        """
        expected_returns = {}

        for symbol, df in historical_data.items():
            if df.empty or len(df) < self.min_data_points:
                # Insufficient data - use default (0% expected return)
                expected_returns[symbol] = 0.0
                continue

            # Use last lookback_days
            recent_df = df.tail(self.lookback_days)

            # Calculate daily returns
            returns = recent_df['close'].pct_change().dropna()

            if len(returns) < self.min_data_points:
                expected_returns[symbol] = 0.0
                continue

            # Annualize arithmetic mean
            mean_daily_return = returns.mean()
            annualized_return = mean_daily_return * 252

            expected_returns[symbol] = annualized_return

        return expected_returns

    def forecast_covariance(
        self,
        historical_data: Dict[str, pd.DataFrame],
        current_date: date
    ) -> pd.DataFrame:
        """
        Forecast covariance using sample covariance matrix.

        Calculates sample covariance from historical returns and annualizes.
        """
        # Build returns matrix
        returns_dict = {}

        for symbol, df in historical_data.items():
            if df.empty or len(df) < self.min_data_points:
                continue

            # Use last lookback_days
            recent_df = df.tail(self.lookback_days)

            # Calculate daily returns
            returns = recent_df['close'].pct_change().dropna()

            if len(returns) >= self.min_data_points:
                returns_dict[symbol] = returns

        if not returns_dict:
            # No valid data - return empty DataFrame
            return pd.DataFrame()

        # Align returns (use only dates where all symbols have data)
        returns_df = pd.DataFrame(returns_dict)

        # Sample covariance matrix
        cov_matrix = returns_df.cov()

        # Annualize (multiply by 252 trading days)
        annualized_cov = cov_matrix * 252

        return annualized_cov

    def __repr__(self) -> str:
        return (f"HistoricalMeanForecastor("
                f"lookback_days={self.lookback_days}, "
                f"min_data_points={self.min_data_points})")
