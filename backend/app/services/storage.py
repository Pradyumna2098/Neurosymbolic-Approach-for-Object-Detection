"""File storage service for managing uploads, jobs, and results.

This service provides file validation, storage management, and job tracking
for the neurosymbolic object detection system. It uses local filesystem storage
with organized directory structures and UUID-based file identification.

Note: This service supersedes app.storage.local.LocalStorageService with enhanced
features including PIL/Pillow validation, metadata extraction, and multi-stage
result storage. The LocalStorageService is kept for backward compatibility but
new code should use this StorageService implementation.
"""

import json
import re
import uuid
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image

from app.core import settings


def _sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and other attacks.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem use
        
    Raises:
        ValueError: If filename is invalid or contains dangerous patterns
    """
    # Extract basename to prevent path traversal
    basename = Path(filename).name
    
    # Reject empty filenames or filenames starting with dots
    if not basename or basename.startswith('.'):
        raise ValueError(f"Invalid filename: {filename}")
    
    # Only allow alphanumeric, underscores, hyphens, and dots
    # This prevents special characters and shell metacharacters
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', basename):
        raise ValueError(f"Filename contains invalid characters: {filename}")
    
    # Ensure there's an extension
    if '.' not in basename:
        raise ValueError(f"Filename must have an extension: {filename}")
    
    return basename


def _validate_job_id(job_id: str) -> None:
    """Validate job_id to prevent path traversal attacks.
    
    Args:
        job_id: Job identifier to validate
        
    Raises:
        ValueError: If job_id is not a valid UUID
    """
    try:
        # Verify it's a valid UUID
        uuid.UUID(job_id)
    except (ValueError, AttributeError):
        raise ValueError(f"Invalid job_id: must be a valid UUID, got: {job_id}")


class FileValidationError(Exception):
    """Raised when file validation fails."""
    
    pass


class StorageService:
    """Service for managing file storage and job tracking."""
    
    # Supported image formats per specification
    # Note: BMP is not officially supported per specification but included for compatibility
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB per specification
    MIN_FILE_SIZE = 1024  # 1KB minimum
    MIN_DIMENSIONS = (64, 64)  # Minimum width, height
    MAX_DIMENSIONS = (8192, 8192)  # Maximum width, height
    
    def __init__(self):
        """Initialize storage service and ensure directories exist."""
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Create all required data directories if they don't exist."""
        settings.ensure_directories()
    
    def _get_job_upload_dir(self, job_id: str) -> Path:
        """Get upload directory for a specific job.
        
        Args:
            job_id: Job identifier (must be valid UUID)
            
        Returns:
            Path to job's upload directory
            
        Raises:
            ValueError: If job_id is not a valid UUID
        """
        _validate_job_id(job_id)
        job_dir = settings.uploads_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        return job_dir
    
    def _get_job_results_dir(self, job_id: str, stage: str = "raw") -> Path:
        """Get results directory for a specific job and stage.
        
        Args:
            job_id: Job identifier (must be valid UUID)
            stage: Processing stage ('raw', 'nms', or 'refined')
            
        Returns:
            Path to job's results directory for the specified stage
            
        Raises:
            ValueError: If job_id is not a valid UUID
        """
        _validate_job_id(job_id)
        job_results_dir = settings.results_dir / job_id / stage
        job_results_dir.mkdir(parents=True, exist_ok=True)
        return job_results_dir
    
    def _get_job_visualization_dir(self, job_id: str) -> Path:
        """Get visualization directory for a specific job.
        
        Args:
            job_id: Job identifier (must be valid UUID)
            
        Returns:
            Path to job's visualization directory
            
        Raises:
            ValueError: If job_id is not a valid UUID
        """
        _validate_job_id(job_id)
        job_viz_dir = settings.visualizations_dir / job_id
        job_viz_dir.mkdir(parents=True, exist_ok=True)
        return job_viz_dir
    
    def validate_image_file(
        self, 
        content: bytes, 
        filename: str
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """Validate image file format, size, and integrity using PIL/Pillow.
        
        Args:
            content: File content as bytes
            filename: Original filename
            
        Returns:
            Tuple of (is_valid, error_message, metadata)
            - is_valid: True if file passes all validations
            - error_message: Description of validation failure (None if valid)
            - metadata: Dict with image info (width, height, format, mode)
        """
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.SUPPORTED_FORMATS:
            return (
                False, 
                f"INVALID_FORMAT: Unsupported format '{file_ext}'. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}",
                None
            )
        
        # Check file size
        file_size = len(content)
        if file_size < self.MIN_FILE_SIZE:
            return (
                False,
                f"FILE_TOO_SMALL: Image file is suspiciously small. "
                f"Minimum: 1KB, got: {file_size} bytes",
                None
            )
        
        if file_size > self.MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            return (
                False,
                f"FILE_TOO_LARGE: Image exceeds 50MB limit. "
                f"Current size: {size_mb:.2f}MB",
                None
            )
        
        # Validate image integrity and extract metadata using PIL
        try:
            image = Image.open(BytesIO(content))
            
            # Verify image can be decoded (corruption check)
            image.verify()
            
            # Re-open to extract metadata (verify() closes the file)
            image = Image.open(BytesIO(content))
            
            width, height = image.size
            image_format = image.format
            color_mode = image.mode
            
            # Check dimensions
            if width < self.MIN_DIMENSIONS[0] or height < self.MIN_DIMENSIONS[1]:
                return (
                    False,
                    f"DIMENSIONS_TOO_SMALL: Image dimensions {width}x{height} "
                    f"below minimum {self.MIN_DIMENSIONS[0]}x{self.MIN_DIMENSIONS[1]}",
                    None
                )
            
            if width > self.MAX_DIMENSIONS[0] or height > self.MAX_DIMENSIONS[1]:
                return (
                    False,
                    f"DIMENSIONS_EXCEEDED: Image dimensions {width}x{height} "
                    f"exceed maximum {self.MAX_DIMENSIONS[0]}x{self.MAX_DIMENSIONS[1]}",
                    None
                )
            
            # Verify format matches extension (header validation)
            expected_formats = {
                '.jpg': ['JPEG'],
                '.jpeg': ['JPEG'],
                '.png': ['PNG'],
                '.tiff': ['TIFF'],
                '.tif': ['TIFF'],
                '.bmp': ['BMP']
            }
            
            if image_format not in expected_formats.get(file_ext, []):
                return (
                    False,
                    f"INVALID_FORMAT: File extension '{file_ext}' does not match "
                    f"content format '{image_format}'",
                    None
                )
            
            # Extract metadata
            metadata = {
                'width': width,
                'height': height,
                'format': image_format,
                'mode': color_mode,
                'size_bytes': file_size
            }
            
            return True, None, metadata
            
        except Exception as e:
            return (
                False,
                f"CORRUPTED_FILE: Image file is corrupted and cannot be read. "
                f"Error: {str(e)}",
                None
            )
    
    # Job Management Methods
    
    def create_job(self, config: Optional[Dict[str, Any]] = None) -> str:
        """Create a new job with unique ID and initial status.
        
        Args:
            config: Optional job configuration parameters
            
        Returns:
            Generated job ID (UUID)
        """
        job_id = str(uuid.uuid4())
        
        job_data = {
            "job_id": job_id,
            "status": "queued",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "config": config or {},
            "files": [],
            "progress": {},
            "error": None
        }
        
        job_file = settings.jobs_dir / f"{job_id}.json"
        with open(job_file, "w") as f:
            json.dump(job_data, f, indent=2)
        
        # Create job directories
        self._get_job_upload_dir(job_id)
        self._get_job_visualization_dir(job_id)
        for stage in ["raw", "nms", "refined"]:
            self._get_job_results_dir(job_id, stage)
        
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve job data by ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job data dictionary or None if not found
        """
        job_file = settings.jobs_dir / f"{job_id}.json"
        if not job_file.exists():
            return None
        
        with open(job_file, "r") as f:
            return json.load(f)
    
    def update_job(
        self, 
        job_id: str, 
        status: Optional[str] = None,
        progress: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        **kwargs
    ) -> bool:
        """Update job data.
        
        Args:
            job_id: Job identifier
            status: New job status ('queued', 'processing', 'completed', 'failed')
            progress: Progress information dictionary
            error: Error message (for failed jobs)
            **kwargs: Additional fields to update
            
        Returns:
            True if successful, False if job not found
        """
        job_data = self.get_job(job_id)
        if job_data is None:
            return False
        
        # Update provided fields
        if status is not None:
            job_data["status"] = status
        if progress is not None:
            job_data["progress"] = progress
        if error is not None:
            job_data["error"] = error
        
        # Update any additional fields
        job_data.update(kwargs)
        
        # Add updated timestamp
        job_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        job_file = settings.jobs_dir / f"{job_id}.json"
        with open(job_file, "w") as f:
            json.dump(job_data, f, indent=2)
        
        return True
    
    def list_jobs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all jobs sorted by creation time (newest first).
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of job data dictionaries
        """
        jobs = []
        job_files = sorted(
            settings.jobs_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:limit]
        
        for job_file in job_files:
            with open(job_file, "r") as f:
                jobs.append(json.load(f))
        
        return jobs
    
    # File Management Methods
    
    def save_upload(
        self, 
        job_id: str,
        filename: str, 
        content: bytes,
        validate: bool = True
    ) -> Tuple[str, Path, Optional[Dict[str, Any]]]:
        """Save uploaded file for a specific job.
        
        Args:
            job_id: Job identifier (must be valid UUID)
            filename: Original filename
            content: File content as bytes
            validate: Whether to validate the file (default: True)
            
        Returns:
            Tuple of (file_id, file_path, metadata)
            - file_id: Unique file identifier
            - file_path: Path to saved file
            - metadata: Image metadata dict (if validation enabled)
            
        Raises:
            FileValidationError: If validation fails
            ValueError: If filename contains invalid characters or job_id is invalid
        """
        # Sanitize filename to prevent path traversal and injection attacks
        try:
            sanitized_filename = _sanitize_filename(filename)
        except ValueError as e:
            raise FileValidationError(f"Invalid filename: {str(e)}")
        
        # Validate file if requested
        metadata = None
        if validate:
            is_valid, error_msg, metadata = self.validate_image_file(content, sanitized_filename)
            if not is_valid:
                raise FileValidationError(error_msg)
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Preserve original extension from sanitized filename
        file_ext = Path(sanitized_filename).suffix.lower()
        safe_filename = f"{file_id}{file_ext}"
        
        # Save to job's upload directory (validates job_id internally)
        job_upload_dir = self._get_job_upload_dir(job_id)
        file_path = job_upload_dir / safe_filename
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Update job's file list
        job_data = self.get_job(job_id)
        if job_data:
            job_data["files"].append({
                "file_id": file_id,
                "filename": sanitized_filename,  # Store sanitized filename
                "stored_filename": safe_filename,
                "size_bytes": len(content),
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
                "metadata": metadata
            })
            self.update_job(job_id, files=job_data["files"])
        
        return file_id, file_path, metadata
    
    def get_upload_path(self, job_id: str, file_id: str) -> Optional[Path]:
        """Get path to uploaded file by job_id and file_id.
        
        Args:
            job_id: Job identifier
            file_id: File identifier
            
        Returns:
            Path to file or None if not found
        """
        job_data = self.get_job(job_id)
        if not job_data:
            return None
        
        # Find file in job's file list
        for file_info in job_data.get("files", []):
            if file_info["file_id"] == file_id:
                stored_filename = file_info["stored_filename"]
                file_path = self._get_job_upload_dir(job_id) / stored_filename
                return file_path if file_path.exists() else None
        
        return None
    
    def save_result(
        self, 
        job_id: str, 
        result_data: Dict[str, Any],
        stage: str = "raw"
    ) -> Path:
        """Save prediction results for a job at a specific processing stage.
        
        Args:
            job_id: Job identifier
            result_data: Prediction results dictionary
            stage: Processing stage ('raw', 'nms', or 'refined')
            
        Returns:
            Path to saved results file
        """
        results_dir = self._get_job_results_dir(job_id, stage)
        result_file = results_dir / "predictions.json"
        
        with open(result_file, "w") as f:
            json.dump(result_data, f, indent=2)
        
        return result_file
    
    def get_result(self, job_id: str, stage: str = "refined") -> Optional[Dict[str, Any]]:
        """Retrieve prediction results for a job at a specific stage.
        
        Args:
            job_id: Job identifier
            stage: Processing stage ('raw', 'nms', or 'refined')
            
        Returns:
            Results dictionary or None if not found
        """
        results_dir = self._get_job_results_dir(job_id, stage)
        result_file = results_dir / "predictions.json"
        
        if not result_file.exists():
            return None
        
        with open(result_file, "r") as f:
            return json.load(f)
    
    def save_visualization(
        self, 
        job_id: str, 
        image_data: bytes, 
        filename: str = "annotated.png"
    ) -> Path:
        """Save visualization image for a job.
        
        Args:
            job_id: Job identifier
            image_data: Image content as bytes
            filename: Filename for the visualization
            
        Returns:
            Path to saved visualization
        """
        viz_dir = self._get_job_visualization_dir(job_id)
        viz_file = viz_dir / filename
        
        with open(viz_file, "wb") as f:
            f.write(image_data)
        
        return viz_file
    
    def get_visualization_path(
        self, 
        job_id: str, 
        filename: str = "annotated.png"
    ) -> Optional[Path]:
        """Get path to visualization image.
        
        Args:
            job_id: Job identifier
            filename: Visualization filename
            
        Returns:
            Path to visualization or None if not found
        """
        viz_dir = self._get_job_visualization_dir(job_id)
        viz_file = viz_dir / filename
        
        return viz_file if viz_file.exists() else None
    
    def list_job_files(self, job_id: str) -> List[Dict[str, Any]]:
        """List all files associated with a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            List of file information dictionaries
        """
        job_data = self.get_job(job_id)
        if not job_data:
            return []
        
        return job_data.get("files", [])


# Global storage service instance
storage_service = StorageService()
