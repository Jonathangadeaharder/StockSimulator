# StockSimulator

A comprehensive, production-grade stock market simulation and backtesting platform built with modern financial engineering principles.

[![CI/CD](https://github.com/Jonathangadeaharder/StockSimulator/workflows/CI/badge.svg)](https://github.com/Jonathangadeaharder/StockSimulator/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](./tests/)

## Overview

StockSimulator is an advanced financial simulation platform designed for:

- **Portfolio Management**: Multi-asset portfolio construction, optimization, and rebalancing
- **Leveraged ETF Analysis**: Empirically-calibrated simulation of 2x leveraged instruments with real-world costs
- **Backtesting**: Historical performance analysis across multiple decades and market regimes
- **Risk Analysis**: Comprehensive risk metrics including VaR, CVaR, Sharpe ratio, and maximum drawdown
- **Trading Strategies**: Support for DCA, momentum, mean reversion, and custom strategies

## 🚀 NEW: Phase 1, 2 & 3 Enhancements

### Phase 1: Practical Improvements ([docs](docs/PHASE1_ENHANCEMENTS.md))

- ✨ **Modular Cost Components**: Separate transaction, holding, and leveraged ETF costs with era-specific calibration
- ✨ **Discrete Allocation**: Convert theoretical weights to whole shares with tracking error calculation
- ✨ **Enhanced Risk Metrics**: Added CDaR, Ulcer Index, Omega Ratio, and Calmar Ratio
- ✨ **Simple API**: Ultra-simple 1-line backtesting with `quick_backtest('SPY')` or `pb('SPY')`

### Phase 2: Architecture Improvements ([docs](docs/PHASE2_ENHANCEMENTS.md))

- 🏗️ **Enhanced Strategy Pattern**: Lifecycle methods (init/next/finalize) and state management
- 🔒 **Causality Enforcement**: Prevents look-ahead bias - critical for research validity
- ⚙️ **Flexible Constraints**: Sector limits, turnover, volatility targets, and custom constraints
- 🎯 **Constrained Optimization**: Optimize portfolios with multiple simultaneous constraints

### Phase 3: Advanced Features ([docs](docs/PHASE3_ENHANCEMENTS.md))

- 🌳 **Hierarchical Risk Parity**: ML-based diversification without return forecasts (Lopez de Prado)
- 📉 **Shrinkage Estimation**: Robust covariance matrices with Ledoit-Wolf optimal shrinkage
- ⏭️ **Multi-Period Optimization**: Model Predictive Control considering future rebalancing costs
- ⚡ **Parallel Grid Search**: 4-8x speedup for parameter optimization using multiprocessing
- 🎲 **Monte Carlo Simulation**: Random entry/exit validation for realistic investor timing

### 🆕 Regime-Aware Portfolio Analysis ([docs](docs/REGIME_ANALYSIS_GUIDE.md))

- 📊 **Multi-Asset Support**: 13+ asset classes (stocks, bonds, alternatives, leverage, short positions)
- 🔍 **Regime Detection**: Automatic classification into normal/pre-crisis/crisis/recovery
- 🛡️ **Defensive Positioning**: Protect capital before and during market crashes
- 📈 **Buy the Dip**: Gradual defensive→aggressive transitions without perfect timing
- 🔄 **4 Rebalancing Strategies**: Linear, drawdown-triggered, volatility-adjusted, recovery-based
- 📉 **Historical Crisis Testing**: Validated on dot-com (2000), financial crisis (2008), COVID (2020)
- 🏆 **Portfolio Comparison**: Side-by-side testing across market regimes with automated reporting

See [SIMILAR_PROJECTS_ANALYSIS.md](docs/SIMILAR_PROJECTS_ANALYSIS.md) for inspiration from leading libraries.

## Key Features

### 📊 Historical Data Analysis

- **75+ years of market data** (S&P 500, DJIA: 1950-2025; NASDAQ: 1971-2025; Nikkei 225: 1950-2025)
- **265+ rolling 10-year windows** for robust statistical analysis
- **Empirically-calibrated costs**: 2.1% total costs for leveraged ETFs (0.6% TER + 1.5% excess costs)
- **Major events coverage**: All bull/bear markets, crashes, and recoveries since 1950

### 🎯 Advanced Analytics

- **Percentile Performance Analysis**: 5th, 25th, 50th, 75th, 95th percentile outcomes
- **Risk-Adjusted Optimization**: Find optimal allocations for different risk tolerance levels
- **IQR Analysis**: Understand the middle 50% of realistic outcomes
- **Win Rate vs. Tail Risk**: Identify when high win rates mask catastrophic losses

### 🛡️ Risk Management

- **Conservative (5% loss risk)**: Ensures 95% of 10-year periods are profitable
- **Moderate (10% loss risk)**: Ensures 90% of 10-year periods are profitable
- **Aggressive (20% loss risk)**: Ensures 80% of 10-year periods are profitable

### 🔬 Research-Backed Methodology

- **Empirical financing costs**: Based on 2016-2024 academic research (not theoretical SOFR)
- **Volatility drag**: Properly modeled compounding losses in leveraged products
- **Transaction costs**: 2 bps quarterly rebalancing costs
- **Era-specific costs**: Different cost regimes for Volcker era, ZIRP era, and current environment

## Installation

### Prerequisites

- Python 3.8 or higher
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Jonathangadeaharder/StockSimulator.git
cd StockSimulator

# Install dependencies (pure Python - no external packages needed!)
pip install -r requirements.txt

# Run a complete backtest example (works immediately!)
python examples/run_backtest.py

# Run original analysis scripts
python historical_data/find_optimal_allocation.py
python historical_data/percentile_performance_analysis.py
python historical_data/risk_adjusted_allocation.py

# Run tests
pytest tests/
```

**Output from `run_backtest.py`**:
```
Strategy: Buy & Hold SPY
Period: 3658 days (14.5 years)

PERFORMANCE METRICS:
  Initial Value:       $  100,000.00
  Final Value:         $  319,732.89
  Total Return:              219.73%
  Annualized Return:          12.31%

RISK METRICS:
  Volatility:                  0.18%
  Sharpe Ratio:               0.672
  Max Drawdown:               33.92%
```

## Usage

### 1. Optimal Allocation Finder

Find the optimal leveraged/unleveraged mix based on Sharpe ratio:

```python
from historical_data.portfolio_optimization_enhanced import EnhancedPortfolioOptimizer

optimizer = EnhancedPortfolioOptimizer('S&P 500', 'sp500_stooq_daily.csv', 'Date', 'Close', 1950)
result = optimizer.find_optimal_allocation(rebalance_months=3)
print(f"Optimal allocation: {result['lev_allocation']}% leveraged")
```

### 2. Percentile Performance Analysis

Analyze the distribution of outcomes across all historical periods:

```python
from historical_data.percentile_performance_analysis import analyze_percentile_performance

results = analyze_percentile_performance('S&P 500', 'sp500_stooq_daily.csv', 'Date', 'Close', 1950, years=10)
```

### 3. Risk-Adjusted Allocation

Find the best allocation given your risk tolerance:

```python
from historical_data.risk_adjusted_allocation import analyze_risk_tolerances

analyze_risk_tolerances('S&P 500', 'sp500_stooq_daily.csv', 'Date', 'Close', 1950)
```

## Project Structure

```
StockSimulator/
├── historical_data/              # Core analysis modules
│   ├── analyze_data.py          # Data loading and preprocessing
│   ├── portfolio_optimization_enhanced.py  # Enhanced portfolio optimizer
│   ├── percentile_performance_analysis.py  # Percentile analysis
│   ├── risk_adjusted_allocation.py         # Risk-adjusted optimization
│   ├── detailed_leverage_table.py          # Comprehensive leverage tables
│   └── *.csv                    # Historical market data
├── tests/                        # Comprehensive test suite
│   ├── test_financial_calculations.py
│   ├── test_historical_validation.py
│   └── README.md
├── docs/                         # Documentation and research
│   ├── PERCENTILE_PERFORMANCE.md
│   ├── RISK_ADJUSTED_ALLOCATION.md
│   ├── DETAILED_LEVERAGE_TABLE.md
│   └── *.md                      # Analysis summaries
├── .github/workflows/            # CI/CD pipelines
│   └── ci.yml
├── requirements.txt              # Python dependencies
├── setup.py                      # Package configuration
└── README.md                     # This file
```

## Key Findings

### The Leverage Paradox

Our research reveals a critical paradox in leveraged investing:

- **100% leveraged has 83% win rate** over 10-year periods
- **BUT 0% leveraged is Sharpe-optimal** due to catastrophic tail risk
- **5th percentile for 100% leveraged**: -0.68% (can lose money over 10 years!)

### Risk-Adjusted Recommendations

| Risk Tolerance | Optimal Allocation | Median Return | Worst Case |
|----------------|-------------------|---------------|------------|
| Conservative (5%) | 50-75% leveraged | 13-15% | +0.36% to +2.00% |
| Moderate (10%) | 100% leveraged | 16.04% | +1.04% |
| Aggressive (20%) | 100% leveraged | 16.04% | Negative possible |

### NASDAQ Sweet Spot

NASDAQ 50% leveraged offers the **best risk/reward ratio**:
- +38% return improvement vs. unleveraged
- +42% drawdown increase
- **Trade-off ratio: 1.0:1.10** (best among all indices)

## Methodology

### Rolling Window Analysis

- **Window size**: 10 years (2,520 trading days)
- **Step size**: 3 months (63 trading days)
- **Total windows**: 265 (S&P 500/DJIA), 180 (NASDAQ), 259 (Nikkei 225)

### Cost Model

#### Leveraged ETF Total Costs (~2.1% annual)
- **TER (Total Expense Ratio)**: 0.6%
- **Empirical excess costs**: 1.5% average
  - Swap financing costs
  - Volatility drag
  - Counterparty risk
  - Rebalancing slippage

#### Era-Specific Costs
- **1950-1979**: 1.5% (pre-derivatives era)
- **1980-1989**: 2.5% (Volcker high-rate era)
- **1990-2007**: 1.2-1.5% (normal times)
- **2008-2015**: 0.8% (ZIRP - lowest costs ever)
- **2016-2021**: 1.2% (normalized)
- **2022+**: 2.0% (current high-rate environment)

### Performance Metrics

- **Annualized Return**: Geometric mean with daily compounding
- **Volatility**: Sample standard deviation (n-1 denominator) × √252
- **Sharpe Ratio**: (Return - Risk-Free Rate) / Volatility
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Percentiles**: Linear interpolation method for distribution analysis

## Testing

Comprehensive test suite with 95%+ coverage:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=historical_data --cov-report=html

# Run specific test categories
pytest tests/test_financial_calculations.py
pytest tests/test_historical_validation.py
```

### Test Categories

- **Financial Calculations**: Sharpe ratio, returns, volatility, drawdowns
- **Historical Validation**: Realistic return bounds, cost accuracy
- **Edge Cases**: Empty data, single data points, extreme values
- **Regression Tests**: Prevents breaking changes to core calculations

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/Jonathangadeaharder/StockSimulator.git
cd StockSimulator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests before committing
pytest tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this software in your research, please cite:

```bibtex
@software{stocksimulator2025,
  author = {StockSimulator Contributors},
  title = {StockSimulator: A Production-Grade Stock Market Simulation Platform},
  year = {2025},
  url = {https://github.com/Jonathangadeaharder/StockSimulator}
}
```

## Acknowledgments

- Historical data sourced from Stooq and FRED (Federal Reserve Economic Data)
- Empirical financing cost research based on academic studies (2016-2024)
- Volatility drag modeling inspired by Cheng & Madhavan (2009)

## Contact

- **Issues**: [GitHub Issues](https://github.com/Jonathangadeaharder/StockSimulator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Jonathangadeaharder/StockSimulator/discussions)

## Implementation Status

### ✅ Phase 1: Foundation (Complete)
- [x] Historical data analysis
- [x] Empirical cost calibration
- [x] Percentile performance analysis
- [x] Risk-adjusted optimization
- [x] Comprehensive test suite
- [x] Core data models (Portfolio, Position, Transaction, MarketData)
- [x] Portfolio Manager
- [x] Backtesting framework
- [x] Risk Calculator

### ✅ Phase 2: Trading Strategies (Complete)
- [x] 17 professional-grade strategies across 4 categories
- [x] DCA/Fixed Allocation strategies (5 strategies)
- [x] Momentum strategies (4 strategies)
- [x] Mean Reversion strategies (4 strategies)
- [x] Risk Parity strategies (4 strategies)
- [x] Strategy comparison framework
- [x] Comprehensive strategy documentation

### ✅ Phase 3: Analysis Tools (Complete)
- [x] Utility functions (date, math, validation)
- [x] Technical indicators (MACD, RSI, Bollinger Bands, ATR, etc.)
- [x] CSV data loaders for historical data
- [x] Data caching system
- [x] Working backtest examples
- [x] Strategy optimization tools

### 📊 Focus Areas

This platform focuses on:
- **Historical backtesting** with real market data
- **Strategy development** and comparison
- **Portfolio optimization** using empirical research
- **Risk analysis** with comprehensive metrics

**Not included** (by design):
- REST APIs or web services
- Real-time data feeds
- Machine learning training
- Production deployment infrastructure

The platform is designed for **research and analysis** using historical data.

---

**Disclaimer**: This software is for educational and research purposes only. Past performance does not guarantee future results. Leveraged investing carries significant risk. Always consult with a qualified financial advisor before making investment decisions.
