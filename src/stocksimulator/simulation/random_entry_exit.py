"""
Random Entry/Exit Monte Carlo Simulation

Validates strategy performance across random entry and exit points,
simulating realistic investor behavior where timing is imperfect.

Inspired by BadWolf1023/leveraged-etf-simulation methodology.
"""

import random
import numpy as np
import pandas as pd
from typing import List, Dict, Callable, Optional, Tuple
from dataclasses import dataclass
from datetime import date, timedelta

from stocksimulator.core.backtester import Backtester
from stocksimulator.models.market_data import MarketData


@dataclass
class RandomBacktestResult:
    """Result from a single random entry/exit backtest."""
    simulation_id: int
    entry_date: date
    exit_date: date
    holding_period_days: int
    holding_period_years: float
    initial_value: float
    final_value: float
    total_return: float
    annualized_return: float
    max_drawdown: float
    sharpe_ratio: float
    volatility: float
    num_transactions: int


class RandomEntryExitSimulator:
    """
    Monte Carlo simulation with random entry and exit points.

    Validates strategies work across realistic investor behavior
    (imperfect timing). This complements traditional rolling window
    analysis by testing a wider variety of holding periods and
    entry points.

    Key Insight:
    "Average investor's entries and exits are quite random" - need to
    test across random entry/exit points to ensure robustness.
    """

    def __init__(
        self,
        min_holding_years: float = 2.0,
        max_holding_years: float = 20.0,
        num_simulations: int = 1000,
        seed: Optional[int] = None
    ):
        """
        Initialize random entry/exit simulator.

        Args:
            min_holding_years: Minimum holding period in years
            max_holding_years: Maximum holding period in years
            num_simulations: Number of random simulations to run
            seed: Random seed for reproducibility (None = random)
        """
        self.min_holding_years = min_holding_years
        self.max_holding_years = max_holding_years
        self.num_simulations = num_simulations

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

    def run_monte_carlo(
        self,
        strategy_func: Callable,
        strategy_name: str,
        market_data: Dict[str, MarketData],
        initial_cash: float = 100000.0,
        transaction_cost_bps: float = 2.0,
        verbose: bool = True
    ) -> List[RandomBacktestResult]:
        """
        Run Monte Carlo simulation with random entry/exit.

        Args:
            strategy_func: Strategy function or callable
            strategy_name: Name for the strategy
            market_data: Market data dictionary
            initial_cash: Initial cash amount
            transaction_cost_bps: Transaction cost in basis points
            verbose: Print progress updates

        Returns:
            List of RandomBacktestResult for each simulation

        Example:
            >>> simulator = RandomEntryExitSimulator(
            ...     min_holding_years=2,
            ...     max_holding_years=20,
            ...     num_simulations=1000
            ... )
            >>> results = simulator.run_monte_carlo(
            ...     strategy_func=my_strategy,
            ...     strategy_name="60/40",
            ...     market_data=market_data
            ... )
            >>> stats = simulator.analyze_results(results)
            >>> print(f"Mean Return: {stats['annualized_return']['mean']:.2f}%")
        """
        # Get available date range
        all_dates = self._get_date_range(market_data)

        if len(all_dates) == 0:
            raise ValueError("No market data available")

        min_days = int(self.min_holding_years * 252)
        max_days = int(self.max_holding_years * 252)

        if len(all_dates) < max_days:
            raise ValueError(
                f"Insufficient data: need {max_days} days, have {len(all_dates)} days"
            )

        results = []

        if verbose:
            print(f"Running {self.num_simulations} Monte Carlo simulations...")
            print(f"  Strategy: {strategy_name}")
            print(f"  Date range: {all_dates[0]} to {all_dates[-1]}")
            print(f"  Holding period: {self.min_holding_years:.1f} to {self.max_holding_years:.1f} years")
            print()

        for i in range(self.num_simulations):
            # Random entry date (leave room for max holding period)
            max_entry_idx = len(all_dates) - max_days
            if max_entry_idx <= 0:
                raise ValueError("Insufficient data for simulation")

            entry_idx = random.randint(0, max_entry_idx)
            entry_date = all_dates[entry_idx]

            # Random holding period
            holding_days = random.randint(min_days, max_days)
            exit_idx = min(entry_idx + holding_days, len(all_dates) - 1)
            exit_date = all_dates[exit_idx]
            actual_holding_days = exit_idx - entry_idx

            # Run backtest for this random period
            backtester = Backtester(
                initial_cash=initial_cash,
                transaction_cost_bps=transaction_cost_bps
            )

            result = backtester.run_backtest(
                strategy_name=f"{strategy_name}_sim_{i}",
                market_data=market_data,
                strategy_func=strategy_func,
                start_date=entry_date,
                end_date=exit_date
            )

            summary = result.get_performance_summary()

            # Store result
            results.append(RandomBacktestResult(
                simulation_id=i,
                entry_date=entry_date,
                exit_date=exit_date,
                holding_period_days=actual_holding_days,
                holding_period_years=actual_holding_days / 252.0,
                initial_value=initial_cash,
                final_value=result.portfolio_values[-1],
                total_return=summary['total_return'],
                annualized_return=summary['annualized_return'],
                max_drawdown=summary['max_drawdown'],
                sharpe_ratio=summary['sharpe_ratio'],
                volatility=summary['volatility'],
                num_transactions=summary['num_transactions']
            ))

            if verbose and (i + 1) % 100 == 0:
                print(f"  Completed {i + 1}/{self.num_simulations} simulations")

        if verbose:
            print(f"\nCompleted all {self.num_simulations} simulations!")

        return results

    def analyze_results(self, results: List[RandomBacktestResult]) -> Dict:
        """
        Analyze Monte Carlo results to find distribution statistics.

        Args:
            results: List of RandomBacktestResult

        Returns:
            Dictionary with statistical summaries

        Example:
            >>> stats = simulator.analyze_results(results)
            >>> print(f"Win rate: {stats['win_rate']:.1f}%")
            >>> print(f"5th percentile return: {stats['annualized_return']['percentile_5']:.2f}%")
        """
        if len(results) == 0:
            raise ValueError("No results to analyze")

        # Extract metrics
        returns = [r.annualized_return for r in results]
        total_returns = [r.total_return for r in results]
        sharpes = [r.sharpe_ratio for r in results]
        max_dds = [r.max_drawdown for r in results]
        volatilities = [r.volatility for r in results]
        holding_periods = [r.holding_period_years for r in results]

        return {
            'num_simulations': len(results),
            'annualized_return': {
                'mean': np.mean(returns),
                'median': np.median(returns),
                'std': np.std(returns),
                'min': np.min(returns),
                'max': np.max(returns),
                'percentile_5': np.percentile(returns, 5),
                'percentile_10': np.percentile(returns, 10),
                'percentile_25': np.percentile(returns, 25),
                'percentile_75': np.percentile(returns, 75),
                'percentile_90': np.percentile(returns, 90),
                'percentile_95': np.percentile(returns, 95)
            },
            'total_return': {
                'mean': np.mean(total_returns),
                'median': np.median(total_returns),
                'std': np.std(total_returns),
                'min': np.min(total_returns),
                'max': np.max(total_returns),
                'percentile_5': np.percentile(total_returns, 5),
                'percentile_95': np.percentile(total_returns, 95)
            },
            'sharpe_ratio': {
                'mean': np.mean(sharpes),
                'median': np.median(sharpes),
                'std': np.std(sharpes),
                'min': np.min(sharpes),
                'max': np.max(sharpes)
            },
            'max_drawdown': {
                'mean': np.mean(max_dds),
                'median': np.median(max_dds),
                'worst': np.min(max_dds),
                'best': np.max(max_dds),
                'std': np.std(max_dds)
            },
            'volatility': {
                'mean': np.mean(volatilities),
                'median': np.median(volatilities),
                'std': np.std(volatilities)
            },
            'holding_period_years': {
                'mean': np.mean(holding_periods),
                'median': np.median(holding_periods),
                'min': np.min(holding_periods),
                'max': np.max(holding_periods)
            },
            'win_rate': sum(1 for r in returns if r > 0) / len(returns) * 100,
            'positive_return_rate': sum(1 for r in total_returns if r > 0) / len(total_returns) * 100
        }

    def compare_strategies(
        self,
        strategies: Dict[str, Callable],
        market_data: Dict[str, MarketData],
        initial_cash: float = 100000.0,
        verbose: bool = True
    ) -> pd.DataFrame:
        """
        Compare multiple strategies using Monte Carlo simulation.

        Args:
            strategies: Dict of strategy_name -> strategy_function
            market_data: Market data
            initial_cash: Initial cash
            verbose: Print progress

        Returns:
            DataFrame comparing strategy statistics

        Example:
            >>> strategies = {
            ...     '60/40': balanced_strategy,
            ...     '100% Stocks': stock_strategy,
            ...     'HRP': hrp_strategy
            ... }
            >>> comparison = simulator.compare_strategies(strategies, market_data)
            >>> print(comparison.sort_values('mean_return', ascending=False))
        """
        all_stats = {}

        for strategy_name, strategy_func in strategies.items():
            if verbose:
                print(f"\n{'='*80}")
                print(f"Running simulations for: {strategy_name}")
                print(f"{'='*80}\n")

            results = self.run_monte_carlo(
                strategy_func=strategy_func,
                strategy_name=strategy_name,
                market_data=market_data,
                initial_cash=initial_cash,
                verbose=verbose
            )

            stats = self.analyze_results(results)
            all_stats[strategy_name] = stats

        # Build comparison DataFrame
        comparison_data = []
        for name, stats in all_stats.items():
            comparison_data.append({
                'strategy': name,
                'mean_return': stats['annualized_return']['mean'],
                'median_return': stats['annualized_return']['median'],
                'return_5th_pct': stats['annualized_return']['percentile_5'],
                'return_95th_pct': stats['annualized_return']['percentile_95'],
                'mean_sharpe': stats['sharpe_ratio']['mean'],
                'median_sharpe': stats['sharpe_ratio']['median'],
                'mean_max_dd': stats['max_drawdown']['mean'],
                'worst_max_dd': stats['max_drawdown']['worst'],
                'win_rate': stats['win_rate'],
                'volatility': stats['volatility']['mean']
            })

        df = pd.DataFrame(comparison_data)
        df = df.set_index('strategy')

        return df

    def export_results(
        self,
        results: List[RandomBacktestResult],
        filename: str
    ):
        """
        Export simulation results to CSV.

        Args:
            results: List of RandomBacktestResult
            filename: Output CSV filename
        """
        data = []
        for r in results:
            data.append({
                'simulation_id': r.simulation_id,
                'entry_date': r.entry_date,
                'exit_date': r.exit_date,
                'holding_period_years': r.holding_period_years,
                'total_return': r.total_return,
                'annualized_return': r.annualized_return,
                'max_drawdown': r.max_drawdown,
                'sharpe_ratio': r.sharpe_ratio,
                'volatility': r.volatility,
                'num_transactions': r.num_transactions
            })

        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Exported {len(results)} simulation results to {filename}")

    def _get_date_range(self, market_data: Dict[str, MarketData]) -> List[date]:
        """
        Extract sorted list of all available dates from market data.

        Args:
            market_data: Dictionary of symbol -> MarketData

        Returns:
            Sorted list of dates
        """
        all_dates = set()
        for md in market_data.values():
            all_dates.update(d.date for d in md.data)

        return sorted(all_dates)


def print_monte_carlo_summary(stats: Dict):
    """
    Print formatted summary of Monte Carlo statistics.

    Args:
        stats: Statistics dictionary from analyze_results()

    Example:
        >>> stats = simulator.analyze_results(results)
        >>> print_monte_carlo_summary(stats)
    """
    print("\n" + "=" * 80)
    print("MONTE CARLO SIMULATION RESULTS")
    print("=" * 80)

    print(f"\nSimulations: {stats['num_simulations']}")

    print("\nANNUALIZED RETURN:")
    print(f"  Mean:        {stats['annualized_return']['mean']:>8.2f}%")
    print(f"  Median:      {stats['annualized_return']['median']:>8.2f}%")
    print(f"  Std Dev:     {stats['annualized_return']['std']:>8.2f}%")
    print(f"  5th Pct:     {stats['annualized_return']['percentile_5']:>8.2f}%")
    print(f"  25th Pct:    {stats['annualized_return']['percentile_25']:>8.2f}%")
    print(f"  75th Pct:    {stats['annualized_return']['percentile_75']:>8.2f}%")
    print(f"  95th Pct:    {stats['annualized_return']['percentile_95']:>8.2f}%")
    print(f"  Min:         {stats['annualized_return']['min']:>8.2f}%")
    print(f"  Max:         {stats['annualized_return']['max']:>8.2f}%")

    print("\nSHARPE RATIO:")
    print(f"  Mean:        {stats['sharpe_ratio']['mean']:>8.3f}")
    print(f"  Median:      {stats['sharpe_ratio']['median']:>8.3f}")

    print("\nMAX DRAWDOWN:")
    print(f"  Mean:        {stats['max_drawdown']['mean']:>8.2f}%")
    print(f"  Median:      {stats['max_drawdown']['median']:>8.2f}%")
    print(f"  Worst:       {stats['max_drawdown']['worst']:>8.2f}%")
    print(f"  Best:        {stats['max_drawdown']['best']:>8.2f}%")

    print("\nVOLATILITY:")
    print(f"  Mean:        {stats['volatility']['mean']:>8.2f}%")
    print(f"  Median:      {stats['volatility']['median']:>8.2f}%")

    print("\nWIN RATE:")
    print(f"  Positive Annualized Return: {stats['win_rate']:>6.1f}%")

    print("\nHOLDING PERIOD:")
    print(f"  Mean:        {stats['holding_period_years']['mean']:>8.2f} years")
    print(f"  Median:      {stats['holding_period_years']['median']:>8.2f} years")
    print(f"  Range:       {stats['holding_period_years']['min']:>8.2f} - "
          f"{stats['holding_period_years']['max']:.2f} years")

    print("\n" + "=" * 80)
