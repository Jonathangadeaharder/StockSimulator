# StockSimulator Test Suite

Comprehensive test suite for the StockSimulator analysis modules following software engineering best practices.

## 🎯 Design Principles

### SOLID
- **Single Responsibility**: Each test class focuses on one component/feature
- **Open/Closed**: Tests are extensible without modification
- **Liskov Substitution**: Test fixtures use consistent interfaces
- **Interface Segregation**: Tests target specific, well-defined interfaces
- **Dependency Inversion**: Mocks used where appropriate

### DRY (Don't Repeat Yourself)
- Reusable fixture methods (`setUp`, helper functions)
- Common test data extracted to methods
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

## 📦 Test Coverage

### TestIRRCalculation (8 tests)
Tests the Internal Rate of Return calculation function.

**Covers:**
- Simple IRR calculations
- Monthly contribution patterns
- Empty/invalid inputs
- Single cash flow rejection
- Mismatched data lengths
- Loss scenarios
- Extreme value rejection
- Break-even scenarios

**Key Edge Cases:**
- Returns `None` for unrealistic rates (>1000% or <-99%)
- Handles convergence failures gracefully
- Newton-Raphson algorithm validation

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
- Basic percentile identification
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

## 🚀 Running the Tests

### Run all tests:
```bash
python3 tests/test_analysis_suite.py
```

### Run with verbose output:
```bash
python3 tests/test_analysis_suite.py -v
```

### Run specific test class:
```bash
python3 -m unittest tests.test_analysis_suite.TestIRRCalculation
```

### Run specific test:
```bash
python3 -m unittest tests.test_analysis_suite.TestIRRCalculation.test_simple_irr_calculation
```

## ✅ Test Results

```
================================================================================
Tests run: 26
Successes: 26
Failures: 0
Errors: 0
================================================================================
```

All tests pass successfully, validating:
- IRR calculations with Newton-Raphson convergence
- Financial return mathematics
- Leveraged ETF simulation accuracy
- Percentile distribution calculations
- Data validation and filtering
- Monthly investment timing
- Edge case handling

## 📊 Test Coverage Summary

| Component | Tests | Coverage |
|-----------|-------|----------|
| IRR Calculation | 8 | Full |
| Return Calculations | 4 | Core logic |
| Leveraged ETF Simulation | 3 | Key mechanics |
| Percentile Calculations | 3 | Basic ops |
| Data Validation | 2 | CSV & filtering |
| Monthly Investment | 2 | DCA timing |
| Edge Cases | 3 | Error handling |
| Integration | 1 | End-to-end |

## 🔧 Extending the Test Suite

### Adding New Tests

1. **Create a new test class** following the naming convention `Test<Component>`
2. **Use descriptive docstrings** for both class and methods
3. **Follow the AAA pattern**: Arrange, Act, Assert
4. **Use setUp/tearDown** for common fixtures
5. **Add to test suite** in `run_test_suite()` function

### Example:
```python
class TestNewFeature(unittest.TestCase):
    """Test description of the new feature."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_data = [1, 2, 3]

    def test_specific_behavior(self):
        """Should do something specific."""
        # Arrange
        input_value = 5

        # Act
        result = some_function(input_value)

        # Assert
        self.assertEqual(result, expected_value)
```

## 🧪 Best Practices in This Suite

1. **Test Isolation**: Each test is independent
2. **Clear Assertions**: Single, focused assertion per test (where possible)
3. **Descriptive Names**: Test names explain what is being tested
4. **Edge Case Coverage**: Boundary conditions explicitly tested
5. **Error Handling**: Invalid inputs tested for graceful failures
6. **Mathematical Validation**: Financial calculations verified for accuracy
7. **Documentation**: Docstrings explain purpose and coverage

## 📝 Notes

- Tests use real mathematical examples to validate accuracy
- IRR tests include realistic investment scenarios
- Leveraged ETF tests demonstrate volatility decay
- Percentile tests use simple, verifiable distributions
- Integration tests simulate realistic multi-month cycles

## 🔍 Debugging Failed Tests

If a test fails:

1. **Read the assertion error** - shows expected vs actual
2. **Check the test docstring** - explains what should happen
3. **Review test data** - often in `setUp()` or inline
4. **Run in isolation** - use `-m unittest` to run just one test
5. **Add print statements** - temporarily for debugging
6. **Verify assumptions** - check if implementation changed

## 🎓 Learning Resources

- [Python unittest documentation](https://docs.python.org/3/library/unittest.html)
- [Test-Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [DRY Principle](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)

---

**Version**: 1.0
**Last Updated**: 2025-01-08
**Test Suite Author**: Claude (Anthropic)
**Total Tests**: 26
**Pass Rate**: 100%
