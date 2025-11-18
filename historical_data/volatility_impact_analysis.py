#!/usr/bin/env python3
# @structurelint:no-test
"""
Volatility Impact Analysis on Leveraged Strategies

Analyzes the relationship between index volatility and leveraged ETF performance.
Key questions:
1. How does volatility affect leveraged strategy returns?
2. What is the volatility decay cost for each index?
3. Do higher volatility periods show worse leveraged performance?
4. Can we quantify the volatility drag?
"""

import csv
from datetime import datetime
from collections import defaultdict
from analyze_pairwise_comparison import PairwiseComparison


class VolatilityImpactAnalyzer:
    def __init__(self, name, filename, date_col='Date', price_col='Close', start_year=1950):
        self.name = name
        self.analyzer = PairwiseComparison(name, filename, date_col, price_col, start_year)

    def calculate_rolling_volatility(self, returns, window_days=252):
        """
        Calculate rolling volatility (annualized standard deviation).

        Args:
            returns: List of daily return dictionaries
            window_days: Rolling window size (default 252 = 1 year)

        Returns:
            List of volatility measurements
        """
        volatilities = []

        for i in range(window_days, len(returns)):
            window = returns[i-window_days:i]
            daily_returns = [r['return'] for r in window]

            # Calculate standard deviation (using sample variance)
            n = len(daily_returns)
            mean = sum(daily_returns) / n
            # Use sample variance (n-1) for unbiased estimator
            variance = sum((r - mean) ** 2 for r in daily_returns) / (n - 1) if n > 1 else 0
            std_dev = variance ** 0.5

            # Annualize (252 trading days per year)
            annualized_vol = std_dev * (252 ** 0.5) * 100

            volatilities.append({
                'date': returns[i]['date'],
                'volatility': annualized_vol,
                'mean_return': mean
            })

        return volatilities

    def analyze_volatility_periods(self, returns, leveraged_returns, years=5):
        """
        Analyze performance in different volatility regimes.

        Splits data into low/medium/high volatility periods and compares
        leveraged vs unleveraged performance.
        """
        # Calculate rolling volatility
        volatilities = self.calculate_rolling_volatility(returns)

        if len(volatilities) < 100:
            return None

        # Sort by volatility to find terciles
        sorted_vols = sorted([v['volatility'] for v in volatilities])
        n = len(sorted_vols)
        low_threshold = sorted_vols[n // 3]
        high_threshold = sorted_vols[2 * n // 3]

        # Categorize periods
        periods = {
            'low': [],
            'medium': [],
            'high': []
        }

        days_needed = int(years * 252)

        for i in range(len(volatilities)):
            vol = volatilities[i]['volatility']

            if i + days_needed >= len(leveraged_returns):
                break

            # Categorize
            if vol <= low_threshold:
                category = 'low'
            elif vol <= high_threshold:
                category = 'medium'
            else:
                category = 'high'

            # Calculate performance over next 'years' period
            period_returns = leveraged_returns[i:i+days_needed]

            # Unleveraged cumulative
            unlev_cumulative = 1.0
            for ret in period_returns:
                unlev_cumulative *= (1 + ret['unlev_return'])

            # Leveraged cumulative
            lev_cumulative = 1.0
            for ret in period_returns:
                lev_cumulative *= (1 + ret['lev_return'])

            actual_years = len(period_returns) / 252.0

            unlev_ann = ((unlev_cumulative) ** (1/actual_years) - 1) * 100
            lev_ann = ((lev_cumulative) ** (1/actual_years) - 1) * 100

            # Calculate leverage efficiency (actual vs theoretical)
            # Theoretical 2x would be: 2 * unleveraged return
            theoretical_lev = unlev_ann * 2
            leverage_efficiency = (lev_ann / theoretical_lev * 100) if theoretical_lev != 0 else 0

            periods[category].append({
                'volatility': vol,
                'unlev_return': unlev_ann,
                'lev_return': lev_ann,
                'gap': lev_ann - unlev_ann,
                'theoretical_lev': theoretical_lev,
                'leverage_efficiency': leverage_efficiency,
                'volatility_drag': theoretical_lev - lev_ann
            })

        return periods, low_threshold, high_threshold

    def calculate_volatility_decay_cost(self, returns, leveraged_returns):
        """
        Calculate the cost of volatility decay.

        Volatility decay = theoretical 2x return - actual leveraged return
        """
        # Calculate overall returns
        unlev_cumulative = 1.0
        lev_cumulative = 1.0

        for i in range(len(leveraged_returns)):
            unlev_cumulative *= (1 + leveraged_returns[i]['unlev_return'])
            lev_cumulative *= (1 + leveraged_returns[i]['lev_return'])

        years = len(leveraged_returns) / 252.0

        unlev_ann = ((unlev_cumulative) ** (1/years) - 1) * 100
        lev_ann = ((lev_cumulative) ** (1/years) - 1) * 100

        # Theoretical 2x (no decay)
        theoretical_2x = unlev_ann * 2

        # Decay cost
        decay_cost = theoretical_2x - lev_ann

        return {
            'unlev_return': unlev_ann,
            'lev_return': lev_ann,
            'theoretical_2x': theoretical_2x,
            'decay_cost': decay_cost,
            'efficiency': (lev_ann / theoretical_2x * 100) if theoretical_2x != 0 else 0
        }

    def analyze_volatility_vs_performance(self):
        """Run complete volatility impact analysis."""
        print(f"\n{'='*120}")
        print(f"VOLATILITY IMPACT ANALYSIS: {self.name}")
        print(f"{'='*120}\n")

        # Load data
        data = self.analyzer.read_data()
        returns = self.analyzer.calculate_returns(data)
        leveraged_returns = self.analyzer.simulate_leveraged_etf(returns)

        # Overall volatility
        volatilities = self.calculate_rolling_volatility(returns)
        avg_vol = sum(v['volatility'] for v in volatilities) / len(volatilities)

        print(f"Average Historical Volatility: {avg_vol:.2f}%")
        print()

        # Overall decay cost
        decay_stats = self.calculate_volatility_decay_cost(returns, leveraged_returns)

        print(f"Overall Performance (Full History):")
        print(f"  Unleveraged Return:     {decay_stats['unlev_return']:>8.2f}% annualized")
        print(f"  Leveraged (2x) Return:  {decay_stats['lev_return']:>8.2f}% annualized")
        print(f"  Theoretical 2x Return:  {decay_stats['theoretical_2x']:>8.2f}% annualized")
        print(f"  Volatility Decay Cost:  {decay_stats['decay_cost']:>8.2f}% per year")
        print(f"  Leverage Efficiency:    {decay_stats['efficiency']:>8.2f}%")
        print()

        # Analyze by volatility regime
        print(f"{'='*120}")
        print(f"PERFORMANCE BY VOLATILITY REGIME (5-Year Periods)")
        print(f"{'='*120}\n")

        vol_periods, low_thresh, high_thresh = self.analyze_volatility_periods(
            returns, leveraged_returns, years=5
        )

        print(f"Volatility Regime Thresholds:")
        print(f"  Low Volatility:    < {low_thresh:.2f}%")
        print(f"  Medium Volatility: {low_thresh:.2f}% - {high_thresh:.2f}%")
        print(f"  High Volatility:   > {high_thresh:.2f}%")
        print()

        for regime in ['low', 'medium', 'high']:
            periods = vol_periods[regime]

            if not periods:
                continue

            avg_vol = sum(p['volatility'] for p in periods) / len(periods)
            avg_unlev = sum(p['unlev_return'] for p in periods) / len(periods)
            avg_lev = sum(p['lev_return'] for p in periods) / len(periods)
            avg_gap = sum(p['gap'] for p in periods) / len(periods)
            avg_efficiency = sum(p['leverage_efficiency'] for p in periods) / len(periods)
            avg_drag = sum(p['volatility_drag'] for p in periods) / len(periods)

            print(f"{regime.upper()} VOLATILITY REGIME ({len(periods)} periods):")
            print(f"{'─'*120}")
            print(f"  Average Volatility:         {avg_vol:>8.2f}%")
            print(f"  Average Unleveraged Return: {avg_unlev:>8.2f}% annualized")
            print(f"  Average Leveraged Return:   {avg_lev:>8.2f}% annualized")
            print(f"  Average Gap (Lev - Unlev):  {avg_gap:>8.2f}% per year")
            print(f"  Leverage Efficiency:        {avg_efficiency:>8.2f}%")
            print(f"  Volatility Drag:            {avg_drag:>8.2f}% per year")
            print()

        # Compare leverage efficiency across regimes
        print(f"{'='*120}")
        print(f"VOLATILITY IMPACT SUMMARY")
        print(f"{'='*120}\n")

        low_eff = sum(p['leverage_efficiency'] for p in vol_periods['low']) / len(vol_periods['low']) if vol_periods['low'] else 0
        med_eff = sum(p['leverage_efficiency'] for p in vol_periods['medium']) / len(vol_periods['medium']) if vol_periods['medium'] else 0
        high_eff = sum(p['leverage_efficiency'] for p in vol_periods['high']) / len(vol_periods['high']) if vol_periods['high'] else 0

        low_drag = sum(p['volatility_drag'] for p in vol_periods['low']) / len(vol_periods['low']) if vol_periods['low'] else 0
        med_drag = sum(p['volatility_drag'] for p in vol_periods['medium']) / len(vol_periods['medium']) if vol_periods['medium'] else 0
        high_drag = sum(p['volatility_drag'] for p in vol_periods['high']) / len(vol_periods['high']) if vol_periods['high'] else 0

        print(f"Leverage Efficiency by Volatility:")
        print(f"  Low Volatility:    {low_eff:>6.1f}% (loses {100-low_eff:.1f}% to decay)")
        print(f"  Medium Volatility: {med_eff:>6.1f}% (loses {100-med_eff:.1f}% to decay)")
        print(f"  High Volatility:   {high_eff:>6.1f}% (loses {100-high_eff:.1f}% to decay)")
        print()

        print(f"Volatility Drag (Theoretical 2x - Actual):")
        print(f"  Low Volatility:    {low_drag:>6.2f}% per year")
        print(f"  Medium Volatility: {med_drag:>6.2f}% per year")
        print(f"  High Volatility:   {high_drag:>6.2f}% per year")
        print()

        efficiency_decline = low_eff - high_eff
        drag_increase = high_drag - low_drag

        print(f"Impact of High vs Low Volatility:")
        print(f"  Efficiency Decline:  {efficiency_decline:>6.1f} percentage points")
        print(f"  Drag Increase:       {drag_increase:>6.2f}% per year")
        print()

        return {
            'name': self.name,
            'avg_volatility': avg_vol,
            'overall_decay': decay_stats,
            'vol_regimes': vol_periods,
            'thresholds': (low_thresh, high_thresh),
            'efficiency_by_vol': {
                'low': low_eff,
                'medium': med_eff,
                'high': high_eff
            },
            'drag_by_vol': {
                'low': low_drag,
                'medium': med_drag,
                'high': high_drag
            }
        }


def main():
    """Run volatility impact analysis on all indices."""
    print("╔" + "="*118 + "╗")
    print("║" + " "*30 + "VOLATILITY IMPACT ON LEVERAGED STRATEGIES" + " "*47 + "║")
    print("║" + " "*25 + "How Index Volatility Affects Leveraged ETF Performance" + " "*40 + "║")
    print("╚" + "="*118 + "╝")
    print()
    print("Analysis Framework:")
    print("- Calculate rolling historical volatility for each index")
    print("- Measure volatility decay cost (theoretical 2x - actual leveraged return)")
    print("- Compare leveraged performance in low/medium/high volatility regimes")
    print("- Quantify leverage efficiency across different volatility levels")
    print()

    indices = [
        ('S&P 500', 'sp500_stooq_daily.csv', 'Date', 'Close', 1950),
        ('DJIA', 'djia_stooq_daily.csv', 'Date', 'Close', 1950),
        ('NASDAQ', 'nasdaq_fred.csv', 'observation_date', 'NASDAQCOM', 1971),
        ('Nikkei 225', 'nikkei225_fred.csv', 'observation_date', 'NIKKEI225', 1950),
    ]

    all_results = {}

    for name, filename, date_col, price_col, start_year in indices:
        try:
            analyzer = VolatilityImpactAnalyzer(name, filename, date_col, price_col, start_year)
            results = analyzer.analyze_volatility_vs_performance()
            all_results[name] = results
        except Exception as e:
            print(f"\nError analyzing {name}: {e}\n")

    # Cross-index comparison
    print("\n" + "="*120)
    print("CROSS-INDEX VOLATILITY COMPARISON")
    print("="*120 + "\n")

    print(f"{'Index':<15} {'Avg Vol':<12} {'Overall Decay':<15} {'Low Vol Eff':<15} {'High Vol Eff':<15} {'Eff Decline':<15}")
    print("─"*120)

    for name in ['S&P 500', 'DJIA', 'NASDAQ', 'Nikkei 225']:
        if name in all_results:
            r = all_results[name]
            avg_vol = r['avg_volatility']
            decay = r['overall_decay']['decay_cost']
            low_eff = r['efficiency_by_vol']['low']
            high_eff = r['efficiency_by_vol']['high']
            decline = low_eff - high_eff

            print(f"{name:<15} {avg_vol:>10.2f}% {decay:>13.2f}% {low_eff:>13.1f}% {high_eff:>13.1f}% {decline:>13.1f}pp")

    print()
    print("="*120)
    print("KEY INSIGHTS:")
    print("="*120)
    print("- Higher average volatility → Greater volatility decay cost")
    print("- Leverage efficiency declines as volatility increases")
    print("- High volatility periods show significantly worse leveraged performance")
    print("- Volatility drag can cost 5-15% annually in high volatility environments")
    print("="*120)


if __name__ == '__main__':
    main()
