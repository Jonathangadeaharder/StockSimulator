# Trading Strategies

This module provides a comprehensive collection of trading strategies for use with the StockSimulator backtesting framework.

## Table of Contents

- [Overview](#overview)
- [Strategy Categories](#strategy-categories)
- [Quick Start](#quick-start)
- [Strategy Reference](#strategy-reference)
- [Creating Custom Strategies](#creating-custom-strategies)
- [Best Practices](#best-practices)

## Overview

All strategies inherit from `BaseStrategy` and implement a common interface:

```python
def calculate_allocation(
    current_date: date,
    market_data: Dict[str, MarketData],
    portfolio: Portfolio,
    current_prices: Dict[str, float]
) -> Dict[str, float]:
    """Return target allocation as dict of symbol -> percentage"""
    pass
```

## Strategy Categories

### 1. Fixed Allocation / DCA

**Philosophy**: Buy and hold with periodic rebalancing

- `DCAStrategy`: Basic dollar-cost averaging with fixed allocations
- `FixedAllocationStrategy`: Alias for DCA
- `Balanced6040Strategy`: Classic 60/40 stocks/bonds
- `AllWeatherStrategy`: Ray Dalio's All Weather Portfolio
- `ThreeFundPortfolio`: Bogleheads three-fund approach

**Best For**: Long-term investors, passive investing, retirement accounts

### 2. Momentum

**Philosophy**: Buy what's going up, sell what's going down

- `MomentumStrategy`: Relative strength momentum
- `DualMomentumStrategy`: Antonacci's absolute + relative momentum
- `MovingAverageCrossoverStrategy`: Golden/Death cross signals
- `RotationalMomentumStrategy`: Rotate between top performers

**Best For**: Trending markets, capturing bull runs, tactical allocation

### 3. Mean Reversion

**Philosophy**: Buy low, sell high (contrarian)

- `MeanReversionStrategy`: Z-score based mean reversion
- `BollingerBandsStrategy`: Buy at lower band, sell at upper
- `RSIMeanReversionStrategy`: Oversold/overbought signals
- `PairsTradingStrategy`: Statistical arbitrage between pairs

**Best For**: Range-bound markets, short-term trading, pairs trading

### 4. Risk Parity

**Philosophy**: Balance risk, not dollars

- `RiskParityStrategy`: Equal risk contribution
- `VolatilityTargetingStrategy`: Maintain constant volatility
- `EqualRiskContributionStrategy`: Advanced ERC with correlations
- `MinimumVarianceStrategy`: Minimize portfolio volatility

**Best For**: Risk management, all-weather performance, institutional portfolios

## Quick Start

### Example 1: Run a Simple Backtest

```python
from src.stocksimulator.core.backtester import Backtester
from src.stocksimulator.strategies import Balanced6040Strategy
from datetime import date

# Create strategy
strategy = Balanced6040Strategy()

# Initialize backtester
backtester = Backtester(initial_cash=100000.0)

# Run backtest
result = backtester.run_backtest(
    strategy_name="60/40 Portfolio",
    market_data=market_data,  # Your loaded data
    strategy_func=strategy,
    start_date=date(2010, 1, 1),
    end_date=date(2024, 12, 31),
    rebalance_frequency='quarterly'
)

# Get results
summary = result.get_performance_summary()
print(f"Annual Return: {summary['annualized_return']:.2f}%")
print(f"Sharpe Ratio: {summary['sharpe_ratio']:.3f}")
print(f"Max Drawdown: {summary['max_drawdown']:.2f}%")
```

### Example 2: Compare Multiple Strategies

```python
from src.stocksimulator.strategies import (
    Balanced6040Strategy,
    MomentumStrategy,
    RiskParityStrategy
)

strategies = {
    "60/40": Balanced6040Strategy(),
    "Momentum": MomentumStrategy(lookback_days=126, top_n=3),
    "Risk Parity": RiskParityStrategy()
}

results = backtester.compare_strategies(
    strategies=strategies,
    market_data=market_data,
    start_date=date(2010, 1, 1),
    end_date=date(2024, 12, 31)
)

for name, result in results.items():
    summary = result.get_performance_summary()
    print(f"{name}: {summary['annualized_return']:.2f}%")
```

## Strategy Reference

### DCA / Fixed Allocation

#### `Balanced6040Strategy`

Classic 60/40 portfolio (60% stocks, 40% bonds).

```python
strategy = Balanced6040Strategy(
    stock_symbol='SPY',         # Stock ETF
    bond_symbol='TLT',          # Bond ETF
    stock_allocation=60.0,      # Stock percentage
    rebalance_threshold=5.0     # Rebalance when drift > 5%
)
```

**Parameters**:
- `stock_symbol`: Stock ETF symbol
- `bond_symbol`: Bond ETF symbol
- `stock_allocation`: Percentage in stocks (default: 60%)
- `rebalance_threshold`: Rebalance trigger (default: 5%)

#### `AllWeatherStrategy`

Ray Dalio's All Weather Portfolio.

```python
strategy = AllWeatherStrategy(
    symbols={
        'stocks': 'SPY',
        'long_bonds': 'TLT',
        'intermediate_bonds': 'IEF',
        'gold': 'GLD',
        'commodities': 'DBC'
    }
)
```

**Default Allocation**:
- 30% Stocks
- 40% Long-term Bonds
- 15% Intermediate Bonds
- 7.5% Gold
- 7.5% Commodities

### Momentum

#### `MomentumStrategy`

Buys assets with strongest recent performance.

```python
strategy = MomentumStrategy(
    lookback_days=126,          # 6-month lookback
    top_n=2,                    # Hold top 2 performers
    equal_weight=True,          # Equal weight holdings
    momentum_threshold=0.0      # Minimum momentum to invest
)
```

**Key Insight**: "Buy strength, sell weakness"

#### `DualMomentumStrategy`

Combines absolute and relative momentum (Gary Antonacci's approach).

```python
strategy = DualMomentumStrategy(
    symbols=['SPY', 'VEA', 'VWO'],  # US, Developed, Emerging
    lookback_days=126,               # 6-month momentum
    cash_proxy='SHY'                 # Cash substitute
)
```

**Logic**:
1. Find asset with highest relative momentum
2. If absolute momentum > 0, invest in that asset
3. If absolute momentum ≤ 0, go to cash

#### `MovingAverageCrossoverStrategy`

Golden Cross / Death Cross strategy.

```python
strategy = MovingAverageCrossoverStrategy(
    symbol='SPY',
    fast_period=50,      # 50-day MA
    slow_period=200,     # 200-day MA
    cash_proxy='SHY'
)
```

**Signals**:
- **Bullish**: Fast MA > Slow MA → 100% invested
- **Bearish**: Fast MA < Slow MA → Go to cash

### Mean Reversion

#### `BollingerBandsStrategy`

Buy at lower band, sell at upper band.

```python
strategy = BollingerBandsStrategy(
    lookback_days=20,    # 20-day MA
    num_std=2.0          # 2 standard deviations
)
```

**Bands**: MA ± (2 × Standard Deviation)

**Signals**:
- Price ≤ Lower Band → Buy signal
- Price ≥ Upper Band → Sell signal

#### `RSIMeanReversionStrategy`

RSI-based oversold/overbought strategy.

```python
strategy = RSIMeanReversionStrategy(
    rsi_period=14,
    oversold_threshold=30.0,    # Buy when RSI < 30
    overbought_threshold=70.0   # Sell when RSI > 70
)
```

**RSI Scale**: 0-100
- RSI < 30: Oversold (buy signal)
- RSI > 70: Overbought (sell signal)

### Risk Parity

#### `RiskParityStrategy`

Equal risk contribution from each asset.

```python
strategy = RiskParityStrategy(
    lookback_days=252,      # 1-year volatility
    min_allocation=5.0,     # Min 5% per asset
    max_allocation=50.0     # Max 50% per asset
)
```

**Logic**: Lower volatility assets get higher allocations to equalize risk.

#### `VolatilityTargetingStrategy`

Maintains constant portfolio volatility.

```python
strategy = VolatilityTargetingStrategy(
    symbol='SPY',
    target_volatility=0.10,  # Target 10% annual vol
    lookback_days=60,
    max_allocation=100.0
)
```

**Formula**: Allocation = (Target Vol / Current Vol) × 100%

**Use Case**: Dynamic leverage/de-leverage based on market volatility.

## Creating Custom Strategies

### Step 1: Inherit from BaseStrategy

```python
from src.stocksimulator.strategies import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    def __init__(self, my_parameter=10):
        super().__init__(
            name="My Custom Strategy",
            description="Description of what it does",
            parameters={'my_parameter': my_parameter}
        )
        self.my_parameter = my_parameter
```

### Step 2: Implement calculate_allocation

```python
    def calculate_allocation(self, current_date, market_data, portfolio, current_prices):
        """
        Calculate target allocation.

        Returns:
            Dict[str, float]: symbol -> allocation percentage
        """
        allocation = {}

        # Your strategy logic here
        for symbol, md in market_data.items():
            # Get historical data
            data = self.get_lookback_data(md, current_date, lookback_days=20)

            # Calculate indicators
            ma = self.calculate_moving_average(data, period=20)

            # Make allocation decision
            if data[-1].close > ma:
                allocation[symbol] = 50.0

        return allocation
```

### Step 3: Use Helper Methods

The `BaseStrategy` class provides helper methods:

```python
# Get lookback data
data = self.get_lookback_data(market_data, current_date, lookback_days=252)

# Calculate moving average
ma = self.calculate_moving_average(data, period=50)

# Calculate returns
returns = self.calculate_returns(data, period=1)

# Calculate volatility
vol = self.calculate_volatility(returns, annualize=True)

# Validate allocation
is_valid = self.validate_allocation(allocation)
```

### Example: Hybrid Strategy

```python
class MomentumMeanReversionHybrid(BaseStrategy):
    """
    Combines long-term momentum with short-term mean reversion.
    """

    def __init__(self, momentum_days=126, reversion_days=20):
        super().__init__(
            name="Momentum-MeanReversion Hybrid",
            description="Long-term momentum + short-term reversion",
            parameters={
                'momentum_days': momentum_days,
                'reversion_days': reversion_days
            }
        )
        self.momentum_days = momentum_days
        self.reversion_days = reversion_days

    def calculate_allocation(self, current_date, market_data, portfolio, current_prices):
        allocation = {}

        for symbol, md in market_data.items():
            # Long-term momentum filter
            momentum_data = self.get_lookback_data(md, current_date, self.momentum_days)
            if len(momentum_data) < self.momentum_days:
                continue

            momentum = (momentum_data[-1].close - momentum_data[0].close) / momentum_data[0].close

            # Only consider assets with positive long-term momentum
            if momentum > 0:
                # Short-term mean reversion entry
                reversion_data = self.get_lookback_data(md, current_date, self.reversion_days)
                if len(reversion_data) < self.reversion_days:
                    continue

                ma = self.calculate_moving_average(reversion_data, self.reversion_days)
                current_price = reversion_data[-1].close

                # Buy when price is below MA but has positive momentum
                if current_price < ma:
                    allocation[symbol] = 50.0

        return allocation
```

## Best Practices

### 1. Parameter Selection

- **Lookback Periods**: Longer = more stable but slower to react
  - Short-term: 20-60 days
  - Medium-term: 60-126 days
  - Long-term: 126-252 days

- **Rebalance Frequency**: Balance trading costs vs drift
  - Daily: High turnover, high costs
  - Weekly/Monthly: Good balance
  - Quarterly: Low turnover, larger drift

### 2. Risk Management

- **Diversification**: Don't allocate >50% to single asset
- **Cash Buffers**: Keep 5-10% cash for opportunities
- **Stop Losses**: Use momentum filters to exit bear markets
- **Volatility Targeting**: Scale position size by volatility

### 3. Backtesting Tips

- **Lookback Bias**: Ensure strategy only uses past data
- **Transaction Costs**: Include realistic costs (2-10 bps)
- **Multiple Regimes**: Test on bull, bear, and sideways markets
- **Out-of-Sample**: Reserve recent data for validation

### 4. Combining Strategies

```python
class MultiStrategy(BaseStrategy):
    """Run multiple strategies and combine allocations."""

    def __init__(self, strategies, weights):
        self.strategies = strategies
        self.weights = weights

    def calculate_allocation(self, current_date, market_data, portfolio, current_prices):
        combined = {}

        for strategy, weight in zip(self.strategies, self.weights):
            allocation = strategy.calculate_allocation(
                current_date, market_data, portfolio, current_prices
            )

            for symbol, pct in allocation.items():
                combined[symbol] = combined.get(symbol, 0) + (pct * weight)

        return combined
```

### 5. Strategy Selection Guide

| Market Regime | Best Strategy Type |
|---------------|-------------------|
| **Strong Bull** | Momentum |
| **Bear Market** | Defensive (bonds, cash) |
| **Sideways/Choppy** | Mean Reversion |
| **High Volatility** | Risk Parity, Vol Targeting |
| **Low Volatility** | Momentum, Growth |

## Performance Expectations

### Expected Sharpe Ratios

- **Buy & Hold (60/40)**: 0.5 - 0.8
- **Momentum**: 0.6 - 1.0
- **Mean Reversion**: 0.3 - 0.7 (higher turnover)
- **Risk Parity**: 0.7 - 1.2
- **Combined**: 0.8 - 1.5

### Expected Turnover

- **DCA/Fixed**: 5-20% annually
- **Momentum**: 50-200% annually
- **Mean Reversion**: 200-500% annually
- **Risk Parity**: 20-50% annually

## Further Reading

- **Momentum**: "Dual Momentum Investing" by Gary Antonacci
- **Risk Parity**: "Risk Parity Fundamentals" by Edward Qian
- **Mean Reversion**: "Evidence-Based Technical Analysis" by David Aronson
- **Backtesting**: "Advances in Financial Machine Learning" by Marcos López de Prado

## Support

For questions or issues:
- GitHub Issues: [StockSimulator Issues](https://github.com/Jonathangadeaharder/StockSimulator/issues)
- Documentation: See `docs/` directory
- Examples: See `examples/strategy_comparison.py`
