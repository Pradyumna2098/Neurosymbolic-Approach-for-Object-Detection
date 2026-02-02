# Contributing to Neurosymbolic Object Detection

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Pull Request Process](#pull-request-process)
5. [Coding Standards](#coding-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Documentation](#documentation)

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

**Unacceptable behavior includes:**
- Harassment, trolling, or derogatory comments
- Publishing others' private information
- Other conduct which could be considered inappropriate

## Getting Started

### Prerequisites

Before you begin:
1. Read the [instructions.md](instructions.md) file thoroughly
2. Set up your development environment using `./setup.sh`
3. Familiarize yourself with the codebase structure
4. Review existing issues and pull requests

### Finding Issues to Work On

- Look for issues labeled `good-first-issue` for beginner-friendly tasks
- Check issues labeled `help-wanted` for more challenging work
- Feel free to propose new features or improvements

## Development Workflow

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/Neurosymbolic-Approach-for-Object-Detection.git
cd Neurosymbolic-Approach-for-Object-Detection

# Add upstream remote
git remote add upstream https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection.git
```

### 2. Create a Branch

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number-description
```

Branch naming conventions:
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation updates
- `test/` - Test additions or modifications
- `refactor/` - Code refactoring

### 3. Make Your Changes

- Write clean, readable code following our style guide
- Add tests for new functionality
- Update documentation as needed
- Keep commits small and focused

### 4. Test Your Changes

```bash
# Run backend tests
pytest tests/backend/ -v

# Run pipeline tests
pytest tests/pipeline/ -v

# Run frontend tests
cd frontend && npm test

# Check linting
flake8 .
black --check .
cd frontend && npx prettier --check "src/**/*.{js,jsx,css}"
```

### 5. Commit Your Changes

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git add .
git commit -m "feat: add new training endpoint"
# or
git commit -m "fix: resolve NMS threshold bug"
```

Commit types:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `style:` - Formatting changes
- `refactor:` - Code restructuring
- `test:` - Adding tests
- `chore:` - Maintenance

### 6. Keep Your Branch Updated

```bash
git fetch upstream
git rebase upstream/main
```

### 7. Push Your Changes

```bash
git push origin feature/your-feature-name
```

## Pull Request Process

### Before Submitting

Ensure your PR:
- [ ] Passes all CI checks
- [ ] Includes tests for new functionality
- [ ] Updates relevant documentation
- [ ] Follows our coding standards
- [ ] Has a clear, descriptive title
- [ ] References related issues

### PR Template

Use this template for your PR description:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #(issue number)

## How to Test
Steps to test the changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added to complex code
- [ ] Documentation updated
- [ ] Tests added and passing
- [ ] No new warnings generated
```

### Review Process

1. Maintainers will review your PR within 1-3 business days
2. Address any feedback or requested changes
3. Once approved, a maintainer will merge your PR
4. Your changes will be included in the next release

## Coding Standards

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints for all functions
- Maximum line length: 88 characters (Black standard)
- Write docstrings for all public functions/classes

Example:
```python
def process_predictions(
    predictions: List[Dict[str, float]], 
    threshold: float = 0.5
) -> List[Dict[str, float]]:
    """Filter predictions by confidence threshold.
    
    Args:
        predictions: List of prediction dictionaries
        threshold: Minimum confidence threshold
        
    Returns:
        Filtered list of predictions
    """
    return [p for p in predictions if p['confidence'] >= threshold]
```

### JavaScript/React

- Use functional components with hooks
- Follow Airbnb JavaScript style guide
- Use meaningful variable names
- Keep components small and focused

Example:
```javascript
function PredictionCard({ prediction, onSelect }) {
  const [isHovered, setIsHovered] = useState(false);
  
  return (
    <div 
      className={`prediction-card ${isHovered ? 'hovered' : ''}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => onSelect(prediction.id)}
    >
      <h3>{prediction.class_name}</h3>
      <p>Confidence: {(prediction.confidence * 100).toFixed(2)}%</p>
    </div>
  );
}
```

## Testing Guidelines

### Unit Tests

- Test individual functions in isolation
- Use descriptive test names
- Follow Arrange-Act-Assert pattern
- Aim for 80%+ code coverage

Example:
```python
def test_apply_nms_removes_overlapping_boxes():
    """Test that NMS correctly removes overlapping detections."""
    # Arrange
    boxes = [
        {'bbox': [0, 0, 10, 10], 'confidence': 0.9},
        {'bbox': [1, 1, 11, 11], 'confidence': 0.7}
    ]
    
    # Act
    filtered = apply_nms(boxes, iou_threshold=0.5)
    
    # Assert
    assert len(filtered) == 1
    assert filtered[0]['confidence'] == 0.9
```

### Integration Tests

- Test component interactions
- Use realistic test data
- Mock external dependencies

### Frontend Tests

```javascript
test('displays prediction list', async () => {
  const mockPredictions = [
    { id: 1, class: 'car', confidence: 0.95 }
  ];
  
  render(<PredictionList predictions={mockPredictions} />);
  
  expect(screen.getByText('car')).toBeInTheDocument();
  expect(screen.getByText('95%')).toBeInTheDocument();
});
```

## Documentation

### Code Documentation

- Add docstrings to all public functions/classes
- Comment complex logic
- Keep comments up-to-date

### README Updates

Update README.md when adding:
- New features or endpoints
- Configuration options
- Dependencies
- Setup instructions

### API Documentation

- Document all API endpoints
- Include request/response examples
- Note authentication requirements
- List possible error codes

## Questions?

- Open an issue for bugs or feature requests
- Use GitHub Discussions for questions
- Check existing issues before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing! 🎉
