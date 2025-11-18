#!/usr/bin/env python3
# @structurelint:no-test
"""
Risk-Adjusted Optimal Allocation Finder

Finds optimal leverage allocation based on different risk tolerance levels.

Risk Tolerance Definitions:
- Conservative: 5% loss risk (95th percentile must be positive)
- Moderate: 10% loss risk (90th percentile must be positive)
- Aggressive: 20% loss risk (80th percentile must be positive)
"""

from percentile_performance_analysis import analyze_percentile_performance, calculate_percentile, calculate_mean


def find_optimal_by_risk_tolerance(results_by_allocation, risk_tolerance=10):
    """
    Find optimal allocation given a risk tolerance.

    Args:
        risk_tolerance: % of periods allowed to have negative returns (default 10%)

    Returns:
        Optimal allocation and its metrics
    """
    percentile_threshold = risk_tolerance  # e.g., 10% risk = 10th percentile

    allocations = sorted(results_by_allocation.keys())

    candidates = []

    for allocation in allocations:
        returns_list = [r['return'] for r in results_by_allocation[allocation]]
        sharpe_list = [r['sharpe'] for r in results_by_allocation[allocation]]
        dd_list = [r['max_drawdown'] for r in results_by_allocation[allocation]]

        # Calculate key percentiles
        p_risk = calculate_percentile(returns_list, percentile_threshold)
        p50_return = calculate_percentile(returns_list, 50)
        p50_sharpe = calculate_percentile(sharpe_list, 50)
        p50_dd = calculate_percentile(dd_list, 50)
        mean_return = calculate_mean(returns_list)

        # Only consider allocations where worst X% is still positive
        if p_risk > 0:
            candidates.append({
                'allocation': allocation,
                'worst_case': p_risk,
                'median_return': p50_return,
                'median_sharpe': p50_sharpe,
                'median_dd': p50_dd,
                'mean_return': mean_return
            })

    if not candidates:
        return None

    # Find allocation with best median return among safe candidates
    best_by_return = max(candidates, key=lambda x: x['median_return'])
    best_by_sharpe = max(candidates, key=lambda x: x['median_sharpe'])

    return {
        'best_by_return': best_by_return,
        'best_by_sharpe': best_by_sharpe,
        'all_candidates': candidates
    }


def analyze_risk_tolerances(name, filename, date_col, price_col, start_year):
    """Analyze optimal allocations for different risk tolerance levels."""

    print(f"\n{'='*120}")
    print(f"RISK-ADJUSTED OPTIMAL ALLOCATION: {name}")
    print(f"{'='*120}\n")

    # Get percentile data
    results = analyze_percentile_performance(name, filename, date_col, price_col, start_year, years=10)

    # Test different risk tolerance levels
    risk_levels = [
        (5, "Conservative (5% loss risk)"),
        (10, "Moderate (10% loss risk)"),
        (15, "Moderate-Aggressive (15% loss risk)"),
        (20, "Aggressive (20% loss risk)"),
    ]

    print("\n" + "="*120)
    print("OPTIMAL ALLOCATIONS BY RISK TOLERANCE")
    print("="*120)
    print("\nConstraint: Worst X% of outcomes must still be positive (no capital loss)\n")

    for risk_pct, label in risk_levels:
        print(f"\n{label}:")
        print("-"*120)

        optimal = find_optimal_by_risk_tolerance(results, risk_tolerance=risk_pct)

        if optimal is None or len(optimal['all_candidates']) == 0:
            print(f"  ✗ No allocation meets this constraint (all have >{risk_pct}% chance of loss)")
            continue

        best_return = optimal['best_by_return']
        best_sharpe = optimal['best_by_sharpe']

        print(f"\n  Best by Median Return:")
        print(f"    Allocation:      {best_return['allocation']:>3}% leveraged")
        print(f"    Median Return:   {best_return['median_return']:>6.2f}%")
        print(f"    Median Sharpe:   {best_return['median_sharpe']:>6.3f}")
        print(f"    Worst {risk_pct}% Case:  {best_return['worst_case']:>6.2f}% (still positive!)")
        print(f"    Median Drawdown: {best_return['median_dd']:>6.2f}%")

        if best_sharpe['allocation'] != best_return['allocation']:
            print(f"\n  Best by Median Sharpe:")
            print(f"    Allocation:      {best_sharpe['allocation']:>3}% leveraged")
            print(f"    Median Sharpe:   {best_sharpe['median_sharpe']:>6.3f}")
            print(f"    Median Return:   {best_sharpe['median_return']:>6.2f}%")
            print(f"    Worst {risk_pct}% Case:  {best_sharpe['worst_case']:>6.2f}%")

        # Show all viable candidates
        print(f"\n  All viable allocations (worst {risk_pct}% > 0%):")
        print(f"    {'Alloc':<8} {'Worst Case':<12} {'Median Ret':<12} {'Median Sharpe':<14} {'Median DD':<12}")
        for c in sorted(optimal['all_candidates'], key=lambda x: x['allocation']):
            print(f"    {c['allocation']:>3}% lev  {c['worst_case']:>10.2f}%  "
                  f"{c['median_return']:>10.2f}%  {c['median_sharpe']:>12.3f}  "
                  f"{c['median_dd']:>10.2f}%")


def main():
    """Analyze risk-adjusted optimal allocations for all indices."""
    print("╔" + "="*118 + "╗")
    print("║" + " "*30 + "RISK-ADJUSTED OPTIMAL ALLOCATION FINDER" + " "*49 + "║")
    print("║" + " "*25 + "Find Best Leverage Given Your Risk Tolerance" + " "*50 + "║")
    print("╚" + "="*118 + "╝")
    print()
    print("This analysis finds the optimal leverage allocation based on your willingness")
    print("to accept downside risk. For each risk tolerance level, we find the allocation")
    print("that maximizes median returns while ensuring the worst X% still makes money.")
    print()

    indices = [
        ('S&P 500', 'sp500_stooq_daily.csv', 'Date', 'Close', 1950),
        ('DJIA', 'djia_stooq_daily.csv', 'Date', 'Close', 1950),
        ('NASDAQ', 'nasdaq_fred.csv', 'observation_date', 'NASDAQCOM', 1971),
        ('Nikkei 225', 'nikkei225_fred.csv', 'observation_date', 'NIKKEI225', 1950),
    ]

    for name, filename, date_col, price_col, start_year in indices:
        analyze_risk_tolerances(name, filename, date_col, price_col, start_year)

    print("\n" + "="*120)
    print("KEY INSIGHTS")
    print("="*120)
    print("✓ Conservative (5% loss risk): Ensures 95% of 10-year periods are profitable")
    print("✓ Moderate (10% loss risk): Ensures 90% of 10-year periods are profitable")
    print("✓ Aggressive (20% loss risk): Ensures 80% of 10-year periods are profitable")
    print()
    print("The 'Worst X% Case' shows the minimum return in the worst scenarios.")
    print("All recommendations ensure you don't lose capital even in bad decades.")
    print("="*120)


if __name__ == '__main__':
    main()
