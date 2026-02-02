---
applyTo: "pipeline/**/*.py,src/**/*.py,training.py,nsai pipeline.py,config_utils.py"
---

# Machine Learning Pipeline Instructions

These instructions apply to the ML pipeline components, training scripts, and inference code.

## Overview

This section covers the neurosymbolic object detection pipeline that combines YOLO-based neural detectors with symbolic reasoning using Prolog.

## Code Organization

- `training.py` - Main training script for YOLOv11-OBB models
- `pipeline/` - Symbolic reasoning pipeline stages (preprocess, symbolic, eval)
- `src/` - SAHI-based prediction and knowledge graph construction
- `config_utils.py` - Configuration loading utilities

## Key Patterns

### Model Loading and Inference
```python
from ultralytics import YOLO

# Always use device parameter for GPU/CPU control
model = YOLO(model_path)
results = model.predict(
    source=image_path,
    conf=confidence_threshold,
    iou=iou_threshold,
    device='cuda' if torch.cuda.is_available() else 'cpu'
)
```

### YOLO Format Conventions
- Ground truth labels use YOLO normalized coordinates: `[class_id, cx, cy, width, height]`
- Predictions use YOLO normalized coordinates with confidence: `[class_id, cx, cy, width, height, confidence]`
- Center coordinates (cx, cy) and dimensions (width, height) are normalized to [0, 1]
- Convert to VOC format for NMS: `[x_min, y_min, x_max, y_max]`

### Configuration Loading
```python
from config_utils import load_config_file
from pathlib import Path

# Always load from YAML, never hardcode paths
config = load_config_file(Path(config_path))
```

## Reproducibility Requirements

### Random Seeds
Always set random seeds for reproducible experiments:
```python
import random
import numpy as np
import torch

def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
```

### Configuration Files
- Store all hyperparameters in YAML configs under `configs/`
- Never hardcode dataset paths, model paths, or hyperparameters
- Use `configs/training_local.yaml` for local development
- Use `configs/training_kaggle.yaml` for Kaggle environments

## Data Processing Guidelines

### Dataset Validation
Before training or inference:
- Verify image files exist in expected locations
- Check label files match images (same basename, different extension)
- Validate YOLO format: 6 values per line (class_id, cx, cy, w, h, conf for predictions)
- Ensure class IDs are within valid range

### NMS Processing
- Use class-wise NMS to avoid suppressing different object classes
- Default IoU threshold: 0.45 for general use
- Higher threshold (0.6+) for crowded scenes
- Always use torchvision.ops.nms for consistency

```python
from pipeline.utils import pre_filter_with_nms

# Group by class and apply NMS
filtered = pre_filter_with_nms(detections, iou_threshold=0.45)
```

## Symbolic Reasoning Integration

### Prolog Facts
- Category definitions: `dataset_categories.pl`
- Confidence modifiers: `rules.pl`
- Generated facts: output from knowledge graph builder

### PySwip Usage
```python
from pyswip import Prolog

prolog = Prolog()
prolog.consult(rules_file)

# Query with proper escaping
results = list(prolog.query(f"adjust_confidence({class_id}, {conf}, Adjusted)"))
```

## Performance Considerations

### GPU Usage
- Always check `torch.cuda.is_available()` before using GPU
- Set `device` parameter explicitly in all YOLO operations
- For SAHI, GPU is strongly recommended for large images

### Memory Management
- Process images in batches when using SAHI
- Clear CUDA cache if memory errors occur: `torch.cuda.empty_cache()`
- Use smaller slice dimensions for SAHI if memory is limited

## Error Handling

### Path Validation
```python
from pathlib import Path

def validate_paths(config):
    """Validate all paths exist before processing."""
    required_paths = [config['data_yaml'], config['model_path']]
    for path in required_paths:
        if not Path(path).exists():
            raise FileNotFoundError(f"Required path not found: {path}")
```

### Graceful Fallbacks
- If GPU unavailable, fall back to CPU with warning
- If Prolog not installed, skip symbolic reasoning stage
- If output directory missing, create it automatically

## Testing ML Code

- Use small synthetic datasets for unit tests
- Mock heavy operations (model loading, training)
- Test with deterministic seeds
- Verify output formats and dimensions

Example:
```python
@pytest.fixture
def mock_yolo_results():
    """Mock YOLO prediction results for testing."""
    return [{
        'boxes': torch.tensor([[10, 20, 30, 40]]),
        'scores': torch.tensor([0.95]),
        'labels': torch.tensor([0])
    }]
```

## Common Pitfalls

1. **Forgetting to set seeds** - Results become non-reproducible
2. **Hardcoding paths** - Breaks on different environments
3. **Not checking device availability** - Code crashes without GPU
4. **Incorrect coordinate formats** - YOLO uses normalized, VOC uses pixels
5. **Missing parent directories** - Scripts fail if output dirs don't exist
6. **Not applying class-wise NMS** - Different classes suppress each other

## Pipeline Stage Dependencies

1. **Training** (`training.py`) → Generates model weights
2. **Prediction** (`sahi_yolo_prediction.py`) → Generates YOLO .txt predictions
3. **Preprocess** (`pipeline.preprocess`) → Applies NMS to predictions
4. **Symbolic** (`pipeline.symbolic`) → Applies Prolog confidence modifiers
5. **Evaluation** (`pipeline.eval`) → Computes mAP metrics
6. **Knowledge Graph** (`weighted_kg_sahi.py`) → Extracts spatial relations

Each stage outputs to a configured directory that the next stage reads from.
