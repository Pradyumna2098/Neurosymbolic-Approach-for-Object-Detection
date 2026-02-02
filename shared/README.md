# Shared Resources

This directory contains shared configurations and utilities used across all subprojects.

## Structure

```
shared/
├── configs/        # YAML configuration files
│   ├── training_*.yaml           # Training configurations
│   ├── pipeline_*.yaml           # Pipeline configurations
│   ├── prediction_*.yaml         # Prediction configurations
│   └── knowledge_graph_*.yaml    # Knowledge graph configurations
└── utils/          # Shared utility modules
    └── config_utils.py           # Configuration loading and validation
```

## Configuration Files

### Naming Convention
- `*_local.yaml`: Configurations for local development
- `*_kaggle.yaml`: Configurations for Kaggle notebooks/environments

### Usage

Import and use configuration utilities:

```python
from shared.utils.config_utils import load_config_file
from pathlib import Path

config = load_config_file(Path("shared/configs/training_local.yaml"))
```

### Configuration Validation

The `config_utils.py` module provides:
- Path expansion and validation
- Configuration merging with CLI overrides
- Error handling for missing/invalid configurations
- Path requirement checking

## Adding New Configurations

When adding new configuration files:
1. Create both `*_local.yaml` and `*_kaggle.yaml` versions
2. Document all configuration options
3. Provide sensible defaults
4. Include example values in comments
5. Validate paths and values before use

## Shared Utilities

### config_utils.py

Provides the following utilities:

- `load_config_file(path)`: Load YAML configuration from file
- `expand_path(path_str)`: Expand environment variables and user home in paths
- `ensure_paths(config, requirements)`: Validate that required paths exist
- `apply_overrides(config, overrides)`: Merge CLI arguments into configuration
- `ConfigError`: Exception for configuration-related errors
- `PathRequirement`: Enum for path validation requirements

## Environment-Specific Considerations

### Local Development
- Use absolute paths in local configs
- Point to your local dataset directories
- Adjust batch sizes and workers based on your hardware

### Kaggle Environment
- Use `/kaggle/input/` for read-only input data
- Use `/kaggle/working/` for outputs and temporary files
- Be aware of disk space limitations (20GB working directory)
- GPU is available but may be time-limited

## Related Documentation

See the main README for complete setup instructions and troubleshooting.
