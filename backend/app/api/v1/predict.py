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

from app.services import storage_service
from app.services.inference import inference_service, InferenceError

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
    """Run inference using SAHI and YOLO model in background thread.
    
    This function integrates the actual SAHI inference pipeline:
    1. Loads YOLO model from config.model_path
    2. Runs SAHI sliced prediction on all uploaded images
    3. Saves predictions to data/results/{job_id}/raw/ in YOLO format
    4. Updates job status and progress throughout processing
    
    Args:
        job_id: Job identifier
        config: Inference configuration with model path and parameters
    """
    try:
        logger.info(f"Starting SAHI inference for job {job_id}")
        
        # Extract configuration
        model_path = config.model_path
        confidence_threshold = config.confidence_threshold
        iou_threshold = config.iou_threshold
        
        # Prepare SAHI configuration
        sahi_config = {}
        if config.sahi.enabled:
            sahi_config = {
                'slice_width': config.sahi.slice_width,
                'slice_height': config.sahi.slice_height,
                'overlap_ratio': config.sahi.overlap_ratio,
            }
            logger.info(f"SAHI enabled: {sahi_config}")
        else:
            # Use full image inference (no slicing)
            logger.info("SAHI disabled, using full image inference")
            sahi_config = {
                'slice_width': 999999,  # Large value to process full image
                'slice_height': 999999,
                'overlap_ratio': 0.0,
            }
        
        # Prepare symbolic reasoning configuration
        symbolic_config = {
            'enabled': config.symbolic_reasoning.enabled,
            'rules_file': config.symbolic_reasoning.rules_file,
        }
        
        # Prepare visualization configuration
        visualization_config = {
            'enabled': config.visualization.enabled,
            'show_labels': config.visualization.show_labels,
            'confidence_display': config.visualization.confidence_display,
        }
        
        # Run inference using the inference service
        inference_stats = inference_service.run_inference(
            job_id=job_id,
            model_path=model_path,
            confidence_threshold=confidence_threshold,
            iou_threshold=iou_threshold,
            sahi_config=sahi_config,
            storage_service=storage_service,
            symbolic_config=symbolic_config,
            visualization_config=visualization_config,
        )
        
        logger.info(
            f"Inference completed for job {job_id}: "
            f"{inference_stats['processed_images']}/{inference_stats['total_images']} images, "
            f"{inference_stats['total_detections']} detections"
        )
        
    except InferenceError as e:
        # Handle inference-specific errors
        error_message = f"Inference failed: {str(e)}"
        logger.error(f"Inference error for job {job_id}: {error_message}", exc_info=True)
        
        storage_service.update_job(
            job_id,
            status="failed",
            error=error_message,
            progress={
                "stage": "failed",
                "message": error_message
            }
        )
    except Exception as e:
        # Handle unexpected errors
        error_message = f"Unexpected error during inference: {str(e)}"
        logger.error(f"Unexpected error for job {job_id}: {error_message}", exc_info=True)
        
        storage_service.update_job(
            job_id,
            status="failed",
            error=error_message,
            progress={
                "stage": "failed",
                "message": error_message
            }
        )


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

