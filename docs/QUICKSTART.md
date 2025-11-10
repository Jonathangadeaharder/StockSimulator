# Quick Start Guide

Get up and running with StockSimulator in 5 minutes!

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Jonathangadeaharder/StockSimulator.git
cd StockSimulator
```

### 2. Install Dependencies

```bash
# Core dependencies (minimal - pure Python)
pip install -r requirements.txt

# Development dependencies (for testing and development)
pip install -r requirements-dev.txt
```

### 3. Verify Installation

```bash
# Run tests
pytest tests/ -v

# Should see: All tests passing ✓
```

## Basic Usage

### Example 1: Find Optimal Allocation

Find the optimal leveraged/unleveraged mix for S&P 500:

```bash
python historical_data/find_optimal_allocation.py
```

**Output**:
```
OPTIMAL ALLOCATION ANALYSIS: S&P 500
================================================================================
Best Sharpe Ratio:    0% leveraged → Sharpe: 0.842
Best Return:        100% leveraged → Return: 16.04%
Minimum Drawdown:     0% leveraged → Drawdown: 33.81%
```

### Example 2: Percentile Performance Analysis

Analyze the distribution of outcomes across all historical periods:

```bash
python historical_data/percentile_performance_analysis.py
```

**Output**:
```
PERCENTILE PERFORMANCE ANALYSIS: S&P 500
================================================================================

ANNUALIZED RETURN PERCENTILES (10-year periods)
Allocation    Count    5th %      25th %     50th %     75th %     95th %
  0% lev      265      0.75%      6.50%     10.13%     13.30%     17.89%
 50% lev      265      2.84%      7.90%     13.25%     18.10%     24.56%
100% lev      265     -0.68%      8.50%     16.04%     22.30%     30.12%
```

**Key Insight**: 100% leveraged has highest median (16.04%) but can lose money (5th percentile: -0.68%)

### Example 3: Risk-Adjusted Allocation

Find the best allocation for your risk tolerance:

```bash
python historical_data/risk_adjusted_allocation.py
```

**Output**:
```
RISK-ADJUSTED OPTIMAL ALLOCATION: S&P 500
================================================================================

Conservative (5% loss risk):
  Best by Median Return:
    Allocation:       75% leveraged
    Median Return:   14.55%
    Worst 5% Case:   +0.36% (still positive!)

Moderate (10% loss risk):
  Best by Median Return:
    Allocation:      100% leveraged
    Median Return:   16.04%
    Worst 10% Case:  +1.04% (still positive!)
```

### Example 4: Detailed Leverage Table

See comprehensive statistics for all leverage levels:

```bash
python historical_data/detailed_leverage_table.py
```

## Using the Python API

### Example: Run a Backtest

```python
from src.stocksimulator.core.backtester import Backtester
from src.stocksimulator.models.market_data import MarketData, OHLCV
from datetime import date

# Define a simple strategy
def buy_and_hold_strategy(current_date, market_data, portfolio, current_prices):
    """Simple 60/40 portfolio"""
    return {'SPY': 60.0, 'TLT': 40.0}

# Load historical data (example - you'd load from CSV/API)
spy_data = MarketData(symbol='SPY', data=[
    OHLCV(date=date(2020, 1, 2), open=320, high=325, low=318, close=322, volume=1000000),
    # ... more data
])

tlt_data = MarketData(symbol='TLT', data=[
    OHLCV(date=date(2020, 1, 2), open=140, high=142, low=139, close=141, volume=500000),
    # ... more data
])

# Run backtest
backtester = Backtester(initial_cash=100000.0)
result = backtester.run_backtest(
    strategy_name="60/40 Portfolio",
    market_data={'SPY': spy_data, 'TLT': tlt_data},
    strategy_func=buy_and_hold_strategy,
    rebalance_frequency='quarterly'
)

# Get results
summary = result.get_performance_summary()
print(f"Total Return: {summary['total_return']:.2f}%")
print(f"Sharpe Ratio: {summary['sharpe_ratio']:.3f}")
print(f"Max Drawdown: {summary['max_drawdown']:.2f}%")
```

### Example: Calculate Risk Metrics

```python
from src.stocksimulator.core.risk_calculator import RiskCalculator

# Daily returns (example)
returns = [0.01, -0.005, 0.02, -0.01, 0.015, 0.008, -0.003]
values = [100000, 101000, 100495, 102505, 101479, 103001, 103825, 103513]

# Calculate risk metrics
risk_calc = RiskCalculator(risk_free_rate=0.02)

volatility = risk_calc.calculate_volatility(returns)
sharpe = risk_calc.calculate_sharpe_ratio(returns)
max_dd = risk_calc.calculate_max_drawdown(values)

print(f"Annualized Volatility: {volatility:.2%}")
print(f"Sharpe Ratio: {sharpe:.3f}")
print(f"Maximum Drawdown: {max_dd:.2f}%")
```

## Understanding the Results

### The Leverage Paradox

Our analysis reveals a critical paradox:

- **100% leveraged wins 83% of the time** (over 10-year periods)
- **BUT 0% leveraged is Sharpe-optimal** (best risk-adjusted returns)
- **5th percentile for 100% leveraged**: -0.68% (can lose money!)

This happens because:
1. High win rate doesn't justify catastrophic tail risk
2. Kelly Criterion math: Don't bet big when losses can be devastating
3. Sharpe ratio properly accounts for volatility and worst-case scenarios

### Risk-Adjusted Recommendations

| Risk Tolerance | Recommended Allocation | Expected Median Return | Worst-Case Scenario |
|----------------|------------------------|------------------------|---------------------|
| **Conservative** (5% loss risk) | 50-75% leveraged | 13-15% | +0.36% to +2.00% |
| **Moderate** (10% loss risk) | 100% leveraged | 16.04% | +1.04% |
| **Aggressive** (20% loss risk) | 100% leveraged | 16.04% | Can be negative |

### NASDAQ Sweet Spot

NASDAQ 50% leveraged offers the **best risk/reward ratio**:
- **+38%** return improvement vs unleveraged
- **+42%** drawdown increase
- **Trade-off ratio: 1.0:1.10** (best among all indices)

This means you get 38% more return for only 42% more risk - the best deal available!

## Key Concepts

### 1. Rolling Windows

We analyze **265 rolling 10-year windows** (for S&P 500):
- Window size: 10 years (2,520 trading days)
- Step size: 3 months (63 trading days)
- Coverage: All market regimes since 1950

### 2. Empirical Costs

We use **empirical costs from research** (not theoretical):
- Total leveraged ETF costs: ~2.1% annually
- Components:
  - 0.6% TER (Total Expense Ratio)
  - 1.5% excess costs (swap financing, volatility drag, etc.)
- Era-specific: Higher in Volcker era, lower in ZIRP era

### 3. Percentiles

- **5th percentile**: Worst 5% of outcomes (bear markets)
- **50th percentile (median)**: Typical outcome
- **95th percentile**: Best 5% of outcomes (bull markets)
- **IQR (25th-75th)**: Middle 50% of realistic outcomes

## Next Steps

### Explore More

1. **Read the full research findings**:
   - [Percentile Performance Analysis](../PERCENTILE_PERFORMANCE.md)
   - [Risk-Adjusted Allocation](../RISK_ADJUSTED_ALLOCATION.md)
   - [Detailed Leverage Tables](../DETAILED_LEVERAGE_TABLE.md)

2. **Understand the architecture**:
   - [Architecture Overview](./ARCHITECTURE.md)
   - [API Documentation](./api/)

3. **Contribute**:
   - [Contributing Guidelines](../CONTRIBUTING.md)
   - [Development Setup](../CONTRIBUTING.md#development-setup)

### Run Your Own Analysis

Customize the analysis for your needs:

```python
# Example: Analyze different time horizon
from historical_data.percentile_performance_analysis import analyze_percentile_performance

# 5-year windows instead of 10-year
results = analyze_percentile_performance(
    'S&P 500',
    'sp500_stooq_daily.csv',
    'Date',
    'Close',
    1950,
    years=5  # Changed from default 10
)
```

### Build Custom Strategies

```python
def momentum_strategy(current_date, market_data, portfolio, current_prices):
    """
    Example: Simple momentum strategy
    Go 100% into asset with best 6-month performance
    """
    # Calculate 6-month returns for each asset
    returns_6m = {}
    for symbol, md in market_data.items():
        recent_data = md.get_latest(126)  # ~6 months
        if len(recent_data) >= 2:
            ret = (recent_data[0].close - recent_data[-1].close) / recent_data[-1].close
            returns_6m[symbol] = ret

    # Find best performer
    best_symbol = max(returns_6m, key=returns_6m.get)

    # Return 100% allocation to best
    return {best_symbol: 100.0}
```

## Common Issues

### Issue: Import Errors

**Problem**: `ModuleNotFoundError: No module named 'stocksimulator'`

**Solution**:
```bash
# Install package in development mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### Issue: Data Not Found

**Problem**: `FileNotFoundError: sp500_stooq_daily.csv`

**Solution**:
```bash
# Make sure you're in the project root
cd /path/to/StockSimulator

# Check data files exist
ls historical_data/*.csv
```

### Issue: Tests Failing

**Problem**: Some tests fail with assertion errors

**Solution**:
```bash
# Update dependencies
pip install -r requirements-dev.txt --upgrade

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -name "*.pyc" -delete

# Run tests again
pytest tests/ -v
```

## Getting Help

- **Documentation**: Check the [docs/](.) directory
- **Issues**: [GitHub Issues](https://github.com/Jonathangadeaharder/StockSimulator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Jonathangadeaharder/StockSimulator/discussions)

---

**Ready to dive deeper?** Check out the [full documentation](./README.md) or explore the [architecture](./ARCHITECTURE.md)!
