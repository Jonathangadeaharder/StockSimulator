# Historical Index Data - Download Summary

This directory contains the longest available **daily** historical data for major global stock market indices.

## Downloaded Datasets

### 1. S&P 500 Index

#### **sp500_stooq_daily.csv** ⭐ LONGEST DAILY DATA
- **Source**: Stooq.com
- **Date Range**: May 1, 1789 - November 7, 2025
- **Duration**: 236+ years
- **Records**: 39,570 daily observations
- **Format**: CSV (Date, Open, High, Low, Close, Volume)
- **Note**: Early data (pre-1871) is reconstructed historical data

#### **shiller_sp500.xls**
- **Source**: Robert Shiller (Yale University)
- **Date Range**: January 1871 - September 2023
- **Duration**: 152 years
- **Records**: Monthly data (~1,834 observations)
- **Format**: Excel (.xls)
- **Includes**: Price, Dividend, Earnings, CPI, Long Interest Rate, Real Price, Real Dividend, Real Earnings, PE10 (CAPE)
- **Note**: This is the famous Shiller dataset used for long-term market analysis

#### **sp500_github_monthly.csv**
- **Source**: GitHub datasets repository (Shiller data in CSV format)
- **Date Range**: January 1871 - September 2023
- **Duration**: 152 years
- **Records**: 1,834 monthly observations
- **Format**: CSV version of Shiller data

---

### 2. Dow Jones Industrial Average (DJIA)

#### **djia_stooq_daily.csv** ⭐ OLDEST INDEX
- **Source**: Stooq.com
- **Date Range**: May 27, 1896 - November 7, 2025
- **Duration**: 129+ years
- **Records**: 33,510 daily observations
- **Format**: CSV (Date, Open, High, Low, Close, Volume)
- **Note**: The DJIA was first calculated on May 26, 1896. This is one of the oldest continuous stock indices.

---

### 3. NASDAQ Composite

#### **nasdaq_fred.csv**
- **Source**: FRED (Federal Reserve Economic Data - St. Louis Fed)
- **Date Range**: February 5, 1971 - November 6, 2025
- **Duration**: 54+ years
- **Records**: 14,286 daily observations
- **Format**: CSV (observation_date, NASDAQCOM)
- **Note**: NASDAQ Composite launched on Feb 5, 1971 at base value of 100

---

### 4. Nikkei 225 (Japan)

#### **nikkei225_fred.csv** ⭐ LONGEST ASIAN INDEX
- **Source**: FRED (Federal Reserve Economic Data - St. Louis Fed)
- **Date Range**: May 16, 1949 - November 7, 2025
- **Duration**: 76+ years
- **Records**: 19,956 daily observations
- **Format**: CSV (observation_date, NIKKEI225)
- **Note**: Covers entire post-WWII period of Japanese economic history

---

### 5. MSCI World & MSCI ACWI (Global Indices)

#### **msci_world_urth_stooq_daily.csv**
- **Source**: Stooq.com (iShares MSCI World ETF - URTH)
- **Date Range**: January 19, 2012 - November 7, 2025
- **Duration**: 13+ years
- **Records**: 3,274 daily observations
- **Format**: CSV (Date, Open, High, Low, Close, Volume)
- **Note**: ETF tracking MSCI World index (developed markets)

#### **msci_acwi_stooq_daily.csv**
- **Source**: Stooq.com (iShares MSCI ACWI ETF)
- **Date Range**: March 28, 2008 - November 7, 2025
- **Duration**: 17+ years
- **Records**: 4,434 daily observations
- **Format**: CSV (Date, Open, High, Low, Close, Volume)
- **Coverage**: 23 Developed Markets + 24 Emerging Markets countries
- **Note**: ACWI = All Country World Index. Most comprehensive global equity benchmark.

> **Important**: The actual MSCI World and MSCI ACWI indices have data back to 1969, but this requires downloading directly from MSCI's website (https://www.msci.com/real-time-index-data-search) which may require registration.

---

### 6. VIX (Volatility Index)

#### **vix_daily.csv**
- **Source**: GitHub datasets repository
- **Records**: 9,054 daily observations
- **Format**: CSV
- **Note**: CBOE Volatility Index, measuring market volatility expectations

---

## Data Quality Notes

### Reconstructed Historical Data
- **S&P 500 pre-1957**: Data before March 1957 is based on historical reconstructions, as the modern 500-stock index launched on March 4, 1957
- **S&P 500 pre-1871**: Data from 1789-1871 (Stooq) is heavily reconstructed based on various historical sources

### Most Reliable Long-term Data
1. **DJIA from Stooq** (1896-present): 129 years of actual index history
2. **Shiller S&P 500** (1871-present): 152 years, widely cited in academic research
3. **Nikkei 225 from FRED** (1949-present): 76 years of official data

---

## Usage Recommendations

### For Backtesting & Research

- **US Large Cap**: Use `sp500_stooq_daily.csv` or `djia_stooq_daily.csv`
- **US Tech Stocks**: Use `nasdaq_fred.csv` (from 1971)
- **Asian Markets**: Use `nikkei225_fred.csv`
- **Global Developed Markets**: Use `msci_world_urth_stooq_daily.csv` or download from MSCI directly
- **Global All Markets**: Use `msci_acwi_stooq_daily.csv`
- **Long-term Analysis with Fundamentals**: Use `shiller_sp500.xls` (includes P/E, dividends, earnings)

### For Maximum Historical Depth

**Daily data ranking**:
1. S&P 500 (Stooq): 1789 - 236 years ⭐
2. DJIA (Stooq): 1896 - 129 years
3. Nikkei 225 (FRED): 1949 - 76 years
4. NASDAQ (FRED): 1971 - 54 years
5. MSCI ACWI ETF: 2008 - 17 years
6. MSCI World ETF: 2012 - 13 years

---

## File Formats

All CSV files follow standard formats:
- **Stooq format**: Date, Open, High, Low, Close, Volume
- **FRED format**: observation_date, [INDEX_CODE]
- **Shiller format**: Date, SP500, Dividend, Earnings, CPI, Long Interest Rate, Real Price, Real Dividend, Real Earnings, PE10

---

## Data Sources & Attribution

1. **Stooq.com** (https://stooq.com) - Free historical market data
2. **FRED** (https://fred.stlouisfed.org) - Federal Reserve Economic Data
3. **Robert Shiller** (http://www.econ.yale.edu/~shiller/data.htm) - Yale University, Nobel Prize-winning economist
4. **GitHub datasets** (https://github.com/datasets) - Community-maintained open data

---

## Next Steps

### To Get Official MSCI Index Data (1969-present):

1. Visit https://www.msci.com/real-time-index-data-search
2. Search for "MSCI World" or "MSCI ACWI"
3. Configure:
   - Interval: Daily
   - Index Type: TR (Total Return) or PR (Price Return)
   - Currency: USD (or your preference)
   - Period: Max available
4. Download as CSV

### Additional Indices to Consider:

- **FTSE 100** (UK, from 1984)
- **STOXX Europe 600** (European markets)
- **DAX** (Germany)
- **CAC 40** (France)
- **Hang Seng** (Hong Kong)
- **Shanghai Composite** (China)
- **BSE Sensex** (India)

---

## License & Terms of Use

Please review the terms of use for each data source:
- FRED data: Free for research and non-commercial use
- Stooq data: Check their terms of service
- Shiller data: Public domain for academic and research purposes
- MSCI data: Subject to MSCI's licensing terms

**Disclaimer**: This data is provided for educational and research purposes. Verify data quality before using for financial decisions or commercial applications.

---

*Last Updated: November 7, 2025*
