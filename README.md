# Neurosymbolic Approach for Object Detection

This repository contains the end-to-end pipeline that combines YOLO-based neural detectors with symbolic reasoning and a knowledge-graph (KG) layer for explainability and downstream analytics.  The workflow is organised around four entry points that can be executed independently or chained together depending on the experiment you want to run.

## Environment setup
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
3. Ensure the working directories referenced in your configuration files exist. Sample Kaggle and local YAML files live in `configs/` – copy the closest one and tweak the paths for your environment.
4. Validate that ground-truth labels use YOLO normalised coordinates; the symbolic pipeline expects `.txt` predictions/labels in that format.

## Workflow at a glance
- **Neural stage**
  - Train a YOLOv11 OBB detector (`training.py`).
  - Optionally generate high-resolution sliced predictions with SAHI (`sahi_yolo_prediction.py`).
- **Symbolic stage**
  - Clean YOLO predictions with NMS, apply Prolog-based confidence modifiers, and evaluate mAP (`nsai_pipeline.py`).
- **Knowledge-graph stage**
  - Build weighted co-occurrence and spatial-relation graphs from predictions and emit Prolog facts/visualisations (`weighted_kg_sahi.py`).

Outputs are written into the locations defined in the YAML configuration files (for example `/kaggle/working/yolo/viz_results`, `/kaggle/working/predictions_refined`, and `/kaggle/working/knowledge_graph`). Adjust these paths when running outside Kaggle.

## Entry points

### `training.py` — neural training & inference
- Trains a YOLOv11-OBB model and runs inference over a held-out image set, saving annotated renders plus a JSON dump of detections.
- **Customising paths**: provide a YAML file (see `configs/training_*.yaml`) via `--config` or override specific values with CLI flags like `--data-yaml`, `--test-image-dir`, and `--zip-source-dir`.
- **Running**:
  ```bash
  python training.py --config configs/training_kaggle.yaml
  # or override one-off values
  python training.py --config configs/training_local.yaml --epochs 100 --conf-threshold 0.2
  ```
  The script validates that input paths exist and creates missing output folders. GPU acceleration is used automatically when `torch.cuda.is_available()` returns `True`.

### `nsai_pipeline.py` (`nsai pipeline.py`) — symbolic reasoning workflow
- Stage 1 performs class-wise NMS over YOLO prediction `.txt` files, Stage 2 applies Prolog-defined confidence modifiers, and Stage 3 reports TorchMetrics mAP for each variant of the predictions.
- **Customising paths**: point the script at a YAML file such as `configs/pipeline_kaggle.yaml`, or override flags like `--raw-predictions-dir` and `--rules-file`. Output directories are created automatically.
- **Dependencies**: requires `swi-prolog` at runtime for `pyswip`. Install via apt on Linux or use the Kaggle image where it is available.
- **Running**:
  ```bash
  python "nsai pipeline.py" --config configs/pipeline_local.yaml
  ```
  (On shells that dislike spaces in filenames, quote or escape the path.)

### `sahi_yolo_prediction.py` (`sahi yolo prediction.py`) — sliced inference helper
- Loads a trained YOLO checkpoint with SAHI to generate dense predictions over large images, emitting YOLO-format `.txt` files ready for the symbolic pipeline.
- **Customising paths**: use a YAML config (see `configs/prediction_*.yaml`) or pass flags like `--model-path`, `--test-images-dir`, and `--output-predictions-dir`.
- **Running**:
  ```bash
  python "sahi yolo prediction.py" --config configs/prediction_kaggle.yaml
  ```
  GPU usage is automatic when `torch.cuda.is_available()` reports a device.

### `weighted_kg_sahi.py` (`weighted kg +sahi.py`) — knowledge-graph construction
- Runs SAHI inference over configured dataset splits, extracts spatial relations, and aggregates them into a weighted directed graph.
- Emits:
  - Prolog facts at the configured `facts_filename` within `knowledge_graph_dir`.
  - Visualisations at the configured `graph_filename`.
- **Customising paths**: select a config file like `configs/knowledge_graph_kaggle.yaml` or override the CLI flags (`--model-path`, `--knowledge-graph-dir`, `--data-split train=/path/to/images/train`, etc.). Relation filter sets (`ALLOWED_*`) remain editable in the script if you need domain-specific tweaks.
- **Running**:
  ```bash
  python "weighted kg +sahi.py" --config configs/knowledge_graph_local.yaml
  ```

## Troubleshooting
- **Missing folders (e.g. `/kaggle/working/...`)**: create the directories manually or update the relevant configuration values before running. Every entry point creates its output folders, but parent directories must already exist.
- **Kaggle-specific default paths**: when running locally, replace `/kaggle/input/...` and `/kaggle/working/...` references inside the config files with your local dataset and scratch directories.
- **Prolog not found**: install SWI-Prolog (e.g. `sudo apt-get install swi-prolog`) before running `nsai_pipeline.py`.
- **GPU not detected**: verify that NVIDIA drivers and CUDA runtime compatible with your PyTorch version are installed. The scripts fall back to CPU, but performance will degrade significantly.
- **Package install failures**: upgrade `pip` and ensure build tools such as `build-essential`, `cmake`, and Python headers are present when compiling packages like `pyswip`.

## Outputs and artefact locations
- YOLO training runs: `runs/obb/<experiment_name>/` inside the working directory used by Ultralytics.
- Visualisations and JSON predictions: `visualization_dir` defined in your training config.
- Symbolic reports: `refined_predictions_dir` and the configured `report_file` in the pipeline config.
- Knowledge graph artefacts: the configured `knowledge_graph_dir`.

Adjust the directory constants if you wish to persist results outside the transient Kaggle filesystem.
