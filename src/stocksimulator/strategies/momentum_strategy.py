"""
Momentum Strategy

Implements momentum-based trading strategies that follow trends.
"""

from typing import Dict, List, Optional
from datetime import date
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from stocksimulator.strategies.base_strategy import BaseStrategy
from stocksimulator.models.portfolio import Portfolio
from stocksimulator.models.market_data import MarketData


class MomentumStrategy(BaseStrategy):
    """
    Momentum Strategy based on relative strength.

    Allocates to assets with the strongest recent performance.
    This is the classic "buy what's going up" approach.

    Parameters:
        lookback_days: Period for momentum calculation (default: 126 = ~6 months)
        top_n: Number of top performers to hold (default: 2)
        equal_weight: Whether to equal-weight holdings (default: True)
        momentum_threshold: Minimum momentum to invest (default: 0.0)

    Example:
        >>> strategy = MomentumStrategy(lookback_days=126, top_n=2)
        >>> # Buys top 2 performers over last 6 months
    """

    def __init__(
        self,
        lookback_days: int = 126,
        top_n: int = 2,
        equal_weight: bool = True,
        momentum_threshold: float = 0.0,
        name: str = "Momentum Strategy"
    ):
        """
        Initialize momentum strategy.

        Args:
            lookback_days: Lookback period in days (default: 126 = ~6 months)
            top_n: Number of top performers to hold
            equal_weight: Equal weight holdings vs momentum-weighted
            momentum_threshold: Minimum momentum required to invest
            name: Strategy name
        """
        super().__init__(
            name=name,
            description=f"Momentum strategy with {lookback_days}-day lookback",
            parameters={
                'lookback_days': lookback_days,
                'top_n': top_n,
                'equal_weight': equal_weight,
                'momentum_threshold': momentum_threshold
            }
        )

        self.lookback_days = lookback_days
        self.top_n = top_n
        self.equal_weight = equal_weight
        self.momentum_threshold = momentum_threshold

    def calculate_momentum(
        self,
        market_data: MarketData,
        current_date: date,
        lookback_days: int
    ) -> Optional[float]:
        """
        Calculate momentum (total return) over lookback period.

        Args:
            market_data: Market data for asset
            current_date: Current date
            lookback_days: Lookback period

        Returns:
            Momentum (total return) or None if insufficient data
        """
        data = self.get_lookback_data(market_data, current_date, lookback_days)

        if len(data) < lookback_days:
            return None

        start_price = data[0].close
        end_price = data[-1].close

        if start_price <= 0:
            return None

        momentum = (end_price - start_price) / start_price

        return momentum

    def calculate_allocation(
        self,
        current_date: date,
        market_data: Dict[str, MarketData],
        portfolio: Portfolio,
        current_prices: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate allocation based on momentum.

        Args:
            current_date: Current date
            market_data: Market data dictionary
            portfolio: Current portfolio
            current_prices: Current prices

        Returns:
            Target allocation dictionary
        """
        # Calculate momentum for each asset
        momentum_scores = {}

        for symbol, md in market_data.items():
            momentum = self.calculate_momentum(md, current_date, self.lookback_days)

            if momentum is not None and momentum >= self.momentum_threshold:
                momentum_scores[symbol] = momentum

        # If no assets meet threshold, go to cash
        if not momentum_scores:
            return {}

        # Sort by momentum (descending)
        sorted_assets = sorted(
            momentum_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Select top N
        top_assets = sorted_assets[:self.top_n]

        # Calculate allocation
        allocation = {}

        if self.equal_weight:
            # Equal weight among top performers
            weight = 100.0 / len(top_assets)
            for symbol, _ in top_assets:
                allocation[symbol] = weight
        else:
            # Weight by momentum strength
            total_momentum = sum(momentum for _, momentum in top_assets)

            if total_momentum > 0:
                for symbol, momentum in top_assets:
                    allocation[symbol] = (momentum / total_momentum) * 100.0

        return allocation


class DualMomentumStrategy(BaseStrategy):
    """
    Dual Momentum Strategy (Absolute + Relative).

    Combines absolute momentum (trend following) with relative momentum
    (relative strength). Only invests when both absolute and relative
    momentum are positive.

    This is based on Gary Antonacci's research.

    Parameters:
        lookback_days: Momentum calculation period
        cash_proxy: Symbol to hold when momentum is negative (default: 'SHY')

    Example:
        >>> strategy = DualMomentumStrategy(['SPY', 'VEA', 'VWO'], cash_proxy='SHY')
    """

    def __init__(
        self,
        symbols: List[str],
        lookback_days: int = 126,
        cash_proxy: str = 'SHY',
        name: str = "Dual Momentum Strategy"
    ):
        """
        Initialize dual momentum strategy.

        Args:
            symbols: List of symbols to evaluate
            lookback_days: Lookback period
            cash_proxy: Cash proxy symbol (short-term treasuries)
            name: Strategy name
        """
        super().__init__(
            name=name,
            description="Dual momentum (absolute + relative)",
            parameters={
                'symbols': symbols,
                'lookback_days': lookback_days,
                'cash_proxy': cash_proxy
            }
        )

        self.symbols = symbols
        self.lookback_days = lookback_days
        self.cash_proxy = cash_proxy

    def calculate_allocation(
        self,
        current_date: date,
        market_data: Dict[str, MarketData],
        portfolio: Portfolio,
        current_prices: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate dual momentum allocation.

        Steps:
        1. Calculate momentum for each asset
        2. Find asset with highest relative momentum
        3. If absolute momentum > 0, invest in that asset
        4. If absolute momentum <= 0, invest in cash proxy

        Args:
            current_date: Current date
            market_data: Market data dictionary
            portfolio: Current portfolio
            current_prices: Current prices

        Returns:
            Target allocation dictionary
        """
        # Calculate momentum for tracked symbols
        momentum_scores = {}

        for symbol in self.symbols:
            if symbol in market_data:
                md = market_data[symbol]
                data = self.get_lookback_data(md, current_date, self.lookback_days)

                if len(data) >= self.lookback_days:
                    start_price = data[0].close
                    end_price = data[-1].close

                    if start_price > 0:
                        momentum = (end_price - start_price) / start_price
                        momentum_scores[symbol] = momentum

        if not momentum_scores:
            # No data, go to cash
            return {self.cash_proxy: 100.0}

        # Find best performer (relative momentum)
        best_symbol = max(momentum_scores, key=momentum_scores.get)
        best_momentum = momentum_scores[best_symbol]

        # Check absolute momentum
        if best_momentum > 0:
            # Positive absolute momentum - invest 100% in best asset
            return {best_symbol: 100.0}
        else:
            # Negative absolute momentum - go to cash
            return {self.cash_proxy: 100.0}


class MovingAverageCrossoverStrategy(BaseStrategy):
    """
    Moving Average Crossover Strategy.

    Invests when fast MA is above slow MA (bullish signal),
    goes to cash when fast MA is below slow MA (bearish signal).

    Classic trend-following approach.

    Parameters:
        symbol: Symbol to trade
        fast_period: Fast moving average period (default: 50)
        slow_period: Slow moving average period (default: 200)
        cash_proxy: Symbol to hold during bearish periods

    Example:
        >>> strategy = MovingAverageCrossoverStrategy('SPY', fast_period=50, slow_period=200)
    """

    def __init__(
        self,
        symbol: str,
        fast_period: int = 50,
        slow_period: int = 200,
        cash_proxy: str = 'SHY',
        name: str = "MA Crossover Strategy"
    ):
        """
        Initialize MA crossover strategy.

        Args:
            symbol: Symbol to trade
            fast_period: Fast MA period (days)
            slow_period: Slow MA period (days)
            cash_proxy: Cash proxy during bearish periods
            name: Strategy name
        """
        super().__init__(
            name=name,
            description=f"MA Crossover ({fast_period}/{slow_period})",
            parameters={
                'symbol': symbol,
                'fast_period': fast_period,
                'slow_period': slow_period,
                'cash_proxy': cash_proxy
            }
        )

        self.symbol = symbol
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.cash_proxy = cash_proxy

    def calculate_allocation(
        self,
        current_date: date,
        market_data: Dict[str, MarketData],
        portfolio: Portfolio,
        current_prices: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate allocation based on MA crossover.

        Args:
            current_date: Current date
            market_data: Market data dictionary
            portfolio: Current portfolio
            current_prices: Current prices

        Returns:
            Target allocation dictionary
        """
        if self.symbol not in market_data:
            return {self.cash_proxy: 100.0}

        md = market_data[self.symbol]

        # Get sufficient data for slow MA
        data = self.get_lookback_data(md, current_date, self.slow_period)

        if len(data) < self.slow_period:
            # Insufficient data, stay in cash
            return {self.cash_proxy: 100.0}

        # Calculate moving averages
        fast_ma = self.calculate_moving_average(data, self.fast_period)
        slow_ma = self.calculate_moving_average(data, self.slow_period)

        if fast_ma is None or slow_ma is None:
            return {self.cash_proxy: 100.0}

        # Generate signal
        if fast_ma > slow_ma:
            # Bullish - invest 100%
            return {self.symbol: 100.0}
        else:
            # Bearish - go to cash
            return {self.cash_proxy: 100.0}


class RotationalMomentumStrategy(BaseStrategy):
    """
    Rotational Momentum Strategy.

    Rotates between multiple asset classes based on momentum,
    always holding the top N performers.

    Parameters:
        lookback_days: Momentum calculation period
        top_n: Number of assets to hold
        rebalance_period: How often to recalculate (default: 21 = monthly)

    Example:
        >>> strategy = RotationalMomentumStrategy(
        ...     lookback_days=126,
        ...     top_n=3,
        ...     rebalance_period=21
        ... )
    """

    def __init__(
        self,
        lookback_days: int = 126,
        top_n: int = 3,
        rebalance_period: int = 21,
        name: str = "Rotational Momentum"
    ):
        """
        Initialize rotational momentum strategy.

        Args:
            lookback_days: Lookback period for momentum
            top_n: Number of top assets to hold
            rebalance_period: Days between rebalances
            name: Strategy name
        """
        super().__init__(
            name=name,
            description=f"Rotational momentum holding top {top_n} assets",
            parameters={
                'lookback_days': lookback_days,
                'top_n': top_n,
                'rebalance_period': rebalance_period
            }
        )

        self.lookback_days = lookback_days
        self.top_n = top_n
        self.rebalance_period = rebalance_period
        self.last_rebalance = None

    def calculate_allocation(
        self,
        current_date: date,
        market_data: Dict[str, MarketData],
        portfolio: Portfolio,
        current_prices: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate rotational momentum allocation.

        Args:
            current_date: Current date
            market_data: Market data dictionary
            portfolio: Current portfolio
            current_prices: Current prices

        Returns:
            Target allocation dictionary
        """
        # Calculate momentum for all assets
        momentum_scores = {}

        for symbol, md in market_data.items():
            data = self.get_lookback_data(md, current_date, self.lookback_days)

            if len(data) >= self.lookback_days:
                start_price = data[0].close
                end_price = data[-1].close

                if start_price > 0:
                    momentum = (end_price - start_price) / start_price
                    momentum_scores[symbol] = momentum

        if not momentum_scores:
            return {}

        # Sort by momentum
        sorted_assets = sorted(
            momentum_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Select top N
        top_assets = sorted_assets[:self.top_n]

        # Equal weight allocation
        weight = 100.0 / len(top_assets)
        allocation = {symbol: weight for symbol, _ in top_assets}

        return allocation
