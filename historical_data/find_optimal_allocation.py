#!/usr/bin/env python3
"""
Find the optimal leveraged/unleveraged portfolio allocation.

Tests all allocations from 0-100% in 5% increments across full historical data.
"""

from portfolio_optimization_enhanced import EnhancedPortfolioOptimizer


def find_optimal_allocation(name, filename, date_col, price_col, start_year, rebalance_months=3):
    """Find optimal allocation for an index."""
    print(f"\n{'='*100}")
    print(f"OPTIMAL ALLOCATION ANALYSIS: {name}")
    print(f"{'='*100}")
    print(f"Rebalancing: {'Quarterly' if rebalance_months == 3 else 'Monthly' if rebalance_months == 1 else 'Buy & Hold'}")
    print()

    optimizer = EnhancedPortfolioOptimizer(name, filename, date_col, price_col, start_year)

    # Load data
    data = optimizer.analyzer.read_data()
    returns = optimizer.analyzer.calculate_returns(data)
    leveraged_returns = optimizer.analyzer.simulate_leveraged_etf(returns)

    # Test all allocations
    results = []
    for allocation in range(0, 101, 5):
        result = optimizer.simulate_portfolio(
            leveraged_returns,
            allocation,
            years=len(leveraged_returns) / 252.0,
            rebalance_months=rebalance_months,
            transaction_cost_bps=2.0
        )
        results.append(result)

    # Find optimal by different metrics
    best_sharpe = max(results, key=lambda x: x['sharpe_ratio'])
    best_return = max(results, key=lambda x: x['annualized_return'])
    min_drawdown = min(results, key=lambda x: x['max_drawdown'])

    print(f"{'Metric':<25} {'Allocation':<15} {'Value':<15}")
    print('-'*100)
    print(f"{'Best Sharpe Ratio':<25} {best_sharpe['lev_allocation']:>3}% leveraged   "
          f"Sharpe: {best_sharpe['sharpe_ratio']:.3f}")
    print(f"{'Best Return':<25} {best_return['lev_allocation']:>3}% leveraged   "
          f"Return: {best_return['annualized_return']:.2f}%")
    print(f"{'Minimum Drawdown':<25} {min_drawdown['lev_allocation']:>3}% leveraged   "
          f"Drawdown: {min_drawdown['max_drawdown']:.2f}%")

    print(f"\n{'DETAILED RESULTS:':<100}")
    print(f"\n{'Allocation':<12} {'Return':<12} {'Volatility':<12} {'Sharpe':<12} {'Max DD':<12} {'Final Value':<15}")
    print('-'*100)

    for r in results:
        marker = ""
        if r['lev_allocation'] == best_sharpe['lev_allocation']:
            marker = " ← Best Sharpe"

        print(f"{r['lev_allocation']:>3}% lev    {r['annualized_return']:>10.2f}%  "
              f"{r['volatility']:>10.2f}%  {r['sharpe_ratio']:>10.3f}  "
              f"{r['max_drawdown']:>9.2f}%  ${r['final_value']:>13,.0f}{marker}")

    return best_sharpe


def main():
    """Find optimal allocations for all indices."""
    print("╔" + "="*98 + "╗")
    print("║" + " "*30 + "OPTIMAL PORTFOLIO ALLOCATION FINDER" + " "*33 + "║")
    print("║" + " "*25 + "Full Historical Data with Transaction Costs" + " "*30 + "║")
    print("╚" + "="*98 + "╝")

    indices = [
        ('S&P 500', 'sp500_stooq_daily.csv', 'Date', 'Close', 1950),
        ('DJIA', 'djia_stooq_daily.csv', 'Date', 'Close', 1950),
        ('NASDAQ', 'nasdaq_fred.csv', 'observation_date', 'NASDAQCOM', 1971),
        ('Nikkei 225', 'nikkei225_fred.csv', 'observation_date', 'NIKKEI225', 1950),
    ]

    # Test quarterly rebalancing (most practical)
    print("\n" + "="*100)
    print("QUARTERLY REBALANCING (Recommended)")
    print("="*100)

    optimal_allocations = []
    for name, filename, date_col, price_col, start_year in indices:
        best = find_optimal_allocation(name, filename, date_col, price_col, start_year, rebalance_months=3)
        optimal_allocations.append((name, best))

    # Summary
    print("\n" + "="*100)
    print("SUMMARY: OPTIMAL ALLOCATIONS BY SHARPE RATIO")
    print("="*100)
    print(f"\n{'Index':<15} {'Optimal Mix':<30} {'Sharpe':<12} {'Return':<12} {'Volatility':<12}")
    print('-'*100)

    for name, result in optimal_allocations:
        mix_desc = f"{result['lev_allocation']}% 2x Lev / {100-result['lev_allocation']}% Unlev"
        print(f"{name:<15} {mix_desc:<30} {result['sharpe_ratio']:>10.3f}  "
              f"{result['annualized_return']:>10.2f}%  {result['volatility']:>10.2f}%")

    print("\n" + "="*100)
    print("KEY INSIGHTS:")
    print("="*100)

    # Find highest Sharpe overall
    best_overall = max(optimal_allocations, key=lambda x: x[1]['sharpe_ratio'])
    print(f"✓ Best risk-adjusted returns: {best_overall[0]} with {best_overall[1]['lev_allocation']}% leveraged")
    print(f"  → Sharpe Ratio: {best_overall[1]['sharpe_ratio']:.3f}")

    # Find highest return
    best_return_overall = max(optimal_allocations, key=lambda x: x[1]['annualized_return'])
    print(f"✓ Highest returns: {best_return_overall[0]} with {best_return_overall[1]['lev_allocation']}% leveraged")
    print(f"  → Annualized Return: {best_return_overall[1]['annualized_return']:.2f}%")

    print("\n✓ All allocations use quarterly rebalancing with 2 bps transaction costs")
    print("✓ Historical risk-free rates vary by era (4.5% 1950s, 9% 1980s, 0.5% 2008-2015)")
    print("="*100)


if __name__ == '__main__':
    main()
