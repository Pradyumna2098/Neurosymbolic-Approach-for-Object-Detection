# File and Data Handling - Quick Reference

**Last Updated:** February 3, 2026

Quick reference guide for common file handling operations in the Neurosymbolic Object Detection application.

---

## Quick Navigation

| Topic | Jump To |
|-------|---------|
| File Validation Rules | [→ Validation](#file-validation-rules) |
| Directory Structure | [→ Structure](#directory-structure) |
| File Naming | [→ Naming](#file-naming-conventions) |
| Session Management | [→ Sessions](#session-management) |
| Code Examples | [→ Examples](#code-examples) |
| Common Issues | [→ Troubleshooting](#troubleshooting) |

---

## File Validation Rules

### Supported Formats

| Type | Extensions | Max Size | Notes |
|------|-----------|----------|-------|
| **Images** | `.jpg`, `.jpeg`, `.png` | 50 MB | Primary formats |
| **Predictions** | `.txt` | 10 MB | YOLO format |
| **Configs** | `.yaml`, `.yml` | 1 MB | UTF-8 encoding |

### Quick Validation Checklist

✅ **Images:**
- Extension: `.jpg`, `.jpeg`, `.png`
- Size: 1 KB - 50 MB
- Dimensions: 64×64 to 8192×8192
- Format: Valid image header

✅ **Predictions:**
- Extension: `.txt`
- Format: `class_id cx cy w h confidence`
- Fields: Exactly 6 space-separated values
- Coordinates: Normalized [0, 1]

---

## Directory Structure

### Development Layout

```
project_root/
├── data/uploads/
│   └── session_{uuid}/
│       ├── raw/              # Original uploads
│       └── validated/        # Validated files
│
└── outputs/
    └── session_{uuid}/
        ├── predictions/      # Model outputs
        │   ├── raw/
        │   ├── nms/
        │   └── refined/
        ├── visualizations/   # Bounding box images
        ├── knowledge_graphs/ # KG artifacts
        ├── reports/          # Metrics & logs
        └── logs/
```

### Production Layout

```
/var/lib/neurosymbolic/
├── storage/
│   └── user_{id}/
│       └── session_{uuid}/
├── models/production/
├── cache/                    # Temp, auto-cleanup
└── archive/                  # Compressed long-term
```

---

## File Naming Conventions

### Uploaded Images

```
Format: {original_name}_{timestamp}_{uuid}.{ext}

Examples:
aerial_view_20260203_180132_a3f2.jpg
satellite_image_20260203_180145_9b7e.png
```

### Prediction Files

```
Format: {image_stem}.txt

Examples:
aerial_view_20260203_180132_a3f2.txt  # Matches image name
satellite_image_20260203_180145_9b7e.txt
```

### Visualization Files

```
Format: {image_stem}_{type}_vis.{ext}

Types: raw, nms, refined

Examples:
aerial_view_20260203_180132_a3f2_raw_vis.jpg
aerial_view_20260203_180132_a3f2_nms_vis.jpg
aerial_view_20260203_180132_a3f2_refined_vis.jpg
```

### Session/Job IDs

```
Session ID: session_{uuid_v4}
Job ID:     job_{timestamp}_{uuid_v4}

Examples:
session_a3f2b8d4-c9e1-4f6a-8b2c-1d3e5f7a9b0c
job_20260203180132_a3f2b8d4-c9e1-4f6a-8b2c-1d3e5f7a9b0c
```

---

## Session Management

### Create Session

```python
import uuid
from pathlib import Path

def create_session(user_id: Optional[str] = None) -> str:
    """Create isolated session for file operations."""
    session_uuid = str(uuid.uuid4())
    session_id = f"session_{session_uuid}"
    
    # Create directories
    session_path = BASE_DIR / "session" / session_id
    (session_path / "uploads" / "raw").mkdir(parents=True)
    (session_path / "uploads" / "validated").mkdir(parents=True)
    (session_path / "outputs" / "predictions").mkdir(parents=True)
    
    return session_id
```

### Session Isolation

```python
# ✅ Good: Session-isolated paths
session_path = BASE_DIR / session_id
upload_path = session_path / "uploads" / "validated"

# ❌ Bad: Shared paths (conflicts)
upload_path = BASE_DIR / "uploads"  # All users share
```

---

## Code Examples

### 1. Generate Safe Filename

```python
import uuid
from datetime import datetime
from pathlib import Path

def generate_safe_filename(original_filename: str) -> str:
    """Generate unique, safe filename."""
    path = Path(original_filename)
    stem = path.stem
    ext = path.suffix.lower()
    
    # Sanitize
    safe_stem = "".join(c if c.isalnum() or c in '-_' else '_' for c in stem)
    safe_stem = safe_stem[:100]
    
    # Add timestamp and UUID
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    
    return f"{safe_stem}_{timestamp}_{short_uuid}{ext}"

# Example usage:
# "my file (1).jpg" -> "my_file_1_20260203_180132_a3f2.jpg"
```

### 2. Validate Image File

```python
from PIL import Image

def validate_image_file(file_path: Path) -> tuple[bool, str]:
    """Validate uploaded image file.
    
    Returns:
        (is_valid, error_message)
    """
    # Check extension
    if file_path.suffix.lower() not in {'.jpg', '.jpeg', '.png'}:
        return False, f"Invalid extension: {file_path.suffix}"
    
    # Check size
    size_mb = file_path.stat().st_size / (1024 * 1024)
    if size_mb > 50:
        return False, f"File too large: {size_mb:.1f} MB (max 50 MB)"
    if size_mb < 0.001:
        return False, "File too small (< 1 KB)"
    
    # Check image integrity
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            
            if width < 64 or height < 64:
                return False, f"Dimensions too small: {width}×{height}"
            if width > 8192 or height > 8192:
                return False, f"Dimensions too large: {width}×{height}"
                
    except Exception as e:
        return False, f"Corrupted image: {e}"
    
    return True, ""
```

### 3. Validate Prediction File

```python
def validate_prediction_file(file_path: Path) -> tuple[bool, str]:
    """Validate YOLO format prediction file.
    
    Returns:
        (is_valid, error_message)
    """
    if file_path.suffix != '.txt':
        return False, "Prediction files must be .txt"
    
    try:
        with file_path.open('r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()
                if len(parts) != 6:
                    return False, f"Line {line_num}: Expected 6 fields, got {len(parts)}"
                
                try:
                    class_id = int(parts[0])
                    cx, cy, w, h, conf = map(float, parts[1:])
                except ValueError:
                    return False, f"Line {line_num}: Invalid numeric values"
                
                # Validate ranges
                if not (0 <= class_id <= 14):
                    return False, f"Line {line_num}: Invalid class_id {class_id}"
                
                if not (0 <= cx <= 1 and 0 <= cy <= 1):
                    return False, f"Line {line_num}: Coordinates out of range"
                
                if not (0 < w <= 1 and 0 < h <= 1):
                    return False, f"Line {line_num}: Width/height out of range"
                
                if not (0 <= conf <= 1):
                    return False, f"Line {line_num}: Confidence out of range"
                    
    except Exception as e:
        return False, f"Error reading file: {e}"
    
    return True, ""
```

### 4. Atomic File Upload

```python
import shutil

def handle_file_upload(file_stream, session_id: str, filename: str) -> Path:
    """Handle file upload with atomic operations."""
    
    # Step 1: Write to temp location
    temp_id = str(uuid.uuid4())[:8]
    temp_path = TEMP_DIR / f"{temp_id}_{filename}"
    
    with temp_path.open('wb') as f:
        shutil.copyfileobj(file_stream, f)
    
    # Step 2: Validate
    is_valid, error_msg = validate_image_file(temp_path)
    if not is_valid:
        temp_path.unlink()
        raise ValidationError(error_msg)
    
    # Step 3: Generate final name and move atomically
    final_filename = generate_safe_filename(filename)
    final_path = get_session_path(session_id) / "uploads" / "validated" / final_filename
    
    temp_path.rename(final_path)  # Atomic operation
    
    return final_path
```

### 5. File Locking for Concurrent Access

```python
import fcntl
import time
from contextlib import contextmanager

@contextmanager
def file_lock(file_path: Path, timeout: float = 30.0):
    """Acquire exclusive file lock with timeout."""
    lock_file = file_path.with_suffix(file_path.suffix + ".lock")
    lock_fd = None
    start_time = time.time()
    
    try:
        lock_fd = open(lock_file, 'w')
        
        # Try to acquire lock
        while True:
            try:
                fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"Lock timeout on {file_path}")
                time.sleep(0.1)
        
        yield
        
    finally:
        if lock_fd:
            fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
            lock_fd.close()
        if lock_file.exists():
            lock_file.unlink()

# Usage:
with file_lock(metadata_path):
    # Perform file operations
    update_metadata(metadata_path, data)
```

---

## Configuration Examples

### Pipeline Configuration Template

```yaml
# Auto-generated for session_{uuid}

raw_predictions_dir: /path/to/session_{uuid}/predictions/raw
nms_predictions_dir: /path/to/session_{uuid}/predictions/nms
refined_predictions_dir: /path/to/session_{uuid}/predictions/refined
ground_truth_dir: /path/to/session_{uuid}/uploads/validated
rules_file: /path/to/pipeline/prolog/rules.pl
dataset_categories_file: /path/to/pipeline/prolog/dataset_categories.pl
report_file: /path/to/session_{uuid}/reports/explainability.csv
nms_iou_threshold: 0.5
```

### Cleanup Policy Configuration

```yaml
cleanup_policies:
  temporary_uploads:
    location: "data/uploads/temp/"
    retention: "1 hour"
    action: "delete"
    
  active_sessions:
    location: "data/uploads/session_*/"
    retention: "7 days"
    action: "archive"
    
  archived_sessions:
    location: "archive/{year}/{month}/"
    retention: "90 days"
    action: "delete"
    compression: "tar.gz"
```

---

## Troubleshooting

### Common Issues

#### Issue: "File too large" error

```python
# Solution: Compress or resize before upload
from PIL import Image

def compress_image(input_path: Path, max_size_mb: float = 10.0) -> Path:
    """Compress image to meet size limit."""
    with Image.open(input_path) as img:
        # Calculate quality to meet size target
        output_path = input_path.with_suffix('.compressed.jpg')
        
        quality = 95
        while quality > 20:
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            size_mb = output_path.stat().st_size / (1024 * 1024)
            
            if size_mb <= max_size_mb:
                break
            quality -= 5
        
        return output_path
```

#### Issue: Filename conflicts

```python
# Solution: Always use generate_safe_filename()
# ✅ Good: Unique filenames
filename = generate_safe_filename(uploaded_file.name)

# ❌ Bad: Original filename (conflicts)
filename = uploaded_file.name
```

#### Issue: Permission denied on file operations

```bash
# Solution: Fix ownership and permissions
sudo chown -R app_user:app_group /var/lib/neurosymbolic/storage
sudo chmod -R 755 /var/lib/neurosymbolic/storage
```

#### Issue: Disk space exhausted

```python
# Solution: Implement cleanup
def emergency_cleanup():
    """Free disk space by cleaning temp files and archiving."""
    # Clean temp files
    for temp_file in TEMP_DIR.glob("*"):
        if temp_file.is_file():
            temp_file.unlink()
    
    # Archive old sessions
    cutoff = datetime.utcnow() - timedelta(days=7)
    for session_dir in SESSIONS_DIR.glob("session_*"):
        session_time = datetime.fromtimestamp(session_dir.stat().st_mtime)
        if session_time < cutoff:
            archive_session(session_dir.name)
```

#### Issue: Corrupted prediction file

```python
# Solution: Regenerate predictions
def recover_corrupted_predictions(session_id: str, image_name: str):
    """Regenerate predictions for corrupted file."""
    session_path = get_session_path(session_id)
    
    # Delete corrupted file
    pred_file = session_path / "predictions" / "raw" / f"{image_name}.txt"
    if pred_file.exists():
        pred_file.unlink()
    
    # Re-run inference
    image_path = session_path / "uploads" / "validated" / f"{image_name}.jpg"
    run_inference(image_path, output_dir=pred_file.parent)
```

---

## Performance Tips

### 1. Batch Operations

```python
# ✅ Good: Batch file validation
def validate_batch(file_paths: List[Path]) -> Dict[Path, bool]:
    """Validate multiple files in parallel."""
    from concurrent.futures import ThreadPoolExecutor
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(validate_image_file, file_paths)
    
    return {path: result[0] for path, result in zip(file_paths, results)}

# ❌ Bad: Sequential validation
for path in file_paths:
    validate_image_file(path)
```

### 2. Stream Large Files

```python
# ✅ Good: Stream file upload
def stream_upload(file_stream, output_path: Path, chunk_size: int = 8192):
    """Stream large file upload."""
    with output_path.open('wb') as f:
        while chunk := file_stream.read(chunk_size):
            f.write(chunk)

# ❌ Bad: Load entire file in memory
data = file_stream.read()  # Memory issue for large files
```

### 3. Use Compression

```python
# ✅ Good: Compress archives
import tarfile

with tarfile.open(archive_path, "w:gz") as tar:
    tar.add(session_path, arcname=session_id)

# ❌ Bad: Uncompressed archives
shutil.make_archive(archive_path, 'tar', session_path)
```

---

## Security Checklist

✅ **File Validation:**
- [ ] Validate file extensions and magic numbers
- [ ] Enforce size limits
- [ ] Sanitize filenames

✅ **Access Control:**
- [ ] Isolate user/session data
- [ ] Prevent path traversal attacks
- [ ] Check file permissions

✅ **Data Protection:**
- [ ] Use HTTPS for file transfers
- [ ] Encrypt sensitive files at rest
- [ ] Implement rate limiting

✅ **Cleanup:**
- [ ] Delete temporary files
- [ ] Archive or delete old sessions
- [ ] Secure file deletion (overwrite)

---

## API Integration Examples

### Upload Files via API

```python
import requests

# Create session
response = requests.post("http://api.example.com/api/v1/sessions/create")
session_id = response.json()["session_id"]

# Upload files
files = [
    ('files', ('image1.jpg', open('image1.jpg', 'rb'), 'image/jpeg')),
    ('files', ('image2.jpg', open('image2.jpg', 'rb'), 'image/jpeg'))
]
response = requests.post(
    f"http://api.example.com/api/v1/sessions/{session_id}/upload",
    files=files
)

# Check results
print(response.json())
```

### Download Results

```python
# Download visualizations
response = requests.get(
    f"http://api.example.com/api/v1/sessions/{session_id}/visualizations/nms"
)

# Save files
for file_info in response.json()["files"]:
    file_url = file_info["download_url"]
    file_data = requests.get(file_url).content
    
    with open(file_info["filename"], 'wb') as f:
        f.write(file_data)
```

---

## Monitoring Metrics

### Key Metrics to Track

```python
from prometheus_client import Counter, Histogram, Gauge

# File operations
files_uploaded = Counter('files_uploaded_total', 'Total uploads')
upload_size_bytes = Histogram('upload_size_bytes', 'Upload size')
validation_failures = Counter('validation_failures_total', 'Validation failures')

# Storage
disk_usage_bytes = Gauge('disk_usage_bytes', 'Disk usage')
active_sessions = Gauge('active_sessions', 'Active sessions')

# Performance
file_processing_seconds = Histogram('file_processing_seconds', 'Processing time')
```

---

## Related Documentation

- [Complete Specification](file_data_handling_specifications.md) - Full detailed specification
- [Backend API Architecture](backend_api_architecture.md) - API integration
- [Model Pipeline Integration](model_pipeline_integration.md) - Pipeline integration
- [Visualization Logic Design](visualization_logic_design.md) - Visualization output handling

---

**Quick Links:**
- [File Validation](#file-validation-rules)
- [Directory Structure](#directory-structure)
- [Code Examples](#code-examples)
- [Troubleshooting](#troubleshooting)
