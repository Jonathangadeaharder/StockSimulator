# Contributing to StockSimulator

Thank you for your interest in contributing to StockSimulator! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and professional in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/StockSimulator.git
   cd StockSimulator
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/Jonathangadeaharder/StockSimulator.git
   ```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Installation

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install development dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Install pre-commit hooks** (optional but recommended):
   ```bash
   pre-commit install
   ```

### Verify Installation

Run the test suite to ensure everything is set up correctly:

```bash
pytest tests/ -v
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or modifications

### 2. Make Changes

- Write clean, readable code
- Follow the code style guidelines (see below)
- Add or update tests as needed
- Update documentation as needed

### 3. Test Your Changes

Run the full test suite:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=historical_data --cov=src/stocksimulator --cov-report=html

# Run specific test file
pytest tests/test_financial_calculations.py -v
```

### 4. Format and Lint

```bash
# Format code with black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 historical_data/ src/stocksimulator/ tests/ --max-line-length=120

# Security check with bandit
bandit -r historical_data/ src/stocksimulator/ -ll
```

### 5. Commit Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add feature: description of what you added

- Bullet point of major change 1
- Bullet point of major change 2

Fixes #issue_number (if applicable)"
```

Commit message guidelines:
- Use present tense ("Add feature" not "Added feature")
- First line should be under 72 characters
- Reference relevant issues with #issue_number

### 6. Keep Your Branch Updated

```bash
git fetch upstream
git rebase upstream/main
```

### 7. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

## Code Style

### Python Style Guidelines

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 120 characters (not 79)
- **Quotes**: Use single quotes for strings unless double quotes avoid escapes
- **Imports**: Organized by stdlib, third-party, local (use isort)
- **Type hints**: Strongly encouraged for all functions
- **Docstrings**: Google style for all public functions/classes

### Example Function

```python
from typing import List, Dict, Optional


def calculate_sharpe_ratio(
    returns: List[float],
    risk_free_rate: float = 0.02,
    periods_per_year: int = 252
) -> float:
    """
    Calculate the Sharpe ratio for a series of returns.

    Args:
        returns: List of period returns
        risk_free_rate: Annual risk-free rate (default: 2%)
        periods_per_year: Number of periods per year (default: 252 for daily)

    Returns:
        Sharpe ratio as a float

    Example:
        >>> returns = [0.01, 0.02, -0.01, 0.03]
        >>> sharpe = calculate_sharpe_ratio(returns)
        >>> print(f"Sharpe Ratio: {sharpe:.3f}")
    """
    if len(returns) < 2:
        return 0.0

    # Calculate mean return
    mean_return = sum(returns) / len(returns)
    annualized_return = (1 + mean_return) ** periods_per_year - 1

    # Calculate volatility
    variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
    volatility = (variance ** 0.5) * (periods_per_year ** 0.5)

    # Calculate Sharpe
    if volatility == 0:
        return 0.0

    sharpe = (annualized_return - risk_free_rate) / volatility

    return sharpe
```

### Code Organization

- **One class per file** (with rare exceptions)
- **Group related functions** together
- **Use meaningful names** that describe purpose
- **Keep functions focused** - do one thing well
- **Avoid magic numbers** - use named constants

## Testing

### Test Structure

Tests are organized in the `tests/` directory:

```
tests/
├── test_financial_calculations.py  # Core financial calculations
├── test_historical_validation.py   # Historical data validation
├── test_models.py                  # Data model tests
├── test_core.py                    # Core module tests
└── test_integration.py             # Integration tests
```

### Writing Tests

Use `pytest` for all tests:

```python
import pytest
from stocksimulator.models.portfolio import Portfolio


class TestPortfolio:
    """Test suite for Portfolio model."""

    def test_create_portfolio(self):
        """Test portfolio creation."""
        portfolio = Portfolio(
            portfolio_id="test_001",
            name="Test Portfolio",
            initial_cash=100000.0
        )

        assert portfolio.portfolio_id == "test_001"
        assert portfolio.name == "Test Portfolio"
        assert portfolio.cash == 100000.0
        assert len(portfolio.positions) == 0

    def test_invalid_allocation(self):
        """Test that invalid allocations raise ValueError."""
        portfolio = Portfolio("test_002", "Test", 100000.0)

        with pytest.raises(ValueError):
            portfolio.rebalance({'AAPL': 150}, {'AAPL': 100.0})  # >100%
```

### Test Coverage

- Aim for **>90% code coverage**
- Test **edge cases** and error conditions
- Include **integration tests** for complex workflows
- Add **regression tests** for fixed bugs

## Documentation

### Code Documentation

- **All public functions/classes** must have docstrings
- Use **Google-style docstrings**
- Include **type hints** in function signatures
- Add **examples** for complex functions

### README and Guides

- Update README.md if adding major features
- Add guides to `docs/guides/` for new workflows
- Update API documentation in `docs/api/`

### Inline Comments

Use comments sparingly and only when:
- Explaining **why**, not what
- Clarifying **complex algorithms**
- Noting **important assumptions**

```python
# Good: Explains why
# Use sample variance (n-1) for unbiased volatility estimate
variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)

# Bad: States the obvious
# Loop through returns
for r in returns:
    ...
```

## Pull Request Process

### Before Submitting

1. **All tests pass** locally
2. **Code is formatted** (black, isort)
3. **No linting errors** (flake8)
4. **Documentation is updated**
5. **Commit messages are clear**

### Submitting a PR

1. **Push your branch** to your fork
2. **Create a pull request** on GitHub
3. **Fill out the PR template** completely
4. **Link related issues** with "Fixes #issue_number"

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass
- [ ] Added new tests
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

### Review Process

1. **CI checks must pass** (automated)
2. **At least one approval** from maintainers
3. **All comments addressed**
4. **No merge conflicts**

### After Merge

- Delete your feature branch
- Pull latest changes from upstream
- Celebrate! 🎉

## Questions?

- **General questions**: [GitHub Discussions](https://github.com/Jonathangadeaharder/StockSimulator/discussions)
- **Bug reports**: [GitHub Issues](https://github.com/Jonathangadeaharder/StockSimulator/issues)
- **Security issues**: Email (see SECURITY.md)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to StockSimulator! Your efforts help make this project better for everyone.
