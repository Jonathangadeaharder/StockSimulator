#!/usr/bin/env python3
"""
Clean comparison of $500/month investment across THREE strategies:
1. $500/month into 2x Leveraged ETF
2. $500/month into Non-Leveraged index
3. Lump-sum equivalent into 2x Leveraged ETF (for reference)

Show results for 5, 10, 15 year periods across all indices
"""

import csv
from datetime import datetime, timedelta

class MonthlyInvestmentComparison:
    def __init__(self, name, filename, date_col='Date', price_col='Close', start_year=1950):
        self.name = name
        self.filename = filename
        self.date_col = date_col
        self.price_col = price_col
        self.start_year = start_year

    def read_data(self):
        """Read index data"""
        data = []
        with open(self.filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    date = datetime.strptime(row[self.date_col], '%Y-%m-%d')
                    if date.year < self.start_year:
                        continue
                    price = float(row[self.price_col]) if row[self.price_col] else None
                    if price and price > 0:
                        data.append({'date': date, 'close': price})
                except (ValueError, KeyError):
                    continue
        return data

    def calculate_returns(self, data, avg_dividend_yield=0.02):
        """Calculate daily returns"""
        returns = []
        daily_dividend = avg_dividend_yield / 252
        for i in range(1, len(data)):
            price_return = (data[i]['close'] - data[i-1]['close']) / data[i-1]['close']
            total_return = price_return + daily_dividend
            returns.append({
                'date': data[i]['date'],
                'return': total_return
            })
        return returns

    def simulate_leveraged_etf(self, returns, leverage=2.0, ter=0.006):
        """Simulate leveraged ETF"""
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

    def compare_monthly_strategies(self, returns, monthly_amount, years):
        """
        Compare three strategies:
        1. $500/month into 2x leveraged
        2. $500/month into non-leveraged
        3. Lump-sum (total) into 2x leveraged (reference)
        """
        results = []
        total_investment = monthly_amount * years * 12
        months_needed = years * 12

        for start_idx in range(0, len(returns), 21):
            end_date = returns[start_idx]['date'] + timedelta(days=years*365.25)

            end_idx = None
            for i in range(start_idx, len(returns)):
                if returns[i]['date'] >= end_date:
                    end_idx = i
                    break

            if end_idx is None or end_idx >= len(returns):
                break

            # Strategy 1: $500/month into 2x leveraged
            monthly_lev_shares = 0.0
            monthly_lev_price = 100.0
            monthly_lev_invested = 0

            # Strategy 2: $500/month into non-leveraged
            monthly_unlev_shares = 0.0
            monthly_unlev_price = 100.0
            monthly_unlev_invested = 0

            # Strategy 3: Lump-sum into 2x leveraged (reference)
            lump_lev_cumulative = 1.0

            month = 0

            for i in range(start_idx, end_idx):
                ret = returns[i]

                # Update prices
                monthly_lev_price *= (1 + ret['lev_return'])
                monthly_unlev_price *= (1 + ret['unlev_return'])
                lump_lev_cumulative *= (1 + ret['lev_return'])

                # Monthly investments
                days_since_start = (ret['date'] - returns[start_idx]['date']).days
                expected_month = days_since_start / 30.44
                if int(expected_month) > month and month < months_needed:
                    month = int(expected_month)
                    # Buy shares for monthly strategies
                    monthly_lev_shares += monthly_amount / monthly_lev_price
                    monthly_unlev_shares += monthly_amount / monthly_unlev_price
                    monthly_lev_invested += monthly_amount
                    monthly_unlev_invested += monthly_amount

            # Final values
            monthly_lev_final = monthly_lev_shares * monthly_lev_price
            monthly_unlev_final = monthly_unlev_shares * monthly_unlev_price
            lump_lev_final = total_investment * lump_lev_cumulative

            actual_years = (returns[end_idx - 1]['date'] - returns[start_idx]['date']).days / 365.25

            # Annualized returns
            monthly_lev_ann = ((monthly_lev_final / monthly_lev_invested) ** (1/actual_years) - 1) * 100 if monthly_lev_invested > 0 else 0
            monthly_unlev_ann = ((monthly_unlev_final / monthly_unlev_invested) ** (1/actual_years) - 1) * 100 if monthly_unlev_invested > 0 else 0
            lump_lev_ann = ((lump_lev_cumulative) ** (1/actual_years) - 1) * 100

            # Determine winner
            values = [
                ('Monthly_2x_Lev', monthly_lev_final),
                ('Monthly_Unlev', monthly_unlev_final),
                ('Lump_2x_Lev', lump_lev_final)
            ]
            values.sort(key=lambda x: x[1], reverse=True)

            results.append({
                'start_date': returns[start_idx]['date'],
                'end_date': returns[end_idx - 1]['date'],
                'years': actual_years,
                'monthly_lev_final': monthly_lev_final,
                'monthly_unlev_final': monthly_unlev_final,
                'lump_lev_final': lump_lev_final,
                'monthly_lev_ann': monthly_lev_ann,
                'monthly_unlev_ann': monthly_unlev_ann,
                'lump_lev_ann': lump_lev_ann,
                'total_invested': monthly_lev_invested,
                'winner': values[0][0],
                'second': values[1][0],
                'third': values[2][0]
            })

        return results

    def calculate_percentiles(self, values, percentiles=[10, 25, 50, 75, 90]):
        """Calculate percentiles from a list of values"""
        sorted_values = sorted(values)
        n = len(sorted_values)
        result = {}
        for p in percentiles:
            idx = int(n * p / 100)
            if idx >= n:
                idx = n - 1
            result[p] = sorted_values[idx]
        return result

    def analyze(self, timeframes=[5, 10, 15], monthly_amount=500):
        """Run analysis"""
        print("=" * 120)
        print(f"$500/MONTH INVESTMENT COMPARISON: {self.name}")
        print("=" * 120)
        print()

        data = self.read_data()
        daily_returns = self.calculate_returns(data)
        leveraged_returns = self.simulate_leveraged_etf(daily_returns)

        summary = {}

        for years in timeframes:
            total_investment = monthly_amount * years * 12

            print(f"{'='*120}")
            print(f"{years}-YEAR PERIOD (Total Investment: ${total_investment:,})")
            print(f"{'='*120}")
            print()

            results = self.compare_monthly_strategies(leveraged_returns, monthly_amount, years)

            if not results:
                print(f"Not enough data\n")
                continue

            # Statistics
            monthly_lev_wins = sum(1 for r in results if r['winner'] == 'Monthly_2x_Lev')
            monthly_unlev_wins = sum(1 for r in results if r['winner'] == 'Monthly_Unlev')
            lump_lev_wins = sum(1 for r in results if r['winner'] == 'Lump_2x_Lev')

            print(f"Win Statistics ({len(results):,} periods analyzed):")
            print(f"  $500/month → 2x Leveraged: {monthly_lev_wins:>4} wins ({100*monthly_lev_wins/len(results):>5.1f}%)")
            print(f"  $500/month → Non-Leveraged: {monthly_unlev_wins:>4} wins ({100*monthly_unlev_wins/len(results):>5.1f}%)")
            print(f"  Lump-Sum → 2x Leveraged:  {lump_lev_wins:>4} wins ({100*lump_lev_wins/len(results):>5.1f}%) [reference]")
            print()

            # Percentile analysis
            monthly_lev_returns = [r['monthly_lev_ann'] for r in results]
            monthly_unlev_returns = [r['monthly_unlev_ann'] for r in results]
            lump_lev_returns = [r['lump_lev_ann'] for r in results]

            monthly_lev_percentiles = self.calculate_percentiles(monthly_lev_returns)
            monthly_unlev_percentiles = self.calculate_percentiles(monthly_unlev_returns)
            lump_lev_percentiles = self.calculate_percentiles(lump_lev_returns)

            print("-" * 120)
            print("RETURN PERCENTILES (Annualized %)")
            print("-" * 120)
            print(f"{'Strategy':<30} {'10th %':<12} {'25th %':<12} {'50th %':<12} {'75th %':<12} {'90th %':<12}")
            print("-" * 120)
            print(f"{'Monthly 2x Leveraged':<30} {monthly_lev_percentiles[10]:>10.2f}% {monthly_lev_percentiles[25]:>10.2f}% {monthly_lev_percentiles[50]:>10.2f}% {monthly_lev_percentiles[75]:>10.2f}% {monthly_lev_percentiles[90]:>10.2f}%")
            print(f"{'Monthly Non-Leveraged':<30} {monthly_unlev_percentiles[10]:>10.2f}% {monthly_unlev_percentiles[25]:>10.2f}% {monthly_unlev_percentiles[50]:>10.2f}% {monthly_unlev_percentiles[75]:>10.2f}% {monthly_unlev_percentiles[90]:>10.2f}%")
            print(f"{'Lump-Sum 2x Leveraged':<30} {lump_lev_percentiles[10]:>10.2f}% {lump_lev_percentiles[25]:>10.2f}% {lump_lev_percentiles[50]:>10.2f}% {lump_lev_percentiles[75]:>10.2f}% {lump_lev_percentiles[90]:>10.2f}%")
            print()

            # Final value percentiles
            monthly_lev_values = [r['monthly_lev_final'] for r in results]
            monthly_unlev_values = [r['monthly_unlev_final'] for r in results]
            lump_lev_values = [r['lump_lev_final'] for r in results]

            monthly_lev_val_pct = self.calculate_percentiles(monthly_lev_values)
            monthly_unlev_val_pct = self.calculate_percentiles(monthly_unlev_values)
            lump_lev_val_pct = self.calculate_percentiles(lump_lev_values)

            print("-" * 120)
            print(f"FINAL VALUE PERCENTILES (from ${total_investment:,} invested)")
            print("-" * 120)
            print(f"{'Strategy':<30} {'10th %':<15} {'25th %':<15} {'50th %':<15} {'75th %':<15} {'90th %':<15}")
            print("-" * 120)
            print(f"{'Monthly 2x Leveraged':<30} ${monthly_lev_val_pct[10]:>13,.0f} ${monthly_lev_val_pct[25]:>13,.0f} ${monthly_lev_val_pct[50]:>13,.0f} ${monthly_lev_val_pct[75]:>13,.0f} ${monthly_lev_val_pct[90]:>13,.0f}")
            print(f"{'Monthly Non-Leveraged':<30} ${monthly_unlev_val_pct[10]:>13,.0f} ${monthly_unlev_val_pct[25]:>13,.0f} ${monthly_unlev_val_pct[50]:>13,.0f} ${monthly_unlev_val_pct[75]:>13,.0f} ${monthly_unlev_val_pct[90]:>13,.0f}")
            print(f"{'Lump-Sum 2x Leveraged':<30} ${lump_lev_val_pct[10]:>13,.0f} ${lump_lev_val_pct[25]:>13,.0f} ${lump_lev_val_pct[50]:>13,.0f} ${lump_lev_val_pct[75]:>13,.0f} ${lump_lev_val_pct[90]:>13,.0f}")
            print()

            # Find worst for each strategy
            worst_monthly_lev = min(results, key=lambda x: x['monthly_lev_ann'])
            worst_monthly_unlev = min(results, key=lambda x: x['monthly_unlev_ann'])
            worst_lump_lev = min(results, key=lambda x: x['lump_lev_ann'])

            # Find where monthly unleveraged beat both leveraged options
            unlev_beats_both = [r for r in results if r['winner'] == 'Monthly_Unlev']
            if unlev_beats_both:
                best_unlev_win = max(unlev_beats_both, key=lambda x: x['monthly_unlev_final'])
                print("-" * 120)
                print("BEST CASE WHERE NON-LEVERAGED WON (Beat both leveraged options)")
                print("-" * 120)
                print(f"Period: {best_unlev_win['start_date'].strftime('%Y-%m')} to {best_unlev_win['end_date'].strftime('%Y-%m')}")
                print()
                print(f"Final Values:")
                print(f"  Monthly Non-Leveraged: ${best_unlev_win['monthly_unlev_final']:>12,.0f} ({best_unlev_win['monthly_unlev_ann']:>7.2f}% ann.) ✅ BEST")
                print(f"  Monthly 2x Leveraged:  ${best_unlev_win['monthly_lev_final']:>12,.0f} ({best_unlev_win['monthly_lev_ann']:>7.2f}% ann.)")
                print(f"  Lump-Sum 2x Leveraged: ${best_unlev_win['lump_lev_final']:>12,.0f} ({best_unlev_win['lump_lev_ann']:>7.2f}% ann.)")
                print()

            print("-" * 120)
            print("WORST PERIOD FOR EACH STRATEGY")
            print("-" * 120)
            print()

            print(f"Worst for $500/month → 2x Leveraged:")
            print(f"  Period: {worst_monthly_lev['start_date'].strftime('%Y-%m')} to {worst_monthly_lev['end_date'].strftime('%Y-%m')}")
            print(f"  Final Value: ${worst_monthly_lev['monthly_lev_final']:,.0f} from ${worst_monthly_lev['total_invested']:,.0f} invested")
            print(f"  Annualized Return: {worst_monthly_lev['monthly_lev_ann']:.2f}%")
            print(f"  Ranking: {worst_monthly_lev['winner']} won, Monthly_2x_Lev was {['first', 'second', 'third'][[worst_monthly_lev['winner'], worst_monthly_lev['second'], worst_monthly_lev['third']].index('Monthly_2x_Lev')]}")
            print()

            print(f"Worst for $500/month → Non-Leveraged:")
            print(f"  Period: {worst_monthly_unlev['start_date'].strftime('%Y-%m')} to {worst_monthly_unlev['end_date'].strftime('%Y-%m')}")
            print(f"  Final Value: ${worst_monthly_unlev['monthly_unlev_final']:,.0f} from ${worst_monthly_unlev['total_invested']:,.0f} invested")
            print(f"  Annualized Return: {worst_monthly_unlev['monthly_unlev_ann']:.2f}%")
            print(f"  Ranking: {worst_monthly_unlev['winner']} won, Monthly_Unlev was {['first', 'second', 'third'][[worst_monthly_unlev['winner'], worst_monthly_unlev['second'], worst_monthly_unlev['third']].index('Monthly_Unlev')]}")
            print()

            print(f"Worst for Lump-Sum → 2x Leveraged [reference]:")
            print(f"  Period: {worst_lump_lev['start_date'].strftime('%Y-%m')} to {worst_lump_lev['end_date'].strftime('%Y-%m')}")
            print(f"  Final Value: ${worst_lump_lev['lump_lev_final']:,.0f} from ${total_investment:,.0f} invested")
            print(f"  Annualized Return: {worst_lump_lev['lump_lev_ann']:.2f}%")
            print()

            summary[years] = {
                'total_periods': len(results),
                'monthly_lev_wins': monthly_lev_wins,
                'monthly_unlev_wins': monthly_unlev_wins,
                'lump_lev_wins': lump_lev_wins,
                'worst_monthly_lev': worst_monthly_lev,
                'worst_monthly_unlev': worst_monthly_unlev,
                'worst_lump_lev': worst_lump_lev,
                'monthly_lev_percentiles': monthly_lev_percentiles,
                'monthly_unlev_percentiles': monthly_unlev_percentiles,
                'lump_lev_percentiles': lump_lev_percentiles,
                'monthly_lev_val_pct': monthly_lev_val_pct,
                'monthly_unlev_val_pct': monthly_unlev_val_pct,
                'lump_lev_val_pct': lump_lev_val_pct
            }

        return summary


# Analyze all indices
indices = [
    MonthlyInvestmentComparison("S&P 500", "sp500_stooq_daily.csv", 'Date', 'Close', 1950),
    MonthlyInvestmentComparison("DJIA", "djia_stooq_daily.csv", 'Date', 'Close', 1950),
    MonthlyInvestmentComparison("NASDAQ", "nasdaq_fred.csv", 'observation_date', 'NASDAQCOM', 1971),
    MonthlyInvestmentComparison("Nikkei 225", "nikkei225_fred.csv", 'observation_date', 'NIKKEI225', 1950),
]

print()
print("╔" + "=" * 118 + "╗")
print("║" + " " * 35 + "$500/MONTH INVESTMENT COMPARISON" + " " * 51 + "║")
print("║" + " " * 20 + "Monthly 2x Leverage vs Monthly Non-Leveraged vs Lump-Sum 2x" + " " * 38 + "║")
print("╚" + "=" * 118 + "╝")
print()

all_results = {}

for idx_analyzer in indices:
    try:
        results = idx_analyzer.analyze(timeframes=[5, 10, 15], monthly_amount=500)
        all_results[idx_analyzer.name] = results
        print()
    except Exception as e:
        print(f"Error analyzing {idx_analyzer.name}: {e}\n")

# Summary table
print()
print("=" * 120)
print("SUMMARY: WIN RATES FOR $500/MONTH INVESTMENT")
print("=" * 120)
print()

for years in [5, 10, 15]:
    print(f"{years}-YEAR PERIODS:")
    print("-" * 120)
    print(f"{'Index':<20} {'Monthly 2x Lev':<25} {'Monthly Non-Lev':<25} {'Lump 2x Lev (ref)':<25}")
    print("-" * 120)

    for idx_name, results in all_results.items():
        if years in results:
            r = results[years]
            total = r['total_periods']
            print(f"{idx_name:<20} {r['monthly_lev_wins']:>6} ({100*r['monthly_lev_wins']/total:>5.1f}%)           "
                  f"{r['monthly_unlev_wins']:>6} ({100*r['monthly_unlev_wins']/total:>5.1f}%)           "
                  f"{r['lump_lev_wins']:>6} ({100*r['lump_lev_wins']/total:>5.1f}%)")
    print()

print("=" * 120)
print()
print()

# Percentile Summary Tables
print("=" * 120)
print("PERCENTILE SUMMARY: ANNUALIZED RETURNS")
print("=" * 120)
print()

for years in [5, 10, 15]:
    print(f"{years}-YEAR PERIODS - Annualized Return Percentiles:")
    print("-" * 120)

    for idx_name, results in all_results.items():
        if years in results:
            r = results[years]
            print(f"\n{idx_name}:")
            print(f"{'Strategy':<30} {'10th %':<12} {'25th %':<12} {'50th %':<12} {'75th %':<12} {'90th %':<12}")
            print("-" * 120)

            ml = r['monthly_lev_percentiles']
            mu = r['monthly_unlev_percentiles']
            ll = r['lump_lev_percentiles']

            print(f"{'Monthly 2x Leveraged':<30} {ml[10]:>10.2f}% {ml[25]:>10.2f}% {ml[50]:>10.2f}% {ml[75]:>10.2f}% {ml[90]:>10.2f}%")
            print(f"{'Monthly Non-Leveraged':<30} {mu[10]:>10.2f}% {mu[25]:>10.2f}% {mu[50]:>10.2f}% {mu[75]:>10.2f}% {mu[90]:>10.2f}%")
            print(f"{'Lump-Sum 2x Leveraged':<30} {ll[10]:>10.2f}% {ll[25]:>10.2f}% {ll[50]:>10.2f}% {ll[75]:>10.2f}% {ll[90]:>10.2f}%")
    print()

print("=" * 120)
print()
print()

# Final Value Percentiles
print("=" * 120)
print("PERCENTILE SUMMARY: FINAL VALUES")
print("=" * 120)
print()

for years in [5, 10, 15]:
    total_investment = 500 * years * 12
    print(f"{years}-YEAR PERIODS - Final Value Percentiles (from ${total_investment:,} invested):")
    print("-" * 120)

    for idx_name, results in all_results.items():
        if years in results:
            r = results[years]
            print(f"\n{idx_name}:")
            print(f"{'Strategy':<30} {'10th %':<15} {'25th %':<15} {'50th %':<15} {'75th %':<15} {'90th %':<15}")
            print("-" * 120)

            ml = r['monthly_lev_val_pct']
            mu = r['monthly_unlev_val_pct']
            ll = r['lump_lev_val_pct']

            print(f"{'Monthly 2x Leveraged':<30} ${ml[10]:>13,.0f} ${ml[25]:>13,.0f} ${ml[50]:>13,.0f} ${ml[75]:>13,.0f} ${ml[90]:>13,.0f}")
            print(f"{'Monthly Non-Leveraged':<30} ${mu[10]:>13,.0f} ${mu[25]:>13,.0f} ${mu[50]:>13,.0f} ${mu[75]:>13,.0f} ${mu[90]:>13,.0f}")
            print(f"{'Lump-Sum 2x Leveraged':<30} ${ll[10]:>13,.0f} ${ll[25]:>13,.0f} ${ll[50]:>13,.0f} ${ll[75]:>13,.0f} ${ll[90]:>13,.0f}")
    print()

print("=" * 120)
