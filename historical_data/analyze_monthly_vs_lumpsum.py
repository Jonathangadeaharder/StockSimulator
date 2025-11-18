#!/usr/bin/env python3
# @structurelint:no-test
"""
Compare Monthly Investing ($500/month) vs Lump-Sum Investment
2x Leveraged ETF vs Unleveraged S&P 500
"""

import csv
from datetime import datetime, timedelta

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
            'price': curr['close']
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
            'unlev_return': ret['return'],
            'price': ret['price']
        })
    return leveraged_returns

def calculate_xirr(cash_flows, dates, guess=0.1):
    """
    Calculate XIRR (Extended Internal Rate of Return) using Newton-Raphson method.
    
    Args:
        cash_flows: List of cash flows (negative for outflows, positive for inflows)
        dates: List of dates corresponding to cash flows
        guess: Initial guess for the rate (default 0.1 = 10%)
    
    Returns:
        Annualized IRR as a decimal (e.g., 0.08 for 8%), or None if calculation fails
    """
    if len(cash_flows) != len(dates) or len(cash_flows) < 2:
        return None
    
    # Check if all cash flows are zero or same sign
    if abs(sum(cash_flows)) < 1e-6 or all(cf >= 0 for cf in cash_flows) or all(cf <= 0 for cf in cash_flows):
        return None
    
    # Sort by date
    sorted_pairs = sorted(zip(dates, cash_flows))
    dates = [d for d, _ in sorted_pairs]
    cash_flows = [cf for _, cf in sorted_pairs]
    
    base_date = dates[0]
    days_diff = [(d - base_date).days for d in dates]
    
    # Newton-Raphson method
    rate = guess
    max_iterations = 100
    tolerance = 1e-6
    
    for _ in range(max_iterations):
        # Calculate NPV and derivative
        npv = 0
        dnpv = 0
        
        for i, cf in enumerate(cash_flows):
            years = days_diff[i] / 365.25
            discount_factor = (1 + rate) ** years
            npv += cf / discount_factor
            dnpv -= cf * years / discount_factor / (1 + rate)
        
        # Check convergence
        if abs(npv) < tolerance:
            return rate
        
        # Update rate
        if abs(dnpv) < 1e-10:
            return None
        
        rate = rate - npv / dnpv
        
        # Prevent extreme values
        if rate < -0.99 or rate > 10:
            return None
    
    return None

def simulate_monthly_investing(returns, monthly_amount=500, years=5):
    """
    Simulate monthly investing strategy

    Returns a list of all possible periods with their outcomes
    """
    results = []

    # We need at least 'years' worth of data
    months_needed = years * 12

    # Step through possible start dates (monthly intervals)
    for start_idx in range(0, len(returns), 21):  # ~21 trading days per month

        # Check if we have enough data for this period
        end_date = returns[start_idx]['date'] + timedelta(days=years*365.25)

        # Find the end index
        end_idx = None
        for i in range(start_idx, len(returns)):
            if returns[i]['date'] >= end_date:
                end_idx = i
                break

        if end_idx is None or end_idx >= len(returns):
            break

        # Simulate monthly investments
        lev_shares = 0.0
        unlev_shares = 0.0
        lev_price = 100.0  # Start leveraged ETF at $100
        unlev_price = 100.0  # Start unleveraged at $100

        total_invested = 0
        month = 0
        
        # Track cash flows for IRR calculation
        contribution_dates = []
        contribution_amounts = []

        # Track monthly investment dates
        for i in range(start_idx, end_idx):
            ret = returns[i]

            # Update ETF prices
            lev_price *= (1 + ret['lev_return'])
            unlev_price *= (1 + ret['unlev_return'])

            # Check if it's time to invest (approximately monthly)
            days_since_start = (ret['date'] - returns[start_idx]['date']).days
            expected_month = days_since_start / 30.44  # Average days per month

            if int(expected_month) > month and month < months_needed:
                month = int(expected_month)

                # Buy shares with monthly_amount
                lev_shares += monthly_amount / lev_price
                unlev_shares += monthly_amount / unlev_price
                total_invested += monthly_amount
                
                # Track contribution for IRR calculation (negative = outflow)
                contribution_dates.append(ret['date'])
                contribution_amounts.append(-monthly_amount)

        # Calculate final values
        lev_final_value = lev_shares * lev_price
        unlev_final_value = unlev_shares * unlev_price

        # Calculate returns
        lev_total_return = ((lev_final_value / total_invested) - 1) * 100 if total_invested > 0 else 0
        unlev_total_return = ((unlev_final_value / total_invested) - 1) * 100 if total_invested > 0 else 0

        actual_years = (returns[end_idx]['date'] - returns[start_idx]['date']).days / 365.25

        # Calculate annualized return using XIRR (cash-flow aware)
        # Build cash flow series: negative contributions + positive final value
        lev_cash_flows = contribution_amounts + [lev_final_value]
        unlev_cash_flows = contribution_amounts + [unlev_final_value]
        cash_flow_dates = contribution_dates + [returns[end_idx]['date']]
        
        # Calculate XIRR and convert to percentage
        lev_irr = calculate_xirr(lev_cash_flows, cash_flow_dates)
        unlev_irr = calculate_xirr(unlev_cash_flows, cash_flow_dates)
        
        # Convert IRR to annualized percentage, fallback to NaN if calculation fails
        lev_annualized = (lev_irr * 100) if lev_irr is not None else float('nan')
        unlev_annualized = (unlev_irr * 100) if unlev_irr is not None else float('nan')
        if lev_irr is None or unlev_irr is None:
            print(f"Warning: XIRR calculation failed for period {returns[start_idx]['date']} to {returns[end_idx]['date']}")
        # Additional safety check for invalid years
        if actual_years <= 0:
            lev_annualized = 0
            unlev_annualized = 0

        results.append({
            'start_date': returns[start_idx]['date'],
            'end_date': returns[end_idx]['date'],
            'years': actual_years,
            'total_invested': total_invested,
            'lev_final_value': lev_final_value,
            'unlev_final_value': unlev_final_value,
            'lev_total_return': lev_total_return,
            'unlev_total_return': unlev_total_return,
            'lev_annualized': lev_annualized,
            'unlev_annualized': unlev_annualized,
            'absolute_gap': lev_annualized - unlev_annualized,
            'lev_shares': lev_shares,
            'unlev_shares': unlev_shares,
            'months_invested': month
        })

    return results

def simulate_lumpsum_investing(returns, initial_amount=30000, years=5):
    """
    Simulate lump-sum investing strategy for comparison
    $30,000 = $500/month * 60 months (5 years)
    """
    results = []

    days_needed = int(years * 252)

    for start_idx in range(0, len(returns) - days_needed, 21):
        end_idx = start_idx + days_needed

        if end_idx >= len(returns):
            break

        # Calculate cumulative returns
        lev_cumulative = 1.0
        unlev_cumulative = 1.0

        for i in range(start_idx, end_idx):
            ret = returns[i]
            lev_cumulative *= (1 + ret['lev_return'])
            unlev_cumulative *= (1 + ret['unlev_return'])

        lev_final_value = initial_amount * lev_cumulative
        unlev_final_value = initial_amount * unlev_cumulative

        lev_total_return = (lev_cumulative - 1) * 100
        unlev_total_return = (unlev_cumulative - 1) * 100

        actual_years = (returns[end_idx]['date'] - returns[start_idx]['date']).days / 365.25

        lev_annualized = ((lev_cumulative) ** (1/actual_years) - 1) * 100
        unlev_annualized = ((unlev_cumulative) ** (1/actual_years) - 1) * 100

        results.append({
            'start_date': returns[start_idx]['date'],
            'end_date': returns[end_idx]['date'],
            'years': actual_years,
            'total_invested': initial_amount,
            'lev_final_value': lev_final_value,
            'unlev_final_value': unlev_final_value,
            'lev_total_return': lev_total_return,
            'unlev_total_return': unlev_total_return,
            'lev_annualized': lev_annualized,
            'unlev_annualized': unlev_annualized,
            'absolute_gap': lev_annualized - unlev_annualized
        })

    return results

# Main analysis
print("=" * 100)
print("MONTHLY INVESTING ($500/MONTH) VS LUMP-SUM ANALYSIS")
print("2x Leveraged ETF vs Unleveraged S&P 500")
print("=" * 100)
print()

# Load data
print("Loading data...")
data = read_daily_data('sp500_stooq_daily.csv', start_year=1950)
print(f"  Period: {data[0]['date'].strftime('%Y-%m-%d')} to {data[-1]['date'].strftime('%Y-%m-%d')}")
print(f"  Trading days: {len(data):,}")
print()

daily_returns = calculate_daily_returns(data, avg_dividend_yield=0.02)
leveraged_returns = simulate_leveraged_etf_daily(daily_returns, leverage=2.0, ter=0.006)

# Analyze different timeframes
timeframes = [5, 10, 15]

for years in timeframes:
    print("=" * 100)
    print(f"{years}-YEAR INVESTMENT PERIOD")
    print("=" * 100)
    print()

    monthly_investment = 500
    total_monthly_investment = monthly_investment * years * 12

    print(f"Scenario A (Lump-Sum): ${total_monthly_investment:,} invested on Day 1")
    print(f"Scenario B (Monthly DCA): ${monthly_investment}/month for {years * 12} months (${total_monthly_investment:,} total)")
    print()

    # Run simulations
    print("Running simulations...")
    monthly_results = simulate_monthly_investing(leveraged_returns, monthly_amount=monthly_investment, years=years)
    lumpsum_results = simulate_lumpsum_investing(leveraged_returns, initial_amount=total_monthly_investment, years=years)

    print(f"  Monthly DCA: Analyzed {len(monthly_results):,} periods")
    print(f"  Lump-Sum: Analyzed {len(lumpsum_results):,} periods")
    print()

    # Find worst periods
    worst_monthly = sorted(monthly_results, key=lambda x: x['absolute_gap'])[0]
    worst_lumpsum = sorted(lumpsum_results, key=lambda x: x['absolute_gap'])[0]

    print("-" * 100)
    print("WORST PERIOD - MONTHLY DCA ($500/month)")
    print("-" * 100)
    print(f"Period: {worst_monthly['start_date'].strftime('%Y-%m-%d')} to {worst_monthly['end_date'].strftime('%Y-%m-%d')}")
    print(f"Total Invested: ${worst_monthly['total_invested']:,.0f} (over {worst_monthly['months_invested']} months)")
    print()
    print(f"Final Values:")
    print(f"  Unleveraged: ${worst_monthly['unlev_final_value']:,.2f} ({worst_monthly['unlev_total_return']:+.2f}% total return)")
    print(f"  2x Leveraged: ${worst_monthly['lev_final_value']:,.2f} ({worst_monthly['lev_total_return']:+.2f}% total return)")
    print(f"  Difference: ${worst_monthly['lev_final_value'] - worst_monthly['unlev_final_value']:+,.2f}")
    print()
    print(f"Annualized Returns:")
    print(f"  Unleveraged: {worst_monthly['unlev_annualized']:+.2f}%")
    print(f"  2x Leveraged: {worst_monthly['lev_annualized']:+.2f}%")
    print(f"  Gap: {worst_monthly['absolute_gap']:+.2f}% per year")
    print()

    print("-" * 100)
    print(f"WORST PERIOD - LUMP-SUM (${total_monthly_investment:,} on Day 1)")
    print("-" * 100)
    print(f"Period: {worst_lumpsum['start_date'].strftime('%Y-%m-%d')} to {worst_lumpsum['end_date'].strftime('%Y-%m-%d')}")
    print(f"Total Invested: ${worst_lumpsum['total_invested']:,.0f}")
    print()
    print(f"Final Values:")
    print(f"  Unleveraged: ${worst_lumpsum['unlev_final_value']:,.2f} ({worst_lumpsum['unlev_total_return']:+.2f}% total return)")
    print(f"  2x Leveraged: ${worst_lumpsum['lev_final_value']:,.2f} ({worst_lumpsum['lev_total_return']:+.2f}% total return)")
    print(f"  Difference: ${worst_lumpsum['lev_final_value'] - worst_lumpsum['unlev_final_value']:+,.2f}")
    print()
    print(f"Annualized Returns:")
    print(f"  Unleveraged: {worst_lumpsum['unlev_annualized']:+.2f}%")
    print(f"  2x Leveraged: {worst_lumpsum['lev_annualized']:+.2f}%")
    print(f"  Gap: {worst_lumpsum['absolute_gap']:+.2f}% per year")
    print()

    print("-" * 100)
    print("COMPARISON")
    print("-" * 100)

    monthly_worse = worst_monthly['absolute_gap']
    lumpsum_worse = worst_lumpsum['absolute_gap']

    print(f"Worst Gap - Monthly DCA: {monthly_worse:+.2f}% per year")
    print(f"Worst Gap - Lump-Sum: {lumpsum_worse:+.2f}% per year")
    print()

    if monthly_worse > lumpsum_worse:
        improvement = monthly_worse - lumpsum_worse
        print(f"✅ Monthly DCA is BETTER by {improvement:.2f}% per year in worst case!")
        print(f"   DCA reduces worst-case underperformance")
    else:
        worsening = lumpsum_worse - monthly_worse
        print(f"⚠️  Lump-Sum is better by {worsening:.2f}% per year in worst case")

    # Statistical summary
    monthly_underperform = [r for r in monthly_results if r['absolute_gap'] < 0]
    lumpsum_underperform = [r for r in lumpsum_results if r['absolute_gap'] < 0]

    print()
    print(f"Probability of Underperformance:")
    print(f"  Monthly DCA: {len(monthly_underperform)}/{len(monthly_results)} ({100*len(monthly_underperform)/len(monthly_results):.1f}%)")
    print(f"  Lump-Sum: {len(lumpsum_underperform)}/{len(lumpsum_results)} ({100*len(lumpsum_underperform)/len(lumpsum_results):.1f}%)")
    print()

    # Average gaps
    avg_monthly = sum(r['absolute_gap'] for r in monthly_results) / len(monthly_results)
    avg_lumpsum = sum(r['absolute_gap'] for r in lumpsum_results) / len(lumpsum_results)

    print(f"Average Gap:")
    print(f"  Monthly DCA: {avg_monthly:+.2f}% per year")
    print(f"  Lump-Sum: {avg_lumpsum:+.2f}% per year")
    print()

print("=" * 100)
print()
print("KEY INSIGHTS:")
print()
print("1. Monthly DCA changes the risk profile of leveraged ETFs")
print("2. Buying during crashes with monthly investments averages down costs")
print("3. DCA reduces timing risk - you're not trying to pick the perfect entry")
print("4. Worst-case scenarios may be less severe with regular contributions")
print()
print("=" * 100)
