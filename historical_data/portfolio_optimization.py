#!/usr/bin/env python3
# @structurelint:no-test
"""
Portfolio Optimization: Optimal Leveraged Allocation

Analyzes different portfolio allocations between leveraged (2x) and unleveraged
strategies to find optimal mix based on:
- Sharpe ratio (risk-adjusted returns)
- Maximum drawdown
- Return/volatility tradeoffs
- Different rebalancing strategies
"""

import csv
from datetime import datetime, timedelta
from analyze_pairwise_comparison import PairwiseComparison


class PortfolioOptimizer:
    def __init__(self, name, filename, date_col='Date', price_col='Close', start_year=1950):
        self.name = name
        self.analyzer = PairwiseComparison(name, filename, date_col, price_col, start_year)

    def simulate_portfolio(self, leveraged_returns, lev_allocation, years=10, rebalance_months=1, initial_investment=10000):
        """
        Simulate a portfolio with mixed leveraged/unleveraged allocation.

        Args:
            leveraged_returns: Daily returns data
            lev_allocation: Percentage in leveraged (0-100)
            years: Investment period in years
            rebalance_months: Rebalancing frequency (1=monthly, 0=never)
            initial_investment: Starting capital

        Returns:
            Dict with performance metrics
        """
        unlev_allocation = 100 - lev_allocation

        # Track portfolio value and components
        lev_value = initial_investment * (lev_allocation / 100)
        unlev_value = initial_investment * (unlev_allocation / 100)
        total_value = initial_investment

        max_value = initial_investment
        max_drawdown = 0
        daily_returns = []
        values = []
        days_since_rebalance = 0

        days_needed = min(len(leveraged_returns), int(years * 252))

        for i in range(days_needed):
            ret = leveraged_returns[i]

            # Apply returns
            lev_value *= (1 + ret['lev_return'])
            unlev_value *= (1 + ret['unlev_return'])
            total_value = lev_value + unlev_value

            # Track for metrics
            values.append(total_value)
            if i > 0:
                daily_return = (total_value - values[i-1]) / values[i-1]
                daily_returns.append(daily_return)

            # Track drawdown
            if total_value > max_value:
                max_value = total_value
            drawdown = (max_value - total_value) / max_value
            if drawdown > max_drawdown:
                max_drawdown = drawdown

            # Rebalancing
            if rebalance_months > 0:
                days_since_rebalance += 1
                if days_since_rebalance >= (rebalance_months * 21):  # ~21 trading days per month
                    days_since_rebalance = 0
                    target_lev = total_value * (lev_allocation / 100)
                    target_unlev = total_value * (unlev_allocation / 100)
                    lev_value = target_lev
                    unlev_value = target_unlev

        # Calculate metrics
        actual_years = days_needed / 252.0
        total_return = (total_value / initial_investment - 1) * 100
        annualized_return = ((total_value / initial_investment) ** (1/actual_years) - 1) * 100

        # Volatility (annualized std dev using sample variance)
        if len(daily_returns) > 1:
            mean_daily = sum(daily_returns) / len(daily_returns)
            # Use sample variance (n-1) for unbiased estimator
            variance = sum((r - mean_daily) ** 2 for r in daily_returns) / (len(daily_returns) - 1)
            daily_vol = variance ** 0.5
            annualized_vol = daily_vol * (252 ** 0.5) * 100
        else:
            annualized_vol = 0

        # Sharpe ratio (assuming 2% risk-free rate)
        risk_free = 2.0
        sharpe = (annualized_return - risk_free) / annualized_vol if annualized_vol > 0 else 0

        return {
            'lev_allocation': lev_allocation,
            'final_value': total_value,
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': annualized_vol,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown * 100,
            'years': actual_years
        }

    def optimize_allocation(self, leveraged_returns, years=10, rebalance_months=1):
        """
        Test different allocations to find optimal mix.

        Tests allocations from 0% to 100% leveraged in 5% increments.
        """
        allocations = list(range(0, 101, 5))  # 0%, 5%, 10%, ..., 100%
        results = []

        for alloc in allocations:
            result = self.simulate_portfolio(
                leveraged_returns,
                lev_allocation=alloc,
                years=years,
                rebalance_months=rebalance_months
            )
            results.append(result)

        return results

    def find_optimal_allocations(self, results):
        """
        Find optimal allocations for different objectives.

        Returns:
            Dict with optimal allocations for different criteria
        """
        # Max Sharpe ratio
        max_sharpe = max(results, key=lambda x: x['sharpe_ratio'])

        # Max return (regardless of risk)
        max_return = max(results, key=lambda x: x['annualized_return'])

        # Min volatility
        min_vol = min(results, key=lambda x: x['volatility'])

        # Min drawdown
        min_dd = min(results, key=lambda x: x['max_drawdown'])

        # Best return per unit volatility
        max_return_vol_ratio = max(results, key=lambda x: x['annualized_return'] / x['volatility'] if x['volatility'] > 0 else 0)

        # Target volatility ~15% (similar to S&P 500)
        target_vol = 15.0
        closest_to_target_vol = min(results, key=lambda x: abs(x['volatility'] - target_vol))

        return {
            'max_sharpe': max_sharpe,
            'max_return': max_return,
            'min_volatility': min_vol,
            'min_drawdown': min_dd,
            'max_return_vol_ratio': max_return_vol_ratio,
            'target_15pct_vol': closest_to_target_vol
        }

    def analyze_optimal_portfolio(self):
        """Run complete portfolio optimization analysis."""
        print(f"\n{'='*120}")
        print(f"PORTFOLIO OPTIMIZATION: {self.name}")
        print(f"{'='*120}\n")

        # Load data
        data = self.analyzer.read_data()
        returns = self.analyzer.calculate_returns(data)
        leveraged_returns = self.analyzer.simulate_leveraged_etf(returns)

        print(f"Analyzing {len(leveraged_returns)} days of historical data")
        print(f"Time period: {leveraged_returns[0]['date'].strftime('%Y-%m-%d')} to {leveraged_returns[-1]['date'].strftime('%Y-%m-%d')}")
        print()

        # Test different time periods and rebalancing strategies
        periods = [10, 15, 20]
        rebalance_strategies = {
            'Monthly Rebalance': 1,
            'Quarterly Rebalance': 3,
            'Annual Rebalance': 12,
            'Buy & Hold (No Rebalance)': 0
        }

        all_results = {}

        for years in periods:
            print(f"\n{'='*120}")
            print(f"{years}-YEAR INVESTMENT PERIOD")
            print(f"{'='*120}\n")

            period_results = {}

            for strategy_name, rebal_months in rebalance_strategies.items():
                print(f"Strategy: {strategy_name}")
                print(f"{'─'*120}")

                results = self.optimize_allocation(
                    leveraged_returns[:int(years * 252)],
                    years=years,
                    rebalance_months=rebal_months
                )

                optimal = self.find_optimal_allocations(results)
                period_results[strategy_name] = {
                    'all_results': results,
                    'optimal': optimal
                }

                # Print summary
                print(f"\nOptimal Allocations for {strategy_name}:")
                print(f"  Max Sharpe Ratio:      {optimal['max_sharpe']['lev_allocation']:>3}% leveraged "
                      f"(Sharpe: {optimal['max_sharpe']['sharpe_ratio']:.2f}, Return: {optimal['max_sharpe']['annualized_return']:.2f}%, "
                      f"Vol: {optimal['max_sharpe']['volatility']:.2f}%)")

                print(f"  Max Return:            {optimal['max_return']['lev_allocation']:>3}% leveraged "
                      f"(Return: {optimal['max_return']['annualized_return']:.2f}%, Vol: {optimal['max_return']['volatility']:.2f}%, "
                      f"MaxDD: {optimal['max_return']['max_drawdown']:.1f}%)")

                print(f"  Min Volatility:        {optimal['min_volatility']['lev_allocation']:>3}% leveraged "
                      f"(Vol: {optimal['min_volatility']['volatility']:.2f}%, Return: {optimal['min_volatility']['annualized_return']:.2f}%)")

                print(f"  Min Drawdown:          {optimal['min_drawdown']['lev_allocation']:>3}% leveraged "
                      f"(MaxDD: {optimal['min_drawdown']['max_drawdown']:.1f}%, Return: {optimal['min_drawdown']['annualized_return']:.2f}%)")

                print(f"  Target 15% Volatility: {optimal['target_15pct_vol']['lev_allocation']:>3}% leveraged "
                      f"(Vol: {optimal['target_15pct_vol']['volatility']:.2f}%, Return: {optimal['target_15pct_vol']['annualized_return']:.2f}%, "
                      f"Sharpe: {optimal['target_15pct_vol']['sharpe_ratio']:.2f})")
                print()

            all_results[years] = period_results

        return all_results


def print_allocation_table(results, years):
    """Print detailed allocation table."""
    print(f"\n{'='*120}")
    print(f"DETAILED ALLOCATION ANALYSIS ({years}-YEAR PERIOD)")
    print(f"{'='*120}\n")

    # Use monthly rebalance results for table
    monthly_results = results[years]['Monthly Rebalance']['all_results']

    print(f"{'Lev %':<8} {'Return':<10} {'Volatility':<12} {'Sharpe':<10} {'Max DD':<10} {'Return/Vol':<12}")
    print("─"*120)

    for r in monthly_results:
        ret_vol_ratio = r['annualized_return'] / r['volatility'] if r['volatility'] > 0 else 0
        print(f"{r['lev_allocation']:>3}%    {r['annualized_return']:>7.2f}%  {r['volatility']:>9.2f}%  "
              f"{r['sharpe_ratio']:>8.2f}  {r['max_drawdown']:>8.1f}%  {ret_vol_ratio:>9.2f}")


def main():
    """Run portfolio optimization on all indices."""
    print("╔" + "="*118 + "╗")
    print("║" + " "*30 + "PORTFOLIO OPTIMIZATION ANALYSIS" + " "*57 + "║")
    print("║" + " "*25 + "Optimal Leveraged Allocation Based on Historical Data" + " "*40 + "║")
    print("╚" + "="*118 + "╝")
    print()
    print("Analysis Framework:")
    print("- Test allocations from 0% to 100% leveraged (5% increments)")
    print("- Evaluate different rebalancing strategies (monthly, quarterly, annual, buy & hold)")
    print("- Find optimal allocation for different objectives:")
    print("  * Maximum Sharpe ratio (best risk-adjusted returns)")
    print("  * Maximum return")
    print("  * Minimum volatility")
    print("  * Minimum drawdown")
    print("  * Target volatility level")
    print()

    indices = [
        ('S&P 500', 'sp500_stooq_daily.csv', 'Date', 'Close', 1950),
        ('DJIA', 'djia_stooq_daily.csv', 'Date', 'Close', 1950),
        ('NASDAQ', 'nasdaq_fred.csv', 'observation_date', 'NASDAQCOM', 1971),
        ('Nikkei 225', 'nikkei225_fred.csv', 'observation_date', 'NIKKEI225', 1950),
    ]

    all_index_results = {}

    for name, filename, date_col, price_col, start_year in indices:
        try:
            optimizer = PortfolioOptimizer(name, filename, date_col, price_col, start_year)
            results = optimizer.analyze_optimal_portfolio()
            all_index_results[name] = results

            # Print detailed table for 10-year period
            print_allocation_table(results, 10)

        except Exception as e:
            print(f"\nError analyzing {name}: {e}\n")

    # Cross-index comparison
    print("\n\n" + "="*120)
    print("CROSS-INDEX OPTIMAL ALLOCATION COMPARISON (10-Year Period, Monthly Rebalance)")
    print("="*120 + "\n")

    print(f"{'Index':<15} {'Objective':<25} {'Opt %':<8} {'Return':<10} {'Vol':<10} {'Sharpe':<10} {'MaxDD':<10}")
    print("─"*120)

    for name in ['S&P 500', 'DJIA', 'NASDAQ', 'Nikkei 225']:
        if name in all_index_results:
            opt = all_index_results[name][10]['Monthly Rebalance']['optimal']

            for obj_name, obj_key in [
                ('Max Sharpe', 'max_sharpe'),
                ('Target 15% Vol', 'target_15pct_vol'),
                ('Min Drawdown', 'min_drawdown')
            ]:
                obj = opt[obj_key]
                print(f"{name:<15} {obj_name:<25} {obj['lev_allocation']:>3}%    {obj['annualized_return']:>7.2f}%  "
                      f"{obj['volatility']:>7.2f}%  {obj['sharpe_ratio']:>8.2f}  {obj['max_drawdown']:>8.1f}%")
            print()

    print("="*120)
    print("KEY RECOMMENDATIONS:")
    print("="*120)
    print("- For risk-averse investors: Use optimal Sharpe ratio allocation (typically 30-50% leveraged)")
    print("- For target volatility matching S&P 500: Use target 15% vol allocation")
    print("- For minimizing drawdowns: Use min drawdown allocation (typically 0-30% leveraged)")
    print("- Monthly or quarterly rebalancing is recommended to maintain allocations")
    print("- 100% leveraged allocation maximizes returns but also volatility and drawdowns")
    print("="*120)


if __name__ == '__main__':
    main()
