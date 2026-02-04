"""Job status endpoint for tracking inference job progress.

This endpoint allows clients to poll for job status and progress information
by reading from local JSON files in the data/jobs directory.
"""

import logging
from typing import Any, Dict, Optional, Union

from fastapi import APIRouter, HTTPException, status

from app.models.responses import (
    JobError,
    JobProgress,
    JobStatusData,
    JobStatusResponse,
    JobSummary,
)
from app.services import storage_service

# Logger
logger = logging.getLogger(__name__)

router = APIRouter()


def _parse_progress(progress_data: Optional[Dict[str, Any]]) -> Optional[JobProgress]:
    """Parse progress data from job JSON into JobProgress model.
    
    Args:
        progress_data: Progress dictionary from job JSON
        
    Returns:
        JobProgress model or None if no progress data
    """
    if not progress_data:
        return None
    
    return JobProgress(
        stage=progress_data.get("stage"),
        message=progress_data.get("message"),
        percentage=progress_data.get("percentage"),
        total_images=progress_data.get("total_images"),
        processed_images=progress_data.get("processed_images"),
    )


def _parse_summary(summary_data: Optional[Dict[str, Any]]) -> Optional[JobSummary]:
    """Parse summary data from job JSON into JobSummary model.
    
    Args:
        summary_data: Summary dictionary from job JSON
        
    Returns:
        JobSummary model or None if no summary data
    """
    if not summary_data:
        return None
    
    return JobSummary(
        total_detections=summary_data.get("total_detections"),
        average_confidence=summary_data.get("average_confidence"),
        processing_time_seconds=summary_data.get("processing_time_seconds"),
    )


def _parse_error(error_data: Optional[Union[str, Dict[str, Any]]]) -> Optional[JobError]:
    """Parse error data from job JSON into JobError model.
    
    Args:
        error_data: Error data from job JSON (can be string or dict)
        
    Returns:
        JobError model or None if no error data
    """
    if not error_data:
        return None
    
    # Handle both string and dict error formats
    if isinstance(error_data, str):
        return JobError(
            code="ERROR",
            message=error_data,
        )
    elif isinstance(error_data, dict):
        return JobError(
            code=error_data.get("code", "ERROR"),
            message=error_data.get("message", "Unknown error"),
            details=error_data.get("details"),
        )
    
    return None


@router.get("/jobs/{job_id}/status", response_model=JobStatusResponse, status_code=status.HTTP_200_OK)
async def get_job_status(job_id: str) -> JobStatusResponse:
    """Get current status of an inference job.
    
    Reads job status from local JSON file and returns formatted response
    with progress information, timestamps, and results URLs.
    
    Args:
        job_id: Job identifier (UUID)
        
    Returns:
        JobStatusResponse: Current job status and progress
        
    Raises:
        HTTPException: 404 if job not found
    """
    logger.info(f"Retrieving status for job {job_id}")
    
    # Read job data from file
    job_data = storage_service.get_job(job_id)
    
    if job_data is None:
        logger.warning(f"Job not found: {job_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "error",
                "message": f"Job not found: {job_id}",
                "error_code": "JOB_NOT_FOUND"
            }
        )
    
    # Extract job status and timestamps
    job_status = job_data.get("status", "unknown")
    
    # Parse progress data
    progress = _parse_progress(job_data.get("progress", {}))
    
    # Parse summary data (for completed jobs)
    summary = None
    if job_status == "completed":
        summary = _parse_summary(job_data.get("summary", {}))
    
    # Parse error data (for failed jobs)
    error = None
    if job_status == "failed":
        error = _parse_error(job_data.get("error"))
    
    # Generate result URLs for completed jobs
    results_url = None
    visualization_url = None
    if job_status == "completed":
        results_url = f"/api/v1/jobs/{job_id}/results"
        visualization_url = f"/api/v1/jobs/{job_id}/visualization"
    
    # Build response data
    status_data = JobStatusData(
        job_id=job_id,
        status=job_status,
        created_at=job_data.get("created_at", ""),
        updated_at=job_data.get("updated_at"),
        started_at=job_data.get("started_at"),
        completed_at=job_data.get("completed_at"),
        failed_at=job_data.get("failed_at"),
        progress=progress,
        summary=summary,
        error=error,
        results_url=results_url,
        visualization_url=visualization_url,
    )
    
    logger.info(f"Job {job_id} status: {job_status}")
    
    return JobStatusResponse(
        status="success",
        data=status_data
    )
