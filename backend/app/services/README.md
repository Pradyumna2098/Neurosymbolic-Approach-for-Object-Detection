# Storage Service Documentation

## Overview

The `StorageService` provides file validation, storage management, and job tracking for the neurosymbolic object detection system. It uses local filesystem storage with organized directory structures and UUID-based file identification.

## Key Features

✅ **File Validation** - Validates images using PIL/Pillow  
✅ **Format Support** - JPEG, PNG, TIFF  
✅ **Size Limits** - 1KB minimum, 50MB maximum  
✅ **Dimension Checks** - 64x64 minimum, 8192x8192 maximum  
✅ **UUID File IDs** - Unique file identification  
✅ **Job Tracking** - JSON-based job status management  
✅ **Staged Results** - Separate storage for raw/NMS/refined predictions  
✅ **Directory Organization** - Job-specific subdirectories

## Directory Structure

```
data/
├── uploads/{job_id}/           # Input images
├── jobs/{job_id}.json          # Job metadata and status
├── results/{job_id}/           # Predictions
│   ├── raw/                    # Raw YOLO predictions
│   ├── nms/                    # After NMS filtering
│   └── refined/                # After symbolic reasoning
└── visualizations/{job_id}/    # Annotated images
```

## Job JSON Schema

Each job is stored as a JSON file with the following structure:

```json
{
  "job_id": "uuid",
  "status": "queued|processing|completed|failed",
  "created_at": "ISO 8601 timestamp",
  "updated_at": "ISO 8601 timestamp",
  "config": {
    "model": "yolov11m-obb",
    "confidence_threshold": 0.25
  },
  "files": [
    {
      "file_id": "uuid",
      "filename": "original.png",
      "stored_filename": "uuid.png",
      "size_bytes": 12345,
      "uploaded_at": "ISO 8601 timestamp",
      "metadata": {
        "width": 800,
        "height": 600,
        "format": "PNG",
        "mode": "RGB",
        "size_bytes": 12345
      }
    }
  ],
  "progress": {
    "stage": "nms",
    "percent": 50
  },
  "error": null
}
```

## Usage Examples

### Import the Service

```python
from app.services.storage import StorageService, FileValidationError

service = StorageService()
```

### Create a Job

```python
job_id = service.create_job(config={
    "model": "yolov11m-obb",
    "confidence_threshold": 0.25,
    "iou_threshold": 0.45
})
print(f"Created job: {job_id}")
```

### Upload and Validate an Image

```python
with open("image.png", "rb") as f:
    content = f.read()

try:
    file_id, file_path, metadata = service.save_upload(
        job_id, 
        "image.png", 
        content, 
        validate=True
    )
    print(f"File uploaded: {file_id}")
    print(f"Metadata: {metadata}")
except FileValidationError as e:
    print(f"Validation failed: {e}")
```

### Update Job Status

```python
# Update to processing
service.update_job(
    job_id, 
    status="processing",
    progress={"stage": "inference", "percent": 25}
)

# Mark as completed
service.update_job(
    job_id,
    status="completed",
    progress={"stage": "done", "percent": 100}
)

# Mark as failed with error
service.update_job(
    job_id,
    status="failed",
    error="Model failed to load"
)
```

### Save Predictions at Different Stages

```python
# Raw predictions from YOLO
raw_predictions = {
    "detections": [...],
    "num_detections": 10
}
service.save_result(job_id, raw_predictions, stage="raw")

# After NMS filtering
nms_predictions = {
    "detections": [...],
    "num_detections": 8
}
service.save_result(job_id, nms_predictions, stage="nms")

# After symbolic reasoning
refined_predictions = {
    "detections": [...],
    "num_detections": 8
}
service.save_result(job_id, refined_predictions, stage="refined")
```

### Retrieve Results

```python
# Get refined results (default)
results = service.get_result(job_id)

# Get results from specific stage
raw_results = service.get_result(job_id, stage="raw")
nms_results = service.get_result(job_id, stage="nms")
```

### Save and Retrieve Visualizations

```python
# Save annotated image
with open("annotated.png", "rb") as f:
    viz_data = f.read()

service.save_visualization(job_id, viz_data, filename="annotated.png")

# Get visualization path
viz_path = service.get_visualization_path(job_id, filename="annotated.png")
if viz_path:
    print(f"Visualization at: {viz_path}")
```

### List Files in a Job

```python
files = service.list_job_files(job_id)
for file_info in files:
    print(f"{file_info['filename']} ({file_info['size_bytes']} bytes)")
```

### Retrieve File by ID

```python
file_path = service.get_upload_path(job_id, file_id)
if file_path:
    with open(file_path, "rb") as f:
        content = f.read()
```

## File Validation

The service validates images using PIL/Pillow with the following rules:

### Supported Formats
- **JPEG** (.jpg, .jpeg)
- **PNG** (.png)
- **TIFF** (.tiff, .tif)

### Size Constraints
- **Minimum:** 1KB
- **Maximum:** 50MB

### Dimension Constraints
- **Minimum:** 64×64 pixels
- **Maximum:** 8192×8192 pixels

### Validation Checks
1. ✓ File extension matches supported formats
2. ✓ File size within limits
3. ✓ Image can be opened and decoded (corruption check)
4. ✓ Image dimensions within limits
5. ✓ File header matches extension (format verification)

### Validation Error Codes

| Error Code | Description |
|------------|-------------|
| `INVALID_FORMAT` | Unsupported format or format mismatch |
| `FILE_TOO_SMALL` | File smaller than 1KB |
| `FILE_TOO_LARGE` | File exceeds 50MB limit |
| `DIMENSIONS_TOO_SMALL` | Image dimensions below 64×64 |
| `DIMENSIONS_EXCEEDED` | Image dimensions exceed 8192×8192 |
| `CORRUPTED_FILE` | Image file is corrupted or unreadable |

## API Reference

### StorageService Class

#### Job Management

**`create_job(config: Optional[Dict] = None) -> str`**
- Creates a new job with unique ID
- Returns: Job ID (UUID)

**`get_job(job_id: str) -> Optional[Dict]`**
- Retrieves job data by ID
- Returns: Job data dict or None if not found

**`update_job(job_id: str, status: Optional[str] = None, progress: Optional[Dict] = None, error: Optional[str] = None, **kwargs) -> bool`**
- Updates job data
- Returns: True if successful, False if job not found

**`list_jobs(limit: int = 100) -> List[Dict]`**
- Lists all jobs sorted by creation time
- Returns: List of job data dicts

#### File Management

**`validate_image_file(content: bytes, filename: str) -> Tuple[bool, Optional[str], Optional[Dict]]`**
- Validates image file
- Returns: (is_valid, error_message, metadata)

**`save_upload(job_id: str, filename: str, content: bytes, validate: bool = True) -> Tuple[str, Path, Optional[Dict]]`**
- Saves uploaded file with optional validation
- Returns: (file_id, file_path, metadata)
- Raises: FileValidationError if validation fails

**`get_upload_path(job_id: str, file_id: str) -> Optional[Path]`**
- Gets path to uploaded file
- Returns: Path or None if not found

**`list_job_files(job_id: str) -> List[Dict]`**
- Lists all files for a job
- Returns: List of file info dicts

#### Results Management

**`save_result(job_id: str, result_data: Dict, stage: str = "raw") -> Path`**
- Saves prediction results for a stage
- Returns: Path to saved results file

**`get_result(job_id: str, stage: str = "refined") -> Optional[Dict]`**
- Retrieves prediction results
- Returns: Results dict or None if not found

#### Visualization Management

**`save_visualization(job_id: str, image_data: bytes, filename: str = "annotated.png") -> Path`**
- Saves visualization image
- Returns: Path to saved visualization

**`get_visualization_path(job_id: str, filename: str = "annotated.png") -> Optional[Path]`**
- Gets path to visualization
- Returns: Path or None if not found

## Testing

Run the test suite:

```bash
pytest tests/backend/test_storage_service.py -v
```

Run the demonstration script:

```bash
cd backend
python demo_storage.py
```

## Integration with FastAPI

The storage service can be used in FastAPI endpoints:

```python
from fastapi import FastAPI, UploadFile, HTTPException, Path as FastAPIPath
from app.services.storage import storage_service, FileValidationError

app = FastAPI()

@app.post("/jobs")
async def create_job():
    job_id = storage_service.create_job()
    return {"job_id": job_id}

@app.post("/jobs/{job_id}/upload")
async def upload_file(
    job_id: str = FastAPIPath(..., regex=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'),
    file: UploadFile = None
):
    """Upload file for a job. job_id must be a valid UUID to prevent path traversal."""
    content = await file.read()
    
    try:
        file_id, _, metadata = storage_service.save_upload(
            job_id, file.filename, content, validate=True
        )
        return {"file_id": file_id, "metadata": metadata}
    except FileValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        # Catches invalid job_id or filename
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/jobs/{job_id}")
async def get_job(
    job_id: str = FastAPIPath(..., regex=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
):
    """Get job details. job_id must be a valid UUID to prevent path traversal."""
    try:
        job = storage_service.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**Security Note:** Always validate `job_id` as a strict UUID using FastAPI's path regex validation
or Pydantic validators to prevent path traversal attacks. The storage service validates internally,
but API layer validation provides defense in depth.

## Notes

- This is a **prototype implementation** using local filesystem storage
- Production deployments should consider using:
  - PostgreSQL for job metadata
  - S3/MinIO for file storage
  - Redis for caching
- The service is thread-safe for read operations
- Write operations should be synchronized in multi-worker deployments

---

# Symbolic Reasoning Service Documentation

## Overview

The `SymbolicReasoningService` provides Prolog-based confidence adjustment for object detection predictions using domain knowledge rules. It implements Stage 2b of the neurosymbolic pipeline, applying symbolic reasoning to refine predictions based on spatial relationships between detected objects.

## Key Features

✅ **Prolog Integration** - PySwip interface to SWI-Prolog  
✅ **Rule-Based Reasoning** - Load custom Prolog rules for confidence adjustment  
✅ **Spatial Awareness** - Considers object proximity and overlap  
✅ **Confidence Boost** - Increases confidence for positive co-occurrences  
✅ **Confidence Penalty** - Decreases confidence for implausible combinations  
✅ **Explainability** - Generates CSV reports documenting all adjustments  
✅ **Optional Stage** - Can be disabled without affecting other stages  
✅ **Error Handling** - Graceful degradation when Prolog is unavailable

## How It Works

### 1. Load Prolog Rules

The service loads confidence modifier rules from a Prolog file:

```prolog
% Positive co-occurrence (boost confidence)
confidence_modifier(ship, harbor, 1.25).
confidence_modifier(harbor, ship, 1.25).

% Implausible combination (penalize confidence)
confidence_modifier(plane, harbor, 0.2).
confidence_modifier(harbor, plane, 0.2).
```

### 2. Apply Spatial Reasoning

For each pair of detected objects:

**Boost Logic (weight > 1.0):**
- Objects must be nearby (distance < 2× average diagonal)
- Both confidences multiplied by weight
- Example: ship + harbor → both boosted by 1.25×

**Penalty Logic (weight < 1.0):**
- Objects must significantly overlap (IoU > 50% of smaller box)
- Lower confidence object penalized
- Example: plane + harbor overlap → harbor (lower conf) × 0.2

### 3. Save Results

- Refined predictions saved to `data/results/{job_id}/refined/`
- Explainability report saved to `data/results/{job_id}/symbolic_reasoning_report.csv`

## Usage Examples

### Basic Usage

```python
from app.services.symbolic import symbolic_reasoning_service
from pathlib import Path

# Apply symbolic reasoning to a job
stats = symbolic_reasoning_service.apply_symbolic_reasoning(
    job_id="abc-123",
    rules_file=Path("pipeline/prolog/rules.pl"),
    storage_service=storage_service
)

print(f"Processed {stats['total_images']} images")
print(f"Applied {stats['total_adjustments']} confidence adjustments")
```

### With Custom Rules

```python
# Create custom rules file
custom_rules = Path("custom_rules.pl")
custom_rules.write_text("""
% Custom domain rules
confidence_modifier(car, road, 1.3).
confidence_modifier(person, car, 1.2).
confidence_modifier(boat, road, 0.1).
""")

# Apply with custom rules
stats = symbolic_reasoning_service.apply_symbolic_reasoning(
    job_id="abc-123",
    rules_file=custom_rules
)
```

### Integration with Inference Pipeline

The service integrates automatically with the inference pipeline:

```python
from app.services.inference import inference_service
from app.services.storage import storage_service

# Run inference with symbolic reasoning enabled
inference_stats = inference_service.run_inference(
    job_id="abc-123",
    model_path="/path/to/model.pt",
    confidence_threshold=0.25,
    iou_threshold=0.45,
    sahi_config={
        'slice_width': 640,
        'slice_height': 640,
        'overlap_ratio': 0.2,
    },
    storage_service=storage_service,
    symbolic_config={
        'enabled': True,  # Enable symbolic reasoning
        'rules_file': 'pipeline/prolog/rules.pl'
    }
)

# Check symbolic reasoning stats
symbolic_stats = inference_stats.get('symbolic_reasoning', {})
print(f"Adjustments: {symbolic_stats.get('total_adjustments', 0)}")
```

### Via REST API

Enable symbolic reasoning in prediction request:

```python
import requests

response = requests.post("http://localhost:8000/api/v1/predict", json={
    "job_id": "abc-123",
    "config": {
        "model_path": "/path/to/model.pt",
        "confidence_threshold": 0.25,
        "iou_threshold": 0.45,
        "sahi": {
            "enabled": True,
            "slice_width": 640,
            "slice_height": 640,
            "overlap_ratio": 0.2
        },
        "symbolic_reasoning": {
            "enabled": True,  # Enable symbolic reasoning
            "rules_file": "pipeline/prolog/rules.pl"  # Optional
        }
    }
})
```

## Configuration

### Default Configuration

```python
symbolic_config = {
    'enabled': True,                        # Enable/disable stage
    'rules_file': 'pipeline/prolog/rules.pl'  # Path to Prolog rules
}
```

### Custom Class Mapping

```python
custom_class_map = {
    0: "car",
    1: "person",
    2: "bike",
    3: "truck"
}

stats = symbolic_reasoning_service.apply_symbolic_reasoning(
    job_id="abc-123",
    class_map=custom_class_map
)
```

## Explainability Report

The service generates a CSV report documenting all confidence adjustments:

```csv
image_name,action,rule_pair,object_1,conf_1_before,conf_1_after,object_2,conf_2_before,conf_2_after,suppressed_object,kept_object,kept_object_conf
image001.png,BOOST,ship<->harbor,ship,0.70,0.88,harbor,0.60,0.75,,,
image002.png,PENALTY,plane<->harbor,plane,0.90,0.90,harbor,0.30,0.06,harbor,plane,0.90
```

**Report Fields:**
- `image_name`: Image file name
- `action`: BOOST or PENALTY
- `rule_pair`: Classes involved in the rule
- `object_1`, `object_2`: Class names
- `conf_*_before`, `conf_*_after`: Confidence values before/after adjustment
- `suppressed_object`, `kept_object`: For penalties, which object was penalized

## Prolog Rules Format

### Rule Structure

```prolog
% confidence_modifier(ClassA, ClassB, Weight).
confidence_modifier(ship, harbor, 1.25).  % Boost: weight > 1.0
confidence_modifier(plane, harbor, 0.2).   % Penalty: weight < 1.0
```

### Rule Types

**1. Fixed Rules:**
```prolog
confidence_modifier(ship, harbor, 1.25).
confidence_modifier(large_vehicle, small_vehicle, 1.15).
```

**2. Category-Based Rules:**
```prolog
% Define categories
vehicle(plane).
vehicle(ship).
infrastructure(harbor).

% Apply to all in category
confidence_modifier(V, Infra, 0.5) :-
    vehicle(V),
    infrastructure(Infra).
```

### Default Rules (DOTA Dataset)

The service includes default rules for the DOTA aerial object detection dataset:

**Positive Co-occurrences (Boost):**
- ship + harbor (1.25×)
- helicopter + ship (1.20×)
- large_vehicle + small_vehicle (1.15×)
- sports facilities together (1.10×)

**Implausible Combinations (Penalty):**
- ship + bridge (0.1×)
- ship + roundabout (0.1×)
- plane + harbor (0.2×)
- plane + bridge (0.2×)
- vehicles + sports facilities (0.5×)

## API Reference

### SymbolicReasoningService Class

#### Main Method

**`apply_symbolic_reasoning(job_id: str, rules_file: Optional[Path] = None, class_map: Optional[Dict[int, str]] = None, storage_service: Any = None) -> Dict[str, Any]`**

Apply Prolog-based symbolic reasoning to NMS-filtered predictions.

**Parameters:**
- `job_id`: Job identifier
- `rules_file`: Path to Prolog rules file (default: `pipeline/prolog/rules.pl`)
- `class_map`: Class ID to name mapping (default: DOTA classes)
- `storage_service`: Storage service for job updates

**Returns:**
Dictionary with statistics:
```python
{
    'total_images': 10,
    'refined_images': 10,
    'total_adjustments': 25,
    'modifier_rules_loaded': 12,
    'elapsed_time_seconds': 0.45
}
```

**Raises:**
- `SymbolicReasoningError`: If processing fails

#### Internal Methods

**`_load_prolog_engine(rules_file: Path) -> Any`**
- Loads Prolog engine and consults rules file
- Returns initialized Prolog engine

**`_load_modifier_map(prolog_engine: Any) -> Dict[Tuple[str, str], float]`**
- Extracts modifier rules from Prolog
- Returns mapping of (class_a, class_b) to weight

**`_parse_predictions(predictions_dir: Path) -> Dict[str, List[Dict]]`**
- Loads YOLO-format predictions from directory
- Returns mapping of image names to predictions

**`_apply_modifiers(objects: List[Dict], modifier_map: Dict, class_map: Dict) -> Tuple[List[Dict], List[Dict]]`**
- Applies confidence modifiers to objects
- Returns (modified_objects, explainability_log)

**`_save_predictions(predictions: Dict, output_dir: Path) -> None`**
- Saves refined predictions in YOLO format

**`_save_explainability_report(report: List[Dict], report_file: Path) -> None`**
- Saves CSV report of confidence adjustments

## Error Handling

The service handles errors gracefully:

### Prolog Not Available

```python
# Service logs warning and skips processing
stats = symbolic_reasoning_service.apply_symbolic_reasoning(job_id="abc-123")
# Returns: {'skipped': True, 'reason': 'PySwip not installed'}
```

### Missing Rules File

```python
stats = symbolic_reasoning_service.apply_symbolic_reasoning(
    job_id="abc-123",
    rules_file=Path("/nonexistent/rules.pl")
)
# Returns: {'skipped': True, 'reason': 'Rules file not found'}
```

### No Modifier Rules

```python
# Rules file exists but has no confidence_modifier facts
stats = symbolic_reasoning_service.apply_symbolic_reasoning(job_id="abc-123")
# Returns: {'skipped': True, 'reason': 'No modifier rules found'}
```

### Integration with Pipeline

```python
# Symbolic reasoning errors don't fail the entire inference job
inference_stats = inference_service.run_inference(...)
symbolic_stats = inference_stats.get('symbolic_reasoning', {})

if symbolic_stats.get('skipped'):
    print(f"Symbolic reasoning skipped: {symbolic_stats['reason']}")
else:
    print(f"Applied {symbolic_stats['total_adjustments']} adjustments")
```

## Testing

Run the test suite:

```bash
# Run all symbolic reasoning tests
pytest tests/backend/test_symbolic_service.py -v

# Run specific test
pytest tests/backend/test_symbolic_service.py::TestSymbolicReasoningService::test_apply_modifiers_boost -v

# Skip tests requiring real Prolog
pytest tests/backend/test_symbolic_service.py -v -k "not real_prolog"
```

## Dependencies

### Required
- **PySwip** (>=0.2.10): Python-SWI-Prolog bridge
- **SWI-Prolog**: System installation of Prolog

### Installation

```bash
# Install PySwip
pip install pyswip>=0.2.10

# Install SWI-Prolog (Ubuntu/Debian)
sudo apt-get install swi-prolog

# Install SWI-Prolog (macOS)
brew install swi-prolog

# Install SWI-Prolog (Windows)
# Download installer from https://www.swi-prolog.org/download/stable
```

## Performance Considerations

- **Prolog Engine Loading:** One-time cost per service instance
- **Rule Query:** O(n) where n = number of rules
- **Pairwise Comparison:** O(m²) where m = objects per image
- **Typical Performance:** ~0.5 seconds for 10 images with 5-10 objects each

### Optimization Tips

1. **Cache Prolog Engine:** Service caches engine instance
2. **Filter Predictions First:** Apply NMS before symbolic reasoning
3. **Limit Rule Complexity:** Keep Prolog rules simple for fast queries
4. **Batch Processing:** Process multiple images in single call

## Notes

- Symbolic reasoning is **optional** and can be disabled without affecting other pipeline stages
- The service is consistent with the existing `pipeline/core/symbolic.py` implementation
- Default rules are tailored for aerial object detection (DOTA dataset)
- Custom rules can be created for any domain
- Explainability reports provide transparency into confidence adjustments
- Service handles Prolog unavailability gracefully with informative logging

