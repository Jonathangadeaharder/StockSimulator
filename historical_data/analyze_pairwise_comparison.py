#!/usr/bin/env python3
"""
Pairwise comparisons of investment strategies:
1. Lump-Sum 2x Leveraged vs Monthly Non-Leveraged (same total $)
2. Monthly 2x Leveraged vs Monthly Non-Leveraged (same monthly $)

Shows head-to-head performance without the three-way complexity
"""

import csv
from datetime import datetime, timedelta

class PairwiseComparison:
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

    def compare_lumpsum_vs_monthly_unlev(self, returns, monthly_amount, years):
        """
        Compare:
        - Lump-sum (total) into 2x leveraged
        - $500/month into non-leveraged
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

            # Strategy 1: Lump-sum into 2x leveraged
            lump_lev_cumulative = 1.0

            # Strategy 2: $500/month into non-leveraged
            monthly_unlev_shares = 0.0
            monthly_unlev_price = 100.0
            monthly_unlev_invested = 0

            month = 0

            for i in range(start_idx, end_idx):
                ret = returns[i]

                # Lump-sum compounds
                lump_lev_cumulative *= (1 + ret['lev_return'])

                # Monthly non-leveraged
                monthly_unlev_price *= (1 + ret['unlev_return'])

                # Monthly investments
                days_since_start = (ret['date'] - returns[start_idx]['date']).days
                expected_month = days_since_start / 30.44
                if int(expected_month) > month and month < months_needed:
                    month = int(expected_month)
                    monthly_unlev_shares += monthly_amount / monthly_unlev_price
                    monthly_unlev_invested += monthly_amount

            # Final values
            lump_lev_final = total_investment * lump_lev_cumulative
            monthly_unlev_final = monthly_unlev_shares * monthly_unlev_price

            actual_years = (returns[end_idx]['date'] - returns[start_idx]['date']).days / 365.25

            # Annualized returns
            lump_lev_ann = ((lump_lev_cumulative) ** (1/actual_years) - 1) * 100
            monthly_unlev_ann = ((monthly_unlev_final / monthly_unlev_invested) ** (1/actual_years) - 1) * 100 if monthly_unlev_invested > 0 else 0

            results.append({
                'start_date': returns[start_idx]['date'],
                'end_date': returns[end_idx]['date'],
                'years': actual_years,
                'lump_lev_final': lump_lev_final,
                'monthly_unlev_final': monthly_unlev_final,
                'lump_lev_ann': lump_lev_ann,
                'monthly_unlev_ann': monthly_unlev_ann,
                'gap': lump_lev_ann - monthly_unlev_ann,
                'lump_wins': lump_lev_final > monthly_unlev_final,
                'total_invested': total_investment
            })

        return results

    def compare_monthly_2x_vs_monthly_unlev(self, returns, monthly_amount, years):
        """
        Compare:
        - $500/month into 2x leveraged
        - $500/month into non-leveraged
        """
        results = []
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

            month = 0

            for i in range(start_idx, end_idx):
                ret = returns[i]

                # Update prices
                monthly_lev_price *= (1 + ret['lev_return'])
                monthly_unlev_price *= (1 + ret['unlev_return'])

                # Monthly investments
                days_since_start = (ret['date'] - returns[start_idx]['date']).days
                expected_month = days_since_start / 30.44
                if int(expected_month) > month and month < months_needed:
                    month = int(expected_month)
                    monthly_lev_shares += monthly_amount / monthly_lev_price
                    monthly_unlev_shares += monthly_amount / monthly_unlev_price
                    monthly_lev_invested += monthly_amount
                    monthly_unlev_invested += monthly_amount

            # Final values
            monthly_lev_final = monthly_lev_shares * monthly_lev_price
            monthly_unlev_final = monthly_unlev_shares * monthly_unlev_price

            actual_years = (returns[end_idx]['date'] - returns[start_idx]['date']).days / 365.25

            # Annualized returns
            monthly_lev_ann = ((monthly_lev_final / monthly_lev_invested) ** (1/actual_years) - 1) * 100 if monthly_lev_invested > 0 else 0
            monthly_unlev_ann = ((monthly_unlev_final / monthly_unlev_invested) ** (1/actual_years) - 1) * 100 if monthly_unlev_invested > 0 else 0

            results.append({
                'start_date': returns[start_idx]['date'],
                'end_date': returns[end_idx]['date'],
                'years': actual_years,
                'monthly_lev_final': monthly_lev_final,
                'monthly_unlev_final': monthly_unlev_final,
                'monthly_lev_ann': monthly_lev_ann,
                'monthly_unlev_ann': monthly_unlev_ann,
                'gap': monthly_lev_ann - monthly_unlev_ann,
                'lev_wins': monthly_lev_final > monthly_unlev_final,
                'total_invested': monthly_lev_invested
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
        """Run pairwise analysis"""
        print("=" * 120)
        print(f"PAIRWISE COMPARISON ANALYSIS: {self.name}")
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

            # Comparison 1: Lump-Sum 2x vs Monthly Non-Lev
            print("─" * 120)
            print(f"COMPARISON 1: Lump-Sum ${total_investment:,} (2x Leveraged) vs Monthly ${monthly_amount} (Non-Leveraged)")
            print("─" * 120)
            print()

            lump_vs_unlev = self.compare_lumpsum_vs_monthly_unlev(leveraged_returns, monthly_amount, years)

            if lump_vs_unlev:
                lump_wins = sum(1 for r in lump_vs_unlev if r['lump_wins'])
                win_rate = 100 * lump_wins / len(lump_vs_unlev)

                print(f"Win Statistics ({len(lump_vs_unlev):,} periods analyzed):")
                print(f"  Lump-Sum 2x Leveraged wins: {lump_wins:>6} ({win_rate:>5.1f}%)")
                print(f"  Monthly Non-Leveraged wins:  {len(lump_vs_unlev)-lump_wins:>6} ({100-win_rate:>5.1f}%)")
                print()

                # Percentiles
                lump_returns = [r['lump_lev_ann'] for r in lump_vs_unlev]
                unlev_returns = [r['monthly_unlev_ann'] for r in lump_vs_unlev]
                gaps = [r['gap'] for r in lump_vs_unlev]

                lump_pct = self.calculate_percentiles(lump_returns)
                unlev_pct = self.calculate_percentiles(unlev_returns)
                gap_pct = self.calculate_percentiles(gaps)

                print("Return Percentiles (Annualized %):")
                print(f"{'Strategy':<30} {'10th %':<12} {'25th %':<12} {'50th %':<12} {'75th %':<12} {'90th %':<12}")
                print("-" * 120)
                print(f"{'Lump-Sum 2x Leveraged':<30} {lump_pct[10]:>10.2f}% {lump_pct[25]:>10.2f}% {lump_pct[50]:>10.2f}% {lump_pct[75]:>10.2f}% {lump_pct[90]:>10.2f}%")
                print(f"{'Monthly Non-Leveraged':<30} {unlev_pct[10]:>10.2f}% {unlev_pct[25]:>10.2f}% {unlev_pct[50]:>10.2f}% {unlev_pct[75]:>10.2f}% {unlev_pct[90]:>10.2f}%")
                print(f"{'Gap (Lump 2x - Non-Lev)':<30} {gap_pct[10]:>10.2f}% {gap_pct[25]:>10.2f}% {gap_pct[50]:>10.2f}% {gap_pct[75]:>10.2f}% {gap_pct[90]:>10.2f}%")
                print()

                # Final values
                lump_values = [r['lump_lev_final'] for r in lump_vs_unlev]
                unlev_values = [r['monthly_unlev_final'] for r in lump_vs_unlev]

                lump_val_pct = self.calculate_percentiles(lump_values)
                unlev_val_pct = self.calculate_percentiles(unlev_values)

                print(f"Final Value Percentiles (from ${total_investment:,} invested):")
                print(f"{'Strategy':<30} {'10th %':<15} {'25th %':<15} {'50th %':<15} {'75th %':<15} {'90th %':<15}")
                print("-" * 120)
                print(f"{'Lump-Sum 2x Leveraged':<30} ${lump_val_pct[10]:>13,.0f} ${lump_val_pct[25]:>13,.0f} ${lump_val_pct[50]:>13,.0f} ${lump_val_pct[75]:>13,.0f} ${lump_val_pct[90]:>13,.0f}")
                print(f"{'Monthly Non-Leveraged':<30} ${unlev_val_pct[10]:>13,.0f} ${unlev_val_pct[25]:>13,.0f} ${unlev_val_pct[50]:>13,.0f} ${unlev_val_pct[75]:>13,.0f} ${unlev_val_pct[90]:>13,.0f}")
                print()

                # Worst cases
                worst_gap = min(lump_vs_unlev, key=lambda x: x['gap'])
                print(f"Worst Period for Lump-Sum 2x (biggest underperformance):")
                print(f"  Period: {worst_gap['start_date'].strftime('%Y-%m')} to {worst_gap['end_date'].strftime('%Y-%m')}")
                print(f"  Lump-Sum 2x: {worst_gap['lump_lev_ann']:>6.2f}% ann. (${worst_gap['lump_lev_final']:>12,.0f})")
                print(f"  Monthly Non-Lev: {worst_gap['monthly_unlev_ann']:>6.2f}% ann. (${worst_gap['monthly_unlev_final']:>12,.0f})")
                print(f"  Gap: {worst_gap['gap']:>6.2f}% per year")
                print()

                summary[f"{years}_lump_vs_unlev"] = {
                    'win_rate': win_rate,
                    'lump_pct': lump_pct,
                    'unlev_pct': unlev_pct,
                    'gap_pct': gap_pct,
                    'worst_gap': worst_gap
                }

            print()
            print("─" * 120)
            print(f"COMPARISON 2: Monthly ${monthly_amount} (2x Leveraged) vs Monthly ${monthly_amount} (Non-Leveraged)")
            print("─" * 120)
            print()

            monthly_2x_vs_unlev = self.compare_monthly_2x_vs_monthly_unlev(leveraged_returns, monthly_amount, years)

            if monthly_2x_vs_unlev:
                lev_wins = sum(1 for r in monthly_2x_vs_unlev if r['lev_wins'])
                win_rate = 100 * lev_wins / len(monthly_2x_vs_unlev)

                print(f"Win Statistics ({len(monthly_2x_vs_unlev):,} periods analyzed):")
                print(f"  Monthly 2x Leveraged wins:  {lev_wins:>6} ({win_rate:>5.1f}%)")
                print(f"  Monthly Non-Leveraged wins: {len(monthly_2x_vs_unlev)-lev_wins:>6} ({100-win_rate:>5.1f}%)")
                print()

                # Percentiles
                lev_returns = [r['monthly_lev_ann'] for r in monthly_2x_vs_unlev]
                unlev_returns = [r['monthly_unlev_ann'] for r in monthly_2x_vs_unlev]
                gaps = [r['gap'] for r in monthly_2x_vs_unlev]

                lev_pct = self.calculate_percentiles(lev_returns)
                unlev_pct = self.calculate_percentiles(unlev_returns)
                gap_pct = self.calculate_percentiles(gaps)

                print("Return Percentiles (Annualized %):")
                print(f"{'Strategy':<30} {'10th %':<12} {'25th %':<12} {'50th %':<12} {'75th %':<12} {'90th %':<12}")
                print("-" * 120)
                print(f"{'Monthly 2x Leveraged':<30} {lev_pct[10]:>10.2f}% {lev_pct[25]:>10.2f}% {lev_pct[50]:>10.2f}% {lev_pct[75]:>10.2f}% {lev_pct[90]:>10.2f}%")
                print(f"{'Monthly Non-Leveraged':<30} {unlev_pct[10]:>10.2f}% {unlev_pct[25]:>10.2f}% {unlev_pct[50]:>10.2f}% {unlev_pct[75]:>10.2f}% {unlev_pct[90]:>10.2f}%")
                print(f"{'Gap (Monthly 2x - Non-Lev)':<30} {gap_pct[10]:>10.2f}% {gap_pct[25]:>10.2f}% {gap_pct[50]:>10.2f}% {gap_pct[75]:>10.2f}% {gap_pct[90]:>10.2f}%")
                print()

                # Final values
                lev_values = [r['monthly_lev_final'] for r in monthly_2x_vs_unlev]
                unlev_values = [r['monthly_unlev_final'] for r in monthly_2x_vs_unlev]

                lev_val_pct = self.calculate_percentiles(lev_values)
                unlev_val_pct = self.calculate_percentiles(unlev_values)

                print(f"Final Value Percentiles (from ${total_investment:,} invested):")
                print(f"{'Strategy':<30} {'10th %':<15} {'25th %':<15} {'50th %':<15} {'75th %':<15} {'90th %':<15}")
                print("-" * 120)
                print(f"{'Monthly 2x Leveraged':<30} ${lev_val_pct[10]:>13,.0f} ${lev_val_pct[25]:>13,.0f} ${lev_val_pct[50]:>13,.0f} ${lev_val_pct[75]:>13,.0f} ${lev_val_pct[90]:>13,.0f}")
                print(f"{'Monthly Non-Leveraged':<30} ${unlev_val_pct[10]:>13,.0f} ${unlev_val_pct[25]:>13,.0f} ${unlev_val_pct[50]:>13,.0f} ${unlev_val_pct[75]:>13,.0f} ${unlev_val_pct[90]:>13,.0f}")
                print()

                # Worst cases
                worst_gap = min(monthly_2x_vs_unlev, key=lambda x: x['gap'])
                print(f"Worst Period for Monthly 2x (biggest underperformance):")
                print(f"  Period: {worst_gap['start_date'].strftime('%Y-%m')} to {worst_gap['end_date'].strftime('%Y-%m')}")
                print(f"  Monthly 2x: {worst_gap['monthly_lev_ann']:>6.2f}% ann. (${worst_gap['monthly_lev_final']:>12,.0f})")
                print(f"  Monthly Non-Lev: {worst_gap['monthly_unlev_ann']:>6.2f}% ann. (${worst_gap['monthly_unlev_final']:>12,.0f})")
                print(f"  Gap: {worst_gap['gap']:>6.2f}% per year")
                print()

                summary[f"{years}_monthly_vs_unlev"] = {
                    'win_rate': win_rate,
                    'lev_pct': lev_pct,
                    'unlev_pct': unlev_pct,
                    'gap_pct': gap_pct,
                    'worst_gap': worst_gap
                }

            print()

        return summary


# Analyze all indices
indices = [
    PairwiseComparison("S&P 500", "sp500_stooq_daily.csv", 'Date', 'Close', 1950),
    PairwiseComparison("DJIA", "djia_stooq_daily.csv", 'Date', 'Close', 1950),
    PairwiseComparison("NASDAQ", "nasdaq_fred.csv", 'observation_date', 'NASDAQCOM', 1971),
    PairwiseComparison("Nikkei 225", "nikkei225_fred.csv", 'observation_date', 'NIKKEI225', 1950),
]

print()
print("╔" + "=" * 118 + "╗")
print("║" + " " * 40 + "PAIRWISE COMPARISON ANALYSIS" + " " * 50 + "║")
print("║" + " " * 25 + "Head-to-Head: Leveraged vs Non-Leveraged Strategies" + " " * 42 + "║")
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

# Summary tables
print()
print("=" * 120)
print("SUMMARY: WIN RATES BY COMPARISON")
print("=" * 120)
print()

for comparison in ["lump_vs_unlev", "monthly_vs_unlev"]:
    if comparison == "lump_vs_unlev":
        print("COMPARISON 1: Lump-Sum 2x Leveraged vs Monthly Non-Leveraged")
    else:
        print("COMPARISON 2: Monthly 2x Leveraged vs Monthly Non-Leveraged")

    print("-" * 120)

    for years in [5, 10, 15]:
        print(f"\n{years}-YEAR PERIODS:")
        print(f"{'Index':<20} {'Leveraged Win Rate':<30} {'Non-Leveraged Win Rate':<30}")
        print("-" * 120)

        for idx_name, results in all_results.items():
            key = f"{years}_{comparison}"
            if key in results:
                r = results[key]
                lev_rate = r['win_rate']
                unlev_rate = 100 - lev_rate
                print(f"{idx_name:<20} {lev_rate:>8.1f}%                     {unlev_rate:>8.1f}%")

    print()
    print("=" * 120)
    print()

print("=" * 120)
