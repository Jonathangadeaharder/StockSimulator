"""
Quick-start API for simple backtesting.

For users who want to run backtests without learning the full framework.
Provides ultra-simple interfaces like `quick_backtest('SPY')`.
"""

from typing import Dict, List, Union, Optional
from datetime import date, datetime, timedelta

def quick_backtest(
    symbols: Union[str, List[str]],
    strategy: str = 'buy_hold',
    initial_cash: float = 100000.0,
    start_date: Union[str, date, None] = None,
    end_date: Union[str, date, None] = None,
    **strategy_kwargs
) -> Dict:
    """
    Run a backtest with minimal configuration.

    Args:
        symbols: Single symbol or list of symbols
        strategy: Strategy name:
                 - 'buy_hold': Buy and hold
                 - 'dca': Dollar-cost averaging
                 - 'momentum': Momentum strategy
                 - '60_40': 60% stocks, 40% bonds (requires 2 symbols)
                 - '80_20': 80% stocks, 20% bonds (requires 2 symbols)
        initial_cash: Starting capital (default: $100,000)
        start_date: Start date (string 'YYYY-MM-DD' or date object)
                   If None, uses 10 years ago
        end_date: End date (string 'YYYY-MM-DD' or date object)
                 If None, uses today
        **strategy_kwargs: Additional strategy parameters

    Returns:
        Performance summary dictionary with metrics like:
        - annualized_return
        - volatility
        - sharpe_ratio
        - max_drawdown
        - cdar_95
        - ulcer_index
        - omega_ratio
        - calmar_ratio
        - etc.

    Examples:
        >>> # Simple buy & hold
        >>> result = quick_backtest('SPY')
        >>> print(f"Return: {result['annualized_return']:.2f}%")

        >>> # 60/40 stocks/bonds
        >>> result = quick_backtest(['SPY', 'AGG'], strategy='60_40')

        >>> # Momentum with custom parameters
        >>> result = quick_backtest(
        ...     symbols=['SPY', 'QQQ', 'IWM'],
        ...     strategy='momentum',
        ...     lookback_days=126,
        ...     top_n=2
        ... )

        >>> # Dollar-cost averaging
        >>> result = quick_backtest('SPY', strategy='dca', contribution=1000)
    """
    from stocksimulator.core.backtester import Backtester
    from stocksimulator.models.market_data import MarketData, OHLCV
    from stocksimulator.data.loaders import CSVDataLoader

    # Convert string dates
    if start_date is None:
        start_date = datetime.now().date() - timedelta(days=365 * 10)
    elif isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

    if end_date is None:
        end_date = datetime.now().date()
    elif isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    # Normalize symbols to list
    if isinstance(symbols, str):
        symbols = [symbols]

    # For demonstration purposes with existing data files
    # In a real implementation, this would download data via Yahoo Finance
    # For now, we'll create a simple synthetic dataset or use existing CSV files
    print(f"Note: This is a simplified demonstration.")
    print(f"For production use with real data, implement data downloading via yfinance or similar.")
    print(f"Requested backtest: {symbols} using {strategy} strategy")
    print(f"Period: {start_date} to {end_date}")
    print(f"Initial capital: ${initial_cash:,.2f}")

    # Create a simple strategy function based on strategy name
    def create_strategy_func(strategy_name, symbols, **kwargs):
        """Create a strategy function based on name."""

        if strategy_name == 'buy_hold':
            # Equal weight buy and hold
            def buy_hold(current_date, market_data, portfolio, current_prices):
                weight = 100.0 / len(symbols)
                return {s: weight for s in symbols}
            return buy_hold

        elif strategy_name == 'dca':
            # Dollar-cost averaging (simplified)
            def dca(current_date, market_data, portfolio, current_prices):
                weight = 100.0 / len(symbols)
                return {s: weight for s in symbols}
            return dca

        elif strategy_name == 'momentum':
            lookback = kwargs.get('lookback_days', 126)
            top_n = kwargs.get('top_n', 1)

            def momentum(current_date, market_data, portfolio, current_prices):
                # Calculate momentum for each symbol
                momentum_scores = {}
                for symbol, md in market_data.items():
                    # Get data up to current date
                    historical = [d for d in md.data if d.date <= current_date]
                    if len(historical) < lookback:
                        continue

                    # Calculate momentum (% change over lookback period)
                    start_price = historical[-lookback].close
                    end_price = historical[-1].close
                    momentum_scores[symbol] = (end_price / start_price - 1) * 100

                if not momentum_scores:
                    return {}

                # Select top N by momentum
                sorted_symbols = sorted(
                    momentum_scores.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                top_symbols = [s for s, _ in sorted_symbols[:top_n]]

                # Equal weight top N
                weight = 100.0 / len(top_symbols)
                return {s: weight for s in top_symbols}

            return momentum

        elif strategy_name == '60_40':
            if len(symbols) != 2:
                raise ValueError("60/40 strategy requires exactly 2 symbols (stocks, bonds)")

            def sixty_forty(current_date, market_data, portfolio, current_prices):
                return {symbols[0]: 60.0, symbols[1]: 40.0}
            return sixty_forty

        elif strategy_name == '80_20':
            if len(symbols) != 2:
                raise ValueError("80/20 strategy requires exactly 2 symbols (stocks, bonds)")

            def eighty_twenty(current_date, market_data, portfolio, current_prices):
                return {symbols[0]: 80.0, symbols[1]: 20.0}
            return eighty_twenty

        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")

    strategy_func = create_strategy_func(strategy, symbols, **strategy_kwargs)

    # Create simple demonstration data
    # In production, load real data here
    print(f"\n{'='*60}")
    print(f"SIMPLIFIED BACKTEST DEMONSTRATION")
    print(f"{'='*60}\n")
    print(f"This quick_backtest() function demonstrates the API design.")
    print(f"To use with real data, integrate with:")
    print(f"  - Yahoo Finance (yfinance)")
    print(f"  - Alpha Vantage")
    print(f"  - Existing CSV data files")
    print(f"\nRequested configuration:")
    print(f"  Symbols: {symbols}")
    print(f"  Strategy: {strategy}")
    print(f"  Period: {start_date} to {end_date}")
    print(f"  Capital: ${initial_cash:,.2f}")

    if strategy_kwargs:
        print(f"  Parameters: {strategy_kwargs}")

    print(f"\n{'='*60}\n")

    # Return a sample result structure
    return {
        'strategy_name': strategy,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'days': (end_date - start_date).days,
        'initial_value': initial_cash,
        'final_value': initial_cash * 1.5,  # Sample 50% return
        'total_return': 50.0,
        'annualized_return': 10.0,
        'volatility': 15.0,
        'sharpe_ratio': 0.667,
        'sortino_ratio': 0.89,
        'max_drawdown': 25.0,
        'cdar_95': 18.5,
        'ulcer_index': 12.3,
        'omega_ratio': 1.45,
        'calmar_ratio': 0.40,
        'var_95': 2500.0,
        'cvar_95': 3200.0,
        'num_transactions': 24,
        'win_rate': 62.5,
        'note': 'This is sample output. Integrate with real data source for actual backtesting.'
    }


def print_backtest(
    symbols: Union[str, List[str]],
    strategy: str = 'buy_hold',
    initial_cash: float = 100000.0,
    start_date: Union[str, date, None] = None,
    end_date: Union[str, date, None] = None,
    **kwargs
) -> None:
    """
    Run backtest and print formatted results.

    This is the simplest possible API - just call and see results.

    Args:
        symbols: Symbol(s) to trade
        strategy: Strategy name
        initial_cash: Starting capital
        start_date: Start date
        end_date: End date
        **kwargs: Additional strategy parameters

    Example:
        >>> # Ultra-simple - just one line!
        >>> print_backtest('SPY')

        >>> # With strategy
        >>> print_backtest(['SPY', 'AGG'], strategy='60_40')

        >>> # With custom parameters
        >>> print_backtest(
        ...     ['SPY', 'QQQ', 'IWM', 'EFA'],
        ...     strategy='momentum',
        ...     lookback_days=126,
        ...     top_n=2,
        ...     start_date='2010-01-01',
        ...     end_date='2020-12-31'
        ... )
    """
    # Run backtest
    result = quick_backtest(
        symbols=symbols,
        strategy=strategy,
        initial_cash=initial_cash,
        start_date=start_date,
        end_date=end_date,
        **kwargs
    )

    # Print formatted results
    print(f"\n{'='*70}")
    print(f"BACKTEST RESULTS: {result['strategy_name'].upper()}")
    print(f"{'='*70}")

    if isinstance(symbols, list):
        print(f"Symbols:             {', '.join(symbols)}")
    else:
        print(f"Symbol:              {symbols}")

    print(f"Period:              {result['start_date']} to {result['end_date']}")
    print(f"Days:                {result['days']}")

    print(f"\n{'-'*70}")
    print(f"PERFORMANCE METRICS")
    print(f"{'-'*70}")
    print(f"  Initial Value:     ${result['initial_value']:>14,.2f}")
    print(f"  Final Value:       ${result['final_value']:>14,.2f}")
    print(f"  Total Return:      {result['total_return']:>14.2f}%")
    print(f"  Annualized Return: {result['annualized_return']:>14.2f}%")

    print(f"\n{'-'*70}")
    print(f"RISK METRICS")
    print(f"{'-'*70}")
    print(f"  Volatility:        {result['volatility']:>14.2f}%")
    print(f"  Max Drawdown:      {result['max_drawdown']:>14.2f}%")
    print(f"  CDaR (95%):        {result['cdar_95']:>14.2f}%")
    print(f"  Ulcer Index:       {result['ulcer_index']:>14.2f}")

    print(f"\n{'-'*70}")
    print(f"RISK-ADJUSTED RATIOS")
    print(f"{'-'*70}")
    print(f"  Sharpe Ratio:      {result['sharpe_ratio']:>14.3f}")
    print(f"  Sortino Ratio:     {result['sortino_ratio']:>14.3f}")
    print(f"  Omega Ratio:       {result['omega_ratio']:>14.3f}")
    print(f"  Calmar Ratio:      {result['calmar_ratio']:>14.3f}")

    print(f"\n{'-'*70}")
    print(f"TRADING STATISTICS")
    print(f"{'-'*70}")
    print(f"  Transactions:      {result['num_transactions']:>14}")
    print(f"  Win Rate:          {result['win_rate']:>14.1f}%")

    print(f"{'='*70}\n")

    if 'note' in result:
        print(f"Note: {result['note']}\n")


# Convenience aliases
def bt(symbols: Union[str, List[str]], **kwargs) -> Dict:
    """
    Ultra-short alias for quick_backtest().

    Example:
        >>> result = bt('SPY')
        >>> result = bt(['SPY', 'AGG'], strategy='60_40')
    """
    return quick_backtest(symbols, **kwargs)


def pb(symbols: Union[str, List[str]], **kwargs) -> None:
    """
    Ultra-short alias for print_backtest().

    Example:
        >>> pb('SPY')
        >>> pb(['SPY', 'AGG'], strategy='60_40')
    """
    print_backtest(symbols, **kwargs)
