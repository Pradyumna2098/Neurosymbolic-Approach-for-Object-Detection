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
3. Ensure the working directories referenced by the scripts exist. By default they use Kaggle notebook paths under `/kaggle/input/` and `/kaggle/working/`. When running locally, edit the constants at the top of each script to point to your dataset root and desired output folders.
4. Validate that ground-truth labels use YOLO normalised coordinates; the symbolic pipeline expects `.txt` predictions/labels in that format.

## Workflow at a glance
- **Neural stage**
  - Train a YOLOv11 OBB detector (`training.py`).
  - Optionally generate high-resolution sliced predictions with SAHI (`sahi_yolo_prediction.py`).
- **Symbolic stage**
  - Clean YOLO predictions with NMS, apply Prolog-based confidence modifiers, and evaluate mAP (`nsai_pipeline.py`).
- **Knowledge-graph stage**
  - Build weighted co-occurrence and spatial-relation graphs from predictions and emit Prolog facts/visualisations (`weighted_kg_sahi.py`).

Outputs are written into the locations defined by each script (for example `/kaggle/working/yolo/viz_results`, `/kaggle/working/predictions_refined`, and `/kaggle/working/knowledge_graph`). Adjust these paths when running outside Kaggle.

## Entry points

### `training.py` — neural training & inference
- Installs Ultralytics, trains a YOLOv11-OBB model using the dataset pointed to by `DATA_YAML`, and runs inference on `TEST_IMAGE_DIR`.
- Produces visualisations (`VISUALIZATION_DIR`), a JSON export of detections, and a zipped artifact for convenient download.
- **Customising paths**: edit `DATA_YAML`, `TEST_IMAGE_DIR`, `VISUALIZATION_DIR`, and `MODEL_WEIGHTS_DIR` at the top of the file to match your environment. All directories are created automatically if they are missing.
- **Running**:
  ```bash
  python training.py
  ```
  In Kaggle notebooks, run the cell directly; locally ensure CUDA/cuDNN are installed if you expect GPU acceleration.

### `nsai_pipeline.py` (`nsai pipeline.py`) — symbolic reasoning workflow
- Stage 1 performs class-wise NMS over YOLO prediction `.txt` files in `RAW_PREDICTIONS_DIR` and writes the cleaned outputs to `NMS_PREDICTIONS_DIR`.
- Stage 2 loads Prolog rules (`RULES_FILE`), applies confidence adjustments, and emits an explainability report at `REPORT_FILE` plus refined predictions in `REFINED_PREDICTIONS_DIR`.
- Stage 3 evaluates mAP for the raw, NMS-filtered, and refined detections using TorchMetrics.
- **Customising paths**: adjust the constants for the input/output folders (`RAW_PREDICTIONS_DIR`, `RULES_FILE`, etc.) so they point to your filesystem. Each stage creates its output folder if required.
- **Dependencies**: requires `swi-prolog` at runtime for `pyswip`. Install via apt on Linux or use the Kaggle image where it is available.
- **Running**:
  ```bash
  python "nsai pipeline.py"
  ```
  (On shells that dislike spaces in filenames, quote or escape the path.)

### `sahi_yolo_prediction.py` (`sahi yolo prediction.py`) — sliced inference helper
- Loads a trained YOLO checkpoint with SAHI to generate dense predictions over large images located in `TEST_IMAGES_DIR`.
- Saves YOLO-format `.txt` prediction files to `OUTPUT_PREDICTIONS_DIR`, suitable as input for the symbolic pipeline.
- **Customising paths**: set `MODEL_PATH`, `TEST_IMAGES_DIR`, and `OUTPUT_PREDICTIONS_DIR` to match where your weights, images, and target output folder live.
- **Running**:
  ```bash
  python "sahi yolo prediction.py"
  ```
  GPU usage is automatic when `torch.cuda.is_available()` reports a device.

### `weighted_kg_sahi.py` (`weighted kg +sahi.py`) — knowledge-graph construction
- Runs SAHI inference over the dataset splits declared in `DATA_SPLITS`, extracts spatial relations, and aggregates them into a weighted directed graph.
- Emits:
  - Prolog facts at `knowledge_graph/facts.pl` (relative to `WORK_DIR`).
  - Visualisations at `knowledge_graph/knowledge_graph_visuals.png`.
- **Customising paths**: update `MODEL_PATH`, `WORK_DIR`, `DATA_ROOT`, and the `DATA_SPLITS` dictionary so they reflect your dataset layout. Add or adjust relation filters (`ALLOWED_*` sets) to control which relations are recorded.
- **Running**:
  ```bash
  python "weighted kg +sahi.py"
  ```
  The script creates the `knowledge_graph/` folder if missing.

## Troubleshooting
- **Missing folders (e.g. `/kaggle/working/...`)**: create the directories manually or update the corresponding constants in each script before running. Every entry point calls `os.makedirs(..., exist_ok=True)` for its outputs, but the parent path must still be valid for your platform.
- **Kaggle-specific default paths**: when running locally, replace `/kaggle/input/...` and `/kaggle/working/...` references with your local dataset and scratch directories. The simplest approach is to edit the constants at the top of the script or set environment variables and read them via `os.getenv` if you prefer to avoid modifying code.
- **Prolog not found**: install SWI-Prolog (e.g. `sudo apt-get install swi-prolog`) before running `nsai_pipeline.py`.
- **GPU not detected**: verify that NVIDIA drivers and CUDA runtime compatible with your PyTorch version are installed. The scripts fall back to CPU, but performance will degrade significantly.
- **Package install failures**: upgrade `pip` and ensure build tools such as `build-essential`, `cmake`, and Python headers are present when compiling packages like `pyswip`.

## Outputs and artefact locations
- YOLO training runs: `runs/obb/<experiment_name>/` inside the working directory used by Ultralytics.
- Visualisations and JSON predictions: `VISUALIZATION_DIR` in `training.py`.
- Symbolic reports: `REFINED_PREDICTIONS_DIR` and `explainability_report1.csv` in `nsai_pipeline.py`.
- Knowledge graph artefacts: `knowledge_graph/` under `WORK_DIR`.

Adjust the directory constants if you wish to persist results outside the transient Kaggle filesystem.
