#!/usr/bin/env python3
"""
Strategy Comparison Example

Demonstrates how to use the StockSimulator strategies with the backtesting framework.
This example compares multiple strategies on historical data.
"""

import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.stocksimulator.core.backtester import Backtester
from src.stocksimulator.models.market_data import MarketData, OHLCV
from src.stocksimulator.strategies import (
    Balanced6040Strategy,
    AllWeatherStrategy,
    MomentumStrategy,
    DualMomentumStrategy,
    RiskParityStrategy,
    MovingAverageCrossoverStrategy
)


def load_sample_data():
    """
    Load sample market data for demonstration.

    In a real application, you would load this from CSV files or APIs.
    This creates synthetic data for demonstration purposes.
    """
    print("Loading sample market data...")

    # In practice, you would load real data like this:
    # from historical_data.analyze_data import load_data
    # spy_data = load_data('historical_data/sp500_stooq_daily.csv', 'Date', 'Close')

    # For this example, we'll create a simple placeholder
    # You should replace this with actual data loading
    market_data = {
        'SPY': MarketData(symbol='SPY', data=[]),
        'TLT': MarketData(symbol='TLT', data=[]),
        'GLD': MarketData(symbol='GLD', data=[]),
    }

    print("Note: This example requires real market data to run.")
    print("Please load historical data from CSV files or APIs.")
    print()

    return market_data


def compare_strategies():
    """
    Compare multiple trading strategies.

    This example demonstrates:
    1. Creating different strategy instances
    2. Running backtests for each strategy
    3. Comparing performance metrics
    """

    print("="*80)
    print("STRATEGY COMPARISON EXAMPLE")
    print("="*80)
    print()

    # Load market data
    market_data = load_sample_data()

    # Define strategies to compare
    strategies = {
        "60/40 Balanced": Balanced6040Strategy(
            stock_symbol='SPY',
            bond_symbol='TLT',
            stock_allocation=60.0
        ),

        "All Weather": AllWeatherStrategy(),

        "Momentum (6-month)": MomentumStrategy(
            lookback_days=126,  # ~6 months
            top_n=2,
            equal_weight=True
        ),

        "Dual Momentum": DualMomentumStrategy(
            symbols=['SPY', 'VEA', 'VWO'],
            lookback_days=126,
            cash_proxy='SHY'
        ),

        "Risk Parity": RiskParityStrategy(
            lookback_days=252,
            min_allocation=5.0,
            max_allocation=50.0
        ),

        "MA Crossover (50/200)": MovingAverageCrossoverStrategy(
            symbol='SPY',
            fast_period=50,
            slow_period=200,
            cash_proxy='SHY'
        ),
    }

    print(f"Comparing {len(strategies)} strategies:")
    for name in strategies.keys():
        print(f"  - {name}")
    print()

    # Note: This example requires real data to run
    # The code below shows how you would run the comparison
    print("="*80)
    print("EXAMPLE CODE (requires real market data)")
    print("="*80)
    print()

    print("""
# Initialize backtester
backtester = Backtester(
    initial_cash=100000.0,
    transaction_cost_bps=2.0
)

# Run backtest for each strategy
results = {}

for strategy_name, strategy in strategies.items():
    print(f"Running backtest for: {strategy_name}")

    result = backtester.run_backtest(
        strategy_name=strategy_name,
        market_data=market_data,
        strategy_func=strategy,  # Strategies are callable
        start_date=date(2010, 1, 1),
        end_date=date(2024, 12, 31),
        rebalance_frequency='quarterly'
    )

    results[strategy_name] = result

# Compare results
print()
print("="*80)
print("PERFORMANCE COMPARISON")
print("="*80)
print()

# Print summary table
print(f"{'Strategy':<30} {'Return':<12} {'Sharpe':<10} {'Max DD':<10} {'Trades':<10}")
print("-"*80)

for strategy_name, result in results.items():
    summary = result.get_performance_summary()

    print(f"{strategy_name:<30} "
          f"{summary['annualized_return']:>10.2f}% "
          f"{summary['sharpe_ratio']:>10.3f} "
          f"{summary['max_drawdown']:>10.2f}% "
          f"{summary['num_transactions']:>10d}")

print()
print("="*80)
    """)


def strategy_usage_examples():
    """
    Show basic usage examples for each strategy type.
    """

    print("="*80)
    print("STRATEGY USAGE EXAMPLES")
    print("="*80)
    print()

    print("1. BALANCED 60/40 PORTFOLIO")
    print("-" * 40)
    print("""
from src.stocksimulator.strategies import Balanced6040Strategy

# Classic 60% stocks, 40% bonds
strategy = Balanced6040Strategy(
    stock_symbol='SPY',
    bond_symbol='TLT',
    stock_allocation=60.0,
    rebalance_threshold=5.0  # Rebalance when drift > 5%
)
    """)

    print()
    print("2. MOMENTUM STRATEGY")
    print("-" * 40)
    print("""
from src.stocksimulator.strategies import MomentumStrategy

# Buy top 3 performers over last 6 months
strategy = MomentumStrategy(
    lookback_days=126,  # ~6 months
    top_n=3,            # Hold top 3 assets
    equal_weight=True,  # Equal weight among holdings
    momentum_threshold=0.0  # Only buy positive momentum
)
    """)

    print()
    print("3. DUAL MOMENTUM (ANTONACCI)")
    print("-" * 40)
    print("""
from src.stocksimulator.strategies import DualMomentumStrategy

# Absolute + Relative momentum
strategy = DualMomentumStrategy(
    symbols=['SPY', 'VEA', 'VWO'],  # US, Developed, Emerging
    lookback_days=126,
    cash_proxy='SHY'  # Go to cash if momentum negative
)
    """)

    print()
    print("4. RISK PARITY")
    print("-" * 40)
    print("""
from src.stocksimulator.strategies import RiskParityStrategy

# Equal risk contribution from each asset
strategy = RiskParityStrategy(
    lookback_days=252,   # 1 year volatility
    min_allocation=5.0,  # Min 5% per asset
    max_allocation=50.0  # Max 50% per asset
)
    """)

    print()
    print("5. BOLLINGER BANDS MEAN REVERSION")
    print("-" * 40)
    print("""
from src.stocksimulator.strategies import BollingerBandsStrategy

# Buy at lower band, sell at upper band
strategy = BollingerBandsStrategy(
    lookback_days=20,  # 20-day moving average
    num_std=2.0        # 2 standard deviations
)
    """)

    print()
    print("6. RSI MEAN REVERSION")
    print("-" * 40)
    print("""
from src.stocksimulator.strategies import RSIMeanReversionStrategy

# Buy when oversold, sell when overbought
strategy = RSIMeanReversionStrategy(
    rsi_period=14,
    oversold_threshold=30.0,   # Buy signal
    overbought_threshold=70.0  # Sell signal
)
    """)

    print()
    print("7. MOVING AVERAGE CROSSOVER")
    print("-" * 40)
    print("""
from src.stocksimulator.strategies import MovingAverageCrossoverStrategy

# Golden Cross / Death Cross
strategy = MovingAverageCrossoverStrategy(
    symbol='SPY',
    fast_period=50,   # 50-day MA
    slow_period=200,  # 200-day MA
    cash_proxy='SHY'
)
    """)

    print()
    print("8. VOLATILITY TARGETING")
    print("-" * 40)
    print("""
from src.stocksimulator.strategies import VolatilityTargetingStrategy

# Maintain constant portfolio volatility
strategy = VolatilityTargetingStrategy(
    symbol='SPY',
    target_volatility=0.10,  # Target 10% annual volatility
    lookback_days=60,
    max_allocation=100.0
)
    """)


def custom_strategy_example():
    """
    Show how to create a custom strategy.
    """

    print()
    print("="*80)
    print("CREATING CUSTOM STRATEGIES")
    print("="*80)
    print()

    print("""
from src.stocksimulator.strategies import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    '''
    Example custom strategy that combines momentum and mean reversion.
    '''

    def __init__(self, momentum_lookback=126, reversion_lookback=20):
        super().__init__(
            name="Custom Hybrid Strategy",
            description="Combines momentum and mean reversion",
            parameters={
                'momentum_lookback': momentum_lookback,
                'reversion_lookback': reversion_lookback
            }
        )
        self.momentum_lookback = momentum_lookback
        self.reversion_lookback = reversion_lookback

    def calculate_allocation(self, current_date, market_data, portfolio, current_prices):
        '''Calculate custom allocation.'''

        allocation = {}

        for symbol, md in market_data.items():
            # Calculate long-term momentum
            momentum_data = self.get_lookback_data(md, current_date, self.momentum_lookback)
            if len(momentum_data) >= self.momentum_lookback:
                momentum = (momentum_data[-1].close - momentum_data[0].close) / momentum_data[0].close

                # Only consider assets with positive momentum
                if momentum > 0:
                    # Calculate short-term mean reversion signal
                    reversion_data = self.get_lookback_data(md, current_date, self.reversion_lookback)
                    if len(reversion_data) >= self.reversion_lookback:
                        ma = self.calculate_moving_average(reversion_data, self.reversion_lookback)
                        current_price = reversion_data[-1].close

                        # Buy when price is below MA but long-term momentum is positive
                        if current_price < ma:
                            allocation[symbol] = 50.0  # Allocate 50%

        return allocation

# Usage
strategy = MyCustomStrategy(momentum_lookback=126, reversion_lookback=20)
    """)


def main():
    """Main function."""

    print()
    print("╔" + "="*78 + "╗")
    print("║" + " "*25 + "STOCKSIMULATOR" + " "*40 + "║")
    print("║" + " "*20 + "Strategy Comparison Examples" + " "*29 + "║")
    print("╚" + "="*78 + "╝")
    print()

    # Show strategy comparison
    compare_strategies()

    print()
    input("Press Enter to see usage examples...")
    print()

    # Show usage examples
    strategy_usage_examples()

    print()
    input("Press Enter to see custom strategy example...")
    print()

    # Show custom strategy example
    custom_strategy_example()

    print()
    print("="*80)
    print("Next Steps:")
    print("="*80)
    print()
    print("1. Load real historical data from CSV files or APIs")
    print("2. Choose a strategy or create your own")
    print("3. Run backtests with the Backtester class")
    print("4. Compare results and optimize parameters")
    print()
    print("For more information, see:")
    print("  - docs/QUICKSTART.md")
    print("  - docs/ARCHITECTURE.md")
    print("  - README.md")
    print()


if __name__ == "__main__":
    main()
