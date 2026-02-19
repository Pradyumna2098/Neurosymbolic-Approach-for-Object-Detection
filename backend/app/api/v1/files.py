"""File serving endpoint for original and annotated images.

This endpoint serves image files from the local filesystem for visualization
purposes. It provides access to both original uploaded images and annotated
images with bounding boxes drawn.
"""

import logging

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from app.services import storage_service

# Logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/files/{job_id}/{file_id}/original")
async def get_original_image(job_id: str, file_id: str) -> FileResponse:
    """Serve original uploaded image.
    
    Args:
        job_id: Job identifier (UUID)
        file_id: File identifier (UUID)
        
    Returns:
        FileResponse: Binary image data
        
    Raises:
        HTTPException: 404 if image not found
    """
    logger.info(f"Serving original image for job {job_id}, file {file_id}")
    
    # Get upload path from storage service
    image_path = storage_service.get_upload_path(job_id, file_id)
    
    if image_path is None or not image_path.exists():
        logger.warning(f"Original image not found: job={job_id}, file={file_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "error",
                "message": "Original image not found",
                "error_code": "ORIGINAL_IMAGE_NOT_FOUND"
            }
        )
    
    # Determine media type from extension
    ext = image_path.suffix.lower()
    media_type = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".bmp": "image/bmp",
        ".tiff": "image/tiff",
        ".tif": "image/tiff"
    }.get(ext, "image/png")
    
    return FileResponse(
        path=image_path,
        media_type=media_type,
        filename=image_path.name
    )


@router.get("/files/{job_id}/{file_id}/annotated")
async def get_annotated_image(job_id: str, file_id: str) -> FileResponse:
    """Serve annotated image with bounding boxes.
    
    Args:
        job_id: Job identifier (UUID)
        file_id: File identifier (UUID)
        
    Returns:
        FileResponse: Binary image data with annotations
        
    Raises:
        HTTPException: 404 if image not found
    """
    logger.info(f"Serving annotated image for job {job_id}, file {file_id}")
    
    # Get job data to find stored filename
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
    
    # Find file in job files
    stored_filename = None
    for file_info in job_data.get("files", []):
        if file_info["file_id"] == file_id:
            stored_filename = file_info["stored_filename"]
            break
    
    if stored_filename is None:
        logger.warning(f"File not found in job: job={job_id}, file={file_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "error",
                "message": f"File not found: {file_id}",
                "error_code": "FILE_NOT_FOUND"
            }
        )
    
    # Get visualization path
    viz_dir = storage_service._get_job_visualization_dir(job_id)
    image_path = viz_dir / stored_filename
    
    if not image_path.exists():
        logger.warning(f"Annotated image not found: {image_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "error",
                "message": "Annotated image not found",
                "error_code": "ANNOTATED_IMAGE_NOT_FOUND",
                "details": "Visualization may not have been generated yet"
            }
        )
    
    # Determine media type from extension
    ext = image_path.suffix.lower()
    media_type = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".bmp": "image/bmp",
        ".tiff": "image/tiff",
        ".tif": "image/tiff"
    }.get(ext, "image/png")
    
    return FileResponse(
        path=image_path,
        media_type=media_type,
        filename=image_path.name
    )

