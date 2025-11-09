╔======================================================================================================================╗
║                                   STATISTICAL ROBUSTNESS ANALYSIS                                                    ║
║                         Bootstrap Analysis with Random Time Period Sampling                                          ║
╚======================================================================================================================╝

Methodology:
- Randomly sample non-overlapping time periods from historical data
- Run pairwise comparison on each sample
- Calculate statistics: mean, median, std dev, confidence intervals
- Verify findings are consistent across different market periods


========================================================================================================================
ANALYZING: S&P 500
========================================================================================================================

5-YEAR PERIODS:
------------------------------------------------------------------------------------------------------------------------
Loading data for S&P 500...
Sampling 100 random 5-year periods...
Successfully sampled 8 periods
Analyzing 8 samples...
Successfully analyzed 8 samples

========================================================================================================================
ROBUSTNESS ANALYSIS: S&P 500 (5-Year Periods)
========================================================================================================================
Number of random samples analyzed: 8

------------------------------------------------------------------------------------------------------------------------
COMPARISON 1: Lump-Sum 2x Leveraged vs Monthly Non-Leveraged
------------------------------------------------------------------------------------------------------------------------

Win Rate Across Samples: 100.0%
(Lump-sum 2x won in 8/8 random periods)

Return Gap Distribution (Lump 2x - Non-Lev, annualized %):

  Mean:                 13.54
  Median:               17.78
  Std Dev:              10.61
  Min:                  -2.13
  Max:                  33.37
  95% CI:            [  -2.13,   33.37]
  90% CI:            [  -2.13,   33.37]


Lump-Sum 2x Return Distribution (annualized %):

  Mean:                 18.40
  Median:               22.86
  Std Dev:              15.35
  Min:                  -4.83
  Max:                  47.46
  95% CI:            [  -4.83,   47.46]
  90% CI:            [  -4.83,   47.46]


------------------------------------------------------------------------------------------------------------------------
COMPARISON 2: Monthly 2x Leveraged vs Monthly Non-Leveraged
------------------------------------------------------------------------------------------------------------------------

Win Rate Across Samples: 75.0%
(Monthly 2x won in 6/8 random periods)

Return Gap Distribution (Monthly 2x - Non-Lev, annualized %):

  Mean:                  3.92
  Median:                5.10
  Std Dev:               6.03
  Min:                  -5.93
  Max:                  16.02
  95% CI:            [  -5.93,   16.02]
  90% CI:            [  -5.93,   16.02]


Monthly 2x Return Distribution (annualized %):

  Mean:                  8.78
  Median:                9.72
  Std Dev:              10.84
  Min:                  -8.63
  Max:                  30.11
  95% CI:            [  -8.63,   30.11]
  90% CI:            [  -8.63,   30.11]



10-YEAR PERIODS:
------------------------------------------------------------------------------------------------------------------------
Loading data for S&P 500...
Sampling 100 random 10-year periods...
Successfully sampled 4 periods
Analyzing 4 samples...
Successfully analyzed 4 samples

========================================================================================================================
ROBUSTNESS ANALYSIS: S&P 500 (10-Year Periods)
========================================================================================================================
Number of random samples analyzed: 4

------------------------------------------------------------------------------------------------------------------------
COMPARISON 1: Lump-Sum 2x Leveraged vs Monthly Non-Leveraged
------------------------------------------------------------------------------------------------------------------------

Win Rate Across Samples: 100.0%
(Lump-sum 2x won in 4/4 random periods)

Return Gap Distribution (Lump 2x - Non-Lev, annualized %):

  Mean:                  9.92
  Median:               11.97
  Std Dev:               3.76
  Min:                   5.04
  Max:                  14.83
  95% CI:            [   5.04,   14.83]
  90% CI:            [   5.04,   14.83]


Lump-Sum 2x Return Distribution (annualized %):

  Mean:                 15.80
  Median:               16.77
  Std Dev:               5.82
  Min:                  10.34
  Max:                  24.93
  95% CI:            [  10.34,   24.93]
  90% CI:            [  10.34,   24.93]


------------------------------------------------------------------------------------------------------------------------
COMPARISON 2: Monthly 2x Leveraged vs Monthly Non-Leveraged
------------------------------------------------------------------------------------------------------------------------

Win Rate Across Samples: 100.0%
(Monthly 2x won in 4/4 random periods)

Return Gap Distribution (Monthly 2x - Non-Lev, annualized %):

  Mean:                  5.45
  Median:                4.75
  Std Dev:               3.27
  Min:                   2.31
  Max:                  10.91
  95% CI:            [   2.31,   10.91]
  90% CI:            [   2.31,   10.91]


Monthly 2x Return Distribution (annualized %):

  Mean:                 11.34
  Median:                9.54
  Std Dev:               5.78
  Min:                   5.66
  Max:                  21.01
  95% CI:            [   5.66,   21.01]
  90% CI:            [   5.66,   21.01]



========================================================================================================================
ANALYZING: DJIA
========================================================================================================================

5-YEAR PERIODS:
------------------------------------------------------------------------------------------------------------------------
Loading data for DJIA...
Sampling 100 random 5-year periods...
Successfully sampled 8 periods
Analyzing 8 samples...
Successfully analyzed 8 samples

========================================================================================================================
ROBUSTNESS ANALYSIS: DJIA (5-Year Periods)
========================================================================================================================
Number of random samples analyzed: 8

------------------------------------------------------------------------------------------------------------------------
COMPARISON 1: Lump-Sum 2x Leveraged vs Monthly Non-Leveraged
------------------------------------------------------------------------------------------------------------------------

Win Rate Across Samples: 100.0%
(Lump-sum 2x won in 8/8 random periods)

Return Gap Distribution (Lump 2x - Non-Lev, annualized %):

  Mean:                 11.20
  Median:               12.38
  Std Dev:               9.21
  Min:                  -2.39
  Max:                  30.89
  95% CI:            [  -2.39,   30.89]
  90% CI:            [  -2.39,   30.89]


Lump-Sum 2x Return Distribution (annualized %):

  Mean:                 15.54
  Median:               12.94
  Std Dev:              11.75
  Min:                  -4.99
  Max:                  38.44
  95% CI:            [  -4.99,   38.44]
  90% CI:            [  -4.99,   38.44]


------------------------------------------------------------------------------------------------------------------------
COMPARISON 2: Monthly 2x Leveraged vs Monthly Non-Leveraged
------------------------------------------------------------------------------------------------------------------------

Win Rate Across Samples: 75.0%
(Monthly 2x won in 6/8 random periods)

Return Gap Distribution (Monthly 2x - Non-Lev, annualized %):

  Mean:                  3.28
  Median:                4.11
  Std Dev:               3.59
  Min:                  -3.37
  Max:                   7.53
  95% CI:            [  -3.37,    7.53]
  90% CI:            [  -3.37,    7.53]


Monthly 2x Return Distribution (annualized %):

  Mean:                  7.62
  Median:               11.03
  Std Dev:               7.04
  Min:                  -5.97
  Max:                  15.40
  95% CI:            [  -5.97,   15.40]
  90% CI:            [  -5.97,   15.40]



10-YEAR PERIODS:
------------------------------------------------------------------------------------------------------------------------
Loading data for DJIA...
Sampling 100 random 10-year periods...
Successfully sampled 5 periods
Analyzing 5 samples...
Successfully analyzed 5 samples

========================================================================================================================
ROBUSTNESS ANALYSIS: DJIA (10-Year Periods)
========================================================================================================================
Number of random samples analyzed: 5

------------------------------------------------------------------------------------------------------------------------
COMPARISON 1: Lump-Sum 2x Leveraged vs Monthly Non-Leveraged
------------------------------------------------------------------------------------------------------------------------

Win Rate Across Samples: 80.0%
(Lump-sum 2x won in 4/5 random periods)

Return Gap Distribution (Lump 2x - Non-Lev, annualized %):

  Mean:                  7.63
  Median:               13.78
  Std Dev:               9.02
  Min:                  -5.10
  Max:                  15.71
  95% CI:            [  -5.10,   15.71]
  90% CI:            [  -5.10,   15.71]


Lump-Sum 2x Return Distribution (annualized %):

  Mean:                 10.29
  Median:               19.52
  Std Dev:              12.99
  Min:                  -8.68
  Max:                  21.48
  95% CI:            [  -8.68,   21.48]
  90% CI:            [  -8.68,   21.48]


------------------------------------------------------------------------------------------------------------------------
COMPARISON 2: Monthly 2x Leveraged vs Monthly Non-Leveraged
------------------------------------------------------------------------------------------------------------------------

Win Rate Across Samples: 60.0%
(Monthly 2x won in 3/5 random periods)

Return Gap Distribution (Monthly 2x - Non-Lev, annualized %):

  Mean:                  1.36
  Median:                4.01
  Std Dev:               4.51
  Min:                  -5.82
  Max:                   6.10
  95% CI:            [  -5.82,    6.10]
  90% CI:            [  -5.82,    6.10]


Monthly 2x Return Distribution (annualized %):

  Mean:                  4.02
  Median:                7.82
  Std Dev:               8.66
  Min:                  -9.41
  Max:                  13.79
  95% CI:            [  -9.41,   13.79]
  90% CI:            [  -9.41,   13.79]



========================================================================================================================
ANALYZING: NASDAQ
========================================================================================================================

5-YEAR PERIODS:
------------------------------------------------------------------------------------------------------------------------
Loading data for NASDAQ...
Sampling 100 random 5-year periods...
Successfully sampled 6 periods
Analyzing 6 samples...
Successfully analyzed 6 samples

========================================================================================================================
ROBUSTNESS ANALYSIS: NASDAQ (5-Year Periods)
========================================================================================================================
Number of random samples analyzed: 6

------------------------------------------------------------------------------------------------------------------------
COMPARISON 1: Lump-Sum 2x Leveraged vs Monthly Non-Leveraged
------------------------------------------------------------------------------------------------------------------------

Win Rate Across Samples: 100.0%
(Lump-sum 2x won in 6/6 random periods)

Return Gap Distribution (Lump 2x - Non-Lev, annualized %):

  Mean:                 16.30
  Median:               18.97
  Std Dev:              16.83
  Min:                  -3.26
  Max:                  47.60
  95% CI:            [  -3.26,   47.60]
  90% CI:            [  -3.26,   47.60]


Lump-Sum 2x Return Distribution (annualized %):

  Mean:                 23.64
  Median:               25.02
  Std Dev:              20.55
  Min:                  -0.97
  Max:                  63.91
  95% CI:            [  -0.97,   63.91]
  90% CI:            [  -0.97,   63.91]


------------------------------------------------------------------------------------------------------------------------
COMPARISON 2: Monthly 2x Leveraged vs Monthly Non-Leveraged
------------------------------------------------------------------------------------------------------------------------

Win Rate Across Samples: 83.3%
(Monthly 2x won in 5/6 random periods)

Return Gap Distribution (Monthly 2x - Non-Lev, annualized %):

  Mean:                  6.31
  Median:                6.57
  Std Dev:               6.08
  Min:                  -1.46
  Max:                  17.44
  95% CI:            [  -1.46,   17.44]
  90% CI:            [  -1.46,   17.44]


Monthly 2x Return Distribution (annualized %):

  Mean:                 13.64
  Median:               13.26
  Std Dev:              10.49
  Min:                   0.83
  Max:                  33.75
  95% CI:            [   0.83,   33.75]
  90% CI:            [   0.83,   33.75]



10-YEAR PERIODS:
------------------------------------------------------------------------------------------------------------------------
Loading data for NASDAQ...
Sampling 100 random 10-year periods...
Successfully sampled 3 periods
Analyzing 3 samples...
Successfully analyzed 3 samples

========================================================================================================================
ROBUSTNESS ANALYSIS: NASDAQ (10-Year Periods)
========================================================================================================================
Number of random samples analyzed: 3

------------------------------------------------------------------------------------------------------------------------
COMPARISON 1: Lump-Sum 2x Leveraged vs Monthly Non-Leveraged
------------------------------------------------------------------------------------------------------------------------

Win Rate Across Samples: 100.0%
(Lump-sum 2x won in 3/3 random periods)

Return Gap Distribution (Lump 2x - Non-Lev, annualized %):

  Mean:                 10.40
  Median:               10.79
  Std Dev:               6.63
  Min:                   2.09
  Max:                  18.32
  95% CI:            [   2.09,   18.32]
  90% CI:            [   2.09,   18.32]


Lump-Sum 2x Return Distribution (annualized %):

  Mean:                 17.22
  Median:               18.28
  Std Dev:               6.81
  Min:                   8.40
  Max:                  24.99
  95% CI:            [   8.40,   24.99]
  90% CI:            [   8.40,   24.99]


------------------------------------------------------------------------------------------------------------------------
COMPARISON 2: Monthly 2x Leveraged vs Monthly Non-Leveraged
------------------------------------------------------------------------------------------------------------------------

Win Rate Across Samples: 100.0%
(Monthly 2x won in 3/3 random periods)

Return Gap Distribution (Monthly 2x - Non-Lev, annualized %):

  Mean:                  6.12
  Median:                6.45
  Std Dev:               0.55
  Min:                   5.35
  Max:                   6.58
  95% CI:            [   5.35,    6.58]
  90% CI:            [   5.35,    6.58]


Monthly 2x Return Distribution (annualized %):

  Mean:                 12.95
  Median:               12.89
  Std Dev:               0.12
  Min:                  12.84
  Max:                  13.12
  95% CI:            [  12.84,   13.12]
  90% CI:            [  12.84,   13.12]



========================================================================================================================
ANALYZING: Nikkei 225
========================================================================================================================

5-YEAR PERIODS:
------------------------------------------------------------------------------------------------------------------------
Loading data for Nikkei 225...
Sampling 100 random 5-year periods...
Successfully sampled 9 periods
Analyzing 9 samples...
Successfully analyzed 9 samples

========================================================================================================================
ROBUSTNESS ANALYSIS: Nikkei 225 (5-Year Periods)
========================================================================================================================
Number of random samples analyzed: 9

------------------------------------------------------------------------------------------------------------------------
COMPARISON 1: Lump-Sum 2x Leveraged vs Monthly Non-Leveraged
------------------------------------------------------------------------------------------------------------------------

Win Rate Across Samples: 66.7%
(Lump-sum 2x won in 5/9 random periods)

Return Gap Distribution (Lump 2x - Non-Lev, annualized %):

  Mean:                 16.76
  Median:               16.76
  Std Dev:              24.56
  Min:                 -10.75
  Max:                  52.24
  95% CI:            [ -10.75,   52.24]
  90% CI:            [ -10.75,   52.24]


Lump-Sum 2x Return Distribution (annualized %):

  Mean:                 24.24
  Median:               23.92
  Std Dev:              28.41
  Min:                 -11.19
  Max:                  65.51
  95% CI:            [ -11.19,   65.51]
  90% CI:            [ -11.19,   65.51]


------------------------------------------------------------------------------------------------------------------------
COMPARISON 2: Monthly 2x Leveraged vs Monthly Non-Leveraged
------------------------------------------------------------------------------------------------------------------------

Win Rate Across Samples: 77.8%
(Monthly 2x won in 7/9 random periods)

Return Gap Distribution (Monthly 2x - Non-Lev, annualized %):

  Mean:                  7.44
  Median:                6.59
  Std Dev:               7.10
  Min:                  -4.57
  Max:                  17.72
  95% CI:            [  -4.57,   17.72]
  90% CI:            [  -4.57,   17.72]


Monthly 2x Return Distribution (annualized %):

  Mean:                 14.92
  Median:               13.60
  Std Dev:              12.29
  Min:                  -6.77
  Max:                  33.29
  95% CI:            [  -6.77,   33.29]
  90% CI:            [  -6.77,   33.29]



10-YEAR PERIODS:
------------------------------------------------------------------------------------------------------------------------
Loading data for Nikkei 225...
Sampling 100 random 10-year periods...
Successfully sampled 5 periods
Analyzing 5 samples...
Successfully analyzed 5 samples

========================================================================================================================
ROBUSTNESS ANALYSIS: Nikkei 225 (10-Year Periods)
========================================================================================================================
Number of random samples analyzed: 5

------------------------------------------------------------------------------------------------------------------------
COMPARISON 1: Lump-Sum 2x Leveraged vs Monthly Non-Leveraged
------------------------------------------------------------------------------------------------------------------------

Win Rate Across Samples: 80.0%
(Lump-sum 2x won in 4/5 random periods)

Return Gap Distribution (Lump 2x - Non-Lev, annualized %):

  Mean:                 12.06
  Median:               15.03
  Std Dev:              13.17
  Min:                 -13.09
  Max:                  23.60
  95% CI:            [ -13.09,   23.60]
  90% CI:            [ -13.09,   23.60]


Lump-Sum 2x Return Distribution (annualized %):

  Mean:                 15.51
  Median:               19.38
  Std Dev:              16.39
  Min:                 -15.45
  Max:                  29.52
  95% CI:            [ -15.45,   29.52]
  90% CI:            [ -15.45,   29.52]


------------------------------------------------------------------------------------------------------------------------
COMPARISON 2: Monthly 2x Leveraged vs Monthly Non-Leveraged
------------------------------------------------------------------------------------------------------------------------

Win Rate Across Samples: 60.0%
(Monthly 2x won in 3/5 random periods)

Return Gap Distribution (Monthly 2x - Non-Lev, annualized %):

  Mean:                  2.60
  Median:                4.66
  Std Dev:               5.07
  Min:                  -5.57
  Max:                   8.59
  95% CI:            [  -5.57,    8.59]
  90% CI:            [  -5.57,    8.59]


Monthly 2x Return Distribution (annualized %):

  Mean:                  6.05
  Median:               10.92
  Std Dev:               8.85
  Min:                  -7.93
  Max:                  16.45
  95% CI:            [  -7.93,   16.45]
  90% CI:            [  -7.93,   16.45]




========================================================================================================================
ROBUSTNESS SUMMARY: Consistency Check
========================================================================================================================

Key Question: Are win rates consistent across random samples?


S&P 500:
------------------------------------------------------------------------------------------------------------------------
Period     Comparison                               Win %        Gap Mean     Gap Std      95% CI                   
------------------------------------------------------------------------------------------------------------------------
5Y       Lump-Sum 2x vs Monthly Non-Lev                100.0%      13.54%      10.61% [ -2.13%,  33.37%]
           Monthly 2x vs Monthly Non-Lev                  75.0%       3.92%       6.03% [ -5.93%,  16.02%]
10Y       Lump-Sum 2x vs Monthly Non-Lev                100.0%       9.92%       3.76% [  5.04%,  14.83%]
           Monthly 2x vs Monthly Non-Lev                 100.0%       5.45%       3.27% [  2.31%,  10.91%]


DJIA:
------------------------------------------------------------------------------------------------------------------------
Period     Comparison                               Win %        Gap Mean     Gap Std      95% CI                   
------------------------------------------------------------------------------------------------------------------------
5Y       Lump-Sum 2x vs Monthly Non-Lev                100.0%      11.20%       9.21% [ -2.39%,  30.89%]
           Monthly 2x vs Monthly Non-Lev                  75.0%       3.28%       3.59% [ -3.37%,   7.53%]
10Y       Lump-Sum 2x vs Monthly Non-Lev                 80.0%       7.63%       9.02% [ -5.10%,  15.71%]
           Monthly 2x vs Monthly Non-Lev                  60.0%       1.36%       4.51% [ -5.82%,   6.10%]


NASDAQ:
------------------------------------------------------------------------------------------------------------------------
Period     Comparison                               Win %        Gap Mean     Gap Std      95% CI                   
------------------------------------------------------------------------------------------------------------------------
5Y       Lump-Sum 2x vs Monthly Non-Lev                100.0%      16.30%      16.83% [ -3.26%,  47.60%]
           Monthly 2x vs Monthly Non-Lev                  83.3%       6.31%       6.08% [ -1.46%,  17.44%]
10Y       Lump-Sum 2x vs Monthly Non-Lev                100.0%      10.40%       6.63% [  2.09%,  18.32%]
           Monthly 2x vs Monthly Non-Lev                 100.0%       6.12%       0.55% [  5.35%,   6.58%]


Nikkei 225:
------------------------------------------------------------------------------------------------------------------------
Period     Comparison                               Win %        Gap Mean     Gap Std      95% CI                   
------------------------------------------------------------------------------------------------------------------------
5Y       Lump-Sum 2x vs Monthly Non-Lev                 66.7%      16.76%      24.56% [-10.75%,  52.24%]
           Monthly 2x vs Monthly Non-Lev                  77.8%       7.44%       7.10% [ -4.57%,  17.72%]
10Y       Lump-Sum 2x vs Monthly Non-Lev                 80.0%      12.06%      13.17% [-13.09%,  23.60%]
           Monthly 2x vs Monthly Non-Lev                  60.0%       2.60%       5.07% [ -5.57%,   8.59%]


========================================================================================================================
ROBUSTNESS INTERPRETATION:
========================================================================================================================
- Small std dev (<5%) indicates highly robust findings
- Narrow confidence intervals indicate consistent results across time periods
- Wide intervals suggest results vary significantly by market conditions
========================================================================================================================
