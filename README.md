# Neurosymbolic Approach for Object Detection

![CI Pipeline](https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection/workflows/CI%20Pipeline/badge.svg)
[![codecov](https://codecov.io/gh/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection/branch/master/graph/badge.svg)](https://codecov.io/gh/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection)

This mono-repository contains an end-to-end pipeline that combines YOLO-based neural detectors with symbolic reasoning and knowledge-graph construction for explainable object detection and spatial relationship extraction.

## Repository Structure

This repository is organized as a mono-repository with three distinct subprojects and shared resources:

```
.
├── backend/              # APIs for pipeline interaction (planned)
├── frontend/             # Visual dashboards and interfaces (planned)
├── pipeline/             # Core AI/ML pipeline
│   ├── core/            # Preprocessing, symbolic reasoning, evaluation
│   ├── training/        # Model training scripts
│   ├── inference/       # SAHI prediction & knowledge graph construction
│   └── prolog/          # Symbolic reasoning rules
├── shared/              # Shared configurations and utilities
│   ├── configs/         # YAML configuration files
│   └── utils/           # Shared utility modules
├── tests/               # Test suite organized by subproject
│   ├── pipeline/        # Pipeline tests
│   ├── backend/         # Backend tests (planned)
│   └── frontend/        # Frontend tests (planned)
├── monitoring/          # Metrics and logging infrastructure
│   ├── metrics/         # Performance metrics
│   └── logs/            # Application logs
└── docs/                # Additional documentation

```

### Subproject Overview

| Subproject | Purpose | Status |
|------------|---------|--------|
| **Pipeline** | Core AI/ML code for object detection and symbolic reasoning | ✅ Active |
| **Backend** | REST APIs for pipeline interaction and job management | 📋 Planned |
| **Frontend** | Web dashboards for visualization and monitoring | 📋 Planned |
| **Shared** | Common configurations and utilities | ✅ Active |
| **Monitoring** | Metrics tracking and logging infrastructure | 📋 Planned |

For detailed information about each subproject, see their respective README files:
- [Pipeline README](pipeline/README.md)
- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)
- [Shared Resources README](shared/README.md)
- [Monitoring README](monitoring/README.md)

**📖 Documentation:**
- [Repository Structure Guide](docs/STRUCTURE.md) - Detailed overview of the mono-repo organization
- [Migration Guide](docs/MIGRATION.md) - Guide for transitioning from the old structure
- [CI/CD Quick Start](docs/CI_QUICKSTART.md) - ⚡ Quick guide to using the CI/CD pipeline
- [CI/CD Pipeline](docs/CICD.md) - Comprehensive CI/CD documentation
- [Branch Protection Setup](docs/BRANCH_PROTECTION.md) - Guide for enforcing CI checks before merging

## Quick Start

### Environment Setup
- **Python**: tested with Python 3.10+. PyTorch/Ultralytics currently publish wheels for 3.8–3.11, so stay within that range.
- **GPU**: a CUDA-capable NVIDIA GPU is strongly recommended for the training and SAHI slicing stages. The scripts fall back to CPU inference, but training without a GPU will be prohibitively slow.
- **Dependencies**: create a virtual environment and install the pinned packages.

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt
```

> **Note**: Kaggle notebooks have the required system packages pre-installed. For local Linux setups you may additionally need `sudo apt-get install swig swi-prolog` before installing `pyswip`.

## Dataset preparation
1. Prepare the DOTA-style dataset in YOLO format with matching `images/` and `labels/` folders for each split you plan to use (e.g. `train`, `val`, `test`).
2. Update the dataset YAML (for example, `dota.yaml`) so that it references the absolute paths for your machine.
3. Ensure the working directories referenced in your configuration files exist. Sample Kaggle and local YAML files live in `shared/configs/` – copy the closest one and tweak the paths for your environment.
4. Validate that ground-truth labels use YOLO normalised coordinates; the symbolic pipeline expects `.txt` predictions/labels in that format.

## Pipeline Workflow

The neurosymbolic pipeline consists of three main stages:

### 1. Neural Stage (Training & Inference)
- **Train YOLOv11-OBB**: Train object detection models on DOTA-style datasets
- **SAHI Inference**: Generate high-resolution sliced predictions for large images

### 2. Symbolic Reasoning Stage
- **NMS Preprocessing**: Apply class-wise Non-Maximum Suppression
- **Prolog Reasoning**: Adjust confidence scores using symbolic rules
- **Evaluation**: Compute mAP metrics across prediction sets

### 3. Knowledge Graph Stage
- **Relationship Extraction**: Build spatial relationship graphs
- **Prolog Facts**: Generate symbolic facts for downstream reasoning
- **Visualization**: Create graph visualizations

## Usage Examples

### Training a Model

```bash
python pipeline/training/training.py --config shared/configs/training_local.yaml
```

### Running the Full Symbolic Pipeline

```bash
# Run all stages sequentially
python -m pipeline.core.run_pipeline --config shared/configs/pipeline_local.yaml

# Or run individual stages
python -m pipeline.core.preprocess --config shared/configs/pipeline_local.yaml
python -m pipeline.core.symbolic --config shared/configs/pipeline_local.yaml
python -m pipeline.core.eval --config shared/configs/pipeline_local.yaml
```

### SAHI Prediction

```bash
python pipeline/inference/sahi_yolo_prediction.py --config shared/configs/prediction_local.yaml
```

### Knowledge Graph Construction

```bash
python pipeline/inference/weighted_kg_sahi.py --config shared/configs/knowledge_graph_local.yaml
```

## Configuration

All configurations are stored in `shared/configs/` with separate files for local and Kaggle environments:

- `training_*.yaml` - Model training configurations
- `pipeline_*.yaml` - Symbolic pipeline configurations
- `prediction_*.yaml` - SAHI inference configurations
- `knowledge_graph_*.yaml` - Knowledge graph construction configurations

### Configuration Example

```yaml
# shared/configs/pipeline_local.yaml
raw_predictions_dir: /path/to/predictions/raw
nms_predictions_dir: /path/to/predictions/nms
refined_predictions_dir: /path/to/predictions/refined
ground_truth_dir: /path/to/data/labels/val
rules_file: /path/to/pipeline/prolog/rules.pl
report_file: /path/to/reports/explainability_report.csv
nms_iou_threshold: 0.5
```

## Outputs and Artifacts

Outputs are written to locations defined in YAML configuration files:

- **Training outputs**: Model weights, loss curves, validation metrics
- **Predictions**: Raw, NMS-filtered, and symbolically-refined detections
- **Symbolic reports**: Confidence adjustments and explainability metrics
- **Knowledge graphs**: Prolog facts, graph visualizations, relationship statistics
- **Evaluation metrics**: mAP scores, precision-recall curves, confusion matrices

## Testing

Run tests for specific subprojects:

```bash
# Run pipeline tests
pytest tests/pipeline/ -v

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=pipeline --cov=shared
```

## Development

### Project Structure Philosophy

This mono-repository follows a modular architecture:

- **Separation of Concerns**: Each subproject has a clear, distinct purpose
- **Shared Resources**: Common utilities and configurations avoid duplication
- **Independent Development**: Subprojects can be developed and tested independently
- **Future-Ready**: Structure supports addition of backend APIs and frontend dashboards

### Adding New Features

1. Identify the appropriate subproject (pipeline, backend, frontend)
2. Add code following the existing structure and conventions
3. Update relevant configuration files in `shared/configs/`
4. Add tests in the corresponding `tests/` subdirectory
5. Update the subproject's README with new functionality
6. Add any new dependencies to `requirements.txt` or `requirements/common.txt`

## Legacy Compatibility

The `pipeline/nsai_pipeline.py` script is maintained for backwards compatibility. It's a thin wrapper around the new modular pipeline structure.

```bash
# Legacy usage (still supported)
python pipeline/nsai_pipeline.py --config shared/configs/pipeline_local.yaml
```

## Troubleshooting
- **Missing folders**: Create directories manually or update configuration values before running. Scripts create output folders, but parent directories must exist.
- **Kaggle-specific paths**: When running locally, replace `/kaggle/input/...` and `/kaggle/working/...` references with your local paths in `shared/configs/`.
- **Prolog not found**: Install SWI-Prolog (e.g., `sudo apt-get install swi-prolog`) before running symbolic reasoning stages.
- **GPU not detected**: Verify NVIDIA drivers and CUDA runtime compatible with your PyTorch version. Scripts fall back to CPU but with degraded performance.
- **Package install failures**: Upgrade `pip` and ensure build tools (`build-essential`, `cmake`, Python headers) are present when compiling packages like `pyswip`.
- **Import errors**: Ensure you're running from the repository root and have activated your virtual environment.

## Contributing

Contributions are welcome! Please:
1. Follow the existing code structure and conventions
2. Add tests for new functionality in the appropriate `tests/` subdirectory
3. Update relevant documentation (README files)
4. Use meaningful commit messages
5. Ensure all CI checks pass before requesting review

All pull requests to `master` must pass automated CI checks including:
- ✅ Unit tests (Python 3.10 & 3.11)
- ✅ Code quality checks (flake8)
- ✅ Build verification

See [CI/CD Documentation](docs/CICD.md) for details on the testing pipeline.

## License

See [LICENSE](LICENSE) file for details.

## Citation

If you use this code in your research, please cite:

```bibtex
@misc{neurosymbolic-object-detection,
  author = {Repository Authors},
  title = {Neurosymbolic Approach for Object Detection},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection}
}
```
