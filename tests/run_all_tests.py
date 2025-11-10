#!/usr/bin/env python3
"""
Master test runner for StockSimulator project.

Runs both test suites:
1. Unit Tests (test_analysis_suite.py) - Code structure and basic functionality
2. Validation Tests (test_financial_validation.py) - Real data and financial correctness
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import test modules
from tests.test_analysis_suite import run_test_suite as run_unit_tests
from tests.test_financial_validation import run_validation_suite


def run_all_tests():
    """Run complete test suite."""
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "STOCKSIMULATOR COMPREHENSIVE TEST SUITE" + " " * 19 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # Run unit tests
    print("=" * 80)
    print("PART 1: UNIT TESTS (Code Structure & Basic Functionality)")
    print("=" * 80)
    print()

    unit_result = run_unit_tests()

    print("\n")

    # Run validation tests
    print("=" * 80)
    print("PART 2: FINANCIAL VALIDATION TESTS (Real Data & Correctness)")
    print("=" * 80)
    print()

    validation_result = run_validation_suite()

    print("\n")

    # Summary
    print("=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)

    total_tests = unit_result.testsRun + validation_result.testsRun
    total_failures = len(unit_result.failures) + len(validation_result.failures)
    total_errors = len(unit_result.errors) + len(validation_result.errors)
    total_success = total_tests - total_failures - total_errors

    print(f"Unit Tests:       {unit_result.testsRun:>3} tests "
          f"({unit_result.testsRun - len(unit_result.failures) - len(unit_result.errors)} pass, "
          f"{len(unit_result.failures)} fail, {len(unit_result.errors)} error)")
    print(f"Validation Tests: {validation_result.testsRun:>3} tests "
          f"({validation_result.testsRun - len(validation_result.failures) - len(validation_result.errors)} pass, "
          f"{len(validation_result.failures)} fail, {len(validation_result.errors)} error)")
    print("-" * 80)
    print(f"TOTAL:            {total_tests:>3} tests "
          f"({total_success} pass, {total_failures} fail, {total_errors} error)")

    success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
    print(f"Success Rate:     {success_rate:.1f}%")
    print("=" * 80)

    if total_failures > 0 or total_errors > 0:
        print("\n⚠️  TESTS FAILED - See details above")
        return False
    else:
        print("\n✅ ALL TESTS PASSED")
        return True


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
