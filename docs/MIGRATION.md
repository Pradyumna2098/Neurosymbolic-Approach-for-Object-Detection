# Migration Guide: Transitioning to Mono-Repository Structure

This guide helps users migrate from the old repository structure to the new mono-repository organization.

## What Changed?

The repository has been restructured into a mono-repository with three distinct subprojects:
- **Backend**: For APIs to interact with the pipeline (planned)
- **Frontend**: For visual dashboards and interfaces (planned)
- **Pipeline**: For all core AI/ML code

## File Location Changes

### Core Files

| Old Path | New Path | Notes |
|----------|----------|-------|
| `training.py` | `pipeline/training/training.py` | Training script moved |
| `config_utils.py` | `shared/utils/config_utils.py` | Now in shared utilities |
| `nsai pipeline.py` | `pipeline/nsai_pipeline.py` | Legacy wrapper maintained |

### Pipeline Modules

| Old Path | New Path |
|----------|----------|
| `pipeline/__init__.py` | `pipeline/core/__init__.py` |
| `pipeline/config.py` | `pipeline/core/config.py` |
| `pipeline/eval.py` | `pipeline/core/eval.py` |
| `pipeline/preprocess.py` | `pipeline/core/preprocess.py` |
| `pipeline/run_pipeline.py` | `pipeline/core/run_pipeline.py` |
| `pipeline/symbolic.py` | `pipeline/core/symbolic.py` |
| `pipeline/utils.py` | `pipeline/core/utils.py` |

### Inference & Knowledge Graph

| Old Path | New Path |
|----------|----------|
| `src/sahi_yolo_prediction.py` | `pipeline/inference/sahi_yolo_prediction.py` |
| `src/weighted_kg_sahi.py` | `pipeline/inference/weighted_kg_sahi.py` |

### Configurations

| Old Path | New Path |
|----------|----------|
| `configs/*.yaml` | `shared/configs/*.yaml` |

### Prolog Files

| Old Path | New Path |
|----------|----------|
| `dataset_categories.pl` | `pipeline/prolog/dataset_categories.pl` |
| `prolog_facts.pl` | `pipeline/prolog/prolog_facts.pl` |
| `rules.pl` | `pipeline/prolog/rules.pl` |

### Tests

| Old Path | New Path |
|----------|----------|
| `tests/test_utils.py` | `tests/pipeline/test_utils.py` |

## Command Changes

### Training

**Old:**
```bash
python training.py --config configs/training_local.yaml
```

**New:**
```bash
python pipeline/training/training.py --config shared/configs/training_local.yaml
```

### Pipeline Execution

**Old:**
```bash
python -m pipeline.run_pipeline --config configs/pipeline_local.yaml
python -m pipeline.preprocess --config configs/pipeline_local.yaml
python -m pipeline.symbolic --config configs/pipeline_local.yaml
python -m pipeline.eval --config configs/pipeline_local.yaml
```

**New:**
```bash
python -m pipeline.core.run_pipeline --config shared/configs/pipeline_local.yaml
python -m pipeline.core.preprocess --config shared/configs/pipeline_local.yaml
python -m pipeline.core.symbolic --config shared/configs/pipeline_local.yaml
python -m pipeline.core.eval --config shared/configs/pipeline_local.yaml
```

### SAHI Prediction

**Old:**
```bash
python "sahi yolo prediction.py" --config configs/prediction_local.yaml
```

**New:**
```bash
python pipeline/inference/sahi_yolo_prediction.py --config shared/configs/prediction_local.yaml
```

### Knowledge Graph Construction

**Old:**
```bash
python "weighted kg +sahi.py" --config configs/knowledge_graph_local.yaml
```

**New:**
```bash
python pipeline/inference/weighted_kg_sahi.py --config shared/configs/knowledge_graph_local.yaml
```

### Legacy Compatibility

The legacy `nsai_pipeline.py` wrapper is still available:

```bash
# Still works (maintained for backwards compatibility)
python pipeline/nsai_pipeline.py --config shared/configs/pipeline_local.yaml
```

## Import Statement Changes

### In Your Code

**Old:**
```python
from config_utils import load_config_file
from pipeline.utils import pre_filter_with_nms
from pipeline.config import load_pipeline_config
```

**New:**
```python
from shared.utils.config_utils import load_config_file
from pipeline.core.utils import pre_filter_with_nms
from pipeline.core.config import load_pipeline_config
```

### In Tests

**Old:**
```python
from pipeline.utils import apply_symbolic_modifiers
```

**New:**
```python
from pipeline.core.utils import apply_symbolic_modifiers
```

## Configuration File Changes

### Path References

Update paths in your local configuration files:

**Old (`configs/pipeline_local.yaml`):**
```yaml
rules_file: /path/to/project/prolog/rules.pl
```

**New (`shared/configs/pipeline_local.yaml`):**
```yaml
rules_file: /path/to/project/pipeline/prolog/rules.pl
```

### Default Config Paths

If you were using default config paths in your code:

**Old:**
```python
DEFAULT_CONFIG_PATH = Path("configs/training_kaggle.yaml")
```

**New:**
```python
DEFAULT_CONFIG_PATH = Path("shared/configs/training_kaggle.yaml")
```

## Git Operations

### Pulling Latest Changes

```bash
git pull origin main
```

### Updating Local Branches

If you have local branches based on the old structure:

```bash
# Merge or rebase with the new structure
git checkout your-branch
git merge main  # or git rebase main
```

You may need to resolve conflicts in import statements and file paths.

## Scripts and Automation

If you have scripts that call the training or pipeline:

**Old script:**
```bash
#!/bin/bash
python training.py --config configs/training_local.yaml
python -m pipeline.run_pipeline --config configs/pipeline_local.yaml
```

**New script:**
```bash
#!/bin/bash
python pipeline/training/training.py --config shared/configs/training_local.yaml
python -m pipeline.core.run_pipeline --config shared/configs/pipeline_local.yaml
```

## Jupyter Notebooks

Update any notebook imports:

**Old:**
```python
import sys
sys.path.append('.')

from config_utils import load_config_file
from pipeline.utils import pre_filter_with_nms
```

**New:**
```python
import sys
sys.path.append('.')

from shared.utils.config_utils import load_config_file
from pipeline.core.utils import pre_filter_with_nms
```

## CI/CD Pipelines

Update your CI/CD configuration:

**Old (`.github/workflows/test.yml`):**
```yaml
- name: Run tests
  run: pytest tests/test_utils.py
```

**New:**
```yaml
- name: Run tests
  run: pytest tests/pipeline/test_utils.py
```

## Docker / Container Images

Update Dockerfiles if applicable:

**Old:**
```dockerfile
COPY training.py /app/
COPY pipeline/ /app/pipeline/
COPY configs/ /app/configs/
```

**New:**
```dockerfile
COPY pipeline/ /app/pipeline/
COPY shared/ /app/shared/
COPY tests/ /app/tests/
COPY monitoring/ /app/monitoring/
```

## Virtual Environments

No changes needed for virtual environments. The dependencies remain the same:

```bash
# Still works the same
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Testing Your Migration

After updating your code, verify everything works:

```bash
# 1. Syntax check
python -m py_compile pipeline/training/training.py
python -m py_compile pipeline/core/*.py

# 2. Import test
python -c "from shared.utils.config_utils import load_config_file; print('OK')"
python -c "from pipeline.core.utils import pre_filter_with_nms; print('OK')"

# 3. Run tests
pytest tests/pipeline/ -v

# 4. Test a simple command
python pipeline/training/training.py --help
python -m pipeline.core.preprocess --help
```

## Common Issues

### Import Errors

**Problem:**
```
ModuleNotFoundError: No module named 'config_utils'
```

**Solution:**
Update imports:
```python
from shared.utils.config_utils import load_config_file
```

### Config File Not Found

**Problem:**
```
FileNotFoundError: configs/training_local.yaml
```

**Solution:**
Update config path:
```bash
python pipeline/training/training.py --config shared/configs/training_local.yaml
```

### Module Import Path Issues

**Problem:**
```
ModuleNotFoundError: No module named 'pipeline.utils'
```

**Solution:**
Update to new module path:
```python
from pipeline.core.utils import function_name
```

## Benefits of New Structure

✅ **Clear Separation**: Backend, frontend, and pipeline are distinct
✅ **Scalability**: Easy to add new subprojects
✅ **Better Testing**: Tests organized by subproject
✅ **Shared Resources**: Common configs and utils in one place
✅ **Future-Ready**: Structure supports API and dashboard additions
✅ **Monitoring**: Dedicated infrastructure for metrics and logs

## Getting Help

If you encounter issues during migration:

1. Check this guide for your specific case
2. Review [STRUCTURE.md](STRUCTURE.md) for overall organization
3. Check subproject READMEs for detailed information
4. Open an issue on GitHub with details about the problem

## Rollback (Emergency)

If you need to temporarily rollback to the old structure:

```bash
git checkout <commit-before-restructure>
```

However, we recommend adapting to the new structure for long-term benefits.

## Timeline

- **Current**: New structure in place, legacy commands still work
- **Next Release**: Full documentation and examples updated
- **Future**: Legacy wrapper may be deprecated (with advance notice)

## Questions?

See the [README.md](../README.md) or open an issue for assistance.
