"""
Risk Parity Strategy

Implements risk parity allocation strategies that balance risk contribution
rather than dollar allocation across assets.
"""

from typing import Dict, List, Optional
from datetime import date
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

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


class EqualRiskContributionStrategy(BaseStrategy):
    """
    Equal Risk Contribution (ERC) Strategy.

    Advanced risk parity that ensures each asset contributes equally to
    portfolio risk, accounting for correlations between assets.

    This is a simplified implementation that uses pairwise correlations.

    Parameters:
        lookback_days: Period for risk calculation (default: 252)
        rebalance_threshold: Minimum drift to trigger rebalance (default: 5%)

    Example:
        >>> strategy = EqualRiskContributionStrategy(lookback_days=252)
    """

    def __init__(
        self,
        lookback_days: int = 252,
        rebalance_threshold: float = 5.0,
        name: str = "Equal Risk Contribution"
    ):
        """
        Initialize ERC strategy.

        Args:
            lookback_days: Lookback period
            rebalance_threshold: Rebalance threshold
            name: Strategy name
        """
        super().__init__(
            name=name,
            description="Equal risk contribution with correlations",
            parameters={
                'lookback_days': lookback_days,
                'rebalance_threshold': rebalance_threshold
            }
        )

        self.lookback_days = lookback_days
        self.rebalance_threshold = rebalance_threshold

    def calculate_correlation(
        self,
        returns_a: List[float],
        returns_b: List[float]
    ) -> float:
        """
        Calculate correlation between two return series.

        Args:
            returns_a: Returns for asset A
            returns_b: Returns for asset B

        Returns:
            Correlation coefficient (-1 to 1)
        """
        if len(returns_a) != len(returns_b) or len(returns_a) < 2:
            return 0.0

        # Calculate means
        mean_a = sum(returns_a) / len(returns_a)
        mean_b = sum(returns_b) / len(returns_b)

        # Calculate covariance and standard deviations
        covariance = sum(
            (a - mean_a) * (b - mean_b)
            for a, b in zip(returns_a, returns_b)
        ) / (len(returns_a) - 1)

        var_a = sum((a - mean_a) ** 2 for a in returns_a) / (len(returns_a) - 1)
        var_b = sum((b - mean_b) ** 2 for b in returns_b) / (len(returns_b) - 1)

        std_a = var_a ** 0.5
        std_b = var_b ** 0.5

        if std_a == 0 or std_b == 0:
            return 0.0

        correlation = covariance / (std_a * std_b)

        return max(-1.0, min(1.0, correlation))  # Clamp to [-1, 1]

    def calculate_allocation(
        self,
        current_date: date,
        market_data: Dict[str, MarketData],
        portfolio: Portfolio,
        current_prices: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate ERC allocation.

        This is a simplified version that adjusts inverse volatility weights
        based on average correlations.

        Args:
            current_date: Current date
            market_data: Market data dictionary
            portfolio: Current portfolio
            current_prices: Current prices

        Returns:
            Target allocation dictionary
        """
        # Calculate returns and volatilities
        asset_returns = {}
        asset_volatilities = {}

        for symbol, md in market_data.items():
            data = self.get_lookback_data(md, current_date, self.lookback_days)

            if len(data) < 2:
                continue

            returns = []
            for i in range(1, len(data)):
                if data[i-1].close > 0:
                    ret = (data[i].close - data[i-1].close) / data[i-1].close
                    returns.append(ret)

            if len(returns) < 2:
                continue

            vol = self.calculate_volatility(returns, annualize=True)

            if vol > 0:
                asset_returns[symbol] = returns
                asset_volatilities[symbol] = vol

        if not asset_volatilities:
            return {}

        # Calculate average correlation for each asset
        avg_correlations = {}
        symbols = list(asset_returns.keys())

        for symbol in symbols:
            correlations = []

            for other_symbol in symbols:
                if symbol != other_symbol:
                    corr = self.calculate_correlation(
                        asset_returns[symbol],
                        asset_returns[other_symbol]
                    )
                    correlations.append(abs(corr))  # Use absolute correlation

            avg_corr = sum(correlations) / len(correlations) if correlations else 0.5
            avg_correlations[symbol] = avg_corr

        # Calculate adjusted weights
        # Lower volatility and lower correlation = higher weight
        adjusted_weights = {}

        for symbol in asset_volatilities:
            vol = asset_volatilities[symbol]
            corr = avg_correlations[symbol]

            # Inverse volatility, adjusted for correlation
            # High correlation reduces the benefit of diversification
            correlation_factor = 1.0 - (corr * 0.5)  # Reduce weight for high correlation
            adjusted_weights[symbol] = (1.0 / vol) * correlation_factor

        # Normalize to 100%
        total_weight = sum(adjusted_weights.values())
        allocation = {}

        if total_weight > 0:
            allocation = {
                symbol: (w / total_weight) * 100.0
                for symbol, w in adjusted_weights.items()
            }

        return allocation


class MinimumVarianceStrategy(BaseStrategy):
    """
    Minimum Variance Portfolio Strategy.

    Constructs a portfolio that minimizes overall volatility.
    This is a simplified implementation using inverse variance weighting.

    Parameters:
        lookback_days: Period for variance calculation (default: 252)
        min_allocation: Minimum allocation per asset (default: 0%)
        max_allocation: Maximum allocation per asset (default: 100%)

    Example:
        >>> strategy = MinimumVarianceStrategy(lookback_days=252)
    """

    def __init__(
        self,
        lookback_days: int = 252,
        min_allocation: float = 0.0,
        max_allocation: float = 100.0,
        name: str = "Minimum Variance"
    ):
        """
        Initialize minimum variance strategy.

        Args:
            lookback_days: Lookback period
            min_allocation: Minimum allocation per asset (%)
            max_allocation: Maximum allocation per asset (%)
            name: Strategy name
        """
        super().__init__(
            name=name,
            description="Minimum variance portfolio",
            parameters={
                'lookback_days': lookback_days,
                'min_allocation': min_allocation,
                'max_allocation': max_allocation
            }
        )

        self.lookback_days = lookback_days
        self.min_allocation = min_allocation
        self.max_allocation = max_allocation

    def calculate_allocation(
        self,
        current_date: date,
        market_data: Dict[str, MarketData],
        portfolio: Portfolio,
        current_prices: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate minimum variance allocation.

        Uses inverse variance weighting as a simple approximation.

        Args:
            current_date: Current date
            market_data: Market data dictionary
            portfolio: Current portfolio
            current_prices: Current prices

        Returns:
            Target allocation dictionary
        """
        # Calculate variances
        variances = {}

        for symbol, md in market_data.items():
            data = self.get_lookback_data(md, current_date, self.lookback_days)

            if len(data) < 2:
                continue

            returns = []
            for i in range(1, len(data)):
                if data[i-1].close > 0:
                    ret = (data[i].close - data[i-1].close) / data[i-1].close
                    returns.append(ret)

            if len(returns) < 2:
                continue

            # Calculate variance
            mean = sum(returns) / len(returns)
            variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)

            if variance > 0:
                variances[symbol] = variance

        if not variances:
            return {}

        # Inverse variance weighting
        inverse_vars = {symbol: 1.0 / var for symbol, var in variances.items()}
        total_inv_var = sum(inverse_vars.values())

        # Calculate allocation
        allocation = {}
        for symbol, inv_var in inverse_vars.items():
            weight = (inv_var / total_inv_var) * 100.0

            # Apply constraints
            weight = max(self.min_allocation, min(self.max_allocation, weight))
            allocation[symbol] = weight

        # Renormalize
        total_weight = sum(allocation.values())
        if total_weight > 0:
            allocation = {
                symbol: (w / total_weight) * 100.0
                for symbol, w in allocation.items()
            }

        return allocation
