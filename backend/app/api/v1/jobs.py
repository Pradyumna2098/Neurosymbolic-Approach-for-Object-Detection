"""Job status endpoint for tracking inference job progress.

This endpoint allows clients to poll for job status and progress information
by reading from local JSON files in the data/jobs directory.
"""

import logging
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from fastapi import APIRouter, HTTPException, status

from app.models.responses import (
    ClassSummary,
    Detection,
    DetectionBBox,
    ImageResult,
    JobError,
    JobProgress,
    JobResultsData,
    JobResultsResponse,
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


def _parse_yolo_prediction_line(line: str) -> Optional[Tuple[int, float, float, float, float, float]]:
    """Parse a single line from YOLO format prediction file.
    
    Args:
        line: Single line from prediction file
        
    Returns:
        Tuple of (class_id, center_x, center_y, width, height, confidence) or None if invalid
    """
    parts = line.strip().split()
    if len(parts) != 6:
        return None
    
    try:
        class_id = int(float(parts[0]))
        center_x = float(parts[1])
        center_y = float(parts[2])
        width = float(parts[3])
        height = float(parts[4])
        confidence = float(parts[5])
        return (class_id, center_x, center_y, width, height, confidence)
    except (ValueError, IndexError):
        return None


def _parse_prediction_files(results_dir: Path) -> Dict[str, List[Detection]]:
    """Parse YOLO format prediction files from results directory.
    
    Args:
        results_dir: Directory containing .txt prediction files
        
    Returns:
        Dictionary mapping image names to list of Detection objects
    """
    predictions: Dict[str, List[Detection]] = defaultdict(list)
    
    if not results_dir.exists():
        return predictions
    
    for pred_file in results_dir.iterdir():
        if pred_file.suffix.lower() != ".txt":
            continue
        
        # Image name is the .txt filename with .png extension
        image_name = pred_file.stem + ".png"

        # Ensure an entry exists even if the file has no valid detections
        if image_name not in predictions:
            predictions[image_name] = []
        
        with open(pred_file, "r", encoding="utf-8") as f:
            for line in f:
                parsed = _parse_yolo_prediction_line(line)
                if parsed is None:
                    continue
                
                class_id, cx, cy, w, h, conf = parsed
                
                # Create detection with YOLO format bounding box
                detection = Detection(
                    class_id=class_id,
                    confidence=conf,
                    bbox=DetectionBBox(
                        format="yolo",
                        center_x=cx,
                        center_y=cy,
                        width=w,
                        height=h
                    )
                )
                predictions[image_name].append(detection)
    
    return predictions


def _calculate_class_distribution(predictions: Dict[str, List[Detection]]) -> List[ClassSummary]:
    """Calculate class distribution from predictions.
    
    Args:
        predictions: Dictionary mapping image names to detections
        
    Returns:
        List of ClassSummary objects with counts and average confidence per class
    """
    class_stats: Dict[int, Dict[str, Any]] = defaultdict(lambda: {"count": 0, "total_confidence": 0.0})
    
    for detections in predictions.values():
        for detection in detections:
            class_id = detection.class_id
            class_stats[class_id]["count"] += 1
            class_stats[class_id]["total_confidence"] += detection.confidence
    
    summaries = []
    for class_id, stats in sorted(class_stats.items()):
        avg_conf = stats["total_confidence"] / stats["count"] if stats["count"] > 0 else 0.0
        summaries.append(
            ClassSummary(
                class_id=class_id,
                count=stats["count"],
                average_confidence=avg_conf
            )
        )
    
    return summaries


@router.get("/jobs/{job_id}/results", response_model=JobResultsResponse, status_code=status.HTTP_200_OK)
async def get_job_results(job_id: str) -> JobResultsResponse:
    """Get prediction results for a completed job.
    
    Reads YOLO format prediction files from the results directory and returns
    structured JSON with per-image detections and summary statistics.
    
    Args:
        job_id: Job identifier (UUID)
        
    Returns:
        JobResultsResponse: Prediction results with detections per image
        
    Raises:
        HTTPException: 404 if job not found or results not available
    """
    logger.info(f"Retrieving results for job {job_id}")
    
    # Check if job exists
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
    
    # Check if job is completed
    job_status = job_data.get("status", "unknown")
    if job_status != "completed":
        logger.warning(f"Results not available for job {job_id} (status: {job_status})")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "error",
                "message": "Results not available",
                "error_code": "RESULTS_NOT_READY",
                "details": f"Job is {job_status}"
            }
        )
    
    # Read prediction files from refined results directory
    results_dir = storage_service._get_job_results_dir(job_id, stage="refined")
    predictions = _parse_prediction_files(results_dir)
    
    # If no predictions found, check if results directory is empty
    if not predictions:
        logger.warning(f"No prediction files found for job {job_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "error",
                "message": "Results not available",
                "error_code": "RESULTS_NOT_FOUND",
                "details": "No prediction files found in results directory"
            }
        )
    
    # Get file metadata from job data
    job_files = job_data.get("files", [])
    file_id_map: Dict[str, Dict[str, Any]] = {}
    for f in job_files:
        stored_filename = f.get("stored_filename")
        key: Optional[str]
        if stored_filename:
            # Use Path.stem to robustly strip the extension (handles multiple dots)
            key = Path(stored_filename).stem
        else:
            # Fallback to file_id if stored_filename is missing or empty
            file_id_value = f.get("file_id")
            key = str(file_id_value) if file_id_value is not None else None
        
        if key:
            file_id_map[key] = f
    
    # Build per-image results
    image_results = []
    total_detections = 0
    
    for image_name, detections in predictions.items():
        # Try to find original filename from job files
        base_name = Path(image_name).stem
        file_info = file_id_map.get(base_name)
        
        if file_info:
            file_id = file_info["file_id"]
            original_filename = file_info["filename"]
        else:
            # Fallback if file info not found
            file_id = base_name
            original_filename = image_name
        
        detection_count = len(detections)
        total_detections += detection_count
        
        image_result = ImageResult(
            file_id=file_id,
            filename=original_filename,
            detections=detections,
            detection_count=detection_count
        )
        image_results.append(image_result)
    
    # Calculate class distribution
    class_distribution = _calculate_class_distribution(predictions)
    
    # Build response
    results_data = JobResultsData(
        job_id=job_id,
        format="json",
        total_images=len(image_results),
        total_detections=total_detections,
        class_distribution=class_distribution,
        results=image_results
    )
    
    logger.info(f"Job {job_id} results: {total_detections} detections across {len(image_results)} images")
    
    return JobResultsResponse(
        status="success",
        data=results_data
    )
