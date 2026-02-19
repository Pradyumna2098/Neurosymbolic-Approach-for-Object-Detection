"""Image upload endpoint for neurosymbolic object detection API.

This endpoint handles multipart/form-data image uploads, validates files,
saves them to the local filesystem organized by job_id, and creates job
metadata for tracking.
"""

import logging
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.models import UploadedFileInfo, UploadResponse
from app.services import storage_service, FileValidationError

# Constants
MAX_FILES_PER_UPLOAD = 100

# Logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_200_OK, tags=["Upload"])
async def upload_images(
    files: List[UploadFile] = File(..., description="Image files to upload (JPEG, PNG, TIFF, BMP)")
) -> UploadResponse:
    """Upload one or more images for inference.
    
    Accepts multiple image files via multipart/form-data, validates each file,
    saves them to the local filesystem, and creates a job for tracking.
    
    Args:
        files: List of uploaded image files
        
    Returns:
        UploadResponse: Contains job_id and metadata for uploaded files
        
    Raises:
        HTTPException: 400 if no files provided or validation fails
    """
    # Validate that at least one file was uploaded
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": "No files provided",
                "code": "NO_FILES"
            }
        )
    
    # Validate batch size limit
    if len(files) > MAX_FILES_PER_UPLOAD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": f"Too many files. Maximum {MAX_FILES_PER_UPLOAD} files per upload, got {len(files)}",
                "code": "TOO_MANY_FILES"
            }
        )
    
    uploaded_files = []
    validation_errors = []
    
    # Process each uploaded file first (before creating job)
    for upload_file in files:
        try:
            # Read file content
            content = await upload_file.read()
            
            # Validate file size (basic check before detailed validation)
            if len(content) == 0:
                validation_errors.append({
                    "filename": upload_file.filename,
                    "error": "File is empty"
                })
                continue
            
            # Store file info for later processing
            uploaded_files.append({
                "filename": upload_file.filename,
                "content": content
            })
            
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Unexpected error reading file {upload_file.filename}: {e}", exc_info=True)
            validation_errors.append({
                "filename": upload_file.filename,
                "error": f"Failed to read file: {str(e)}"
            })
    
    # If all files failed initial validation, return error without creating job
    if not uploaded_files and validation_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": "All files failed validation",
                "code": "VALIDATION_FAILED",
                "errors": validation_errors
            }
        )
    
    # Create job with status "uploaded" (single atomic operation)
    job_id = storage_service.create_job(
        config={"file_count": len(uploaded_files)},
        status="uploaded"
    )
    
    # Now save files and collect results
    successfully_uploaded = []
    
    for file_info in uploaded_files:
        try:
            # Save the file using storage service (includes validation)
            # Returns tuple: (file_id, file_path, metadata)
            file_id, file_path, metadata = storage_service.save_upload(
                job_id=job_id,
                filename=file_info["filename"],
                content=file_info["content"]
            )
            
            # Build response with file metadata
            successfully_uploaded.append(UploadedFileInfo(
                filename=file_info["filename"],
                size=len(file_info["content"]),
                file_id=file_id,
                format=metadata.get('format') if metadata else None,
                width=metadata.get('width') if metadata else None,
                height=metadata.get('height') if metadata else None
            ))
            
        except FileValidationError as e:
            # Log validation errors for debugging
            logger.warning(f"File validation failed for {file_info['filename']}: {e}")
            validation_errors.append({
                "filename": file_info["filename"],
                "error": str(e)
            })
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Unexpected error saving file {file_info['filename']}: {e}", exc_info=True)
            validation_errors.append({
                "filename": file_info["filename"],
                "error": f"Failed to save file: {str(e)}"
            })
    
    # If all files failed validation after job creation, clean up the job
    if not successfully_uploaded and validation_errors:
        # Clean up the orphaned job
        try:
            import shutil
            job_upload_dir = storage_service._get_job_upload_dir(job_id)
            if job_upload_dir.exists():
                shutil.rmtree(job_upload_dir.parent)  # Remove entire job directory
            
            # Remove job JSON
            from backend.app.core import settings
            job_file = settings.jobs_dir / f"{job_id}.json"
            if job_file.exists():
                job_file.unlink()
            
            logger.info(f"Cleaned up orphaned job {job_id} after all files failed validation")
        except Exception as cleanup_error:
            logger.error(f"Failed to clean up orphaned job {job_id}: {cleanup_error}")
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": "All files failed validation",
                "code": "VALIDATION_FAILED",
                "errors": validation_errors
            }
        )
    
    # Convert validation errors to warnings for partial success
    warnings = None
    if validation_errors:
        from backend.app.models import FileValidationWarning
        warnings = [
            FileValidationWarning(filename=err["filename"], error=err["error"])
            for err in validation_errors
        ]
        logger.info(f"Job {job_id}: {len(successfully_uploaded)} files uploaded successfully, "
                   f"{len(validation_errors)} files failed validation")
    
    return UploadResponse(
        status="success",
        job_id=job_id,
        files=successfully_uploaded,
        warnings=warnings
    )

