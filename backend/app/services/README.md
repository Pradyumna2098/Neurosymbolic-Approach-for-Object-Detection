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
