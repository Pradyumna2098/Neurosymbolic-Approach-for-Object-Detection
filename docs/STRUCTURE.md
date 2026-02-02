# Repository Structure Guide

This document provides a comprehensive overview of the mono-repository structure.

## Directory Tree

```
Neurosymbolic-Approach-for-Object-Detection/
│
├── backend/                          # Backend APIs (planned)
│   ├── __init__.py
│   └── README.md
│
├── frontend/                         # Frontend dashboards (planned)
│   ├── __init__.py
│   └── README.md
│
├── pipeline/                         # Core AI/ML Pipeline
│   ├── __init__.py
│   ├── README.md
│   ├── nsai_pipeline.py             # Legacy wrapper script
│   │
│   ├── core/                        # Core pipeline logic
│   │   ├── __init__.py
│   │   ├── config.py                # Configuration management
│   │   ├── eval.py                  # Evaluation stage
│   │   ├── preprocess.py            # NMS preprocessing stage
│   │   ├── run_pipeline.py          # Pipeline orchestrator
│   │   ├── symbolic.py              # Symbolic reasoning stage
│   │   └── utils.py                 # Shared utilities
│   │
│   ├── training/                    # Model training
│   │   ├── __init__.py
│   │   └── training.py              # YOLOv11 training script
│   │
│   ├── inference/                   # Inference & knowledge graphs
│   │   ├── __init__.py
│   │   ├── sahi_yolo_prediction.py  # SAHI-based inference
│   │   └── weighted_kg_sahi.py      # Knowledge graph builder
│   │
│   └── prolog/                      # Symbolic reasoning rules
│       ├── dataset_categories.pl    # Category definitions
│       ├── prolog_facts.pl          # Generated facts
│       └── rules.pl                 # Confidence adjustment rules
│
├── shared/                          # Shared resources
│   ├── __init__.py
│   ├── README.md
│   │
│   ├── configs/                     # Configuration files
│   │   ├── knowledge_graph_kaggle.yaml
│   │   ├── knowledge_graph_local.yaml
│   │   ├── pipeline_kaggle.yaml
│   │   ├── pipeline_local.yaml
│   │   ├── prediction_kaggle.yaml
│   │   ├── prediction_local.yaml
│   │   ├── training_kaggle.yaml
│   │   └── training_local.yaml
│   │
│   └── utils/                       # Shared utilities
│       ├── __init__.py
│       └── config_utils.py          # Configuration loading
│
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── README.md
│   │
│   ├── pipeline/                    # Pipeline tests
│   │   ├── __init__.py
│   │   ├── README.md
│   │   └── test_utils.py
│   │
│   ├── backend/                     # Backend tests (planned)
│   │   ├── .gitkeep
│   │   └── README.md
│   │
│   └── frontend/                    # Frontend tests (planned)
│       ├── .gitkeep
│       └── README.md
│
├── monitoring/                      # Monitoring infrastructure
│   ├── __init__.py
│   ├── README.md
│   │
│   ├── metrics/                     # Performance metrics
│   │   ├── .gitkeep
│   │   └── README.md
│   │
│   └── logs/                        # Application logs
│       ├── .gitkeep
│       └── README.md
│
├── docs/                            # Documentation
│   └── dependency_overview.md
│
├── requirements/                    # Dependency specifications
│   └── common.txt
│
├── .github/                         # GitHub configuration
│   ├── instructions/                # Copilot instructions
│   └── workflows/                   # CI/CD workflows
│
├── .gitignore                       # Git ignore rules
├── .gitattributes                   # Git attributes
├── LICENSE                          # License file
├── README.md                        # Main documentation
├── requirements.txt                 # Python dependencies
└── requirements-kaggle.txt          # Kaggle-specific deps
```

## Module Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  ┌──────────────┐                        ┌──────────────┐   │
│  │   Frontend   │ ← (planned) ────────→ │   Backend    │   │
│  │  Dashboards  │                        │     APIs     │   │
│  └──────────────┘                        └──────┬───────┘   │
└─────────────────────────────────────────────────┼───────────┘
                                                  │
                                                  ↓
┌─────────────────────────────────────────────────┼───────────┐
│                    Core Pipeline Layer          │           │
│  ┌──────────────────────────────────────────────▼────────┐  │
│  │              Pipeline (AI/ML Core)                    │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │  │
│  │  │  Training  │→│   Core     │→│ Inference  │     │  │
│  │  │            │  │ Pipeline   │  │    & KG    │     │  │
│  │  └────────────┘  └────────────┘  └────────────┘     │  │
│  │                        ↓                              │  │
│  │                  ┌────────────┐                       │  │
│  │                  │   Prolog   │                       │  │
│  │                  │   Rules    │                       │  │
│  │                  └────────────┘                       │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                              ↕
┌──────────────────────────────────────────────────────────────┐
│                     Support Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │    Shared    │  │    Tests     │  │  Monitoring  │       │
│  │  Configs &   │  │   (pytest)   │  │  Metrics &   │       │
│  │   Utils      │  │              │  │    Logs      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────────────────────────────────────────┘
```

## Data Flow

### Training Pipeline
```
Dataset → Training Script → YOLO Model → Checkpoints
   ↓
Configs
```

### Inference Pipeline
```
Images → SAHI Prediction → Raw Detections → NMS Preprocessing
            ↓                                      ↓
         Model                            Filtered Detections
                                                  ↓
                                          Symbolic Reasoning
                                                  ↓
                                          Refined Detections
                                                  ↓
                                            Evaluation
```

### Knowledge Graph Pipeline
```
Images → SAHI Inference → Detections → Spatial Relations
                                            ↓
                                      Knowledge Graph
                                            ↓
                                      Prolog Facts
```

## Import Patterns

### From Pipeline to Shared
```python
from shared.utils.config_utils import load_config_file
```

### Within Pipeline Submodules
```python
from pipeline.core.utils import pre_filter_with_nms
from pipeline.core.config import load_pipeline_config
```

### In Tests
```python
from pipeline.core.utils import apply_symbolic_modifiers
```

## Configuration Flow

```
shared/configs/*.yaml → config_utils.py → Pipeline Modules
                                              ↓
                                         Execution
```

## Subproject Responsibilities

| Subproject | Responsibility | Status |
|-----------|---------------|--------|
| **pipeline/** | Core AI/ML logic, training, inference, symbolic reasoning | ✅ Active |
| **shared/** | Common configurations and utilities | ✅ Active |
| **backend/** | REST APIs, job management, model serving | 📋 Planned |
| **frontend/** | Web dashboards, visualization interfaces | 📋 Planned |
| **monitoring/** | Metrics collection, logging infrastructure | 📋 Planned |
| **tests/** | Comprehensive test suite | ✅ Partial |

## Entry Points

### Command Line
```bash
# Training
python pipeline/training/training.py --config shared/configs/training_local.yaml

# Full Pipeline
python -m pipeline.core.run_pipeline --config shared/configs/pipeline_local.yaml

# Individual Stages
python -m pipeline.core.preprocess --config shared/configs/pipeline_local.yaml
python -m pipeline.core.symbolic --config shared/configs/pipeline_local.yaml
python -m pipeline.core.eval --config shared/configs/pipeline_local.yaml

# SAHI Inference
python pipeline/inference/sahi_yolo_prediction.py --config shared/configs/prediction_local.yaml

# Knowledge Graph
python pipeline/inference/weighted_kg_sahi.py --config shared/configs/knowledge_graph_local.yaml

# Legacy
python pipeline/nsai_pipeline.py --config shared/configs/pipeline_local.yaml
```

### Python API (Future)
```python
# Backend API (planned)
POST /api/v1/train
POST /api/v1/predict
GET  /api/v1/metrics
```

## Migration from Old Structure

| Old Location | New Location |
|-------------|-------------|
| `training.py` | `pipeline/training/training.py` |
| `config_utils.py` | `shared/utils/config_utils.py` |
| `pipeline/*.py` | `pipeline/core/*.py` |
| `src/*.py` | `pipeline/inference/*.py` |
| `configs/*.yaml` | `shared/configs/*.yaml` |
| `*.pl` | `pipeline/prolog/*.pl` |
| `tests/*.py` | `tests/pipeline/*.py` |
| `nsai pipeline.py` | `pipeline/nsai_pipeline.py` |

## Key Design Principles

1. **Separation of Concerns**: Each subproject has a single, well-defined purpose
2. **Modularity**: Components can be developed and tested independently
3. **Shared Resources**: Common code and configs avoid duplication
4. **Scalability**: Structure supports future additions (backend, frontend)
5. **Maintainability**: Clear organization makes code easier to navigate
6. **Testing**: Tests organized by subproject for clarity

## Navigation Tips

- Start at `README.md` for overview
- Read subproject READMEs for detailed information
- Check `shared/configs/` for configuration examples
- Look in `tests/` for usage examples
- See `docs/` for additional documentation

## Related Documentation

- [Main README](../README.md)
- [Pipeline README](../pipeline/README.md)
- [Shared Resources README](../shared/README.md)
- [Tests README](../tests/README.md)
- [Monitoring README](../monitoring/README.md)
