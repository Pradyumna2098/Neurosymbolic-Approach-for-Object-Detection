# Model Pipeline Integration for Automated Object Detection

**Document Version:** 1.0  
**Last Updated:** February 3, 2026  
**Status:** Design Specification (No Code Implementation)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Pipeline Architecture Overview](#pipeline-architecture-overview)
3. [Component Structure](#component-structure)
4. [Backend API Integration](#backend-api-integration)
5. [End-to-End Integration Flow](#end-to-end-integration-flow)
6. [File Outputs and Formats](#file-outputs-and-formats)
7. [Prometheus Metrics Integration](#prometheus-metrics-integration)
8. [Pseudocode Examples](#pseudocode-examples)
9. [Error Handling and Recovery](#error-handling-and-recovery)
10. [Future Extensibility](#future-extensibility)

---

## Executive Summary

This document describes the integration of the existing YOLO/SAHI object detection pipeline into an automated workflow suitable for backend/API invocation. The neurosymbolic pipeline combines neural object detection with symbolic reasoning to provide explainable, high-confidence predictions.

### Key Capabilities

- **SAHI (Slicing Aided Hyper Inference)**: High-resolution image processing through intelligent slicing
- **YOLOv11-OBB**: Oriented bounding box detection for complex aerial/satellite imagery
- **Symbolic Reasoning**: Prolog-based confidence adjustment and relationship extraction
- **Knowledge Graph Construction**: Spatial relationship modeling between detected objects
- **Comprehensive Metrics**: Integration-ready for Prometheus monitoring

### Integration Goals

1. Enable programmatic invocation of prediction pipeline from backend APIs
2. Streamline output generation for frontend visualization
3. Provide extensible metrics reporting for production monitoring
4. Maintain modularity for independent component scaling

---

## Pipeline Architecture Overview

The pipeline consists of four main stages that can be invoked independently or as a complete workflow:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        NEUROSYMBOLIC PIPELINE                            │
│                                                                          │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────┐             │
│  │   Stage 1   │───▶│   Stage 2    │───▶│   Stage 3     │             │
│  │   Neural    │    │   Symbolic   │    │  Knowledge    │             │
│  │  Detection  │    │  Reasoning   │    │    Graph      │             │
│  └─────────────┘    └──────────────┘    └───────────────┘             │
│       │                   │                    │                        │
│       │                   │                    │                        │
│       ▼                   ▼                    ▼                        │
│  [Raw Predictions]  [Refined Predictions]  [Spatial Relations]         │
│  [Visualizations]   [Explainability]       [Prolog Facts]              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Stage 1: Neural Detection (SAHI + YOLO)

**Purpose:** Generate initial object detections from input images

**Components:**
- `pipeline/inference/sahi_yolo_prediction.py` - Main prediction script
- SAHI library - Intelligent image slicing for high-resolution processing
- YOLOv11-OBB model - Oriented bounding box detection

**Inputs:**
- Test images (JPG/PNG)
- Trained YOLO model weights (.pt file)
- Configuration parameters (slice size, overlap, confidence thresholds)

**Outputs:**
- YOLO-format prediction files (.txt) - One per image
- Raw detection bounding boxes and confidence scores

### Stage 2: Symbolic Reasoning

**Purpose:** Refine predictions using symbolic rules and evaluate performance

**Sub-stages:**

#### 2a. Preprocessing (`pipeline/core/preprocess.py`)
- Apply class-wise Non-Maximum Suppression (NMS)
- Filter overlapping detections
- Generate NMS-filtered predictions

#### 2b. Symbolic Adjustment (`pipeline/core/symbolic.py`)
- Load Prolog rules from `pipeline/prolog/rules.pl`
- Apply symbolic reasoning to adjust confidence scores
- Generate explainability reports

#### 2c. Evaluation (`pipeline/core/eval.py`)
- Compute mAP (mean Average Precision) metrics
- Compare predictions against ground truth
- Generate performance reports

### Stage 3: Knowledge Graph Construction

**Purpose:** Extract spatial relationships and build knowledge representation

**Component:**
- `pipeline/inference/weighted_kg_sahi.py`

**Capabilities:**
- Spatial relationship extraction (co-occurrence, adjacency, location)
- Prolog fact generation for symbolic reasoning
- Network graph visualization

---

## Component Structure

### Directory Layout

```
pipeline/
├── core/                           # Symbolic reasoning stages
│   ├── config.py                  # Configuration management
│   ├── preprocess.py              # NMS filtering
│   ├── symbolic.py                # Prolog-based refinement
│   ├── eval.py                    # Metrics computation
│   ├── run_pipeline.py            # Orchestration script
│   └── utils.py                   # Shared utilities
├── inference/                      # Neural detection and KG
│   ├── sahi_yolo_prediction.py   # SAHI-based prediction
│   └── weighted_kg_sahi.py       # Knowledge graph builder
├── training/                       # Model training (separate workflow)
│   └── training.py
├── prolog/                         # Symbolic rules
│   ├── rules.pl                   # Confidence adjustment rules
│   └── dataset_categories.pl     # Category definitions
└── nsai_pipeline.py               # Legacy wrapper

shared/
├── configs/                        # YAML configurations
│   ├── prediction_local.yaml
│   ├── prediction_kaggle.yaml
│   ├── pipeline_local.yaml
│   ├── pipeline_kaggle.yaml
│   ├── knowledge_graph_local.yaml
│   └── knowledge_graph_kaggle.yaml
└── utils/
    └── config_utils.py            # Config loading utilities
```

### Key Scripts and Their Purposes

| Script | Purpose | Invocation Pattern | Key Outputs |
|--------|---------|-------------------|-------------|
| `sahi_yolo_prediction.py` | Generate raw YOLO predictions with SAHI slicing | CLI or programmatic | `.txt` prediction files |
| `run_pipeline.py` | Orchestrate all symbolic stages (preprocess → symbolic → eval) | CLI or programmatic | Refined predictions, metrics reports |
| `preprocess.py` | Apply NMS to raw predictions | Independent or via `run_pipeline.py` | NMS-filtered predictions |
| `symbolic.py` | Apply Prolog rules for confidence adjustment | Independent or via `run_pipeline.py` | Refined predictions, explainability CSV |
| `eval.py` | Compute mAP and performance metrics | Independent or via `run_pipeline.py` | Evaluation reports (JSON/CSV) |
| `weighted_kg_sahi.py` | Build knowledge graph from predictions | Independent | Prolog facts, graph visualizations |

---

## Backend API Integration

### Integration Patterns

The pipeline can be integrated with backend APIs using three approaches:

#### Approach 1: Direct Subprocess Invocation

**When to use:** Simple deployments, prototyping, low-volume inference

```python
# Pseudocode for backend API handler
import subprocess
from pathlib import Path

def invoke_prediction(image_dir: str, model_path: str, output_dir: str):
    """Invoke SAHI prediction pipeline via subprocess."""

    # Construct command
    cmd = [
        "python", "-m", "pipeline.inference.sahi_yolo_prediction",
        "--model-path", model_path,
        "--test-images-dir", image_dir,
        "--output-predictions-dir", output_dir,
        "--confidence-threshold", "0.25",
        "--slice-height", "1024",
        "--slice-width", "1024"
    ]

    # Execute with timeout and error handling
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=600,  # 10-minute timeout
        check=True
    )

    return {
        "status": "success",
        "output_dir": output_dir,
        "stdout": result.stdout
    }
```

**Pros:**
- Simple implementation
- Process isolation
- Easy error handling

**Cons:**
- Synchronous blocking
- Resource inefficient for high-volume
- Limited scalability

#### Approach 2: Async Task Queue (Recommended)

**When to use:** Production deployments, high-volume inference, horizontal scaling

```python
# Pseudocode for Celery task integration
from celery import Celery
from pathlib import Path
import sys

app = Celery('pipeline_tasks', broker='redis://localhost:6379')

@app.task(bind=True, max_retries=3)
def run_inference_task(self, job_id: str, image_paths: list, config: dict):
    """Async task for running inference pipeline."""

    try:
        # Import pipeline modules
        sys.path.insert(0, "/path/to/project/root")
        from pipeline.inference import sahi_yolo_prediction

        # Set up configuration
        prediction_config = {
            "model_path": config["model_path"],
            "test_images_dir": config["image_dir"],
            "output_predictions_dir": config["output_dir"],
            "confidence_threshold": config.get("confidence", 0.25),
            "slice_height": config.get("slice_height", 1024),
            "slice_width": config.get("slice_width", 1024),
        }

        # Update job status to "processing"
        update_job_status(job_id, "processing")

        # Run prediction pipeline
        processed_count = sahi_yolo_prediction.run_prediction_pipeline(prediction_config)

        # Update job status to "completed"
        update_job_status(job_id, "completed", {
            "images_processed": processed_count,
            "output_dir": config["output_dir"]
        })

        return {"status": "completed", "processed": processed_count}

    except Exception as exc:
        # Retry logic with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

**Pros:**
- Asynchronous, non-blocking
- Horizontal scalability
- Built-in retry and error handling
- Queue prioritization support

**Cons:**
- Requires additional infrastructure (Redis/RabbitMQ)
- More complex setup

#### Approach 3: Direct Python Import

**When to use:** In-process execution, shared memory optimization, low latency

```python
# Pseudocode for direct import integration
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, "/path/to/project/root")

from pipeline.inference.sahi_yolo_prediction import (
    load_detection_model,
    run_prediction_pipeline
)
from shared.utils.config_utils import load_config_file

def predict_on_images(config_path: str, overrides: dict = None):
    """Direct Python integration for prediction."""

    # Load base configuration
    config = load_config_file(Path(config_path))

    # Apply runtime overrides
    if overrides:
        config.update(overrides)

    # Run pipeline directly
    processed_count = run_prediction_pipeline(config)

    return {
        "status": "success",
        "images_processed": processed_count,
        "output_dir": config["output_predictions_dir"]
    }
```

**Pros:**
- Lowest latency
- Shared memory (efficient for GPU)
- Direct exception handling

**Cons:**
- Same process isolation (memory leaks affect main process)
- GIL limitations for CPU-bound tasks
- Less fault-tolerant

### Recommended Architecture for Production

```
┌──────────────────────────────────────────────────────────────────────┐
│                         BACKEND API LAYER                             │
│  ┌────────────────┐                                                   │
│  │  FastAPI/Flask │  ◀──── HTTP Requests (upload, trigger, poll)     │
│  │   REST API     │                                                   │
│  └────────┬───────┘                                                   │
│           │                                                            │
│           ▼                                                            │
│  ┌───────────────────────────────────────────────────────┐           │
│  │         Job Queue (Redis + Celery)                    │           │
│  │                                                        │           │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐       │           │
│  │  │  Worker  │    │  Worker  │    │  Worker  │       │           │
│  │  │    1     │    │    2     │    │    N     │       │           │
│  │  └────┬─────┘    └────┬─────┘    └────┬─────┘       │           │
│  └───────┼──────────────┼───────────────┼──────────────┘           │
│          │              │               │                            │
└──────────┼──────────────┼───────────────┼───────────────────────────┘
           │              │               │
           ▼              ▼               ▼
    ┌───────────────────────────────────────────────┐
    │      PIPELINE EXECUTION LAYER                 │
    │                                                │
    │  ┌──────────────────────────────────────┐    │
    │  │  SAHI + YOLO Inference               │    │
    │  │  (sahi_yolo_prediction.py)           │    │
    │  └──────────────┬───────────────────────┘    │
    │                 │                             │
    │                 ▼                             │
    │  ┌──────────────────────────────────────┐    │
    │  │  Symbolic Reasoning Pipeline         │    │
    │  │  (preprocess → symbolic → eval)      │    │
    │  └──────────────┬───────────────────────┘    │
    │                 │                             │
    │                 ▼                             │
    │  ┌──────────────────────────────────────┐    │
    │  │  Knowledge Graph Construction        │    │
    │  │  (weighted_kg_sahi.py)               │    │
    │  └──────────────────────────────────────┘    │
    │                                                │
    └────────────────────────────────────────────────┘
                     │
                     ▼
    ┌────────────────────────────────────────────────┐
    │         OUTPUT STORAGE LAYER                   │
    │                                                 │
    │  • Prediction files (.txt)                     │
    │  • Visualization images (.png)                 │
    │  • Evaluation reports (.json/.csv)             │
    │  • Knowledge graph artifacts (.pl, .png)       │
    │  • Metadata and logs                           │
    └────────────────────────────────────────────────┘
                     │
                     ▼
    ┌────────────────────────────────────────────────┐
    │      MONITORING & METRICS LAYER                │
    │                                                 │
    │  • Prometheus metrics endpoint (/metrics)      │
    │  • Grafana dashboards                          │
    │  • Application logs                            │
    └────────────────────────────────────────────────┘
```

---

## End-to-End Integration Flow

### Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        END-TO-END WORKFLOW                                   │
└─────────────────────────────────────────────────────────────────────────────┘

   ┌─────────┐
   │ Frontend│
   │  Client │
   └────┬────┘
        │
        │ 1. Upload Images
        ▼
   ┌─────────────────┐
   │   Backend API   │◀───── POST /api/v1/inference/upload
   │   (FastAPI)     │
   └────┬────────────┘
        │
        │ 2. Validate & Store
        ▼
   ┌─────────────────┐
   │  File Storage   │
   │   (MinIO/S3)    │
   └────┬────────────┘
        │
        │ 3. Create Job
        ▼
   ┌─────────────────┐
   │   Job Queue     │◀───── POST /api/v1/inference/run
   │   (Celery)      │        {job_id, config}
   └────┬────────────┘
        │
        │ 4. Dequeue Job
        ▼
   ┌─────────────────┐
   │ Celery Worker   │
   │                 │
   │  ┌───────────┐  │
   │  │ Stage 1:  │  │ ──▶ Run SAHI + YOLO Prediction
   │  │ Neural    │  │     • Load model weights
   │  │ Detection │  │     • Process images with slicing
   │  │           │  │     • Generate raw predictions (.txt)
   │  └─────┬─────┘  │     • Log inference metrics
   │        │        │
   │        ▼        │
   │  ┌───────────┐  │
   │  │ Stage 2:  │  │ ──▶ Run Symbolic Reasoning
   │  │ Symbolic  │  │     • Apply NMS filtering
   │  │ Reasoning │  │     • Load Prolog rules
   │  │           │  │     • Adjust confidence scores
   │  └─────┬─────┘  │     • Generate explainability report
   │        │        │     • Compute mAP metrics
   │        ▼        │
   │  ┌───────────┐  │
   │  │ Stage 3:  │  │ ──▶ Build Knowledge Graph (Optional)
   │  │ Knowledge │  │     • Extract spatial relationships
   │  │ Graph     │  │     • Generate Prolog facts
   │  │           │  │     • Create graph visualization
   │  └─────┬─────┘  │
   │        │        │
   └────────┼────────┘
            │
            │ 5. Write Results
            ▼
   ┌─────────────────┐
   │ Output Storage  │
   │                 │
   │ • predictions/  │ ──▶ YOLO .txt files
   │ • visualizations│ ──▶ Annotated images
   │ • reports/      │ ──▶ JSON/CSV metrics
   │ • knowledge_graph│ ──▶ Prolog facts, graphs
   └────┬────────────┘
        │
        │ 6. Update Job Status
        ▼
   ┌─────────────────┐
   │   Database      │ ──▶ job_status: "completed"
   │  (PostgreSQL)   │     output_files: [...]
   └────┬────────────┘     metrics: {...}
        │
        │ 7. Emit Metrics
        ▼
   ┌─────────────────┐
   │  Prometheus     │ ──▶ inference_duration_seconds
   │   Metrics       │     images_processed_total
   └────┬────────────┘     model_confidence_avg
        │
        │ 8. Poll Status & Retrieve
        ▼
   ┌─────────────────┐
   │   Backend API   │◀───── GET /api/v1/jobs/{job_id}
   │                 │       GET /api/v1/results/{job_id}/predictions
   └────┬────────────┘       GET /api/v1/results/{job_id}/visualizations
        │
        │ 9. Return Results
        ▼
   ┌─────────┐
   │ Frontend│
   │  Client │ ──▶ Display results, charts, graphs
   └─────────┘
```

### Detailed Step-by-Step Flow

#### Step 1-3: Request Initiation

```
Frontend                Backend API              Storage
   │                         │                      │
   │ POST /upload/images     │                      │
   ├────────────────────────▶│                      │
   │                         │ Save images          │
   │                         ├─────────────────────▶│
   │                         │                      │
   │ Response: upload_id     │                      │
   │◀────────────────────────┤                      │
   │                         │                      │
   │ POST /inference/run     │                      │
   │ {upload_id, config}     │                      │
   ├────────────────────────▶│                      │
   │                         │                      │
   │                         │ Create job record    │
   │                         │ (status: "queued")   │
   │                         │                      │
   │ Response: job_id        │                      │
   │◀────────────────────────┤                      │
   │                         │                      │
```

#### Step 4-5: Async Processing

```
Backend API         Celery Queue         Worker              Pipeline
   │                     │                  │                    │
   │ Enqueue job         │                  │                    │
   ├────────────────────▶│                  │                    │
   │                     │                  │                    │
   │                     │ Dequeue job      │                    │
   │                     ├─────────────────▶│                    │
   │                     │                  │                    │
   │                     │                  │ Load config        │
   │                     │                  │ Prepare paths      │
   │                     │                  │                    │
   │                     │                  │ Invoke Stage 1     │
   │                     │                  ├───────────────────▶│
   │                     │                  │                    │
   │                     │                  │  SAHI Prediction   │
   │                     │                  │  • Load YOLO model │
   │                     │                  │  • Slice images    │
   │                     │                  │  • Detect objects  │
   │                     │                  │  • Write .txt      │
   │                     │                  │                    │
   │                     │                  │◀───────────────────│
   │                     │                  │                    │
   │                     │                  │ Invoke Stage 2     │
   │                     │                  ├───────────────────▶│
   │                     │                  │                    │
   │                     │                  │  NMS Preprocess    │
   │                     │                  │  Symbolic Reason   │
   │                     │                  │  Evaluate mAP      │
   │                     │                  │                    │
   │                     │                  │◀───────────────────│
   │                     │                  │                    │
   │                     │                  │ Write results      │
   │                     │                  │ Update job status  │
   │                     │                  │ Emit metrics       │
   │                     │                  │                    │
   │                     │ Task complete    │                    │
   │                     │◀─────────────────┤                    │
   │                     │                  │                    │
```

#### Step 6-9: Result Retrieval

```
Frontend            Backend API          Database           Storage
   │                     │                   │                 │
   │ GET /jobs/{id}      │                   │                 │
   ├────────────────────▶│                   │                 │
   │                     │ Query job status  │                 │
   │                     ├──────────────────▶│                 │
   │                     │                   │                 │
   │                     │ job_status: "completed"            │
   │                     │◀──────────────────┤                 │
   │                     │                   │                 │
   │ Response: status    │                   │                 │
   │◀────────────────────┤                   │                 │
   │                     │                   │                 │
   │ GET /results/{id}   │                   │                 │
   ├────────────────────▶│                   │                 │
   │                     │ Fetch output paths                 │
   │                     ├──────────────────▶│                 │
   │                     │                   │                 │
   │                     │ Read files        │                 │
   │                     ├────────────────────────────────────▶│
   │                     │                   │                 │
   │                     │ File contents     │                 │
   │                     │◀────────────────────────────────────┤
   │                     │                   │                 │
   │ Response: results   │                   │                 │
   │◀────────────────────┤                   │                 │
   │                     │                   │                 │
```

---

## File Outputs and Formats

### Output Directory Structure

```
output_root/
├── predictions/
│   ├── raw/                        # Stage 1 output
│   │   ├── image001.txt
│   │   ├── image002.txt
│   │   └── ...
│   ├── nms_filtered/               # Stage 2a output
│   │   ├── image001.txt
│   │   ├── image002.txt
│   │   └── ...
│   └── refined/                    # Stage 2b output
│       ├── image001.txt
│       ├── image002.txt
│       └── ...
├── visualizations/
│   ├── annotated/                  # Bounding box overlays
│   │   ├── image001_annotated.png
│   │   ├── image002_annotated.png
│   │   └── ...
│   └── confidence_maps/            # Heatmaps (optional)
│       ├── image001_heatmap.png
│       └── ...
├── reports/
│   ├── explainability_report.csv  # Symbolic reasoning adjustments
│   ├── evaluation_metrics.json    # mAP, precision, recall
│   └── inference_summary.json     # Processing statistics
├── knowledge_graph/
│   ├── facts.pl                   # Prolog spatial facts
│   ├── knowledge_graph_visuals.png # Graph visualization
│   └── relation_statistics.json   # Relationship counts
└── logs/
    ├── inference.log              # Detailed execution logs
    └── error.log                  # Error tracking
```

### Prediction File Format (.txt)

**YOLO Normalized Format:**

```
<class_id> <x_center> <y_center> <width> <height> <confidence>
```

**Example:**
```txt
0 0.512345 0.678912 0.123456 0.089765 0.945123
1 0.234567 0.456789 0.098765 0.123456 0.876543
0 0.789012 0.345678 0.156789 0.234567 0.912345
```

**Field Descriptions:**
- `class_id`: Integer category ID (e.g., 0=plane, 1=ship, 2=storage_tank)
- `x_center`: Normalized x-coordinate of bounding box center (0.0-1.0)
- `y_center`: Normalized y-coordinate of bounding box center (0.0-1.0)
- `width`: Normalized width of bounding box (0.0-1.0)
- `height`: Normalized height of bounding box (0.0-1.0)
- `confidence`: Detection confidence score (0.0-1.0)

**Conversion to Pixel Coordinates:**

```python
# Pseudocode for YOLO → VOC pixel conversion
def yolo_to_voc(yolo_coords, image_width, image_height):
    """Convert YOLO normalized to VOC pixel coordinates."""
    cx, cy, w, h = yolo_coords
    
    # Calculate pixel coordinates
    x_center_px = cx * image_width
    y_center_px = cy * image_height
    width_px = w * image_width
    height_px = h * image_height
    
    # Convert to corner coordinates
    x_min = x_center_px - (width_px / 2)
    y_min = y_center_px - (height_px / 2)
    x_max = x_center_px + (width_px / 2)
    y_max = y_center_px + (height_px / 2)
    
    return [x_min, y_min, x_max, y_max]
```

### Evaluation Metrics Format (JSON)

**File:** `reports/evaluation_metrics.json`

```json
{
  "dataset": "validation_set",
  "model": "yolov11m-obb",
  "timestamp": "2026-02-03T16:52:39Z",
  "overall_metrics": {
    "mAP_50": 0.756,
    "mAP_75": 0.623,
    "mAP_50_95": 0.589,
    "precision": 0.812,
    "recall": 0.734
  },
  "per_class_metrics": {
    "plane": {
      "ap_50": 0.823,
      "ap_75": 0.701,
      "precision": 0.856,
      "recall": 0.789,
      "instances": 1024
    },
    "ship": {
      "ap_50": 0.791,
      "ap_75": 0.678,
      "precision": 0.834,
      "recall": 0.756,
      "instances": 892
    }
  },
  "processing_stats": {
    "images_processed": 458,
    "total_detections": 15234,
    "average_confidence": 0.847,
    "inference_time_seconds": 312.45,
    "average_time_per_image": 0.682
  }
}
```

### Explainability Report Format (CSV)

**File:** `reports/explainability_report.csv`

```csv
image_name,object_id,class_id,class_name,original_confidence,adjusted_confidence,adjustment_reason,spatial_context
image001.png,0,2,small_vehicle,0.85,0.92,located_near_parking_lot,adjacent_to_road
image001.png,1,5,plane,0.78,0.88,located_on_airport_runway,near_hangar
image002.png,0,3,ship,0.91,0.95,located_in_harbor,near_dock
image002.png,1,3,ship,0.73,0.81,cooccurs_with_other_ships,in_formation
```

**Column Descriptions:**
- `image_name`: Source image filename
- `object_id`: Sequential object ID within image
- `class_id`: Numeric category identifier
- `class_name`: Human-readable category label
- `original_confidence`: Initial YOLO confidence score
- `adjusted_confidence`: Post-symbolic-reasoning confidence
- `adjustment_reason`: Prolog rule that triggered adjustment
- `spatial_context`: Contextual information from spatial relationships

### Knowledge Graph Prolog Facts

**File:** `knowledge_graph/facts.pl`

```prolog
% fact(Relation, Subject, Object, Count).
fact('cooccurs', 'plane', 'plane', 15234).
fact('cooccurs', 'ship', 'harbor', 8234).
fact('cooccurs', 'small_vehicle', 'small_vehicle', 45123).
fact('located_near', 'ship', 'harbor', 1234).
fact('located_near', 'small_vehicle', 'roundabout', 876).
fact('located_on', 'large_vehicle', 'Bridge', 234).
fact('adjacent_to', 'tennis_court', 'basketball_court', 456).
fact('adjacent_to', 'plane', 'plane', 789).
```

**Usage in Symbolic Reasoning:**

```prolog
% Query examples
?- fact('located_near', 'ship', Object, Count).
Object = 'harbor', Count = 1234.

?- fact(Relation, 'plane', 'plane', Count), Count > 1000.
Relation = 'cooccurs', Count = 15234.
```



---

## Prometheus Metrics Integration

### Metrics Collection Strategy

The pipeline exposes metrics at multiple stages to enable comprehensive monitoring:

```
┌────────────────────────────────────────────────────────────────┐
│                    METRICS COLLECTION POINTS                    │
└────────────────────────────────────────────────────────────────┘

Stage 1: Neural Detection
  ├─ inference_duration_seconds (histogram)
  ├─ images_processed_total (counter)
  ├─ model_load_duration_seconds (histogram)
  ├─ average_confidence_score (gauge)
  ├─ detections_per_image (histogram)
  └─ gpu_memory_usage_bytes (gauge)

Stage 2: Symbolic Reasoning
  ├─ nms_filtering_duration_seconds (histogram)
  ├─ prolog_reasoning_duration_seconds (histogram)
  ├─ confidence_adjustments_total (counter)
  ├─ average_confidence_delta (gauge)
  └─ symbolic_rules_applied_total (counter)

Stage 3: Knowledge Graph
  ├─ kg_construction_duration_seconds (histogram)
  ├─ spatial_relations_extracted_total (counter)
  ├─ prolog_facts_generated_total (counter)
  └─ graph_nodes_total (gauge)

Overall Pipeline
  ├─ pipeline_execution_duration_seconds (histogram)
  ├─ pipeline_success_total (counter)
  ├─ pipeline_failure_total (counter)
  └─ pipeline_stage_duration_seconds (histogram, by stage)
```

### Metric Definitions

#### Counter Metrics

**Characteristics:** Monotonically increasing, reset on restart

```python
# images_processed_total
# HELP images_processed_total Total number of images processed through inference
# TYPE images_processed_total counter
images_processed_total{stage="neural_detection",model="yolov11m-obb"} 15234

# confidence_adjustments_total
# HELP confidence_adjustments_total Number of detections with confidence adjusted by symbolic reasoning
# TYPE confidence_adjustments_total counter
confidence_adjustments_total{adjustment_type="increase"} 3421
confidence_adjustments_total{adjustment_type="decrease"} 876
```

#### Histogram Metrics

**Characteristics:** Track distribution of values (duration, size, etc.)

```python
# inference_duration_seconds
# HELP inference_duration_seconds Time taken for inference per image
# TYPE inference_duration_seconds histogram
inference_duration_seconds_bucket{le="0.5"} 234
inference_duration_seconds_bucket{le="1.0"} 1245
inference_duration_seconds_bucket{le="2.0"} 3421
inference_duration_seconds_bucket{le="5.0"} 4567
inference_duration_seconds_bucket{le="+Inf"} 4892
inference_duration_seconds_sum 8234.56
inference_duration_seconds_count 4892

# detections_per_image
# HELP detections_per_image Number of objects detected per image
# TYPE detections_per_image histogram
detections_per_image_bucket{le="10"} 456
detections_per_image_bucket{le="50"} 2345
detections_per_image_bucket{le="100"} 3789
detections_per_image_bucket{le="+Inf"} 4892
detections_per_image_sum 234561
detections_per_image_count 4892
```

#### Gauge Metrics

**Characteristics:** Can increase or decrease, represents current state

```python
# average_confidence_score
# HELP average_confidence_score Current average confidence across all active detections
# TYPE average_confidence_score gauge
average_confidence_score{stage="raw_predictions"} 0.847
average_confidence_score{stage="refined_predictions"} 0.892

# gpu_memory_usage_bytes
# HELP gpu_memory_usage_bytes Current GPU memory usage in bytes
# TYPE gpu_memory_usage_bytes gauge
gpu_memory_usage_bytes{device="cuda:0"} 4294967296
```

### Instrumentation Example

**Pseudocode for adding metrics to pipeline:**

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
images_processed = Counter(
    'images_processed_total',
    'Total images processed',
    ['stage', 'model']
)

inference_duration = Histogram(
    'inference_duration_seconds',
    'Time spent on inference per image',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

average_confidence = Gauge(
    'average_confidence_score',
    'Average confidence of predictions',
    ['stage']
)

def run_prediction_with_metrics(image_path: str, model, config: dict):
    """Run inference with Prometheus instrumentation."""
    
    # Track processing
    start_time = time.time()
    
    try:
        # Run actual inference
        result = model.predict(image_path, **config)
        
        # Record metrics
        duration = time.time() - start_time
        inference_duration.observe(duration)
        
        images_processed.labels(
            stage='neural_detection',
            model=config['model_name']
        ).inc()
        
        # Calculate and record average confidence
        confidences = [pred.confidence for pred in result.predictions]
        avg_conf = sum(confidences) / len(confidences) if confidences else 0
        average_confidence.labels(stage='raw_predictions').set(avg_conf)
        
        return result
        
    except Exception as exc:
        # Track failures
        pipeline_failures.labels(stage='neural_detection').inc()
        raise
```

### Metrics Endpoint

The backend API should expose a `/metrics` endpoint for Prometheus scraping:

```python
# FastAPI example
from fastapi import FastAPI
from prometheus_client import make_asgi_app

app = FastAPI()

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

**Prometheus Scrape Configuration:**

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'neurosymbolic_pipeline'
    scrape_interval: 15s
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
```

### Grafana Dashboard Configuration

**Key Dashboard Panels:**

1. **Throughput Panel**
   - Metric: `rate(images_processed_total[5m])`
   - Visualization: Graph (time series)
   - Description: Images processed per second over time

2. **Latency Panel**
   - Metric: `histogram_quantile(0.95, rate(inference_duration_seconds_bucket[5m]))`
   - Visualization: Graph (percentiles: p50, p95, p99)
   - Description: Inference latency distribution

3. **Success Rate Panel**
   - Metric: `rate(pipeline_success_total[5m]) / (rate(pipeline_success_total[5m]) + rate(pipeline_failure_total[5m]))`
   - Visualization: Gauge (0-100%)
   - Description: Pipeline success rate

4. **Confidence Distribution Panel**
   - Metric: `average_confidence_score`
   - Visualization: Stat panel with sparkline
   - Description: Current average confidence trends

5. **GPU Utilization Panel**
   - Metric: `gpu_memory_usage_bytes / gpu_memory_total_bytes`
   - Visualization: Gauge (0-100%)
   - Description: GPU memory usage percentage

---

## Pseudocode Examples

### Example 1: Complete Inference Workflow

```python
"""
Complete inference workflow from image upload to result retrieval.
This example shows the recommended async task queue approach.
"""

from fastapi import FastAPI, UploadFile, File
from celery import Celery
from pathlib import Path
import uuid
import sys

# FastAPI application
app = FastAPI()

# Celery configuration
celery_app = Celery('tasks', broker='redis://localhost:6379')

# Database models (pseudocode)
class Job:
    job_id: str
    status: str  # "queued", "processing", "completed", "failed"
    upload_id: str
    config: dict
    results: dict
    created_at: datetime
    updated_at: datetime


# Step 1: Upload images
@app.post("/api/v1/inference/upload")
async def upload_images(files: list[UploadFile] = File(...)):
    """Upload images for inference."""
    
    upload_id = str(uuid.uuid4())
    upload_dir = Path(f"/storage/uploads/{upload_id}")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    uploaded_files = []
    for file in files:
        file_path = upload_dir / file.filename
        with file_path.open('wb') as f:
            f.write(await file.read())
        uploaded_files.append(str(file_path))
    
    return {
        "upload_id": upload_id,
        "files_count": len(uploaded_files),
        "storage_path": str(upload_dir)
    }


# Step 2: Trigger inference
@app.post("/api/v1/inference/run")
async def trigger_inference(upload_id: str, config: dict = None):
    """Create inference job and enqueue for processing."""
    
    # Validate upload exists
    upload_dir = Path(f"/storage/uploads/{upload_id}")
    if not upload_dir.exists():
        raise HTTPException(404, "Upload not found")
    
    # Create job record
    job_id = str(uuid.uuid4())
    job = Job(
        job_id=job_id,
        status="queued",
        upload_id=upload_id,
        config=config or get_default_config(),
        results={},
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    save_job(job)
    
    # Enqueue Celery task
    inference_task.delay(job_id)
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Inference job created and queued for processing"
    }


# Step 3: Celery worker task
@celery_app.task(bind=True, max_retries=3)
def inference_task(self, job_id: str):
    """Execute inference pipeline asynchronously."""
    
    try:
        # Load job configuration
        job = load_job(job_id)
        update_job_status(job_id, "processing")
        
        # Prepare paths
        upload_dir = Path(f"/storage/uploads/{job.upload_id}")
        output_dir = Path(f"/storage/outputs/{job_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Import pipeline modules
        sys.path.insert(0, "/path/to/project/root")
        from pipeline.inference import sahi_yolo_prediction
        from pipeline.core import run_pipeline
        
        # Stage 1: SAHI + YOLO Prediction
        prediction_config = {
            "model_path": job.config.get("model_path", "/models/yolov11m-obb.pt"),
            "test_images_dir": str(upload_dir),
            "output_predictions_dir": str(output_dir / "predictions" / "raw"),
            "confidence_threshold": job.config.get("confidence", 0.25),
            "slice_height": job.config.get("slice_height", 1024),
            "slice_width": job.config.get("slice_width", 1024),
            "overlap_height": job.config.get("overlap_height", 0.2),
            "overlap_width": job.config.get("overlap_width", 0.2),
        }
        
        processed_count = sahi_yolo_prediction.run_prediction_pipeline(
            prediction_config
        )
        
        # Stage 2: Symbolic Reasoning (Optional)
        if job.config.get("enable_symbolic_reasoning", True):
            pipeline_config = {
                "raw_predictions_dir": str(output_dir / "predictions" / "raw"),
                "nms_predictions_dir": str(output_dir / "predictions" / "nms"),
                "refined_predictions_dir": str(output_dir / "predictions" / "refined"),
                "ground_truth_dir": job.config.get("ground_truth_dir"),
                "rules_file": "/path/to/pipeline/prolog/rules.pl",
                "report_file": str(output_dir / "reports" / "explainability.csv"),
                "nms_iou_threshold": job.config.get("iou_threshold", 0.45),
            }
            
            run_pipeline.main(pipeline_config)
        
        # Stage 3: Knowledge Graph (Optional)
        if job.config.get("enable_knowledge_graph", False):
            from pipeline.inference import weighted_kg_sahi
            kg_config = {
                "model_path": prediction_config["model_path"],
                "data_splits": {"test": str(upload_dir)},
                "knowledge_graph_dir": str(output_dir / "knowledge_graph"),
                "confidence_threshold": prediction_config["confidence_threshold"],
                "slice_height": prediction_config["slice_height"],
                "slice_width": prediction_config["slice_width"],
            }
            
            weighted_kg_sahi.main(kg_config)
        
        # Update job with results
        job.results = {
            "images_processed": processed_count,
            "output_directory": str(output_dir),
            "prediction_files": list_files(output_dir / "predictions" / "refined"),
            "report_files": list_files(output_dir / "reports"),
        }
        update_job_status(job_id, "completed", job.results)
        
        return {"status": "completed", "job_id": job_id}
        
    except Exception as exc:
        # Handle errors and retry
        update_job_status(job_id, "failed", {"error": str(exc)})
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


# Step 4: Poll job status
@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get current status of inference job."""
    
    job = load_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    
    return {
        "job_id": job.job_id,
        "status": job.status,
        "upload_id": job.upload_id,
        "config": job.config,
        "results": job.results,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
    }


# Step 5: Retrieve results
@app.get("/api/v1/results/{job_id}/predictions")
async def get_predictions(job_id: str, image_name: str = None):
    """Retrieve prediction results for completed job."""
    
    job = load_job(job_id)
    if not job or job.status != "completed":
        raise HTTPException(400, "Job not completed or not found")
    
    output_dir = Path(job.results["output_directory"])
    predictions_dir = output_dir / "predictions" / "refined"
    
    if image_name:
        # Return predictions for specific image
        pred_file = predictions_dir / f"{Path(image_name).stem}.txt"
        if not pred_file.exists():
            raise HTTPException(404, "Predictions not found for image")
        
        predictions = parse_prediction_file(pred_file)
        return {"image": image_name, "predictions": predictions}
    else:
        # Return summary of all predictions
        all_predictions = {}
        for pred_file in predictions_dir.glob("*.txt"):
            all_predictions[pred_file.stem] = parse_prediction_file(pred_file)
        
        return {"predictions": all_predictions, "total_images": len(all_predictions)}


@app.get("/api/v1/results/{job_id}/metrics")
async def get_metrics(job_id: str):
    """Retrieve evaluation metrics for completed job."""
    
    job = load_job(job_id)
    if not job or job.status != "completed":
        raise HTTPException(400, "Job not completed or not found")
    
    output_dir = Path(job.results["output_directory"])
    metrics_file = output_dir / "reports" / "evaluation_metrics.json"
    
    if not metrics_file.exists():
        return {"message": "Metrics not available"}
    
    with metrics_file.open('r') as f:
        metrics = json.load(f)
    
    return metrics


# Helper functions
def parse_prediction_file(file_path: Path) -> list:
    """Parse YOLO prediction file into structured format."""
    predictions = []
    with file_path.open('r') as f:
        for line in f:
            parts = line.strip().split()
            predictions.append({
                "class_id": int(parts[0]),
                "x_center": float(parts[1]),
                "y_center": float(parts[2]),
                "width": float(parts[3]),
                "height": float(parts[4]),
                "confidence": float(parts[5]) if len(parts) > 5 else None
            })
    return predictions


def get_default_config() -> dict:
    """Return default inference configuration."""
    return {
        "model_path": "/models/yolov11m-obb.pt",
        "confidence": 0.25,
        "iou_threshold": 0.45,
        "slice_height": 1024,
        "slice_width": 1024,
        "overlap_height": 0.2,
        "overlap_width": 0.2,
        "enable_symbolic_reasoning": True,
        "enable_knowledge_graph": False,
    }
```

### Example 2: Direct Python Import Integration

```python
"""
Direct Python import for low-latency, in-process inference.
Suitable for simple deployments or when GPU sharing is required.
"""

from pathlib import Path
import sys
import logging

# Add project to path
sys.path.insert(0, "/path/to/project/root")

from pipeline.inference.sahi_yolo_prediction import (
    load_configuration,
    load_detection_model,
    collect_image_files,
    run_prediction_pipeline
)
from shared.utils.config_utils import load_config_file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_inference_direct(
    image_dir: str,
    model_path: str,
    output_dir: str,
    config_overrides: dict = None
) -> dict:
    """
    Run inference directly in current process.
    
    Args:
        image_dir: Directory containing input images
        model_path: Path to YOLO model weights
        output_dir: Directory for output predictions
        config_overrides: Optional config parameter overrides
    
    Returns:
        Dictionary with processing results and metrics
    """
    
    # Build configuration
    config = {
        "model_path": Path(model_path),
        "test_images_dir": Path(image_dir),
        "output_predictions_dir": Path(output_dir),
        "confidence_threshold": 0.25,
        "slice_height": 1024,
        "slice_width": 1024,
        "overlap_height": 0.2,
        "overlap_width": 0.2,
    }
    
    # Apply overrides
    if config_overrides:
        config.update(config_overrides)
    
    # Ensure output directory exists
    config["output_predictions_dir"].mkdir(parents=True, exist_ok=True)
    
    try:
        # Load model
        logger.info(f"Loading YOLO model from {model_path}")
        detection_model = load_detection_model(config)
        
        # Collect images
        image_files = list(collect_image_files(config["test_images_dir"]))
        logger.info(f"Found {len(image_files)} images to process")
        
        if not image_files:
            return {
                "status": "error",
                "message": "No images found in input directory"
            }
        
        # Run predictions
        logger.info("Starting inference...")
        processed_count = run_prediction_pipeline(config)
        logger.info(f"Successfully processed {processed_count} images")
        
        # Return results
        return {
            "status": "success",
            "images_processed": processed_count,
            "output_directory": str(config["output_predictions_dir"]),
            "prediction_files": [
                str(f) for f in config["output_predictions_dir"].glob("*.txt")
            ]
        }
        
    except FileNotFoundError as exc:
        logger.error(f"File not found: {exc}")
        return {"status": "error", "message": str(exc)}
    
    except RuntimeError as exc:
        logger.error(f"Runtime error: {exc}")
        return {"status": "error", "message": str(exc)}
    
    except Exception as exc:
        logger.exception("Unexpected error during inference")
        return {"status": "error", "message": f"Unexpected error: {exc}"}


# Usage example
if __name__ == "__main__":
    result = run_inference_direct(
        image_dir="/data/test_images",
        model_path="/models/yolov11m-obb.pt",
        output_dir="/outputs/predictions",
        config_overrides={
            "confidence_threshold": 0.3,
            "slice_height": 640,
            "slice_width": 640,
        }
    )
    
    print(f"Inference result: {result}")
```



### Example 3: Subprocess Invocation with Error Handling

```python
"""
Subprocess invocation pattern with comprehensive error handling.
Suitable for simple deployments where process isolation is preferred.
"""

import subprocess
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class PipelineInvocationError(Exception):
    """Custom exception for pipeline invocation errors."""
    pass


def invoke_pipeline_subprocess(
    command: list[str],
    timeout: int = 600,
    cwd: Optional[str] = None
) -> Dict[str, Any]:
    """
    Invoke pipeline script as subprocess with error handling.
    
    Args:
        command: Command and arguments as list
        timeout: Maximum execution time in seconds
        cwd: Working directory for subprocess
    
    Returns:
        Dictionary with execution results
    
    Raises:
        PipelineInvocationError: If execution fails
    """
    
    try:
        logger.info(f"Executing command: {' '.join(command)}")
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            check=True
        )
        
        logger.info("Command executed successfully")
        return {
            "status": "success",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
        
    except subprocess.TimeoutExpired as exc:
        logger.error(f"Command timed out after {timeout} seconds")
        raise PipelineInvocationError(
            f"Pipeline execution timed out after {timeout} seconds"
        ) from exc
    
    except subprocess.CalledProcessError as exc:
        logger.error(f"Command failed with return code {exc.returncode}")
        logger.error(f"STDOUT: {exc.stdout}")
        logger.error(f"STDERR: {exc.stderr}")
        raise PipelineInvocationError(
            f"Pipeline execution failed: {exc.stderr}"
        ) from exc
    
    except FileNotFoundError as exc:
        logger.error(f"Command not found: {command[0]}")
        raise PipelineInvocationError(
            f"Python interpreter or script not found: {command[0]}"
        ) from exc
    
    except Exception as exc:
        logger.exception("Unexpected error during pipeline execution")
        raise PipelineInvocationError(
            f"Unexpected error: {exc}"
        ) from exc


def run_sahi_prediction_subprocess(
    model_path: str,
    image_dir: str,
    output_dir: str,
    config: dict = None
) -> Dict[str, Any]:
    """
    Run SAHI prediction via subprocess.
    
    Args:
        model_path: Path to YOLO model weights
        image_dir: Directory containing input images
        output_dir: Directory for output predictions
        config: Optional configuration overrides
    
    Returns:
        Dictionary with processing results
    """
    
    # Validate inputs
    if not Path(model_path).exists():
        raise PipelineInvocationError(f"Model not found: {model_path}")
    
    if not Path(image_dir).exists():
        raise PipelineInvocationError(f"Image directory not found: {image_dir}")
    
    # Prepare output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Build command
    cmd = [
        "python", "-m", "pipeline.inference.sahi_yolo_prediction",
        "--model-path", model_path,
        "--test-images-dir", image_dir,
        "--output-predictions-dir", output_dir,
    ]
    
    # Add optional config parameters
    if config:
        if "confidence_threshold" in config:
            cmd.extend(["--confidence-threshold", str(config["confidence_threshold"])])
        if "slice_height" in config:
            cmd.extend(["--slice-height", str(config["slice_height"])])
        if "slice_width" in config:
            cmd.extend(["--slice-width", str(config["slice_width"])])
    
    # Execute
    result = invoke_pipeline_subprocess(cmd, timeout=600)
    
    # Parse results
    prediction_files = list(Path(output_dir).glob("*.txt"))
    
    return {
        "status": "success",
        "images_processed": len(prediction_files),
        "output_directory": output_dir,
        "prediction_files": [str(f) for f in prediction_files]
    }


# Usage example
if __name__ == "__main__":
    try:
        result = run_sahi_prediction_subprocess(
            model_path="/models/yolov11m-obb.pt",
            image_dir="/data/test_images",
            output_dir="/outputs/predictions",
            config={
                "confidence_threshold": 0.25,
                "slice_height": 1024,
                "slice_width": 1024
            }
        )
        print(json.dumps(result, indent=2))
        
    except PipelineInvocationError as exc:
        print(f"Pipeline error: {exc}")
        exit(1)
```

---

## Error Handling and Recovery

### Error Categories

The pipeline can encounter various types of errors during execution. Understanding these categories helps implement appropriate recovery strategies:

#### 1. Configuration Errors

**Examples:**
- Missing required configuration parameters
- Invalid file paths
- Incorrect data types
- Out-of-range values

**Detection:**
- Early validation before pipeline execution
- Schema validation for configuration files
- Path existence checks

**Recovery Strategy:**
```python
def validate_config(config: dict) -> None:
    """Validate configuration and raise descriptive errors."""
    
    # Check required fields
    required = ["model_path", "test_images_dir", "output_predictions_dir"]
    for field in required:
        if field not in config:
            raise ConfigError(f"Missing required field: {field}")
    
    # Validate paths
    if not Path(config["model_path"]).exists():
        raise ConfigError(f"Model not found: {config['model_path']}")
    
    if not Path(config["test_images_dir"]).exists():
        raise ConfigError(f"Image directory not found: {config['test_images_dir']}")
    
    # Validate numeric ranges
    if not (0 < config.get("confidence_threshold", 0.25) <= 1.0):
        raise ConfigError("confidence_threshold must be between 0 and 1")
```

#### 2. Resource Errors

**Examples:**
- Out of memory (GPU/CPU)
- Disk space exhausted
- GPU not available when required
- Network timeouts (model downloads)

**Detection:**
- Monitor system resources before execution
- Catch out-of-memory exceptions
- Check GPU availability

**Recovery Strategy:**
```python
import torch
import psutil

def check_resources(config: dict) -> dict:
    """Check system resources and recommend adjustments."""
    
    warnings = []
    
    # Check GPU availability
    if not torch.cuda.is_available():
        warnings.append({
            "type": "gpu_unavailable",
            "message": "GPU not available, will use CPU (slower performance)",
            "recommendation": "Install CUDA-compatible GPU drivers"
        })
    else:
        # Check GPU memory
        gpu_mem = torch.cuda.get_device_properties(0).total_memory
        if gpu_mem < 4 * 1024 ** 3:  # Less than 4GB
            warnings.append({
                "type": "low_gpu_memory",
                "message": f"GPU memory ({gpu_mem / 1024**3:.1f}GB) may be insufficient",
                "recommendation": "Reduce batch size or slice dimensions"
            })
    
    # Check disk space
    disk_usage = psutil.disk_usage(config["output_predictions_dir"])
    if disk_usage.free < 10 * 1024 ** 3:  # Less than 10GB free
        warnings.append({
            "type": "low_disk_space",
            "message": f"Low disk space ({disk_usage.free / 1024**3:.1f}GB free)",
            "recommendation": "Free up disk space or change output directory"
        })
    
    # Check RAM
    ram = psutil.virtual_memory()
    if ram.available < 4 * 1024 ** 3:  # Less than 4GB available
        warnings.append({
            "type": "low_memory",
            "message": f"Low RAM ({ram.available / 1024**3:.1f}GB available)",
            "recommendation": "Close other applications or reduce image batch size"
        })
    
    return {"warnings": warnings}
```

#### 3. Data Errors

**Examples:**
- Corrupted images
- Unsupported image formats
- Empty prediction files
- Malformed label files

**Detection:**
- File validation before processing
- Try-except around image loading
- Content verification after processing

**Recovery Strategy:**
```python
from PIL import Image

def validate_image(image_path: Path) -> bool:
    """Validate image file is readable and supported."""
    
    try:
        with Image.open(image_path) as img:
            img.verify()  # Verify it's a valid image
        
        # Check format
        if image_path.suffix.lower() not in {'.jpg', '.jpeg', '.png'}:
            logger.warning(f"Unsupported format: {image_path}")
            return False
        
        return True
        
    except Exception as exc:
        logger.error(f"Invalid image {image_path}: {exc}")
        return False


def process_images_with_validation(image_dir: Path, config: dict):
    """Process images with per-image error handling."""
    
    image_files = list(image_dir.glob("*.{jpg,png}"))
    processed = []
    failed = []
    
    for image_path in image_files:
        try:
            # Validate before processing
            if not validate_image(image_path):
                failed.append({
                    "file": str(image_path),
                    "error": "Invalid or unsupported image format"
                })
                continue
            
            # Process image
            result = process_single_image(image_path, config)
            processed.append(str(image_path))
            
        except Exception as exc:
            logger.exception(f"Failed to process {image_path}")
            failed.append({
                "file": str(image_path),
                "error": str(exc)
            })
            continue
    
    return {
        "processed": processed,
        "failed": failed,
        "success_rate": len(processed) / len(image_files) if image_files else 0
    }
```

#### 4. Model Errors

**Examples:**
- Model weights not found
- Incompatible model versions
- Model loading failures
- Inference errors

**Detection:**
- Model validation after loading
- Version compatibility checks
- Inference dry-run

**Recovery Strategy:**
```python
from ultralytics import YOLO

def load_model_with_validation(model_path: str, expected_classes: int = None):
    """Load YOLO model with validation."""
    
    try:
        # Load model
        model = YOLO(model_path)
        
        # Validate model structure
        if expected_classes and len(model.names) != expected_classes:
            raise RuntimeError(
                f"Model has {len(model.names)} classes, expected {expected_classes}"
            )
        
        # Test inference on dummy data
        import numpy as np
        dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
        _ = model.predict(dummy_image, verbose=False)
        
        logger.info(f"Model loaded successfully: {model_path}")
        logger.info(f"Classes: {list(model.names.values())}")
        
        return model
        
    except FileNotFoundError:
        raise RuntimeError(f"Model weights not found: {model_path}")
    
    except Exception as exc:
        raise RuntimeError(f"Failed to load model: {exc}")
```

### Retry Mechanisms

For transient failures, implement exponential backoff retry:

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, backoff_factor=2, exceptions=(Exception,)):
    """Decorator for retrying failed operations with exponential backoff."""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    retries += 1
                    if retries >= max_retries:
                        raise
                    
                    wait_time = backoff_factor ** retries
                    logger.warning(
                        f"{func.__name__} failed (attempt {retries}/{max_retries}), "
                        f"retrying in {wait_time}s: {exc}"
                    )
                    time.sleep(wait_time)
        return wrapper
    return decorator


@retry_on_failure(max_retries=3, exceptions=(RuntimeError, TimeoutError))
def download_model(model_url: str, dest_path: str):
    """Download model with automatic retry on failure."""
    # Implementation here
    pass
```

### Graceful Degradation

When certain features fail, provide fallback behavior:

```python
def run_pipeline_with_fallback(config: dict) -> dict:
    """Run pipeline with graceful degradation on feature failures."""
    
    results = {
        "stage_1_neural": None,
        "stage_2_symbolic": None,
        "stage_3_knowledge_graph": None,
        "warnings": []
    }
    
    # Stage 1: Neural Detection (Required)
    try:
        results["stage_1_neural"] = run_neural_detection(config)
    except Exception as exc:
        # Cannot proceed without stage 1
        raise RuntimeError(f"Neural detection failed: {exc}")
    
    # Stage 2: Symbolic Reasoning (Optional)
    try:
        results["stage_2_symbolic"] = run_symbolic_reasoning(config)
    except Exception as exc:
        logger.warning(f"Symbolic reasoning failed: {exc}")
        results["warnings"].append({
            "stage": "symbolic_reasoning",
            "error": str(exc),
            "impact": "Predictions will not be refined with symbolic rules"
        })
    
    # Stage 3: Knowledge Graph (Optional)
    try:
        results["stage_3_knowledge_graph"] = run_knowledge_graph(config)
    except Exception as exc:
        logger.warning(f"Knowledge graph construction failed: {exc}")
        results["warnings"].append({
            "stage": "knowledge_graph",
            "error": str(exc),
            "impact": "Spatial relationships will not be extracted"
        })
    
    return results
```

---

## Future Extensibility

### Planned Enhancements

#### 1. Model Versioning and A/B Testing

**Capability:** Support multiple model versions with side-by-side comparison

```python
# Proposed configuration
models:
  - id: "yolov11m-v1"
    path: "/models/yolov11m-obb-v1.pt"
    weight: 0.8  # 80% of traffic
  - id: "yolov11m-v2"
    path: "/models/yolov11m-obb-v2.pt"
    weight: 0.2  # 20% of traffic (A/B test)

# Pseudocode for model selection
def select_model(models_config, job_id):
    """Select model based on configured weights."""
    import random
    random.seed(hash(job_id))
    rand_val = random.random()
    
    cumulative = 0
    for model in models_config:
        cumulative += model["weight"]
        if rand_val <= cumulative:
            return model
    
    return models_config[0]  # Fallback to first model
```

#### 2. Batch Processing Optimization

**Capability:** Process multiple images in batches for improved GPU utilization

```python
# Proposed batch processing
def run_batch_inference(images: list, model, batch_size=8):
    """Process images in batches for efficiency."""
    
    results = []
    for i in range(0, len(images), batch_size):
        batch = images[i:i + batch_size]
        batch_results = model.predict(batch, stream=False)
        results.extend(batch_results)
    
    return results
```

#### 3. Streaming Predictions

**Capability:** Stream predictions as they're generated instead of waiting for all images

```python
# Proposed streaming API
@app.get("/api/v1/jobs/{job_id}/stream")
async def stream_predictions(job_id: str):
    """Stream predictions as they're generated."""
    
    async def prediction_generator():
        job = load_job(job_id)
        output_dir = Path(job.results["output_directory"])
        predictions_dir = output_dir / "predictions" / "refined"
        
        seen_files = set()
        while True:
            # Check for new prediction files
            current_files = set(predictions_dir.glob("*.txt"))
            new_files = current_files - seen_files
            
            for file in new_files:
                predictions = parse_prediction_file(file)
                yield json.dumps({
                    "image": file.stem,
                    "predictions": predictions,
                    "timestamp": time.time()
                }) + "
"
                seen_files.add(file)
            
            # Check if job is complete
            if load_job(job_id).status == "completed":
                break
            
            await asyncio.sleep(1)
    
    return StreamingResponse(prediction_generator(), media_type="application/x-ndjson")
```

#### 4. Multi-Model Ensemble

**Capability:** Combine predictions from multiple models for improved accuracy

```python
# Proposed ensemble configuration
ensemble:
  models:
    - path: "/models/yolov11m.pt"
      weight: 0.5
    - path: "/models/yolov11x.pt"
      weight: 0.3
    - path: "/models/custom_model.pt"
      weight: 0.2
  fusion_strategy: "weighted_average"  # or "nms", "voting"

# Pseudocode for ensemble fusion
def fuse_predictions(predictions_list, weights, strategy="weighted_average"):
    """Fuse predictions from multiple models."""
    
    if strategy == "weighted_average":
        # Average confidence scores with model weights
        fused = []
        for bbox in align_bboxes(predictions_list):
            avg_conf = sum(p.conf * w for p, w in zip(bbox.preds, weights))
            fused.append(create_prediction(bbox.coords, avg_conf))
        return fused
    
    elif strategy == "nms":
        # Apply NMS across all model predictions
        all_preds = [p for preds in predictions_list for p in preds]
        return apply_nms(all_preds, iou_threshold=0.5)
    
    elif strategy == "voting":
        # Keep predictions agreed upon by majority
        return majority_vote(predictions_list, threshold=0.5)
```

#### 5. Active Learning Integration

**Capability:** Identify low-confidence predictions for human review and model improvement

```python
# Proposed active learning workflow
def identify_uncertain_predictions(predictions_dir: Path, confidence_threshold=0.7):
    """Identify predictions needing human review."""
    
    uncertain_cases = []
    
    for pred_file in predictions_dir.glob("*.txt"):
        predictions = parse_prediction_file(pred_file)
        
        low_confidence = [p for p in predictions if p["confidence"] < confidence_threshold]
        
        if low_confidence:
            uncertain_cases.append({
                "image": pred_file.stem,
                "uncertain_count": len(low_confidence),
                "predictions": low_confidence,
                "priority": 1.0 - min(p["confidence"] for p in low_confidence)
            })
    
    # Sort by priority (lowest confidence first)
    uncertain_cases.sort(key=lambda x: x["priority"], reverse=True)
    
    return uncertain_cases
```

#### 6. Distributed Processing

**Capability:** Distribute inference across multiple GPU nodes for horizontal scaling

```python
# Proposed distributed configuration
distributed:
  workers:
    - host: "gpu-node-1"
      gpu_id: 0
      capacity: 8  # Max concurrent jobs
    - host: "gpu-node-2"
      gpu_id: 0
      capacity: 8
  load_balancing: "least_loaded"  # or "round_robin", "weighted"

# Pseudocode for work distribution
def distribute_inference_job(images: list, workers_config):
    """Distribute images across available workers."""
    
    # Split images among workers based on capacity
    worker_assignments = []
    for i, worker in enumerate(workers_config):
        start = i * len(images) // len(workers_config)
        end = (i + 1) * len(images) // len(workers_config)
        worker_assignments.append({
            "worker": worker,
            "images": images[start:end]
        })
    
    # Submit jobs to workers
    futures = []
    for assignment in worker_assignments:
        future = submit_remote_job(
            assignment["worker"],
            assignment["images"]
        )
        futures.append(future)
    
    # Collect results
    results = []
    for future in futures:
        results.extend(future.result())
    
    return results
```

#### 7. Model Performance Monitoring

**Capability:** Track model drift and performance degradation over time

```python
# Proposed monitoring metrics
class ModelPerformanceMonitor:
    """Monitor model performance trends over time."""
    
    def __init__(self):
        self.metrics_history = []
    
    def record_inference(self, predictions: list, ground_truth: list = None):
        """Record inference metrics for monitoring."""
        
        metrics = {
            "timestamp": time.time(),
            "num_predictions": len(predictions),
            "avg_confidence": np.mean([p["confidence"] for p in predictions]),
            "confidence_distribution": self._compute_distribution(predictions),
        }
        
        if ground_truth:
            metrics["accuracy"] = self._compute_accuracy(predictions, ground_truth)
            metrics["mAP"] = self._compute_map(predictions, ground_truth)
        
        self.metrics_history.append(metrics)
        
        # Check for drift
        if self._detect_drift():
            alert_model_drift()
    
    def _detect_drift(self) -> bool:
        """Detect if model performance is degrading."""
        if len(self.metrics_history) < 100:
            return False
        
        recent = self.metrics_history[-20:]
        baseline = self.metrics_history[-100:-20]
        
        recent_conf = np.mean([m["avg_confidence"] for m in recent])
        baseline_conf = np.mean([m["avg_confidence"] for m in baseline])
        
        # Alert if average confidence dropped by >10%
        return (baseline_conf - recent_conf) / baseline_conf > 0.1
```

### Extension Points

The pipeline is designed with clear extension points for future enhancements:

1. **Custom Preprocessing**: Add image preprocessing hooks before inference
2. **Custom Post-processing**: Inject custom logic after predictions
3. **Custom Symbolic Rules**: Extend Prolog rule base with domain-specific knowledge
4. **Custom Metrics**: Add application-specific performance metrics
5. **Custom Visualizations**: Implement specialized visualization for specific domains
6. **Plugin Architecture**: Support third-party plugins for specialized processing

---

## Conclusion

This document provides a comprehensive guide for integrating the YOLO/SAHI object detection pipeline into automated backend workflows. The recommended architecture uses async task queues (Celery + Redis) for scalability, with clear extension points for future enhancements.

### Key Takeaways

1. **Modular Design**: Each pipeline stage can be invoked independently or as part of a complete workflow
2. **Multiple Integration Patterns**: Choose between subprocess, direct import, or async task queue based on your requirements
3. **Comprehensive Monitoring**: Prometheus metrics at every stage enable production monitoring
4. **Error Resilience**: Robust error handling with graceful degradation and retry mechanisms
5. **Future-Ready**: Clear extension points for A/B testing, distributed processing, and active learning

### Next Steps

1. **Review & Validate**: Have stakeholders review this integration design
2. **Prototype**: Implement a proof-of-concept using the recommended async task queue approach
3. **Performance Testing**: Benchmark throughput and latency under various loads
4. **Monitoring Setup**: Configure Prometheus and Grafana dashboards
5. **Production Deployment**: Roll out incrementally with monitoring and alerting

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** February 3, 2026
- **Status:** Design Specification (No Code Implementation)
- **Related Documents:**
  - [Backend API Architecture](backend_api_architecture.md)
  - [Backend API Workflows](backend_api_workflows.md)
  - [Frontend UI Design](frontend_ui_design.md)
  - [Main README](../../README.md)

**Feedback & Questions:**
For questions or feedback on this integration design, please create an issue in the GitHub repository referencing this document.
