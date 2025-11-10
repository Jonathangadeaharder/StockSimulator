"""
Risk Parity Strategy

Implements risk parity allocation strategies that balance risk contribution
rather than dollar allocation across assets.
"""

from typing import Dict, List, Optional
from datetime import date

from stocksimulator.strategies.base_strategy import BaseStrategy
from stocksimulator.models.portfolio import Portfolio
from stocksimulator.models.market_data import MarketData


class RiskParityStrategy(BaseStrategy):
    """
    Risk Parity Strategy.

    Allocates capital such that each asset contributes equally to portfolio risk.
    This is a simplified implementation using inverse volatility weighting.

    In a true risk parity approach, assets with lower volatility get higher
    allocations, so each contributes the same amount to portfolio risk.

    Parameters:
        lookback_days: Period for volatility calculation (default: 252 = 1 year)
        min_allocation: Minimum allocation per asset (default: 5%)
        max_allocation: Maximum allocation per asset (default: 50%)

    Example:
        >>> strategy = RiskParityStrategy(lookback_days=252)
    """

    def __init__(
        self,
        lookback_days: int = 252,
        min_allocation: float = 5.0,
        max_allocation: float = 50.0,
        name: str = "Risk Parity Strategy"
    ):
        """
        Initialize risk parity strategy.

        Args:
            lookback_days: Lookback period for volatility
            min_allocation: Minimum allocation per asset (%)
            max_allocation: Maximum allocation per asset (%)
            name: Strategy name
        """
        super().__init__(
            name=name,
            description="Risk parity using inverse volatility weighting",
            parameters={
                'lookback_days': lookback_days,
                'min_allocation': min_allocation,
                'max_allocation': max_allocation
            }
        )

        self.lookback_days = lookback_days
        self.min_allocation = min_allocation
        self.max_allocation = max_allocation

    def calculate_asset_volatility(
        self,
        market_data: MarketData,
        current_date: date,
        lookback_days: int
    ) -> Optional[float]:
        """
        Calculate asset volatility.

        Args:
            market_data: Market data
            current_date: Current date
            lookback_days: Lookback period

        Returns:
            Annualized volatility or None
        """
        data = self.get_lookback_data(market_data, current_date, lookback_days)

        if len(data) < 2:
            return None

        # Calculate daily returns
        returns = []
        for i in range(1, len(data)):
            if data[i-1].close > 0:
                ret = (data[i].close - data[i-1].close) / data[i-1].close
                returns.append(ret)

        if len(returns) < 2:
            return None

        # Calculate volatility
        volatility = self.calculate_volatility(returns, annualize=True, periods_per_year=252)

        return volatility

    def calculate_allocation(
        self,
        current_date: date,
        market_data: Dict[str, MarketData],
        portfolio: Portfolio,
        current_prices: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate risk parity allocation using inverse volatility weighting.

        Args:
            current_date: Current date
            market_data: Market data dictionary
            portfolio: Current portfolio
            current_prices: Current prices

        Returns:
            Target allocation dictionary
        """
        # Calculate volatility for each asset
        volatilities = {}

        for symbol, md in market_data.items():
            vol = self.calculate_asset_volatility(md, current_date, self.lookback_days)

            if vol is not None and vol > 0:
                volatilities[symbol] = vol

        if not volatilities:
            return {}

        # Calculate inverse volatility weights
        # Lower volatility = higher weight
        inverse_vols = {symbol: 1.0 / vol for symbol, vol in volatilities.items()}
        total_inverse_vol = sum(inverse_vols.values())

        # Normalize to percentages
        allocation = {}
        for symbol, inv_vol in inverse_vols.items():
            weight = (inv_vol / total_inverse_vol) * 100.0

            # Apply min/max constraints
            weight = max(self.min_allocation, min(self.max_allocation, weight))
            allocation[symbol] = weight

        # Renormalize to ensure sum = 100%
        total_weight = sum(allocation.values())
        if total_weight > 0:
            allocation = {symbol: (w / total_weight) * 100.0 for symbol, w in allocation.items()}

        return allocation


class VolatilityTargetingStrategy(BaseStrategy):
    """
    Volatility Targeting Strategy.

    Adjusts allocation to maintain a target portfolio volatility.
    When volatility is high, reduces allocation. When low, increases allocation.

    This is commonly used for leverage management.

    Parameters:
        symbol: Symbol to trade
        target_volatility: Target annual volatility (default: 0.10 = 10%)
        lookback_days: Period for volatility calculation (default: 60)
        cash_proxy: Cash proxy symbol (default: 'SHY')

    Example:
        >>> strategy = VolatilityTargetingStrategy('SPY', target_volatility=0.10)
    """

    def __init__(
        self,
        symbol: str,
        target_volatility: float = 0.10,
        lookback_days: int = 60,
        cash_proxy: str = 'SHY',
        max_allocation: float = 100.0,
        name: str = "Volatility Targeting"
    ):
        """
        Initialize volatility targeting strategy.

        Args:
            symbol: Symbol to trade
            target_volatility: Target annual volatility (e.g., 0.10 = 10%)
            lookback_days: Lookback for volatility calculation
            cash_proxy: Cash proxy symbol
            max_allocation: Maximum allocation (%)
            name: Strategy name
        """
        super().__init__(
            name=name,
            description=f"Vol targeting {target_volatility*100:.0f}%",
            parameters={
                'symbol': symbol,
                'target_volatility': target_volatility,
                'lookback_days': lookback_days,
                'cash_proxy': cash_proxy,
                'max_allocation': max_allocation
            }
        )

        self.symbol = symbol
        self.target_volatility = target_volatility
        self.lookback_days = lookback_days
        self.cash_proxy = cash_proxy
        self.max_allocation = max_allocation

    def calculate_allocation(
        self,
        current_date: date,
        market_data: Dict[str, MarketData],
        portfolio: Portfolio,
        current_prices: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate allocation based on volatility targeting.

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
        data = self.get_lookback_data(md, current_date, self.lookback_days)

        if len(data) < 2:
            return {self.cash_proxy: 100.0}

        # Calculate returns
        returns = []
        for i in range(1, len(data)):
            if data[i-1].close > 0:
                ret = (data[i].close - data[i-1].close) / data[i-1].close
                returns.append(ret)

        if len(returns) < 2:
            return {self.cash_proxy: 100.0}

        # Calculate current volatility
        current_vol = self.calculate_volatility(returns, annualize=True)

        if current_vol == 0:
            return {self.cash_proxy: 100.0}

        # Calculate target allocation
        # allocation = target_vol / current_vol
        allocation_pct = (self.target_volatility / current_vol) * 100.0

        # Cap at max allocation
        allocation_pct = min(allocation_pct, self.max_allocation)

        # Ensure positive
        allocation_pct = max(0.0, allocation_pct)

        if allocation_pct < 5.0:
            # Too risky, go to cash
            return {self.cash_proxy: 100.0}

        # Allocate remainder to cash
        cash_pct = max(0.0, 100.0 - allocation_pct)

        result = {self.symbol: allocation_pct}
        if cash_pct > 0:
            result[self.cash_proxy] = cash_pct

        return result
