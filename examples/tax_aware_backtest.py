# @structurelint:no-test
"""
Example: Tax-Aware Backtesting

Demonstrates how tax impact affects investment returns.
"""

import sys
import os
from datetime import date

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from stocksimulator.data import load_from_csv
from stocksimulator.core.backtester import Backtester
from stocksimulator.tax import TaxCalculator
from stocksimulator.strategies import MomentumStrategy


def run_backtest_with_taxes(strategy_name, strategy_func, market_data, start_date, end_date):
    """Run backtest and calculate tax impact."""
    print(f"\nRunning: {strategy_name}")
    print("-" * 80)

    # Standard backtest
    backtester = Backtester(initial_cash=100000.0, transaction_cost_bps=2.0)

    result = backtester.run_backtest(
        strategy_name=strategy_name,
        market_data=market_data,
        strategy_func=strategy_func,
        start_date=start_date,
        end_date=end_date
    )

    summary = result.get_performance_summary()

    # Tax calculator
    tax_calc = TaxCalculator(
        short_term_rate=0.24,  # 24% ordinary income
        long_term_rate=0.15,   # 15% long-term gains
        lot_method='FIFO'
    )

    # Process all trades through tax calculator
    for trade in result.trades:
        if trade.transaction_type.value == 'BUY':
            tax_calc.record_purchase(
                symbol=trade.symbol,
                quantity=trade.quantity,
                price=trade.price,
                purchase_date=trade.date
            )
        elif trade.transaction_type.value == 'SELL':
            tax_calc.record_sale(
                symbol=trade.symbol,
                quantity=trade.quantity,
                price=trade.price,
                sale_date=trade.date
            )

    # Get current prices for unrealized gains
    current_prices = {}
    for symbol, data in market_data.items():
        if data.data:
            current_prices[symbol] = data.data[-1].close

    unrealized = tax_calc.get_unrealized_gains(current_prices, end_date)
    tax_summary = tax_calc.get_summary()

    # Calculate after-tax returns
    pre_tax_gain = (result.equity_curve[-1].value - 100000.0) if result.equity_curve else 0
    total_tax = tax_summary['total_tax'] + unrealized['total_potential_tax']
    after_tax_value = 100000.0 + pre_tax_gain - total_tax
    after_tax_return = ((after_tax_value - 100000.0) / 100000.0) * 100

    # Display results
    print(f"\nPre-Tax Performance:")
    print(f"  Final Value:    ${result.equity_curve[-1].value:,.2f}")
    print(f"  Total Return:   {summary['total_return']:+.2f}%")
    print(f"  Ann. Return:    {summary['annualized_return']:+.2f}%")
    print(f"  Sharpe Ratio:   {summary['sharpe_ratio']:.3f}")
    print(f"  Max Drawdown:   {summary['max_drawdown']:.2f}%")

    print(f"\nTax Impact:")
    print(f"  Short-term gains:      ${tax_summary['short_term_gains']:>12,.2f}")
    print(f"  Long-term gains:       ${tax_summary['long_term_gains']:>12,.2f}")
    print(f"  Total realized gains:  ${tax_summary['total_gains']:>12,.2f}")
    print()
    print(f"  Short-term tax (24%):  ${tax_summary['short_term_tax']:>12,.2f}")
    print(f"  Long-term tax (15%):   ${tax_summary['long_term_tax']:>12,.2f}")
    print(f"  Realized taxes:        ${tax_summary['total_tax']:>12,.2f}")
    print()
    print(f"  Unrealized ST gains:   ${unrealized['unrealized_short_term']:>12,.2f}")
    print(f"  Unrealized LT gains:   ${unrealized['unrealized_long_term']:>12,.2f}")
    print(f"  Potential taxes:       ${unrealized['total_potential_tax']:>12,.2f}")

    print(f"\nAfter-Tax Performance:")
    print(f"  After-tax value:       ${after_tax_value:>12,.2f}")
    print(f"  After-tax return:      {after_tax_return:>12.2f}%")
    print(f"  Tax drag:              {summary['total_return'] - after_tax_return:>12.2f}%")

    print(f"\nTrading Stats:")
    print(f"  Total trades:          {tax_summary['total_trades']}")
    print(f"  Short-term trades:     {tax_summary['num_short_term_trades']}")
    print(f"  Long-term trades:      {tax_summary['num_long_term_trades']}")
    print(f"  Effective tax rate:    {tax_summary['effective_tax_rate'] * 100:.2f}%")

    # Tax-loss harvesting opportunities
    opportunities = tax_calc.find_tax_loss_harvest_opportunities(
        current_prices=current_prices,
        current_date=end_date,
        min_loss=500.0
    )

    if opportunities:
        print(f"\nTax-Loss Harvesting Opportunities:")
        for symbol, lot, loss in opportunities[:5]:  # Show top 5
            print(f"  {symbol}: ${loss:,.2f} (bought {lot.purchase_date})")

    return {
        'pre_tax_return': summary['total_return'],
        'after_tax_return': after_tax_return,
        'tax_drag': summary['total_return'] - after_tax_return,
        'total_tax': total_tax,
        'effective_rate': tax_summary['effective_tax_rate']
    }


def main():
    """Compare tax impact of different strategies."""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 24 + "TAX-AWARE BACKTESTING" + " " * 33 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # Load data
    print("Loading market data...")
    spy_data = load_from_csv('sp500_stooq_daily.csv', 'SPY', 'historical_data')
    print(f"✓ Loaded {len(spy_data.data)} data points")

    # Set test period (5 years)
    end_date = spy_data.data[-1].date
    start_date = date(end_date.year - 5, end_date.month, end_date.day)

    print(f"Test period: {start_date} to {end_date}")

    # Strategy 1: Buy and Hold (low turnover)
    def buy_hold(current_date, market_data, portfolio, current_prices):
        return {'SPY': 100.0}

    results_bh = run_backtest_with_taxes(
        strategy_name='Buy & Hold',
        strategy_func=buy_hold,
        market_data={'SPY': spy_data},
        start_date=start_date,
        end_date=end_date
    )

    # Strategy 2: Momentum (higher turnover)
    momentum = MomentumStrategy(lookback_days=126, top_n=1)

    results_momentum = run_backtest_with_taxes(
        strategy_name='Momentum (6-month)',
        strategy_func=momentum,
        market_data={'SPY': spy_data},
        start_date=start_date,
        end_date=end_date
    )

    # Comparison
    print("\n" + "=" * 80)
    print("COMPARISON")
    print("=" * 80)
    print()
    print(f"{'Strategy':<25} {'Pre-Tax':<12} {'After-Tax':<12} {'Tax Drag':<12}")
    print("-" * 80)
    print(f"{'Buy & Hold':<25} {results_bh['pre_tax_return']:>10.2f}%  "
          f"{results_bh['after_tax_return']:>10.2f}%  "
          f"{results_bh['tax_drag']:>10.2f}%")
    print(f"{'Momentum':<25} {results_momentum['pre_tax_return']:>10.2f}%  "
          f"{results_momentum['after_tax_return']:>10.2f}%  "
          f"{results_momentum['tax_drag']:>10.2f}%")
    print()

    print("=" * 80)
    print("KEY INSIGHTS")
    print("=" * 80)
    print()
    print("1. Tax Drag: Active strategies face higher taxes due to:")
    print("   - More short-term capital gains (taxed at higher rates)")
    print("   - Frequent realization of gains")
    print()
    print("2. Buy & Hold Benefits:")
    print("   - Defers taxes until sale")
    print("   - Qualifies for long-term capital gains rates")
    print("   - Lower effective tax rate")
    print()
    print("3. Optimization Considerations:")
    print("   - Hold positions > 1 year when possible")
    print("   - Harvest losses to offset gains")
    print("   - Consider tax-advantaged accounts (IRA, 401k)")
    print()
    print("4. Tax-Loss Harvesting:")
    print("   - Sell losing positions to offset gains")
    print("   - Avoid wash sales (30-day rule)")
    print("   - Can reduce effective tax rate")
    print()


if __name__ == '__main__':
    main()
