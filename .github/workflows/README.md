# GitHub Actions Workflows

## run-tests.yml

Automatically runs the test suite and commits results back to the branch.

### What It Does

1. **Triggers on every push** to any branch
2. **Runs the test suite** (`tests/test_analysis_suite.py`)
3. **Captures full output** to `tests.log` file
4. **Amends the last commit** with the test results
5. **Force pushes** back to the branch

### Workflow

```
Developer pushes code
    ↓
GitHub Action triggers
    ↓
Tests execute
    ↓
Results written to tests.log
    ↓
Commit amended with tests.log
    ↓
Force pushed back to branch
    ↓
Developer pulls to see results
```

### Test Log Format

The `tests.log` file contains:
- Branch name
- Commit SHA
- Execution timestamp
- Full test output
- Pass/Fail status

### Example tests.log

```
================================================
Test Execution Log
Branch: feature/new-analysis
Commit: abc123def456
Timestamp: 2025-01-08 14:30:22 UTC
================================================

test_irr_handles_loss_scenario ... ok
test_irr_handles_zero_return ... ok
test_irr_rejects_empty_cash_flows ... ok
...

----------------------------------------------------------------------
Ran 26 tests in 0.006s

OK

================================================
✅ ALL TESTS PASSED
================================================
```

### Usage

#### After Pushing Code

```bash
# 1. Push your changes
git push origin your-branch

# 2. Wait ~30 seconds for GitHub Action to complete

# 3. Pull to get the amended commit with test results
git pull --rebase origin your-branch

# 4. View test results
cat tests.log
```

#### Checking Action Status

- Go to GitHub → Actions tab
- Click on your latest commit
- View the "Run Tests and Commit Results" workflow
- Green checkmark = tests passed
- Red X = tests failed

### Important Notes

⚠️ **Force Push Warning**: This action uses `--force-with-lease` to amend commits.

- ✅ Safe for personal/feature branches
- ⚠️ Use caution on shared branches
- ❌ Not recommended for `main` branch

### Skipping the Action

To push without triggering tests:

```bash
git commit -m "Your message [skip ci]"
git push
```

The `[skip ci]` tag tells GitHub Actions to skip the workflow.

### Configuration

Edit `.github/workflows/run-tests.yml` to customize:

- **Python version**: Change `python-version: '3.10'`
- **Triggers**: Modify the `on:` section
- **Dependencies**: Uncomment `pip install -r requirements.txt` if needed
- **Test command**: Change the test execution command

### Troubleshooting

**Problem**: Pull shows conflicts after GitHub Action runs

**Solution**: Use `git pull --rebase` instead of `git pull`

```bash
git pull --rebase origin your-branch
```

**Problem**: Action fails with "permission denied"

**Solution**: Ensure repository has Actions enabled:
- Settings → Actions → General
- Enable "Read and write permissions"

**Problem**: Tests run locally but fail in CI

**Solution**: Check the `tests.log` file for detailed error messages

### Disabling Auto-Commit

If you want tests to run WITHOUT auto-committing results:

1. Comment out the "Commit test results" step in the workflow
2. Or add `[skip ci]` to your commit messages

### Advanced: Conditional Test Running

The workflow can be modified to only run tests on specific paths:

```yaml
on:
  push:
    paths:
      - 'tests/**'
      - 'historical_data/**'
      - '**.py'
```

This will only trigger when Python files or test files change.
