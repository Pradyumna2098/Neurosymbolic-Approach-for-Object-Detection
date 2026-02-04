"""Pydantic models for API request/response schemas."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(..., description="Current server timestamp")
    version: str = Field(..., description="API version")
    message: str = Field(default="Service is healthy", description="Status message")


class ErrorDetail(BaseModel):
    """Detailed error information."""
    
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[str] = Field(None, description="Additional error context")
    field: Optional[str] = Field(None, description="Field name for validation errors")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Error timestamp"
    )


class ErrorResponse(BaseModel):
    """Standard error response format."""
    
    status: str = Field(default="error", description="Response status")
    error: ErrorDetail = Field(..., description="Error details")


class SuccessResponse(BaseModel):
    """Generic success response."""
    
    status: str = Field(default="success", description="Response status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Optional response data")


class UploadedFileInfo(BaseModel):
    """Information about a single uploaded file."""
    
    filename: str = Field(..., description="Original filename")
    size: int = Field(..., description="File size in bytes")
    file_id: Optional[str] = Field(None, description="Unique file identifier")
    format: Optional[str] = Field(None, description="Image format (e.g., JPEG, PNG)")
    width: Optional[int] = Field(None, description="Image width in pixels")
    height: Optional[int] = Field(None, description="Image height in pixels")


class FileValidationWarning(BaseModel):
    """Warning for a file that failed validation."""
    
    filename: str = Field(..., description="Name of the file that failed")
    error: str = Field(..., description="Validation error message")


class UploadResponse(BaseModel):
    """Response for successful file upload."""
    
    status: str = Field(default="success", description="Response status")
    job_id: str = Field(..., description="Unique job identifier for tracking")
    files: List[UploadedFileInfo] = Field(..., description="List of uploaded files with metadata")
    warnings: Optional[List[FileValidationWarning]] = Field(None, description="Warnings for files that failed validation (partial success)")


class JobProgress(BaseModel):
    """Job progress information."""
    
    stage: Optional[str] = Field(None, description="Current processing stage")
    message: Optional[str] = Field(None, description="Progress message")
    percentage: Optional[float] = Field(None, ge=0, le=100, description="Progress percentage (0-100)")
    total_images: Optional[int] = Field(None, description="Total number of images to process")
    processed_images: Optional[int] = Field(None, description="Number of images processed")


class JobSummary(BaseModel):
    """Summary information for completed jobs."""
    
    total_detections: Optional[int] = Field(None, description="Total number of detections")
    average_confidence: Optional[float] = Field(None, ge=0, le=1, description="Average confidence score")
    processing_time_seconds: Optional[float] = Field(None, description="Total processing time in seconds")


class JobError(BaseModel):
    """Error information for failed jobs."""
    
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[str] = Field(None, description="Additional error details")


class JobStatusData(BaseModel):
    """Job status data."""
    
    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Job status (queued, processing, completed, failed)")
    created_at: str = Field(..., description="Job creation timestamp (ISO 8601)")
    updated_at: Optional[str] = Field(None, description="Last update timestamp (ISO 8601)")
    started_at: Optional[str] = Field(None, description="Processing start timestamp (ISO 8601)")
    completed_at: Optional[str] = Field(None, description="Completion timestamp (ISO 8601)")
    failed_at: Optional[str] = Field(None, description="Failure timestamp (ISO 8601)")
    progress: Optional[JobProgress] = Field(None, description="Progress information")
    summary: Optional[JobSummary] = Field(None, description="Summary for completed jobs")
    error: Optional[JobError] = Field(None, description="Error details for failed jobs")
    results_url: Optional[str] = Field(None, description="URL to retrieve results (for completed jobs)")
    visualization_url: Optional[str] = Field(None, description="URL to retrieve visualizations (for completed jobs)")


class JobStatusResponse(BaseModel):
    """Response for job status endpoint."""
    
    status: str = Field(default="success", description="Response status")
    data: JobStatusData = Field(..., description="Job status data")


class DetectionBBox(BaseModel):
    """Bounding box coordinates for a detection."""
    
    format: str = Field(..., description="Coordinate format (yolo or xyxy)")
    center_x: Optional[float] = Field(None, description="Normalized center X (YOLO format)")
    center_y: Optional[float] = Field(None, description="Normalized center Y (YOLO format)")
    width: Optional[float] = Field(None, description="Normalized width (YOLO format)")
    height: Optional[float] = Field(None, description="Normalized height (YOLO format)")
    x_min: Optional[float] = Field(None, description="Absolute X minimum (xyxy format)")
    y_min: Optional[float] = Field(None, description="Absolute Y minimum (xyxy format)")
    x_max: Optional[float] = Field(None, description="Absolute X maximum (xyxy format)")
    y_max: Optional[float] = Field(None, description="Absolute Y maximum (xyxy format)")


class Detection(BaseModel):
    """Individual object detection."""
    
    class_id: int = Field(..., description="Class ID of detected object")
    class_name: Optional[str] = Field(None, description="Class name (if available)")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence score")
    bbox: DetectionBBox = Field(..., description="Bounding box coordinates")


class ImageResult(BaseModel):
    """Detection results for a single image."""
    
    file_id: str = Field(..., description="File identifier")
    filename: str = Field(..., description="Original filename")
    detections: List[Detection] = Field(..., description="List of detections")
    detection_count: int = Field(..., description="Total number of detections")


class ClassSummary(BaseModel):
    """Summary of detections by class."""
    
    class_id: int = Field(..., description="Class ID")
    class_name: Optional[str] = Field(None, description="Class name (if available)")
    count: int = Field(..., description="Number of detections for this class")
    average_confidence: float = Field(..., ge=0, le=1, description="Average confidence for this class")


class JobResultsData(BaseModel):
    """Results data for a completed job."""
    
    job_id: str = Field(..., description="Job identifier")
    format: str = Field(default="json", description="Output format")
    total_images: int = Field(..., description="Total number of images processed")
    total_detections: int = Field(..., description="Total number of detections across all images")
    class_distribution: List[ClassSummary] = Field(..., description="Distribution of detections by class")
    results: List[ImageResult] = Field(..., description="Per-image detection results")


class JobResultsResponse(BaseModel):
    """Response for job results endpoint."""
    
    status: str = Field(default="success", description="Response status")
    data: JobResultsData = Field(..., description="Job results data")


class VisualizationItem(BaseModel):
    """Metadata for a single visualization image."""
    
    file_id: str = Field(..., description="File identifier")
    filename: str = Field(..., description="Original filename")
    original_url: str = Field(..., description="URL to original image")
    annotated_url: str = Field(..., description="URL to annotated image")
    detection_count: int = Field(..., description="Number of detections in image")


class VisualizationData(BaseModel):
    """Visualization data for a job."""
    
    job_id: str = Field(..., description="Job identifier")
    visualizations: List[VisualizationItem] = Field(..., description="List of visualization items")


class VisualizationResponse(BaseModel):
    """Response for visualization endpoint with URLs."""
    
    status: str = Field(default="success", description="Response status")
    data: VisualizationData = Field(..., description="Visualization data")


class Base64VisualizationData(BaseModel):
    """Base64-encoded visualization data for a single image."""
    
    file_id: str = Field(..., description="File identifier")
    filename: str = Field(..., description="Original filename")
    format: str = Field(default="base64", description="Response format")
    original_image: str = Field(..., description="Base64-encoded original image with data URI prefix")
    annotated_image: str = Field(..., description="Base64-encoded annotated image with data URI prefix")
    detection_count: int = Field(..., description="Number of detections in image")


class Base64VisualizationResponse(BaseModel):
    """Response for visualization endpoint with base64 encoding."""
    
    status: str = Field(default="success", description="Response status")
    data: Base64VisualizationData = Field(..., description="Base64 visualization data")
