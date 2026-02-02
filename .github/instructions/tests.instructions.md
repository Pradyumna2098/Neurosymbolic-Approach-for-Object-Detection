---
applyTo: "tests/**/*.py"
---

# Unit Tests Instructions

These instructions apply to all test files in the repository.

## Testing Framework

This project uses **pytest** as the testing framework.

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_utils.py

# Run with coverage
pytest --cov=pipeline --cov=src tests/

# Run with verbose output
pytest -v

# Run specific test function
pytest tests/test_utils.py::test_function_name
```

## Test Structure

### Test File Organization
- Test files must be named `test_*.py` or `*_test.py`
- Place tests in the `tests/` directory
- Mirror the structure of the source code being tested

Example:
```
pipeline/
  utils.py
  preprocess.py
tests/
  test_utils.py
  test_preprocess.py
```

### Test Function Naming
- Use descriptive names: `test_<function>_<scenario>_<expected_result>`
- Examples:
  - `test_parse_predictions_with_valid_file_returns_dict`
  - `test_nms_with_empty_list_returns_empty_list`
  - `test_load_config_with_missing_file_raises_error`

## Writing Tests

### Basic Test Pattern
```python
import pytest
from pipeline.utils import parse_predictions_for_nms

def test_parse_predictions_returns_dict(tmp_path):
    """Test that parse_predictions returns a dictionary."""
    # Arrange - set up test data
    predictions_dir = tmp_path / "predictions"
    predictions_dir.mkdir()
    pred_file = predictions_dir / "image001.txt"
    pred_file.write_text("0 0.5 0.5 0.1 0.1 0.95\n")
    
    # Act - execute the function
    result = parse_predictions_for_nms(predictions_dir)
    
    # Assert - verify the outcome
    assert isinstance(result, dict)
    assert "image001.png" in result
    assert len(result["image001.png"]) == 1
```

### Using Fixtures

Pytest fixtures provide reusable test setup:

```python
import pytest
from pathlib import Path

@pytest.fixture
def sample_predictions_dir(tmp_path):
    """Create a temporary predictions directory with sample files."""
    predictions_dir = tmp_path / "predictions"
    predictions_dir.mkdir()
    
    # Create sample prediction file
    pred_file = predictions_dir / "test_image.txt"
    pred_file.write_text("0 0.5 0.5 0.2 0.2 0.9\n1 0.3 0.3 0.1 0.1 0.8\n")
    
    return predictions_dir

def test_function_with_fixture(sample_predictions_dir):
    """Test using the fixture."""
    result = parse_predictions_for_nms(sample_predictions_dir)
    assert len(result) > 0
```

### Testing with Mock Data

For ML components, use small synthetic datasets:

```python
import torch
import numpy as np

@pytest.fixture
def mock_detections():
    """Mock detection results for testing."""
    return [
        {
            "category_id": 0,
            "bbox_voc": [10, 10, 50, 50],
            "bbox_yolo": [0.3, 0.3, 0.2, 0.2],
            "confidence": 0.95
        },
        {
            "category_id": 0,
            "bbox_voc": [15, 15, 55, 55],
            "bbox_yolo": [0.35, 0.35, 0.2, 0.2],
            "confidence": 0.85
        }
    ]

def test_nms_removes_overlapping_boxes(mock_detections):
    """Test NMS removes overlapping detections."""
    from pipeline.utils import pre_filter_with_nms
    
    filtered = pre_filter_with_nms(mock_detections, iou_threshold=0.5)
    
    # Should keep only the higher confidence detection
    assert len(filtered) == 1
    assert filtered[0]["confidence"] == 0.95
```

### Mocking Heavy Operations

Mock model loading and inference to avoid long test times:

```python
from unittest.mock import Mock, patch

@patch('ultralytics.YOLO')
def test_training_script_loads_model(mock_yolo):
    """Test that training script properly loads YOLO model."""
    mock_model = Mock()
    mock_yolo.return_value = mock_model
    
    # Your training code here
    from training import train_model
    
    train_model({'model': {'variant': 'yolov11n'}})
    
    # Verify model was loaded
    mock_yolo.assert_called_once_with('yolov11n')
```

## Test Coverage

### Coverage Requirements
- Aim for at least **80% code coverage** for core functionality
- All public functions should have tests
- Edge cases and error conditions must be tested

### Running Coverage
```bash
# Generate coverage report
pytest --cov=pipeline --cov=src --cov-report=html tests/

# View report
open htmlcov/index.html  # or xdg-open on Linux
```

## Testing Guidelines

### What to Test
1. **Happy path**: Function works with valid inputs
2. **Edge cases**: Empty inputs, boundary values, large datasets
3. **Error conditions**: Invalid inputs, missing files, wrong types
4. **Integration**: Components work together correctly

### What NOT to Test
1. **Third-party libraries**: Don't test PyTorch, YOLO, etc.
2. **Python built-ins**: Don't test standard library functions
3. **Simple getters/setters**: Only test if they have logic

### Assertion Best Practices

Use specific assertions:
```python
# Good - specific assertions
assert result == expected_value
assert isinstance(result, dict)
assert len(result) == 3
assert "key" in result
assert result["key"] > 0

# Bad - too generic
assert result
assert result is not None
```

### Testing Exceptions
```python
import pytest

def test_function_raises_error_with_invalid_input():
    """Test that function raises ValueError for invalid input."""
    with pytest.raises(ValueError, match="Invalid input"):
        function_that_should_fail(invalid_input)

def test_function_raises_file_not_found():
    """Test that function raises FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError):
        load_file("/nonexistent/path.txt")
```

## Parametrized Tests

Test multiple scenarios efficiently:

```python
@pytest.mark.parametrize("input_val,expected", [
    (0, 0),
    (1, 1),
    (5, 25),
    (10, 100),
])
def test_square_function(input_val, expected):
    """Test square function with multiple inputs."""
    assert square(input_val) == expected

@pytest.mark.parametrize("iou_threshold", [0.3, 0.5, 0.7])
def test_nms_with_different_thresholds(iou_threshold, mock_detections):
    """Test NMS with various IoU thresholds."""
    result = pre_filter_with_nms(mock_detections, iou_threshold)
    assert isinstance(result, list)
```

## Reproducibility in Tests

### Set Random Seeds
```python
import random
import numpy as np
import torch

@pytest.fixture(autouse=True)
def set_random_seed():
    """Set random seeds before each test for reproducibility."""
    seed = 42
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
```

### Deterministic Tests
- Tests should produce the same results every time
- Avoid time-based values unless necessary
- Use fixed random seeds for stochastic operations

## Testing ML Components

### Dataset Tests
```python
def test_dataset_returns_correct_format(sample_dataset):
    """Test dataset returns expected data format."""
    item = sample_dataset[0]
    
    assert "image" in item
    assert "labels" in item
    assert isinstance(item["image"], torch.Tensor)
    assert item["image"].shape[0] == 3  # RGB channels
```

### Model Tests
```python
def test_model_output_shape(mock_model, sample_input):
    """Test model produces output with expected shape."""
    output = mock_model(sample_input)
    
    assert output.shape[0] == sample_input.shape[0]  # Batch size
    assert len(output.shape) == 2  # 2D output
```

### Metric Tests
```python
def test_map_calculation_with_perfect_predictions():
    """Test mAP is 1.0 with perfect predictions."""
    from torchmetrics.detection import MeanAveragePrecision
    
    metric = MeanAveragePrecision()
    
    # Perfect predictions
    preds = [{"boxes": torch.tensor([[0, 0, 10, 10]]), 
              "scores": torch.tensor([1.0]),
              "labels": torch.tensor([0])}]
    
    targets = [{"boxes": torch.tensor([[0, 0, 10, 10]]),
                "labels": torch.tensor([0])}]
    
    metric.update(preds, targets)
    result = metric.compute()
    
    assert result["map"].item() == 1.0
```

## CI/CD Integration

Tests run automatically on every push and pull request:

```yaml
# .github/workflows/tests.yml (example)
- name: Run tests
  run: |
    pytest tests/ -v --cov=pipeline --cov=src
```

### Making Tests CI-Friendly
1. **Fast execution**: Keep tests under 5 minutes total
2. **No external dependencies**: Mock API calls, file downloads
3. **Skip GPU tests in CI**: Use `@pytest.mark.skipif(not torch.cuda.is_available())`
4. **Deterministic**: No flaky tests that pass/fail randomly

```python
@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
def test_gpu_inference():
    """Test model inference on GPU."""
    # GPU-specific test
    pass
```

## Debugging Tests

### Run Single Test with Output
```bash
pytest tests/test_utils.py::test_specific_function -v -s
```

### Use Debugger
```python
def test_function():
    import pdb; pdb.set_trace()  # Set breakpoint
    result = function_to_test()
    assert result == expected
```

### Print Debug Info
```python
def test_function(capfd):
    """Test with captured output."""
    result = function_to_test()
    print(f"Result: {result}")  # Will be captured
    
    captured = capfd.readouterr()
    assert "expected" in captured.out
```

## Common Testing Patterns

### Testing File I/O
```python
def test_save_predictions(tmp_path):
    """Test saving predictions to file."""
    output_file = tmp_path / "predictions.txt"
    predictions = [{"class": 0, "confidence": 0.9}]
    
    save_predictions(predictions, output_file)
    
    assert output_file.exists()
    content = output_file.read_text()
    assert "0.9" in content
```

### Testing CLI Scripts
```python
from click.testing import CliRunner

def test_cli_command():
    """Test command-line interface."""
    runner = CliRunner()
    result = runner.invoke(cli_command, ['--config', 'test_config.yaml'])
    
    assert result.exit_code == 0
    assert "Success" in result.output
```

## Test Maintenance

- Keep tests up to date with code changes
- Remove obsolete tests when features are removed
- Refactor tests to reduce duplication
- Update fixtures when data formats change
- Document complex test setups

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Testing PyTorch Code](https://pytorch.org/docs/stable/notes/randomness.html)
