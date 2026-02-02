# Contributing to Neurosymbolic Approach for Object Detection

This document provides comprehensive guidelines for contributing to this repository, ensuring consistent code quality, reproducibility, and a smooth development workflow.

---

## Table of Contents

1. [Python Best Practices](#python-best-practices)
2. [Machine Learning Lifecycle Guidelines](#machine-learning-lifecycle-guidelines)
3. [Software Development Lifecycle (SDLC) Principles](#software-development-lifecycle-sdlc-principles)
4. [Code Review Standards](#code-review-standards)

---

## Python Best Practices

### Coding Standards and PEP 8

We strictly adhere to [PEP 8](https://peps.python.org/pep-0008/), the official Python style guide. Key conventions include:

#### Indentation and Line Length
- Use **4 spaces** per indentation level (no tabs)
- Limit lines to **79 characters** for code
- Limit lines to **72 characters** for docstrings and comments
- Use implicit line continuation inside parentheses, brackets, and braces when possible

```python
# Good - implicit continuation
result = some_function(
    arg1, arg2, arg3,
    arg4, arg5
)

# Avoid - explicit backslash continuation
result = some_function(arg1, arg2, arg3, \
    arg4, arg5)
```

#### Imports
- Group imports in the following order:
  1. Standard library imports
  2. Related third-party imports
  3. Local application/library imports
- Place a blank line between each group
- Use absolute imports over relative imports

```python
# Good
import os
import sys
from pathlib import Path

import numpy as np
import torch
from ultralytics import YOLO

from config_utils import load_config_file
from pipeline.utils import parse_predictions_for_nms
```

#### Whitespace
- Avoid extraneous whitespace in the following situations:
  - Immediately inside parentheses, brackets, or braces
  - Between a trailing comma and a following close parenthesis
  - Immediately before a comma, semicolon, or colon

```python
# Good
spam(ham[1], {eggs: 2})
foo = (0,)
if x == 4: print(x, y); x, y = y, x

# Bad
spam( ham[ 1 ], { eggs: 2 } )
foo = (0, )
if x == 4 : print(x , y) ; x , y = y , x
```

### Naming Guidelines

Follow these naming conventions throughout the codebase:

#### General Rules
- **Modules**: `lowercase_with_underscores.py`
- **Classes**: `CapitalizedWords` (PascalCase)
- **Functions/Methods**: `lowercase_with_underscores` (snake_case)
- **Constants**: `UPPERCASE_WITH_UNDERSCORES`
- **Variables**: `lowercase_with_underscores`
- **Private attributes/methods**: prefix with single underscore `_private_method`

```python
# Good examples
class YOLOPredictor:
    """YOLO-based object detector."""
    
    MAX_DETECTIONS = 100
    
    def __init__(self):
        self.model_path = None
        self._confidence_threshold = 0.5
    
    def predict_on_image(self, image_path: str) -> list:
        """Run inference on a single image."""
        return self._apply_nms(image_path)
    
    def _apply_nms(self, image_path: str) -> list:
        """Private method for NMS filtering."""
        pass
```

#### Type Hints
- Use type hints for function parameters and return values
- Import types from `typing` module when needed

```python
from typing import List, Dict, Optional, Tuple

def load_predictions(
    predictions_dir: Path,
    confidence_threshold: float = 0.5
) -> Dict[str, List[Dict[str, Any]]]:
    """Load and filter predictions from directory."""
    pass
```

### Docstring Guidelines

We follow the **Google docstring style** for consistency. Every module, class, and function should have a docstring.

#### Module Docstrings
Place at the top of each file:

```python
"""Utility helpers shared across the neurosymbolic pipeline stages.

This module provides functions for parsing YOLO predictions, applying NMS,
and evaluating model performance using TorchMetrics.
"""
```

#### Class Docstrings

```python
class KnowledgeGraphBuilder:
    """Constructs weighted knowledge graphs from object detections.
    
    This class processes YOLO predictions to extract spatial relationships
    between detected objects and builds a directed graph representation.
    
    Attributes:
        model_path: Path to the trained YOLO checkpoint.
        confidence_threshold: Minimum confidence score for detections.
        iou_threshold: IoU threshold for NMS filtering.
    """
    
    def __init__(self, model_path: str, confidence_threshold: float = 0.5):
        """Initialize the KnowledgeGraphBuilder.
        
        Args:
            model_path: Path to the trained YOLO model weights.
            confidence_threshold: Minimum confidence score. Defaults to 0.5.
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
```

#### Function/Method Docstrings

```python
def pre_filter_with_nms(
    objects_in_image: List[Dict[str, Any]], 
    iou_threshold: float
) -> List[Dict[str, Any]]:
    """Apply torchvision NMS filtering to objects belonging to the same class.
    
    This function groups detections by class ID and applies Non-Maximum
    Suppression to eliminate duplicate detections with high overlap.
    
    Args:
        objects_in_image: List of detection dictionaries containing bbox_voc,
            confidence, and category_id keys.
        iou_threshold: Intersection-over-Union threshold for suppression.
            Detections with IoU > threshold are considered duplicates.
    
    Returns:
        Filtered list of detections after NMS is applied per class.
    
    Raises:
        ValueError: If objects_in_image contains invalid bbox format.
    
    Example:
        >>> detections = [
        ...     {"bbox_voc": [0, 0, 10, 10], "confidence": 0.9, "category_id": 0},
        ...     {"bbox_voc": [1, 1, 11, 11], "confidence": 0.8, "category_id": 0}
        ... ]
        >>> filtered = pre_filter_with_nms(detections, iou_threshold=0.5)
        >>> len(filtered)
        1
    """
    if not objects_in_image:
        return []
    # Implementation...
```

### Additional Python Best Practices

#### Error Handling
- Use specific exception types, not bare `except:`
- Provide meaningful error messages

```python
# Good
try:
    config = load_config_file(config_path)
except FileNotFoundError as e:
    raise FileNotFoundError(f"Config file not found: {config_path}") from e
except yaml.YAMLError as e:
    raise ValueError(f"Invalid YAML format in {config_path}") from e

# Bad
try:
    config = load_config_file(config_path)
except:
    pass
```

#### Context Managers
- Use context managers for resource management

```python
# Good
with open(file_path, 'r') as f:
    data = f.read()

# Also good for multiple resources
with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
    outfile.write(infile.read())
```

#### List Comprehensions
- Use list comprehensions for simple transformations
- Avoid overly complex comprehensions; use regular loops for clarity

```python
# Good - simple and readable
valid_files = [f for f in files if f.suffix == '.txt']

# Bad - too complex
result = [process(x) for sublist in nested_list 
          for x in sublist if x > 0 and validate(x)]

# Better - use regular loop for complex logic
result = []
for sublist in nested_list:
    for x in sublist:
        if x > 0 and validate(x):
            result.append(process(x))
```

---

## Machine Learning Lifecycle Guidelines

This section outlines best practices for managing the complete ML lifecycle, from data preparation to model deployment.

### 1. Data Preprocessing

#### Data Organization
- Store datasets in a consistent directory structure:
  ```
  dataset/
  ├── train/
  │   ├── images/
  │   └── labels/
  ├── val/
  │   ├── images/
  │   └── labels/
  └── test/
      ├── images/
      └── labels/
  ```

#### Data Versioning
- Use DVC (Data Version Control) or similar tools to track dataset versions
- Document dataset versions in `configs/` YAML files
- Never commit large data files to Git; use `.gitignore` appropriately

```yaml
# Example dataset configuration
dataset:
  name: "DOTA-v1.5"
  version: "2024-01-15"
  path: "/path/to/dataset"
  splits:
    train: "train"
    val: "val"
    test: "test"
```

#### Data Quality Checks
- Validate input data before training:
  - Check for missing files
  - Verify label formats (YOLO normalized coordinates)
  - Ensure class IDs are within expected range
  - Check for corrupted images

```python
def validate_dataset(data_yaml: str) -> None:
    """Validate dataset integrity before training.
    
    Args:
        data_yaml: Path to dataset configuration file.
    
    Raises:
        ValueError: If dataset structure is invalid.
    """
    # Check images and labels exist
    # Verify label format
    # Report statistics
    pass
```

### 2. Model Training

#### Reproducibility
To ensure reproducible experiments:

1. **Set Random Seeds**
   ```python
   import random
   import numpy as np
   import torch
   
   def set_seed(seed: int = 42) -> None:
       """Set random seeds for reproducibility.
       
       Args:
           seed: Random seed value.
       """
       random.seed(seed)
       np.random.seed(seed)
       torch.manual_seed(seed)
       if torch.cuda.is_available():
           torch.cuda.manual_seed(seed)
           torch.cuda.manual_seed_all(seed)
           torch.backends.cudnn.deterministic = True
           torch.backends.cudnn.benchmark = False
   ```

2. **Document Hyperparameters**
   - Store all hyperparameters in YAML configuration files
   - Version control configuration files
   - Log hyperparameters to experiment tracking tools (MLflow, Weights & Biases)

   ```yaml
   # training_config.yaml
   model:
     architecture: "yolov11"
     variant: "yolov11m-obb"
   
   training:
     epochs: 100
     batch_size: 16
     learning_rate: 0.001
     seed: 42
     device: "cuda"
   
   augmentation:
     hsv_h: 0.015
     hsv_s: 0.7
     hsv_v: 0.4
     degrees: 0.0
     translate: 0.1
   ```

3. **Track Experiments**
   - Log all experiments with unique identifiers
   - Save model checkpoints with descriptive names
   - Record training metrics (loss, mAP, etc.)

#### Training Best Practices
- Use GPU acceleration when available
- Implement early stopping to prevent overfitting
- Save checkpoints periodically
- Monitor training with validation metrics

```python
def train_model(config: dict) -> None:
    """Train YOLO model with configured parameters.
    
    Args:
        config: Training configuration dictionary.
    """
    set_seed(config['training']['seed'])
    
    model = YOLO(config['model']['variant'])
    
    results = model.train(
        data=config['data']['yaml_path'],
        epochs=config['training']['epochs'],
        batch=config['training']['batch_size'],
        device=config['training']['device'],
        project=config['output']['project_dir'],
        name=config['output']['experiment_name'],
        seed=config['training']['seed'],
        # Early stopping
        patience=config['training'].get('patience', 50),
    )
    
    return results
```

### 3. Model Evaluation

#### Comprehensive Metrics
- Report multiple evaluation metrics:
  - mAP (mean Average Precision) at different IoU thresholds
  - Precision and Recall per class
  - Confusion matrix
  - Inference time statistics

```python
def evaluate_model(
    predictions: List[Dict],
    ground_truth: List[Dict],
    class_names: List[str]
) -> Dict[str, float]:
    """Evaluate model predictions against ground truth.
    
    Args:
        predictions: List of prediction dictionaries.
        ground_truth: List of ground truth annotation dictionaries.
        class_names: List of class names for reporting.
    
    Returns:
        Dictionary containing evaluation metrics.
    """
    from torchmetrics.detection.mean_ap import MeanAveragePrecision
    
    metric = MeanAveragePrecision(box_format='xyxy', iou_type='bbox')
    metric.update(predictions, ground_truth)
    results = metric.compute()
    
    return {
        'mAP_50': results['map_50'].item(),
        'mAP_75': results['map_75'].item(),
        'mAP_50_95': results['map'].item(),
    }
```

#### Validation Protocol
- Use separate validation and test sets
- Perform cross-validation for small datasets
- Test on out-of-distribution samples when possible
- Document any data leakage issues

### 4. Model Deployment

#### Model Artifacts
- Package model weights with metadata:
  - Model architecture version
  - Training date and dataset version
  - Performance metrics
  - Inference requirements

```python
# model_metadata.yaml
model_info:
  name: "yolov11m-obb-dota"
  version: "1.0.0"
  created: "2024-01-15"
  framework: "ultralytics"
  
training:
  dataset: "DOTA-v1.5"
  epochs: 100
  final_map50: 0.756

requirements:
  python: ">=3.10"
  torch: ">=2.0.0"
  ultralytics: ">=8.0.0"

inference:
  input_size: [1024, 1024]
  confidence_threshold: 0.25
  iou_threshold: 0.45
```

#### Deployment Checklist
- [ ] Model weights are saved in a portable format
- [ ] Inference code is well-documented
- [ ] Input preprocessing is consistent with training
- [ ] Output format is documented
- [ ] Performance benchmarks are provided
- [ ] Error handling is robust

#### Inference Pipeline
```python
class ModelInference:
    """Production-ready inference pipeline.
    
    Attributes:
        model: Loaded YOLO model.
        config: Inference configuration.
    """
    
    def __init__(self, model_path: str, config: dict):
        """Initialize inference pipeline.
        
        Args:
            model_path: Path to model weights.
            config: Inference configuration dictionary.
        """
        self.model = self._load_model(model_path)
        self.config = config
    
    def _load_model(self, model_path: str):
        """Load model with error handling."""
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        return YOLO(model_path)
    
    def predict(self, image_path: str) -> List[Dict]:
        """Run inference on single image.
        
        Args:
            image_path: Path to input image.
        
        Returns:
            List of detection dictionaries.
        
        Raises:
            FileNotFoundError: If image does not exist.
            RuntimeError: If inference fails.
        """
        try:
            results = self.model.predict(
                source=image_path,
                conf=self.config['confidence_threshold'],
                iou=self.config['iou_threshold'],
                device=self.config.get('device', 'cpu'),
            )
            return self._format_results(results)
        except Exception as e:
            raise RuntimeError(f"Inference failed: {e}") from e
```

---

## Software Development Lifecycle (SDLC) Principles

### Git Workflow

We follow a **feature branch workflow** with the following conventions:

#### Branch Naming
- `feature/<description>` - New features
- `bugfix/<description>` - Bug fixes
- `hotfix/<description>` - Urgent production fixes
- `refactor/<description>` - Code refactoring
- `docs/<description>` - Documentation updates

Examples:
- `feature/add-sahi-integration`
- `bugfix/fix-nms-iou-calculation`
- `docs/update-installation-guide`

#### Workflow Steps

1. **Create a Feature Branch**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/my-new-feature
   ```

2. **Make Changes and Commit Regularly**
   - Write clear, descriptive commit messages
   - Follow the commit message format:
     ```
     <type>: <subject>
     
     <body>
     
     <footer>
     ```
   
   Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
   
   Examples:
   ```bash
   git commit -m "feat: add SAHI sliced inference support

   - Integrate SAHI library for large image processing
   - Add slice_width and slice_height parameters
   - Update documentation with SAHI usage examples"
   
   git commit -m "fix: correct IoU calculation in NMS
   
   The previous implementation didn't account for edge cases
   where boxes had zero area. Added validation checks.
   
   Closes #123"
   ```

3. **Keep Your Branch Updated**
   ```bash
   git checkout main
   git pull origin main
   git checkout feature/my-new-feature
   git merge main
   # Or use rebase for cleaner history (if you're comfortable with it)
   git rebase main
   ```

4. **Push Changes**
   ```bash
   git push origin feature/my-new-feature
   ```

5. **Open a Pull Request**
   - Use the PR template (see below)
   - Link related issues
   - Request reviews from relevant team members

#### Commit Message Best Practices

**Good Commit Messages:**
```
feat: implement knowledge graph construction pipeline

- Add weighted_kg_sahi.py for spatial relation extraction
- Integrate co-occurrence graph generation
- Export Prolog facts for symbolic reasoning

Closes #42
```

**Bad Commit Messages:**
```
update files
fix bug
changes
WIP
```

#### Pull Request Guidelines

##### PR Title Format
```
<type>: <brief description>
```

Examples:
- `feat: add symbolic reasoning pipeline`
- `fix: resolve CUDA memory leak in training loop`
- `docs: update README with configuration examples`

##### PR Description Template
```markdown
## Description
Brief summary of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Changes Made
- Detailed list of changes
- What was added/modified/removed

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

Describe the tests you ran and their results.

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Related Issues
Closes #<issue_number>
Relates to #<issue_number>
```

#### Squashing Commits
- Before merging, consider squashing related commits into logical units
- Preserve meaningful commit history
- Use interactive rebase for cleanup:
  ```bash
  git rebase -i main
  ```

### CI/CD Pipeline Expectations

#### Continuous Integration

Our CI pipeline runs automatically on every push and pull request. It includes:

1. **Dependency Installation**
   - Install system dependencies (SWI-Prolog)
   - Install Python dependencies from `requirements.txt`

2. **Code Quality Checks**
   - Linting with `flake8` or `pylint`
   - Type checking with `mypy` (if configured)
   - Import sorting with `isort`

3. **Testing**
   - Unit tests with `pytest`
   - Code coverage reporting
   - Minimum coverage threshold enforcement

4. **Build Verification**
   - Byte-compile all Python modules
   - Verify no syntax errors

#### CI Configuration

All CI workflows are defined in `.github/workflows/`. Key workflows include:

- `dependency-check.yml` - Validates dependencies and runs smoke tests
- Add more workflows as needed for:
  - Linting (`lint.yml`)
  - Testing (`tests.yml`)
  - Documentation building (`docs.yml`)

#### Making CI-Friendly Code

- **Ensure tests are deterministic**: Set random seeds, mock external dependencies
- **Keep tests fast**: Use smaller datasets for CI, parallelize when possible
- **Handle missing resources gracefully**: Skip GPU tests if CUDA unavailable
- **Document CI requirements**: List any system dependencies needed

```python
import pytest

@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
def test_gpu_training():
    """Test training with GPU acceleration."""
    pass

@pytest.fixture
def sample_config():
    """Provide minimal config for testing."""
    return {
        'training': {'epochs': 1, 'batch_size': 1},
        'data': {'yaml_path': 'test_data.yaml'},
    }
```

#### Continuous Deployment (Future)

When implementing CD:
- Deploy only from `main` branch
- Use semantic versioning for releases
- Tag releases in Git
- Automate model artifact uploads
- Update documentation automatically

---

## Code Review Standards

### For Contributors (Code Authors)

Before requesting a review, ensure your PR meets these criteria:

#### Pre-Review Checklist
- [ ] **Code Quality**
  - Follows PEP 8 style guidelines
  - No linting errors (`flake8`, `pylint`)
  - Type hints are present and correct
  - Complex logic is commented

- [ ] **Testing**
  - All new code has corresponding tests
  - All tests pass locally
  - Code coverage meets or exceeds project threshold
  - Edge cases are tested

- [ ] **Documentation**
  - Docstrings are complete and accurate
  - README is updated if needed
  - Configuration examples are provided
  - Breaking changes are clearly documented

- [ ] **Functionality**
  - Changes solve the intended problem
  - No unrelated changes included
  - Error handling is robust
  - Logging is appropriate

- [ ] **Performance**
  - No obvious performance regressions
  - Resource usage is reasonable
  - Large datasets are handled efficiently

- [ ] **Security**
  - No hardcoded credentials or secrets
  - Input validation is present
  - No SQL injection or similar vulnerabilities
  - Dependencies are from trusted sources

### For Reviewers

#### Review Process

1. **Understand the Context**
   - Read the PR description and linked issues
   - Understand the problem being solved
   - Check if the approach is appropriate

2. **Code Quality Review**
   - Verify adherence to style guidelines
   - Check for code smells and anti-patterns
   - Ensure proper use of language features
   - Look for opportunities to simplify

3. **Functional Review**
   - Does the code do what it claims?
   - Are edge cases handled?
   - Is error handling appropriate?
   - Are there potential bugs?

4. **Testing Review**
   - Are tests comprehensive?
   - Do tests actually verify the functionality?
   - Are tests maintainable?
   - Is test coverage adequate?

5. **Documentation Review**
   - Are docstrings accurate and complete?
   - Is the README updated?
   - Are configuration changes documented?
   - Are breaking changes clearly noted?

#### Reviewer Checklist

- [ ] **Correctness**
  - Code logic is sound
  - No obvious bugs
  - Edge cases are handled
  - Algorithm implementation is correct

- [ ] **Design**
  - Code is well-structured
  - Appropriate abstraction levels
  - Follows SOLID principles
  - Integrates well with existing code

- [ ] **Readability**
  - Code is self-documenting where possible
  - Complex sections are commented
  - Naming is clear and consistent
  - No unnecessary complexity

- [ ] **Testing**
  - Tests cover the main functionality
  - Tests are reliable and deterministic
  - Negative test cases are included
  - Mocking is used appropriately

- [ ] **Documentation**
  - All public APIs are documented
  - Usage examples are provided
  - Configuration is explained
  - Dependencies are documented

- [ ] **Performance**
  - No obvious performance issues
  - Algorithms are efficient
  - Resource usage is reasonable
  - Bottlenecks are addressed

- [ ] **Security**
  - No security vulnerabilities introduced
  - Input is validated
  - No sensitive data exposure
  - Dependencies are up to date

#### Providing Feedback

**Good Feedback:**
- Specific and actionable
- Explains the "why" behind suggestions
- Offers alternatives when possible
- Balances criticism with praise
- Uses a constructive tone

Example:
```
Consider using a dictionary comprehension here instead of a loop for better performance:

# Current:
result = {}
for item in items:
    result[item.id] = item.value

# Suggested:
result = {item.id: item.value for item in items}

This is more Pythonic and generally faster for building dictionaries.
```

**Poor Feedback:**
```
This is bad. Fix it.
```

#### Review Categories

Use these labels to categorize feedback:

- **[CRITICAL]** - Must be fixed before merging (bugs, security issues)
- **[MAJOR]** - Should be fixed (design issues, significant improvements)
- **[MINOR]** - Nice to have (style, minor improvements)
- **[QUESTION]** - Seeking clarification
- **[PRAISE]** - Positive feedback on good code

Example:
```
[CRITICAL] This will cause a division by zero error when `total_items` is 0. 
Add a check before division.

[MINOR] Consider using f-strings instead of .format() for better readability.

[PRAISE] Great use of type hints and clear docstring!
```

### Merging Criteria

A PR can be merged when:

1. **All Required Reviews are Approved**
   - At least one approval from a core maintainer
   - All review comments are addressed or resolved

2. **All CI Checks Pass**
   - Tests pass
   - Linting passes
   - Build succeeds
   - Coverage meets threshold

3. **No Merge Conflicts**
   - Branch is up to date with main
   - No conflicting changes

4. **Documentation is Complete**
   - Docstrings are present
   - README is updated if needed
   - Breaking changes are documented

5. **Author Confirmation**
   - Author confirms PR is ready to merge
   - All requested changes have been made

### Post-Merge

After merging:
- Delete the feature branch (if no longer needed)
- Close related issues
- Update project board or tracking system
- Consider creating a release if appropriate
- Monitor for any issues in production/staging

---

## Additional Resources

### Useful Tools

- **Code Formatting**: `black`, `autopep8`
- **Linting**: `flake8`, `pylint`
- **Type Checking**: `mypy`
- **Testing**: `pytest`, `unittest`
- **Coverage**: `pytest-cov`, `coverage`
- **Documentation**: `sphinx`, `mkdocs`

### Learning Resources

- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Real Python Tutorials](https://realpython.com/)
- [Python Type Hints Documentation](https://docs.python.org/3/library/typing.html)
- [Git Best Practices](https://git-scm.com/book/en/v2)
- [Effective Python by Brett Slatkin](https://effectivepython.com/)

### Getting Help

If you have questions or need assistance:
1. Check existing documentation and issues
2. Ask in pull request discussions
3. Create a new issue with the `question` label
4. Reach out to maintainers

---

## Conclusion

Following these guidelines ensures:
- **Consistent code quality** across the repository
- **Reproducible experiments** and results
- **Smooth collaboration** among contributors
- **Easier maintenance** and debugging
- **Better code reviews** and faster merges

Thank you for contributing to the Neurosymbolic Approach for Object Detection project! 🚀
