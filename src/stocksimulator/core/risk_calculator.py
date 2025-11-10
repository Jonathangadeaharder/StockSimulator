"""
Risk Calculator

Comprehensive risk metrics and calculations for portfolio analysis.
"""

from typing import List, Dict, Optional
import math


class RiskCalculator:
    """
    Calculate comprehensive risk metrics for portfolios and strategies.

    Provides calculations for:
    - Volatility (standard deviation)
    - Sharpe ratio
    - Maximum drawdown
    - Value at Risk (VaR)
    - Conditional Value at Risk (CVaR)
    - Beta
    - Sortino ratio
    """

    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize risk calculator.

        Args:
            risk_free_rate: Annual risk-free rate (default: 2%)
        """
        self.risk_free_rate = risk_free_rate

    def calculate_volatility(
        self,
        returns: List[float],
        annualize: bool = True,
        periods_per_year: int = 252
    ) -> float:
        """
        Calculate volatility (standard deviation of returns).

        Args:
            returns: List of period returns
            annualize: Whether to annualize the volatility
            periods_per_year: Number of periods per year (252 for daily)

        Returns:
            Volatility (annualized if requested)
        """
        if len(returns) < 2:
            return 0.0

        # Calculate mean
        mean = sum(returns) / len(returns)

        # Calculate variance (using n-1 for sample)
        variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)

        # Standard deviation
        std_dev = math.sqrt(variance)

        # Annualize if requested
        if annualize:
            return std_dev * math.sqrt(periods_per_year)

        return std_dev

    def calculate_sharpe_ratio(
        self,
        returns: List[float],
        risk_free_rate: Optional[float] = None,
        periods_per_year: int = 252
    ) -> float:
        """
        Calculate Sharpe ratio.

        Args:
            returns: List of period returns
            risk_free_rate: Annual risk-free rate (None = use instance default)
            periods_per_year: Number of periods per year

        Returns:
            Sharpe ratio
        """
        if len(returns) < 2:
            return 0.0

        rfr = risk_free_rate if risk_free_rate is not None else self.risk_free_rate

        # Calculate excess returns
        mean_return = sum(returns) / len(returns)
        annualized_return = (1 + mean_return) ** periods_per_year - 1

        # Calculate volatility
        volatility = self.calculate_volatility(returns, annualize=True, periods_per_year=periods_per_year)

        if volatility == 0:
            return 0.0

        # Sharpe ratio
        sharpe = (annualized_return - rfr) / volatility

        return sharpe

    def calculate_sortino_ratio(
        self,
        returns: List[float],
        risk_free_rate: Optional[float] = None,
        periods_per_year: int = 252
    ) -> float:
        """
        Calculate Sortino ratio (uses downside deviation instead of total volatility).

        Args:
            returns: List of period returns
            risk_free_rate: Annual risk-free rate
            periods_per_year: Number of periods per year

        Returns:
            Sortino ratio
        """
        if len(returns) < 2:
            return 0.0

        rfr = risk_free_rate if risk_free_rate is not None else self.risk_free_rate

        # Calculate mean return
        mean_return = sum(returns) / len(returns)
        annualized_return = (1 + mean_return) ** periods_per_year - 1

        # Calculate downside deviation (only negative returns)
        downside_returns = [r for r in returns if r < 0]

        if not downside_returns:
            return float('inf')  # No downside = infinite Sortino

        downside_mean = sum(downside_returns) / len(downside_returns)
        downside_variance = sum((r - downside_mean) ** 2 for r in downside_returns) / len(downside_returns)
        downside_deviation = math.sqrt(downside_variance) * math.sqrt(periods_per_year)

        if downside_deviation == 0:
            return 0.0

        # Sortino ratio
        sortino = (annualized_return - rfr) / downside_deviation

        return sortino

    def calculate_max_drawdown(self, values: List[float]) -> float:
        """
        Calculate maximum drawdown from a series of portfolio values.

        Args:
            values: List of portfolio values over time

        Returns:
            Maximum drawdown as percentage
        """
        if not values:
            return 0.0

        peak = values[0]
        max_dd = 0.0

        for value in values:
            if value > peak:
                peak = value

            drawdown = (peak - value) / peak if peak > 0 else 0
            max_dd = max(max_dd, drawdown)

        return max_dd * 100  # Return as percentage

    def calculate_var(
        self,
        returns: List[float],
        confidence_level: float = 0.95,
        portfolio_value: float = 1.0
    ) -> float:
        """
        Calculate Value at Risk (VaR) using historical method.

        Args:
            returns: List of period returns
            confidence_level: Confidence level (e.g., 0.95 for 95%)
            portfolio_value: Current portfolio value

        Returns:
            VaR in dollar terms
        """
        if not returns:
            return 0.0

        # Sort returns
        sorted_returns = sorted(returns)

        # Find the return at the confidence level
        index = int((1 - confidence_level) * len(sorted_returns))
        var_return = sorted_returns[index]

        # Convert to dollar VaR
        var = abs(var_return * portfolio_value)

        return var

    def calculate_cvar(
        self,
        returns: List[float],
        confidence_level: float = 0.95,
        portfolio_value: float = 1.0
    ) -> float:
        """
        Calculate Conditional Value at Risk (CVaR / Expected Shortfall).

        Args:
            returns: List of period returns
            confidence_level: Confidence level
            portfolio_value: Current portfolio value

        Returns:
            CVaR in dollar terms
        """
        if not returns:
            return 0.0

        # Sort returns
        sorted_returns = sorted(returns)

        # Find returns worse than VaR
        index = int((1 - confidence_level) * len(sorted_returns))
        tail_returns = sorted_returns[:index]

        if not tail_returns:
            return 0.0

        # Average of tail returns
        cvar_return = sum(tail_returns) / len(tail_returns)

        # Convert to dollar CVaR
        cvar = abs(cvar_return * portfolio_value)

        return cvar

    def calculate_beta(
        self,
        asset_returns: List[float],
        market_returns: List[float]
    ) -> float:
        """
        Calculate beta (systematic risk) relative to market.

        Args:
            asset_returns: List of asset returns
            market_returns: List of market returns

        Returns:
            Beta coefficient
        """
        if len(asset_returns) != len(market_returns) or len(asset_returns) < 2:
            return 0.0

        # Calculate means
        asset_mean = sum(asset_returns) / len(asset_returns)
        market_mean = sum(market_returns) / len(market_returns)

        # Calculate covariance and market variance
        covariance = sum(
            (a - asset_mean) * (m - market_mean)
            for a, m in zip(asset_returns, market_returns)
        ) / (len(asset_returns) - 1)

        market_variance = sum(
            (m - market_mean) ** 2
            for m in market_returns
        ) / (len(market_returns) - 1)

        if market_variance == 0:
            return 0.0

        beta = covariance / market_variance

        return beta

    def calculate_information_ratio(
        self,
        portfolio_returns: List[float],
        benchmark_returns: List[float]
    ) -> float:
        """
        Calculate Information Ratio.

        Args:
            portfolio_returns: Portfolio returns
            benchmark_returns: Benchmark returns

        Returns:
            Information ratio
        """
        if len(portfolio_returns) != len(benchmark_returns) or len(portfolio_returns) < 2:
            return 0.0

        # Calculate active returns (excess returns vs benchmark)
        active_returns = [p - b for p, b in zip(portfolio_returns, benchmark_returns)]

        # Mean active return
        mean_active = sum(active_returns) / len(active_returns)

        # Tracking error (std dev of active returns)
        tracking_error_variance = sum(
            (r - mean_active) ** 2
            for r in active_returns
        ) / (len(active_returns) - 1)

        tracking_error = math.sqrt(tracking_error_variance)

        if tracking_error == 0:
            return 0.0

        # Information ratio
        ir = mean_active / tracking_error

        return ir

    def calculate_comprehensive_metrics(
        self,
        returns: List[float],
        values: List[float],
        benchmark_returns: Optional[List[float]] = None
    ) -> Dict:
        """
        Calculate comprehensive set of risk metrics.

        Args:
            returns: List of period returns
            values: List of portfolio values
            benchmark_returns: Optional benchmark returns for beta/IR

        Returns:
            Dictionary with all risk metrics
        """
        metrics = {
            'volatility': self.calculate_volatility(returns),
            'sharpe_ratio': self.calculate_sharpe_ratio(returns),
            'sortino_ratio': self.calculate_sortino_ratio(returns),
            'max_drawdown': self.calculate_max_drawdown(values),
            'var_95': self.calculate_var(returns, confidence_level=0.95),
            'cvar_95': self.calculate_cvar(returns, confidence_level=0.95)
        }

        if benchmark_returns and len(benchmark_returns) == len(returns):
            metrics['beta'] = self.calculate_beta(returns, benchmark_returns)
            metrics['information_ratio'] = self.calculate_information_ratio(returns, benchmark_returns)

        return metrics

    def __repr__(self) -> str:
        return f"RiskCalculator(risk_free_rate={self.risk_free_rate:.2%})"
