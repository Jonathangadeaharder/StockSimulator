#!/usr/bin/env python3
"""
Run all new stocksimulator module tests.

Tests the new src/stocksimulator/ modules.
"""

import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def run_tests():
    """Run all new module tests."""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "STOCKSIMULATOR MODULE TESTS" + " " * 31 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # Discover and run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Get absolute paths to test directories
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_dirs = [
        os.path.join(script_dir, 'test_core'),
        os.path.join(script_dir, 'test_data'),
        os.path.join(script_dir, 'test_strategies'),
        os.path.join(script_dir, 'test_indicators'),
    ]

    total_tests = 0
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            tests = loader.discover(test_dir, pattern='test_*.py', top_level_dir=script_dir)
            suite.addTests(tests)
            total_tests += tests.countTestCases()

    print(f"Running {total_tests} tests...")
    print("=" * 80)
    print()

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests run:    {result.testsRun}")
    print(f"Successes:          {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures:           {len(result.failures)}")
    print(f"Errors:             {len(result.errors)}")
    print(f"Skipped:            {len(result.skipped)}")
    print("=" * 80)

    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"Success Rate:       {success_rate:.1f}%")
    print("=" * 80)

    # Exit with appropriate code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
