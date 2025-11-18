#!/usr/bin/env python3
# @structurelint:no-test
"""
Compare THREE strategies across all indices:
1. Monthly DCA with 2x leverage
2. Lump-sum with 2x leverage
3. Non-leveraged baseline (lump-sum unleveraged)

Show which performs best/worst in each scenario
"""

import csv
from datetime import datetime, timedelta

class ThreeWayComparison:
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
                'return': total_return,
                'price': data[i]['close']
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

    def three_way_comparison(self, returns, monthly_amount, years):
        """Compare all three strategies for given period"""
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

            # Strategy 1: Monthly DCA with 2x leverage
            dca_lev_shares = 0.0
            dca_lev_price = 100.0
            dca_invested = 0
            month = 0

            # Strategy 2: Lump-sum with 2x leverage
            lump_lev_cumulative = 1.0

            # Strategy 3: Non-leveraged lump-sum
            unlev_cumulative = 1.0

            for i in range(start_idx, end_idx):
                ret = returns[i]

                # Update DCA leveraged ETF price
                dca_lev_price *= (1 + ret['lev_return'])

                # Update lump-sum leveraged
                lump_lev_cumulative *= (1 + ret['lev_return'])

                # Update unleveraged
                unlev_cumulative *= (1 + ret['unlev_return'])

                # DCA monthly investment
                days_since_start = (ret['date'] - returns[start_idx]['date']).days
                expected_month = days_since_start / 30.44
                if int(expected_month) > month and month < months_needed:
                    month = int(expected_month)
                    dca_lev_shares += monthly_amount / dca_lev_price
                    dca_invested += monthly_amount

            # Final values
            dca_lev_final = dca_lev_shares * dca_lev_price
            lump_lev_final = total_investment * lump_lev_cumulative
            unlev_final = total_investment * unlev_cumulative

            actual_years = (returns[end_idx]['date'] - returns[start_idx]['date']).days / 365.25

            # Annualized returns
            dca_lev_ann = ((dca_lev_final / dca_invested) ** (1/actual_years) - 1) * 100 if dca_invested > 0 else 0
            lump_lev_ann = ((lump_lev_cumulative) ** (1/actual_years) - 1) * 100
            unlev_ann = ((unlev_cumulative) ** (1/actual_years) - 1) * 100

            # Rankings
            final_values = [
                ('DCA_Lev', dca_lev_final),
                ('Lump_Lev', lump_lev_final),
                ('Unlev', unlev_final)
            ]
            final_values.sort(key=lambda x: x[1], reverse=True)

            results.append({
                'start_date': returns[start_idx]['date'],
                'end_date': returns[end_idx]['date'],
                'years': actual_years,
                'dca_lev_final': dca_lev_final,
                'lump_lev_final': lump_lev_final,
                'unlev_final': unlev_final,
                'dca_lev_ann': dca_lev_ann,
                'lump_lev_ann': lump_lev_ann,
                'unlev_ann': unlev_ann,
                'total_invested': total_investment,
                'winner': final_values[0][0],
                'second': final_values[1][0],
                'third': final_values[2][0]
            })

        return results

    def analyze_comprehensive(self, timeframes=[5, 10, 15], monthly_amount=500):
        """Run comprehensive three-way analysis"""
        print("=" * 110)
        print(f"THREE-WAY COMPARISON: {self.name}")
        print("=" * 110)
        print()

        data = self.read_data()
        print(f"Period: {data[0]['date'].strftime('%Y-%m-%d')} to {data[-1]['date'].strftime('%Y-%m-%d')}")
        print(f"Trading days: {len(data):,}")
        print()

        daily_returns = self.calculate_returns(data)
        leveraged_returns = self.simulate_leveraged_etf(daily_returns)

        all_results = {}

        for years in timeframes:
            print(f"{'='*110}")
            print(f"{years}-YEAR INVESTMENT PERIOD")
            print(f"{'='*110}")
            print()

            results = self.three_way_comparison(leveraged_returns, monthly_amount, years)

            if not results:
                print(f"Not enough data for {years}-year analysis\n")
                continue

            # Find worst for each strategy
            worst_dca_lev = min(results, key=lambda x: x['dca_lev_ann'])
            worst_lump_lev = min(results, key=lambda x: x['lump_lev_ann'])
            worst_unlev = min(results, key=lambda x: x['unlev_ann'])

            # Find period where leverage hurt most vs unleveraged
            worst_leverage_damage = min(results, key=lambda x: min(x['dca_lev_ann'], x['lump_lev_ann']) - x['unlev_ann'])

            # Statistics
            dca_wins = sum(1 for r in results if r['winner'] == 'DCA_Lev')
            lump_wins = sum(1 for r in results if r['winner'] == 'Lump_Lev')
            unlev_wins = sum(1 for r in results if r['winner'] == 'Unlev')

            print(f"Analyzed {len(results):,} periods")
            print()
            print(f"Win Statistics:")
            print(f"  DCA 2x Leverage:    {dca_wins:,} periods ({100*dca_wins/len(results):.1f}%)")
            print(f"  Lump-Sum 2x Leverage: {lump_wins:,} periods ({100*lump_wins/len(results):.1f}%)")
            print(f"  Non-Leveraged:      {unlev_wins:,} periods ({100*unlev_wins/len(results):.1f}%)")
            print()

            print("-" * 110)
            print("WORST PERIOD WHERE LEVERAGE HURT MOST")
            print("-" * 110)
            w = worst_leverage_damage
            print(f"Period: {w['start_date'].strftime('%Y-%m')} to {w['end_date'].strftime('%Y-%m')}")
            print()
            print(f"Final Values (from ${w['total_invested']:,} invested):")
            print(f"  DCA 2x Leverage:      ${w['dca_lev_final']:>12,.0f}  ({w['dca_lev_ann']:>7.2f}% ann.)")
            print(f"  Lump-Sum 2x Leverage: ${w['lump_lev_final']:>12,.0f}  ({w['lump_lev_ann']:>7.2f}% ann.)")
            print(f"  Non-Leveraged:        ${w['unlev_final']:>12,.0f}  ({w['unlev_ann']:>7.2f}% ann.)")
            print()
            print(f"Ranking: 1st={w['winner']}, 2nd={w['second']}, 3rd={w['third']}")
            print()

            print("-" * 110)
            print("WORST PERIOD FOR EACH STRATEGY")
            print("-" * 110)
            print()

            print(f"DCA 2x Leverage:")
            print(f"  Period: {worst_dca_lev['start_date'].strftime('%Y-%m')} to {worst_dca_lev['end_date'].strftime('%Y-%m')}")
            print(f"  Annualized Return: {worst_dca_lev['dca_lev_ann']:.2f}%")
            print()

            print(f"Lump-Sum 2x Leverage:")
            print(f"  Period: {worst_lump_lev['start_date'].strftime('%Y-%m')} to {worst_lump_lev['end_date'].strftime('%Y-%m')}")
            print(f"  Annualized Return: {worst_lump_lev['lump_lev_ann']:.2f}%")
            print()

            print(f"Non-Leveraged:")
            print(f"  Period: {worst_unlev['start_date'].strftime('%Y-%m')} to {worst_unlev['end_date'].strftime('%Y-%m')}")
            print(f"  Annualized Return: {worst_unlev['unlev_ann']:.2f}%")
            print()

            all_results[years] = {
                'total_periods': len(results),
                'dca_wins': dca_wins,
                'lump_wins': lump_wins,
                'unlev_wins': unlev_wins,
                'worst_leverage_period': worst_leverage_damage,
                'worst_dca': worst_dca_lev,
                'worst_lump': worst_lump_lev,
                'worst_unlev': worst_unlev
            }

        return all_results


# Analyze all indices
indices = [
    ThreeWayComparison("S&P 500", "sp500_stooq_daily.csv", 'Date', 'Close', 1950),
    ThreeWayComparison("DJIA", "djia_stooq_daily.csv", 'Date', 'Close', 1950),
    ThreeWayComparison("NASDAQ", "nasdaq_fred.csv", 'observation_date', 'NASDAQCOM', 1971),
    ThreeWayComparison("Nikkei 225", "nikkei225_fred.csv", 'observation_date', 'NIKKEI225', 1950),
]

print()
print("╔" + "=" * 108 + "╗")
print("║" + " " * 30 + "THREE-WAY STRATEGY COMPARISON" + " " * 49 + "║")
print("║" + " " * 20 + "DCA 2x Leverage vs Lump-Sum 2x Leverage vs Non-Leveraged" + " " * 32 + "║")
print("╚" + "=" * 108 + "╝")
print()

all_index_results = {}

for idx_analyzer in indices:
    try:
        results = idx_analyzer.analyze_comprehensive(timeframes=[5, 10, 15], monthly_amount=500)
        all_index_results[idx_analyzer.name] = results
        print()
    except Exception as e:
        print(f"Error analyzing {idx_analyzer.name}: {e}\n")

# Summary table
print()
print("=" * 110)
print("SUMMARY: WHO WINS MOST OFTEN?")
print("=" * 110)
print()

for years in [5, 10, 15]:
    print(f"{years}-YEAR PERIODS:")
    print("-" * 110)
    print(f"{'Index':<20} {'DCA 2x Lev':<20} {'Lump 2x Lev':<20} {'Non-Lev':<20}")
    print("-" * 110)

    for idx_name, results in all_index_results.items():
        if years in results:
            r = results[years]
            total = r['total_periods']
            print(f"{idx_name:<20} {r['dca_wins']:>6} ({100*r['dca_wins']/total:>5.1f}%)      "
                  f"{r['lump_wins']:>6} ({100*r['lump_wins']/total:>5.1f}%)      "
                  f"{r['unlev_wins']:>6} ({100*r['unlev_wins']/total:>5.1f}%)")
    print()

print("=" * 110)
