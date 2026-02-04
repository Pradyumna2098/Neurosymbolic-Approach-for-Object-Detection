"""Inference trigger endpoint for neurosymbolic object detection API.

This endpoint handles inference job triggering, validates job existence,
and starts inference processing in a background thread (prototype implementation).
"""

import logging
import threading
import time
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services import storage_service, inference_service

# Logger
logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models for inference configuration

class SAHIConfig(BaseModel):
    """SAHI (Slicing Aided Hyper Inference) configuration."""
    
    enabled: bool = Field(default=True, description="Enable SAHI sliced inference")
    slice_width: int = Field(default=640, ge=256, le=2048, description="Slice width in pixels")
    slice_height: int = Field(default=640, ge=256, le=2048, description="Slice height in pixels")
    overlap_ratio: float = Field(default=0.2, ge=0.0, le=0.5, description="Overlap ratio between slices")


class SymbolicReasoningConfig(BaseModel):
    """Symbolic reasoning configuration."""
    
    enabled: bool = Field(default=True, description="Enable symbolic reasoning with Prolog")
    rules_file: Optional[str] = Field(default=None, description="Path to Prolog rules file")


class VisualizationConfig(BaseModel):
    """Visualization configuration."""
    
    enabled: bool = Field(default=True, description="Enable visualization generation")
    show_labels: bool = Field(default=True, description="Display class labels on visualizations")
    confidence_display: bool = Field(default=True, description="Display confidence scores")


class InferenceConfig(BaseModel):
    """Complete inference configuration."""
    
    model_config = {"protected_namespaces": ()}  # Allow model_ prefix
    
    model_path: str = Field(..., description="Path to trained YOLO model weights")
    confidence_threshold: float = Field(default=0.25, ge=0.0, le=1.0, description="Minimum confidence threshold")
    iou_threshold: float = Field(default=0.45, ge=0.0, le=1.0, description="IoU threshold for NMS")
    sahi: SAHIConfig = Field(default_factory=SAHIConfig, description="SAHI configuration")
    symbolic_reasoning: SymbolicReasoningConfig = Field(
        default_factory=SymbolicReasoningConfig, 
        description="Symbolic reasoning configuration"
    )
    visualization: VisualizationConfig = Field(
        default_factory=VisualizationConfig,
        description="Visualization configuration"
    )


class PredictRequest(BaseModel):
    """Request body for inference prediction."""
    
    job_id: str = Field(..., description="Job identifier from upload endpoint")
    config: InferenceConfig = Field(..., description="Inference configuration")


class PredictResponse(BaseModel):
    """Response for successful inference job creation."""
    
    status: str = Field(default="accepted", description="Response status")
    message: str = Field(default="Inference job started", description="Status message")
    job_id: str = Field(..., description="Job identifier")
    job_status: str = Field(..., description="Current job status")


def run_inference(job_id: str, config: InferenceConfig) -> None:
    """Run SAHI + YOLO inference in background thread.
    
    This function loads the YOLO model, runs SAHI sliced inference on all
    uploaded images, and saves predictions to the job's results directory.
    
    Args:
        job_id: Job identifier
        config: Inference configuration
    """
    try:
        logger.info(f"Starting inference for job {job_id}")
        
        # Run SAHI inference using the inference service
        inference_service.run_inference(
            job_id=job_id,
            model_path=config.model_path,
            confidence_threshold=config.confidence_threshold,
            iou_threshold=config.iou_threshold,
            sahi_config=config.sahi.model_dump(),
            device=None  # Auto-detect GPU/CPU
        )
        
        logger.info(f"Inference completed for job {job_id}")
        
    except Exception as e:
        # Error handling is done inside inference_service.run_inference
        # This just logs at the endpoint level
        logger.error(f"Inference error for job {job_id}: {str(e)}", exc_info=True)


@router.post("/predict", response_model=PredictResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_inference(request: PredictRequest) -> PredictResponse:
    """Trigger inference job for uploaded images.
    
    Validates that the job exists and has uploaded files, then starts
    inference processing in a background thread.
    
    Args:
        request: Prediction request with job_id and configuration
        
    Returns:
        PredictResponse: Accepted response with job information
        
    Raises:
        HTTPException: 404 if job not found, 400 if job status invalid
    """
    job_id = request.job_id
    config = request.config
    
    # Validate job exists
    job_data = storage_service.get_job(job_id)
    if job_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "error",
                "message": f"Job not found: {job_id}",
                "code": "JOB_NOT_FOUND"
            }
        )
    
    # Validate job has uploaded files
    if not job_data.get("files") or len(job_data["files"]) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": f"Job {job_id} has no uploaded files",
                "code": "NO_FILES"
            }
        )
    
    # Validate job status is "uploaded" (ready for inference)
    current_status = job_data.get("status")
    if current_status != "uploaded":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": f"Job {job_id} is not ready for inference. Current status: {current_status}",
                "code": "INVALID_STATUS"
            }
        )
    
    # Update job status to "processing"
    storage_service.update_job(
        job_id,
        status="processing",
        config=config.model_dump(),
        progress={
            "stage": "queued",
            "message": "Inference job queued"
        }
    )
    
    # Start inference in background thread
    # NOTE: Prototype implementation using threading (not Celery)
    # LIMITATION: Potential race condition exists in storage_service.update_job()
    # which uses read-modify-write without file locking. The endpoint prevents
    # concurrent inference on same job by checking status != "uploaded", but
    # this is not atomic. For production, consider:
    # - File locking in storage service (per file_data_handling_specifications.md)
    # - Task queue with atomic operations (Celery)
    # - Optimistic locking with version numbers
    inference_thread = threading.Thread(
        target=run_inference,
        args=(job_id, config),
        daemon=True  # Daemon thread will not prevent program exit
    )
    inference_thread.start()
    
    logger.info(f"Inference job started for {job_id} in background thread")
    
    # Return 202 Accepted immediately
    return PredictResponse(
        status="accepted",
        message="Inference job started",
        job_id=job_id,
        job_status="processing"
    )
