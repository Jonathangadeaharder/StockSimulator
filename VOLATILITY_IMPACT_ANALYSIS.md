╔======================================================================================================================╗
║                              VOLATILITY IMPACT ON LEVERAGED STRATEGIES                                               ║
║                         How Index Volatility Affects Leveraged ETF Performance                                        ║
╚======================================================================================================================╝

Analysis Framework:
- Calculate rolling historical volatility for each index
- Measure volatility decay cost (theoretical 2x - actual leveraged return)
- Compare leveraged performance in low/medium/high volatility regimes
- Quantify leverage efficiency across different volatility levels


========================================================================================================================
VOLATILITY IMPACT ANALYSIS: S&P 500
========================================================================================================================

Average Historical Volatility: 14.40%

Overall Performance (Full History):
  Unleveraged Return:        10.39% annualized
  Leveraged (2x) Return:     18.11% annualized
  Theoretical 2x Return:     20.79% annualized
  Volatility Decay Cost:      2.68% per year
  Leverage Efficiency:       87.13%

========================================================================================================================
PERFORMANCE BY VOLATILITY REGIME (5-Year Periods)
========================================================================================================================

Volatility Regime Thresholds:
  Low Volatility:    < 10.92%
  Medium Volatility: 10.92% - 14.99%
  High Volatility:   > 14.99%

LOW VOLATILITY REGIME (6307 periods):
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Average Volatility:             9.30%
  Average Unleveraged Return:    10.60% annualized
  Average Leveraged Return:      19.72% annualized
  Average Gap (Lev - Unlev):      9.12% per year
  Leverage Efficiency:          112.47%
  Volatility Drag:                1.48% per year

MEDIUM VOLATILITY REGIME (5848 periods):
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Average Volatility:            12.80%
  Average Unleveraged Return:    11.42% annualized
  Average Leveraged Return:      20.83% annualized
  Average Gap (Lev - Unlev):      9.41% per year
  Leverage Efficiency:          137.31%
  Volatility Drag:                2.00% per year

HIGH VOLATILITY REGIME (5756 periods):
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Average Volatility:            21.22%
  Average Unleveraged Return:     8.39% annualized
  Average Leveraged Return:      13.48% annualized
  Average Gap (Lev - Unlev):      5.09% per year
  Leverage Efficiency:           91.34%
  Volatility Drag:                3.30% per year

========================================================================================================================
VOLATILITY IMPACT SUMMARY
========================================================================================================================

Leverage Efficiency by Volatility:
  Low Volatility:     112.5% (loses -12.5% to decay)
  Medium Volatility:  137.3% (loses -37.3% to decay)
  High Volatility:     91.3% (loses 8.7% to decay)

Volatility Drag (Theoretical 2x - Actual):
  Low Volatility:      1.48% per year
  Medium Volatility:   2.00% per year
  High Volatility:     3.30% per year

Impact of High vs Low Volatility:
  Efficiency Decline:    21.1 percentage points
  Drag Increase:         1.82% per year


========================================================================================================================
VOLATILITY IMPACT ANALYSIS: DJIA
========================================================================================================================

Average Historical Volatility: 14.27%

Overall Performance (Full History):
  Unleveraged Return:         9.61% annualized
  Leveraged (2x) Return:     16.52% annualized
  Theoretical 2x Return:     19.23% annualized
  Volatility Decay Cost:      2.71% per year
  Leverage Efficiency:       85.90%

========================================================================================================================
PERFORMANCE BY VOLATILITY REGIME (5-Year Periods)
========================================================================================================================

Volatility Regime Thresholds:
  Low Volatility:    < 10.77%
  Medium Volatility: 10.77% - 14.98%
  High Volatility:   > 14.98%

LOW VOLATILITY REGIME (6139 periods):
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Average Volatility:             9.40%
  Average Unleveraged Return:    10.12% annualized
  Average Leveraged Return:      18.81% annualized
  Average Gap (Lev - Unlev):      8.69% per year
  Leverage Efficiency:           95.05%
  Volatility Drag:                1.42% per year

MEDIUM VOLATILITY REGIME (5952 periods):
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Average Volatility:            12.76%
  Average Unleveraged Return:    10.34% annualized
  Average Leveraged Return:      18.47% annualized
  Average Gap (Lev - Unlev):      8.13% per year
  Leverage Efficiency:           82.09%
  Volatility Drag:                2.21% per year

HIGH VOLATILITY REGIME (5829 periods):
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Average Volatility:            20.90%
  Average Unleveraged Return:     8.15% annualized
  Average Leveraged Return:      12.89% annualized
  Average Gap (Lev - Unlev):      4.74% per year
  Leverage Efficiency:           60.46%
  Volatility Drag:                3.41% per year

========================================================================================================================
VOLATILITY IMPACT SUMMARY
========================================================================================================================

Leverage Efficiency by Volatility:
  Low Volatility:      95.1% (loses 4.9% to decay)
  Medium Volatility:   82.1% (loses 17.9% to decay)
  High Volatility:     60.5% (loses 39.5% to decay)

Volatility Drag (Theoretical 2x - Actual):
  Low Volatility:      1.42% per year
  Medium Volatility:   2.21% per year
  High Volatility:     3.41% per year

Impact of High vs Low Volatility:
  Efficiency Decline:    34.6 percentage points
  Drag Increase:         1.99% per year


========================================================================================================================
VOLATILITY IMPACT ANALYSIS: NASDAQ
========================================================================================================================

Average Historical Volatility: 18.01%

Overall Performance (Full History):
  Unleveraged Return:        12.67% annualized
  Leveraged (2x) Return:     21.08% annualized
  Theoretical 2x Return:     25.34% annualized
  Volatility Decay Cost:      4.26% per year
  Leverage Efficiency:       83.19%

========================================================================================================================
PERFORMANCE BY VOLATILITY REGIME (5-Year Periods)
========================================================================================================================

Volatility Regime Thresholds:
  Low Volatility:    < 12.74%
  Medium Volatility: 12.74% - 18.62%
  High Volatility:   > 18.62%

LOW VOLATILITY REGIME (4519 periods):
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Average Volatility:            10.33%
  Average Unleveraged Return:    15.05% annualized
  Average Leveraged Return:      29.35% annualized
  Average Gap (Lev - Unlev):     14.30% per year
  Leverage Efficiency:          133.59%
  Volatility Drag:                0.75% per year

MEDIUM VOLATILITY REGIME (4147 periods):
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Average Volatility:            15.10%
  Average Unleveraged Return:    15.40% annualized
  Average Leveraged Return:      28.16% annualized
  Average Gap (Lev - Unlev):     12.76% per year
  Leverage Efficiency:           80.89%
  Volatility Drag:                2.64% per year

HIGH VOLATILITY REGIME (3880 periods):
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Average Volatility:            28.90%
  Average Unleveraged Return:     8.91% annualized
  Average Leveraged Return:      11.47% annualized
  Average Gap (Lev - Unlev):      2.56% per year
  Leverage Efficiency:          149.09%
  Volatility Drag:                6.35% per year

========================================================================================================================
VOLATILITY IMPACT SUMMARY
========================================================================================================================

Leverage Efficiency by Volatility:
  Low Volatility:     133.6% (loses -33.6% to decay)
  Medium Volatility:   80.9% (loses 19.1% to decay)
  High Volatility:    149.1% (loses -49.1% to decay)

Volatility Drag (Theoretical 2x - Actual):
  Low Volatility:      0.75% per year
  Medium Volatility:   2.64% per year
  High Volatility:     6.35% per year

Impact of High vs Low Volatility:
  Efficiency Decline:   -15.5 percentage points
  Drag Increase:         5.60% per year


========================================================================================================================
VOLATILITY IMPACT ANALYSIS: Nikkei 225
========================================================================================================================

Average Historical Volatility: 18.16%

Overall Performance (Full History):
  Unleveraged Return:        10.75% annualized
  Leveraged (2x) Return:     17.32% annualized
  Theoretical 2x Return:     21.51% annualized
  Volatility Decay Cost:      4.18% per year
  Leverage Efficiency:       80.55%

========================================================================================================================
PERFORMANCE BY VOLATILITY REGIME (5-Year Periods)
========================================================================================================================

Volatility Regime Thresholds:
  Low Volatility:    < 14.95%
  Medium Volatility: 14.95% - 20.23%
  High Volatility:   > 20.23%

LOW VOLATILITY REGIME (6194 periods):
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Average Volatility:            11.26%
  Average Unleveraged Return:    16.70% annualized
  Average Leveraged Return:      33.24% annualized
  Average Gap (Lev - Unlev):     16.54% per year
  Leverage Efficiency:           63.34%
  Volatility Drag:                0.15% per year

MEDIUM VOLATILITY REGIME (5588 periods):
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Average Volatility:            17.46%
  Average Unleveraged Return:     9.15% annualized
  Average Leveraged Return:      15.24% annualized
  Average Gap (Lev - Unlev):      6.09% per year
  Leverage Efficiency:         -138.85%
  Volatility Drag:                3.05% per year

HIGH VOLATILITY REGIME (5790 periods):
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Average Volatility:            25.78%
  Average Unleveraged Return:     4.34% annualized
  Average Leveraged Return:       3.98% annualized
  Average Gap (Lev - Unlev):     -0.36% per year
  Leverage Efficiency:          147.76%
  Volatility Drag:                4.70% per year

========================================================================================================================
VOLATILITY IMPACT SUMMARY
========================================================================================================================

Leverage Efficiency by Volatility:
  Low Volatility:      63.3% (loses 36.7% to decay)
  Medium Volatility: -138.9% (loses 238.9% to decay)
  High Volatility:    147.8% (loses -47.8% to decay)

Volatility Drag (Theoretical 2x - Actual):
  Low Volatility:      0.15% per year
  Medium Volatility:   3.05% per year
  High Volatility:     4.70% per year

Impact of High vs Low Volatility:
  Efficiency Decline:   -84.4 percentage points
  Drag Increase:         4.55% per year


========================================================================================================================
CROSS-INDEX VOLATILITY COMPARISON
========================================================================================================================

Index           Avg Vol      Overall Decay   Low Vol Eff     High Vol Eff    Eff Decline    
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
S&P 500              21.22%          2.68%         112.5%          91.3%          21.1pp
DJIA                 20.90%          2.71%          95.1%          60.5%          34.6pp
NASDAQ               28.90%          4.26%         133.6%         149.1%         -15.5pp
Nikkei 225           25.78%          4.18%          63.3%         147.8%         -84.4pp

========================================================================================================================
KEY INSIGHTS:
========================================================================================================================
- Higher average volatility → Greater volatility decay cost
- Leverage efficiency declines as volatility increases
- High volatility periods show significantly worse leveraged performance
- Volatility drag can cost 5-15% annually in high volatility environments
========================================================================================================================
