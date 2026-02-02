# Development Instructions and Best Practices

This document defines the standards and best practices for contributing to the Neurosymbolic Object Detection repository. All contributors should familiarize themselves with these guidelines before making changes.

## Table of Contents

1. [Python Best Practices](#python-best-practices)
2. [ML Lifecycle Guidelines](#ml-lifecycle-guidelines)
3. [SDLC Principles](#sdlc-principles)
4. [Code Review Standards](#code-review-standards)

---

## Python Best Practices

### PEP 8 Conventions

All Python code must adhere to [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines:

- **Indentation**: Use 4 spaces per indentation level (no tabs)
- **Line Length**: Maximum 88 characters (Black formatter standard)
- **Imports**: Group imports in the following order:
  1. Standard library imports
  2. Related third-party imports
  3. Local application/library imports
- **Naming Conventions**:
  - `snake_case` for functions, methods, and variables
  - `PascalCase` for class names
  - `UPPER_CASE` for constants
  - Private methods/attributes should start with `_`

### Docstring Standards

Use Google-style docstrings for all public modules, classes, and functions:

```python
def calculate_iou(box1: list[float], box2: list[float]) -> float:
    """Calculate Intersection over Union (IoU) between two bounding boxes.

    Args:
        box1: Bounding box in format [x1, y1, x2, y2]
        box2: Bounding box in format [x1, y1, x2, y2]

    Returns:
        IoU value between 0 and 1

    Raises:
        ValueError: If boxes have invalid coordinates

    Example:
        >>> calculate_iou([0, 0, 10, 10], [5, 5, 15, 15])
        0.142857
    """
    # Implementation here
    pass
```

### Type Hints

Use type hints for all function parameters and return values:

```python
from typing import Dict, List, Optional, Union
from pathlib import Path

def load_config(config_path: Path) -> Dict[str, Union[str, int, float]]:
    """Load configuration from YAML file."""
    pass

def process_predictions(
    predictions: List[Dict[str, float]], 
    threshold: float = 0.5
) -> Optional[List[Dict[str, float]]]:
    """Filter predictions by confidence threshold."""
    pass
```

### Error Handling

- Use specific exception types
- Always provide meaningful error messages
- Log errors appropriately

```python
import logging

logger = logging.getLogger(__name__)

try:
    result = process_data(input_data)
except FileNotFoundError as e:
    logger.error(f"Input file not found: {e}")
    raise
except ValueError as e:
    logger.error(f"Invalid data format: {e}")
    raise
```

### Code Organization

- Keep functions small and focused (< 50 lines ideally)
- Follow Single Responsibility Principle
- Use meaningful variable names
- Avoid magic numbers - use named constants

```python
# Bad
def process(x, y):
    return x * 0.114 + y * 0.299

# Good
RED_WEIGHT = 0.299
BLUE_WEIGHT = 0.114

def calculate_grayscale(red_channel: float, blue_channel: float) -> float:
    """Calculate grayscale value using standard RGB weights."""
    return red_channel * RED_WEIGHT + blue_channel * BLUE_WEIGHT
```

---

## ML Lifecycle Guidelines

### Data Preprocessing

1. **Reproducibility**: Always set random seeds for reproducible results
   ```python
   import random
   import numpy as np
   import torch
   
   def set_seed(seed: int = 42) -> None:
       """Set random seeds for reproducibility."""
       random.seed(seed)
       np.random.seed(seed)
       torch.manual_seed(seed)
       if torch.cuda.is_available():
           torch.cuda.manual_seed_all(seed)
   ```

2. **Data Versioning**: Track dataset versions using:
   - Git LFS for small datasets
   - DVC (Data Version Control) for large datasets
   - Document dataset sources and preprocessing steps

3. **Validation**: Always validate input data:
   ```python
   def validate_image_format(image_path: Path) -> bool:
       """Validate image file format and integrity."""
       valid_extensions = {'.jpg', '.jpeg', '.png'}
       return image_path.suffix.lower() in valid_extensions
   ```

### Model Training

1. **Configuration Management**: Use YAML files for all hyperparameters
2. **Logging**: Log all training metrics and hyperparameters
3. **Checkpointing**: Save model checkpoints regularly
4. **Early Stopping**: Implement early stopping to prevent overfitting

```python
from pathlib import Path
import yaml

def train_model(config_path: Path) -> None:
    """Train model with configuration from YAML file."""
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Set reproducibility
    set_seed(config.get('seed', 42))
    
    # Training loop with logging
    for epoch in range(config['epochs']):
        train_loss = train_epoch(model, train_loader)
        val_loss = validate_epoch(model, val_loader)
        
        logger.info(f"Epoch {epoch}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}")
        
        # Save checkpoint
        if epoch % config['save_every'] == 0:
            save_checkpoint(model, epoch, val_loss)
```

### Model Evaluation

1. **Metrics**: Use standard metrics appropriate for the task
   - Object Detection: mAP, precision, recall, IoU
2. **Test Set**: Never train on test data
3. **Documentation**: Document evaluation methodology and results

### Deployment

1. **Model Serialization**: Save models in standard formats (PyTorch .pt, ONNX)
2. **API Design**: Follow RESTful principles
3. **Monitoring**: Implement metrics collection for production models

---

## SDLC Principles

### Git Workflow

#### Branch Strategy

- `main`: Production-ready code only
- `develop`: Integration branch for features
- `feature/*`: Feature development branches
- `bugfix/*`: Bug fix branches
- `hotfix/*`: Critical production fixes

#### Workflow Steps

1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/add-new-endpoint
   ```

2. **Make Changes**: Commit early and often with meaningful messages
   ```bash
   git add .
   git commit -m "feat: Add /predict endpoint for real-time inference"
   ```

3. **Keep Branch Updated**:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

4. **Push Changes**:
   ```bash
   git push origin feature/add-new-endpoint
   ```

5. **Create Pull Request**: Use descriptive PR title and description

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: Add Prometheus metrics endpoint
fix: Resolve NMS threshold calculation bug
docs: Update API documentation for /train endpoint
test: Add unit tests for symbolic reasoning module
```

### Pull Request Guidelines

1. **Title**: Clear and descriptive (e.g., "Add FastAPI backend with training endpoint")
2. **Description**: Include:
   - What changes were made
   - Why changes were necessary
   - How to test the changes
   - Related issues (if any)
3. **Size**: Keep PRs focused and reasonably sized (< 500 lines preferred)
4. **Tests**: Include tests for new functionality
5. **Documentation**: Update docs if behavior changes

### CI/CD Pipeline Expectations

All code must pass automated checks before merging:

1. **Linting**: Code must pass linting checks
   - Python: `flake8`, `black`
   - JavaScript: `prettier`, `eslint`

2. **Testing**: All tests must pass
   - Minimum 80% code coverage for new code
   - Unit tests for business logic
   - Integration tests for APIs

3. **Security**: No security vulnerabilities
   - Dependency scanning
   - Code security analysis

4. **Docker Builds**: Container images must build successfully

---

## Code Review Standards

### For Contributors (Before Requesting Review)

#### Pre-Review Checklist

- [ ] Code follows PEP 8 and project style guidelines
- [ ] All functions have docstrings
- [ ] Type hints are included
- [ ] Tests are written and passing (80%+ coverage)
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] Branch is up-to-date with main/develop
- [ ] No sensitive data or credentials in code
- [ ] Linting passes without errors
- [ ] CI/CD pipeline passes

#### Self-Review

Before requesting review:
1. Review your own diff on GitHub
2. Check for commented-out code or debug statements
3. Verify test coverage
4. Run the code locally to ensure it works

### For Reviewers

#### Review Checklist

- [ ] **Functionality**: Does the code do what it's supposed to?
- [ ] **Tests**: Are there adequate tests? Do they test the right things?
- [ ] **Documentation**: Is the code well-documented?
- [ ] **Code Quality**: Is the code clean, readable, and maintainable?
- [ ] **Performance**: Are there any obvious performance issues?
- [ ] **Security**: Are there security concerns?
- [ ] **Architecture**: Does it fit with existing architecture?
- [ ] **Error Handling**: Are errors handled appropriately?

#### Review Guidelines

1. **Be Constructive**: Provide specific, actionable feedback
   - Good: "Consider extracting this logic into a separate function for reusability"
   - Bad: "This code is messy"

2. **Ask Questions**: If something is unclear, ask for clarification

3. **Acknowledge Good Work**: Highlight good practices and clever solutions

4. **Focus on Important Issues**: Distinguish between:
   - **Critical**: Must be fixed (bugs, security issues)
   - **Important**: Should be fixed (design issues, missing tests)
   - **Nice-to-have**: Suggestions for improvement

5. **Be Timely**: Try to review PRs within 24 hours

### Merging Criteria

A PR can be merged when:

1. ✅ All automated checks pass (CI/CD green)
2. ✅ At least one approval from a code owner
3. ✅ All critical and important feedback addressed
4. ✅ No unresolved conversations
5. ✅ Documentation updated
6. ✅ Tests passing with adequate coverage

### After Merging

1. Delete the feature branch
2. Verify deployment (if applicable)
3. Monitor for any issues
4. Update related issues/tickets

---

## Additional Resources

- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [PyTorch Best Practices](https://pytorch.org/docs/stable/notes/best_practices.html)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [React Best Practices](https://react.dev/learn)

---

## Questions or Suggestions?

If you have questions about these guidelines or suggestions for improvements, please:
1. Open an issue for discussion
2. Submit a PR to update this document
3. Contact the maintainers

Remember: These guidelines exist to ensure code quality and maintainability. When in doubt, ask for clarification!
