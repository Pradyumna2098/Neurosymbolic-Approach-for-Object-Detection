# Tests

This directory contains the test suite for all subprojects in the mono-repository.

## Structure

```
tests/
├── pipeline/           # Tests for pipeline subproject (AI/ML core)
│   ├── test_utils.py
│   └── README.md
├── backend/            # Tests for backend APIs (planned)
│   └── README.md
├── frontend/           # Tests for frontend dashboards (planned)
│   └── README.md
└── README.md           # This file
```

## Running Tests

### All Tests
```bash
pytest tests/ -v
```

### By Subproject
```bash
# Pipeline tests
pytest tests/pipeline/ -v

# Backend tests (when implemented)
pytest tests/backend/ -v

# Frontend tests (when implemented)
pytest tests/frontend/ -v
```

### With Coverage
```bash
# Generate coverage report
pytest tests/ --cov=pipeline --cov=backend --cov=frontend --cov=shared --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Test Organization

Tests are organized by subproject to maintain separation of concerns:

- **pipeline/**: Tests for AI/ML pipeline components
  - Data preprocessing and NMS
  - Symbolic reasoning with Prolog
  - Model training and evaluation
  - Knowledge graph construction
  
- **backend/**: Tests for API endpoints and services (planned)
  - REST API endpoint testing
  - Authentication and authorization
  - Job queue management
  - Database operations
  
- **frontend/**: Tests for UI components and workflows (planned)
  - Component unit tests
  - Integration tests
  - End-to-end tests
  - Visual regression tests

## Test Requirements

All code changes should include appropriate tests:

1. **Unit Tests**: Test individual functions and methods in isolation
2. **Integration Tests**: Test interactions between components
3. **Edge Cases**: Test boundary conditions and error handling
4. **Mocking**: Mock external dependencies (APIs, databases, models)
5. **Documentation**: Include docstrings explaining what each test validates

## Coverage Goals

- **Pipeline**: Aim for 80%+ coverage on core functionality
- **Backend**: Aim for 90%+ coverage on API endpoints
- **Frontend**: Aim for 80%+ coverage on components
- **Shared**: Aim for 90%+ coverage on utilities

## Continuous Integration

Tests run automatically on:
- Every push to any branch
- Every pull request
- Scheduled daily runs on main branch

See `.github/workflows/` for CI configuration.

## Writing Good Tests

### Test Naming
Use descriptive names that explain what is being tested:
```python
def test_nms_removes_overlapping_boxes_with_high_iou():
    """Test that NMS filters out boxes with IoU > threshold."""
    # Test implementation
```

### Test Structure (AAA Pattern)
```python
def test_example():
    # Arrange: Set up test data
    detections = create_test_detections()
    
    # Act: Execute the function
    result = process_detections(detections)
    
    # Assert: Verify the outcome
    assert len(result) == expected_count
    assert result[0]['confidence'] > 0.5
```

### Fixtures for Common Setup
```python
import pytest

@pytest.fixture
def sample_config():
    """Provide a sample configuration for tests."""
    return {
        'model': 'yolov11m',
        'confidence_threshold': 0.25,
        'iou_threshold': 0.45
    }

def test_with_fixture(sample_config):
    model = load_model(sample_config)
    assert model is not None
```

## Test Dependencies

Install test dependencies:
```bash
pip install pytest pytest-cov pytest-mock
```

For additional testing tools, see `requirements/test.txt` (if exists).

## Debugging Tests

### Run Single Test
```bash
pytest tests/pipeline/test_utils.py::test_specific_function -v
```

### Show Print Statements
```bash
pytest tests/ -v -s
```

### Drop into Debugger on Failure
```bash
pytest tests/ --pdb
```

### Show Local Variables on Failure
```bash
pytest tests/ -v -l
```

## Related Documentation

- [Pipeline Tests README](pipeline/README.md)
- [Backend Tests README](backend/README.md)
- [Frontend Tests README](frontend/README.md)
- Main [Testing Instructions](../.github/instructions/tests.instructions.md)

## Contributing

When adding new features:
1. Write tests first (TDD approach recommended)
2. Ensure all tests pass before committing
3. Maintain or improve code coverage
4. Update test documentation if needed
