# 2x Leveraged ETF Analysis - Worst Historical Periods

## Executive Summary

This analysis identifies the **worst performing periods for a 2x leveraged S&P 500 ETF** compared to the non-leveraged index, across timeframes of 5-15 years.

### Key Findings

**🏆 WORST PERIOD OVERALL: March 2004 - March 2009 (5 years)**

- **Unleveraged S&P 500**: -7.27% annualized (-31.44% total return)
- **2x Leveraged ETF**: -18.74% annualized (-64.59% total return)
- **Underperformance Gap**: **-11.48% per year**

**Investment Outcome:**
- $10,000 in unleveraged index → **$6,856** (lost $3,144)
- $10,000 in 2x leveraged ETF → **$3,541** (lost $6,459)
- **Difference: $3,315 worse with leverage**

---

## Analysis Methodology

### Dataset Selected: **Daily S&P 500 Data (Stooq)**
- **Period**: 1950 - 2025 (19,172 trading days)
- **Why This Dataset**:
  - Contains daily price data for accurate simulation of daily rebalancing
  - 75+ years of data to test multiple market cycles
  - Includes bull markets, bear markets, crashes, and recoveries

### Simulation Parameters

```
Leverage:              2.0x (daily rebalancing)
TER (Expense Ratio):   0.6% per year (0.00238% per day)
Dividend Yield:        ~2% annual (distributed daily)
Rebalancing:           Daily (if index rises 10%, ETF rises 20% that day)
Time Windows:          5 to 15 years (rolling windows)
```

### Daily Rebalancing Mechanics

A 2x leveraged ETF resets to 2x exposure **every single day**:
- If S&P 500 gains 10% on Day 1 → 2x ETF gains 20%
- If S&P 500 loses 5% on Day 2 → 2x ETF loses 10%

This daily rebalancing creates **volatility decay**:
```
Example over 2 days:
Index:    $100 → $110 (+10%) → $99 (-10%) = -1% total
2x ETF:   $100 → $120 (+20%) → $96 (-20%) = -4% total
```

Even though the index only lost 1%, the 2x ETF lost 4% due to compounding effects.

---

## Top 15 Worst Periods (All Timeframes)

| Rank | Period                      | Years | Lev Return | Unlev Return | Gap/Year |
|------|----------------------------|-------|------------|--------------|----------|
| 1    | Mar 2004 - Mar 2009        | 5.0   | -18.74%    | -7.27%       | **-11.48%** |
| 2    | Feb 2000 - Mar 2009        | 9.0   | -14.51%    | -4.98%       | -9.53%   |
| 3    | Feb 2001 - Mar 2009        | 8.0   | -14.28%    | -4.85%       | -9.43%   |
| 4    | Mar 2000 - Apr 2009        | 9.0   | -13.93%    | -4.60%       | -9.33%   |
| 5    | Mar 2002 - Mar 2009        | 7.0   | -13.71%    | -4.50%       | -9.21%   |
| 6    | Apr 2004 - Apr 2009        | 5.0   | -13.04%    | -3.92%       | -9.12%   |
| 7    | Jun 2007 - Jun 2012        | 5.0   | -10.64%    | -1.71%       | -8.93%   |
| 8    | Feb 2004 - Feb 2009        | 5.0   | -13.07%    | -4.21%       | -8.87%   |
| 9    | Jan 2001 - Feb 2009        | 8.0   | -12.94%    | -4.18%       | -8.76%   |
| 10   | Nov 2000 - Dec 2008        | 8.0   | -12.77%    | -4.16%       | -8.61%   |

**Pattern**: All top 10 worst periods include the 2008 Financial Crisis or the Dot-com crash + Financial Crisis combination.

---

## Worst Period By Window Length

### 5-Year Window
**March 2004 - March 2009**
- Leveraged: -18.74% ann. (total: -64.59%)
- Unleveraged: -7.27% ann. (total: -31.44%)
- **Gap: -11.48% per year**

### 6-Year Window
**December 1968 - December 1974** (Stagflation Era)
- Leveraged: -12.83% ann. (total: -56.05%)
- Unleveraged: -5.40% ann. (total: -28.27%)
- Gap: -7.43% per year

### 7-Year Window
**March 2002 - March 2009**
- Leveraged: -13.71% ann. (total: -64.39%)
- Unleveraged: -4.50% ann. (total: -27.54%)
- Gap: -9.21% per year

### 8-Year Window
**February 2001 - March 2009**
- Leveraged: -14.28% ann. (total: -70.91%)
- Unleveraged: -4.85% ann. (total: -32.85%)
- Gap: -9.43% per year

### 9-Year Window
**February 2000 - March 2009** (Dot-com Crash → Financial Crisis)
- Leveraged: -14.51% ann. (total: -75.70%)
- Unleveraged: -4.98% ann. (total: -36.94%)
- **Gap: -9.53% per year**

### 10-Year Window
**February 1999 - March 2009**
- Leveraged: -11.71% ann. (total: -71.27%)
- Unleveraged: -3.51% ann. (total: -30.06%)
- Gap: -8.20% per year

### 15-Year Window
**August 2000 - September 2015**
- Leveraged: 2.85% ann. (total: 52.47%)
- Unleveraged: 3.79% ann. (total: 74.89%)
- Gap: -0.94% per year

---

## Detailed Analysis: Worst Period (Mar 2004 - Mar 2009)

### Timeline Context
This 5-year period captures:
- **2004-2007**: Housing bubble buildup, moderate gains
- **2007-2008**: Subprime mortgage crisis begins
- **Sept 2008**: Lehman Brothers collapse, market crash
- **2008-2009**: Financial crisis bottom (March 2009)

### Market Characteristics
- **Annualized Volatility**: 22.34%
- **Positive Days**: 685 / 1,260 (54.4%)
- **Negative Days**: 575 / 1,260 (45.6%)

Despite having slightly more positive days than negative, the magnitude and timing of losses created severe volatility decay.

### Why This Period Was Devastating for Leveraged ETFs

1. **High Volatility**: 22.34% annualized volatility amplified volatility decay
2. **Sharp Drawdowns**: Major crashes (especially Oct 2008) caused massive leveraged losses
3. **Choppy Recovery**: Multiple false rallies and reversals compounded losses
4. **Daily Rebalancing Cost**: Each day's volatility eroded returns

### Leverage Efficiency Breakdown

**Expected Performance** (theoretical 2x):
- If unleveraged returned -7.27%, perfect 2x leverage would return -14.53%

**Actual Performance**:
- 2x leveraged returned -18.74%

**Shortfall**: -4.21% per year below theoretical 2x
- This represents the cost of volatility decay and fees

**Leverage Ratio**: 0.52x
- The leveraged ETF delivered only 0.52x the unleveraged return
- In a perfect world, it should deliver 2.0x
- This is a 74% failure of the leverage mechanism over 5 years

---

## Historical Context: Other Notable Bad Periods

### Great Depression Era (1929-1934) - 5 Years
Using monthly data from Shiller dataset:
- Unleveraged: -17.31% ann. (total: -61.34%)
- 2x Leveraged: -41.92% ann. (total: -93.39%)
- **Gap: -24.61% per year**

This was the absolute worst in history, but predates modern ETF markets.

### Stagflation Era (1968-1974) - 6 Years
- Unleveraged: -5.40% ann.
- 2x Leveraged: -12.83% ann.
- Gap: -7.43% per year

### Dot-com Crash Only (2000-2002)
Not the worst because it was followed by recovery before 2004.

---

## Why Leveraged ETFs Underperform in These Periods

### 1. **Volatility Decay**
Daily rebalancing means losses compound faster than gains:

```
Day 1: Index +10% → 2x ETF +20%
Day 2: Index -10% → 2x ETF -20%

Result:
Index: 1.10 × 0.90 = 0.99 (-1%)
2x ETF: 1.20 × 0.80 = 0.96 (-4%)
```

### 2. **Path Dependency**
The order of returns matters enormously:
- A 50% drop requires a 100% gain to break even
- A 2x leveraged 50% drop (-100%) means total wipeout

### 3. **Compounding in Reverse**
Losses compound more severely:
- Losing 20% means you need 25% gain to recover
- Losing 50% means you need 100% gain to recover
- Losing 75% means you need 300% gain to recover

### 4. **Fee Drag**
0.6% TER × 2 (leverage) = effective 1.2% drag on the leveraged position

### 5. **Market Regime**
Choppy, sideways, or declining markets are worst:
- Multiple reversals maximize rebalancing costs
- Each down day is amplified 2x
- Recovery requires 2x gains just to match unleveraged

---

## Key Takeaways

### ✅ When Leveraged ETFs Work Well
- **Strong, steady bull markets** with low volatility
- **Short holding periods** (days to weeks)
- **Low volatility environments**
- **Trending markets** (up or down, but consistent)

### ❌ When Leveraged ETFs Fail
- **Choppy, sideways markets** ← WORST
- **High volatility periods** (like 2008)
- **Long holding periods** (5+ years)
- **Bear markets followed by slow recovery**
- **Multiple boom-bust cycles** (like 2000-2009)

### 🎯 The Answer to Your Question

**Most adequate dataset**: **Daily S&P 500 data from Stooq (1950-2025)**

**Worst 5-15 year timeframe**: **March 2004 - March 2009 (5 years)**
- This period encompasses the 2008 Financial Crisis
- High volatility (22.34% annualized)
- Severe drawdowns followed by choppy recovery
- 2x leveraged ETF lost 64.59% vs 31.44% for unleveraged
- **Underperformed by 11.48% per year**

### 📊 Investment Scenario
If you invested $10,000 in March 2004:
- **Unleveraged S&P 500** (with dividends): $6,856 in March 2009
- **2x Leveraged ETF** (with 0.6% TER): $3,541 in March 2009
- **You lost an extra $3,315** by using leverage

---

## Recommendations for Investors

1. **Avoid leveraged ETFs for long-term holdings** (5+ years)
2. **Use only in trending markets** with clear direction
3. **Monitor volatility** - exit when volatility spikes
4. **Consider shorter timeframes** if using leverage
5. **Understand that "2x returns" only applies daily**, not over longer periods
6. **During crashes, leveraged ETFs can lose MORE than 2x** the index loss

---

## Data Sources

- **Daily Price Data**: Stooq.com S&P 500 dataset (1950-2025)
- **Historical Fundamentals**: Robert Shiller S&P 500 dataset (1871-2023)
- **Analysis Period**: 1950-2025 (75 years, 19,172 trading days)
- **Windows Analyzed**: 8,723 different 5-15 year periods

---

## Files in This Analysis

1. `analyze_leveraged_etf.py` - Monthly data analysis (historical, 1871+)
2. `analyze_leveraged_modern.py` - Monthly data analysis (modern, 1950+)
3. `analyze_leveraged_daily.py` - **Daily data analysis (most accurate)**
4. `LEVERAGED_ETF_ANALYSIS.md` - This summary report

**Recommended**: Use `analyze_leveraged_daily.py` for the most accurate simulation of daily rebalancing effects.

---

*Analysis completed: November 2025*
*Dataset: S&P 500 daily prices (1950-2025) with 2% dividend yield*
*Simulation: 2.0x leverage, 0.6% TER, daily rebalancing*
