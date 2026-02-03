# GitHub Actions Workflows

This directory contains GitHub Actions workflow definitions for automated CI/CD.

## Workflows

### `ci.yml` - Main CI Pipeline

**Purpose**: Continuous Integration pipeline that runs on all pull requests to `master` branch.

**Triggers**:
- Pull requests to `master` or `main`
- Direct pushes to `master` or `main`
- Manual workflow dispatch

**Jobs**:

1. **test-pipeline** - Run automated tests
   - Runs on Python 3.10 and 3.11
   - Executes pytest with coverage reporting
   - Uploads coverage to Codecov

2. **code-quality** - Code quality checks
   - Runs flake8 linting
   - Checks for syntax errors
   - Compiles all Python files

3. **build-verification** - Build and import verification
   - Installs all dependencies
   - Verifies package imports work
   - Tests CLI scripts can be invoked

**Duration**: ~5-10 minutes per run

**Required for merge**: All jobs must pass

## Adding New Workflows

When adding new workflow files:

1. Create a new `.yml` file in this directory
2. Follow GitHub Actions syntax
3. Test with `workflow_dispatch` trigger first
4. Update this README
5. Add to branch protection rules if required for merge

## Debugging Workflows

- **View logs**: Go to Actions tab → Select workflow run → Click on job
- **Local testing**: Use [act](https://github.com/nektos/act) to run workflows locally
- **Syntax validation**: Use `yamllint` or GitHub's workflow validator

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Repository CI/CD Guide](../../docs/CICD.md)
