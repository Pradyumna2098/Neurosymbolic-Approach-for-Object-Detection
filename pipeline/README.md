# Pipeline Subproject

This subproject contains all the core AI/ML code for the neurosymbolic object detection pipeline.

## Structure

```
pipeline/
├── core/           # Core pipeline logic
│   ├── preprocess.py    # NMS filtering stage
│   ├── symbolic.py      # Prolog-based symbolic reasoning
│   ├── eval.py          # Model evaluation with TorchMetrics
│   ├── utils.py         # Shared utility functions
│   ├── config.py        # Configuration management
│   └── run_pipeline.py  # Orchestrator for all stages
├── training/       # Model training
│   └── training.py      # YOLOv11-OBB training script
├── inference/      # Inference and knowledge graph construction
│   ├── sahi_yolo_prediction.py   # SAHI-based sliced inference
│   └── weighted_kg_sahi.py       # Knowledge graph builder
├── prolog/         # Prolog rule files
│   ├── rules.pl                  # Symbolic reasoning rules
│   ├── dataset_categories.pl     # Dataset category definitions
│   └── prolog_facts.pl           # Generated Prolog facts
└── nsai_pipeline.py  # Legacy wrapper script

```

## Components

### Core Pipeline (`core/`)
The symbolic reasoning pipeline that processes YOLO detections:
1. **Preprocessing**: Applies class-wise NMS to raw predictions
2. **Symbolic Reasoning**: Uses Prolog rules to adjust confidence scores
3. **Evaluation**: Computes mAP metrics across different prediction sets

Run the full pipeline:
```bash
python -m pipeline.core.run_pipeline --config shared/configs/pipeline_local.yaml
```

Or run individual stages:
```bash
python -m pipeline.core.preprocess --config shared/configs/pipeline_local.yaml
python -m pipeline.core.symbolic --config shared/configs/pipeline_local.yaml
python -m pipeline.core.eval --config shared/configs/pipeline_local.yaml
```

### Training (`training/`)
Neural network training for YOLOv11-OBB models on DOTA-style datasets.

```bash
python pipeline/training/training.py --config shared/configs/training_local.yaml
```

### Inference (`inference/`)
- **SAHI Prediction**: Generates dense predictions on large images using sliced inference
- **Knowledge Graph**: Builds weighted graphs from spatial relationships between detected objects

```bash
python pipeline/inference/sahi_yolo_prediction.py --config shared/configs/prediction_local.yaml
python pipeline/inference/weighted_kg_sahi.py --config shared/configs/knowledge_graph_local.yaml
```

### Prolog Rules (`prolog/`)
Symbolic reasoning rules and facts for confidence adjustment based on:
- Object categories and relationships
- Spatial proximity
- Co-occurrence patterns

## Dependencies

See `requirements.txt` in the root directory for all dependencies.

Key dependencies:
- PyTorch & torchvision
- Ultralytics (YOLOv11)
- SAHI (Sliced Aided Hyper Inference)
- PySwip (Prolog integration)
- TorchMetrics (evaluation)

## Configuration

All configurations are stored in `shared/configs/` and support both local and Kaggle environments.

See the main README for detailed setup and troubleshooting instructions.
