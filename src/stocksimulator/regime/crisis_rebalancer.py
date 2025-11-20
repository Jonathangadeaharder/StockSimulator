"""
Crisis Rebalancing Optimizer

Optimizes the transition from defensive to aggressive portfolios during/after crises.

Key features:
- Gradual "buy the dip" strategies
- Dollar-cost averaging into equities during downturns
- Optimal rebalancing frequency and magnitude
- Risk-aware transition paths
- Backtesting across historical crises
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Callable
from datetime import date, timedelta
from dataclasses import dataclass
from enum import Enum


class RebalancingStrategy(Enum):
    """Type of rebalancing strategy during crisis."""
    LINEAR = "linear"                    # Linear transition over time
    DRAWDOWN_TRIGGERED = "drawdown_triggered"  # Buy more as drawdown deepens
    VOLATILITY_ADJUSTED = "volatility_adjusted"  # Reduce when vol is high
    RECOVERY_BASED = "recovery_based"    # Accelerate as recovery begins


@dataclass
class RebalancingSchedule:
    """Schedule for transitioning between portfolios."""
    dates: List[date]
    allocations: List[Dict[str, float]]
    rationale: List[str]  # Why this allocation at this time


@dataclass
class TransitionResult:
    """Result of crisis transition backtest."""
    strategy_name: str
    start_date: date
    end_date: date
    initial_value: float
    final_value: float
    total_return: float
    annualized_return: float
    max_drawdown: float
    sharpe_ratio: float
    num_rebalances: int
    total_transaction_costs: float
    schedule: RebalancingSchedule


class CrisisRebalancer:
    """
    Optimizes rebalancing from defensive to aggressive during/after crises.

    Implements sophisticated "buy the dip" strategies that gradually
    shift from defensive assets to aggressive assets as crisis unfolds,
    without trying to time the exact bottom.
    """

    def __init__(
        self,
        defensive_portfolio: Dict[str, float],
        aggressive_portfolio: Dict[str, float],
        strategy: RebalancingStrategy = RebalancingStrategy.DRAWDOWN_TRIGGERED,
        rebalance_frequency_days: int = 7,  # Weekly during crisis
        max_single_shift_pct: float = 10.0,  # Max 10% shift per rebalance
        transaction_cost_bps: float = 5.0   # Higher costs during crisis
    ):
        """
        Initialize crisis rebalancer.

        Args:
            defensive_portfolio: Starting defensive allocation {'asset': weight%}
            aggressive_portfolio: Target aggressive allocation {'asset': weight%}
            strategy: Type of rebalancing strategy
            rebalance_frequency_days: Days between rebalances
            max_single_shift_pct: Maximum % to shift in single rebalance
            transaction_cost_bps: Transaction costs in basis points

        Example:
            >>> defensive = {'LONG_TREASURY': 70, 'SHORT_BOND': 30}
            >>> aggressive = {'SP500': 80, 'WORLD': 20}
            >>> rebalancer = CrisisRebalancer(
            ...     defensive_portfolio=defensive,
            ...     aggressive_portfolio=aggressive,
            ...     strategy=RebalancingStrategy.DRAWDOWN_TRIGGERED
            ... )
        """
        self.defensive_portfolio = defensive_portfolio
        self.aggressive_portfolio = aggressive_portfolio
        self.strategy = strategy
        self.rebalance_frequency_days = rebalance_frequency_days
        self.max_single_shift_pct = max_single_shift_pct
        self.transaction_cost_bps = transaction_cost_bps

    def create_transition_schedule(
        self,
        crisis_start_date: date,
        crisis_end_date: date,
        market_data: pd.DataFrame,
        start_defensive: bool = True
    ) -> RebalancingSchedule:
        """
        Create optimized transition schedule for a crisis period.

        Args:
            crisis_start_date: When crisis begins (or when to start transition)
            crisis_end_date: When crisis ends (or target completion date)
            market_data: Market price data (Date, Close) for decision-making
            start_defensive: If True, start with defensive; else start aggressive

        Returns:
            RebalancingSchedule with dates and allocations

        Example:
            >>> schedule = rebalancer.create_transition_schedule(
            ...     crisis_start_date=date(2008, 10, 1),
            ...     crisis_end_date=date(2009, 3, 31),
            ...     market_data=sp500_data
            ... )
            >>> print(f"{len(schedule.dates)} rebalancing events")
        """
        # Filter market data to crisis period
        crisis_data = market_data[
            (market_data['Date'] >= pd.Timestamp(crisis_start_date)) &
            (market_data['Date'] <= pd.Timestamp(crisis_end_date))
        ].copy()

        if len(crisis_data) == 0:
            raise ValueError("No market data in crisis period")

        # Calculate drawdown and volatility for decision-making
        crisis_data['CumulativeMax'] = crisis_data['Close'].expanding().max()
        crisis_data['Drawdown'] = (crisis_data['Close'] / crisis_data['CumulativeMax']) - 1
        crisis_data['Returns'] = crisis_data['Close'].pct_change()
        crisis_data['Volatility'] = crisis_data['Returns'].rolling(window=20).std() * np.sqrt(252)

        # Generate rebalancing dates
        rebalance_dates = self._generate_rebalance_dates(
            crisis_start_date,
            crisis_end_date,
            self.rebalance_frequency_days
        )

        # Calculate allocation for each date based on strategy
        allocations = []
        rationale = []

        source_portfolio = self.defensive_portfolio if start_defensive else self.aggressive_portfolio
        target_portfolio = self.aggressive_portfolio if start_defensive else self.defensive_portfolio

        cumulative_transition = 0.0  # Track how far we've transitioned (0 to 1)

        for rebal_date in rebalance_dates:
            # Find market conditions on this date
            date_data = crisis_data[crisis_data['Date'] <= pd.Timestamp(rebal_date)]

            if len(date_data) == 0:
                # Before crisis data starts
                allocations.append(source_portfolio.copy())
                rationale.append("Pre-crisis: maintain starting allocation")
                continue

            latest = date_data.iloc[-1]

            # Calculate transition step based on strategy
            if self.strategy == RebalancingStrategy.LINEAR:
                transition_step = self._linear_transition_step(
                    rebal_date, crisis_start_date, crisis_end_date
                )
                reason = f"Linear transition: {transition_step:.1%} progress"

            elif self.strategy == RebalancingStrategy.DRAWDOWN_TRIGGERED:
                transition_step = self._drawdown_triggered_step(
                    latest['Drawdown'], cumulative_transition
                )
                reason = f"Drawdown {latest['Drawdown']:.1%}: transition step {transition_step:.1%}"

            elif self.strategy == RebalancingStrategy.VOLATILITY_ADJUSTED:
                transition_step = self._volatility_adjusted_step(
                    latest['Volatility'], cumulative_transition
                )
                reason = f"Vol {latest['Volatility']:.1%}: transition step {transition_step:.1%}"

            elif self.strategy == RebalancingStrategy.RECOVERY_BASED:
                transition_step = self._recovery_based_step(
                    latest['Drawdown'], crisis_data, cumulative_transition
                )
                reason = f"Recovery signal: transition step {transition_step:.1%}"

            else:
                raise ValueError(f"Unknown strategy: {self.strategy}")

            # Apply step (cap at max_single_shift_pct)
            transition_step = min(transition_step, self.max_single_shift_pct / 100)
            cumulative_transition = min(1.0, cumulative_transition + transition_step)

            # Calculate blended allocation
            allocation = self._blend_portfolios(
                source_portfolio,
                target_portfolio,
                cumulative_transition
            )

            allocations.append(allocation)
            rationale.append(reason)

        return RebalancingSchedule(
            dates=rebalance_dates,
            allocations=allocations,
            rationale=rationale
        )

    def backtest_transition(
        self,
        schedule: RebalancingSchedule,
        asset_prices: Dict[str, pd.DataFrame],
        initial_capital: float = 100000.0
    ) -> TransitionResult:
        """
        Backtest a transition schedule.

        Args:
            schedule: RebalancingSchedule from create_transition_schedule()
            asset_prices: Dict of asset -> price DataFrame
            initial_capital: Starting capital

        Returns:
            TransitionResult with performance metrics
        """
        portfolio_value = initial_capital
        portfolio_shares = {}  # Shares of each asset
        transaction_costs = 0.0

        # Initialize
        initial_allocation = schedule.allocations[0]
        for asset, weight_pct in initial_allocation.items():
            if asset in asset_prices:
                price_df = asset_prices[asset]
                start_price = price_df[price_df['Date'] <= pd.Timestamp(schedule.dates[0])]['Close'].iloc[-1]
                shares = (portfolio_value * weight_pct / 100) / start_price
                portfolio_shares[asset] = shares

        # Track value over time
        value_history = []
        dates_history = []

        # Simulate through schedule
        for i, (rebal_date, target_allocation) in enumerate(zip(schedule.dates, schedule.allocations)):
            # Calculate current portfolio value
            current_value = 0.0
            for asset, shares in portfolio_shares.items():
                if asset in asset_prices:
                    price_df = asset_prices[asset]
                    current_price = price_df[price_df['Date'] <= pd.Timestamp(rebal_date)]['Close'].iloc[-1]
                    current_value += shares * current_price

            # Rebalance to target allocation
            new_shares = {}
            rebal_cost = 0.0

            for asset, target_pct in target_allocation.items():
                if asset in asset_prices:
                    target_value = current_value * target_pct / 100
                    price_df = asset_prices[asset]
                    current_price = price_df[price_df['Date'] <= pd.Timestamp(rebal_date)]['Close'].iloc[-1]
                    new_shares[asset] = target_value / current_price

                    # Calculate transaction cost
                    old_shares = portfolio_shares.get(asset, 0)
                    shares_traded = abs(new_shares[asset] - old_shares)
                    rebal_cost += shares_traded * current_price * (self.transaction_cost_bps / 10000)

            portfolio_shares = new_shares
            current_value -= rebal_cost
            transaction_costs += rebal_cost

            value_history.append(current_value)
            dates_history.append(rebal_date)

        # Calculate final value
        final_date = schedule.dates[-1]
        final_value = 0.0
        for asset, shares in portfolio_shares.items():
            if asset in asset_prices:
                price_df = asset_prices[asset]
                final_price = price_df[price_df['Date'] <= pd.Timestamp(final_date)]['Close'].iloc[-1]
                final_value += shares * final_price

        # Calculate metrics
        total_return = (final_value / initial_capital - 1) * 100
        days = (schedule.dates[-1] - schedule.dates[0]).days
        annualized_return = ((final_value / initial_capital) ** (365.25 / max(days, 1)) - 1) * 100

        # Max drawdown
        values_arr = np.array(value_history)
        cummax = np.maximum.accumulate(values_arr)
        drawdowns = (values_arr / cummax) - 1
        max_drawdown = np.min(drawdowns) * 100

        # Sharpe ratio (simplified)
        returns = np.diff(values_arr) / values_arr[:-1]
        if len(returns) > 0 and np.std(returns) > 0:
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252 / self.rebalance_frequency_days)
        else:
            sharpe_ratio = 0.0

        return TransitionResult(
            strategy_name=self.strategy.value,
            start_date=schedule.dates[0],
            end_date=schedule.dates[-1],
            initial_value=initial_capital,
            final_value=final_value,
            total_return=total_return,
            annualized_return=annualized_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            num_rebalances=len(schedule.dates),
            total_transaction_costs=transaction_costs,
            schedule=schedule
        )

    def _linear_transition_step(
        self,
        current_date: date,
        start_date: date,
        end_date: date
    ) -> float:
        """Calculate transition progress for linear strategy."""
        total_days = (end_date - start_date).days
        elapsed_days = (current_date - start_date).days

        if total_days == 0:
            return 1.0

        progress = elapsed_days / total_days
        return max(0.0, min(1.0, progress))

    def _drawdown_triggered_step(
        self,
        current_drawdown: float,
        cumulative_transition: float
    ) -> float:
        """
        Calculate transition step based on drawdown depth.

        Deeper drawdowns = more aggressive buying.
        """
        # Map drawdown to transition rate
        # -10% DD = slow transition
        # -30% DD = fast transition
        # -50% DD = very fast transition

        if current_drawdown >= -0.10:
            step = 0.02  # 2% per rebalance
        elif current_drawdown >= -0.20:
            step = 0.05  # 5% per rebalance
        elif current_drawdown >= -0.30:
            step = 0.08  # 8% per rebalance
        else:
            step = 0.12  # 12% per rebalance (aggressive buying)

        # Slow down as we approach full transition
        if cumulative_transition > 0.8:
            step *= 0.5

        return step

    def _volatility_adjusted_step(
        self,
        current_volatility: float,
        cumulative_transition: float
    ) -> float:
        """
        Calculate transition step adjusted for volatility.

        Lower vol = faster transition (market stabilizing).
        """
        # Inverse relationship: high vol = slow down
        if pd.isna(current_volatility):
            return 0.05

        if current_volatility > 0.40:  # Very high vol
            step = 0.02
        elif current_volatility > 0.30:
            step = 0.04
        elif current_volatility > 0.20:
            step = 0.06
        else:  # Low vol
            step = 0.10

        return step

    def _recovery_based_step(
        self,
        current_drawdown: float,
        crisis_data: pd.DataFrame,
        cumulative_transition: float
    ) -> float:
        """
        Calculate transition step based on recovery signals.

        Accelerate transition when recovery begins.
        """
        # Check if we're recovering (drawdown improving)
        if len(crisis_data) < 20:
            return 0.05

        recent_dd = crisis_data.tail(20)['Drawdown']
        trend = recent_dd.diff().mean()

        if trend > 0.001:  # Recovering (drawdown improving)
            step = 0.10  # Accelerate
        elif trend > 0:
            step = 0.06  # Mild recovery
        else:
            step = 0.03  # Still declining

        return step

    def _blend_portfolios(
        self,
        portfolio_a: Dict[str, float],
        portfolio_b: Dict[str, float],
        blend_factor: float  # 0 = 100% A, 1 = 100% B
    ) -> Dict[str, float]:
        """Blend two portfolios based on blend factor."""
        all_assets = set(portfolio_a.keys()) | set(portfolio_b.keys())

        blended = {}
        for asset in all_assets:
            weight_a = portfolio_a.get(asset, 0.0)
            weight_b = portfolio_b.get(asset, 0.0)
            blended[asset] = weight_a * (1 - blend_factor) + weight_b * blend_factor

        # Normalize to 100%
        total = sum(blended.values())
        if total > 0:
            blended = {k: v / total * 100 for k, v in blended.items()}

        return blended

    def _generate_rebalance_dates(
        self,
        start_date: date,
        end_date: date,
        frequency_days: int
    ) -> List[date]:
        """Generate list of rebalancing dates."""
        dates = []
        current = start_date

        while current <= end_date:
            dates.append(current)
            current += timedelta(days=frequency_days)

        # Always include end date
        if dates[-1] != end_date:
            dates.append(end_date)

        return dates


def compare_rebalancing_strategies(
    defensive_portfolio: Dict[str, float],
    aggressive_portfolio: Dict[str, float],
    crisis_start: date,
    crisis_end: date,
    market_data: pd.DataFrame,
    asset_prices: Dict[str, pd.DataFrame],
    strategies: Optional[List[RebalancingStrategy]] = None
) -> pd.DataFrame:
    """
    Compare different rebalancing strategies for a crisis period.

    Args:
        defensive_portfolio: Starting defensive allocation
        aggressive_portfolio: Target aggressive allocation
        crisis_start: Crisis start date
        crisis_end: Crisis end date
        market_data: Market data for decision-making
        asset_prices: Price data for each asset
        strategies: List of strategies to compare (defaults to all)

    Returns:
        DataFrame comparing strategies

    Example:
        >>> comparison = compare_rebalancing_strategies(
        ...     defensive_portfolio={'LONG_TREASURY': 70, 'SHORT_BOND': 30},
        ...     aggressive_portfolio={'SP500': 80, 'WORLD': 20},
        ...     crisis_start=date(2008, 10, 1),
        ...     crisis_end=date(2009, 3, 31),
        ...     market_data=sp500_data,
        ...     asset_prices={'SP500': sp500_prices, ...}
        ... )
        >>> print(comparison.sort_values('total_return', ascending=False))
    """
    if strategies is None:
        strategies = list(RebalancingStrategy)

    results = []

    for strategy in strategies:
        rebalancer = CrisisRebalancer(
            defensive_portfolio=defensive_portfolio,
            aggressive_portfolio=aggressive_portfolio,
            strategy=strategy
        )

        schedule = rebalancer.create_transition_schedule(
            crisis_start_date=crisis_start,
            crisis_end_date=crisis_end,
            market_data=market_data
        )

        result = rebalancer.backtest_transition(schedule, asset_prices)

        results.append({
            'strategy': strategy.value,
            'total_return': result.total_return,
            'annualized_return': result.annualized_return,
            'max_drawdown': result.max_drawdown,
            'sharpe_ratio': result.sharpe_ratio,
            'num_rebalances': result.num_rebalances,
            'transaction_costs': result.total_transaction_costs
        })

    df = pd.DataFrame(results)
    return df.sort_values('total_return', ascending=False)


if __name__ == '__main__':
    # Demo
    print("Crisis Rebalancing Optimizer Demo")
    print("=" * 80)

    # Define portfolios
    defensive = {
        'LONG_TREASURY': 70.0,
        'SHORT_BOND': 30.0
    }

    aggressive = {
        'SP500': 80.0,
        'WORLD': 20.0
    }

    # Create rebalancer
    rebalancer = CrisisRebalancer(
        defensive_portfolio=defensive,
        aggressive_portfolio=aggressive,
        strategy=RebalancingStrategy.DRAWDOWN_TRIGGERED
    )

    print("\nDefensive Portfolio:")
    for asset, weight in defensive.items():
        print(f"  {asset}: {weight:.1f}%")

    print("\nAggressive Portfolio:")
    for asset, weight in aggressive.items():
        print(f"  {asset}: {weight:.1f}%")

    print(f"\nStrategy: {rebalancer.strategy.value}")
    print(f"Rebalance frequency: {rebalancer.rebalance_frequency_days} days")
    print(f"Max single shift: {rebalancer.max_single_shift_pct}%")
