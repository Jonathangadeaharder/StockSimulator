#!/usr/bin/env python3
"""
Statistical Robustness Analysis for Investment Strategy Comparisons

Performs bootstrap analysis by randomly sampling time periods to verify
that findings are robust and not artifacts of specific historical periods.

Methodology:
1. Randomly sample N different time windows from historical data
2. Run pairwise comparison on each sample
3. Collect win rates, median returns, percentiles
4. Calculate confidence intervals and variance
5. Test consistency of findings across samples
"""

import csv
import random
from datetime import datetime, timedelta
from collections import defaultdict
from analyze_pairwise_comparison import PairwiseComparison

class RobustnessAnalyzer:
    def __init__(self, name, filename, date_col='Date', price_col='Close', start_year=1950):
        self.name = name
        self.filename = filename
        self.date_col = date_col
        self.price_col = price_col
        self.start_year = start_year
        self.analyzer = PairwiseComparison(name, filename, date_col, price_col, start_year)

    def sample_random_periods(self, data, num_samples, years_per_period, min_gap_years=1):
        """
        Randomly sample non-overlapping time periods from the data.

        Args:
            data: Historical price data
            num_samples: Number of random periods to sample
            years_per_period: Length of each period in years
            min_gap_years: Minimum gap between sampled periods

        Returns:
            List of sampled data periods
        """
        if len(data) < 252 * years_per_period:
            return []

        # Calculate days needed for each period
        days_needed = int(years_per_period * 365.25)
        min_gap_days = int(min_gap_years * 365.25)

        # Find valid start positions
        valid_starts = []
        for i in range(len(data) - days_needed):
            # Check if we can fit the period
            end_date_target = data[i]['date'] + timedelta(days=days_needed)
            # Find actual end index
            for j in range(i, len(data)):
                if data[j]['date'] >= end_date_target:
                    if j < len(data):
                        valid_starts.append((i, j))
                    break

        if len(valid_starts) < num_samples:
            num_samples = len(valid_starts)

        # Sample without replacement, ensuring no overlap
        sampled_periods = []
        sampled_ranges = []

        attempts = 0
        max_attempts = num_samples * 100

        while len(sampled_periods) < num_samples and attempts < max_attempts:
            attempts += 1
            start_idx, end_idx = random.choice(valid_starts)

            # Check for overlap with existing samples
            overlaps = False
            for existing_start, existing_end in sampled_ranges:
                if not (end_idx + min_gap_days < existing_start or start_idx > existing_end + min_gap_days):
                    overlaps = True
                    break

            if not overlaps:
                sampled_periods.append(data[start_idx:end_idx])
                sampled_ranges.append((start_idx, end_idx))

        return sampled_periods

    def analyze_sample(self, sample_data, years, monthly_amount=500):
        """
        Run pairwise analysis on a single sampled period.

        Analyzes just the one specific period, not rolling windows within it.

        Returns:
            Dictionary with returns for this specific period
        """
        # Calculate returns
        returns = self.analyzer.calculate_returns(sample_data)
        if len(returns) < 252 * years * 0.9:  # Allow some tolerance
            return None

        leveraged_returns = self.analyzer.simulate_leveraged_etf(returns)

        # Run comparison for this single period
        total_investment = monthly_amount * years * 12
        months_needed = years * 12

        if len(leveraged_returns) < 252 * years * 0.9:
            return None

        # Limit to exact years needed
        days_needed = int(years * 365.25)

        # Strategy 1: Lump-sum into 2x leveraged
        lump_lev_cumulative = 1.0

        # Strategy 2: $500/month into non-leveraged
        monthly_unlev_shares = 0.0
        monthly_unlev_price = 100.0
        monthly_unlev_invested = 0

        # Strategy 3: $500/month into 2x leveraged
        monthly_lev_shares = 0.0
        monthly_lev_price = 100.0
        monthly_lev_invested = 0

        month = 0
        start_idx = 0
        end_idx = min(len(leveraged_returns), int(years * 252))

        for i in range(start_idx, end_idx):
            ret = leveraged_returns[i]

            # Lump-sum compounds
            lump_lev_cumulative *= (1 + ret['lev_return'])

            # Monthly prices update
            monthly_unlev_price *= (1 + ret['unlev_return'])
            monthly_lev_price *= (1 + ret['lev_return'])

            # Monthly investments
            days_since_start = i
            expected_month = days_since_start / 30.44
            if int(expected_month) > month and month < months_needed:
                month = int(expected_month)
                monthly_unlev_shares += monthly_amount / monthly_unlev_price
                monthly_unlev_invested += monthly_amount
                monthly_lev_shares += monthly_amount / monthly_lev_price
                monthly_lev_invested += monthly_amount

        # Final values
        lump_lev_final = total_investment * lump_lev_cumulative
        monthly_unlev_final = monthly_unlev_shares * monthly_unlev_price
        monthly_lev_final = monthly_lev_shares * monthly_lev_price

        actual_years = end_idx / 252.0

        # Annualized returns
        lump_lev_ann = ((lump_lev_cumulative) ** (1/actual_years) - 1) * 100

        if monthly_unlev_invested > 0:
            monthly_unlev_ann = ((monthly_unlev_final / monthly_unlev_invested) ** (1/actual_years) - 1) * 100
        else:
            monthly_unlev_ann = 0

        if monthly_lev_invested > 0:
            monthly_lev_ann = ((monthly_lev_final / monthly_lev_invested) ** (1/actual_years) - 1) * 100
        else:
            monthly_lev_ann = 0

        return {
            'lump_vs_unlev': {
                'lump_wins': lump_lev_final > monthly_unlev_final,
                'lump_return': lump_lev_ann,
                'unlev_return': monthly_unlev_ann,
                'gap': lump_lev_ann - monthly_unlev_ann
            },
            'monthly_vs_unlev': {
                'lev_wins': monthly_lev_final > monthly_unlev_final,
                'lev_return': monthly_lev_ann,
                'unlev_return': monthly_unlev_ann,
                'gap': monthly_lev_ann - monthly_unlev_ann
            }
        }

    def bootstrap_analysis(self, num_samples=50, years=5, monthly_amount=500):
        """
        Perform bootstrap analysis with multiple random samples.

        Args:
            num_samples: Number of random samples to analyze
            years: Length of investment period
            monthly_amount: Monthly investment amount

        Returns:
            Dictionary with aggregated statistics and confidence intervals
        """
        print(f"Loading data for {self.name}...")
        data = self.analyzer.read_data()

        print(f"Sampling {num_samples} random {years}-year periods...")
        sampled_periods = self.sample_random_periods(data, num_samples, years)

        print(f"Successfully sampled {len(sampled_periods)} periods")

        # Analyze each sample
        print(f"Analyzing {len(sampled_periods)} samples...")
        sample_results = []
        for i, sample in enumerate(sampled_periods):
            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(sampled_periods)} samples...")
            result = self.analyze_sample(sample, years, monthly_amount)
            if result:
                sample_results.append(result)

        print(f"Successfully analyzed {len(sample_results)} samples")

        # Aggregate statistics
        return self.calculate_aggregate_statistics(sample_results)

    def calculate_aggregate_statistics(self, sample_results):
        """Calculate mean, std dev, confidence intervals from sample results."""

        def get_stats(values):
            """Calculate statistics for a list of values."""
            if not values:
                return None
            values = sorted(values)
            n = len(values)
            if n < 2:
                return {
                    'mean': values[0],
                    'median': values[0],
                    'std': 0,
                    'min': values[0],
                    'max': values[0],
                    'ci_95_lower': values[0],
                    'ci_95_upper': values[0],
                    'ci_90_lower': values[0],
                    'ci_90_upper': values[0],
                }
            mean = sum(values) / n
            # Use sample variance (n-1) for unbiased estimator
            return {
                'mean': mean,
                'median': values[n//2],
                'std': (sum((x - mean)**2 for x in values) / (n - 1)) ** 0.5,
                'min': values[0],
                'max': values[-1],
                'ci_95_lower': values[max(0, int(n * 0.025))],
                'ci_95_upper': values[min(n-1, int(n * 0.975))],
                'ci_90_lower': values[max(0, int(n * 0.05))],
                'ci_90_upper': values[min(n-1, int(n * 0.95))],
            }

        # Collect all metrics - now each sample is a single period result
        lump_wins = [1 if r['lump_vs_unlev']['lump_wins'] else 0 for r in sample_results]
        lump_returns = [r['lump_vs_unlev']['lump_return'] for r in sample_results]
        lump_gaps = [r['lump_vs_unlev']['gap'] for r in sample_results]

        monthly_wins = [1 if r['monthly_vs_unlev']['lev_wins'] else 0 for r in sample_results]
        monthly_returns = [r['monthly_vs_unlev']['lev_return'] for r in sample_results]
        monthly_gaps = [r['monthly_vs_unlev']['gap'] for r in sample_results]

        # Calculate win rates
        lump_win_rate = (sum(lump_wins) / len(lump_wins) * 100) if lump_wins else 0
        monthly_win_rate = (sum(monthly_wins) / len(monthly_wins) * 100) if monthly_wins else 0

        return {
            'num_samples': len(sample_results),
            'lump_vs_unlev': {
                'win_rate_pct': lump_win_rate,
                'return': get_stats(lump_returns),
                'gap': get_stats(lump_gaps)
            },
            'monthly_vs_unlev': {
                'win_rate_pct': monthly_win_rate,
                'return': get_stats(monthly_returns),
                'gap': get_stats(monthly_gaps)
            }
        }


def format_statistics(stats, metric_name):
    """Format statistics for display."""
    if not stats:
        return "No data"

    return f"""
  Mean:              {stats['mean']:8.2f}
  Median:            {stats['median']:8.2f}
  Std Dev:           {stats['std']:8.2f}
  Min:               {stats['min']:8.2f}
  Max:               {stats['max']:8.2f}
  95% CI:            [{stats['ci_95_lower']:7.2f}, {stats['ci_95_upper']:7.2f}]
  90% CI:            [{stats['ci_90_lower']:7.2f}, {stats['ci_90_upper']:7.2f}]
"""


def print_robustness_report(index_name, results, years):
    """Print formatted robustness analysis report."""
    print("\n" + "=" * 120)
    print(f"ROBUSTNESS ANALYSIS: {index_name} ({years}-Year Periods)")
    print("=" * 120)
    print(f"Number of random samples analyzed: {results['num_samples']}")
    print()

    print("-" * 120)
    print("COMPARISON 1: Lump-Sum 2x Leveraged vs Monthly Non-Leveraged")
    print("-" * 120)

    print(f"\nWin Rate Across Samples: {results['lump_vs_unlev']['win_rate_pct']:.1f}%")
    print(f"(Lump-sum 2x won in {int(results['lump_vs_unlev']['win_rate_pct'] * results['num_samples'] / 100)}/{results['num_samples']} random periods)")

    print("\nReturn Gap Distribution (Lump 2x - Non-Lev, annualized %):")
    print(format_statistics(results['lump_vs_unlev']['gap'], "Gap"))

    print("\nLump-Sum 2x Return Distribution (annualized %):")
    print(format_statistics(results['lump_vs_unlev']['return'], "Return"))

    print()
    print("-" * 120)
    print("COMPARISON 2: Monthly 2x Leveraged vs Monthly Non-Leveraged")
    print("-" * 120)

    print(f"\nWin Rate Across Samples: {results['monthly_vs_unlev']['win_rate_pct']:.1f}%")
    print(f"(Monthly 2x won in {int(results['monthly_vs_unlev']['win_rate_pct'] * results['num_samples'] / 100)}/{results['num_samples']} random periods)")

    print("\nReturn Gap Distribution (Monthly 2x - Non-Lev, annualized %):")
    print(format_statistics(results['monthly_vs_unlev']['gap'], "Gap"))

    print("\nMonthly 2x Return Distribution (annualized %):")
    print(format_statistics(results['monthly_vs_unlev']['return'], "Return"))
    print()


def main():
    """Run robustness analysis on all indices."""
    print("╔" + "=" * 118 + "╗")
    print("║" + " " * 35 + "STATISTICAL ROBUSTNESS ANALYSIS" + " " * 52 + "║")
    print("║" + " " * 25 + "Bootstrap Analysis with Random Time Period Sampling" + " " * 42 + "║")
    print("╚" + "=" * 118 + "╝")
    print()
    print("Methodology:")
    print("- Randomly sample non-overlapping time periods from historical data")
    print("- Run pairwise comparison on each sample")
    print("- Calculate statistics: mean, median, std dev, confidence intervals")
    print("- Verify findings are consistent across different market periods")
    print()

    # Set random seed for reproducibility
    random.seed(42)

    # Define indices to analyze
    indices = [
        ('S&P 500', 'sp500_stooq_daily.csv', 'Date', 'Close', 1950),
        ('DJIA', 'djia_stooq_daily.csv', 'Date', 'Close', 1950),
        ('NASDAQ', 'nasdaq_fred.csv', 'observation_date', 'NASDAQCOM', 1971),
        ('Nikkei 225', 'nikkei225_fred.csv', 'observation_date', 'NIKKEI225', 1950),
    ]

    # Analysis parameters
    num_samples = 100  # Number of random samples per index (try more, will get what we can)
    time_periods = [5, 10]  # Years per period (focus on 5 and 10 for speed)

    all_results = {}

    for name, filename, date_col, price_col, start_year in indices:
        print("\n" + "=" * 120)
        print(f"ANALYZING: {name}")
        print("=" * 120)

        analyzer = RobustnessAnalyzer(name, filename, date_col, price_col, start_year)

        all_results[name] = {}

        for years in time_periods:
            print(f"\n{years}-YEAR PERIODS:")
            print("-" * 120)

            try:
                results = analyzer.bootstrap_analysis(
                    num_samples=num_samples,
                    years=years,
                    monthly_amount=500
                )

                all_results[name][years] = results
                print_robustness_report(name, results, years)

            except Exception as e:
                print(f"Error analyzing {name} {years}-year periods: {e}")
                continue

    # Summary comparison
    print("\n\n" + "=" * 120)
    print("ROBUSTNESS SUMMARY: Consistency Check")
    print("=" * 120)
    print()
    print("Key Question: Are win rates consistent across random samples?")
    print()

    for name in all_results:
        print(f"\n{name}:")
        print("-" * 120)
        print(f"{'Period':<10} {'Comparison':<40} {'Win %':<12} {'Gap Mean':<12} {'Gap Std':<12} {'95% CI':<25}")
        print("-" * 120)

        for years in time_periods:
            if years not in all_results[name]:
                continue

            r = all_results[name][years]

            # Lump-sum comparison
            lwr = r['lump_vs_unlev']['win_rate_pct']
            lg = r['lump_vs_unlev']['gap']
            if lg:
                print(f"{years}Y{'':<6} {'Lump-Sum 2x vs Monthly Non-Lev':<40} "
                      f"{lwr:>10.1f}% {lg['mean']:>10.2f}% {lg['std']:>10.2f}% "
                      f"[{lg['ci_95_lower']:>6.2f}%, {lg['ci_95_upper']:>6.2f}%]")

            # Monthly comparison
            mwr = r['monthly_vs_unlev']['win_rate_pct']
            mg = r['monthly_vs_unlev']['gap']
            if mg:
                print(f"{'':<10} {'Monthly 2x vs Monthly Non-Lev':<40} "
                      f"{mwr:>10.1f}% {mg['mean']:>10.2f}% {mg['std']:>10.2f}% "
                      f"[{mg['ci_95_lower']:>6.2f}%, {mg['ci_95_upper']:>6.2f}%]")

        print()

    print("\n" + "=" * 120)
    print("ROBUSTNESS INTERPRETATION:")
    print("=" * 120)
    print("- Small std dev (<5%) indicates highly robust findings")
    print("- Narrow confidence intervals indicate consistent results across time periods")
    print("- Wide intervals suggest results vary significantly by market conditions")
    print("=" * 120)


if __name__ == '__main__':
    main()
