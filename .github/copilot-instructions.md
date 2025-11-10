# GitHub Copilot Instructions for StockSimulator

## Project Overview
This is a stock market simulation and analysis tool written in Python. The project analyzes historical stock market data and compares various investment strategies including:
- Dollar-Cost Averaging (DCA)
- Lump-sum investments
- Leveraged ETF strategies
- Monthly vs. periodic investment comparisons

## Project Structure
- **`historical_data/`**: Contains all analysis scripts and downloaded historical market data
  - `download_indices.py`: Downloads historical index data from various sources (FRED, etc.)
  - `analyze_*.py`: Various analysis scripts for different investment strategies
  - `*.md`: Analysis summaries and results in Markdown format

## Coding Standards

### Python Style
- Use Python 3 standard library when possible
- Follow PEP 8 style guidelines
- Use descriptive variable names (e.g., `first_date`, `last_date`, `total_return`)
- Include docstrings for functions and modules
- Use type hints where appropriate

### File Handling
- Use context managers (`with` statements) for file operations
- Handle exceptions gracefully with try-except blocks
- CSV files are the primary data format for historical data

### Data Analysis Conventions
- Date format: `YYYY-MM-DD` (ISO 8601)
- Use `datetime` module for date parsing and calculations
- Financial calculations should be precise (avoid floating point errors where possible)
- Results are typically saved as Markdown files for easy reading

### Script Organization
- Scripts should be executable (`#!/usr/bin/env python3` shebang)
- Include brief module-level docstrings explaining the script's purpose
- Keep analysis scripts focused on a single strategy or comparison
- Output should be human-readable (Markdown tables, clear summaries)

## Common Patterns

### CSV Data Reading
```python
import csv
with open(filename, 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
```

### Date Calculations
```python
from datetime import datetime
first_dt = datetime.strptime(date_str, '%Y-%m-%d')
years = (last_dt - first_dt).days / 365.25
```

### Output Formatting
- Use Markdown format for analysis summaries
- Include tables for numerical comparisons
- Provide clear section headers
- Include key statistics and percentiles

## Dependencies
- The project uses Python standard library only
- No external package dependencies required
- Scripts should work with Python 3.6+

## Testing and Validation
- Verify calculations with `verify_computation_logic.py` when making changes to analysis logic
- Cross-check results across different analysis scripts for consistency
- Ensure downloaded data files are in the expected format before analysis

## Notes for Contributors
- Keep scripts independent and self-contained
- Document any assumptions about data format or market behavior
- Include error handling for missing or malformed data files
- Preserve backward compatibility with existing analysis scripts
