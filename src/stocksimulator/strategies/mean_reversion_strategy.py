"""
Mean Reversion Strategy

Implements mean reversion strategies that buy when prices are low
and sell when prices are high relative to historical averages.
"""

from typing import Dict, Optional
from datetime import date

from stocksimulator.strategies.base_strategy import BaseStrategy
from stocksimulator.models.portfolio import Portfolio
from stocksimulator.models.market_data import MarketData


class MeanReversionStrategy(BaseStrategy):
    """
    Mean Reversion Strategy based on Z-score.

    Buys when price is significantly below moving average,
    sells when price is significantly above moving average.

    Parameters:
        lookback_days: Period for moving average calculation
        buy_threshold: Z-score threshold to buy (default: -2.0)
        sell_threshold: Z-score threshold to sell (default: 2.0)
        allocation_per_position: How much to allocate per position

    Example:
        >>> strategy = MeanReversionStrategy(lookback_days=20, buy_threshold=-2.0)
    """

    def __init__(
        self,
        lookback_days: int = 20,
        buy_threshold: float = -2.0,
        sell_threshold: float = 2.0,
        allocation_per_position: float = 50.0,
        name: str = "Mean Reversion Strategy"
    ):
        """
        Initialize mean reversion strategy.

        Args:
            lookback_days: Lookback period for mean/std calculation
            buy_threshold: Buy when z-score below this (typically negative)
            sell_threshold: Sell when z-score above this (typically positive)
            allocation_per_position: Allocation per position (%)
            name: Strategy name
        """
        super().__init__(
            name=name,
            description=f"Mean reversion with {lookback_days}-day lookback",
            parameters={
                'lookback_days': lookback_days,
                'buy_threshold': buy_threshold,
                'sell_threshold': sell_threshold,
                'allocation_per_position': allocation_per_position
            }
        )

        self.lookback_days = lookback_days
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.allocation_per_position = allocation_per_position

    def calculate_zscore(
        self,
        market_data: MarketData,
        current_date: date,
        lookback_days: int
    ) -> Optional[float]:
        """
        Calculate Z-score (standard deviations from mean).

        Args:
            market_data: Market data
            current_date: Current date
            lookback_days: Lookback period

        Returns:
            Z-score or None if insufficient data
        """
        data = self.get_lookback_data(market_data, current_date, lookback_days)

        if len(data) < lookback_days:
            return None

        prices = [d.close for d in data]
        current_price = prices[-1]

        # Calculate mean and std
        mean_price = sum(prices) / len(prices)
        variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
        std_price = variance ** 0.5

        if std_price == 0:
            return 0.0

        # Calculate z-score
        zscore = (current_price - mean_price) / std_price

        return zscore

    def calculate_allocation(
        self,
        current_date: date,
        market_data: Dict[str, MarketData],
        portfolio: Portfolio,
        current_prices: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate allocation based on mean reversion signals.

        Args:
            current_date: Current date
            market_data: Market data dictionary
            portfolio: Current portfolio
            current_prices: Current prices

        Returns:
            Target allocation dictionary
        """
        allocation = {}

        for symbol, md in market_data.items():
            zscore = self.calculate_zscore(md, current_date, self.lookback_days)

            if zscore is None:
                continue

            # Buy signal: price is low (negative z-score below threshold)
            if zscore <= self.buy_threshold:
                allocation[symbol] = self.allocation_per_position

            # Sell signal is implicit - don't allocate if z-score is high
            # This allows existing positions to be reduced through rebalancing

        return allocation


class BollingerBandsStrategy(BaseStrategy):
    """
    Bollinger Bands Mean Reversion Strategy.

    Buys when price touches or goes below lower band,
    sells when price touches or goes above upper band.

    Bollinger Bands = MA ± (std_dev * num_std)

    Parameters:
        lookback_days: Period for moving average
        num_std: Number of standard deviations for bands (default: 2.0)

    Example:
        >>> strategy = BollingerBandsStrategy(lookback_days=20, num_std=2.0)
    """

    def __init__(
        self,
        lookback_days: int = 20,
        num_std: float = 2.0,
        name: str = "Bollinger Bands Strategy"
    ):
        """
        Initialize Bollinger Bands strategy.

        Args:
            lookback_days: Period for MA and std calculation
            num_std: Number of standard deviations for bands
            name: Strategy name
        """
        super().__init__(
            name=name,
            description=f"Bollinger Bands ({lookback_days}-day, {num_std} std)",
            parameters={
                'lookback_days': lookback_days,
                'num_std': num_std
            }
        )

        self.lookback_days = lookback_days
        self.num_std = num_std

    def calculate_bands(
        self,
        market_data: MarketData,
        current_date: date
    ) -> Optional[Dict[str, float]]:
        """
        Calculate Bollinger Bands.

        Args:
            market_data: Market data
            current_date: Current date

        Returns:
            Dictionary with 'upper', 'middle', 'lower', 'current' or None
        """
        data = self.get_lookback_data(market_data, current_date, self.lookback_days)

        if len(data) < self.lookback_days:
            return None

        prices = [d.close for d in data]
        current_price = prices[-1]

        # Calculate middle band (moving average)
        middle_band = sum(prices) / len(prices)

        # Calculate standard deviation
        variance = sum((p - middle_band) ** 2 for p in prices) / len(prices)
        std_dev = variance ** 0.5

        # Calculate upper and lower bands
        upper_band = middle_band + (self.num_std * std_dev)
        lower_band = middle_band - (self.num_std * std_dev)

        return {
            'upper': upper_band,
            'middle': middle_band,
            'lower': lower_band,
            'current': current_price
        }

    def calculate_allocation(
        self,
        current_date: date,
        market_data: Dict[str, MarketData],
        portfolio: Portfolio,
        current_prices: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate allocation based on Bollinger Bands.

        Args:
            current_date: Current date
            market_data: Market data dictionary
            portfolio: Current portfolio
            current_prices: Current prices

        Returns:
            Target allocation dictionary
        """
        allocation = {}

        for symbol, md in market_data.items():
            bands = self.calculate_bands(md, current_date)

            if bands is None:
                continue

            current = bands['current']
            lower = bands['lower']
            upper = bands['upper']
            middle = bands['middle']

            # Buy signal: price at or below lower band
            if current <= lower:
                allocation[symbol] = 100.0

            # Neutral signal: price between lower and middle
            elif current < middle:
                allocation[symbol] = 50.0

            # Sell signal: price at or above upper band
            # Don't allocate (will reduce position through rebalancing)

        return allocation


class RSIMeanReversionStrategy(BaseStrategy):
    """
    RSI (Relative Strength Index) Mean Reversion Strategy.

    RSI measures momentum on a 0-100 scale:
    - RSI > 70: Overbought (potential sell)
    - RSI < 30: Oversold (potential buy)

    Parameters:
        rsi_period: Period for RSI calculation (default: 14)
        oversold_threshold: RSI threshold for buy signal (default: 30)
        overbought_threshold: RSI threshold for sell signal (default: 70)

    Example:
        >>> strategy = RSIMeanReversionStrategy(rsi_period=14)
    """

    def __init__(
        self,
        rsi_period: int = 14,
        oversold_threshold: float = 30.0,
        overbought_threshold: float = 70.0,
        name: str = "RSI Mean Reversion"
    ):
        """
        Initialize RSI strategy.

        Args:
            rsi_period: RSI calculation period
            oversold_threshold: Buy when RSI below this
            overbought_threshold: Sell when RSI above this
            name: Strategy name
        """
        super().__init__(
            name=name,
            description=f"RSI mean reversion ({rsi_period}-period)",
            parameters={
                'rsi_period': rsi_period,
                'oversold_threshold': oversold_threshold,
                'overbought_threshold': overbought_threshold
            }
        )

        self.rsi_period = rsi_period
        self.oversold_threshold = oversold_threshold
        self.overbought_threshold = overbought_threshold

    def calculate_rsi(
        self,
        market_data: MarketData,
        current_date: date,
        period: int
    ) -> Optional[float]:
        """
        Calculate RSI (Relative Strength Index).

        Args:
            market_data: Market data
            current_date: Current date
            period: RSI period

        Returns:
            RSI value (0-100) or None if insufficient data
        """
        # Need period + 1 data points to calculate period returns
        data = self.get_lookback_data(market_data, current_date, period + 1)

        if len(data) < period + 1:
            return None

        # Calculate price changes
        gains = []
        losses = []

        for i in range(1, len(data)):
            change = data[i].close - data[i-1].close

            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        # Calculate average gain and loss
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100.0  # All gains, RSI = 100

        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))

        return rsi

    def calculate_allocation(
        self,
        current_date: date,
        market_data: Dict[str, MarketData],
        portfolio: Portfolio,
        current_prices: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate allocation based on RSI.

        Args:
            current_date: Current date
            market_data: Market data dictionary
            portfolio: Current portfolio
            current_prices: Current prices

        Returns:
            Target allocation dictionary
        """
        allocation = {}

        for symbol, md in market_data.items():
            rsi = self.calculate_rsi(md, current_date, self.rsi_period)

            if rsi is None:
                continue

            # Oversold: buy signal
            if rsi <= self.oversold_threshold:
                # More oversold = higher allocation
                strength = (self.oversold_threshold - rsi) / self.oversold_threshold
                allocation[symbol] = min(100.0, 50.0 + (strength * 50.0))

            # Moderately oversold: partial position
            elif rsi < 50:
                allocation[symbol] = 25.0

            # Overbought or neutral: no allocation
            # Existing positions will be reduced through rebalancing

        return allocation


