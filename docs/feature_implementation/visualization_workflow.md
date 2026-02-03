# Visualization Workflow and Process Flow

## Overview

This document provides detailed workflow diagrams and process flows for the bounding box visualization system. It complements the main design document with step-by-step execution flows and decision trees.

---

## Table of Contents

1. [High-Level Pipeline](#high-level-pipeline)
2. [Detailed Process Flows](#detailed-process-flows)
3. [Format Detection and Parsing](#format-detection-and-parsing)
4. [Drawing and Rendering](#drawing-and-rendering)
5. [Batch Processing Workflow](#batch-processing-workflow)
6. [Error Recovery Flow](#error-recovery-flow)
7. [Integration with Existing Pipeline](#integration-with-existing-pipeline)

---

## 1. High-Level Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                  VISUALIZATION PIPELINE                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   START      │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────┐
│  Input Validation           │
│  - Check image exists       │
│  - Check prediction exists  │
│  - Validate file formats    │
└──────────┬──────────────────┘
           │
           ▼
     ┌─────────┐
     │ Valid?  │
     └────┬────┘
          │ No
          ├──────────► Log error and skip
          │ Yes
          ▼
┌─────────────────────────────┐
│  Load Input Image           │
│  - Open image file          │
│  - Convert to RGB           │
│  - Store dimensions         │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Parse Predictions          │
│  - Detect format (OBB/YOLO) │
│  - Parse each line          │
│  - Validate coordinates     │
└──────────┬──────────────────┘
           │
           ▼
     ┌──────────┐
     │ Empty?   │
     └────┬─────┘
          │ Yes
          ├──────────► Save original + warning
          │ No
          ▼
┌─────────────────────────────┐
│  Initialize Drawing Context │
│  - Create ImageDraw object  │
│  - Load font                │
│  - Prepare color mapping    │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Draw All Detections        │
│  (Loop for each detection)  │
│  - Draw bounding box        │
│  - Draw label + confidence  │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Save Output Image          │
│  - Create output directory  │
│  - Save with naming conv.   │
│  - Generate metadata (opt.) │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Log Statistics             │
│  - Number of detections     │
│  - Classes found            │
│  - Confidence ranges        │
└──────────┬──────────────────┘
           │
           ▼
     ┌──────────┐
     │   END    │
     └──────────┘
```

---

## 2. Detailed Process Flows

### 2.1 Input Validation Flow

```
START: validate_inputs(image_path, pred_path)
│
├─► Check image_path exists
│   ├─► No: Raise FileNotFoundError
│   └─► Yes: Continue
│
├─► Check image_path is file (not directory)
│   ├─► No: Raise ValueError("Expected file")
│   └─► Yes: Continue
│
├─► Check image extension
│   ├─► Not in [.png, .jpg, .jpeg]: Warning
│   └─► Valid: Continue
│
├─► Check pred_path exists
│   ├─► No: Raise FileNotFoundError
│   └─► Yes: Continue
│
├─► Check pred_path is .txt file
│   ├─► No: Raise ValueError("Expected .txt")
│   └─► Yes: Continue
│
└─► Return: (image_path, pred_path) validated

SUCCESS
```

### 2.2 Image Loading Flow

```
START: load_image(image_path)
│
├─► Try: Open image with PIL
│   ├─► Exception: Try with OpenCV
│   │   ├─► Exception: Raise RuntimeError
│   │   └─► Success: Convert BGR→RGB
│   └─► Success: Continue
│
├─► Check image mode
│   ├─► Mode = 'RGB': Continue
│   ├─► Mode = 'RGBA': Convert to RGB
│   ├─► Mode = 'L' (grayscale): Convert to RGB
│   └─► Other: Convert to RGB
│
├─► Validate image dimensions
│   ├─► Width or Height = 0: Raise ValueError
│   └─► Valid: Continue
│
├─► Store metadata
│   ├─► Width: img.size[0]
│   ├─► Height: img.size[1]
│   └─► Mode: img.mode
│
└─► Return: PIL Image object

SUCCESS
```

### 2.3 Prediction Parsing Flow

```
START: parse_predictions(pred_path)
│
├─► Initialize empty detection list
│
├─► Open prediction file
│   └─► Exception: Raise RuntimeError
│
├─► For each line in file:
│   │
│   ├─► Strip whitespace
│   │
│   ├─► Skip if empty line
│   │
│   ├─► Split by whitespace
│   │
│   ├─► Count parts
│   │   ├─► 10 parts: OBB format
│   │   ├─► 6 parts: YOLO format
│   │   └─► Other: Log warning, skip line
│   │
│   ├─► Parse based on format:
│   │   │
│   │   ├─► OBB Format:
│   │   │   ├─► parts[0]: class_name (string)
│   │   │   ├─► parts[1]: confidence (float)
│   │   │   └─► parts[2-9]: 8 coordinates (4 points)
│   │   │
│   │   └─► YOLO Format:
│   │       ├─► parts[0]: class_id (int)
│   │       ├─► parts[1-4]: cx, cy, w, h (float)
│   │       └─► parts[5]: confidence (float)
│   │
│   ├─► Validate parsed values:
│   │   ├─► Confidence in [0, 1]?
│   │   ├─► Coordinates valid numbers?
│   │   └─► All required fields present?
│   │
│   ├─► If valid: Add to detection list
│   └─► If invalid: Log warning, skip
│
└─► Return: List of detection dicts

SUCCESS
```

---

## 3. Format Detection and Parsing

### 3.1 Format Detection Decision Tree

```
                    ┌─────────────────┐
                    │  Read Line      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Split by space  │
                    │ Count parts     │
                    └────────┬────────┘
                             │
                  ┌──────────┴──────────┐
                  │                     │
                  ▼                     ▼
         ┌────────────────┐    ┌────────────────┐
         │  10 parts?     │    │   6 parts?     │
         └────┬───────────┘    └────┬───────────┘
              │ Yes                 │ Yes
              ▼                     ▼
    ┌──────────────────┐   ┌──────────────────┐
    │ parts[0] string? │   │ parts[0] digit?  │
    └──────┬───────────┘   └──────┬───────────┘
           │ Yes                  │ Yes
           ▼                      ▼
    ┌──────────────┐       ┌──────────────┐
    │ OBB FORMAT   │       │ YOLO FORMAT  │
    └──────────────┘       └──────────────┘
           │                      │
           └──────────┬───────────┘
                      │
                      ▼
            ┌──────────────────┐
            │ Parse accordingly │
            └──────────────────┘
```

### 3.2 OBB Parsing State Machine

```
State 0: Initial
│
├─► Read class_name (string)
│   └─► Validate: Non-empty string
│       └─► SUCCESS → State 1
│
State 1: Class read
│
├─► Read confidence (float)
│   └─► Validate: 0.0 ≤ value ≤ 1.0
│       └─► SUCCESS → State 2
│
State 2: Confidence read
│
├─► Read 8 coordinates (x1,y1,x2,y2,x3,y3,x4,y4)
│   └─► Validate: All are valid floats
│       └─► SUCCESS → State 3
│
State 3: Complete
│
└─► Create detection dict:
    {
        'class_name': str,
        'confidence': float,
        'polygon': [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
    }
    └─► Return detection

DONE
```

### 3.3 YOLO Format Conversion

```
Input: [class_id, cx, cy, w, h, confidence]
Image dimensions: (img_width, img_height)

┌────────────────────────────────────┐
│ Step 1: Denormalize center coords │
└────────────┬───────────────────────┘
             │
             ├─► cx_px = cx * img_width
             └─► cy_px = cy * img_height
             │
             ▼
┌────────────────────────────────────┐
│ Step 2: Denormalize dimensions    │
└────────────┬───────────────────────┘
             │
             ├─► w_px = w * img_width
             └─► h_px = h * img_height
             │
             ▼
┌────────────────────────────────────┐
│ Step 3: Calculate corners         │
└────────────┬───────────────────────┘
             │
             ├─► x_min = cx_px - w_px/2
             ├─► y_min = cy_px - h_px/2
             ├─► x_max = cx_px + w_px/2
             └─► y_max = cy_px + h_px/2
             │
             ▼
┌────────────────────────────────────┐
│ Step 4: Form axis-aligned bbox    │
└────────────┬───────────────────────┘
             │
             └─► bbox = [x_min, y_min, x_max, y_max]

Output: Pixel coordinates ready for drawing
```

---

## 4. Drawing and Rendering

### 4.1 Single Detection Drawing Flow

```
START: draw_detection(draw, detection, font, cache)
│
├─► Get class color
│   ├─► Check color cache
│   ├─► If not cached: Generate color
│   └─► Store in cache
│
├─► Extract polygon/bbox from detection
│
├─► Validate coordinates
│   ├─► Check within image bounds
│   ├─► If out of bounds: Clip coordinates
│   └─► Log warning if clipped
│
├─► Draw bounding box
│   ├─► OBB: draw.polygon(points, outline, width)
│   └─► AABB: draw.rectangle(bbox, outline, width)
│
├─► Prepare label text
│   └─► Format: "{class_name} {confidence:.2f}"
│
├─► Calculate label position
│   ├─► Get top-left of bbox
│   ├─► Check space above bbox
│   ├─► If space: Place above
│   └─► Else: Place inside/below
│
├─► Draw label background
│   ├─► Get text bounding box
│   ├─► Add padding
│   └─► Draw filled rectangle
│
├─► Draw label text
│   └─► draw.text(position, text, color, font)
│
└─► Return: Drawing updated

DONE
```

### 4.2 Batch Drawing Optimization

```
START: draw_all_detections(image, detections)
│
├─► Sort detections by confidence (descending)
│   └─► Reason: Draw high-conf boxes on top
│
├─► Initialize drawing context
│   ├─► Create ImageDraw object
│   ├─► Load/cache font
│   └─► Initialize color cache
│
├─► Group by class (optional)
│   └─► For efficient color lookup
│
├─► For each detection (sorted order):
│   │
│   ├─► Draw bounding box
│   │   └─► Use cached color
│   │
│   └─► Draw label
│       └─► Use cached font
│
└─► Return: Annotated image

DONE
```

### 4.3 Label Placement Strategy

```
Given: polygon/bbox, image dimensions

┌───────────────────────────────────┐
│ Find top-most point of bbox       │
├─► min_y = min(y for all points)  │
└────────────┬──────────────────────┘
             │
             ▼
┌───────────────────────────────────┐
│ Check available space             │
└────────────┬──────────────────────┘
             │
      ┌──────┴───────┐
      │              │
      ▼              ▼
┌──────────┐   ┌──────────┐
│ min_y    │   │ min_y    │
│ > 25px?  │   │ ≤ 25px?  │
└────┬─────┘   └────┬─────┘
     │ Yes          │
     ▼              ▼
┌──────────┐   ┌──────────┐
│ ABOVE    │   │ INSIDE   │
│ BBOX     │   │ BBOX     │
└────┬─────┘   └────┬─────┘
     │              │
     └──────┬───────┘
            │
            ▼
    ┌──────────────┐
    │ Calculate    │
    │ position (x,y)│
    └──────────────┘
```

---

## 5. Batch Processing Workflow

### 5.1 Sequential Processing

```
START: batch_visualize(images_dir, preds_dir, output_dir)
│
├─► Scan prediction directory
│   └─► Find all .txt files
│
├─► Initialize counters
│   ├─► total = 0
│   ├─► success = 0
│   └─► errors = 0
│
├─► For each prediction file:
│   │
│   ├─► total += 1
│   │
│   ├─► Find matching image
│   │   ├─► Try: {stem}og.png
│   │   ├─► Try: {stem}.png
│   │   └─► Try: {stem}.jpg
│   │
│   ├─► If image not found:
│   │   ├─► errors += 1
│   │   └─► Continue to next
│   │
│   ├─► Generate output path
│   │   └─► {output_dir}/{stem}pred.png
│   │
│   ├─► Try: Visualize
│   │   ├─► Success: success += 1
│   │   └─► Error: errors += 1, log error
│   │
│   └─► Progress: Print status
│
├─► Print summary
│   ├─► Total: {total}
│   ├─► Success: {success}
│   └─► Errors: {errors}
│
└─► Return: Summary dict

DONE
```

### 5.2 Parallel Processing

```
START: parallel_batch_visualize(preds_dir, images_dir, output_dir, workers)
│
├─► Scan prediction directory
│   └─► Get list of all .txt files
│
├─► Split files into chunks
│   └─► chunk_size = len(files) / workers
│
├─► Create process pool
│   └─► Pool(processes=workers)
│
├─► Map process_single_image to chunks
│   │
│   │   ┌───────────────────────────────┐
│   │   │  Worker Process 1             │
│   ├──►│  - Process chunk 1            │
│   │   │  - Return results             │
│   │   └───────────────────────────────┘
│   │
│   │   ┌───────────────────────────────┐
│   │   │  Worker Process 2             │
│   ├──►│  - Process chunk 2            │
│   │   │  - Return results             │
│   │   └───────────────────────────────┘
│   │
│   │   ┌───────────────────────────────┐
│   │   │  Worker Process N             │
│   └──►│  - Process chunk N            │
│       │  - Return results             │
│       └───────────────────────────────┘
│
├─► Collect all results
│
├─► Aggregate statistics
│
└─► Return: Combined results

DONE
```

---

## 6. Error Recovery Flow

### 6.1 File-Level Error Handling

```
                    ┌──────────────────┐
                    │  Try Process     │
                    │  Image           │
                    └────────┬─────────┘
                             │
                ┌────────────┴─────────────┐
                │                          │
                ▼                          ▼
        ┌───────────────┐          ┌──────────────┐
        │  SUCCESS      │          │  EXCEPTION   │
        └───────┬───────┘          └──────┬───────┘
                │                         │
                │                         ▼
                │                 ┌───────────────┐
                │                 │ Type of Error?│
                │                 └───────┬───────┘
                │                         │
                │         ┌───────────────┼───────────────┐
                │         │               │               │
                │         ▼               ▼               ▼
                │   ┌─────────┐    ┌──────────┐   ┌──────────┐
                │   │File Not │    │  Image   │   │ Parse    │
                │   │ Found   │    │  Error   │   │  Error   │
                │   └────┬────┘    └────┬─────┘   └────┬─────┘
                │        │              │              │
                │        ▼              ▼              ▼
                │   ┌─────────┐    ┌──────────┐   ┌──────────┐
                │   │Log+Skip │    │Log+Skip  │   │Log+Skip  │
                │   └─────────┘    └──────────┘   └──────────┘
                │        │              │              │
                └────────┴──────────────┴──────────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │  Continue with  │
                          │  next file      │
                          └─────────────────┘
```

### 6.2 Line-Level Error Handling

```
During prediction parsing:

┌──────────────────────────────┐
│  Read line from file         │
└───────────┬──────────────────┘
            │
            ▼
┌──────────────────────────────┐
│  Try: Parse line             │
└───────────┬──────────────────┘
            │
     ┌──────┴───────┐
     │              │
     ▼              ▼
┌─────────┐   ┌─────────────┐
│SUCCESS  │   │  EXCEPTION  │
└────┬────┘   └──────┬──────┘
     │               │
     │               ▼
     │        ┌──────────────────┐
     │        │ Identify error:  │
     │        │ - ValueError     │
     │        │ - IndexError     │
     │        │ - TypeError      │
     │        └────────┬─────────┘
     │                 │
     │                 ▼
     │        ┌──────────────────┐
     │        │ Log warning:     │
     │        │ "Line X invalid" │
     │        │ Include line text│
     │        └────────┬─────────┘
     │                 │
     │                 ▼
     │        ┌──────────────────┐
     │        │ Skip this line   │
     │        │ Continue to next │
     │        └────────┬─────────┘
     │                 │
     └─────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Process next line│
              └─────────────────┘
```

---

## 7. Integration with Existing Pipeline

### 7.1 Pipeline Integration Points

```
┌────────────────────────────────────────────────────────┐
│           NEUROSYMBOLIC DETECTION PIPELINE             │
└────────────────────────────────────────────────────────┘

┌──────────────────┐
│  1. Training     │
│  (YOLOv11-OBB)   │
└────────┬─────────┘
         │ Produces: Model weights
         ▼
┌──────────────────┐
│  2. Inference    │
│  (SAHI Predict)  │
└────────┬─────────┘
         │ Produces: Predictions (.txt)
         │
         ├──────────────────────────────┐
         │                              │
         ▼                              ▼
┌──────────────────┐          ┌────────────────────┐
│ 3a. Symbolic     │          │ 3b. VISUALIZATION  │◄── NEW
│     Reasoning    │          │     (This doc)     │
│  - NMS filter    │          │  - Read preds      │
│  - Prolog rules  │          │  - Draw boxes      │
└────────┬─────────┘          │  - Add labels      │
         │                    └────────┬───────────┘
         │ Produces: Refined preds    │ Produces: Annotated images
         │                            │
         ▼                            ▼
┌──────────────────┐          ┌────────────────────┐
│ 4. Evaluation    │          │ Visual Outputs     │
│  (mAP metrics)   │          │  - P0006pred.png   │
└──────────────────┘          │  - Report images   │
                              └────────────────────┘
```

### 7.2 File Flow Integration

```
Data Flow:

Original Images:
  data/images/val/P0006og.png
           │
           ├─────────────────────┐
           │                     │
           ▼                     ▼
    [SAHI Inference]      [Visualization Input]
           │
           ▼
Predictions:
  predictions/raw/P0006.txt
           │
           ├─────────────────────┐
           │                     │
           ▼                     ▼
  [NMS + Symbolic]        [Visualization Input]
           │
           ▼
Refined Predictions:
  predictions/refined/P0006.txt
           │
           ├─────────────────────┐
           │                     │
           ▼                     ▼
   [Evaluation]          [Visualization Input]
                                 │
                                 ▼
                        Visualized Outputs:
                          visualizations/P0006pred.png
```

### 7.3 Configuration Integration

```yaml
# shared/configs/pipeline_local.yaml

# Existing configuration
raw_predictions_dir: /path/to/predictions/raw
nms_predictions_dir: /path/to/predictions/nms
refined_predictions_dir: /path/to/predictions/refined
ground_truth_dir: /path/to/data/labels/val

# NEW: Visualization configuration
visualization:
  enabled: true
  input_images_dir: /path/to/data/images/val
  output_dir: /path/to/visualizations
  
  # Which predictions to visualize
  visualize_stages:
    - raw          # Visualize raw predictions
    - nms          # Visualize after NMS
    - refined      # Visualize after symbolic reasoning
    - ground_truth # Visualize ground truth labels
  
  # Visual settings
  color_scheme: per_class
  show_confidence: true
  confidence_decimals: 2
  bbox_line_width: 2
  label_font_size: 14
  
  # Output settings
  output_format: png
  output_quality: 95
  create_comparison: true  # Side-by-side before/after
```

### 7.4 CLI Integration

```bash
# Existing pipeline usage
python -m pipeline.core.run_pipeline --config shared/configs/pipeline_local.yaml

# NEW: Add visualization stage
python -m pipeline.core.run_pipeline \
    --config shared/configs/pipeline_local.yaml \
    --enable-visualization \
    --viz-output visualizations/

# OR: Standalone visualization tool
python -m pipeline.core.visualize \
    --images-dir data/images/val \
    --predictions-dir predictions/refined \
    --output-dir visualizations/refined \
    --config shared/configs/visualization.yaml
```

---

## 8. Example Workflows

### 8.1 Complete End-to-End Example

```
USER WORKFLOW:

1. Train model:
   $ python pipeline/training/training.py --config shared/configs/training_local.yaml
   → Produces: artifacts/best.pt

2. Run SAHI inference:
   $ python pipeline/inference/sahi_yolo_prediction.py \
       --config shared/configs/prediction_local.yaml
   → Produces: predictions/*.txt files

3. Run symbolic pipeline:
   $ python -m pipeline.core.run_pipeline \
       --config shared/configs/pipeline_local.yaml
   → Produces: predictions/refined/*.txt files

4. Visualize predictions (NEW):
   $ python -m pipeline.core.visualize \
       --images-dir data/images/val \
       --predictions-dir predictions/refined \
       --output-dir visualizations
   → Produces: visualizations/*pred.png files

5. Review visualizations:
   $ ls visualizations/
   P0006pred.png
   P0007pred.png
   ...
```

### 8.2 Quick Visualization Only

```
# For users who already have predictions and just want to visualize:

$ python -m pipeline.core.visualize \
    --images-dir data/images/val \
    --predictions-dir predictions/raw \
    --output-dir viz_raw \
    --color-scheme per_class \
    --show-confidence

# Batch process entire directory
$ python -m pipeline.core.visualize \
    --batch \
    --workers 4 \
    --images-dir data/images/val \
    --predictions-dir predictions/ \
    --output-dir visualizations/
```

### 8.3 Comparison Workflow

```
# Generate side-by-side comparison of predictions vs ground truth

$ python -m pipeline.core.visualize_compare \
    --images-dir data/images/val \
    --predictions-dir predictions/refined \
    --ground-truth-dir data/labels/val \
    --output-dir visualizations/comparison \
    --layout side-by-side

Result: visualizations/comparison/P0006_compare.png
        [Original] | [Predictions] | [Ground Truth]
```

---

## Summary

This workflow document provides:

1. **Visual Process Flows**: Clear diagrams showing step-by-step execution
2. **Decision Trees**: Logic for format detection and error handling
3. **Integration Points**: How visualization fits into existing pipeline
4. **Practical Examples**: Real-world usage patterns and commands

These workflows complement the main design document and provide actionable guidance for implementation.

---

## Next Steps

1. Implement core visualization functions following these flows
2. Add CLI interface matching the integration examples
3. Test with sample images from pipeline/sample/
4. Create integration tests for each workflow
5. Document any deviations or improvements made during implementation
