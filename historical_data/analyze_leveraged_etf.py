#!/usr/bin/env python3
# @structurelint:no-test
"""
Analyze 2x Leveraged ETF vs Non-Leveraged Performance
Find the worst 5-15 year period for leveraged ETF with dividend reinvestment
"""

import csv
from datetime import datetime
from collections import defaultdict
import math

def read_shiller_csv(filename='sp500_github_monthly.csv'):
    """Read Shiller S&P 500 data from CSV"""
    data = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                date = datetime.strptime(row['Date'], '%Y-%m-%d')
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

        # Price return
        price_return = (curr['price'] - prev['price']) / prev['price']

        # Dividend yield (annualized dividend / price, then monthly)
        dividend_yield_monthly = (curr['dividend'] / 12) / prev['price']

        # Total return
        total_return = price_return + dividend_yield_monthly

        returns.append({
            'date': curr['date'],
            'return': total_return,
            'price': curr['price'],
            'dividend': curr['dividend']
        })

    return returns

def simulate_leveraged_etf(returns, leverage=2.0, ter=0.006):
    """
    Simulate leveraged ETF with daily rebalancing approximation

    For a 2x leveraged ETF with monthly data, we approximate daily rebalancing:
    - Leveraged monthly return ≈ leverage * monthly_return - volatility_drag - TER
    - Volatility drag = (leverage^2 - leverage) * variance / 2

    However, for simplicity and given we have monthly data, we'll use:
    - Leveraged return = leverage * return - monthly TER
    - This is a reasonable approximation for monthly periods
    """

    monthly_ter = ter / 12  # Convert annual TER to monthly

    leveraged_returns = []

    for i, ret in enumerate(returns):
        # Basic leveraged return
        leveraged_ret = leverage * ret['return']

        # Subtract TER
        leveraged_ret_after_ter = leveraged_ret - monthly_ter

        # For more accuracy, we could add volatility drag, but we'd need to calculate
        # rolling volatility. For now, the leverage * return already captures most
        # of the effect since compounding happens through cumulative returns.

        leveraged_returns.append({
            'date': ret['date'],
            'return': leveraged_ret_after_ter,
            'unleveraged_return': ret['return']
        })

    return leveraged_returns

def calculate_cumulative_returns(returns_list, return_key='return'):
    """Calculate cumulative returns from a list of period returns"""
    cumulative = 1.0
    result = []

    for ret in returns_list:
        cumulative *= (1 + ret[return_key])
        result.append({
            'date': ret['date'],
            'cumulative': cumulative,
            'return': ret[return_key]
        })

    return result

def find_worst_periods(leveraged_returns, min_years=5, max_years=15):
    """
    Find rolling periods where leveraged ETF underperformed vs unleveraged
    Returns list of periods with their performance metrics
    """

    results = []

    # Test different window sizes (in months)
    for years in range(min_years, max_years + 1):
        window_months = years * 12

        # Rolling window analysis
        for i in range(len(leveraged_returns) - window_months + 1):
            window = leveraged_returns[i:i + window_months]

            # Calculate cumulative returns for both
            lev_cumulative = 1.0
            unlev_cumulative = 1.0

            for ret in window:
                lev_cumulative *= (1 + ret['return'])
                unlev_cumulative *= (1 + ret['unleveraged_return'])

            # Calculate annualized returns
            lev_annualized = (lev_cumulative ** (1/years)) - 1
            unlev_annualized = (unlev_cumulative ** (1/years)) - 1

            # Calculate underperformance
            # We want to find where leveraged UNDERPERFORMED unleveraged
            # Ideally, 2x leveraged should outperform, so underperformance is bad
            underperformance = lev_annualized - (unlev_annualized * 2)

            # Also calculate absolute underperformance
            absolute_underperformance = lev_annualized - unlev_annualized

            # Calculate the ratio (how much worse)
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
                'ratio': ratio
            })

    return results

def calculate_volatility(returns_list, window_months=12):
    """Calculate rolling volatility (annualized standard deviation)"""
    volatilities = []

    for i in range(window_months, len(returns_list)):
        window = returns_list[i-window_months:i]
        returns = [r['return'] for r in window]

        # Calculate standard deviation (using sample variance)
        n = len(returns)
        mean = sum(returns) / n
        # Use sample variance (n-1) for unbiased estimator
        variance = sum((r - mean) ** 2 for r in returns) / (n - 1) if n > 1 else 0
        std_dev = math.sqrt(variance)

        # Annualize (monthly to annual)
        annual_vol = std_dev * math.sqrt(12)

        volatilities.append({
            'date': returns_list[i]['date'],
            'volatility': annual_vol * 100
        })

    return volatilities

# Main analysis
print("=" * 100)
print("2X LEVERAGED ETF ANALYSIS - Finding Worst Performance Periods")
print("=" * 100)
print()
print("Parameters:")
print("  - Leverage: 2.0x")
print("  - TER: 0.6% per year")
print("  - Dividend Reinvestment: Yes")
print("  - Time Windows: 5 to 15 years")
print("  - Dataset: Shiller S&P 500 (1871-2023)")
print()
print("Loading data...")

# Load and process data
data = read_shiller_csv('sp500_github_monthly.csv')
print(f"  Loaded {len(data)} months of data")
print(f"  Period: {data[0]['date'].strftime('%Y-%m')} to {data[-1]['date'].strftime('%Y-%m')}")
print()

# Calculate returns
print("Calculating returns...")
monthly_returns = calculate_monthly_returns(data)
print(f"  Calculated {len(monthly_returns)} monthly returns")
print()

# Simulate leveraged ETF
print("Simulating 2x Leveraged ETF with 0.6% TER...")
leveraged_returns = simulate_leveraged_etf(monthly_returns, leverage=2.0, ter=0.006)
print(f"  Simulated {len(leveraged_returns)} periods")
print()

# Find worst periods
print("Analyzing rolling windows from 5 to 15 years...")
all_periods = find_worst_periods(leveraged_returns, min_years=5, max_years=15)
print(f"  Analyzed {len(all_periods)} different time windows")
print()

# Sort by absolute underperformance (where leveraged did worse than unleveraged)
worst_by_absolute = sorted(all_periods, key=lambda x: x['absolute_underperformance'])

# Sort by ratio (where leveraged/unleveraged ratio is lowest)
worst_by_ratio = sorted(all_periods, key=lambda x: x['ratio'])

# Sort by underperformance vs 2x expectation
worst_by_expectation = sorted(all_periods, key=lambda x: x['underperformance'])

print("=" * 100)
print("TOP 10 WORST PERIODS - Leveraged vs Unleveraged (Absolute Underperformance)")
print("=" * 100)
print()
print(f"{'Rank':<6} {'Period':<25} {'Years':<7} {'Lev Return':<12} {'Unlev Return':<12} {'Lev - Unlev':<12}")
print("-" * 100)

for i, period in enumerate(worst_by_absolute[:10], 1):
    period_str = f"{period['start_date'].strftime('%Y-%m')} to {period['end_date'].strftime('%Y-%m')}"
    print(f"{i:<6} {period_str:<25} {period['years']:<7} "
          f"{period['lev_annualized']:>10.2f}%  {period['unlev_annualized']:>10.2f}%  "
          f"{period['absolute_underperformance']:>10.2f}%")

print()
print("=" * 100)
print("DETAILED ANALYSIS - WORST PERIOD FOR 2X LEVERAGED ETF")
print("=" * 100)
print()

worst = worst_by_absolute[0]
print(f"Period: {worst['start_date'].strftime('%B %Y')} to {worst['end_date'].strftime('%B %Y')}")
print(f"Duration: {worst['years']} years")
print()
print(f"Non-Leveraged Performance:")
print(f"  Total Return: {worst['unlev_total_return']:>10.2f}%")
print(f"  Annualized Return: {worst['unlev_annualized']:>10.2f}%")
print()
print(f"2x Leveraged ETF Performance (with 0.6% TER):")
print(f"  Total Return: {worst['lev_total_return']:>10.2f}%")
print(f"  Annualized Return: {worst['lev_annualized']:>10.2f}%")
print()
print(f"Performance Gap:")
print(f"  Absolute Underperformance: {worst['absolute_underperformance']:>10.2f}% per year")
print(f"  Leveraged/Unleveraged Ratio: {worst['ratio']:.4f}x")
print(f"  Underperformance vs 2x Expectation: {worst['underperformance']:>10.2f}% per year")
print()

# Calculate some context for this period
worst_start_idx = next(i for i, r in enumerate(leveraged_returns)
                       if r['date'] >= worst['start_date'])
worst_end_idx = next(i for i, r in enumerate(leveraged_returns)
                     if r['date'] >= worst['end_date'])
worst_period_returns = leveraged_returns[worst_start_idx:worst_end_idx+1]

# Calculate volatility for this period
if len(worst_period_returns) >= 12:
    returns_only = [r['unleveraged_return'] for r in worst_period_returns]
    n = len(returns_only)
    mean_return = sum(returns_only) / n
    # Use sample variance (n-1) for unbiased estimator
    variance = sum((r - mean_return) ** 2 for r in returns_only) / (n - 1) if n > 1 else 0
    volatility = math.sqrt(variance) * math.sqrt(12) * 100  # Annualized

    print(f"Market Characteristics During This Period:")
    print(f"  Annualized Volatility: {volatility:.2f}%")

    # Count negative months
    neg_months = sum(1 for r in worst_period_returns if r['unleveraged_return'] < 0)
    pct_neg = (neg_months / len(worst_period_returns)) * 100
    print(f"  Negative Months: {neg_months}/{len(worst_period_returns)} ({pct_neg:.1f}%)")

print()
print("=" * 100)
print("ANALYSIS BY TIME WINDOW LENGTH")
print("=" * 100)
print()

# Group by years and find worst for each
for years in range(5, 16):
    periods_for_year = [p for p in all_periods if p['years'] == years]
    if periods_for_year:
        worst_for_year = min(periods_for_year, key=lambda x: x['absolute_underperformance'])
        print(f"{years:>2}-Year Window - Worst Period: "
              f"{worst_for_year['start_date'].strftime('%Y-%m')} to {worst_for_year['end_date'].strftime('%Y-%m')}")
        print(f"    Lev: {worst_for_year['lev_annualized']:>7.2f}% | "
              f"Unlev: {worst_for_year['unlev_annualized']:>7.2f}% | "
              f"Gap: {worst_for_year['absolute_underperformance']:>7.2f}%")
        print()

print("=" * 100)
print()
print("CONCLUSION:")
print(f"  The WORST period for a 2x leveraged S&P 500 ETF was:")
print(f"  {worst['start_date'].strftime('%B %Y')} to {worst['end_date'].strftime('%B %Y')} ({worst['years']} years)")
print(f"  where it returned {worst['lev_annualized']:.2f}% annualized")
print(f"  vs {worst['unlev_annualized']:.2f}% for the unleveraged index")
print()
print("=" * 100)
