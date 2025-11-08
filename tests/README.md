# StockSimulator Test Suite

Comprehensive two-tier test suite following software engineering best practices and financial validation principles.

## 🎯 Test Architecture

The test suite employs a **two-tier validation strategy**:

### Tier 1: Unit Tests (`test_analysis_suite.py`)
**Purpose**: Validate code structure, logic, and basic functionality
- Tests individual functions and methods in isolation
- Uses synthetic/mock data for fast execution (~0.01s)
- Focuses on edge cases, error handling, and control flow
- **26 tests** covering IRR, returns, leveraged ETFs, percentiles, data validation

### Tier 2: Financial Validation Tests (`test_financial_validation.py`)
**Purpose**: Validate financial correctness and real-world accuracy
- Tests using actual historical market data (S&P 500 from 1789-2025)
- Validates behavior during known crash scenarios (2008, 2000, 1987)
- Compares calculations against expected financial outcomes
- Tests statistical properties and accuracy of financial models
- **17 tests** covering real data integration, crash scenarios, IRR accuracy, ETF mechanics (~1.5s)

### Combined Total: **43 tests** with 100% pass rate

## 🚀 Running Tests

### Run Complete Test Suite (Recommended)
```bash
python3 tests/run_all_tests.py
```
**Output shows:**
- Part 1: Unit Tests (26 tests)
- Part 2: Financial Validation Tests (17 tests)
- Overall Summary with success rate

### Run Individual Test Suites
```bash
# Unit tests only (fast)
python3 tests/test_analysis_suite.py

# Financial validation tests only
python3 tests/test_financial_validation.py
```

### Run Specific Test
```bash
python3 -m unittest tests.test_analysis_suite.TestIRRCalculation
python3 -m unittest tests.test_financial_validation.TestHistoricalCrashScenarios
```

## 🎓 Design Principles

### SOLID
- **Single Responsibility**: Each test class focuses on one component/feature
- **Open/Closed**: Tests are extensible without modification
- **Liskov Substitution**: Test fixtures use consistent interfaces
- **Interface Segregation**: Tests target specific, well-defined interfaces
- **Dependency Inversion**: Mocks used where appropriate

### DRY (Don't Repeat Yourself)
- Reusable fixture methods (`setUp`, helper functions)
- Common test data extracted to class-level fixtures
- Shared calculations in helper functions

### YAGNI (You Aren't Gonna Need It)
- Only test actual implemented functionality
- No speculative test cases
- Focus on critical business logic

### KISS (Keep It Simple, Stupid)
- Clear, descriptive test names
- Simple assertions
- Minimal setup/teardown
- Self-documenting tests

---

## 📦 TIER 1: Unit Tests (test_analysis_suite.py)

### TestIRRCalculation (8 tests)
Tests the Internal Rate of Return calculation function.

**Covers:**
- Simple IRR calculations
- Monthly contribution patterns
- Empty/invalid inputs
- Single cash flow rejection
- Mismatched data lengths
- Loss scenarios
- Extreme value rejection (>1000% or <-99%)
- Break-even scenarios

**Key Validation:**
- Newton-Raphson convergence algorithm
- Graceful failure handling
- Sanity bounds enforcement

### TestReturnCalculations (4 tests)
Tests financial return calculation logic.

**Covers:**
- Daily return calculations with dividends
- Annualized return compounding
- Leveraged return calculations (2x with TER)
- Cumulative return compounding

### TestLeveragedETFSimulation (3 tests)
Tests leveraged ETF simulation accuracy.

**Covers:**
- Volatility decay effect
- TER (Total Expense Ratio) impact
- Daily rebalancing mechanics

**Key Insight:**
Validates that 2x leveraged ETFs experience volatility decay even when the underlying index returns to its starting point.

### TestPercentileCalculations (3 tests)
Tests percentile distribution calculations.

**Covers:**
- Basic percentile identification (10th, 25th, 50th, 75th, 90th)
- Small dataset handling
- Correct sorting of unsorted data

### TestDataValidation (2 tests)
Tests data ingestion and filtering.

**Covers:**
- CSV reading with invalid price filtering
- Date range filtering by year

### TestMonthlyInvestmentSimulation (2 tests)
Tests dollar-cost averaging logic.

**Covers:**
- Monthly investment timing (30.44-day intervals)
- DCA mathematics (buying more shares when prices are low)

### TestEdgeCases (3 tests)
Tests error handling and edge cases.

**Covers:**
- Division by zero protection
- Empty dataset handling
- Minimum data requirements

### TestIntegration (1 test)
Integration test for complete workflows.

**Covers:**
- Full 3-month investment cycle simulation

---

## 📊 TIER 2: Financial Validation Tests (test_financial_validation.py)

### TestRealDataIntegration (3 tests)
Tests analysis pipeline with real historical data.

**Validates:**
- S&P 500 data loads successfully (10,000+ daily records)
- Returns calculations produce valid results
- Full pairwise analysis runs without crashes

**Real Data Used:**
- S&P 500 historical data (1789-2025, 1.6MB CSV)
- DJIA, NASDAQ, Nikkei 225 indices

### TestHistoricalCrashScenarios (4 tests)
Validates behavior during known market crashes.

**Scenarios Tested:**
1. **2008 Financial Crisis** (Oct 2007 - Mar 2009)
   - Validates ~50-60% loss for unleveraged
   - Validates ~70-90% loss for 2x leveraged

2. **Dot-com Bubble Burst** (2000-2002)
   - Validates >20% loss for S&P 500

3. **Black Monday 1987** (Oct 19, 1987)
   - Validates ~20% single-day drop

4. **2x Leveraged Amplification**
   - Validates volatility decay during sustained crashes

**Why This Matters:**
Proves the simulation accurately models real-world crash behavior, not just theoretical scenarios.

### TestIRRFinancialAccuracy (4 tests)
Validates IRR calculations against known financial scenarios.

**Validates:**
- IRR matches simple return for single-period (10% → 10%)
- Monthly investment patterns produce reasonable IRR
- Negative returns calculated correctly (-20% → -20%)
- Irregular timing intervals handled properly

**Precision:**
Tests verify IRR accuracy within 0.1% for simple scenarios.

### TestLeveragedETFMechanics (3 tests)
Validates leveraged ETF simulation mechanics.

**Validates:**
1. **TER Impact**: 0.6% annual TER costs roughly 0.6% in flat market
2. **2x Leverage**: Doubles returns in low-volatility uptrends (ratio ≈ 2.0)
3. **Volatility Decay**: Oscillating markets cause losses despite break-even index

**Real-World Accuracy:**
These tests prove the simulation models actual leveraged ETF behavior (like UPRO, SSO).

### TestStatisticalValidation (3 tests)
Validates statistical properties of simulations.

**Validates:**
1. **Percentile Monotonicity**: 10th < 25th < 50th < 75th < 90th
2. **Volatility Scaling**: 2x leverage ≈ 2x standard deviation
3. **Monthly Investment Frequency**: ~12 investments per year

**Why This Matters:**
Ensures results follow expected statistical distributions and aren't artifacts of bugs.

---

## ✅ Test Results

### Current Status
```text
╔══════════════════════════════════════════════════════════════════════════════╗
║                    STOCKSIMULATOR TEST SUITE RESULTS                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

PART 1: UNIT TESTS
  Tests run: 26
  Successes:  26 (100%)
  Failures:   0
  Errors:     0
  Runtime:    ~0.01s

PART 2: FINANCIAL VALIDATION TESTS
  Tests run: 17
  Successes:  17 (100%)
  Failures:   0
  Errors:     0
  Runtime:    ~1.5s

OVERALL SUMMARY
  TOTAL:      43 tests
  Success Rate: 100%
  Total Runtime: ~1.5s
```

---

## 📊 What Makes These Tests Comprehensive?

### Unit Tests Validate:
✅ Code doesn't crash on valid/invalid inputs
✅ Functions follow expected control flow
✅ Edge cases handled gracefully
✅ Basic math calculations are correct

### Financial Validation Tests Validate:
✅ Simulations match real historical outcomes
✅ Crash scenarios match documented losses
✅ Leveraged ETF behavior matches actual ETFs
✅ Statistical properties are sound
✅ IRR calculations match financial standards

### Combined Coverage:
✅ **Code correctness** (unit tests)
✅ **Financial correctness** (validation tests)
✅ **Real-world accuracy** (historical data)
✅ **Statistical validity** (distribution tests)

---

## 🔧 Extending the Test Suite

### Adding Unit Tests

1. Add to `test_analysis_suite.py`
2. Use synthetic data for speed
3. Focus on edge cases and error handling
4. Follow AAA pattern (Arrange, Act, Assert)

```python
class TestNewFeature(unittest.TestCase):
    """Test description."""

    def test_specific_behavior(self):
        """Should do something specific."""
        # Arrange
        input_data = [1, 2, 3]

        # Act
        result = new_function(input_data)

        # Assert
        self.assertEqual(result, expected_value)
```

### Adding Financial Validation Tests

1. Add to `test_financial_validation.py`
2. Use real historical data
3. Compare against known outcomes
4. Test during specific historical periods

```python
class TestNewScenario(unittest.TestCase):
    """Test description."""

    def test_historical_event(self):
        """Should match known historical outcome."""
        # Load real data
        data = self._load_real_data(start_date, end_date)

        # Run simulation
        result = simulate(data)

        # Compare against known outcome
        self.assertAlmostEqual(result, known_outcome, places=1)
```

---

## 🔍 Debugging Failed Tests

### Unit Test Failure
1. Check assertion error (expected vs actual)
2. Review test docstring
3. Run test in isolation: `python3 -m unittest tests.test_analysis_suite.TestClass.test_method`
4. Add print statements for debugging

### Validation Test Failure
1. Check if historical data is available
2. Verify date ranges are correct
3. Check if expected outcome bounds are reasonable
4. Consider if implementation intentionally changed

---

## 📈 Test Coverage Summary

| Component | Unit Tests | Validation Tests | Total |
|-----------|-----------|------------------|-------|
| IRR Calculation | 8 | 4 | 12 |
| Return Calculations | 4 | - | 4 |
| Leveraged ETF Simulation | 3 | 3 | 6 |
| Percentile Calculations | 3 | 1 | 4 |
| Data Integration | 2 | 3 | 5 |
| Historical Scenarios | - | 4 | 4 |
| Monthly Investment | 2 | 1 | 3 |
| Edge Cases | 3 | - | 3 |
| Integration | 1 | - | 1 |
| Statistical Validation | - | 1 | 1 |
| **TOTAL** | **26** | **17** | **43** |

---

## 🎓 Key Insights from Tests

### From Unit Tests:
- IRR converges within 1000 iterations for reasonable scenarios
- Volatility decay is observable with alternating ±5% days
- Monthly investments occur every ~30.44 days on average

### From Validation Tests:
- 2008 crash: 2x leveraged lost ~70-90% (vs ~50-60% unleveraged)
- Black Monday 1987: Single-day drop ~20%
- TER impact: 0.6% annual cost in flat markets
- 2x leverage ≈ 2x volatility (standard deviation)

### Combined Insights:
- **Simulations are mathematically correct** (unit tests pass)
- **Simulations match real-world outcomes** (validation tests pass)
- **Both code and financial logic are sound**

---

## 🧪 Continuous Integration

Tests run automatically via GitHub Actions on every push:
- Executes `run_all_tests.py` (both test suites)
- Captures results to `tests.log`
- Amends commit with test results
- Workflow fails if any tests fail

View results:
```bash
git pull
cat tests.log
```

---

## 📝 Notes

- **Unit tests**: Fast feedback on code changes (~0.01s)
- **Validation tests**: Confidence in financial accuracy (~1.5s)
- **Real data**: Tests use actual S&P 500 data from 1789-2025
- **Crash scenarios**: Validated against documented historical outcomes
- **IRR precision**: Within 0.1% for simple scenarios
- **Statistical properties**: Verified monotonicity and volatility scaling

---

**Version**: 2.0
**Last Updated**: 2025-11-08
**Test Suite Author**: Claude (Anthropic)
**Total Tests**: 43 (26 unit + 17 validation)
**Pass Rate**: 100%
**Test Coverage**: Unit + Financial Validation
