# Input/Output File and Data Handling Specifications

**Version:** 1.0  
**Date:** February 3, 2026  
**Status:** Design Specification  

## Table of Contents
1. [Overview](#overview)
2. [File Validation Specifications](#file-validation-specifications)
3. [File Organization and Naming Conventions](#file-organization-and-naming-conventions)
4. [Data Handling for Concurrent/Multi-User Scenarios](#data-handling-for-concurrentmulti-user-scenarios)
5. [Sample Directory Structures](#sample-directory-structures)
6. [Integration with Existing Systems](#integration-with-existing-systems)
7. [Best Practices and Guidelines](#best-practices-and-guidelines)
8. [Error Handling and Recovery](#error-handling-and-recovery)

---

## Overview

### Purpose
This document specifies comprehensive policies and standards for handling input files, organizing output data, and managing file operations in the Neurosymbolic Object Detection application. These specifications ensure data integrity, prevent conflicts in multi-user scenarios, and maintain consistent file organization across all components.

### Key Objectives
- **Data Integrity**: Ensure all uploaded and generated files meet quality standards
- **Conflict Prevention**: Avoid file naming conflicts in concurrent operations
- **Organization**: Maintain consistent, predictable file structure
- **Scalability**: Support growth from single-user to multi-user deployments
- **Traceability**: Enable tracking of all files to their source operations
- **Cleanup**: Define policies for temporary and permanent storage

### Scope
This specification covers:
- File validation rules for all input types
- Directory organization and naming conventions
- Session and user data isolation strategies
- File lifecycle management (upload → processing → storage → cleanup)
- Integration patterns with backend API and pipeline

**Out of Scope:**
- Implementation code (specification only)
- Database schema design (separate document)
- Network protocols (covered in backend API docs)

---

## File Validation Specifications

### 1. Image File Validation

#### Supported Image Formats

| Format | Extension | MIME Type | Priority | Notes |
|--------|-----------|-----------|----------|-------|
| **JPEG** | `.jpg`, `.jpeg` | `image/jpeg` | ✅ Primary | Most common, good compression |
| **PNG** | `.png` | `image/png` | ✅ Primary | Lossless, transparency support |
| **BMP** | `.bmp` | `image/bmp` | ⚠️ Supported | Large file size, rarely used |
| **TIFF** | `.tif`, `.tiff` | `image/tiff` | ⚠️ Supported | High quality, large files |

**Recommended Format:** JPEG or PNG for best compatibility and performance.

#### Image File Size Limits

```yaml
# Recommended limits based on use case
image_validation:
  min_file_size: 1KB           # Reject suspiciously small files
  max_file_size: 50MB          # Single image limit
  recommended_max: 10MB        # Optimal for processing
  
  # Size-based warnings
  warn_above: 20MB             # Warn user about large files
  
  # Batch upload limits
  max_batch_files: 100         # Maximum files per batch upload
  max_batch_total_size: 500MB  # Maximum total size per batch
```

**Rationale:**
- **50MB limit**: Accommodates high-resolution satellite/aerial imagery typical in DOTA dataset
- **20MB warning**: Performance considerations for SAHI slicing
- **Batch limits**: Prevent resource exhaustion from massive uploads

#### Image Dimension Constraints

```yaml
image_dimensions:
  min_width: 64                # Minimum useful resolution
  min_height: 64
  max_width: 8192              # Upper limit for memory safety
  max_height: 8192
  recommended_min: 640         # Optimal for YOLO detection
  recommended_max: 4096        # Optimal for SAHI processing
```

**Special Considerations:**
- **SAHI Processing**: Images larger than 1024x1024 benefit from slicing
- **Memory Usage**: 8192x8192 images require ~256MB+ in memory
- **Aspect Ratio**: No restrictions, all aspect ratios supported

#### Content Validation Rules

```python
# Validation checks to perform
validation_checks = {
    "file_header": {
        "description": "Verify file header matches extension",
        "action": "Read first 16 bytes, validate magic number",
        "reject_on_failure": True
    },
    "corruption_check": {
        "description": "Ensure image can be decoded",
        "action": "Attempt to open and read image properties",
        "reject_on_failure": True
    },
    "metadata_extraction": {
        "description": "Extract width, height, format, color mode",
        "action": "Use PIL/Pillow to read image info",
        "reject_on_failure": False
    },
    "color_mode_check": {
        "description": "Verify RGB or RGBA mode (no grayscale issues)",
        "action": "Check image.mode in ['RGB', 'RGBA', 'L']",
        "reject_on_failure": False,
        "convert_if_needed": True
    }
}
```

**Error Messages for Invalid Images:**

| Validation Failure | Error Code | Message | User Action |
|-------------------|------------|---------|-------------|
| Wrong extension | `INVALID_FORMAT` | "File extension does not match content. Expected JPEG/PNG." | Upload correct format |
| Corrupted file | `CORRUPTED_FILE` | "Image file is corrupted and cannot be read." | Re-upload file |
| Size too large | `FILE_TOO_LARGE` | "Image exceeds 50MB limit. Current size: {size}MB." | Compress or resize |
| Size too small | `FILE_TOO_SMALL` | "Image file is suspiciously small. Minimum: 1KB." | Check file integrity |
| Dimensions too large | `DIMENSIONS_EXCEEDED` | "Image dimensions {w}x{h} exceed maximum 8192x8192." | Resize image |
| Dimensions too small | `DIMENSIONS_TOO_SMALL` | "Image dimensions {w}x{h} below minimum 64x64." | Upload larger image |

### 2. Prediction File Validation

#### YOLO Format (.txt) Validation

Prediction files must follow YOLO normalized coordinate format:

```
# Format: class_id center_x center_y width height confidence
# Example:
0 0.5123 0.4567 0.1234 0.0987 0.9234
1 0.7890 0.6543 0.0876 0.1123 0.8765
```

**Validation Rules:**

```yaml
prediction_file_validation:
  required_extension: ".txt"
  encoding: "utf-8"
  
  line_format:
    field_count: 6                    # Must have exactly 6 fields
    separator: " "                    # Space-separated values
    
  field_constraints:
    class_id:
      type: "integer"
      min: 0
      max: 14                         # DOTA dataset has 15 classes (0-14)
      
    center_x:
      type: "float"
      min: 0.0
      max: 1.0                        # Normalized coordinates
      
    center_y:
      type: "float"
      min: 0.0
      max: 1.0
      
    width:
      type: "float"
      min: 0.0001                     # Must be positive
      max: 1.0
      
    height:
      type: "float"
      min: 0.0001
      max: 1.0
      
    confidence:
      type: "float"
      min: 0.0
      max: 1.0
      
  validation_rules:
    - "Allow empty files (no detections)"
    - "Ignore blank lines and lines starting with #"
    - "Reject files with malformed lines"
    - "Validate all coordinates are within [0, 1]"
    - "Ensure width + center_x/2 <= 1.0 and height + center_y/2 <= 1.0"
```

**Example Validation Function:**

```python
def validate_prediction_line(line: str, line_num: int) -> tuple[bool, str]:
    """Validate a single prediction line.
    
    Returns:
        (is_valid, error_message)
    """
    # Skip empty lines and comments
    line = line.strip()
    if not line or line.startswith('#'):
        return True, ""
    
    parts = line.split()
    if len(parts) != 6:
        return False, f"Line {line_num}: Expected 6 fields, got {len(parts)}"
    
    try:
        class_id = int(parts[0])
        cx, cy, w, h, conf = map(float, parts[1:])
    except ValueError as e:
        return False, f"Line {line_num}: Invalid numeric values: {e}"
    
    # Validate ranges
    if not (0 <= class_id <= 14):
        return False, f"Line {line_num}: class_id {class_id} out of range [0, 14]"
    
    if not (0.0 <= cx <= 1.0 and 0.0 <= cy <= 1.0):
        return False, f"Line {line_num}: center coordinates out of range [0, 1]"
    
    if not (0.0 < w <= 1.0 and 0.0 < h <= 1.0):
        return False, f"Line {line_num}: width/height out of range (0, 1]"
    
    if not (0.0 <= conf <= 1.0):
        return False, f"Line {line_num}: confidence {conf} out of range [0, 1]"
    
    # Validate bounding box doesn't exceed image boundaries
    if cx - w/2 < 0 or cx + w/2 > 1.0:
        return False, f"Line {line_num}: bbox extends beyond horizontal bounds"
    
    if cy - h/2 < 0 or cy + h/2 > 1.0:
        return False, f"Line {line_num}: bbox extends beyond vertical bounds"
    
    return True, ""
```

#### Ground Truth Label Validation

Ground truth labels use the same YOLO format but **without confidence score** (5 fields):

```
# Format: class_id center_x center_y width height
# Example:
0 0.5123 0.4567 0.1234 0.0987
1 0.7890 0.6543 0.0876 0.1123
```

**Validation Differences:**
- **Field count**: Exactly 5 fields (no confidence score)
- **Required files**: Each image in training/validation set must have corresponding label
- **Missing labels**: Empty file = image has no objects (valid case)

### 3. Configuration File Validation

#### YAML Configuration Validation

```yaml
config_file_validation:
  required_extension: ".yaml" or ".yml"
  encoding: "utf-8"
  
  required_sections:
    - "model_path"
    - "confidence_threshold"
    
  path_validation:
    - "Expand ~ and environment variables"
    - "Convert to absolute paths"
    - "Verify existence for input paths"
    - "Create directories for output paths if missing"
    
  value_constraints:
    confidence_threshold:
      type: "float"
      min: 0.0
      max: 1.0
      default: 0.25
      
    slice_height:
      type: "integer"
      min: 256
      max: 2048
      default: 1024
      
    slice_width:
      type: "integer"
      min: 256
      max: 2048
      default: 1024
      
    overlap_ratio:
      type: "float"
      min: 0.0
      max: 0.5
      default: 0.2
```

---

## File Organization and Naming Conventions

### 1. Directory Structure Standards

#### Development Environment Structure

```
project_root/
├── data/
│   ├── uploads/              # User uploaded images
│   │   ├── session_<UUID>/   # Per-session isolation
│   │   │   ├── raw/          # Original uploaded files
│   │   │   └── validated/    # Files passing validation
│   │   └── temp/             # Temporary upload staging
│   │
│   ├── images/               # Dataset images
│   │   ├── train/
│   │   ├── val/
│   │   └── test/
│   │
│   └── labels/               # Ground truth labels
│       ├── train/
│       ├── val/
│       └── test/
│
├── outputs/
│   ├── predictions/          # Model predictions
│   │   ├── session_<UUID>/   # Per-session outputs
│   │   │   ├── raw/          # Raw YOLO predictions
│   │   │   ├── nms/          # NMS-filtered predictions
│   │   │   └── refined/      # Symbolically refined predictions
│   │   └── archive/          # Archived old predictions
│   │
│   ├── visualizations/       # Bounding box overlays
│   │   ├── session_<UUID>/
│   │   │   ├── raw/          # Raw predictions visualized
│   │   │   ├── nms/          # NMS predictions visualized
│   │   │   └── refined/      # Refined predictions visualized
│   │   └── archive/
│   │
│   ├── knowledge_graphs/     # KG artifacts
│   │   ├── session_<UUID>/
│   │   │   ├── facts.pl      # Prolog facts
│   │   │   ├── graph.png     # Graph visualization
│   │   │   └── stats.json    # Graph statistics
│   │   └── archive/
│   │
│   ├── reports/              # Evaluation reports
│   │   ├── session_<UUID>/
│   │   │   ├── metrics.json  # mAP scores, precision, recall
│   │   │   ├── explainability.csv  # Confidence adjustments
│   │   │   └── summary.txt   # Human-readable summary
│   │   └── archive/
│   │
│   └── logs/                 # Processing logs
│       ├── session_<UUID>/
│       │   ├── inference.log
│       │   ├── nms.log
│       │   └── symbolic.log
│       └── archive/
│
├── models/                   # Model weights
│   ├── yolo/
│   │   ├── best.pt          # Best checkpoint
│   │   ├── last.pt          # Latest checkpoint
│   │   └── versions/        # Version history
│   └── configs/             # Model configurations
│
└── monitoring/              # Monitoring data
    ├── metrics/             # Prometheus metrics
    └── logs/                # Application logs
```

#### Production Environment Structure

```
/var/lib/neurosymbolic/
├── storage/
│   ├── uploads/
│   │   └── user_<USER_ID>/
│   │       └── session_<UUID>/
│   │           ├── images/
│   │           └── metadata.json
│   │
│   └── outputs/
│       └── user_<USER_ID>/
│           └── session_<UUID>/
│               ├── predictions/
│               ├── visualizations/
│               ├── knowledge_graphs/
│               └── reports/
│
├── models/
│   ├── production/
│   │   └── yolo_v11_obb_best.pt
│   └── staging/
│
├── cache/                    # Temporary processing cache
│   └── session_<UUID>/
│       └── sahi_slices/
│
└── archive/                  # Long-term storage
    ├── 2026/
    │   ├── 01/              # Year/Month
    │   │   └── session_<UUID>.tar.gz
    │   └── 02/
    └── retention_policy.json
```

### 2. File Naming Conventions

#### Uploaded Image Files

**Convention:**
```
<original_filename>_<timestamp>_<short_uuid>.<ext>

Examples:
aerial_view_001.jpg                    # Original uploaded name (preserved)
aerial_view_001_20260203_180132_a3f2.jpg  # Renamed for uniqueness
satellite_image.png                    # Original
satellite_image_20260203_180145_9b7e.png  # Renamed
```

**Naming Rules:**
- **Preserve original name**: Include original filename in renamed file
- **Timestamp format**: `YYYYMMDD_HHMMSS` in UTC
- **Short UUID**: First 8 characters of UUID v4 for uniqueness
- **Extension**: Preserve original extension (lowercase)
- **Character restrictions**: Replace spaces with underscores, remove special chars

**Example Implementation:**

```python
import uuid
from datetime import datetime
from pathlib import Path

def generate_safe_filename(original_filename: str) -> str:
    """Generate a unique, safe filename from original name.
    
    Args:
        original_filename: Original uploaded filename
        
    Returns:
        Safe, unique filename with timestamp and UUID
    """
    # Extract stem and extension
    path = Path(original_filename)
    stem = path.stem
    ext = path.suffix.lower()
    
    # Sanitize stem: remove special chars, replace spaces
    safe_stem = "".join(c if c.isalnum() or c in '-_' else '_' for c in stem)
    safe_stem = safe_stem[:100]  # Limit length
    
    # Generate timestamp and short UUID
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    
    # Construct new filename
    new_filename = f"{safe_stem}_{timestamp}_{short_uuid}{ext}"
    
    return new_filename

# Usage examples:
# "my file (1).jpg" -> "my_file_1_20260203_180132_a3f2.jpg"
# "Aerial View #2.PNG" -> "Aerial_View_2_20260203_180132_b8d4.png"
```

#### Prediction Files

**Convention:**
```
<image_stem>.txt

Examples:
aerial_view_001_20260203_180132_a3f2.txt   # Matches image name
satellite_image_20260203_180145_9b7e.txt
```

**Naming Rules:**
- **Match image filename**: Use same stem as corresponding image
- **Always .txt extension**: YOLO format requirement
- **One file per image**: Each image has exactly one prediction file

#### Visualization Output Files

**Convention:**
```
<image_stem>_<prediction_type>_vis.<ext>

Examples:
aerial_view_001_20260203_180132_a3f2_raw_vis.jpg      # Raw predictions
aerial_view_001_20260203_180132_a3f2_nms_vis.jpg      # NMS-filtered
aerial_view_001_20260203_180132_a3f2_refined_vis.jpg  # Symbolically refined
```

**Prediction Types:**
- `raw` - Raw YOLO/SAHI predictions
- `nms` - After Non-Maximum Suppression
- `refined` - After symbolic reasoning

#### Session and Job Identifiers

**Session ID Format:**
```
session_<UUID_v4>

Examples:
session_a3f2b8d4-c9e1-4f6a-8b2c-1d3e5f7a9b0c
session_9b7e6d5c-4a3b-2c1d-0e9f-8a7b6c5d4e3f
```

**Job ID Format (for async processing):**
```
job_<timestamp>_<UUID_v4>

Examples:
job_20260203180132_a3f2b8d4-c9e1-4f6a-8b2c-1d3e5f7a9b0c
job_20260203180145_9b7e6d5c-4a3b-2c1d-0e9f-8a7b6c5d4e3f
```

**Rationale:**
- **UUID v4**: Guaranteed uniqueness across distributed systems
- **Timestamp prefix for jobs**: Easy chronological sorting
- **Prefix naming**: Easy identification in logs and file systems

---

## Data Handling for Concurrent/Multi-User Scenarios

### 1. Session Isolation Strategy

#### Session Creation and Management

```python
class SessionManager:
    """Manages isolated sessions for concurrent processing."""
    
    def create_session(self, user_id: Optional[str] = None) -> str:
        """Create a new isolated session.
        
        Args:
            user_id: Optional user identifier for multi-user systems
            
        Returns:
            session_id: Unique session identifier
        """
        session_uuid = str(uuid.uuid4())
        session_id = f"session_{session_uuid}"
        
        # Create session metadata
        metadata = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active",
            "files_uploaded": [],
            "jobs_created": []
        }
        
        # Create session directories
        self._create_session_directories(session_id, user_id)
        
        # Store metadata
        self._save_session_metadata(session_id, metadata)
        
        return session_id
    
    def _create_session_directories(self, session_id: str, user_id: Optional[str]):
        """Create all necessary directories for a session."""
        base_path = self._get_session_base_path(session_id, user_id)
        
        directories = [
            base_path / "uploads" / "raw",
            base_path / "uploads" / "validated",
            base_path / "predictions" / "raw",
            base_path / "predictions" / "nms",
            base_path / "predictions" / "refined",
            base_path / "visualizations" / "raw",
            base_path / "visualizations" / "nms",
            base_path / "visualizations" / "refined",
            base_path / "knowledge_graphs",
            base_path / "reports",
            base_path / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
```

#### Multi-User Isolation

**Directory Structure for Multi-User:**
```
/var/lib/neurosymbolic/storage/
├── user_001/
│   ├── session_a3f2b8d4.../
│   └── session_9b7e6d5c.../
├── user_002/
│   ├── session_1a2b3c4d.../
│   └── session_5e6f7g8h.../
└── user_003/
    └── session_9i0j1k2l.../
```

**Access Control Rules:**
```yaml
access_control:
  user_data:
    isolation: "strict"          # Users cannot access other users' data
    path_pattern: "user_{user_id}/session_{session_id}/**"
    
  session_data:
    isolation: "strict"          # Sessions within user are isolated
    concurrent_access: "read_only"  # Multiple reads OK, single writer
    
  model_weights:
    isolation: "shared"          # Models shared across all users
    access: "read_only"          # Users cannot modify models
    
  monitoring:
    isolation: "shared"          # Aggregated monitoring across users
    access: "read_only"
```

### 2. Concurrent Processing Patterns

#### File Upload Concurrency

```python
# Pattern 1: Atomic File Upload with Staging
def handle_file_upload(file_stream, session_id: str, filename: str) -> Path:
    """Handle file upload with atomic operations."""
    
    # Step 1: Write to temporary location with unique name
    temp_id = str(uuid.uuid4())[:8]
    temp_path = TEMP_DIR / f"{temp_id}_{filename}"
    
    with temp_path.open('wb') as f:
        shutil.copyfileobj(file_stream, f)
    
    # Step 2: Validate uploaded file
    if not validate_image_file(temp_path):
        temp_path.unlink()  # Delete invalid file
        raise ValidationError("File validation failed")
    
    # Step 3: Generate final filename and move atomically
    final_filename = generate_safe_filename(filename)
    final_path = get_session_path(session_id) / "uploads" / "validated" / final_filename
    
    # Atomic rename operation (prevents partial writes)
    temp_path.rename(final_path)
    
    # Step 4: Update session metadata
    update_session_metadata(session_id, {"files_uploaded": [final_filename]})
    
    return final_path
```

#### Concurrent Prediction Generation

```python
# Pattern 2: Job Queue with Status Tracking
class InferenceJob:
    """Represents an async inference job."""
    
    def __init__(self, session_id: str, image_paths: List[Path]):
        self.job_id = self._generate_job_id()
        self.session_id = session_id
        self.image_paths = image_paths
        self.status = "pending"
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.error = None
        
    def _generate_job_id(self) -> str:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        job_uuid = str(uuid.uuid4())
        return f"job_{timestamp}_{job_uuid}"
    
    def execute(self):
        """Execute inference job with status updates."""
        try:
            self.status = "running"
            self.started_at = datetime.utcnow()
            self._save_status()
            
            # Process images
            for image_path in self.image_paths:
                # Generate predictions
                predictions = run_inference(image_path)
                
                # Save predictions
                pred_file = self._get_prediction_path(image_path)
                save_predictions(predictions, pred_file)
            
            self.status = "completed"
            self.completed_at = datetime.utcnow()
            
        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            
        finally:
            self._save_status()
    
    def _save_status(self):
        """Persist job status to disk."""
        status_file = get_session_path(self.session_id) / "jobs" / f"{self.job_id}.json"
        status_file.parent.mkdir(parents=True, exist_ok=True)
        
        with status_file.open('w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)
```

### 3. File Locking and Conflict Prevention

#### File Lock Implementation

```python
import fcntl
import time
from contextlib import contextmanager

@contextmanager
def file_lock(file_path: Path, timeout: float = 30.0):
    """Acquire exclusive file lock with timeout.
    
    Args:
        file_path: Path to file to lock
        timeout: Maximum seconds to wait for lock
        
    Raises:
        TimeoutError: If lock cannot be acquired within timeout
        
    Usage:
        with file_lock(Path("session_metadata.json")):
            # Perform file operations
            pass
    """
    lock_file = file_path.with_suffix(file_path.suffix + ".lock")
    lock_fd = None
    start_time = time.time()
    
    try:
        # Create lock file
        lock_fd = open(lock_file, 'w')
        
        # Try to acquire exclusive lock with timeout
        while True:
            try:
                fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break  # Lock acquired
            except BlockingIOError:
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"Could not acquire lock on {file_path} within {timeout}s")
                time.sleep(0.1)  # Wait before retry
        
        yield  # Allow caller to perform operations
        
    finally:
        # Release lock
        if lock_fd:
            fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
            lock_fd.close()
            
        # Remove lock file
        if lock_file.exists():
            lock_file.unlink()

# Usage Example
def update_session_metadata(session_id: str, updates: dict):
    """Update session metadata with file locking."""
    metadata_path = get_session_path(session_id) / "metadata.json"
    
    with file_lock(metadata_path):
        # Read current metadata
        with metadata_path.open('r') as f:
            metadata = json.load(f)
        
        # Update metadata
        metadata.update(updates)
        metadata["updated_at"] = datetime.utcnow().isoformat()
        
        # Write atomically using temp file
        temp_path = metadata_path.with_suffix('.tmp')
        with temp_path.open('w') as f:
            json.dump(metadata, f, indent=2)
        
        # Atomic rename
        temp_path.rename(metadata_path)
```

### 4. Data Lifecycle Management

#### Cleanup Policies

```yaml
cleanup_policies:
  temporary_uploads:
    location: "data/uploads/temp/"
    retention: "1 hour"
    cleanup_trigger: "age"
    action: "delete"
    
  active_sessions:
    location: "data/uploads/session_*/"
    retention: "7 days"
    cleanup_trigger: "age or completion"
    action: "move to archive"
    
  archived_sessions:
    location: "archive/{year}/{month}/"
    retention: "90 days"
    cleanup_trigger: "age"
    action: "delete or move to cold storage"
    compression: "tar.gz"
    
  model_cache:
    location: "cache/session_*/sahi_slices/"
    retention: "24 hours"
    cleanup_trigger: "age or session completion"
    action: "delete"
    
  logs:
    location: "outputs/logs/"
    retention: "30 days"
    cleanup_trigger: "age"
    action: "compress and archive"
```

#### Cleanup Implementation

```python
class DataLifecycleManager:
    """Manages data lifecycle and cleanup policies."""
    
    def cleanup_temp_files(self, age_hours: float = 1.0):
        """Clean up temporary upload files older than specified age."""
        temp_dir = TEMP_DIR
        cutoff_time = datetime.utcnow() - timedelta(hours=age_hours)
        
        for temp_file in temp_dir.glob("*"):
            if temp_file.is_file():
                file_age = datetime.fromtimestamp(temp_file.stat().st_mtime)
                if file_age < cutoff_time:
                    try:
                        temp_file.unlink()
                        logger.info(f"Deleted temp file: {temp_file}")
                    except Exception as e:
                        logger.error(f"Failed to delete {temp_file}: {e}")
    
    def archive_session(self, session_id: str):
        """Archive completed session to compressed storage."""
        session_path = get_session_path(session_id)
        
        # Check if session is complete
        metadata = self._load_session_metadata(session_id)
        if metadata.get("status") != "completed":
            logger.warning(f"Session {session_id} not completed, skipping archive")
            return
        
        # Create archive
        archive_date = datetime.utcnow()
        archive_dir = ARCHIVE_DIR / str(archive_date.year) / f"{archive_date.month:02d}"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        archive_path = archive_dir / f"{session_id}.tar.gz"
        
        # Compress session directory
        import tarfile
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(session_path, arcname=session_id)
        
        # Verify archive
        if self._verify_archive(archive_path):
            # Delete original
            shutil.rmtree(session_path)
            logger.info(f"Archived session {session_id} to {archive_path}")
        else:
            logger.error(f"Archive verification failed for {session_id}")
    
    def cleanup_old_archives(self, retention_days: int = 90):
        """Delete archives older than retention period."""
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        for archive_file in ARCHIVE_DIR.rglob("*.tar.gz"):
            file_age = datetime.fromtimestamp(archive_file.stat().st_mtime)
            if file_age < cutoff_date:
                try:
                    archive_file.unlink()
                    logger.info(f"Deleted old archive: {archive_file}")
                except Exception as e:
                    logger.error(f"Failed to delete {archive_file}: {e}")
```

#### Scheduled Cleanup Tasks

```python
# Example using APScheduler for periodic cleanup

from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
lifecycle_manager = DataLifecycleManager()

# Clean temp files every hour
scheduler.add_job(
    lifecycle_manager.cleanup_temp_files,
    'interval',
    hours=1,
    args=[1.0],  # 1 hour age
    id='cleanup_temp_files'
)

# Archive old sessions daily
scheduler.add_job(
    lifecycle_manager.archive_old_sessions,
    'cron',
    hour=2,  # 2 AM
    minute=0,
    id='archive_sessions'
)

# Delete old archives weekly
scheduler.add_job(
    lifecycle_manager.cleanup_old_archives,
    'cron',
    day_of_week='sun',
    hour=3,  # 3 AM Sunday
    minute=0,
    args=[90],  # 90 days retention
    id='cleanup_archives'
)

scheduler.start()
```

---

## Sample Directory Structures

### Example 1: Single User Development Session

```
project_root/
├── data/
│   └── uploads/
│       └── session_a3f2b8d4.../
│           ├── raw/                          # Original uploads
│           │   ├── aerial_001.jpg           (5.2 MB)
│           │   ├── aerial_002.jpg           (4.8 MB)
│           │   └── aerial_003.jpg           (6.1 MB)
│           │
│           ├── validated/                    # Validated files
│           │   ├── aerial_001_20260203_180132_a3f2.jpg
│           │   ├── aerial_002_20260203_180133_b4e7.jpg
│           │   └── aerial_003_20260203_180134_c5f9.jpg
│           │
│           └── metadata.json                # Session metadata
│
└── outputs/
    ├── predictions/
    │   └── session_a3f2b8d4.../
    │       ├── raw/                         # Raw SAHI predictions
    │       │   ├── aerial_001_20260203_180132_a3f2.txt
    │       │   ├── aerial_002_20260203_180133_b4e7.txt
    │       │   └── aerial_003_20260203_180134_c5f9.txt
    │       │
    │       ├── nms/                         # NMS-filtered
    │       │   ├── aerial_001_20260203_180132_a3f2.txt
    │       │   ├── aerial_002_20260203_180133_b4e7.txt
    │       │   └── aerial_003_20260203_180134_c5f9.txt
    │       │
    │       └── refined/                     # Symbolically refined
    │           ├── aerial_001_20260203_180132_a3f2.txt
    │           ├── aerial_002_20260203_180133_b4e7.txt
    │           └── aerial_003_20260203_180134_c5f9.txt
    │
    ├── visualizations/
    │   └── session_a3f2b8d4.../
    │       ├── raw/
    │       │   ├── aerial_001_20260203_180132_a3f2_raw_vis.jpg
    │       │   ├── aerial_002_20260203_180133_b4e7_raw_vis.jpg
    │       │   └── aerial_003_20260203_180134_c5f9_raw_vis.jpg
    │       │
    │       ├── nms/
    │       │   ├── aerial_001_20260203_180132_a3f2_nms_vis.jpg
    │       │   ├── aerial_002_20260203_180133_b4e7_nms_vis.jpg
    │       │   └── aerial_003_20260203_180134_c5f9_nms_vis.jpg
    │       │
    │       └── refined/
    │           ├── aerial_001_20260203_180132_a3f2_refined_vis.jpg
    │           ├── aerial_002_20260203_180133_b4e7_refined_vis.jpg
    │           └── aerial_003_20260203_180134_c5f9_refined_vis.jpg
    │
    ├── knowledge_graphs/
    │   └── session_a3f2b8d4.../
    │       ├── facts.pl                    # Prolog facts
    │       ├── knowledge_graph_visuals.png  # Graph visualization
    │       └── stats.json                  # Graph statistics
    │
    ├── reports/
    │   └── session_a3f2b8d4.../
    │       ├── metrics.json                # Performance metrics
    │       ├── explainability.csv          # Confidence adjustments
    │       └── summary.txt                 # Human-readable summary
    │
    └── logs/
        └── session_a3f2b8d4.../
            ├── inference.log               # Inference stage logs
            ├── nms.log                     # NMS processing logs
            └── symbolic.log                # Symbolic reasoning logs
```

**File Size Summary:**
```
Session: session_a3f2b8d4...
Total uploaded: 16.1 MB (3 images)
Total predictions: 18 KB (9 txt files)
Total visualizations: 45.6 MB (9 images)
Total knowledge graphs: 2.3 MB
Total reports: 45 KB
Total logs: 120 KB
Total session size: ~64 MB
```

### Example 2: Production Multi-User System

```
/var/lib/neurosymbolic/
├── storage/
│   ├── user_jdoe/
│   │   ├── session_a3f2b8d4.../
│   │   │   ├── uploads/
│   │   │   └── outputs/
│   │   │
│   │   └── session_9b7e6d5c.../
│   │       ├── uploads/
│   │       └── outputs/
│   │
│   ├── user_asmith/
│   │   └── session_1a2b3c4d.../
│   │       ├── uploads/
│   │       └── outputs/
│   │
│   └── quotas.json                        # User storage quotas
│
├── models/
│   ├── production/
│   │   ├── yolo_v11_obb_best.pt         (250 MB)
│   │   └── model_metadata.json
│   │
│   └── staging/
│       └── yolo_v11_obb_candidate.pt
│
├── cache/                                 # Temporary processing cache
│   ├── session_a3f2b8d4.../
│   │   └── sahi_slices/                  # Deleted after processing
│   │
│   └── session_9b7e6d5c.../
│       └── sahi_slices/
│
└── archive/                               # Long-term storage
    ├── 2026/
    │   ├── 01/
    │   │   ├── session_old1.tar.gz      (compressed)
    │   │   └── session_old2.tar.gz
    │   │
    │   └── 02/
    │       └── session_a3f2b8d4.tar.gz
    │
    └── retention_policy.json
```

**User Quotas:**
```json
{
  "user_jdoe": {
    "max_storage_mb": 1000,
    "current_usage_mb": 245,
    "max_concurrent_sessions": 3,
    "active_sessions": 2,
    "max_files_per_upload": 100,
    "rate_limits": {
      "uploads_per_hour": 50,
      "jobs_per_hour": 20
    }
  },
  "user_asmith": {
    "max_storage_mb": 500,
    "current_usage_mb": 89,
    "max_concurrent_sessions": 2,
    "active_sessions": 1
  }
}
```

---

## Integration with Existing Systems

### 1. Backend API Integration

#### API Endpoints for File Operations

```python
# FastAPI endpoint examples

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/api/v1/sessions/create")
async def create_session(user_id: Optional[str] = None):
    """Create a new isolated session for file uploads."""
    try:
        session_manager = SessionManager()
        session_id = session_manager.create_session(user_id)
        
        return {
            "session_id": session_id,
            "status": "active",
            "upload_url": f"/api/v1/sessions/{session_id}/upload",
            "created_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/sessions/{session_id}/upload")
async def upload_files(
    session_id: str,
    files: List[UploadFile] = File(...)
):
    """Upload and validate image files for a session."""
    
    # Validate session exists
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    results = []
    for file in files:
        try:
            # Validate file
            validation_result = validate_uploaded_file(file)
            if not validation_result.is_valid:
                results.append({
                    "filename": file.filename,
                    "status": "rejected",
                    "error": validation_result.error_message
                })
                continue
            
            # Save file
            saved_path = handle_file_upload(file.file, session_id, file.filename)
            
            results.append({
                "filename": file.filename,
                "status": "accepted",
                "file_id": saved_path.stem,
                "size_bytes": saved_path.stat().st_size
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "session_id": session_id,
        "uploaded": len([r for r in results if r["status"] == "accepted"]),
        "rejected": len([r for r in results if r["status"] == "rejected"]),
        "files": results
    }


@app.get("/api/v1/sessions/{session_id}/files")
async def list_session_files(session_id: str):
    """List all files in a session."""
    
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_path = get_session_path(session_id)
    
    files = {
        "uploads": list_files(session_path / "uploads" / "validated"),
        "predictions": {
            "raw": list_files(session_path / "predictions" / "raw"),
            "nms": list_files(session_path / "predictions" / "nms"),
            "refined": list_files(session_path / "predictions" / "refined")
        },
        "visualizations": {
            "raw": list_files(session_path / "visualizations" / "raw"),
            "nms": list_files(session_path / "visualizations" / "nms"),
            "refined": list_files(session_path / "visualizations" / "refined")
        }
    }
    
    return files
```

### 2. Pipeline Integration

#### Configuration File Generation

```python
def generate_pipeline_config(session_id: str) -> Path:
    """Generate pipeline configuration for a session.
    
    Returns:
        Path to generated configuration file
    """
    session_path = get_session_path(session_id)
    
    config = {
        "raw_predictions_dir": str(session_path / "predictions" / "raw"),
        "nms_predictions_dir": str(session_path / "predictions" / "nms"),
        "refined_predictions_dir": str(session_path / "predictions" / "refined"),
        "ground_truth_dir": str(session_path / "uploads" / "validated"),
        "rules_file": str(PROJECT_ROOT / "pipeline" / "prolog" / "rules.pl"),
        "dataset_categories_file": str(PROJECT_ROOT / "pipeline" / "prolog" / "dataset_categories.pl"),
        "report_file": str(session_path / "reports" / "explainability.csv"),
        "nms_iou_threshold": 0.5
    }
    
    config_path = session_path / "pipeline_config.yaml"
    with config_path.open('w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    return config_path
```

#### Pipeline Invocation

```python
async def run_session_pipeline(session_id: str, stages: List[str] = None):
    """Run pipeline stages for a session.
    
    Args:
        session_id: Session identifier
        stages: List of stages to run. Default: ["preprocess", "symbolic", "eval"]
    """
    if stages is None:
        stages = ["preprocess", "symbolic", "eval"]
    
    # Generate config
    config_path = generate_pipeline_config(session_id)
    
    # Run stages
    for stage in stages:
        logger.info(f"Running {stage} stage for session {session_id}")
        
        cmd = [
            "python", "-m", f"pipeline.core.{stage}",
            "--config", str(config_path)
        ]
        
        # Run subprocess
        result = await run_command_async(cmd)
        
        if result.returncode != 0:
            raise RuntimeError(f"Stage {stage} failed: {result.stderr}")
```

### 3. Monitoring Integration

#### Session Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# File operation metrics
files_uploaded = Counter(
    'files_uploaded_total',
    'Total number of files uploaded',
    ['user_id', 'session_id', 'file_type']
)

file_validation_failures = Counter(
    'file_validation_failures_total',
    'Total number of file validation failures',
    ['user_id', 'reason']
)

upload_size_bytes = Histogram(
    'upload_size_bytes',
    'Size of uploaded files in bytes',
    ['user_id', 'file_type']
)

active_sessions = Gauge(
    'active_sessions',
    'Number of currently active sessions',
    ['user_id']
)

# Usage
files_uploaded.labels(user_id='jdoe', session_id='session_a3f2...', file_type='image').inc()
upload_size_bytes.labels(user_id='jdoe', file_type='image').observe(5242880)  # 5MB
```

---

## Best Practices and Guidelines

### 1. File Validation Best Practices

✅ **DO:**
- Validate file extensions and MIME types
- Check file size before processing
- Verify file integrity (magic numbers)
- Provide clear error messages to users
- Log validation failures for monitoring

❌ **DON'T:**
- Trust user-provided filenames or extensions
- Process files without validation
- Allow unlimited file sizes
- Expose system paths in error messages

### 2. File Organization Best Practices

✅ **DO:**
- Use consistent naming conventions
- Organize by session and processing stage
- Include timestamps for traceability
- Use UUIDs for uniqueness
- Document directory structure

❌ **DON'T:**
- Mix files from different sessions
- Use sequential IDs (not unique in distributed systems)
- Store files with user-provided names only
- Create deeply nested directory structures (>5 levels)

### 3. Concurrent Processing Best Practices

✅ **DO:**
- Use file locks for metadata updates
- Implement atomic file operations
- Provide unique job/session IDs
- Track job status persistently
- Implement timeouts for locks

❌ **DON'T:**
- Assume single-threaded access
- Modify files without locking
- Reuse session IDs
- Block indefinitely waiting for locks

### 4. Data Lifecycle Best Practices

✅ **DO:**
- Define clear retention policies
- Archive completed sessions
- Compress archived data
- Schedule regular cleanup
- Monitor storage usage

❌ **DON'T:**
- Keep temporary files indefinitely
- Delete data without archiving
- Fill disk with old data
- Ignore storage quotas

---

## Error Handling and Recovery

### Common Error Scenarios

#### Scenario 1: Disk Space Exhaustion

**Detection:**
```python
import shutil

def check_disk_space(path: Path, required_mb: float = 100.0) -> bool:
    """Check if sufficient disk space is available."""
    stat = shutil.disk_usage(path)
    available_mb = stat.free / (1024 * 1024)
    return available_mb >= required_mb
```

**Handling:**
```python
if not check_disk_space(session_path, required_mb=500):
    # Trigger cleanup
    lifecycle_manager.cleanup_temp_files()
    lifecycle_manager.archive_old_sessions()
    
    # Recheck
    if not check_disk_space(session_path, required_mb=500):
        raise DiskSpaceError("Insufficient disk space for operation")
```

#### Scenario 2: File Corruption During Upload

**Detection:**
```python
def verify_file_integrity(file_path: Path) -> bool:
    """Verify file can be read and is not corrupted."""
    try:
        with Image.open(file_path) as img:
            img.verify()  # Verify image integrity
        return True
    except Exception as e:
        logger.error(f"File corruption detected: {file_path}, error: {e}")
        return False
```

**Recovery:**
```python
try:
    saved_path = handle_file_upload(file_stream, session_id, filename)
except CorruptedFileError as e:
    # Notify user
    return {
        "status": "rejected",
        "error": "File is corrupted. Please re-upload.",
        "error_code": "CORRUPTED_FILE"
    }
```

#### Scenario 3: Session Timeout

**Detection:**
```python
def is_session_expired(session_id: str, timeout_hours: float = 24.0) -> bool:
    """Check if session has expired."""
    metadata = load_session_metadata(session_id)
    created_at = datetime.fromisoformat(metadata["created_at"])
    age = datetime.utcnow() - created_at
    return age.total_seconds() / 3600 > timeout_hours
```

**Handling:**
```python
if is_session_expired(session_id):
    # Archive or cleanup
    lifecycle_manager.archive_session(session_id)
    
    raise SessionExpiredError(
        f"Session {session_id} expired. Create a new session."
    )
```

#### Scenario 4: Concurrent File Access Conflict

**Detection and Recovery:**
```python
try:
    with file_lock(metadata_path, timeout=30.0):
        # Perform operations
        update_metadata(metadata_path, updates)
        
except TimeoutError:
    # Lock timeout - another process is holding lock
    logger.error(f"Lock timeout on {metadata_path}")
    
    # Retry with exponential backoff
    for attempt in range(3):
        time.sleep(2 ** attempt)
        try:
            with file_lock(metadata_path, timeout=30.0):
                update_metadata(metadata_path, updates)
                break
        except TimeoutError:
            continue
    else:
        raise ConcurrencyError("Could not acquire lock after retries")
```

### Recovery Strategies

| Error Type | Detection | Recovery Action | User Impact |
|------------|-----------|-----------------|-------------|
| Disk Full | Disk space check | Cleanup + archive | Temporary failure, retry |
| Corrupted Upload | File verification | Delete + request re-upload | Upload rejected |
| Session Timeout | Age check | Archive session | Create new session |
| Lock Timeout | File lock timeout | Retry with backoff | Slight delay |
| Invalid File Format | Validation check | Reject file | Upload rejected |
| Network Interruption | Upload incomplete | Resume or restart | Partial upload lost |

---

## Summary

This specification provides comprehensive guidelines for:

✅ **File Validation**: Clear rules for validating images, predictions, and configs  
✅ **File Organization**: Consistent directory structure and naming conventions  
✅ **Concurrent Processing**: Session isolation and file locking strategies  
✅ **Data Lifecycle**: Cleanup policies and archival procedures  
✅ **Integration**: Seamless integration with backend API and pipeline  
✅ **Error Handling**: Robust error detection and recovery mechanisms  

**Next Steps:**
1. Review and approve specifications
2. Implement validation logic in backend API
3. Create file management utilities
4. Set up monitoring for file operations
5. Test concurrent scenarios
6. Document operational procedures

---

**Document Version:** 1.0  
**Last Updated:** February 3, 2026  
**Maintained By:** Engineering Team  
**Related Documents:**
- [Backend API Architecture](backend_api_architecture.md)
- [Model Pipeline Integration](model_pipeline_integration.md)
- [Visualization Logic Design](visualization_logic_design.md)
