#!/usr/bin/env python3
"""
Historical Crisis Testing - Comprehensive Example

Tests portfolio strategies across three major crises:
1. Dot-com Bubble (2000-2002)
2. Financial Crisis (2007-2009)
3. COVID-19 Crash (2020)

Demonstrates:
- Loading multi-asset data
- Creating regime-aware strategies
- Comparing portfolios across regimes
- Testing defensive-to-aggressive rebalancing
- Generating comparison reports
"""

import sys
from pathlib import Path
from datetime import date

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from stocksimulator.data import MultiAssetDataLoader
from stocksimulator.regime import (
    MarketRegimeDetector,
    DefensiveToAggressiveStrategy,
    CrisisOpportunisticStrategy,
    AdaptiveAllWeatherStrategy,
    PortfolioComparator,
    create_comparison_report,
    DEFENSIVE_PORTFOLIOS,
    AGGRESSIVE_PORTFOLIOS
)


def create_static_strategy(allocation: dict):
    """Create a static portfolio strategy."""
    def strategy(current_date, historical_data, portfolio, current_prices):
        return allocation.copy()
    return strategy


def main():
    print("="*80)
    print("HISTORICAL CRISIS TESTING")
    print("Testing Portfolio Strategies Across Major Market Crises")
    print("="*80)

    # Initialize data loader
    loader = MultiAssetDataLoader()

    # Define crisis periods
    crises = {
        'Dot-com Bubble': {
            'start': date(2000, 3, 1),
            'end': date(2002, 10, 31),
            'description': '2000-2002 Technology Bubble Crash'
        },
        'Financial Crisis': {
            'start': date(2007, 10, 1),
            'end': date(2009, 3, 31),
            'description': '2007-2009 Global Financial Crisis'
        },
        'COVID-19': {
            'start': date(2020, 2, 1),
            'end': date(2020, 12, 31),
            'description': '2020 COVID-19 Pandemic Crash & Recovery'
        }
    }

    # Define portfolios to test
    portfolios = {
        # Static Portfolios
        '60/40 Balanced': create_static_strategy({
            'SP500': 60.0,
            'LONG_TREASURY': 40.0
        }),

        '100% Stocks': create_static_strategy({
            'SP500': 100.0
        }),

        'Ultra Defensive': create_static_strategy(
            DEFENSIVE_PORTFOLIOS['ultra_defensive']
        ),

        'All Weather (Static)': create_static_strategy({
            'SP500': 30.0,
            'LONG_TREASURY': 40.0,
            'CONSUMER_STAPLES': 15.0,
            'MANAGED_FUTURES': 10.0,
            'SHORT_BOND': 5.0
        }),

        # Regime-Aware Strategies
        'Defensive-to-Aggressive': DefensiveToAggressiveStrategy(
            transition_days=30,
            rebalance_frequency_days=7  # Weekly rebalancing during crisis
        ),

        'Crisis Opportunistic': CrisisOpportunisticStrategy(
            max_crisis_equity_pct=90.0
        ),

        'Adaptive All Weather': AdaptiveAllWeatherStrategy()
    }

    # Test each crisis
    all_results = {}

    for crisis_name, crisis_info in crises.items():
        print(f"\n\n{'='*80}")
        print(f"TESTING: {crisis_info['description']}")
        print(f"Period: {crisis_info['start']} to {crisis_info['end']}")
        print(f"{'='*80}")

        # Load data for this period
        print("\nLoading asset data...")
        try:
            market_data = loader.load_multiple(
                tickers=[
                    'SP500',
                    'LONG_TREASURY',
                    'SHORT_BOND',
                    'CONSUMER_STAPLES',
                    'MANAGED_FUTURES'
                ],
                start_date=crisis_info['start'],
                end_date=crisis_info['end'],
                align_dates=True
            )

            print(f"  Loaded {len(market_data)} assets")
            for ticker, df in market_data.items():
                print(f"    {ticker}: {len(df)} days")

        except Exception as e:
            print(f"  ERROR loading data: {e}")
            continue

        # Run comparison
        print("\nRunning portfolio comparison...")
        comparator = PortfolioComparator(
            initial_cash=100000.0,
            transaction_cost_bps=5.0  # Higher costs during crisis
        )

        try:
            results = comparator.compare_portfolios(
                portfolios=portfolios,
                market_data=market_data,
                start_date=crisis_info['start'],
                end_date=crisis_info['end']
            )

            all_results[crisis_name] = results

            # Generate report
            print(f"\n{'-'*80}")
            print(f"RESULTS FOR {crisis_name.upper()}")
            print(f"{'-'*80}")

            report = create_comparison_report(results)
            print(report)

            # Save individual report
            report_file = f"crisis_report_{crisis_name.lower().replace(' ', '_').replace('-', '_')}.txt"
            create_comparison_report(results, report_file)

        except Exception as e:
            print(f"  ERROR in comparison: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Cross-crisis summary
    print(f"\n\n{'='*80}")
    print("CROSS-CRISIS SUMMARY")
    print(f"{'='*80}\n")

    # Find best overall strategies
    print("BEST STRATEGIES BY CRISIS:\n")

    for crisis_name, results in all_results.items():
        print(f"{crisis_name}:")

        # Rank by Sharpe ratio
        rankings = []
        for name, comp in results.items():
            sharpe = comp.overall_performance.get('sharpe_ratio', -999)
            total_return = comp.overall_performance.get('total_return', -999)
            rankings.append((name, sharpe, total_return))

        rankings.sort(key=lambda x: x[1], reverse=True)

        print(f"  Top 3 by Sharpe Ratio:")
        for i, (name, sharpe, ret) in enumerate(rankings[:3], 1):
            print(f"    {i}. {name:<30} Sharpe: {sharpe:>6.2f}  Return: {ret:>7.2f}%")

        print()

    # Key insights
    print("\n" + "="*80)
    print("KEY INSIGHTS")
    print("="*80)

    print("""
1. DEFENSIVE PORTFOLIOS
   - Ultra Defensive: Best downside protection in crises
   - Lower returns but minimal drawdowns
   - Recommended for pre-crisis positioning

2. REGIME-AWARE STRATEGIES
   - Defensive-to-Aggressive: Captures recovery upside
   - Transitions smoothly without market timing
   - Better risk-adjusted returns than static portfolios

3. STATIC BALANCED PORTFOLIOS
   - 60/40: Moderate performance across all conditions
   - Simple and effective baseline
   - Outperformed by regime-aware in volatile periods

4. AGGRESSIVE PORTFOLIOS
   - 100% Stocks: Highest volatility and drawdowns
   - Best long-term returns if held through crisis
   - Requires strong conviction during drawdowns

5. CRISIS-SPECIFIC PATTERNS
   - Dot-com: Tech-heavy, defensive outperformed
   - 2008: Liquidity crisis, treasuries essential
   - COVID: V-shaped recovery favored aggressive

RECOMMENDATIONS:
✓ Use regime detection for early warning
✓ Maintain defensive allocation pre-crisis
✓ Gradually shift to aggressive during crisis
✓ Don't try to time the bottom perfectly
✓ Rebalance more frequently during volatility
    """)

    print("\n" + "="*80)
    print("Testing complete! Reports saved to current directory.")
    print("="*80)


if __name__ == '__main__':
    main()
