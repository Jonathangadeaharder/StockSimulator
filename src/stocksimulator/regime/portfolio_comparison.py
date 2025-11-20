"""
Portfolio Comparison Framework

Compare multiple portfolio strategies across different market regimes
to identify which performs best in normal/crisis/recovery conditions.

Key features:
- Compare static vs regime-aware portfolios
- Test across historical crisis periods
- Aggregate statistics by regime type
- Side-by-side performance metrics
- Visual comparison tools
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable, Tuple
from datetime import date
from dataclasses import dataclass

from stocksimulator.core.backtester import Backtester
from stocksimulator.regime.regime_detector import MarketRegimeDetector, MarketRegime
from stocksimulator.models.market_data import MarketData, OHLCV


@dataclass
class RegimePerformance:
    """Performance metrics for a specific regime."""
    regime: MarketRegime
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    days_in_regime: int
    num_trades: int


@dataclass
class PortfolioComparison:
    """Comparison results for a portfolio strategy."""
    strategy_name: str
    overall_performance: Dict[str, float]
    regime_performance: Dict[MarketRegime, RegimePerformance]
    equity_curve: pd.DataFrame
    regime_timeline: pd.DataFrame


class PortfolioComparator:
    """
    Compare multiple portfolio strategies across market regimes.

    Enables answering questions like:
    - Which portfolio performs best in crises?
    - Which has the best risk-adjusted return in normal times?
    - How do regime-aware strategies compare to static portfolios?
    """

    def __init__(
        self,
        initial_cash: float = 100000.0,
        transaction_cost_bps: float = 2.0,
        regime_detector: Optional[MarketRegimeDetector] = None
    ):
        """
        Initialize portfolio comparator.

        Args:
            initial_cash: Starting capital for each strategy
            transaction_cost_bps: Transaction costs in basis points
            regime_detector: MarketRegimeDetector instance
        """
        self.initial_cash = initial_cash
        self.transaction_cost_bps = transaction_cost_bps
        self.regime_detector = regime_detector or MarketRegimeDetector()

    def compare_portfolios(
        self,
        portfolios: Dict[str, Callable],
        market_data: Dict[str, pd.DataFrame],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, PortfolioComparison]:
        """
        Compare multiple portfolio strategies.

        Args:
            portfolios: Dict of strategy_name -> strategy_function
            market_data: Market data for all assets
            start_date: Backtest start date
            end_date: Backtest end date

        Returns:
            Dict of strategy_name -> PortfolioComparison

        Example:
            >>> portfolios = {
            ...     '60/40': lambda cd, hd, p, cp: {'SP500': 60, 'LONG_TREASURY': 40},
            ...     'All Weather': adaptive_all_weather_strategy,
            ...     'Crisis Aware': defensive_to_aggressive_strategy
            ... }
            >>> results = comparator.compare_portfolios(portfolios, market_data)
            >>> for name, result in results.items():
            ...     print(f"{name}: {result.overall_performance['sharpe_ratio']:.2f}")
        """
        print(f"\nComparing {len(portfolios)} portfolio strategies...")
        print("=" * 80)

        results = {}

        for strategy_name, strategy_func in portfolios.items():
            print(f"\nRunning: {strategy_name}")

            comparison = self._run_single_portfolio(
                strategy_name,
                strategy_func,
                market_data,
                start_date,
                end_date
            )

            results[strategy_name] = comparison

            # Print summary
            overall = comparison.overall_performance
            print(f"  Total Return: {overall['total_return']:.2f}%")
            print(f"  Sharpe Ratio: {overall['sharpe_ratio']:.2f}")
            print(f"  Max Drawdown: {overall['max_drawdown']:.2f}%")

        print("\n" + "=" * 80)
        print("Comparison complete!\n")

        return results

    def compare_by_regime(
        self,
        comparison_results: Dict[str, PortfolioComparison]
    ) -> pd.DataFrame:
        """
        Create regime-by-regime comparison table.

        Args:
            comparison_results: Output from compare_portfolios()

        Returns:
            DataFrame with regime performance comparison

        Example:
            >>> regime_comparison = comparator.compare_by_regime(results)
            >>> print(regime_comparison)
            >>> # Shows which strategy wins in each regime
        """
        rows = []

        for strategy_name, comparison in comparison_results.items():
            for regime, perf in comparison.regime_performance.items():
                rows.append({
                    'strategy': strategy_name,
                    'regime': regime.value,
                    'return': perf.annualized_return,
                    'volatility': perf.volatility,
                    'sharpe': perf.sharpe_ratio,
                    'max_dd': perf.max_drawdown,
                    'days': perf.days_in_regime
                })

        df = pd.DataFrame(rows)

        # Pivot for easy comparison
        pivot_return = df.pivot(index='strategy', columns='regime', values='return')
        pivot_sharpe = df.pivot(index='strategy', columns='regime', values='sharpe')
        pivot_dd = df.pivot(index='strategy', columns='regime', values='max_dd')

        return {
            'returns': pivot_return,
            'sharpe_ratios': pivot_sharpe,
            'max_drawdowns': pivot_dd,
            'detailed': df
        }

    def rank_portfolios(
        self,
        comparison_results: Dict[str, PortfolioComparison],
        metric: str = 'sharpe_ratio',
        regime: Optional[MarketRegime] = None
    ) -> pd.DataFrame:
        """
        Rank portfolios by a specific metric.

        Args:
            comparison_results: Output from compare_portfolios()
            metric: Metric to rank by ('sharpe_ratio', 'total_return', 'max_drawdown')
            regime: Optional regime to filter by (None = overall)

        Returns:
            DataFrame ranked by metric

        Example:
            >>> # Best Sharpe in crisis
            >>> crisis_ranking = comparator.rank_portfolios(
            ...     results,
            ...     metric='sharpe_ratio',
            ...     regime=MarketRegime.CRISIS
            ... )
            >>> print(crisis_ranking.head())
        """
        rows = []

        for strategy_name, comparison in comparison_results.items():
            if regime is None:
                # Overall performance
                value = comparison.overall_performance.get(metric, 0)
                rows.append({
                    'strategy': strategy_name,
                    'regime': 'overall',
                    metric: value
                })
            else:
                # Regime-specific performance
                if regime in comparison.regime_performance:
                    perf = comparison.regime_performance[regime]
                    value = getattr(perf, metric.replace('total_', '').replace('annualized_', ''), 0)
                    rows.append({
                        'strategy': strategy_name,
                        'regime': regime.value,
                        metric: value
                    })

        df = pd.DataFrame(rows)

        # Sort descending for returns/sharpe, ascending for drawdown
        ascending = metric in ['max_drawdown', 'volatility']
        df = df.sort_values(metric, ascending=ascending)

        return df

    def _run_single_portfolio(
        self,
        strategy_name: str,
        strategy_func: Callable,
        market_data: Dict[str, pd.DataFrame],
        start_date: Optional[date],
        end_date: Optional[date]
    ) -> PortfolioComparison:
        """Run backtest for a single portfolio strategy."""

        # Convert to MarketData format
        market_data_objects = {}
        for symbol, df in market_data.items():
            # Create MarketData objects from DataFrames
            market_data_objects[symbol] = self._dataframe_to_market_data(symbol, df)

        # Run backtest
        backtester = Backtester(
            initial_cash=self.initial_cash,
            transaction_cost_bps=self.transaction_cost_bps
        )

        result = backtester.run_backtest(
            strategy_name=strategy_name,
            market_data=market_data_objects,
            strategy_func=strategy_func,
            start_date=start_date,
            end_date=end_date
        )

        # Get overall performance
        overall = result.get_performance_summary()

        # Detect regimes in market data (use SP500 or first asset)
        if 'SP500' in market_data:
            price_data = market_data['SP500']
        else:
            price_data = list(market_data.values())[0]

        regimes = self.regime_detector.detect_regimes(
            price_data,
            start_date=start_date,
            end_date=end_date
        )

        # Calculate performance by regime
        regime_performance = self._calculate_regime_performance(
            result,
            regimes
        )

        # Create equity curve with regime labels
        equity_curve = pd.DataFrame({
            'date': [pv['date'] for pv in result.portfolio_values],
            'value': [pv['total_value'] for pv in result.portfolio_values]
        })

        # Add regime labels (align by date)
        equity_curve['regime'] = equity_curve['date'].map(
            dict(zip(regimes['Date'], regimes['Regime']))
        )

        return PortfolioComparison(
            strategy_name=strategy_name,
            overall_performance=overall,
            regime_performance=regime_performance,
            equity_curve=equity_curve,
            regime_timeline=regimes
        )

    def _calculate_regime_performance(
        self,
        backtest_result,
        regime_data: pd.DataFrame
    ) -> Dict[MarketRegime, RegimePerformance]:
        """Calculate performance metrics for each regime period."""

        # Align backtest dates with regime data
        dates = pd.Series([pv['date'] for pv in backtest_result.portfolio_values])
        values = pd.Series([pv['total_value'] for pv in backtest_result.portfolio_values])

        performance_by_regime = {}

        for regime_type in MarketRegime:
            # Filter to this regime
            regime_mask = regime_data['Regime'] == regime_type.value
            regime_dates = regime_data[regime_mask]['Date'].values

            if len(regime_dates) == 0:
                continue

            # Find corresponding backtest values
            value_mask = dates.isin(regime_dates)
            regime_values = values[value_mask].values

            if len(regime_values) < 2:
                continue

            # Calculate metrics
            regime_returns = np.diff(regime_values) / regime_values[:-1]

            total_return = (regime_values[-1] / regime_values[0] - 1) * 100

            days = len(regime_values)
            annualized_return = ((regime_values[-1] / regime_values[0]) ** (252 / days) - 1) * 100

            volatility = np.std(regime_returns) * np.sqrt(252) * 100

            sharpe_ratio = (annualized_return / volatility) if volatility > 0 else 0

            # Max drawdown
            cummax = np.maximum.accumulate(regime_values)
            drawdowns = (regime_values / cummax - 1) * 100
            max_drawdown = np.min(drawdowns)

            performance_by_regime[regime_type] = RegimePerformance(
                regime=regime_type,
                total_return=total_return,
                annualized_return=annualized_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                days_in_regime=days,
                num_trades=0  # Would need transaction data
            )

        return performance_by_regime

    def _dataframe_to_market_data(self, symbol: str, df: pd.DataFrame) -> MarketData:
        """Convert pandas DataFrame to MarketData object."""
        data_points = []

        for idx, row in df.iterrows():
            # Get date from 'Date' column if it exists, otherwise from index
            if 'Date' in row:
                data_date = row['Date']
            elif isinstance(idx, pd.Timestamp):
                data_date = idx.date()
            elif isinstance(idx, date):
                data_date = idx
            else:
                continue  # Skip rows without valid dates

            # Convert to date if datetime
            if isinstance(data_date, pd.Timestamp):
                data_date = data_date.date()

            ohlcv = OHLCV(
                date=data_date,
                open=row.get('Open', row.get('Close', 0)),
                high=row.get('High', row.get('Close', 0)),
                low=row.get('Low', row.get('Close', 0)),
                close=row['Close'],
                volume=int(row.get('Volume', 0)),
                adjusted_close=row.get('Adj Close', row['Close'])
            )
            data_points.append(ohlcv)

        return MarketData(symbol=symbol, data=data_points)


def create_comparison_report(
    comparison_results: Dict[str, PortfolioComparison],
    output_file: Optional[str] = None
) -> str:
    """
    Create formatted comparison report.

    Args:
        comparison_results: Output from compare_portfolios()
        output_file: Optional file to save report

    Returns:
        Formatted report string

    Example:
        >>> report = create_comparison_report(results)
        >>> print(report)
        >>> # Or save to file:
        >>> create_comparison_report(results, 'comparison_report.txt')
    """
    lines = []
    lines.append("=" * 80)
    lines.append("PORTFOLIO COMPARISON REPORT")
    lines.append("=" * 80)
    lines.append("")

    # Overall rankings
    lines.append("OVERALL PERFORMANCE RANKINGS")
    lines.append("-" * 80)
    lines.append("")

    # Sort by Sharpe ratio
    rankings = []
    for name, comp in comparison_results.items():
        rankings.append({
            'name': name,
            'sharpe': comp.overall_performance['sharpe_ratio'],
            'return': comp.overall_performance['annualized_return'],
            'drawdown': comp.overall_performance['max_drawdown']
        })

    rankings.sort(key=lambda x: x['sharpe'], reverse=True)

    lines.append(f"{'Rank':<6} {'Strategy':<30} {'Sharpe':<10} {'Return':<12} {'Max DD':<10}")
    lines.append("-" * 80)

    for i, r in enumerate(rankings, 1):
        lines.append(
            f"{i:<6} {r['name']:<30} {r['sharpe']:>8.2f}  "
            f"{r['return']:>10.2f}%  {r['drawdown']:>8.2f}%"
        )

    lines.append("")
    lines.append("")

    # Regime breakdown
    lines.append("PERFORMANCE BY REGIME")
    lines.append("-" * 80)
    lines.append("")

    for regime in [MarketRegime.NORMAL, MarketRegime.PRE_CRISIS,
                   MarketRegime.CRISIS, MarketRegime.RECOVERY]:

        lines.append(f"\n{regime.value.upper().replace('_', ' ')}:")
        lines.append("-" * 40)

        regime_rankings = []
        for name, comp in comparison_results.items():
            if regime in comp.regime_performance:
                perf = comp.regime_performance[regime]
                regime_rankings.append({
                    'name': name,
                    'return': perf.annualized_return,
                    'sharpe': perf.sharpe_ratio,
                    'drawdown': perf.max_drawdown
                })

        if regime_rankings:
            regime_rankings.sort(key=lambda x: x['sharpe'], reverse=True)

            for r in regime_rankings:
                lines.append(
                    f"  {r['name']:<28} Return: {r['return']:>7.2f}%  "
                    f"Sharpe: {r['sharpe']:>5.2f}  DD: {r['drawdown']:>6.2f}%"
                )
        else:
            lines.append("  No data for this regime")

    lines.append("")
    lines.append("=" * 80)

    report = "\n".join(lines)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"Report saved to {output_file}")

    return report


if __name__ == '__main__':
    print("Portfolio Comparison Framework")
    print("=" * 80)
    print("\nThis module enables:")
    print("  - Comparing multiple portfolio strategies")
    print("  - Analyzing performance across market regimes")
    print("  - Ranking portfolios by various metrics")
    print("  - Generating comparison reports")
    print("\nSee examples/regime_analysis/ for usage examples.")
