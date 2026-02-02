# Pipeline Tests

This directory contains tests for the pipeline subproject - the core AI/ML functionality.

## Structure

```
tests/pipeline/
└── test_utils.py         # Tests for utility functions
```

## Running Tests

```bash
# Run all pipeline tests
pytest tests/pipeline/ -v

# Run with coverage
pytest tests/pipeline/ --cov=pipeline --cov-report=html

# Run specific test file
pytest tests/pipeline/test_utils.py -v
```

## Test Coverage

Current tests cover:
- NMS filtering functionality (`test_pre_filter_with_nms_removes_overlapping_boxes`)
- Symbolic modifier application (`test_apply_symbolic_modifiers_boosts_close_detections`)

## Adding New Tests

When adding tests for pipeline components:

### Testing Preprocessing (NMS)
- Test with empty detection lists
- Test with single detections
- Test with overlapping detections (high/low IoU)
- Test with multiple classes
- Test edge cases (identical boxes, nested boxes)

### Testing Symbolic Reasoning
- Test Prolog rule application
- Test confidence adjustment logic
- Test with various spatial configurations
- Mock Prolog queries to avoid dependencies

### Testing Evaluation
- Test mAP calculation with known ground truth
- Test with empty predictions
- Test with perfect predictions (mAP = 1.0)
- Test class-wise metrics

### Testing Training
- Mock YOLO model to avoid heavy operations
- Test configuration loading and validation
- Test path checking and directory creation
- Test hyperparameter application

### Testing Inference
- Mock SAHI predictions
- Test prediction file generation
- Test knowledge graph construction
- Test spatial relationship extraction

## Test Data

Use small, synthetic datasets for testing:
- Create minimal YOLO-format annotations
- Use tiny test images (e.g., 100x100 pixels)
- Keep test datasets in `tests/fixtures/`

## Related

- See [Pipeline README](../../pipeline/README.md) for pipeline architecture
- See main [Testing Instructions](../../.github/instructions/tests.instructions.md) for detailed testing guidelines
