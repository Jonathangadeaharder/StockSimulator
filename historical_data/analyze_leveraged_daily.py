#!/usr/bin/env python3
# @structurelint:no-test
"""
Accurate 2x Leveraged ETF Simulation with DAILY Rebalancing
Uses daily price data for precise simulation
"""

import csv
from datetime import datetime
import math

def read_daily_data(filename='sp500_stooq_daily.csv', start_year=1950):
    """Read daily S&P 500 data"""
    data = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                date = datetime.strptime(row['Date'], '%Y-%m-%d')

                if date.year < start_year:
                    continue

                close = float(row['Close']) if row['Close'] else None

                if close and close > 0:
                    data.append({
                        'date': date,
                        'close': close
                    })
            except (ValueError, KeyError):
                continue

    return data

def calculate_daily_returns(data, avg_dividend_yield=0.02):
    """
    Calculate daily returns

    avg_dividend_yield: Annual dividend yield (default 2%)
    This is distributed across trading days
    """
    returns = []
    daily_dividend_yield = avg_dividend_yield / 252  # Approximate 252 trading days per year

    for i in range(1, len(data)):
        prev = data[i-1]
        curr = data[i]

        # Daily price return
        price_return = (curr['close'] - prev['close']) / prev['close']

        # Add daily dividend yield
        total_return = price_return + daily_dividend_yield

        returns.append({
            'date': curr['date'],
            'return': total_return,
            'price_return': price_return
        })

    return returns

def simulate_leveraged_etf_daily(returns, leverage=2.0, ter=0.006):
    """
    Simulate 2x leveraged ETF with DAILY rebalancing

    Key: If index returns +10% in a day, leveraged ETF returns +20% (2x)
    If index returns -5% in a day, leveraged ETF returns -10% (2x)

    TER is deducted daily
    """
    daily_ter = ter / 252  # Daily TER cost

    leveraged_returns = []

    for ret in returns:
        # Daily leveraged return: 2x the daily return
        leveraged_ret = leverage * ret['return']

        # Subtract daily TER
        leveraged_ret_after_ter = leveraged_ret - daily_ter

        leveraged_returns.append({
            'date': ret['date'],
            'lev_return': leveraged_ret_after_ter,
            'unlev_return': ret['return']
        })

    return leveraged_returns

def find_worst_periods_daily(leveraged_returns, min_years=5, max_years=15):
    """Find worst periods using daily data"""
    results = []

    # Test different window sizes (in trading days)
    for years in range(min_years, max_years + 1):
        window_days = int(years * 252)  # Approximate trading days

        # Rolling window analysis
        for i in range(0, len(leveraged_returns) - window_days, 21):  # Step by ~month to reduce computation
            window = leveraged_returns[i:i + window_days]

            if len(window) < window_days * 0.95:  # Allow some missing days
                continue

            # Calculate cumulative returns
            lev_cumulative = 1.0
            unlev_cumulative = 1.0

            for ret in window:
                lev_cumulative *= (1 + ret['lev_return'])
                unlev_cumulative *= (1 + ret['unlev_return'])

            # Calculate actual years (accounting for weekends/holidays)
            actual_years = (window[-1]['date'] - window[0]['date']).days / 365.25

            if actual_years < years * 0.9:  # Skip if too short
                continue

            # Calculate annualized returns
            lev_annualized = (lev_cumulative ** (1/actual_years)) - 1
            unlev_annualized = (unlev_cumulative ** (1/actual_years)) - 1

            # Calculate metrics
            underperformance = lev_annualized - (unlev_annualized * 2)
            absolute_underperformance = lev_annualized - unlev_annualized
            ratio = lev_cumulative / unlev_cumulative if unlev_cumulative > 0 else 0

            results.append({
                'start_date': window[0]['date'],
                'end_date': window[-1]['date'],
                'years': actual_years,
                'target_years': years,
                'lev_total_return': (lev_cumulative - 1) * 100,
                'unlev_total_return': (unlev_cumulative - 1) * 100,
                'lev_annualized': lev_annualized * 100,
                'unlev_annualized': unlev_annualized * 100,
                'underperformance': underperformance * 100,
                'absolute_underperformance': absolute_underperformance * 100,
                'ratio': ratio,
                'lev_cumulative': lev_cumulative,
                'unlev_cumulative': unlev_cumulative,
                'days': len(window)
            })

    return results

def calculate_volatility(returns, window):
    """Calculate volatility for a window of returns"""
    if not window:
        return 0

    rets = [r['unlev_return'] for r in window]
    n = len(rets)
    mean = sum(rets) / n
    # Use sample variance (n-1) for unbiased estimator
    variance = sum((r - mean) ** 2 for r in rets) / (n - 1) if n > 1 else 0
    daily_vol = math.sqrt(variance)
    annual_vol = daily_vol * math.sqrt(252)  # Annualize
    return annual_vol * 100

# Main analysis
print("=" * 100)
print("2X LEVERAGED ETF - DAILY REBALANCING SIMULATION")
print("=" * 100)
print()
print("This analysis uses DAILY price data for accurate simulation")
print("Key: If S&P 500 rises 10% in one day, the 2x ETF rises 20% that day")
print()
print("Parameters:")
print("  - Leverage: 2.0x (daily rebalancing)")
print("  - TER: 0.6% per year (deducted daily)")
print("  - Dividend Yield: ~2% annual (approximate, distributed daily)")
print("  - Time Windows: 5 to 15 years")
print()

# Load data
print("Loading daily S&P 500 data from 1950...")
data = read_daily_data('sp500_stooq_daily.csv', start_year=1950)
print(f"  Loaded {len(data):,} trading days")
print(f"  Period: {data[0]['date'].strftime('%Y-%m-%d')} to {data[-1]['date'].strftime('%Y-%m-%d')}")
print()

# Calculate returns
print("Calculating daily returns...")
daily_returns = calculate_daily_returns(data, avg_dividend_yield=0.02)
print(f"  Calculated {len(daily_returns):,} daily returns")
print()

# Simulate leveraged ETF
print("Simulating 2x Leveraged ETF with DAILY rebalancing...")
leveraged_returns = simulate_leveraged_etf_daily(daily_returns, leverage=2.0, ter=0.006)
print(f"  Simulated {len(leveraged_returns):,} days")
print()

# Find worst periods
print("Analyzing rolling windows (this may take a minute)...")
all_periods = find_worst_periods_daily(leveraged_returns, min_years=5, max_years=15)
print(f"  Analyzed {len(all_periods):,} time windows")
print()

# Sort by absolute underperformance
worst_by_absolute = sorted(all_periods, key=lambda x: x['absolute_underperformance'])

print("=" * 100)
print("TOP 15 WORST PERIODS - Daily Rebalancing Simulation")
print("=" * 100)
print()
print(f"{'Rank':<6} {'Period':<30} {'Yrs':<6} {'Lev Ann%':<11} {'Unlev Ann%':<13} {'Gap%':<10}")
print("-" * 100)

for i, period in enumerate(worst_by_absolute[:15], 1):
    period_str = f"{period['start_date'].strftime('%Y-%m-%d')} to {period['end_date'].strftime('%Y-%m-%d')}"
    print(f"{i:<6} {period_str:<30} {period['years']:<6.1f} "
          f"{period['lev_annualized']:>9.2f}%  {period['unlev_annualized']:>11.2f}%  "
          f"{period['absolute_underperformance']:>8.2f}%")

print()
print("=" * 100)
print("ABSOLUTE WORST PERIOD - Detailed Analysis")
print("=" * 100)
print()

worst = worst_by_absolute[0]
print(f"Period: {worst['start_date'].strftime('%B %d, %Y')} to {worst['end_date'].strftime('%B %d, %Y')}")
print(f"Duration: {worst['years']:.2f} years ({worst['days']:,} trading days)")
print()
print(f"Starting with $10,000:")
print(f"  Non-Leveraged Final Value: ${10000 * worst['unlev_cumulative']:,.2f}")
print(f"  2x Leveraged Final Value:  ${10000 * worst['lev_cumulative']:,.2f}")
print(f"  Difference:                ${10000 * (worst['unlev_cumulative'] - worst['lev_cumulative']):,.2f}")
print()
print(f"Total Returns:")
print(f"  Non-Leveraged: {worst['unlev_total_return']:>8.2f}%")
print(f"  2x Leveraged:  {worst['lev_total_return']:>8.2f}%")
print()
print(f"Annualized Returns:")
print(f"  Non-Leveraged: {worst['unlev_annualized']:>8.2f}%")
print(f"  2x Leveraged:  {worst['lev_annualized']:>8.2f}%")
print(f"  Underperformance Gap: {worst['absolute_underperformance']:>8.2f}% per year")
print()
print(f"Leverage Efficiency:")
print(f"  Expected 2x Return: {worst['unlev_annualized'] * 2:>8.2f}% (if perfect 2x)")
print(f"  Actual Lev Return:  {worst['lev_annualized']:>8.2f}%")
print(f"  Shortfall:          {worst['underperformance']:>8.2f}% per year")
print(f"  Ratio (Lev/Unlev):  {worst['ratio']:.4f}x")
print()

# Calculate volatility for this period
worst_start_idx = next(i for i, r in enumerate(leveraged_returns)
                       if r['date'] >= worst['start_date'])
worst_end_idx = next(i for i, r in enumerate(leveraged_returns)
                     if r['date'] >= worst['end_date'])
worst_period_returns = leveraged_returns[worst_start_idx:worst_end_idx+1]

volatility = calculate_volatility(leveraged_returns, worst_period_returns)
neg_days = sum(1 for r in worst_period_returns if r['unlev_return'] < 0)
pos_days = len(worst_period_returns) - neg_days

print(f"Market Characteristics:")
print(f"  Annualized Volatility: {volatility:.2f}%")
print(f"  Positive Days: {pos_days:,}/{len(worst_period_returns):,} ({100*pos_days/len(worst_period_returns):.1f}%)")
print(f"  Negative Days: {neg_days:,}/{len(worst_period_returns):,} ({100*neg_days/len(worst_period_returns):.1f}%)")

print()
print("=" * 100)
print("WORST PERIOD BY TARGET WINDOW LENGTH")
print("=" * 100)
print()

for target_years in range(5, 16):
    periods_for_year = [p for p in all_periods if p['target_years'] == target_years]
    if periods_for_year:
        worst_for_year = min(periods_for_year, key=lambda x: x['absolute_underperformance'])
        print(f"{target_years:>2}-Year Window:")
        print(f"    Period: {worst_for_year['start_date'].strftime('%Y-%m-%d')} to "
              f"{worst_for_year['end_date'].strftime('%Y-%m-%d')}")
        print(f"    Leveraged:   {worst_for_year['lev_annualized']:>7.2f}% ann. "
              f"(total: {worst_for_year['lev_total_return']:>8.2f}%)")
        print(f"    Unleveraged: {worst_for_year['unlev_annualized']:>7.2f}% ann. "
              f"(total: {worst_for_year['unlev_total_return']:>8.2f}%)")
        print(f"    Gap:         {worst_for_year['absolute_underperformance']:>7.2f}% per year")
        print()

print("=" * 100)
print()
print("CONCLUSION:")
print(f"  The ABSOLUTE WORST period for a 2x daily-rebalanced leveraged S&P 500 ETF was:")
print(f"  {worst['start_date'].strftime('%B %Y')} to {worst['end_date'].strftime('%B %Y')}")
print(f"  ({worst['years']:.1f} years)")
print()
print(f"  In this period:")
print(f"  - Unleveraged S&P 500 returned {worst['unlev_annualized']:.2f}% annualized")
print(f"  - 2x Leveraged ETF returned {worst['lev_annualized']:.2f}% annualized")
print(f"  - Leveraged UNDERPERFORMED by {worst['absolute_underperformance']:.2f}% per year")
print()
print(f"  This demonstrates the devastating effect of volatility decay and daily")
print(f"  rebalancing costs in choppy/declining markets.")
print()
print("=" * 100)
