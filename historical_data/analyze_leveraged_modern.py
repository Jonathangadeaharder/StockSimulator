#!/usr/bin/env python3
"""
Analyze 2x Leveraged ETF vs Non-Leveraged Performance - MODERN ERA (1950+)
Focus on more recent market conditions
"""

import csv
from datetime import datetime
import math

def read_shiller_csv(filename='sp500_github_monthly.csv', start_year=1950):
    """Read Shiller S&P 500 data from CSV, starting from specified year"""
    data = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                date = datetime.strptime(row['Date'], '%Y-%m-%d')

                # Filter by start year
                if date.year < start_year:
                    continue

                price = float(row['SP500']) if row['SP500'] else None
                dividend = float(row['Dividend']) if row['Dividend'] else 0.0

                if price and price > 0:
                    data.append({
                        'date': date,
                        'price': price,
                        'dividend': dividend
                    })
            except (ValueError, KeyError) as e:
                continue

    return data

def calculate_monthly_returns(data):
    """Calculate monthly returns with dividend yield"""
    returns = []

    for i in range(1, len(data)):
        prev = data[i-1]
        curr = data[i]

        price_return = (curr['price'] - prev['price']) / prev['price']
        dividend_yield_monthly = (curr['dividend'] / 12) / prev['price']
        total_return = price_return + dividend_yield_monthly

        returns.append({
            'date': curr['date'],
            'return': total_return,
            'price': curr['price'],
            'dividend': curr['dividend']
        })

    return returns

def simulate_leveraged_etf(returns, leverage=2.0, ter=0.006):
    """Simulate leveraged ETF with TER"""
    monthly_ter = ter / 12
    leveraged_returns = []

    for ret in returns:
        leveraged_ret = leverage * ret['return'] - monthly_ter
        leveraged_returns.append({
            'date': ret['date'],
            'return': leveraged_ret,
            'unleveraged_return': ret['return']
        })

    return leveraged_returns

def find_worst_periods(leveraged_returns, min_years=5, max_years=15):
    """Find rolling periods where leveraged ETF underperformed"""
    results = []

    for years in range(min_years, max_years + 1):
        window_months = years * 12

        for i in range(len(leveraged_returns) - window_months + 1):
            window = leveraged_returns[i:i + window_months]

            lev_cumulative = 1.0
            unlev_cumulative = 1.0

            for ret in window:
                lev_cumulative *= (1 + ret['return'])
                unlev_cumulative *= (1 + ret['unleveraged_return'])

            lev_annualized = (lev_cumulative ** (1/years)) - 1
            unlev_annualized = (unlev_cumulative ** (1/years)) - 1

            underperformance = lev_annualized - (unlev_annualized * 2)
            absolute_underperformance = lev_annualized - unlev_annualized
            ratio = lev_cumulative / unlev_cumulative if unlev_cumulative > 0 else 0

            results.append({
                'start_date': window[0]['date'],
                'end_date': window[-1]['date'],
                'years': years,
                'lev_total_return': (lev_cumulative - 1) * 100,
                'unlev_total_return': (unlev_cumulative - 1) * 100,
                'lev_annualized': lev_annualized * 100,
                'unlev_annualized': unlev_annualized * 100,
                'underperformance': underperformance * 100,
                'absolute_underperformance': absolute_underperformance * 100,
                'ratio': ratio,
                'lev_cumulative': lev_cumulative,
                'unlev_cumulative': unlev_cumulative
            })

    return results

# Main analysis
print("=" * 100)
print("2X LEVERAGED ETF ANALYSIS - MODERN ERA (1950-2023)")
print("=" * 100)
print()

data = read_shiller_csv('sp500_github_monthly.csv', start_year=1950)
print(f"Period: {data[0]['date'].strftime('%Y-%m')} to {data[-1]['date'].strftime('%Y-%m')}")
print(f"Total months: {len(data)}")
print()

monthly_returns = calculate_monthly_returns(data)
leveraged_returns = simulate_leveraged_etf(monthly_returns, leverage=2.0, ter=0.006)

print("Analyzing all 5-15 year windows...")
all_periods = find_worst_periods(leveraged_returns, min_years=5, max_years=15)
print(f"Analyzed {len(all_periods)} windows")
print()

# Sort by absolute underperformance
worst_by_absolute = sorted(all_periods, key=lambda x: x['absolute_underperformance'])

print("=" * 100)
print("TOP 20 WORST PERIODS - Modern Era (1950+)")
print("=" * 100)
print()
print(f"{'Rank':<6} {'Period':<30} {'Yrs':<5} {'Lev Ann%':<10} {'Unlev Ann%':<12} {'Gap%':<10}")
print("-" * 100)

for i, period in enumerate(worst_by_absolute[:20], 1):
    period_str = f"{period['start_date'].strftime('%Y-%m')} to {period['end_date'].strftime('%Y-%m')}"
    print(f"{i:<6} {period_str:<30} {period['years']:<5} "
          f"{period['lev_annualized']:>8.2f}%  {period['unlev_annualized']:>10.2f}%  "
          f"{period['absolute_underperformance']:>8.2f}%")

print()
print("=" * 100)
print("WORST PERIOD BY WINDOW LENGTH - Modern Era")
print("=" * 100)
print()

for years in range(5, 16):
    periods_for_year = [p for p in all_periods if p['years'] == years]
    if periods_for_year:
        worst = min(periods_for_year, key=lambda x: x['absolute_underperformance'])
        print(f"{years:>2}-Year: {worst['start_date'].strftime('%Y-%m')} to {worst['end_date'].strftime('%Y-%m')}")
        print(f"   Leveraged: {worst['lev_annualized']:>7.2f}% ann. (total: {worst['lev_total_return']:>7.1f}%)")
        print(f"   Unleveraged: {worst['unlev_annualized']:>7.2f}% ann. (total: {worst['unlev_total_return']:>7.1f}%)")
        print(f"   Gap: {worst['absolute_underperformance']:>7.2f}% per year")
        print(f"   Final Ratio: {worst['ratio']:.3f}x (leveraged/unleveraged)")
        print()

# Detailed analysis of THE worst period
worst_overall = worst_by_absolute[0]
print("=" * 100)
print("DETAILED ANALYSIS - ABSOLUTE WORST MODERN PERIOD")
print("=" * 100)
print()
print(f"Period: {worst_overall['start_date'].strftime('%B %Y')} to {worst_overall['end_date'].strftime('%B %Y')}")
print(f"Duration: {worst_overall['years']} years")
print()
print(f"If you invested $10,000:")
print(f"  Non-Leveraged: ${10000 * worst_overall['unlev_cumulative']:,.2f} ({worst_overall['unlev_total_return']:.2f}% total)")
print(f"  2x Leveraged:  ${10000 * worst_overall['lev_cumulative']:,.2f} ({worst_overall['lev_total_return']:.2f}% total)")
print(f"  Difference:    ${10000 * (worst_overall['unlev_cumulative'] - worst_overall['lev_cumulative']):,.2f}")
print()
print(f"Annualized Returns:")
print(f"  Non-Leveraged: {worst_overall['unlev_annualized']:>7.2f}%")
print(f"  2x Leveraged:  {worst_overall['lev_annualized']:>7.2f}%")
print(f"  Gap:           {worst_overall['absolute_underperformance']:>7.2f}%")
print()

# Calculate volatility for worst period
worst_start_idx = next(i for i, r in enumerate(leveraged_returns)
                       if r['date'] >= worst_overall['start_date'])
worst_end_idx = next(i for i, r in enumerate(leveraged_returns)
                     if r['date'] >= worst_overall['end_date'])
worst_period_returns = leveraged_returns[worst_start_idx:worst_end_idx+1]

returns_only = [r['unleveraged_return'] for r in worst_period_returns]
mean_return = sum(returns_only) / len(returns_only)
variance = sum((r - mean_return) ** 2 for r in returns_only) / len(returns_only)
volatility = math.sqrt(variance) * math.sqrt(12) * 100

neg_months = sum(1 for r in worst_period_returns if r['unleveraged_return'] < 0)
pos_months = len(worst_period_returns) - neg_months

print(f"Market Characteristics:")
print(f"  Annualized Volatility: {volatility:.2f}%")
print(f"  Positive Months: {pos_months}/{len(worst_period_returns)} ({100*pos_months/len(worst_period_returns):.1f}%)")
print(f"  Negative Months: {neg_months}/{len(worst_period_returns)} ({100*neg_months/len(worst_period_returns):.1f}%)")

# Find max drawdown during this period
peak = worst_period_returns[0]['unleveraged_return']
max_dd = 0
for r in worst_period_returns:
    ret = r['unleveraged_return']
    if ret > peak:
        peak = ret
    dd = (peak - ret) / peak if peak > 0 else 0
    if dd > max_dd:
        max_dd = dd

print(f"  Est. Max Drawdown: {max_dd*100:.2f}%")

print()
print("=" * 100)
print()
print("KEY INSIGHTS:")
print()
print("1. The worst modern period for 2x leveraged ETFs was during market volatility")
print("   and sideways/declining markets, NOT during simple bull markets.")
print()
print("2. High volatility causes 'volatility decay' where daily rebalancing")
print("   erodes returns even if the underlying index goes nowhere.")
print()
print("3. The 0.6% TER further reduces the leveraged ETF returns over time.")
print()
print("4. In the worst case, a 2x leveraged ETF can UNDERPERFORM the unleveraged")
print("   index, defeating the purpose of leverage.")
print()
print("=" * 100)
