# StockSimulator Jupyter Notebooks

Interactive tutorials for learning StockSimulator's features.

## Notebooks

### 1. Getting Started (`01_getting_started.ipynb`)
- Load historical data
- Create a simple strategy
- Run your first backtest
- Analyze results
- Visualize equity curves

**Recommended for**: Beginners

### 2. Strategy Comparison (`02_strategy_comparison.ipynb`)
- Compare multiple strategies side-by-side
- Analyze risk-adjusted returns
- Visualize performance differences
- Rank strategies by Sharpe ratio

**Recommended for**: Intermediate users

### 3. Optimization (`03_optimization.ipynb`)
- Grid search parameter optimization
- Walk-forward analysis (out-of-sample testing)
- Position sizing with Kelly Criterion
- Avoiding overfitting

**Recommended for**: Advanced users

## Requirements

```bash
# Core requirements
pip install jupyter pandas

# Optional (for visualization)
pip install matplotlib
```

## Running the Notebooks

1. Install Jupyter:
```bash
pip install jupyter
```

2. Navigate to notebooks directory:
```bash
cd notebooks
```

3. Start Jupyter:
```bash
jupyter notebook
```

4. Open a notebook in your browser

## Data Requirements

The notebooks expect historical data in the `../historical_data/` directory.

- `sp500_stooq_daily.csv` - Required for all notebooks
- `tlt_stooq_daily.csv` - Optional, for multi-asset strategies

Download data using:
```python
from stocksimulator.downloaders import YahooFinanceDownloader

downloader = YahooFinanceDownloader()
spy = downloader.download('SPY')
# Save to CSV or use directly
```

## Tips

1. **Run cells in order**: Notebooks build on previous cells
2. **Modify parameters**: Try different lookback periods, allocations, etc.
3. **Add your own strategies**: Use the examples as templates
4. **Visualize results**: Install matplotlib for charts
5. **Save your work**: Use File > Download to save notebooks

## Next Steps

After completing the notebooks:
1. Create your own custom strategies
2. Run optimization on your strategies
3. Generate HTML reports with `HTMLReportGenerator`
4. Test robustness with Monte Carlo simulation
5. Analyze tax impact on returns

## Support

For issues or questions:
- Check the main README.md
- Review the examples/ directory
- Consult the source code documentation
