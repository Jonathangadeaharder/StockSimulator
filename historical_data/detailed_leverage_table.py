#!/usr/bin/env python3
"""
Detailed Leverage Allocation Table

Creates comprehensive tables showing median returns and interquartile ranges
for all leverage levels from 0-100%.
"""

from portfolio_optimization_enhanced import EnhancedPortfolioOptimizer
from percentile_performance_analysis import calculate_percentile, calculate_mean


def create_detailed_table(name, filename, date_col, price_col, start_year, years=10):
    """Create detailed table with all leverage levels."""

    print(f"\n{'='*120}")
    print(f"DETAILED LEVERAGE ALLOCATION TABLE: {name}")
    print(f"{'='*120}")
    print(f"Analysis: {years}-year rolling windows\n")

    optimizer = EnhancedPortfolioOptimizer(name, filename, date_col, price_col, start_year)

    # Load data
    data = optimizer.analyzer.read_data()
    returns = optimizer.analyzer.calculate_returns(data)
    leveraged_returns = optimizer.analyzer.simulate_leveraged_etf(returns)

    # Test all allocations from 0-100% in 5% steps
    allocations = list(range(0, 101, 5))

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
                'max_drawdown': result['max_drawdown']
            })

        results_by_allocation[allocation] = results

    # Create comprehensive table
    print("="*120)
    print("RETURNS BY LEVERAGE LEVEL")
    print("="*120)
    print(f"\n{'Leverage':<10} {'Count':<8} {'P5':<8} {'P25':<8} {'Median':<8} {'P75':<8} "
          f"{'P95':<8} {'Mean':<8} {'IQR Range':<20}")
    print("-"*120)

    for allocation in allocations:
        returns_list = [r['return'] for r in results_by_allocation[allocation]]

        p5 = calculate_percentile(returns_list, 5)
        p25 = calculate_percentile(returns_list, 25)
        p50 = calculate_percentile(returns_list, 50)
        p75 = calculate_percentile(returns_list, 75)
        p95 = calculate_percentile(returns_list, 95)
        mean = calculate_mean(returns_list)

        iqr_range = f"{p25:.1f}% - {p75:.1f}%"

        print(f"{allocation:>3}% lev   {len(returns_list):<8} "
              f"{p5:>6.2f}%  {p25:>6.2f}%  {p50:>6.2f}%  {p75:>6.2f}%  "
              f"{p95:>6.2f}%  {mean:>6.2f}%  {iqr_range:<20}")

    # Sharpe ratio table
    print("\n" + "="*120)
    print("SHARPE RATIOS BY LEVERAGE LEVEL")
    print("="*120)
    print(f"\n{'Leverage':<10} {'P5':<10} {'P25':<10} {'Median':<10} {'P75':<10} "
          f"{'P95':<10} {'IQR Range':<20}")
    print("-"*120)

    for allocation in allocations:
        sharpe_list = [r['sharpe'] for r in results_by_allocation[allocation]]

        p5 = calculate_percentile(sharpe_list, 5)
        p25 = calculate_percentile(sharpe_list, 25)
        p50 = calculate_percentile(sharpe_list, 50)
        p75 = calculate_percentile(sharpe_list, 75)
        p95 = calculate_percentile(sharpe_list, 95)

        iqr_range = f"{p25:.3f} - {p75:.3f}"

        print(f"{allocation:>3}% lev   {p5:>8.3f}  {p25:>8.3f}  {p50:>8.3f}  {p75:>8.3f}  "
              f"{p95:>8.3f}  {iqr_range:<20}")

    # Maximum Drawdown table
    print("\n" + "="*120)
    print("MAXIMUM DRAWDOWNS BY LEVERAGE LEVEL")
    print("="*120)
    print(f"\n{'Leverage':<10} {'P5':<10} {'P25':<10} {'Median':<10} {'P75':<10} "
          f"{'P95':<10} {'IQR Range':<20}")
    print("-"*120)

    for allocation in allocations:
        dd_list = [r['max_drawdown'] for r in results_by_allocation[allocation]]

        p5 = calculate_percentile(dd_list, 5)
        p25 = calculate_percentile(dd_list, 25)
        p50 = calculate_percentile(dd_list, 50)
        p75 = calculate_percentile(dd_list, 75)
        p95 = calculate_percentile(dd_list, 95)

        iqr_range = f"{p25:.1f}% - {p75:.1f}%"

        print(f"{allocation:>3}% lev   {p5:>8.2f}%  {p25:>8.2f}%  {p50:>8.2f}%  {p75:>8.2f}%  "
              f"{p95:>8.2f}%  {iqr_range:<20}")

    # Summary highlights
    print("\n" + "="*120)
    print("KEY INSIGHTS")
    print("="*120)

    # Find optimal by median return
    best_median_alloc = max(allocations,
                           key=lambda a: calculate_percentile([r['return'] for r in results_by_allocation[a]], 50))
    best_median_return = calculate_percentile([r['return'] for r in results_by_allocation[best_median_alloc]], 50)

    # Find optimal by median Sharpe
    best_sharpe_alloc = max(allocations,
                           key=lambda a: calculate_percentile([r['sharpe'] for r in results_by_allocation[a]], 50))
    best_sharpe = calculate_percentile([r['sharpe'] for r in results_by_allocation[best_sharpe_alloc]], 50)

    print(f"\n✓ Best Median Return:  {best_median_alloc}% leveraged → {best_median_return:.2f}%")
    print(f"✓ Best Median Sharpe:  {best_sharpe_alloc}% leveraged → {best_sharpe:.3f}")

    # IQR explanation
    print(f"\nIQR (Interquartile Range) = P25 to P75")
    print(f"  → This range contains the middle 50% of all outcomes")
    print(f"  → Shows the 'typical' range you can expect")
    print("="*120)


def main():
    """Create detailed tables for all indices."""
    print("╔" + "="*118 + "╗")
    print("║" + " "*30 + "DETAILED LEVERAGE ALLOCATION TABLES" + " "*53 + "║")
    print("║" + " "*20 + "Median Returns & Interquartile Ranges for 0-100% Leverage" + " "*41 + "║")
    print("╚" + "="*118 + "╝")
    print()
    print("This analysis shows detailed statistics for every 5% leverage increment.")
    print("IQR (Interquartile Range) = 25th to 75th percentile (middle 50% of outcomes)")
    print()

    indices = [
        ('S&P 500', 'sp500_stooq_daily.csv', 'Date', 'Close', 1950),
        ('DJIA', 'djia_stooq_daily.csv', 'Date', 'Close', 1950),
        ('NASDAQ', 'nasdaq_fred.csv', 'observation_date', 'NASDAQCOM', 1971),
        ('Nikkei 225', 'nikkei225_fred.csv', 'observation_date', 'NIKKEI225', 1950),
    ]

    for name, filename, date_col, price_col, start_year in indices:
        create_detailed_table(name, filename, date_col, price_col, start_year, years=10)


if __name__ == '__main__':
    main()
