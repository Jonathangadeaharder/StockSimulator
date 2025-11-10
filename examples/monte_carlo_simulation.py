"""
Example: Monte Carlo Simulation

Demonstrates how to run Monte Carlo simulations to assess strategy robustness.
"""

import sys
import os
from datetime import date

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from stocksimulator.data import load_from_csv
from stocksimulator.simulation import MonteCarloSimulator
from stocksimulator.strategies import MomentumStrategy


def simple_strategy(current_date, market_data, portfolio, current_prices):
    """Simple buy and hold strategy."""
    return {'SPY': 100.0}


def main():
    """Run Monte Carlo simulation examples."""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 23 + "MONTE CARLO SIMULATION" + " " * 33 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # Load data
    print("Loading market data...")
    spy_data = load_from_csv('sp500_stooq_daily.csv', 'SPY', 'historical_data')
    print(f"✓ Loaded {len(spy_data.data)} data points")
    print()

    # Set backtest period
    end_date = spy_data.data[-1].date
    start_date = date(end_date.year - 5, end_date.month, end_date.day)

    # Example 1: Bootstrap simulation
    print("=" * 80)
    print("EXAMPLE 1: BOOTSTRAP SIMULATION")
    print("=" * 80)
    print()
    print("Bootstrap resampling tests strategy robustness by randomly")
    print("sampling historical data with replacement.")
    print()

    simulator = MonteCarloSimulator()

    result = simulator.run_simulations(
        strategy_func=simple_strategy,
        market_data={'SPY': spy_data},
        num_simulations=500,  # Run 500 simulations
        simulation_method='bootstrap',
        start_date=start_date,
        end_date=end_date
    )

    stats = result.get_statistics()

    print("=" * 80)
    print("BOOTSTRAP RESULTS")
    print("=" * 80)
    print()
    print(f"Number of simulations: {stats['num_simulations']}")
    print()
    print("Total Return Distribution:")
    print(f"  Mean:          {stats['returns']['mean']:>8.2f}%")
    print(f"  Median:        {stats['returns']['median']:>8.2f}%")
    print(f"  5th percentile:{stats['returns']['p5']:>8.2f}%")
    print(f"  95th percentile:{stats['returns']['p95']:>8.2f}%")
    print(f"  Min:           {stats['returns']['min']:>8.2f}%")
    print(f"  Max:           {stats['returns']['max']:>8.2f}%")
    print()
    print("Sharpe Ratio Distribution:")
    print(f"  Mean:          {stats['sharpe_ratio']['mean']:>8.3f}")
    print(f"  Median:        {stats['sharpe_ratio']['median']:>8.3f}")
    print(f"  5th percentile:{stats['sharpe_ratio']['p5']:>8.3f}")
    print(f"  95th percentile:{stats['sharpe_ratio']['p95']:>8.3f}")
    print()
    print("Max Drawdown Distribution:")
    print(f"  Mean:          {stats['max_drawdown']['mean']:>8.2f}%")
    print(f"  Median:        {stats['max_drawdown']['median']:>8.2f}%")
    print(f"  Best (min):    {stats['max_drawdown']['best']:>8.2f}%")
    print(f"  Worst (max):   {stats['max_drawdown']['worst']:>8.2f}%")
    print()

    # Example 2: Shuffled returns simulation
    print("=" * 80)
    print("EXAMPLE 2: SHUFFLED RETURNS SIMULATION")
    print("=" * 80)
    print()
    print("Shuffling returns preserves the return distribution but")
    print("randomizes the sequence to test timing sensitivity.")
    print()

    result2 = simulator.run_simulations(
        strategy_func=simple_strategy,
        market_data={'SPY': spy_data},
        num_simulations=500,
        simulation_method='shuffle_returns',
        start_date=start_date,
        end_date=end_date
    )

    stats2 = result2.get_statistics()

    print("=" * 80)
    print("SHUFFLED RETURNS RESULTS")
    print("=" * 80)
    print()
    print("Total Return Distribution:")
    print(f"  Median:        {stats2['returns']['median']:>8.2f}%")
    print(f"  5th percentile:{stats2['returns']['p5']:>8.2f}%")
    print(f"  95th percentile:{stats2['returns']['p95']:>8.2f}%")
    print()

    # Example 3: Parameter uncertainty
    print("=" * 80)
    print("EXAMPLE 3: PARAMETER UNCERTAINTY")
    print("=" * 80)
    print()
    print("Testing how parameter uncertainty affects strategy performance.")
    print()

    result3 = simulator.run_parameter_uncertainty(
        strategy_class=MomentumStrategy,
        param_ranges={
            'lookback_days': (30, 252),  # Test lookback from 30 to 252 days
            'top_n': (1, 5)               # Test holding 1 to 5 positions
        },
        market_data={'SPY': spy_data},
        num_simulations=300,
        start_date=start_date,
        end_date=end_date
    )

    stats3 = result3.get_statistics()

    print("=" * 80)
    print("PARAMETER UNCERTAINTY RESULTS")
    print("=" * 80)
    print()
    print("With randomly varied parameters:")
    print(f"  Median return: {stats3['returns']['median']:>8.2f}%")
    print(f"  5th percentile:{stats3['returns']['p5']:>8.2f}%")
    print(f"  95th percentile:{stats3['returns']['p95']:>8.2f}%")
    print()
    print(f"  Median Sharpe: {stats3['sharpe_ratio']['median']:>8.3f}")
    print()

    # Get specific percentile results
    print("=" * 80)
    print("PERCENTILE ANALYSIS")
    print("=" * 80)
    print()

    p50_result = result.get_percentile_result(50)
    p5_result = result.get_percentile_result(5)
    p95_result = result.get_percentile_result(95)

    print("50th Percentile (Median) Scenario:")
    summary_p50 = p50_result.get_performance_summary()
    print(f"  Return: {summary_p50['total_return']:+.2f}%")
    print(f"  Sharpe: {summary_p50['sharpe_ratio']:.3f}")
    print()

    print("5th Percentile (Pessimistic) Scenario:")
    summary_p5 = p5_result.get_performance_summary()
    print(f"  Return: {summary_p5['total_return']:+.2f}%")
    print(f"  Sharpe: {summary_p5['sharpe_ratio']:.3f}")
    print()

    print("95th Percentile (Optimistic) Scenario:")
    summary_p95 = p95_result.get_performance_summary()
    print(f"  Return: {summary_p95['total_return']:+.2f}%")
    print(f"  Sharpe: {summary_p95['sharpe_ratio']:.3f}")
    print()

    print("=" * 80)
    print("COMPLETE!")
    print("=" * 80)
    print()
    print("Key Insights:")
    print("  - Bootstrap shows variability from data sampling")
    print("  - Shuffled returns shows sensitivity to sequence")
    print("  - Parameter uncertainty shows robustness to parameter choices")
    print()
    print("Next steps:")
    print("  1. Use confidence intervals for risk assessment")
    print("  2. Compare multiple strategies with Monte Carlo")
    print("  3. Set position sizes based on worst-case scenarios")
    print()


if __name__ == '__main__':
    main()
