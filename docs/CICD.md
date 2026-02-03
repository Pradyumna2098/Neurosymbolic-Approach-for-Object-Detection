# CI/CD Pipeline Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the Neurosymbolic Object Detection repository.

## Overview

The CI/CD pipeline automatically verifies code quality, runs tests, and validates builds for all pull requests targeting the `master` or `main` branch. This ensures that only code that passes all checks can be merged, maintaining the stability and quality of the codebase.

## Pipeline Structure

The pipeline is defined in `.github/workflows/tests.yml` and consists of three main jobs:

### 1. Test Pipeline (`test-pipeline`)

**Purpose**: Run automated tests across multiple Python versions to ensure compatibility.

**Matrix Strategy**: Tests run on Python 3.10 and 3.11 to ensure broad compatibility.

**Steps**:
1. Check out the repository
2. Set up Python environment with dependency caching
3. Install system dependencies (SWI-Prolog for symbolic reasoning)
4. Install Python dependencies (core + pytest)
5. Run pytest with coverage reporting
6. Upload coverage reports to Codecov (Python 3.10 only)

**What it validates**:
- All unit tests pass
- Code coverage is tracked
- The codebase works with supported Python versions

### 2. Code Quality (`code-quality`)

**Purpose**: Enforce code quality standards and catch syntax errors.

**Steps**:
1. Check out the repository
2. Set up Python 3.10 environment
3. Install linting tools (flake8)
4. Run flake8 to detect critical errors (syntax errors, undefined names)
5. Run comprehensive linting (warnings only, non-blocking)
6. Compile all Python files to check for syntax errors

**What it validates**:
- No Python syntax errors
- No undefined variable references
- Code follows basic quality standards
- All Python files can be compiled

### 3. Build Verification (`build-verification`)

**Purpose**: Verify that the package can be installed and imported correctly.

**Steps**:
1. Check out the repository
2. Set up Python environment
3. Install all dependencies
4. Test that main modules can be imported
5. Verify that CLI scripts can be invoked

**What it validates**:
- Dependencies install correctly
- No import errors in main modules
- CLI scripts are properly configured
- The package structure is sound

## Triggers

The CI pipeline runs on:

- **Pull Requests**: Automatically runs when a PR is opened or updated targeting `master` or `main`
- **Push to master/main**: Runs on direct commits to the main branches
- **Manual Trigger**: Can be manually triggered via the GitHub Actions UI using `workflow_dispatch`

## Status Checks

All three jobs (`test-pipeline`, `code-quality`, `build-verification`) must pass for the overall CI status to be green. These status checks will appear on pull requests:

- ✅ **Test Python Pipeline** - Tests pass on all Python versions
- ✅ **Code Quality Checks** - Linting and syntax checks pass
- ✅ **Build Verification** - Package builds and imports successfully

## Branch Protection

To enforce CI checks before merging, configure branch protection rules for the `master` branch.

**📋 See the detailed [Branch Protection Setup Guide](BRANCH_PROTECTION.md) for step-by-step instructions.**

### Quick Setup

1. Go to **Settings** → **Branches** → **Branch protection rules**
2. Add rule for `master` branch
3. Enable the following options:
   - ✅ **Require status checks to pass before merging**
   - ✅ **Require branches to be up to date before merging**
   - Select required status checks:
     - `Test Python Pipeline (3.10)`
     - `Test Python Pipeline (3.11)`
     - `Code Quality Checks`
     - `Build Verification`
   - ✅ **Require pull request reviews before merging** (recommended)
   - ✅ **Dismiss stale pull request approvals when new commits are pushed**

## Extending the Pipeline

### Adding Tests for New Modules

When adding new functionality:

1. **Add tests** in the appropriate `tests/` subdirectory:
   - `tests/pipeline/` for pipeline components
   - `tests/backend/` for backend APIs (when implemented)
   - `tests/frontend/` for frontend tests (when implemented)
   - `tests/shared/` for shared utilities

2. **Follow the existing test structure**:
   ```python
   # tests/pipeline/test_mymodule.py
   import pytest
   from pipeline.mymodule import myfunction
   
   def test_myfunction_basic():
       """Test basic functionality."""
       result = myfunction(input_data)
       assert result == expected_output
   ```

3. **Run tests locally**:
   ```bash
   # Install dev dependencies
   pip install -r requirements/dev.txt
   
   # Run tests
   pytest tests/ -v
   
   # Run with coverage
   pytest tests/ --cov=pipeline --cov=shared --cov-report=html
   ```

### Adding New Components (Backend/Frontend)

When implementing the backend or frontend subprojects:

#### For Backend (Python/FastAPI):

1. **Add backend-specific job** to `.github/workflows/tests.yml`:
   ```yaml
   test-backend:
     name: Test Backend API
     runs-on: ubuntu-latest
     steps:
       - uses: actions/checkout@v4
       - name: Set up Python
         uses: actions/setup-python@v5
         with:
           python-version: "3.10"
       - name: Install dependencies
         run: |
           pip install -r requirements.txt
           pip install -r backend/requirements.txt
       - name: Run backend tests
         run: pytest tests/backend/ -v
   ```

2. **Add backend dependencies** to `backend/requirements.txt`
3. **Add backend tests** to `tests/backend/`

#### For Frontend (Node.js/React/Vue):

1. **Add frontend-specific job** to `.github/workflows/tests.yml`:
   ```yaml
   test-frontend:
     name: Test Frontend
     runs-on: ubuntu-latest
     steps:
       - uses: actions/checkout@v4
       - name: Set up Node.js
         uses: actions/setup-node@v4
         with:
           node-version: "18"
           cache: 'npm'
           cache-dependency-path: frontend/package-lock.json
       - name: Install dependencies
         run: |
           cd frontend
           npm ci
       - name: Run tests
         run: |
           cd frontend
           npm test
       - name: Build
         run: |
           cd frontend
           npm run build
   ```

2. **Initialize frontend** with a package manager:
   ```bash
   cd frontend
   npm init -y
   # or
   npm create vite@latest . -- --template react-ts
   ```

3. **Add tests** using Jest, Vitest, or your chosen framework

### Adding New Python Dependencies

When adding new Python packages:

1. **Add to appropriate requirements file**:
   - Core dependencies → `requirements/common.txt`
   - Development/testing → `requirements/dev.txt`
   - Platform-specific → `requirements.txt` or `requirements-kaggle.txt`

2. **Pin versions** for reproducibility:
   ```
   # Good
   requests==2.31.0
   
   # Avoid
   requests
   requests>=2.0
   ```

3. **Test locally** before pushing:
   ```bash
   pip install -r requirements.txt
   pytest tests/ -v
   ```

### Adding System Dependencies

If new system packages are required (like SWI-Prolog for symbolic reasoning):

1. **Update the CI workflow** to install them:
   ```yaml
   - name: Install system dependencies
     run: |
       sudo apt-get update
       sudo apt-get install -y swi-prolog your-new-package
   ```

2. **Document in README** under installation instructions

3. **Consider Docker** for complex dependencies:
   ```yaml
   # Use a container instead
   container:
     image: your-docker-image:latest
   ```

### Adding Integration Tests

For end-to-end testing:

1. **Create separate workflow** (`.github/workflows/integration.yml`):
   ```yaml
   name: Integration Tests
   
   on:
     pull_request:
       branches: [master, main]
   
   jobs:
     integration:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - name: Run integration tests
           run: pytest tests/integration/ -v --slow
   ```

2. **Use pytest markers** to separate unit and integration tests:
   ```python
   @pytest.mark.slow
   @pytest.mark.integration
   def test_full_pipeline():
       """Test the complete pipeline end-to-end."""
       pass
   ```

## Troubleshooting

### Tests Failing Locally but Passing in CI (or vice versa)

**Common causes**:
- Different Python versions
- Missing system dependencies
- Environment variables not set
- Platform-specific behavior (Windows vs Linux)

**Solutions**:
- Use the same Python version as CI (3.10 or 3.11)
- Install system dependencies: `sudo apt-get install swi-prolog`
- Check `.github/workflows/tests.yml` for environment setup differences

### Flaky Tests

**Symptoms**: Tests pass sometimes but fail other times

**Common causes**:
- Tests depend on random data without setting seeds
- Tests depend on timing (sleep statements)
- Tests depend on external services

**Solutions**:
```python
import random
import numpy as np
import torch

def test_with_fixed_seed():
    # Set seeds for reproducibility
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    
    # Your test code here
```

### CI Taking Too Long

**Symptoms**: CI runs take more than 10 minutes

**Solutions**:
1. **Use caching** for dependencies (already enabled for pip)
2. **Parallelize tests** using pytest-xdist:
   ```yaml
   - name: Run tests
     run: pytest tests/ -v -n auto
   ```
3. **Skip slow tests** in regular CI:
   ```python
   @pytest.mark.slow
   def test_expensive_operation():
       pass
   ```
   ```yaml
   # Regular CI - skip slow tests
   pytest tests/ -v -m "not slow"
   ```

### Dependency Installation Failures

**Symptoms**: `pip install` fails in CI

**Solutions**:
1. **Check package availability** on PyPI
2. **Specify compatible versions**:
   ```
   torch==2.2.2; python_version <= '3.11'
   ```
3. **Use pre-built wheels** when possible
4. **Install build dependencies**:
   ```yaml
   - name: Install build tools
     run: |
       sudo apt-get install -y build-essential python3-dev
   ```

## Monitoring and Badges

### Adding Status Badges to README

Add CI status badges to show pipeline health:

```markdown
![CI Pipeline](https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection/workflows/CI%20Pipeline/badge.svg)
[![codecov](https://codecov.io/gh/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection/branch/master/graph/badge.svg)](https://codecov.io/gh/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection)
```

### Viewing CI Logs

1. Go to the **Actions** tab in GitHub
2. Select the workflow run
3. Click on a job to see detailed logs
4. Download logs for local analysis if needed

### Code Coverage Reports

Coverage reports are uploaded to Codecov for Python 3.10 runs. View them at:
`https://codecov.io/gh/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection`

## Best Practices

### For Contributors

1. **Run tests locally** before pushing:
   ```bash
   pytest tests/ -v
   ```

2. **Check code quality**:
   ```bash
   flake8 pipeline/ shared/
   ```

3. **Keep PRs focused** - smaller PRs are easier to review and test

4. **Write tests** for new features and bug fixes

5. **Update documentation** when changing functionality

### For Maintainers

1. **Keep dependencies updated** but test thoroughly
2. **Monitor CI execution time** and optimize if needed
3. **Review failed CI runs** and fix issues promptly
4. **Configure branch protection** to enforce CI checks
5. **Document new CI requirements** when adding workflows

## Security Considerations

- **Secrets**: Use GitHub Secrets for sensitive data (API keys, tokens)
- **Dependencies**: Regularly update to patch security vulnerabilities
- **Code scanning**: Consider adding CodeQL for security analysis:
  ```yaml
  # Add to .github/workflows/codeql.yml
  - name: Initialize CodeQL
    uses: github/codeql-action/init@v2
    with:
      languages: python
  ```

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [pytest Documentation](https://docs.pytest.org/)
- [flake8 Documentation](https://flake8.pycqa.org/)
- [Codecov Documentation](https://docs.codecov.com/)

## Changelog

### 2026-02-03 - Initial CI/CD Setup
- Created CI pipeline with test, code quality, and build verification jobs
- Added support for Python 3.10 and 3.11
- Integrated pytest with coverage reporting
- Added flake8 for code quality checks
- Configured Codecov integration
- Created comprehensive documentation

## Support

For CI/CD issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review workflow logs in the Actions tab
3. Open an issue with the `ci` label
4. Tag maintainers for urgent pipeline failures
