#!/usr/bin/env python3
"""
Percentile Performance Analysis for Leveraged ETF Allocations

Analyzes the distribution of returns across all rolling time periods
to understand best-case, worst-case, and typical scenarios.
"""

from portfolio_optimization_enhanced import EnhancedPortfolioOptimizer


def calculate_percentile(data, percentile):
    """Calculate percentile without numpy."""
    sorted_data = sorted(data)
    n = len(sorted_data)
    k = (n - 1) * percentile / 100
    f = int(k)
    c = k - f
    if f + 1 < n:
        return sorted_data[f] + c * (sorted_data[f + 1] - sorted_data[f])
    else:
        return sorted_data[f]


def calculate_mean(data):
    """Calculate mean."""
    return sum(data) / len(data)


def analyze_percentile_performance(name, filename, date_col, price_col, start_year, years=10):
    """
    Analyze percentile performance across all rolling windows.

    For each allocation (0%, 25%, 50%, 75%, 100%), calculate:
    - 5th percentile (worst case)
    - 25th percentile
    - 50th percentile (median)
    - 75th percentile
    - 95th percentile (best case)
    """
    print(f"\n{'='*120}")
    print(f"PERCENTILE PERFORMANCE ANALYSIS: {name}")
    print(f"{'='*120}")
    print(f"Analysis: {years}-year rolling windows")
    print()

    optimizer = EnhancedPortfolioOptimizer(name, filename, date_col, price_col, start_year)

    # Load data
    data = optimizer.analyzer.read_data()
    returns = optimizer.analyzer.calculate_returns(data)
    leveraged_returns = optimizer.analyzer.simulate_leveraged_etf(returns)

    # Test allocations
    allocations = [0, 25, 50, 75, 100]

    # Calculate performance for all rolling windows
    window_days = int(years * 252)
    step_size = 63  # ~3 months

    results_by_allocation = {}

    for allocation in allocations:
        results = []

        for i in range(0, len(leveraged_returns) - window_days, step_size):
            window = leveraged_returns[i:i + window_days]

            if len(window) < window_days * 0.95:
                continue

            result = optimizer.simulate_portfolio(
                window,
                allocation,
                years=years,
                rebalance_months=3,
                transaction_cost_bps=2.0,
                start_date=window[0]['date']
            )

            results.append({
                'return': result['annualized_return'],
                'sharpe': result['sharpe_ratio'],
                'volatility': result['volatility'],
                'max_drawdown': result['max_drawdown'],
                'start_date': window[0]['date']
            })

        results_by_allocation[allocation] = results

    # Calculate percentiles for returns
    print("="*120)
    print(f"ANNUALIZED RETURN PERCENTILES ({years}-year periods)")
    print("="*120)
    print(f"\n{'Allocation':<12} {'Count':<8} {'5th %':<10} {'25th %':<10} {'50th %':<10} {'75th %':<10} {'95th %':<10} {'Mean':<10}")
    print("-"*120)

    for allocation in allocations:
        returns_list = [r['return'] for r in results_by_allocation[allocation]]

        p5 = calculate_percentile(returns_list, 5)
        p25 = calculate_percentile(returns_list, 25)
        p50 = calculate_percentile(returns_list, 50)
        p75 = calculate_percentile(returns_list, 75)
        p95 = calculate_percentile(returns_list, 95)
        mean = calculate_mean(returns_list)

        print(f"{allocation:>3}% lev    {len(returns_list):<8} "
              f"{p5:>8.2f}%  {p25:>8.2f}%  {p50:>8.2f}%  {p75:>8.2f}%  {p95:>8.2f}%  {mean:>8.2f}%")

    # Calculate percentiles for Sharpe ratios
    print("\n" + "="*120)
    print(f"SHARPE RATIO PERCENTILES ({years}-year periods)")
    print("="*120)
    print(f"\n{'Allocation':<12} {'Count':<8} {'5th %':<10} {'25th %':<10} {'50th %':<10} {'75th %':<10} {'95th %':<10} {'Mean':<10}")
    print("-"*120)

    for allocation in allocations:
        sharpe_list = [r['sharpe'] for r in results_by_allocation[allocation]]

        p5 = calculate_percentile(sharpe_list, 5)
        p25 = calculate_percentile(sharpe_list, 25)
        p50 = calculate_percentile(sharpe_list, 50)
        p75 = calculate_percentile(sharpe_list, 75)
        p95 = calculate_percentile(sharpe_list, 95)
        mean = calculate_mean(sharpe_list)

        print(f"{allocation:>3}% lev    {len(sharpe_list):<8} "
              f"{p5:>9.3f}  {p25:>9.3f}  {p50:>9.3f}  {p75:>9.3f}  {p95:>9.3f}  {mean:>9.3f}")

    # Calculate percentiles for max drawdowns
    print("\n" + "="*120)
    print(f"MAXIMUM DRAWDOWN PERCENTILES ({years}-year periods)")
    print("="*120)
    print(f"\n{'Allocation':<12} {'Count':<8} {'5th %':<10} {'25th %':<10} {'50th %':<10} {'75th %':<10} {'95th %':<10} {'Mean':<10}")
    print("-"*120)

    for allocation in allocations:
        dd_list = [r['max_drawdown'] for r in results_by_allocation[allocation]]

        p5 = calculate_percentile(dd_list, 5)
        p25 = calculate_percentile(dd_list, 25)
        p50 = calculate_percentile(dd_list, 50)
        p75 = calculate_percentile(dd_list, 75)
        p95 = calculate_percentile(dd_list, 95)
        mean = calculate_mean(dd_list)

        print(f"{allocation:>3}% lev    {len(dd_list):<8} "
              f"{p5:>8.2f}%  {p25:>8.2f}%  {p50:>8.2f}%  {p75:>8.2f}%  {p95:>8.2f}%  {mean:>8.2f}%")

    # Win rate analysis: % of periods where leveraged beats unleveraged
    if 0 in results_by_allocation and len(allocations) > 1:
        print("\n" + "="*120)
        print(f"WIN RATE ANALYSIS (vs. 0% Leveraged Baseline)")
        print("="*120)
        print(f"\n{'Allocation':<12} {'Win Rate':<12} {'Avg Gap (Win)':<15} {'Avg Gap (Loss)':<15}")
        print("-"*120)

        unlev_returns = [r['return'] for r in results_by_allocation[0]]

        for allocation in allocations[1:]:  # Skip 0%
            lev_returns = [r['return'] for r in results_by_allocation[allocation]]

            wins = sum(1 for l, u in zip(lev_returns, unlev_returns) if l > u)
            win_rate = wins / len(lev_returns) * 100

            win_gaps = [l - u for l, u in zip(lev_returns, unlev_returns) if l > u]
            loss_gaps = [l - u for l, u in zip(lev_returns, unlev_returns) if l <= u]

            avg_win_gap = calculate_mean(win_gaps) if win_gaps else 0
            avg_loss_gap = calculate_mean(loss_gaps) if loss_gaps else 0

            print(f"{allocation:>3}% lev    {win_rate:>9.1f}%  {avg_win_gap:>12.2f}%  {avg_loss_gap:>12.2f}%")

    return results_by_allocation


def main():
    """Run percentile performance analysis for all indices."""
    print("╔" + "="*118 + "╗")
    print("║" + " "*35 + "PERCENTILE PERFORMANCE ANALYSIS" + " "*52 + "║")
    print("║" + " "*25 + "Distribution of Returns Across Rolling Windows" + " "*48 + "║")
    print("╚" + "="*118 + "╝")
    print()
    print("This analysis shows the distribution of outcomes across all historical periods.")
    print("Helps understand best-case, worst-case, and typical scenarios for each allocation.")
    print()

    indices = [
        ('S&P 500', 'sp500_stooq_daily.csv', 'Date', 'Close', 1950),
        ('DJIA', 'djia_stooq_daily.csv', 'Date', 'Close', 1950),
        ('NASDAQ', 'nasdaq_fred.csv', 'observation_date', 'NASDAQCOM', 1971),
        ('Nikkei 225', 'nikkei225_fred.csv', 'observation_date', 'NIKKEI225', 1950),
    ]

    for name, filename, date_col, price_col, start_year in indices:
        analyze_percentile_performance(name, filename, date_col, price_col, start_year, years=10)

    print("\n" + "="*120)
    print("KEY INSIGHTS")
    print("="*120)
    print("✓ 5th percentile: Worst 5% of outcomes (bear market scenarios)")
    print("✓ 50th percentile: Median outcome (typical result)")
    print("✓ 95th percentile: Best 5% of outcomes (bull market scenarios)")
    print("✓ Win rate: % of periods where leveraged beat unleveraged")
    print("="*120)


if __name__ == '__main__':
    main()
