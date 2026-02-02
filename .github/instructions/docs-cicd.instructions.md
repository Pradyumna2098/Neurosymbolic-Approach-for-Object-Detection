---
applyTo: "docs/**/*.md,*.md,.github/**/*.yml,.github/**/*.yaml"
---

# Documentation and CI/CD Instructions

These instructions apply to documentation files (Markdown) and CI/CD workflows.

## Documentation Standards

### Markdown Files

#### File Organization
- `README.md` - Project overview, setup instructions, usage examples
- `CONTRIBUTING.md` - Contribution guidelines (if separate from Instructions)
- `docs/` - Detailed documentation, tutorials, API references
- `.github/copilot-instructions.md` - Repository-wide Copilot instructions

#### Writing Style
- Use clear, concise language
- Write in present tense
- Use active voice
- Keep paragraphs short (3-5 sentences)
- Use headings to organize content

#### Markdown Formatting

**Headers**: Use ATX-style headers (# symbols):
```markdown
# Main Title (H1)
## Section (H2)
### Subsection (H3)
```

**Code Blocks**: Always specify language for syntax highlighting:
```markdown
\`\`\`python
def example():
    return "Hello"
\`\`\`

\`\`\`bash
python train.py --config configs/training.yaml
\`\`\`
```

**Lists**:
```markdown
- Unordered item
- Another item
  - Nested item

1. Ordered item
2. Another item
```

**Links**:
```markdown
[Link text](https://url.com)
[Internal link](#section-name)
[Relative link](docs/guide.md)
```

**Images**:
```markdown
![Alt text](path/to/image.png)
```

**Tables**:
```markdown
| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
```

### README.md Structure

Standard README structure:

```markdown
# Project Title

Brief description (1-2 sentences)

## Features
- Key feature 1
- Key feature 2

## Installation

\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Quick Start

\`\`\`bash
python training.py --config configs/training_local.yaml
\`\`\`

## Usage

Detailed usage instructions...

## Configuration

How to configure the project...

## Documentation

Link to full documentation...

## Contributing

How to contribute...

## License

License information...
```

### API Documentation

Document public APIs with clear examples:

```markdown
## `parse_predictions_for_nms(predictions_dir: Path) -> PredictionDict`

Load YOLO-format predictions and derive additional metadata for NMS.

**Parameters:**
- `predictions_dir` (Path): Directory containing .txt prediction files

**Returns:**
- `PredictionDict`: Dictionary mapping image names to lists of prediction dicts

**Example:**
\`\`\`python
from pathlib import Path
from pipeline.utils import parse_predictions_for_nms

predictions = parse_predictions_for_nms(Path("predictions/"))
\`\`\`

**Raises:**
- `FileNotFoundError`: If predictions_dir doesn't exist
```

### Keeping Documentation Updated

- **Update with code changes**: Modify docs when changing functionality
- **Version documentation**: Note which version features were added
- **Deprecation notices**: Document deprecated features and alternatives
- **Examples**: Ensure code examples actually work

## CI/CD Workflows

### GitHub Actions Structure

Workflows are defined in `.github/workflows/`:

```
.github/
  workflows/
    dependency-check.yml  - Dependency health check
    tests.yml            - Run test suite
    lint.yml             - Code quality checks
```

### Workflow Best Practices

#### Naming
- Use descriptive names: `dependency-check.yml`, not `ci.yml`
- Name jobs clearly: `run-tests`, `lint-python`, `build-docs`

#### Triggers
```yaml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  workflow_dispatch:  # Allow manual trigger
```

#### Job Structure
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - name: Check out repository
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run tests
        run: pytest tests/ -v
```

### Environment Setup

#### System Dependencies
```yaml
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y swi-prolog
```

#### Python Environment
```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: "3.10"
    cache: 'pip'  # Cache pip dependencies

- name: Install Python dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```

### Testing in CI

```yaml
- name: Run tests with coverage
  run: |
    pip install pytest pytest-cov
    pytest tests/ -v --cov=pipeline --cov=src --cov-report=xml

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

### Linting in CI

```yaml
- name: Lint with flake8
  run: |
    pip install flake8
    # Stop build if there are Python syntax errors or undefined names
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    # Exit-zero treats all errors as warnings
    flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

### Build Verification

```yaml
- name: Byte-compile source tree
  run: |
    python -m compileall training.py pipeline src

- name: Check for syntax errors
  run: |
    python -m py_compile training.py
    find pipeline src -name "*.py" -exec python -m py_compile {} \;
```

### Caching Dependencies

Speed up workflows with caching:

```yaml
- name: Cache pip packages
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

### Matrix Testing

Test multiple Python versions or configurations:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11"]
    
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Run tests
        run: pytest tests/
```

### Conditional Steps

```yaml
- name: Run GPU tests
  if: runner.os == 'Linux' && runner.arch == 'X64'
  run: pytest tests/test_gpu.py

- name: Deploy
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  run: |
    # Deployment commands
```

### Secrets Management

Never hardcode secrets in workflows:

```yaml
- name: Deploy to server
  env:
    API_KEY: ${{ secrets.API_KEY }}
    SERVER_URL: ${{ secrets.SERVER_URL }}
  run: |
    curl -X POST "$SERVER_URL" -H "Authorization: Bearer $API_KEY"
```

Add secrets in repository settings: Settings → Secrets and variables → Actions

### Artifacts

Save build outputs or test results:

```yaml
- name: Upload test results
  if: always()  # Run even if tests fail
  uses: actions/upload-artifact@v3
  with:
    name: test-results
    path: test-reports/

- name: Upload coverage report
  uses: actions/upload-artifact@v3
  with:
    name: coverage
    path: htmlcov/
```

### Status Badges

Add status badges to README.md:

```markdown
![Tests](https://github.com/user/repo/workflows/Tests/badge.svg)
![Coverage](https://codecov.io/gh/user/repo/branch/main/graph/badge.svg)
```

### Workflow Debugging

#### Enable Debug Logging
Add to repository secrets:
- `ACTIONS_RUNNER_DEBUG`: `true`
- `ACTIONS_STEP_DEBUG`: `true`

#### Use tmate for SSH Access
```yaml
- name: Setup tmate session
  if: failure()  # Only on failure
  uses: mxschmitt/action-tmate@v3
```

#### Add Debug Output
```yaml
- name: Debug information
  run: |
    echo "Python version: $(python --version)"
    echo "Pip version: $(pip --version)"
    echo "Working directory: $(pwd)"
    echo "Files: $(ls -la)"
    pip list
```

### Performance Optimization

1. **Parallel jobs**: Use matrix strategy for independent tests
2. **Cache dependencies**: Cache pip, npm packages
3. **Fail fast**: Set `fail-fast: true` in strategy
4. **Timeout**: Set job timeout to prevent hanging:
   ```yaml
   jobs:
     test:
       timeout-minutes: 30
   ```

### Common CI Patterns

#### Skip CI
Add to commit message to skip CI:
```
git commit -m "docs: update README [skip ci]"
```

#### Required Status Checks
Configure in repository settings which checks must pass before merging.

#### Branch Protection
- Require PR reviews
- Require status checks to pass
- Require branches to be up to date
- No force pushes

## Documentation Generation

### Using Sphinx (Python)

```yaml
- name: Build documentation
  run: |
    pip install sphinx sphinx-rtd-theme
    cd docs
    make html

- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./docs/_build/html
```

### Using MkDocs

```yaml
- name: Build documentation
  run: |
    pip install mkdocs mkdocs-material
    mkdocs build

- name: Deploy
  run: mkdocs gh-deploy --force
```

## Changelog Management

Maintain a CHANGELOG.md following [Keep a Changelog](https://keepachangelog.com/):

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- New feature X

### Changed
- Updated Y to improve performance

### Fixed
- Bug in Z component

## [1.0.0] - 2024-01-15

### Added
- Initial release
```

## Release Process

### Semantic Versioning
- MAJOR.MINOR.PATCH (e.g., 1.2.3)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Creating Releases

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          name: Release ${{ github.ref }}
          draft: false
          prerelease: false
```

## Documentation Checklist

When adding new features, ensure:

- [ ] README.md updated with new functionality
- [ ] Code examples added and tested
- [ ] API documentation updated
- [ ] Configuration options documented
- [ ] Breaking changes highlighted
- [ ] Migration guide provided (if needed)
- [ ] CHANGELOG.md updated

## CI/CD Checklist

Before merging:

- [ ] All tests pass
- [ ] Linting passes
- [ ] Code coverage meets threshold
- [ ] Documentation builds successfully
- [ ] No security vulnerabilities
- [ ] CI workflow completes in reasonable time (<10 minutes)
