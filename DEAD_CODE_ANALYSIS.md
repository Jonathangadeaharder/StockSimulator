# Dead Code Analysis Report
**Date:** 2025-11-10
**Codebase:** StockSimulator Platform
**Total Lines of Code:** 8,922
**Total Python Files:** 45
**Test Coverage:** ~35% of new modules

---

## Executive Summary

With only 35% test coverage, significant dead code exists in the codebase. This analysis identified **88 items of potentially dead code** across 4 main categories:

1. **44 unused utility functions** (entire `utils/` module)
2. **11 unused classes** (including PortfolioManager, 5 strategies, 2 optimizers, 2 position sizers)
3. **1 empty module** (api/__init__.py)
4. **32+ unnecessary imports** (sys/os path manipulation)

**Estimated Dead Code:** ~15-20% of codebase (~1,500-1,800 LOC)

---

## Category 1: Unused Utility Functions (HIGH PRIORITY)

### Status: **ALL 44 FUNCTIONS UNUSED**

The entire `src/stocksimulator/utils/` module (3 files, 44 functions) is exported in `__init__.py` but **never actually used** in examples, tests, or other modules.

#### src/stocksimulator/utils/date_utils.py (16 functions, ~250 LOC)
| Function | Purpose | Used? |
|----------|---------|-------|
| `parse_date()` | Parse date strings | ❌ No |
| `trading_days_between()` | Count trading days | ❌ No |
| `add_trading_days()` | Add N trading days | ❌ No |
| `is_weekend()` | Check if weekend | ❌ No |
| `next_business_day()` | Get next business day | ❌ No |
| `generate_date_range()` | Generate date ranges | ❌ No |
| `get_quarter()` | Get fiscal quarter | ❌ No |
| `format_date()` | Format dates | ❌ No |
| ...and 8 more | Various date utilities | ❌ No |

#### src/stocksimulator/utils/math_utils.py (17 functions, ~400 LOC)
| Function | Purpose | Used? | Notes |
|----------|---------|-------|-------|
| `calculate_mean()` | Calculate mean | ❌ No | RiskCalculator reimplements |
| `calculate_variance()` | Calculate variance | ❌ No | RiskCalculator reimplements |
| `calculate_std_dev()` | Standard deviation | ❌ No | RiskCalculator reimplements |
| `calculate_sharpe()` | Sharpe ratio | ❌ No | RiskCalculator reimplements |
| `calculate_correlation()` | Correlation | ❌ No | - |
| `calculate_covariance()` | Covariance | ❌ No | - |
| `calculate_percentile()` | Percentiles | ❌ No | - |
| `compound_returns()` | Compound returns | ❌ No | - |
| `annualize_return()` | Annualize returns | ❌ No | - |
| `calculate_drawdown()` | Calculate drawdown | ❌ No | RiskCalculator reimplements |
| `geometric_mean()` | Geometric mean | ❌ No | - |
| `linear_regression()` | Linear regression | ❌ No | - |
| `moving_average()` | Moving average | ❌ No | Indicators reimplement |
| `exponential_moving_average()` | EMA | ❌ No | Indicators reimplement |
| `clamp()` | Clamp values | ❌ No | - |
| `normalize()` | Normalize data | ❌ No | - |
| ...and 1 more | - | ❌ No | - |

#### src/stocksimulator/utils/validators.py (11 functions, ~220 LOC)
| Function | Purpose | Used? | Notes |
|----------|---------|-------|-------|
| `validate_allocation()` | Validate allocations | ✅ **Yes** | **ONLY** in DCAStrategy.validate_allocation() |
| `validate_portfolio()` | Validate portfolio | ❌ No | - |
| `validate_price()` | Validate prices | ❌ No | - |
| `validate_date_range()` | Validate date ranges | ❌ No | - |
| `validate_parameter()` | Validate parameters | ❌ No | - |
| `validate_returns()` | Validate returns | ❌ No | - |
| `validate_symbol()` | Validate symbols | ❌ No | - |
| `validate_transaction_cost()` | Validate costs | ❌ No | - |
| `check_data_quality()` | Check data quality | ❌ No | - |
| ...and 2 more | - | ❌ No | - |

**Impact:** ~870 lines of unused code
**Recommendation:**
- Keep `validate_allocation()` (1 usage found)
- Remove remaining 43 functions OR add tests/examples demonstrating their use
- Alternative: Make utils module "private" (not exported) until needed

---

## Category 2: Unused Classes (MEDIUM-HIGH PRIORITY)

### 2.1 Core Module - PortfolioManager (HIGH PRIORITY)

**File:** `src/stocksimulator/core/portfolio_manager.py:21`
**Status:** Exported in `core/__init__.py` but **never instantiated**
**Size:** ~260 LOC

```python
class PortfolioManager:
    """Manage multiple portfolios and compare performance."""
```

**Mentioned in:** Documentation only (QUICKSTART.md, ARCHITECTURE.md)
**Used in code:** ❌ No examples, tests, or other modules

**Recommendation:** Create example demonstrating multi-portfolio comparison OR mark as experimental

---

### 2.2 Unused Strategies (5 classes)

#### 2.2.1 PairsTradingStrategy
**File:** `src/stocksimulator/strategies/mean_reversion_strategy.py`
**Status:** Defined but no examples or tests
**Purpose:** Statistical arbitrage between correlated pairs

#### 2.2.2 EqualRiskContributionStrategy
**File:** `src/stocksimulator/strategies/risk_parity_strategy.py`
**Status:** Defined but no examples or tests
**Purpose:** Alternative risk parity approach

#### 2.2.3 MinimumVarianceStrategy
**File:** `src/stocksimulator/strategies/risk_parity_strategy.py`
**Status:** Defined but no examples or tests
**Purpose:** Minimum variance portfolio optimization

#### 2.2.4 RotationalMomentumStrategy
**File:** `src/stocksimulator/strategies/momentum_strategy.py`
**Status:** Defined but no examples or tests
**Purpose:** Sector/asset rotation based on momentum

#### 2.2.5 ThreeFundPortfolio
**File:** `src/stocksimulator/strategies/base_strategy.py`
**Status:** Defined but no examples or tests
**Purpose:** Classic 3-fund portfolio (stocks/bonds/international)

**Total Strategy Files:** 6
**Total Strategy Classes Defined:** ~17
**Used in Examples:** ~12
**Unused:** 5

**Recommendation:** Add examples for these strategies OR remove them as incomplete

---

### 2.3 Unused Optimization Classes

#### 2.3.1 RandomSearchOptimizer
**File:** `src/stocksimulator/optimization/optimizer.py`
**Status:** Defined but never used
**Purpose:** Random parameter search (alternative to grid search)
**Note:** Only `GridSearchOptimizer` is used in notebook 03_optimization.ipynb

#### 2.3.2 WalkForwardAnalyzer
**File:** `src/stocksimulator/optimization/walk_forward.py:21`
**Status:** ✅ **USED** in notebook `03_optimization.ipynb`
**Note:** **NOT DEAD CODE** - confirmed usage

**Recommendation:** Add example for RandomSearchOptimizer OR document as experimental

---

### 2.4 Unused Position Sizing Classes

#### 2.4.1 FixedRatio
**File:** `src/stocksimulator/optimization/position_sizing.py`
**Status:** Defined but no examples
**Purpose:** Fixed ratio position sizing (Ryan Jones method)
**Note:** Only `KellyCriterion` and `FixedFractional` used in notebook

#### 2.4.2 VolatilityPositionSizer
**File:** `src/stocksimulator/optimization/position_sizing.py`
**Status:** Defined but no examples
**Purpose:** Size positions based on volatility

**Recommendation:** Add examples OR remove as incomplete

---

### 2.5 Indicators - Partial Usage

#### KeltnerChannels
**File:** `src/stocksimulator/indicators/volatility.py`
**Status:** Exported but not demonstrated in examples
**Note:** Lower priority - may be used by users directly

---

## Category 3: Empty/Placeholder Modules (LOW PRIORITY)

### src/stocksimulator/api/__init__.py
**Status:** Empty file (placeholder)
**Contents:** Only docstring, no implementation
**Size:** ~10 LOC

**Recommendation:** Remove if no API planned, or document future plans

---

## Category 4: Unnecessary Imports (LOW PRIORITY)

### Pattern: sys.path.insert() Manipulation

**Found in:** 32+ files across `src/stocksimulator/`

```python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
```

**Issue:** This pattern is used for development but shouldn't be needed in an installed package
**Impact:** Code clutter, potential path issues

**Files affected:**
- Most strategy files
- Most indicator files
- Data loaders
- Core modules
- Examples (appropriate for examples)

**Recommendation:**
- Remove from `src/stocksimulator/` modules (rely on proper package installation)
- Keep in `examples/` and `tests/` (appropriate for standalone scripts)

---

## Summary Statistics

| Category | Count | LOC | Priority |
|----------|-------|-----|----------|
| Unused utility functions | 43 | ~870 | HIGH |
| PortfolioManager class | 1 | ~260 | HIGH |
| Unused strategy classes | 5 | ~400 | MEDIUM |
| Unused optimization classes | 2 | ~150 | MEDIUM |
| Empty modules | 1 | ~10 | LOW |
| Unnecessary imports | 32+ files | ~100 | LOW |
| **TOTAL DEAD CODE** | **~88 items** | **~1,790** | **15-20%** |

---

## Recommendations by Priority

### PRIORITY 1 (Do First)
1. **Document or remove 43 unused utility functions**
   - Decision needed: Are these for future use or legacy code?
   - If keeping: Add tests and examples
   - If removing: Delete entire `utils/` module except `validate_allocation()`

2. **PortfolioManager - Add example or mark experimental**
   - Currently exported as main API but never demonstrated
   - Users may be confused about how to use it

### PRIORITY 2 (Do Soon)
3. **Unused strategies - Complete or remove**
   - 5 strategy classes have no examples/tests
   - Either finish implementation with examples or remove

4. **RandomSearchOptimizer - Add example**
   - Exported alongside GridSearchOptimizer but never used

5. **Position sizing classes - Add examples**
   - FixedRatio and VolatilityPositionSizer defined but not demonstrated

### PRIORITY 3 (Nice to Have)
6. **Clean up sys.path imports**
   - Remove from library code (keep in examples/tests only)

7. **Remove empty api module**
   - Or document future plans

---

## Code Quality Score

**Current State:**
- ✅ **GOOD:** No large commented-out code blocks
- ✅ **GOOD:** Clean code structure
- ⚠️ **FAIR:** 35% test coverage (55/98 tests for new modules)
- ❌ **POOR:** 15-20% dead code (unused functions/classes)
- ❌ **POOR:** Many exported APIs never demonstrated

**Target State:**
- Reduce dead code to <5% (~400 LOC)
- Increase test coverage to >60%
- Every exported class/function should have at least one example or test

---

## Next Steps

1. Review this report with team/maintainer
2. Decide on utility functions: keep or remove?
3. Complete unfinished strategies OR remove them
4. Add PortfolioManager example
5. Run coverage tool to identify untested code paths
6. Consider adding `# pragma: no cover` for defensive/error-handling code

---

## Notes

- Analysis based on current test coverage of ~35%
- Only checked examples/, tests/, and src/stocksimulator/ cross-references
- Did not check notebooks/ exhaustively (found WalkForwardAnalyzer usage there)
- Did not analyze if code is reachable within modules (only checked if modules are imported)

**Conclusion:** Substantial dead code exists. Recommend cleanup pass before 1.0 release.
