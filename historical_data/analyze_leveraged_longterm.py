#!/usr/bin/env python3
# @structurelint:no-test
"""
Analyze 2x Leveraged ETF for LONG-TERM periods (15-30 years)
Check if leveraged ETFs still underperform over very long horizons
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
                    data.append({'date': date, 'close': close})
            except (ValueError, KeyError):
                continue
    return data

def calculate_daily_returns(data, avg_dividend_yield=0.02):
    """Calculate daily returns with dividend yield"""
    returns = []
    daily_dividend_yield = avg_dividend_yield / 252

    for i in range(1, len(data)):
        prev = data[i-1]
        curr = data[i]
        price_return = (curr['close'] - prev['close']) / prev['close']
        total_return = price_return + daily_dividend_yield

        returns.append({
            'date': curr['date'],
            'return': total_return,
            'price_return': price_return
        })
    return returns

def simulate_leveraged_etf_daily(returns, leverage=2.0, ter=0.006):
    """Simulate 2x leveraged ETF with daily rebalancing"""
    daily_ter = ter / 252
    leveraged_returns = []

    for ret in returns:
        leveraged_ret = leverage * ret['return'] - daily_ter
        leveraged_returns.append({
            'date': ret['date'],
            'lev_return': leveraged_ret,
            'unlev_return': ret['return']
        })
    return leveraged_returns

def find_periods_longterm(leveraged_returns, min_years=15, max_years=30):
    """Find all periods for long-term windows"""
    results = []

    for years in range(min_years, max_years + 1):
        window_days = int(years * 252)

        # Use larger steps for long periods to reduce computation
        step = 63 if years >= 20 else 42  # ~3 months or ~2 months

        for i in range(0, len(leveraged_returns) - window_days, step):
            window = leveraged_returns[i:i + window_days]

            if len(window) < window_days * 0.95:
                continue

            # Calculate cumulative returns
            lev_cumulative = 1.0
            unlev_cumulative = 1.0

            for ret in window:
                lev_cumulative *= (1 + ret['lev_return'])
                unlev_cumulative *= (1 + ret['unlev_return'])

            actual_years = (window[-1]['date'] - window[0]['date']).days / 365.25

            if actual_years < years * 0.9:
                continue

            lev_annualized = (lev_cumulative ** (1/actual_years)) - 1
            unlev_annualized = (unlev_cumulative ** (1/actual_years)) - 1

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
    """Calculate annualized volatility for a window"""
    if not window:
        return 0
    rets = [r['unlev_return'] for r in window]
    n = len(rets)
    mean = sum(rets) / n
    # Use sample variance (n-1) for unbiased estimator
    variance = sum((r - mean) ** 2 for r in rets) / (n - 1) if n > 1 else 0
    daily_vol = math.sqrt(variance)
    annual_vol = daily_vol * math.sqrt(252)
    return annual_vol * 100

# Main analysis
print("=" * 100)
print("2X LEVERAGED ETF - LONG-TERM ANALYSIS (15-30 YEARS)")
print("=" * 100)
print()
print("Testing whether leveraged ETFs EVER underperform over very long periods...")
print()

# Load data
print("Loading data...")
data = read_daily_data('sp500_stooq_daily.csv', start_year=1950)
print(f"  Period: {data[0]['date'].strftime('%Y-%m-%d')} to {data[-1]['date'].strftime('%Y-%m-%d')}")
print(f"  Trading days: {len(data):,}")
print()

daily_returns = calculate_daily_returns(data, avg_dividend_yield=0.02)
leveraged_returns = simulate_leveraged_etf_daily(daily_returns, leverage=2.0, ter=0.006)
print(f"  Simulated {len(leveraged_returns):,} days")
print()

print("Analyzing long-term windows (this will take a moment)...")
all_periods = find_periods_longterm(leveraged_returns, min_years=15, max_years=30)
print(f"  Analyzed {len(all_periods):,} time windows")
print()

# Sort by absolute underperformance
worst_by_absolute = sorted(all_periods, key=lambda x: x['absolute_underperformance'])
best_by_absolute = sorted(all_periods, key=lambda x: x['absolute_underperformance'], reverse=True)

print("=" * 100)
print("TOP 15 WORST LONG-TERM PERIODS (15-30 years)")
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
print("TOP 15 BEST LONG-TERM PERIODS (where leverage performed best)")
print("=" * 100)
print()
print(f"{'Rank':<6} {'Period':<30} {'Yrs':<6} {'Lev Ann%':<11} {'Unlev Ann%':<13} {'Gap%':<10}")
print("-" * 100)

for i, period in enumerate(best_by_absolute[:15], 1):
    period_str = f"{period['start_date'].strftime('%Y-%m-%d')} to {period['end_date'].strftime('%Y-%m-%d')}"
    print(f"{i:<6} {period_str:<30} {period['years']:<6.1f} "
          f"{period['lev_annualized']:>9.2f}%  {period['unlev_annualized']:>11.2f}%  "
          f"{period['absolute_underperformance']:>8.2f}%")

print()
print("=" * 100)
print("WORST PERIOD BY WINDOW LENGTH (15-30 years)")
print("=" * 100)
print()

for target_years in range(15, 31):
    periods_for_year = [p for p in all_periods if p['target_years'] == target_years]
    if periods_for_year:
        worst = min(periods_for_year, key=lambda x: x['absolute_underperformance'])
        print(f"{target_years:>2}-Year Window:")
        print(f"    Period: {worst['start_date'].strftime('%Y-%m-%d')} to "
              f"{worst['end_date'].strftime('%Y-%m-%d')}")
        print(f"    Leveraged:   {worst['lev_annualized']:>7.2f}% ann. "
              f"(total: {worst['lev_total_return']:>10.1f}%, final value: ${10000 * worst['lev_cumulative']:,.0f})")
        print(f"    Unleveraged: {worst['unlev_annualized']:>7.2f}% ann. "
              f"(total: {worst['unlev_total_return']:>10.1f}%, final value: ${10000 * worst['unlev_cumulative']:,.0f})")
        print(f"    Gap:         {worst['absolute_underperformance']:>7.2f}% per year")
        print(f"    Ratio:       {worst['ratio']:.3f}x (Lev/Unlev)")
        print()

print("=" * 100)
print("BEST PERIOD BY WINDOW LENGTH (15-30 years)")
print("=" * 100)
print()

for target_years in range(15, 31):
    periods_for_year = [p for p in all_periods if p['target_years'] == target_years]
    if periods_for_year:
        best = max(periods_for_year, key=lambda x: x['absolute_underperformance'])
        print(f"{target_years:>2}-Year Window:")
        print(f"    Period: {best['start_date'].strftime('%Y-%m-%d')} to "
              f"{best['end_date'].strftime('%Y-%m-%d')}")
        print(f"    Leveraged:   {best['lev_annualized']:>7.2f}% ann. "
              f"(total: {best['lev_total_return']:>10.1f}%, final value: ${10000 * best['lev_cumulative']:,.0f})")
        print(f"    Unleveraged: {best['unlev_annualized']:>7.2f}% ann. "
              f"(total: {best['unlev_total_return']:>10.1f}%, final value: ${10000 * best['unlev_cumulative']:,.0f})")
        print(f"    Gap:         {best['absolute_underperformance']:>7.2f}% per year")
        print(f"    Ratio:       {best['ratio']:.3f}x (Lev/Unlev)")
        print()

# Detailed analysis of absolute worst
print("=" * 100)
print("DETAILED ANALYSIS - ABSOLUTE WORST LONG-TERM PERIOD")
print("=" * 100)
print()

worst_overall = worst_by_absolute[0]
print(f"Period: {worst_overall['start_date'].strftime('%B %d, %Y')} to {worst_overall['end_date'].strftime('%B %d, %Y')}")
print(f"Duration: {worst_overall['years']:.2f} years ({worst_overall['days']:,} trading days)")
print()
print(f"Starting with $10,000:")
print(f"  Non-Leveraged: ${10000 * worst_overall['unlev_cumulative']:,.2f} ({worst_overall['unlev_total_return']:+.2f}%)")
print(f"  2x Leveraged:  ${10000 * worst_overall['lev_cumulative']:,.2f} ({worst_overall['lev_total_return']:+.2f}%)")
print(f"  Difference:    ${10000 * (worst_overall['unlev_cumulative'] - worst_overall['lev_cumulative']):,.2f}")
print()
print(f"Annualized Returns:")
print(f"  Non-Leveraged: {worst_overall['unlev_annualized']:>7.2f}%")
print(f"  2x Leveraged:  {worst_overall['lev_annualized']:>7.2f}%")
print(f"  Gap:           {worst_overall['absolute_underperformance']:>7.2f}% per year")
print()

# Calculate how many periods had underperformance
underperforming = [p for p in all_periods if p['absolute_underperformance'] < 0]
outperforming = [p for p in all_periods if p['absolute_underperformance'] >= 0]

print("=" * 100)
print("STATISTICAL SUMMARY")
print("=" * 100)
print()
print(f"Total periods analyzed: {len(all_periods):,}")
print(f"Periods where leveraged UNDERPERFORMED: {len(underperforming):,} ({100*len(underperforming)/len(all_periods):.1f}%)")
print(f"Periods where leveraged OUTPERFORMED: {len(outperforming):,} ({100*len(outperforming)/len(all_periods):.1f}%)")
print()

if underperforming:
    avg_under = sum(p['absolute_underperformance'] for p in underperforming) / len(underperforming)
    print(f"Average underperformance (when it underperforms): {avg_under:.2f}% per year")

if outperforming:
    avg_out = sum(p['absolute_underperformance'] for p in outperforming) / len(outperforming)
    print(f"Average outperformance (when it outperforms): {avg_out:.2f}% per year")

print()

# Overall average
avg_all = sum(p['absolute_underperformance'] for p in all_periods) / len(all_periods)
print(f"Overall average gap across ALL {len(all_periods):,} periods: {avg_all:.2f}% per year")

print()
print("=" * 100)
print()
print("KEY INSIGHTS FOR LONG-TERM PERIODS (15-30 YEARS):")
print()

if len(underperforming) > len(all_periods) / 2:
    print("⚠️  WARNING: The majority of long-term periods show underperformance!")
else:
    print("✓  Most long-term periods show leveraged ETFs outperform")

print()

if avg_all < 0:
    print(f"📊 On average, leveraged ETFs UNDERPERFORM by {abs(avg_all):.2f}% per year")
    print("   Even over 15-30 year periods, volatility decay dominates.")
else:
    print(f"📊 On average, leveraged ETFs OUTPERFORM by {avg_all:.2f}% per year")
    print("   Over very long periods, compounding can overcome volatility decay.")

print()
print("🎯 The worst long-term period shows that even 15+ years isn't always enough")
print("   to overcome the effects of major crashes and high volatility.")
print()
print("=" * 100)
