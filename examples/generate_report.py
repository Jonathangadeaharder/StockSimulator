"""
Example: Generate HTML Performance Report

Demonstrates how to generate comprehensive HTML reports with charts.
"""

import sys
import os
from datetime import date

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from stocksimulator.core.backtester import Backtester
from stocksimulator.data import load_from_csv
from stocksimulator.reporting import HTMLReportGenerator


def simple_buy_and_hold_strategy(current_date, market_data, portfolio, current_prices):
    """Simple buy and hold SPY strategy."""
    return {'SPY': 100.0}


def balanced_60_40_strategy(current_date, market_data, portfolio, current_prices):
    """Balanced 60/40 stocks/bonds strategy."""
    return {
        'SPY': 60.0,  # 60% stocks
        'TLT': 40.0   # 40% bonds
    }


def main():
    """Generate HTML reports for different strategies."""
    print("=" * 80)
    print("HTML REPORT GENERATION EXAMPLE")
    print("=" * 80)
    print()

    # Load market data
    print("Loading market data...")
    spy_data = load_from_csv('sp500_stooq_daily.csv', 'SPY', 'historical_data')
    print(f"✓ Loaded {len(spy_data.data)} data points for SPY")
    print()

    # Set backtest period (last 5 years)
    end_date = spy_data.data[-1].date
    start_date = date(end_date.year - 5, end_date.month, end_date.day)

    # Strategy 1: Buy and Hold
    print("Running Buy & Hold strategy...")
    backtester = Backtester(initial_cash=100000.0, transaction_cost_bps=2.0)

    result1 = backtester.run_backtest(
        strategy_name='Buy & Hold SPY',
        market_data={'SPY': spy_data},
        strategy_func=simple_buy_and_hold_strategy,
        start_date=start_date,
        end_date=end_date,
        rebalance_frequency='monthly'
    )

    summary1 = result1.get_performance_summary()
    print(f"  Total Return: {summary1['total_return']:+.2f}%")
    print(f"  Sharpe Ratio: {summary1['sharpe_ratio']:.3f}")
    print()

    # Generate report
    print("Generating HTML report...")
    generator = HTMLReportGenerator()

    report_path = generator.generate_report(
        backtest_result=result1,
        output_file='reports/buy_and_hold_report.html',
        strategy_description='Simple buy-and-hold strategy investing 100% in SPY (S&P 500 ETF)'
    )

    print(f"✓ Report saved to: {report_path}")
    print()

    # Strategy 2: 60/40 Portfolio (if TLT data available)
    print("Checking for TLT data...")
    try:
        tlt_data = load_from_csv('tlt_stooq_daily.csv', 'TLT', 'historical_data')
        print(f"✓ Found TLT data")
        print()

        print("Running 60/40 strategy...")
        result2 = backtester.run_backtest(
            strategy_name='Balanced 60/40',
            market_data={'SPY': spy_data, 'TLT': tlt_data},
            strategy_func=balanced_60_40_strategy,
            start_date=start_date,
            end_date=end_date,
            rebalance_frequency='monthly'
        )

        summary2 = result2.get_performance_summary()
        print(f"  Total Return: {summary2['total_return']:+.2f}%")
        print(f"  Sharpe Ratio: {summary2['sharpe_ratio']:.3f}")
        print()

        report_path2 = generator.generate_report(
            backtest_result=result2,
            output_file='reports/balanced_60_40_report.html',
            strategy_description='Classic balanced portfolio: 60% SPY (stocks) / 40% TLT (bonds), rebalanced monthly'
        )

        print(f"✓ Report saved to: {report_path2}")
        print()

    except FileNotFoundError:
        print("  ⚠ TLT data not found, skipping 60/40 strategy")
        print("  (Download TLT data to run this example)")
        print()

    # Comparison
    print("=" * 80)
    print("REPORTS GENERATED SUCCESSFULLY")
    print("=" * 80)
    print()
    print("Next steps:")
    print(f"  1. Open {report_path} in your browser")
    print("  2. View interactive charts and statistics")
    print("  3. Compare multiple strategies")
    print()
    print("Note: Install matplotlib for better charts:")
    print("  pip install matplotlib")
    print()


if __name__ == '__main__':
    main()
