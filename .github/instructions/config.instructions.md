---
applyTo: "configs/**/*.yaml,*.yaml"
---

# Configuration Files Instructions

These instructions apply to YAML configuration files used throughout the project.

## Configuration Structure

The project uses YAML files in the `configs/` directory to configure different stages:

- `training_*.yaml` - Training configuration
- `pipeline_*.yaml` - Symbolic pipeline configuration  
- `prediction_*.yaml` - SAHI prediction configuration
- `knowledge_graph_*.yaml` - Knowledge graph construction configuration

## YAML Best Practices

### Formatting
- Use 2-space indentation (not tabs)
- Use lowercase with underscores for keys: `batch_size`, `learning_rate`
- Group related settings under nested keys
- Add comments to explain non-obvious settings

```yaml
# Good structure
training:
  epochs: 100  # Number of training epochs
  batch_size: 16
  learning_rate: 0.001

# Bad structure - flat and unclear
EPOCHS: 100
BatchSize: 16
lr: 0.001
```

### Environment-Specific Configs

Separate configurations for different environments:

```yaml
# configs/training_local.yaml - For local development
data:
  yaml_path: "/home/user/data/dota.yaml"
  train_dir: "/home/user/data/train"

# configs/training_kaggle.yaml - For Kaggle notebooks
data:
  yaml_path: "/kaggle/input/dota-dataset/dota.yaml"
  train_dir: "/kaggle/input/dota-dataset/train"
```

### Path Handling

**Always use absolute paths in configs**:
```yaml
# Good
data_yaml: "/kaggle/input/dota-dataset/dota.yaml"
output_dir: "/kaggle/working/results"

# Bad - relative paths break in different environments
data_yaml: "../data/dota.yaml"
output_dir: "./results"
```

### Required vs Optional Fields

Document which fields are required:

```yaml
# Required fields (must be present)
model:
  architecture: "yolov11"  # Required: Model architecture
  variant: "yolov11m-obb"  # Required: Model variant

# Optional fields (have defaults)
training:
  epochs: 100  # Optional: defaults to 100
  patience: 50  # Optional: early stopping patience
```

## Configuration Schema

### Training Configuration

```yaml
model:
  architecture: "yolov11"
  variant: "yolov11m-obb"  # Model size: n, s, m, l, x

data:
  yaml_path: "/path/to/dataset.yaml"  # YOLO dataset config
  train_dir: "/path/to/train/images"
  val_dir: "/path/to/val/images"
  test_dir: "/path/to/test/images"

training:
  epochs: 100
  batch_size: 16
  learning_rate: 0.001
  seed: 42  # For reproducibility
  device: "cuda"  # or "cpu"
  patience: 50  # Early stopping patience
  
  # Data augmentation
  augmentation:
    hsv_h: 0.015
    hsv_s: 0.7
    hsv_v: 0.4
    degrees: 0.0
    translate: 0.1
    scale: 0.5

output:
  project_dir: "/path/to/output"
  experiment_name: "yolo_training_001"
  visualization_dir: "/path/to/viz"
  save_predictions: true
```

### Pipeline Configuration

```yaml
paths:
  raw_predictions_dir: "/path/to/raw_predictions"
  ground_truth_labels_dir: "/path/to/labels"
  refined_predictions_dir: "/path/to/refined_predictions"
  rules_file: "rules.pl"
  dataset_categories_file: "dataset_categories.pl"

preprocessing:
  iou_threshold: 0.45  # NMS IoU threshold
  
evaluation:
  confidence_threshold: 0.25  # Minimum confidence for evaluation
  iou_thresholds: [0.5, 0.75]  # mAP IoU thresholds

output:
  report_file: "/path/to/report.json"
  visualizations: true
```

### Prediction Configuration

```yaml
model:
  model_path: "/path/to/best.pt"
  confidence_threshold: 0.25
  iou_threshold: 0.45

sahi:
  slice_width: 640
  slice_height: 640
  overlap_ratio: 0.2
  
data:
  test_images_dir: "/path/to/test/images"
  output_predictions_dir: "/path/to/predictions"

inference:
  device: "cuda"
  batch_size: 8
```

## Loading Configurations

### Standard Loading Pattern

```python
from config_utils import load_config_file
from pathlib import Path

def main(config_path: str):
    """Load and validate configuration."""
    # Load config
    config = load_config_file(Path(config_path))
    
    # Validate required fields
    required_keys = ['data', 'training', 'output']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config section: {key}")
    
    # Validate paths exist
    data_yaml = Path(config['data']['yaml_path'])
    if not data_yaml.exists():
        raise FileNotFoundError(f"Dataset config not found: {data_yaml}")
    
    return config
```

### Command-Line Override

Allow CLI arguments to override config values:

```python
import argparse
from config_utils import load_config_file
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--config', required=True, help='Config file path')
parser.add_argument('--epochs', type=int, help='Override training epochs')
parser.add_argument('--batch-size', type=int, help='Override batch size')

args = parser.parse_args()

# Load base config
config = load_config_file(Path(args.config))

# Apply CLI overrides
if args.epochs:
    config['training']['epochs'] = args.epochs
if args.batch_size:
    config['training']['batch_size'] = args.batch_size
```

## Validation

### Path Validation

```python
from pathlib import Path

def validate_config_paths(config: dict) -> None:
    """Validate all file paths in configuration exist."""
    path_keys = [
        ('data', 'yaml_path'),
        ('data', 'train_dir'),
        ('model', 'model_path'),  # if loading pretrained
    ]
    
    for *parent_keys, final_key in path_keys:
        # Navigate nested dict
        current = config
        for key in parent_keys:
            current = current.get(key, {})
        
        if final_key in current:
            path = Path(current[final_key])
            if not path.exists():
                raise FileNotFoundError(
                    f"Path not found: {'.'.join(parent_keys + [final_key])} = {path}"
                )
```

### Type Validation

```python
def validate_config_types(config: dict) -> None:
    """Validate configuration value types."""
    # Check numeric ranges
    if 'training' in config:
        training = config['training']
        
        if 'epochs' in training and training['epochs'] <= 0:
            raise ValueError("epochs must be positive")
        
        if 'batch_size' in training and training['batch_size'] <= 0:
            raise ValueError("batch_size must be positive")
        
        if 'learning_rate' in training:
            lr = training['learning_rate']
            if not (0 < lr < 1):
                raise ValueError("learning_rate must be between 0 and 1")
```

## Configuration Templates

### Creating New Configs

When adding new features, provide template configs:

```yaml
# configs/template_training.yaml
# Copy this file and modify for your environment

model:
  architecture: "yolov11"
  variant: "yolov11m-obb"  # Options: yolov11n, s, m, l, x

data:
  yaml_path: "/path/to/your/dataset.yaml"  # CHANGE THIS
  train_dir: "/path/to/train/images"       # CHANGE THIS
  val_dir: "/path/to/val/images"           # CHANGE THIS
  test_dir: "/path/to/test/images"         # CHANGE THIS

training:
  epochs: 100
  batch_size: 16  # Adjust based on GPU memory
  learning_rate: 0.001
  seed: 42
  device: "cuda"  # Change to "cpu" if no GPU

output:
  project_dir: "/path/to/output"           # CHANGE THIS
  experiment_name: "my_experiment"         # CHANGE THIS
```

## Environment Variables

For sensitive or environment-specific values, use environment variables:

```yaml
# Config file
database:
  host: "${DB_HOST}"
  port: ${DB_PORT}
  password: "${DB_PASSWORD}"

# In code, expand environment variables
import os
import yaml

with open(config_path) as f:
    config_str = f.read()
    # Expand environment variables
    config_str = os.path.expandvars(config_str)
    config = yaml.safe_load(config_str)
```

## Common Configuration Patterns

### Defaults with Overrides

```python
DEFAULT_CONFIG = {
    'training': {
        'epochs': 100,
        'batch_size': 16,
        'patience': 50,
    },
    'evaluation': {
        'confidence_threshold': 0.25,
        'iou_threshold': 0.45,
    }
}

def merge_configs(user_config: dict, defaults: dict) -> dict:
    """Merge user config with defaults."""
    result = defaults.copy()
    for key, value in user_config.items():
        if isinstance(value, dict) and key in result:
            result[key] = merge_configs(value, result[key])
        else:
            result[key] = value
    return result
```

### Multiple Dataset Support

```yaml
datasets:
  - name: "dota_train"
    yaml_path: "/path/to/dota.yaml"
    split: "train"
    
  - name: "dota_val"
    yaml_path: "/path/to/dota.yaml"
    split: "val"
    
  - name: "custom_test"
    yaml_path: "/path/to/custom.yaml"
    split: "test"
```

## Debugging Configuration Issues

### Log Loaded Config

```python
from config_utils import load_config_file
from pathlib import Path
import json

def load_and_log_config(config_path: str) -> dict:
    """Load config and log its contents."""
    config = load_config_file(Path(config_path))
    
    # Log config for debugging
    print(f"Loaded config from: {config_path}")
    print(json.dumps(config, indent=2, default=str))
    
    return config
```

### Validate Before Use

```python
def safe_get_config_value(config: dict, *keys, default=None):
    """Safely get nested config value with default."""
    current = config
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current

# Usage
epochs = safe_get_config_value(config, 'training', 'epochs', default=100)
```

## Documentation

Add a `CONFIG.md` file documenting all configuration options:

```markdown
# Configuration Options

## Training Configuration

### model.architecture
- Type: string
- Required: Yes
- Options: "yolov11"
- Description: Base model architecture

### training.epochs
- Type: integer
- Required: No
- Default: 100
- Description: Number of training epochs
```

## Version Control

- **Commit templates**: Commit `configs/template_*.yaml` files
- **Ignore local configs**: Add to `.gitignore`:
  ```
  configs/*_local.yaml
  configs/my_*.yaml
  ```
- **Document changes**: Update config documentation when adding new options

## Testing with Configs

```python
import pytest
from pathlib import Path

@pytest.fixture
def test_config(tmp_path):
    """Create a minimal test configuration."""
    config = {
        'training': {
            'epochs': 1,
            'batch_size': 1,
        },
        'data': {
            'yaml_path': str(tmp_path / 'test.yaml'),
        },
        'output': {
            'project_dir': str(tmp_path / 'output'),
        }
    }
    
    # Create necessary files
    (tmp_path / 'test.yaml').write_text('names: ["class1"]')
    (tmp_path / 'output').mkdir()
    
    return config

def test_with_config(test_config):
    """Test function using test configuration."""
    assert test_config['training']['epochs'] == 1
```
