"""
Backtesting Framework

Provides comprehensive backtesting capabilities for trading strategies.
"""

from typing import Dict, List, Optional, Callable
from datetime import datetime, date, timedelta

from stocksimulator.models.portfolio import Portfolio
from stocksimulator.models.market_data import MarketData, OHLCV
from stocksimulator.models.transaction import Transaction
from stocksimulator.core.risk_calculator import RiskCalculator

# Import cost components (Phase 1 enhancement)
try:
    from stocksimulator.costs import (
        BaseCost,
        TransactionCost,
        HoldingCost,
        LeveragedETFCost
    )
    COSTS_AVAILABLE = True
except ImportError:
    COSTS_AVAILABLE = False


class BacktestResult:
    """Container for backtest results."""

    def __init__(
        self,
        strategy_name: str,
        start_date: date,
        end_date: date,
        initial_value: float,
        final_value: float,
        transactions: List[Transaction],
        portfolio_values: List[Dict],
        metadata: Optional[Dict] = None
    ):
        """Initialize backtest result."""
        self.strategy_name = strategy_name
        self.start_date = start_date
        self.end_date = end_date
        self.initial_value = initial_value
        self.final_value = final_value
        self.transactions = transactions
        self.portfolio_values = portfolio_values
        self.metadata = metadata or {}

        # Calculate basic metrics
        self.total_return = ((final_value - initial_value) / initial_value) * 100
        days = (end_date - start_date).days
        years = days / 365.25
        self.annualized_return = ((final_value / initial_value) ** (1 / years) - 1) * 100 if years > 0 else 0

    @property
    def equity_curve(self):
        """Alias for portfolio_values for backward compatibility."""
        return self.portfolio_values

    @property
    def trades(self):
        """Alias for transactions for backward compatibility."""
        return self.transactions

    def get_performance_summary(self) -> Dict:
        """Get summary of performance metrics."""
        risk_calc = RiskCalculator()

        # Extract daily values
        daily_values = [pv['total_value'] for pv in self.portfolio_values]
        dates = [pv['date'] for pv in self.portfolio_values]

        # Calculate returns
        daily_returns = []
        for i in range(1, len(daily_values)):
            ret = (daily_values[i] - daily_values[i-1]) / daily_values[i-1]
            daily_returns.append(ret)

        # Calculate risk metrics
        volatility = risk_calc.calculate_volatility(daily_returns) if daily_returns else 0
        sharpe = risk_calc.calculate_sharpe_ratio(daily_returns) if daily_returns else 0
        max_dd = risk_calc.calculate_max_drawdown(daily_values)

        # Win rate
        winning_days = sum(1 for r in daily_returns if r > 0)
        win_rate = (winning_days / len(daily_returns) * 100) if daily_returns else 0

        return {
            'strategy_name': self.strategy_name,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'days': (self.end_date - self.start_date).days,
            'initial_value': self.initial_value,
            'final_value': self.final_value,
            'total_return': self.total_return,
            'annualized_return': self.annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd,
            'num_transactions': len(self.transactions),
            'win_rate': win_rate,
            'metadata': self.metadata
        }

    def __repr__(self) -> str:
        return (f"BacktestResult(strategy={self.strategy_name}, "
                f"return={self.total_return:.2f}%, sharpe={self.get_performance_summary()['sharpe_ratio']:.3f})")


class Backtester:
    """
    Backtesting engine for testing trading strategies on historical data.

    Provides a complete backtesting environment with:
    - Historical data simulation
    - Transaction cost modeling
    - Portfolio tracking
    - Performance analytics
    """

    def __init__(
        self,
        initial_cash: float = 100000.0,
        transaction_cost_bps: float = 2.0,
        costs: Optional[List] = None
    ):
        """
        Initialize backtester.

        Args:
            initial_cash: Starting cash balance
            transaction_cost_bps: Transaction costs in basis points (legacy parameter)
            costs: Optional list of cost components (BaseCost objects).
                  If None, uses default TransactionCost with transaction_cost_bps.
                  Phase 1 enhancement: allows modular cost modeling.

        Example:
            >>> # Legacy usage (still works)
            >>> backtester = Backtester(initial_cash=100000, transaction_cost_bps=2.0)

            >>> # New modular costs (Phase 1)
            >>> from stocksimulator.costs import TransactionCost, LeveragedETFCost
            >>> backtester = Backtester(
            ...     initial_cash=100000,
            ...     costs=[
            ...         TransactionCost(base_bps=2.0),
            ...         LeveragedETFCost(ter=0.006, base_excess_cost=0.015)
            ...     ]
            ... )
        """
        self.initial_cash = initial_cash
        self.transaction_cost_bps = transaction_cost_bps

        # Set up cost components (Phase 1 enhancement)
        if costs is not None:
            self.costs = costs
            self.use_modular_costs = True
        else:
            # Backward compatibility: create default TransactionCost if available
            if COSTS_AVAILABLE:
                self.costs = [TransactionCost(base_bps=transaction_cost_bps)]
                self.use_modular_costs = True
            else:
                self.costs = []
                self.use_modular_costs = False

    def run_backtest(
        self,
        strategy_name: str,
        market_data: Dict[str, MarketData],
        strategy_func: Callable,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        rebalance_frequency: str = 'daily'
    ) -> BacktestResult:
        """
        Run a backtest for a given strategy.

        Args:
            strategy_name: Name of the strategy
            market_data: Dictionary of symbol -> MarketData
            strategy_func: Strategy function that returns target allocation
            start_date: Backtest start date (None = earliest data)
            end_date: Backtest end date (None = latest data)
            rebalance_frequency: 'daily', 'weekly', 'monthly', 'quarterly'

        Returns:
            BacktestResult object
        """
        # Initialize portfolio
        portfolio = Portfolio(
            portfolio_id=f"backtest_{strategy_name}",
            name=strategy_name,
            initial_cash=self.initial_cash
        )

        # Determine date range
        all_dates = set()
        for md in market_data.values():
            all_dates.update(d.date for d in md.data)

        sorted_dates = sorted(all_dates)

        if start_date:
            sorted_dates = [d for d in sorted_dates if d >= start_date]
        if end_date:
            sorted_dates = [d for d in sorted_dates if d <= end_date]

        if not sorted_dates:
            raise ValueError("No data available in specified date range")

        actual_start = sorted_dates[0]
        actual_end = sorted_dates[-1]

        # Track portfolio values over time
        portfolio_values = []

        # Simulation loop
        last_rebalance = None

        for current_date in sorted_dates:
            # Get current prices
            current_prices = {}
            for symbol, md in market_data.items():
                price = md.get_price_on_date(current_date)
                if price:
                    current_prices[symbol] = price

            if not current_prices:
                continue

            # Check if we should rebalance
            should_rebalance = False

            if last_rebalance is None:
                should_rebalance = True
            elif rebalance_frequency == 'daily':
                should_rebalance = True
            elif rebalance_frequency == 'weekly' and (current_date - last_rebalance).days >= 7:
                should_rebalance = True
            elif rebalance_frequency == 'monthly' and (current_date - last_rebalance).days >= 30:
                should_rebalance = True
            elif rebalance_frequency == 'quarterly' and (current_date - last_rebalance).days >= 90:
                should_rebalance = True

            # Execute rebalancing
            if should_rebalance:
                # Get target allocation from strategy
                target_allocation = strategy_func(
                    current_date=current_date,
                    market_data=market_data,
                    portfolio=portfolio,
                    current_prices=current_prices
                )

                # Rebalance portfolio
                if target_allocation:
                    portfolio.rebalance(
                        target_allocation,
                        current_prices,
                        self.transaction_cost_bps
                    )

                last_rebalance = current_date

            # Record portfolio value
            total_value = portfolio.get_total_value(current_prices)
            portfolio_values.append({
                'date': current_date,
                'total_value': total_value,
                'cash': portfolio.cash,
                'num_positions': len(portfolio.positions)
            })

        # Create result
        final_value = portfolio_values[-1]['total_value'] if portfolio_values else self.initial_cash

        result = BacktestResult(
            strategy_name=strategy_name,
            start_date=actual_start,
            end_date=actual_end,
            initial_value=self.initial_cash,
            final_value=final_value,
            transactions=portfolio.transactions,
            portfolio_values=portfolio_values,
            metadata={
                'rebalance_frequency': rebalance_frequency,
                'transaction_cost_bps': self.transaction_cost_bps
            }
        )

        return result

    def compare_strategies(
        self,
        strategies: Dict[str, Callable],
        market_data: Dict[str, MarketData],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, BacktestResult]:
        """
        Compare multiple strategies.

        Args:
            strategies: Dictionary of strategy_name -> strategy_function
            market_data: Dictionary of symbol -> MarketData
            start_date: Backtest start date
            end_date: Backtest end date

        Returns:
            Dictionary of strategy_name -> BacktestResult
        """
        results = {}

        for strategy_name, strategy_func in strategies.items():
            result = self.run_backtest(
                strategy_name=strategy_name,
                market_data=market_data,
                strategy_func=strategy_func,
                start_date=start_date,
                end_date=end_date
            )
            results[strategy_name] = result

        return results

    def calculate_costs(
        self,
        trades: Dict[str, float],
        positions: Dict[str, float],
        prices: Dict[str, float],
        current_date: date
    ) -> float:
        """
        Calculate total costs using modular cost components.

        Phase 1 enhancement: supports modular cost modeling.

        Args:
            trades: Dictionary of symbol -> shares traded
            positions: Dictionary of symbol -> current shares held
            prices: Dictionary of symbol -> current price
            current_date: Current date

        Returns:
            Total cost for this period
        """
        if not self.use_modular_costs:
            # Legacy fallback: use transaction_cost_bps
            total_cost = 0.0
            for symbol, shares in trades.items():
                if abs(shares) < 1e-10:
                    continue
                if symbol not in prices or prices[symbol] <= 0:
                    continue
                trade_value = abs(shares * prices[symbol])
                total_cost += trade_value * (self.transaction_cost_bps / 10000)
            return total_cost

        # Use modular cost components
        return sum(
            cost.calculate(trades, positions, prices, current_date)
            for cost in self.costs
        )

    def __repr__(self) -> str:
        return f"Backtester(initial_cash=${self.initial_cash:,.2f}, costs={len(self.costs)})"
