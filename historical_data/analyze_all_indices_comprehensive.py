#!/usr/bin/env python3
"""
Comprehensive analysis of 2x Leveraged ETF performance across ALL major indices
Compares Monthly DCA vs Lump-Sum for each index
"""

import csv
from datetime import datetime, timedelta

class IndexAnalyzer:
    def __init__(self, name, filename, date_col='Date', price_col='Close', start_year=1950):
        self.name = name
        self.filename = filename
        self.date_col = date_col
        self.price_col = price_col
        self.start_year = start_year

    def read_data(self):
        """Read index data from CSV"""
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
            prev = data[i-1]
            curr = data[i]
            price_return = (curr['close'] - prev['close']) / prev['close']
            total_return = price_return + daily_dividend

            returns.append({
                'date': curr['date'],
                'return': total_return,
                'price': curr['close']
            })
        return returns

    def simulate_leveraged_etf(self, returns, leverage=2.0, ter=0.006):
        """Simulate 2x leveraged ETF"""
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

    def simulate_monthly_dca(self, returns, monthly_amount=500, years=5):
        """Simulate monthly DCA strategy"""
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

            lev_shares = 0.0
            unlev_shares = 0.0
            lev_price = 100.0
            unlev_price = 100.0
            total_invested = 0
            month = 0

            for i in range(start_idx, end_idx):
                ret = returns[i]

                lev_price *= (1 + ret['lev_return'])
                unlev_price *= (1 + ret['unlev_return'])

                days_since_start = (ret['date'] - returns[start_idx]['date']).days
                expected_month = days_since_start / 30.44

                target_month = int(expected_month)
                while month < target_month and month < months_needed:
                    month += 1
                    lev_shares += monthly_amount / lev_price
                    unlev_shares += monthly_amount / unlev_price
                    total_invested += monthly_amount

            lev_final_value = lev_shares * lev_price
            unlev_final_value = unlev_shares * unlev_price

            actual_years = (returns[end_idx]['date'] - returns[start_idx]['date']).days / 365.25

            lev_annualized = ((lev_final_value / total_invested) ** (1/actual_years) - 1) * 100 if total_invested > 0 and actual_years > 0 else 0
            unlev_annualized = ((unlev_final_value / total_invested) ** (1/actual_years) - 1) * 100 if total_invested > 0 and actual_years > 0 else 0

            results.append({
                'start_date': returns[start_idx]['date'],
                'end_date': returns[end_idx]['date'],
                'years': actual_years,
                'total_invested': total_invested,
                'lev_final_value': lev_final_value,
                'unlev_final_value': unlev_final_value,
                'lev_annualized': lev_annualized,
                'unlev_annualized': unlev_annualized,
                'absolute_gap': lev_annualized - unlev_annualized,
                'months_invested': month
            })

        return results

    def simulate_lumpsum(self, returns, initial_amount, years=5):
        """Simulate lump-sum strategy"""
        results = []
        days_needed = int(years * 252)

        for start_idx in range(0, len(returns) - days_needed, 21):
            end_idx = start_idx + days_needed

            if end_idx >= len(returns):
                break

            lev_cumulative = 1.0
            unlev_cumulative = 1.0

            for i in range(start_idx, end_idx):
                ret = returns[i]
                lev_cumulative *= (1 + ret['lev_return'])
                unlev_cumulative *= (1 + ret['unlev_return'])

            lev_final_value = initial_amount * lev_cumulative
            unlev_final_value = initial_amount * unlev_cumulative

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
                'lev_annualized': lev_annualized,
                'unlev_annualized': unlev_annualized,
                'absolute_gap': lev_annualized - unlev_annualized
            })

        return results

    def analyze(self, timeframes=[5, 10, 15], monthly_amount=500):
        """Run complete analysis for this index"""
        print("=" * 100)
        print(f"ANALYZING: {self.name}")
        print("=" * 100)
        print()

        # Load data
        print(f"Loading {self.name} data...")
        data = self.read_data()
        print(f"  Period: {data[0]['date'].strftime('%Y-%m-%d')} to {data[-1]['date'].strftime('%Y-%m-%d')}")
        print(f"  Trading days: {len(data):,}")
        print()

        # Calculate returns
        daily_returns = self.calculate_returns(data)
        leveraged_returns = self.simulate_leveraged_etf(daily_returns)
        print(f"  Simulated {len(leveraged_returns):,} days")
        print()

        results_summary = {}

        for years in timeframes:
            total_investment = monthly_amount * years * 12

            print(f"--- {years}-YEAR PERIOD ---")
            print()

            monthly_results = self.simulate_monthly_dca(leveraged_returns, monthly_amount=monthly_amount, years=years)
            lumpsum_results = self.simulate_lumpsum(leveraged_returns, initial_amount=total_investment, years=years)

            if not monthly_results or not lumpsum_results:
                print(f"  Not enough data for {years}-year analysis")
                print()
                continue

            worst_monthly = sorted(monthly_results, key=lambda x: x['absolute_gap'])[0]
            worst_lumpsum = sorted(lumpsum_results, key=lambda x: x['absolute_gap'])[0]

            monthly_underperform = [r for r in monthly_results if r['absolute_gap'] < 0]
            lumpsum_underperform = [r for r in lumpsum_results if r['absolute_gap'] < 0]

            print(f"Monthly DCA Worst: {worst_monthly['start_date'].strftime('%Y-%m')} to {worst_monthly['end_date'].strftime('%Y-%m')}")
            print(f"  Gap: {worst_monthly['absolute_gap']:+.2f}%/year | Final: ${worst_monthly['lev_final_value']:,.0f}")
            print()

            print(f"Lump-Sum Worst: {worst_lumpsum['start_date'].strftime('%Y-%m')} to {worst_lumpsum['end_date'].strftime('%Y-%m')}")
            print(f"  Gap: {worst_lumpsum['absolute_gap']:+.2f}%/year | Final: ${worst_lumpsum['lev_final_value']:,.0f}")
            print()

            dca_better = worst_monthly['absolute_gap'] > worst_lumpsum['absolute_gap']
            improvement = abs(worst_monthly['absolute_gap'] - worst_lumpsum['absolute_gap'])

            print(f"Winner: {'✅ DCA' if dca_better else 'Lump-Sum'} (by {improvement:.2f}%/year)")
            print(f"Risk: DCA {100*len(monthly_underperform)/len(monthly_results):.1f}% vs Lump {100*len(lumpsum_underperform)/len(lumpsum_results):.1f}%")
            print()

            results_summary[years] = {
                'dca_worst_gap': worst_monthly['absolute_gap'],
                'lumpsum_worst_gap': worst_lumpsum['absolute_gap'],
                'dca_better': dca_better,
                'improvement': improvement if dca_better else -improvement,
                'dca_risk': 100*len(monthly_underperform)/len(monthly_results),
                'lumpsum_risk': 100*len(lumpsum_underperform)/len(lumpsum_results)
            }

        return results_summary


# Define all indices to analyze
indices = [
    IndexAnalyzer("S&P 500", "sp500_stooq_daily.csv", date_col='Date', price_col='Close', start_year=1950),
    IndexAnalyzer("DJIA", "djia_stooq_daily.csv", date_col='Date', price_col='Close', start_year=1950),
    IndexAnalyzer("NASDAQ", "nasdaq_fred.csv", date_col='observation_date', price_col='NASDAQCOM', start_year=1971),
    IndexAnalyzer("Nikkei 225", "nikkei225_fred.csv", date_col='observation_date', price_col='NIKKEI225', start_year=1950),
]

# Run analysis
print()
print("╔" + "=" * 98 + "╗")
print("║" + " " * 25 + "COMPREHENSIVE MULTI-INDEX ANALYSIS" + " " * 39 + "║")
print("║" + " " * 30 + "Monthly DCA vs Lump-Sum" + " " * 45 + "║")
print("╚" + "=" * 98 + "╝")
print()

all_results = {}

for index_analyzer in indices:
    try:
        results = index_analyzer.analyze(timeframes=[5, 10, 15], monthly_amount=500)
        all_results[index_analyzer.name] = results
    except Exception as e:
        print(f"Error analyzing {index_analyzer.name}: {e}")
        print()

# Comparative summary
print()
print("=" * 100)
print("COMPARATIVE SUMMARY ACROSS ALL INDICES")
print("=" * 100)
print()

for years in [5, 10, 15]:
    print(f"{'='*100}")
    print(f"{years}-YEAR INVESTMENT PERIOD")
    print(f"{'='*100}")
    print()
    print(f"{'Index':<20} {'DCA Worst':<12} {'Lump Worst':<12} {'Winner':<12} {'Improvement':<12} {'DCA Risk':<10}")
    print("-" * 100)

    for index_name, results in all_results.items():
        if years in results:
            r = results[years]
            winner = "DCA" if r['dca_better'] else "Lump-Sum"
            print(f"{index_name:<20} {r['dca_worst_gap']:>10.2f}% {r['lumpsum_worst_gap']:>10.2f}% {winner:<12} {r['improvement']:>10.2f}% {r['dca_risk']:>8.1f}%")

    print()

print("=" * 100)
print()
print("KEY FINDINGS:")
print()
print("Compare how DCA vs Lump-Sum performs across different markets:")
print("  • US Large Cap (S&P 500, DJIA)")
print("  • US Tech (NASDAQ)")
print("  • International (Nikkei 225)")
print()
print("=" * 100)
