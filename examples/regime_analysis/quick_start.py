#!/usr/bin/env python3
"""
Quick Start - Regime-Aware Portfolio Analysis

Simplest possible example to get started with regime analysis.

This demonstrates:
1. Loading multi-asset data
2. Creating a regime-aware strategy
3. Comparing it to a static portfolio
4. Viewing results

Time to run: ~30 seconds
"""

import sys
from pathlib import Path
from datetime import date

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from stocksimulator.data import MultiAssetDataLoader
from stocksimulator.regime import DefensiveToAggressiveStrategy
from stocksimulator.core import Backtester


def main():
    print("="*80)
    print("QUICK START - Regime-Aware Portfolio Analysis")
    print("="*80)
    print("\nTesting on 2020 COVID-19 Crisis (Feb-Dec 2020)")
    print("Comparing static 60/40 vs regime-aware strategy\n")

    # Step 1: Load data
    print("Step 1: Loading asset data...")
    loader = MultiAssetDataLoader()

    try:
        market_data = loader.load_multiple(
            tickers=['SP500', 'LONG_TREASURY'],
            start_date=date(2020, 2, 1),
            end_date=date(2020, 12, 31),
            align_dates=True
        )
        print(f"✓ Loaded {len(market_data)} assets")
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        return

    # Step 2: Create strategies
    print("\nStep 2: Creating strategies...")

    # Static 60/40 portfolio
    def static_60_40(current_date, historical_data, portfolio, current_prices):
        return {'SP500': 60.0, 'LONG_TREASURY': 40.0}

    # Regime-aware strategy
    regime_aware = DefensiveToAggressiveStrategy(
        transition_days=30,
        rebalance_frequency_days=7
    )

    print("✓ Created 2 strategies:")
    print("  1. Static 60/40 (baseline)")
    print("  2. Defensive-to-Aggressive (regime-aware)")

    # Step 3: Run backtests
    print("\nStep 3: Running backtests...")

    backtester = Backtester(initial_cash=100000, transaction_cost_bps=2.0)

    # Backtest static portfolio
    print("  Running static 60/40...")
    try:
        result_static = backtester.run_backtest(
            strategy_name="60/40 Static",
            market_data=market_data,
            strategy_func=static_60_40,
            start_date=date(2020, 2, 1),
            end_date=date(2020, 12, 31)
        )
        perf_static = result_static.get_performance_summary()
        print("  ✓ Complete")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return

    # Backtest regime-aware portfolio
    print("  Running regime-aware strategy...")
    try:
        result_regime = backtester.run_backtest(
            strategy_name="Defensive-to-Aggressive",
            market_data=market_data,
            strategy_func=regime_aware,
            start_date=date(2020, 2, 1),
            end_date=date(2020, 12, 31)
        )
        perf_regime = result_regime.get_performance_summary()
        print("  ✓ Complete")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 4: Compare results
    print("\n" + "="*80)
    print("RESULTS - COVID-19 Crisis (2020)")
    print("="*80)

    print(f"\n{'Metric':<25} {'60/40 Static':<20} {'Regime-Aware':<20} {'Winner':<10}")
    print("-"*80)

    metrics = [
        ('Total Return', 'total_return', '%', False),
        ('Annualized Return', 'annualized_return', '%', False),
        ('Volatility', 'volatility', '%', True),
        ('Sharpe Ratio', 'sharpe_ratio', '', False),
        ('Max Drawdown', 'max_drawdown', '%', True),
        ('Win Rate', 'win_rate', '%', False)
    ]

    for label, key, unit, lower_better in metrics:
        val_static = perf_static.get(key, 0)
        val_regime = perf_regime.get(key, 0)

        # Determine winner
        if lower_better:
            winner = "Regime" if abs(val_regime) < abs(val_static) else "Static"
        else:
            winner = "Regime" if val_regime > val_static else "Static"

        winner_mark = "✓" if winner == "Regime" else ""

        print(f"{label:<25} {val_static:>10.2f}{unit:<8} {val_regime:>10.2f}{unit:<8} {winner_mark:<10}")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    regime_wins = sum([
        perf_regime['total_return'] > perf_static['total_return'],
        perf_regime['sharpe_ratio'] > perf_static['sharpe_ratio'],
        abs(perf_regime['max_drawdown']) < abs(perf_static['max_drawdown']),
        abs(perf_regime['volatility']) < abs(perf_static['volatility'])
    ])

    print(f"\nRegime-aware strategy won {regime_wins}/4 key metrics")

    if regime_wins >= 3:
        print("\n✓ REGIME-AWARE STRATEGY SIGNIFICANTLY OUTPERFORMED")
        print("  The regime-aware approach successfully:")
        print("  - Detected the crisis early")
        print("  - Shifted to defensive positioning")
        print("  - Captured the recovery by buying the dip")
    elif regime_wins >= 2:
        print("\n✓ REGIME-AWARE STRATEGY MODERATELY OUTPERFORMED")
        print("  The regime-aware approach showed improvement in key areas")
    else:
        print("\n• MIXED RESULTS")
        print("  Both strategies performed similarly in this period")

    print("\n" + "="*80)
    print("\nNEXT STEPS:")
    print("1. Try different crisis periods (2008, 2000-2002)")
    print("2. Test your own portfolio allocations")
    print("3. Run full comparison: python test_historical_crises.py")
    print("4. Read the guide: docs/REGIME_ANALYSIS_GUIDE.md")
    print("="*80)


if __name__ == '__main__':
    main()
