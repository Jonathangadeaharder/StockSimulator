# Regime-Aware Portfolio Analysis - Complete Guide

**Version**: 1.0.0
**Date**: 2025-11-20

## Overview

This guide explains how to use StockSimulator's regime-aware portfolio analysis system to test portfolios across different market conditions and optimize crisis transitions.

### What You Can Do

- ✅ Analyze 13+ asset classes (equities, bonds, alternatives, leveraged, short)
- ✅ Detect market regimes (normal, pre-crisis, crisis, recovery)
- ✅ Test portfolios in normal vs crisis conditions
- ✅ Optimize defensive → aggressive transitions
- ✅ Compare strategies side-by-side
- ✅ Backtest on historical crises (2000, 2008, 2020)

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Asset Classes](#asset-classes)
3. [Market Regime Detection](#market-regime-detection)
4. [Regime-Aware Strategies](#regime-aware-strategies)
5. [Crisis Rebalancing](#crisis-rebalancing)
6. [Portfolio Comparison](#portfolio-comparison)
7. [Complete Examples](#complete-examples)
8. [API Reference](#api-reference)

---

## Quick Start

### 5-Minute Example

```python
from datetime import date
from stocksimulator.data import MultiAssetDataLoader
from stocksimulator.regime import (
    DefensiveToAggressiveStrategy,
    PortfolioComparator
)

# 1. Load assets
loader = MultiAssetDataLoader()
market_data = loader.load_multiple(
    ['SP500', 'LONG_TREASURY', 'SHORT_BOND'],
    start_date=date(2007, 10, 1),
    end_date=date(2009, 3, 31)
)

# 2. Create strategies
portfolios = {
    '60/40': lambda cd, hd, p, cp: {'SP500': 60, 'LONG_TREASURY': 40},
    'Crisis Aware': DefensiveToAggressiveStrategy()
}

# 3. Compare
comparator = PortfolioComparator()
results = comparator.compare_portfolios(portfolios, market_data)

# 4. View results
for name, comp in results.items():
    perf = comp.overall_performance
    print(f"{name}: {perf['sharpe_ratio']:.2f} Sharpe, {perf['max_drawdown']:.1f}% DD")
```

---

## Asset Classes

### Available Assets

#### Equity Indices (Historical Data)
```python
'SP500'          # S&P 500 (1950-present)
'WORLD'          # MSCI World Developed Markets
'ACWI'           # MSCI All Country World Index
```

#### Leveraged Positions (Synthetic)
```python
'SP500_2X'       # 2x Leveraged S&P 500
'SP500_3X'       # 3x Leveraged S&P 500
'WORLD_2X'       # 2x Leveraged World Index
```

#### Short Positions (Synthetic)
```python
'SP500_SHORT'    # Inverse S&P 500 (-1x)
'WORLD_SHORT'    # Inverse World Index (-1x)
```

#### Fixed Income (Simulated)
```python
'LONG_TREASURY'  # 20+ Year U.S. Treasury Bonds
'SHORT_BOND'     # 1-3 Year U.S. Treasury Bonds
```

#### Alternatives (Simulated)
```python
'MANAGED_FUTURES'  # Trend-Following CTAs
'CONSUMER_STAPLES' # Consumer Staples Sector (Defensive)
'LOW_VOL'          # Low Volatility Index
```

### Loading Asset Data

```python
from stocksimulator.data import MultiAssetDataLoader

loader = MultiAssetDataLoader()

# Single asset
sp500 = loader.load_asset('SP500',
                          start_date=date(2000, 1, 1),
                          end_date=date(2023, 12, 31))

# Multiple assets (aligned dates)
assets = loader.load_multiple(
    tickers=['SP500', 'LONG_TREASURY', 'MANAGED_FUTURES'],
    start_date=date(2000, 1, 1),
    align_dates=True  # Ensures common dates across all assets
)

# Check available assets
from stocksimulator.data import print_asset_summary
print_asset_summary()
```

### Asset Characteristics

| Asset | Volatility | Correlation to Market | Crisis Behavior |
|-------|------------|----------------------|-----------------|
| SP500 | 16% | 1.00 | High drawdown |
| LONG_TREASURY | 14% | -0.15 | Flight to safety |
| SHORT_BOND | 2% | 0.05 | Stable |
| MANAGED_FUTURES | 12% | 0.00 | Crisis alpha |
| CONSUMER_STAPLES | 11% | 0.65 | Defensive |
| SP500_2X | 32% | 0.99 | 2x the pain/gain |

---

## Market Regime Detection

### The Four Regimes

1. **Normal**: Standard market conditions
   - Drawdown < 15%
   - Volatility near historical average
   - Trending with 200-day MA

2. **Pre-Crisis**: Elevated risk warnings
   - Volatility > 1.5x average
   - Price overextended (>15% above MA200)
   - Early warning signals

3. **Crisis**: Active crash/bear market
   - Drawdown ≥ 15%
   - High volatility
   - Panic selling

4. **Recovery**: Post-crisis recovery
   - Drawdown improving from crisis levels
   - Volatility declining
   - Trend reversing

### Detecting Regimes

```python
from stocksimulator.regime import MarketRegimeDetector
from stocksimulator.data import MultiAssetDataLoader

# Load S&P 500
loader = MultiAssetDataLoader()
sp500 = loader.load_asset('SP500', start_date=date(1950, 1, 1))

# Detect regimes
detector = MarketRegimeDetector(
    crisis_drawdown_threshold=-0.15,  # 15% = crisis
    pre_crisis_vol_multiplier=1.5     # 1.5x vol = warning
)

regimes = detector.detect_regimes(sp500)

# View regime distribution
print(regimes['Regime'].value_counts())

# Get regime periods
periods = detector.get_regime_periods(regimes, min_duration_days=60)

# Find crisis periods
crises = [p for p in periods if p.regime == MarketRegime.CRISIS]
for crisis in crises:
    print(f"{crisis.start_date} to {crisis.end_date}: Severity {crisis.severity:.2f}")
```

### Historical Crisis Database

```python
from stocksimulator.regime import HistoricalCrisisDatabase

# Get all known crises
crises = HistoricalCrisisDatabase.get_crisis_periods()

for start, end, name in crises:
    print(f"{name}: {start} to {end}")

# Check if date is in crisis
crisis_name = HistoricalCrisisDatabase.is_crisis_period(date(2008, 10, 15))
if crisis_name:
    print(f"In crisis: {crisis_name}")
```

### Visualization

```python
from stocksimulator.regime import visualize_regimes

# Visualize regimes over time
regimes = detector.detect_regimes(sp500)
visualize_regimes(regimes, title="S&P 500 Market Regimes")
# Shows: price chart with regime backgrounds, drawdown, severity
```

---

## Regime-Aware Strategies

### Built-in Strategies

#### 1. Defensive-to-Aggressive

Gradually shifts from defensive (bonds) to aggressive (stocks) during/after crisis.

```python
from stocksimulator.regime import DefensiveToAggressiveStrategy

strategy = DefensiveToAggressiveStrategy(
    defensive_assets=['LONG_TREASURY', 'SHORT_BOND'],
    aggressive_assets=['SP500', 'WORLD'],
    recovery_aggressiveness=1.5,    # 50% more aggressive in recovery
    transition_days=30,              # Transition over 30 days
    rebalance_frequency_days=7       # Weekly rebalancing
)
```

**Allocations by Regime:**
- **Normal**: 60% stocks, 30% long treasuries, 10% short bonds
- **Pre-Crisis**: 30% stocks, 40% long treasuries, 20% short bonds, 10% staples
- **Crisis**: 50% long treasuries, 30% short bonds, 15% staples, 5% managed futures
- **Recovery**: 70% stocks, 20% world, 10% treasuries (buy the dip!)

#### 2. Crisis Opportunistic

Increases equity exposure as crisis deepens (buy when others are fearful).

```python
from stocksimulator.regime import CrisisOpportunisticStrategy

strategy = CrisisOpportunisticStrategy(
    max_crisis_equity_pct=90.0  # Up to 90% stocks during deep crisis
)
```

#### 3. Adaptive All Weather

All-weather strategy that tilts based on regime.

```python
from stocksimulator.regime import AdaptiveAllWeatherStrategy

strategy = AdaptiveAllWeatherStrategy()
```

**Always maintains diversification:**
- Stocks: 20-40% (varies by regime)
- Bonds: 30-50%
- Alternatives: 10-20%
- Cash: 5-15%

### Custom Regime Strategy

```python
from stocksimulator.regime import create_custom_regime_strategy, MarketRegime

strategy = create_custom_regime_strategy(
    normal_allocation={
        'SP500': 70,
        'LONG_TREASURY': 30
    },
    crisis_allocation={
        'LONG_TREASURY': 60,
        'SHORT_BOND': 30,
        'MANAGED_FUTURES': 10
    },
    # Pre-crisis and recovery are auto-blended
    transition_days=20
)
```

### Pre-built Portfolios

```python
from stocksimulator.regime import DEFENSIVE_PORTFOLIOS, AGGRESSIVE_PORTFOLIOS

# Defensive options
ultra_defensive = DEFENSIVE_PORTFOLIOS['ultra_defensive']
# {'LONG_TREASURY': 60, 'SHORT_BOND': 30, 'MANAGED_FUTURES': 10}

defensive = DEFENSIVE_PORTFOLIOS['defensive']
# {'LONG_TREASURY': 50, 'SHORT_BOND': 20, 'CONSUMER_STAPLES': 20, 'SP500': 10}

# Aggressive options
aggressive = AGGRESSIVE_PORTFOLIOS['aggressive']
# {'SP500': 70, 'SP500_2X': 20, 'SHORT_BOND': 10}

ultra_aggressive = AGGRESSIVE_PORTFOLIOS['ultra_aggressive']
# {'SP500': 60, 'SP500_2X': 30, 'WORLD_2X': 10}
```

---

## Crisis Rebalancing

### The "Buy the Dip" Problem

**Challenge**: You want to shift from defensive to aggressive during a crisis, but:
- You can't time the bottom perfectly
- Buying too early = more pain
- Buying too late = missed recovery
- All-at-once is risky

**Solution**: Gradual, rules-based rebalancing

### Rebalancing Strategies

#### 1. Linear (Time-Based)

Transitions at constant rate over time.

```python
from stocksimulator.regime import CrisisRebalancer, RebalancingStrategy

rebalancer = CrisisRebalancer(
    defensive_portfolio={'LONG_TREASURY': 70, 'SHORT_BOND': 30},
    aggressive_portfolio={'SP500': 80, 'WORLD': 20},
    strategy=RebalancingStrategy.LINEAR,
    rebalance_frequency_days=7
)
```

**When to use**: Fixed timeline (e.g., transition over 6 months)

#### 2. Drawdown-Triggered

Buys more as market falls deeper.

```python
rebalancer = CrisisRebalancer(
    defensive_portfolio={'LONG_TREASURY': 70, 'SHORT_BOND': 30},
    aggressive_portfolio={'SP500': 80, 'WORLD': 20},
    strategy=RebalancingStrategy.DRAWDOWN_TRIGGERED
)
```

**Logic**:
- -10% drawdown → 2% shift per rebalance
- -20% drawdown → 5% shift per rebalance
- -30% drawdown → 8% shift per rebalance
- -40%+ drawdown → 12% shift per rebalance (aggressive!)

**When to use**: "Buy the dip" - more aggressive at lower prices

#### 3. Volatility-Adjusted

Slows down when volatility spikes.

```python
rebalancer = CrisisRebalancer(
    defensive_portfolio={'LONG_TREASURY': 70, 'SHORT_BOND': 30},
    aggressive_portfolio={'SP500': 80, 'WORLD': 20},
    strategy=RebalancingStrategy.VOLATILITY_ADJUSTED
)
```

**Logic**:
- Low vol (< 20%) → 10% shift per rebalance
- Normal vol (20-30%) → 6% shift
- High vol (30-40%) → 4% shift
- Extreme vol (> 40%) → 2% shift (slow down!)

**When to use**: Risk-averse, avoid buying during panic

#### 4. Recovery-Based

Accelerates when recovery signals appear.

```python
rebalancer = CrisisRebalancer(
    defensive_portfolio={'LONG_TREASURY': 70, 'SHORT_BOND': 30},
    aggressive_portfolio={'SP500': 80, 'WORLD': 20},
    strategy=RebalancingStrategy.RECOVERY_BASED
)
```

**Logic**:
- Drawdown improving → 10% shift
- Drawdown stable → 6% shift
- Drawdown worsening → 3% shift

**When to use**: Wait for confirmation before going aggressive

### Creating Transition Schedule

```python
# Get S&P 500 data for 2008 crisis
sp500 = loader.load_asset('SP500')

# Create rebalancing schedule
schedule = rebalancer.create_transition_schedule(
    crisis_start_date=date(2008, 10, 1),
    crisis_end_date=date(2009, 3, 31),
    market_data=sp500
)

print(f"Rebalancing {len(schedule.dates)} times")

# View schedule
for date, allocation, reason in zip(schedule.dates,
                                     schedule.allocations,
                                     schedule.rationale):
    print(f"{date}: {allocation} - {reason}")
```

### Backtesting Transition

```python
# Load asset prices
assets = loader.load_multiple(['SP500', 'LONG_TREASURY', 'SHORT_BOND'])

# Backtest the schedule
result = rebalancer.backtest_transition(
    schedule=schedule,
    asset_prices=assets,
    initial_capital=100000
)

print(f"Total Return: {result.total_return:.2f}%")
print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
print(f"Max Drawdown: {result.max_drawdown:.2f}%")
print(f"Rebalances: {result.num_rebalances}")
print(f"Transaction Costs: ${result.total_transaction_costs:.2f}")
```

### Comparing Strategies

```python
from stocksimulator.regime import compare_rebalancing_strategies

comparison = compare_rebalancing_strategies(
    defensive_portfolio={'LONG_TREASURY': 70, 'SHORT_BOND': 30},
    aggressive_portfolio={'SP500': 80, 'WORLD': 20},
    crisis_start=date(2008, 10, 1),
    crisis_end=date(2009, 3, 31),
    market_data=sp500,
    asset_prices=assets
)

print(comparison.sort_values('total_return', ascending=False))
```

---

## Portfolio Comparison

### Comparing Multiple Portfolios

```python
from stocksimulator.regime import PortfolioComparator, create_comparison_report

# Define portfolios to test
portfolios = {
    '60/40 Balanced': lambda cd, hd, p, cp: {'SP500': 60, 'LONG_TREASURY': 40},

    '100% Stocks': lambda cd, hd, p, cp: {'SP500': 100},

    'All Weather': lambda cd, hd, p, cp: {
        'SP500': 30, 'LONG_TREASURY': 40, 'CONSUMER_STAPLES': 15,
        'MANAGED_FUTURES': 10, 'SHORT_BOND': 5
    },

    'Regime Aware': DefensiveToAggressiveStrategy()
}

# Load data
market_data = loader.load_multiple(
    ['SP500', 'LONG_TREASURY', 'SHORT_BOND', 'CONSUMER_STAPLES', 'MANAGED_FUTURES'],
    start_date=date(2007, 10, 1),
    end_date=date(2009, 3, 31)
)

# Compare
comparator = PortfolioComparator(initial_cash=100000)
results = comparator.compare_portfolios(portfolios, market_data)

# Generate report
report = create_comparison_report(results)
print(report)

# Save report
create_comparison_report(results, 'portfolio_comparison.txt')
```

### Regime-by-Regime Analysis

```python
# Compare performance by regime
regime_comparison = comparator.compare_by_regime(results)

# View returns by regime
print("Annualized Returns by Regime:")
print(regime_comparison['returns'])

# View Sharpe ratios by regime
print("\nSharpe Ratios by Regime:")
print(regime_comparison['sharpe_ratios'])

# View max drawdowns by regime
print("\nMax Drawdowns by Regime:")
print(regime_comparison['max_drawdowns'])
```

### Ranking Portfolios

```python
# Best Sharpe ratio overall
sharpe_ranking = comparator.rank_portfolios(
    results,
    metric='sharpe_ratio'
)
print("Best Sharpe Ratios:")
print(sharpe_ranking)

# Best performance in crisis
from stocksimulator.regime import MarketRegime

crisis_ranking = comparator.rank_portfolios(
    results,
    metric='annualized_return',
    regime=MarketRegime.CRISIS
)
print("\nBest in Crisis:")
print(crisis_ranking)

# Lowest drawdown in crisis
crisis_dd_ranking = comparator.rank_portfolios(
    results,
    metric='max_drawdown',
    regime=MarketRegime.CRISIS
)
print("\nLowest Drawdown in Crisis:")
print(crisis_dd_ranking)
```

---

## Complete Examples

### Example 1: Test on 2008 Financial Crisis

```python
from datetime import date
from stocksimulator.data import MultiAssetDataLoader
from stocksimulator.regime import (
    DefensiveToAggressiveStrategy,
    PortfolioComparator,
    create_comparison_report
)

# Load data
loader = MultiAssetDataLoader()
market_data = loader.load_multiple(
    ['SP500', 'LONG_TREASURY', 'SHORT_BOND', 'MANAGED_FUTURES'],
    start_date=date(2007, 10, 1),
    end_date=date(2009, 3, 31)
)

# Define strategies
portfolios = {
    '60/40': lambda cd, hd, p, cp: {'SP500': 60, 'LONG_TREASURY': 40},
    'Crisis Aware': DefensiveToAggressiveStrategy()
}

# Compare
comparator = PortfolioComparator()
results = comparator.compare_portfolios(portfolios, market_data)

# Report
print(create_comparison_report(results))
```

### Example 2: Custom Crisis Rebalancer

```python
from stocksimulator.regime import CrisisRebalancer, RebalancingStrategy

# Define portfolios
defensive = {'LONG_TREASURY': 60, 'SHORT_BOND': 30, 'MANAGED_FUTURES': 10}
aggressive = {'SP500': 70, 'SP500_2X': 20, 'SHORT_BOND': 10}

# Create rebalancer
rebalancer = CrisisRebalancer(
    defensive_portfolio=defensive,
    aggressive_portfolio=aggressive,
    strategy=RebalancingStrategy.DRAWDOWN_TRIGGERED,
    max_single_shift_pct=10.0,  # Max 10% per rebalance
    rebalance_frequency_days=7   # Weekly
)

# Load data
sp500 = loader.load_asset('SP500')
assets = loader.load_multiple(['SP500', 'SP500_2X', 'LONG_TREASURY',
                                'SHORT_BOND', 'MANAGED_FUTURES'])

# Create schedule
schedule = rebalancer.create_transition_schedule(
    crisis_start_date=date(2008, 10, 1),
    crisis_end_date=date(2009, 3, 31),
    market_data=sp500
)

# Backtest
result = rebalancer.backtest_transition(schedule, assets)

print(f"Strategy: {result.strategy_name}")
print(f"Total Return: {result.total_return:.2f}%")
print(f"Sharpe: {result.sharpe_ratio:.2f}")
print(f"Max DD: {result.max_drawdown:.2f}%")
```

### Example 3: Multi-Crisis Testing

See `examples/regime_analysis/test_historical_crises.py` for a complete example that:
- Tests portfolios on 3 major crises (2000, 2008, 2020)
- Compares 7 different strategies
- Generates comprehensive reports
- Provides actionable insights

---

## API Reference

### Multi-Asset Data Loader

```python
class MultiAssetDataLoader:
    def load_asset(ticker: str, start_date: date, end_date: date) -> pd.DataFrame
    def load_multiple(tickers: List[str], ...) -> Dict[str, pd.DataFrame]

class AssetClassRegistry:
    @classmethod
    def get_available_assets() -> List[str]
    @classmethod
    def get_info(ticker: str) -> AssetClassInfo
```

### Regime Detection

```python
class MarketRegimeDetector:
    def detect_regimes(price_data: pd.DataFrame) -> pd.DataFrame
    def get_regime_periods(regime_data: pd.DataFrame) -> List[RegimeInfo]

class HistoricalCrisisDatabase:
    @classmethod
    def get_crisis_periods() -> List[Tuple[date, date, str]]
    @classmethod
    def is_crisis_period(check_date: date) -> Optional[str]
```

### Strategies

```python
class DefensiveToAggressiveStrategy:
    def __init__(defensive_assets, aggressive_assets, ...)
    def __call__(current_date, historical_data, portfolio, prices) -> Dict

class CrisisRebalancer:
    def create_transition_schedule(...) -> RebalancingSchedule
    def backtest_transition(...) -> TransitionResult
```

### Portfolio Comparison

```python
class PortfolioComparator:
    def compare_portfolios(...) -> Dict[str, PortfolioComparison]
    def compare_by_regime(...) -> pd.DataFrame
    def rank_portfolios(...) -> pd.DataFrame

def create_comparison_report(results, output_file=None) -> str
```

---

## Tips & Best Practices

### 1. Asset Selection

✅ **DO**:
- Use diversified assets (stocks, bonds, alternatives)
- Include defensive assets for crisis periods
- Test with and without leverage

❌ **DON'T**:
- Use only one asset class
- Ignore correlation during crisis
- Over-leverage without hedges

### 2. Regime Detection

✅ **DO**:
- Use multiple indicators (drawdown + volatility + trend)
- Validate against historical crises
- Account for regime transition periods

❌ **DON'T**:
- Rely solely on drawdown
- Ignore pre-crisis warnings
- React too quickly to noise

### 3. Rebalancing

✅ **DO**:
- Rebalance more frequently during crisis
- Limit maximum shift per rebalance
- Account for transaction costs
- Use multiple strategies for robustness

❌ **DON'T**:
- Try to time the exact bottom
- Make all-or-nothing shifts
- Ignore volatility when rebalancing
- Forget about transaction costs

### 4. Backtesting

✅ **DO**:
- Test on multiple historical crises
- Compare regime-aware vs static portfolios
- Check both normal and crisis performance
- Validate with out-of-sample data

❌ **DON'T**:
- Over-optimize to one crisis
- Ignore survivorship bias
- Assume past crises predict future
- Cherry-pick test periods

---

## Troubleshooting

### Q: Not enough data for asset X

**A**: Some assets are simulated. Adjust date range or use different assets.

```python
# Check available date range
df = loader.load_asset('MANAGED_FUTURES')
print(f"Available: {df['Date'].min()} to {df['Date'].max()}")
```

### Q: Regime detector not finding crisis

**A**: Adjust threshold parameters.

```python
detector = MarketRegimeDetector(
    crisis_drawdown_threshold=-0.10,  # Lower threshold (10% = crisis)
    pre_crisis_vol_multiplier=1.3     # More sensitive
)
```

### Q: Portfolio comparison failing

**A**: Ensure all assets have aligned dates.

```python
market_data = loader.load_multiple(
    tickers=['SP500', 'LONG_TREASURY'],
    align_dates=True  # Critical!
)
```

### Q: Leverage costs seem high

**A**: This is realistic! Leveraged ETFs have ~1.5% annual excess costs (from Phase 1 research).

---

## Next Steps

1. **Run the example**: `python examples/regime_analysis/test_historical_crises.py`
2. **Customize portfolios**: Modify allocations for your risk profile
3. **Test your own crises**: Add more historical periods
4. **Optimize parameters**: Find best rebalancing strategy for your needs
5. **Combine with Phase 3**: Use HRP, shrinkage, multi-period optimization

---

## References

- **Phase 1**: Modular costs, discrete allocation
- **Phase 2**: Constraints, causality enforcement
- **Phase 3**: HRP, shrinkage, multi-period optimization, Monte Carlo
- **Regime Analysis**: This guide

**Full Documentation**: See `docs/` directory

**Support**: Create issue at https://github.com/Jonathangadeaharder/StockSimulator/issues

---

*Happy regime-aware investing! 🚀*
