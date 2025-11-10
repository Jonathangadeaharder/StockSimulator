# StockSimulator Architecture

This document describes the architecture and design principles of the StockSimulator platform.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Core Modules](#core-modules)
- [Data Models](#data-models)
- [Design Principles](#design-principles)
- [Data Flow](#data-flow)
- [Extension Points](#extension-points)

## Overview

StockSimulator is designed as a modular, extensible platform for stock market simulation and backtesting. The architecture follows SOLID principles and emphasizes:

- **Separation of Concerns**: Clear boundaries between data, business logic, and presentation
- **Pure Python**: No external dependencies for core functionality
- **Testability**: All components designed for easy unit testing
- **Extensibility**: Plugin architecture for strategies and data sources

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Application Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   CLI Tools  │  │  REST API    │  │   WebUI      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Core Layer                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ Portfolio        │  │   Backtester     │  │     Risk     │  │
│  │ Manager          │  │                  │  │  Calculator  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Data Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Portfolio   │  │   Position   │  │ Transaction  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐                                               │
│  │ MarketData   │                                               │
│  └──────────────┘                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Data Sources                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  CSV Files   │  │    APIs      │  │  Databases   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Core Modules

### Portfolio Manager

**Purpose**: High-level portfolio operations and management

**Responsibilities**:
- Create and track multiple portfolios
- Execute trades with transaction cost modeling
- Rebalance portfolios to target allocations
- Calculate performance metrics

**Key Methods**:
```python
create_portfolio(portfolio_id, name, initial_cash)
execute_trade(portfolio_id, symbol, shares, price)
rebalance_portfolio(portfolio_id, target_allocation, current_prices)
get_portfolio_performance(portfolio_id, current_prices)
```

**Design Patterns**:
- **Repository Pattern**: Manages portfolio storage and retrieval
- **Factory Pattern**: Creates portfolio instances

### Backtester

**Purpose**: Historical simulation and strategy testing

**Responsibilities**:
- Run backtests on historical data
- Support multiple rebalancing frequencies
- Compare different strategies
- Generate performance reports

**Key Methods**:
```python
run_backtest(strategy_name, market_data, strategy_func)
compare_strategies(strategies, market_data)
```

**Design Patterns**:
- **Strategy Pattern**: Pluggable trading strategies
- **Template Method**: Backtest execution flow

### Risk Calculator

**Purpose**: Comprehensive risk metrics calculation

**Responsibilities**:
- Calculate volatility and returns
- Compute risk-adjusted metrics (Sharpe, Sortino)
- Analyze drawdowns
- Calculate VaR and CVaR

**Key Methods**:
```python
calculate_volatility(returns)
calculate_sharpe_ratio(returns, risk_free_rate)
calculate_max_drawdown(values)
calculate_var(returns, confidence_level)
```

**Design Patterns**:
- **Calculator Pattern**: Stateless calculations
- **Facade Pattern**: Simple interface to complex calculations

## Data Models

### Portfolio

**Attributes**:
- `portfolio_id`: Unique identifier
- `name`: Portfolio name
- `cash`: Available cash
- `positions`: Dictionary of symbol → Position
- `transactions`: List of all transactions
- `initial_value`: Starting value

**Invariants**:
- Cash is never negative (enforced by trade execution)
- Position shares accurately reflect all transactions
- Total value = cash + sum(position values)

### Position

**Attributes**:
- `symbol`: Ticker symbol
- `shares`: Number of shares (can be negative for short)
- `cost_basis`: Average cost per share
- `opened_at`: When position was opened
- `updated_at`: Last modification time

**Invariants**:
- Cost basis updated on share additions (not reductions)
- Shares = 0 when position is closed

### Transaction

**Attributes**:
- `transaction_id`: Unique identifier
- `portfolio_id`: Associated portfolio
- `symbol`: Security symbol
- `transaction_type`: BUY, SELL, DIVIDEND, etc.
- `shares`: Number of shares
- `price`: Price per share
- `transaction_cost`: Fees and costs
- `timestamp`: When transaction occurred

**Invariants**:
- Immutable once created (append-only)
- Net cash impact always calculated correctly

### MarketData

**Attributes**:
- `symbol`: Ticker symbol
- `data`: List of OHLCV data points
- `metadata`: Source and data quality info

**Methods**:
- `get_price_on_date(date)`: Price lookup
- `get_returns(period_days)`: Calculate returns
- `get_volatility(window_days)`: Rolling volatility
- `get_max_drawdown()`: Maximum drawdown

## Design Principles

### 1. Pure Python Core

**Rationale**: Maximum portability and reproducibility

- No external dependencies for core calculations
- Easy to understand and verify
- Runs anywhere Python runs
- No binary dependencies to break

### 2. Empirically-Calibrated Models

**Rationale**: Research-backed accuracy

- Leveraged ETF costs based on 2016-2024 research
- Era-specific cost models (Volcker, ZIRP, current)
- Proper volatility drag modeling
- Sample variance for unbiased estimates

### 3. Immutable Transactions

**Rationale**: Audit trail and reproducibility

- All transactions are append-only
- Portfolio state can be reconstructed from transactions
- Easy to debug and verify
- Supports time-travel debugging

### 4. Type Safety

**Rationale**: Catch errors early

- Type hints throughout
- Static analysis with mypy
- Self-documenting code
- Better IDE support

### 5. Testability

**Rationale**: Confidence in correctness

- All components unit-testable
- No global state
- Dependency injection where needed
- Integration tests for workflows

## Data Flow

### Trade Execution Flow

```
User Request
    │
    ▼
Backtester.execute_trade()
    │
    ├─► Validate (sufficient funds/shares)
    │
    ├─► Calculate costs
    │
    ├─► Create Transaction
    │
    ├─► Update Portfolio.cash
    │
    ├─► Update Portfolio.positions
    │
    └─► Return Transaction
```

### Backtest Flow

```
Backtester.run_backtest()
    │
    ├─► Load historical data
    │
    ├─► Initialize portfolio
    │
    └─► For each date:
        │
        ├─► Get current prices
        │
        ├─► Check rebalance trigger
        │
        ├─► If rebalance:
        │   │
        │   ├─► Call strategy_func()
        │   │
        │   ├─► Get target allocation
        │   │
        │   └─► Rebalance portfolio
        │
        ├─► Record portfolio value
        │
        └─► Continue to next date

    ▼
Return BacktestResult
    │
    ├─► Calculate metrics
    │
    └─► Generate report
```

### Risk Calculation Flow

```
RiskCalculator.calculate_comprehensive_metrics()
    │
    ├─► Calculate returns from values
    │
    ├─► Calculate volatility (annualized)
    │
    ├─► Calculate Sharpe ratio
    │
    ├─► Calculate Sortino ratio
    │
    ├─► Calculate max drawdown
    │
    ├─► Calculate VaR
    │
    ├─► Calculate CVaR
    │
    └─► If benchmark provided:
        │
        ├─► Calculate beta
        │
        └─► Calculate information ratio

    ▼
Return metrics dictionary
```

## Extension Points

### 1. Trading Strategies

Implement `strategy_func` with signature:

```python
def my_strategy(
    current_date: date,
    market_data: Dict[str, MarketData],
    portfolio: Portfolio,
    current_prices: Dict[str, float]
) -> Dict[str, float]:
    """
    Returns target allocation as dict of symbol -> percentage
    """
    # Your strategy logic here
    return {'SPY': 60.0, 'TLT': 40.0}
```

### 2. Data Sources

Implement data loader with signature:

```python
def load_market_data(
    symbol: str,
    start_date: date,
    end_date: date
) -> MarketData:
    """
    Load market data from your source
    """
    # Your data loading logic
    return MarketData(symbol=symbol, data=ohlcv_list)
```

### 3. Custom Risk Metrics

Extend `RiskCalculator`:

```python
class CustomRiskCalculator(RiskCalculator):
    def calculate_custom_metric(self, returns: List[float]) -> float:
        """Your custom risk metric"""
        # Implementation
        return metric_value
```

### 4. Portfolio Optimizers

Create optimizer functions:

```python
def custom_optimizer(
    symbols: List[str],
    market_data: Dict[str, MarketData],
    constraints: Dict
) -> Dict[str, float]:
    """
    Returns optimal allocation
    """
    # Your optimization logic
    return {symbol: weight for symbol, weight in allocations}
```

## Performance Considerations

### Memory

- **MarketData**: Store only needed date range
- **Portfolios**: Use generators for large transaction lists
- **Backtests**: Stream results instead of loading all in memory

### Speed

- **Pre-calculate**: Common metrics (volatility, returns)
- **Cache**: Expensive calculations (covariance matrices)
- **Vectorize**: Use list comprehensions instead of loops
- **Parallelize**: Run multiple backtests in parallel

### Accuracy

- **Floating Point**: Use Decimal for critical calculations if needed
- **Dates**: Always use date objects, never strings
- **Rounding**: Round only for display, never intermediate calculations

## Future Architecture

### Phase 2: API Layer

- REST API with FastAPI
- Authentication with JWT
- Rate limiting
- WebSocket for real-time updates

### Phase 3: Event-Driven

- Message queue (RabbitMQ/Redis)
- Event sourcing for portfolios
- CQRS pattern
- Time-series database (InfluxDB)

### Phase 4: Scalability

- Microservices architecture
- Kubernetes deployment
- Distributed caching (Redis)
- Load balancing

---

**Last Updated**: 2025-01-09
**Version**: 1.0.0
