# CI/CD Quick Start Guide

This guide helps you quickly understand and use the CI/CD pipeline that's been set up for this repository.

## 🚀 For Contributors

### Before You Start
Every pull request to `master` will automatically run CI checks. Make sure your code passes locally before pushing!

### Running Tests Locally

```bash
# Install test dependencies
pip install pytest pytest-cov flake8

# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ -v --cov=pipeline --cov=shared

# Check code quality
flake8 pipeline/ shared/ --select=E9,F63,F7,F82
```

### What Gets Checked

When you open a PR, the CI pipeline automatically runs:

1. ✅ **Tests** on Python 3.10 & 3.11
2. ✅ **Code Quality** checks (flake8 linting)
3. ✅ **Build Verification** (imports and compilation)

All checks must pass before your PR can be merged.

### If CI Fails

1. **Check the logs**: Click "Details" next to the failed check
2. **Identify the issue**: Read the error message
3. **Fix locally**: Make changes and test
4. **Push updates**: CI will re-run automatically

Common failures:
- **Test failures**: Fix the failing test or code
- **Linting errors**: Run `flake8` locally and fix issues
- **Import errors**: Ensure all dependencies are in `requirements/common.txt`

## 🔧 For Maintainers

### Initial Setup (One-Time)

After merging this PR:

1. **Enable Branch Protection**
   - Go to Settings → Branches → Add rule
   - Pattern: `master`
   - Enable: "Require status checks to pass"
   - Select all CI checks (see full guide below)

2. **Verify Setup**
   - Create a test PR
   - Confirm CI runs automatically
   - Check that merge is blocked until checks pass

📖 **Full Guide**: See [docs/BRANCH_PROTECTION.md](BRANCH_PROTECTION.md) for detailed instructions.

### Managing CI

**Viewing Runs**: Actions tab → CI Pipeline

**Manual Trigger**: Actions tab → CI Pipeline → Run workflow

**Troubleshooting**: See [docs/CICD.md](CICD.md#troubleshooting)

## 📊 CI Pipeline Jobs

### 1. Test Pipeline
- Runs pytest on Python 3.10 and 3.11
- Generates coverage report
- Uploads to Codecov
- **Duration**: ~3-5 minutes

### 2. Code Quality
- Runs flake8 for linting
- Checks Python syntax
- Compiles all Python files
- **Duration**: ~1-2 minutes

### 3. Build Verification
- Installs dependencies
- Verifies package imports
- Tests CLI scripts
- **Duration**: ~2-3 minutes

**Total CI Time**: ~5-10 minutes per run

## 🎯 Quick Reference

| Action | Command |
|--------|---------|
| Run tests | `pytest tests/ -v` |
| Check coverage | `pytest tests/ --cov=pipeline --cov=shared` |
| Lint code | `flake8 pipeline/ shared/` |
| Check syntax | `python -m compileall pipeline/ shared/` |
| View CI logs | Go to Actions tab |

## 📚 Documentation

| Topic | Link |
|-------|------|
| Complete CI/CD Guide | [docs/CICD.md](CICD.md) |
| Branch Protection Setup | [docs/BRANCH_PROTECTION.md](BRANCH_PROTECTION.md) |
| Workflows Reference | [.github/workflows/README.md](../.github/workflows/README.md) |

## 🆘 Getting Help

**CI Issues?**
1. Check [Troubleshooting](CICD.md#troubleshooting) section
2. Review failed job logs
3. Open an issue with `ci` label

**Questions?**
- See full documentation in [docs/CICD.md](CICD.md)
- Contact repository maintainers

## ✨ Benefits

✅ **Catch bugs early** - Tests run automatically on every PR
✅ **Maintain quality** - Code standards are enforced
✅ **Prevent breakage** - Can't merge broken code
✅ **Track coverage** - See how much code is tested
✅ **Save time** - Automated testing frees you to focus on features

---

**Ready to contribute?** Make sure your code passes local tests, then open a PR! 🎉
