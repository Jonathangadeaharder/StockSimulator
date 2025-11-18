#!/usr/bin/env python3
# @structurelint:no-test
"""
Complete Working Backtest Example

This example demonstrates a complete end-to-end backtest using actual historical data.
"""

import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.stocksimulator.data.loaders import load_from_csv, get_available_symbols
from src.stocksimulator.core.backtester import Backtester
from src.stocksimulator.strategies import (
    Balanced6040Strategy,
    MomentumStrategy,
    RiskParityStrategy
)


def main():
    """Run complete backtest example."""

    print("=" * 80)
    print("STOCKSIMULATOR - COMPLETE BACKTEST EXAMPLE")
    print("=" * 80)
    print()

    # Step 1: Discover available data
    print("Step 1: Discovering available data...")
    available = get_available_symbols('historical_data')
    print(f"Found {len(available)} datasets: {', '.join(available[:5])}")
    if len(available) > 5:
        print(f"  ... and {len(available) - 5} more")
    print()

    # Step 2: Load market data
    print("Step 2: Loading market data...")
    print("  Loading S&P 500 data...")

    try:
        spy_data = load_from_csv('sp500_stooq_daily.csv', 'SPY', 'historical_data')
        print(f"  ✓ Loaded {len(spy_data.data)} data points for SPY")
        print(f"    Date range: {spy_data.metadata['start_date']} to {spy_data.metadata['end_date']}")
    except Exception as e:
        print(f"  ✗ Error loading SPY data: {e}")
        print("\nPlease ensure sp500_stooq_daily.csv exists in historical_data/")
        return

    # For this example, we'll use SPY for both stocks and bonds
    # In practice, you'd load TLT data separately
    market_data = {
        'SPY': spy_data,
        # 'TLT': tlt_data  # Would load bond data here
    }
    print()

    # Step 3: Define strategy
    print("Step 3: Defining trading strategy...")

    # Simple buy-and-hold SPY strategy
    def buy_hold_spy(current_date, market_data, portfolio, current_prices):
        """Simple buy and hold SPY."""
        return {'SPY': 100.0}  # 100% in SPY

    print("  Using: Buy & Hold SPY (100% allocation)")
    print()

    # Step 4: Run backtest
    print("Step 4: Running backtest...")

    backtester = Backtester(
        initial_cash=100000.0,
        transaction_cost_bps=2.0  # 2 basis points transaction cost
    )

    # Use last 10 years of data for backtest
    all_dates = sorted([d.date for d in spy_data.data])
    if len(all_dates) > 2520:  # More than 10 years
        start_date = all_dates[-2520]  # Last 10 years (252 trading days/year)
        end_date = all_dates[-1]
    else:
        start_date = all_dates[0]
        end_date = all_dates[-1]

    print(f"  Backtest period: {start_date} to {end_date}")
    print(f"  Initial capital: $100,000")
    print(f"  Transaction costs: 2 bps")
    print()

    try:
        result = backtester.run_backtest(
            strategy_name="Buy & Hold SPY",
            market_data=market_data,
            strategy_func=buy_hold_spy,
            start_date=start_date,
            end_date=end_date,
            rebalance_frequency='quarterly'
        )

        # Step 5: Display results
        print("=" * 80)
        print("BACKTEST RESULTS")
        print("=" * 80)
        print()

        summary = result.get_performance_summary()

        print(f"Strategy: {summary['strategy_name']}")
        print(f"Period: {summary['days']} days ({summary['days']/252:.1f} years)")
        print()

        print("PERFORMANCE METRICS:")
        print(f"  Initial Value:       ${summary['initial_value']:>12,.2f}")
        print(f"  Final Value:         ${summary['final_value']:>12,.2f}")
        print(f"  Total Return:        {summary['total_return']:>12.2f}%")
        print(f"  Annualized Return:   {summary['annualized_return']:>12.2f}%")
        print()

        print("RISK METRICS:")
        print(f"  Volatility:          {summary['volatility']:>12.2f}%")
        print(f"  Sharpe Ratio:        {summary['sharpe_ratio']:>12.3f}")
        print(f"  Max Drawdown:        {summary['max_drawdown']:>12.2f}%")
        print()

        print("TRADING:")
        print(f"  Num Transactions:    {summary['num_transactions']:>12d}")
        print(f"  Win Rate:            {summary['win_rate']:>12.1f}%")
        print()

    except Exception as e:
        print(f"Error running backtest: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 6: Show how to compare strategies
    print("=" * 80)
    print("COMPARING MULTIPLE STRATEGIES")
    print("=" * 80)
    print()
    print("Example: How to compare different strategies")
    print()

    print("""
# Define multiple strategies:
strategies = {
    "Buy & Hold": buy_hold_spy,
    "Momentum": MomentumStrategy(lookback_days=126, top_n=1),
    "Risk Parity": RiskParityStrategy(lookback_days=252)
}

# Compare them:
results = backtester.compare_strategies(
    strategies=strategies,
    market_data=market_data,
    start_date=start_date,
    end_date=end_date
)

# Print comparison:
for name, result in results.items():
    summary = result.get_performance_summary()
    print(f"{name:20s} {summary['annualized_return']:>8.2f}%  Sharpe: {summary['sharpe_ratio']:.3f}")
    """)

    print()
    print("=" * 80)
    print("✓ Example completed successfully!")
    print()
    print("Next steps:")
    print("  1. Load multiple assets (SPY, TLT, GLD, etc.)")
    print("  2. Try different strategies from src/stocksimulator/strategies/")
    print("  3. Adjust backtest parameters (dates, rebalance frequency, etc.)")
    print("  4. Compare strategies to find optimal approach")
    print()
    print("See examples/strategy_comparison.py for more examples")
    print("=" * 80)


if __name__ == "__main__":
    main()
