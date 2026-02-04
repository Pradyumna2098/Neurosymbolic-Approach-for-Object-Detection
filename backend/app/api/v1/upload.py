"""Image upload endpoint for neurosymbolic object detection API.

This endpoint handles multipart/form-data image uploads, validates files,
saves them to the local filesystem organized by job_id, and creates job
metadata for tracking.
"""

from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core import settings
from app.models import ErrorResponse, UploadedFileInfo, UploadResponse
from app.services import storage_service

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
    if len(files) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": f"Too many files. Maximum 100 files per upload, got {len(files)}",
                "code": "TOO_MANY_FILES"
            }
        )
    
    # Create a new job for this upload
    job_id = storage_service.create_job({
        "file_count": len(files),
    })
    
    # Update job status to "uploaded" after creation
    storage_service.update_job(job_id, status="uploaded")
    
    uploaded_files = []
    validation_errors = []
    
    # Process each uploaded file
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
            
            # Save the file using storage service (includes validation)
            # Returns tuple: (file_id, file_path, metadata)
            file_id, file_path, metadata = storage_service.save_upload(
                job_id=job_id,
                filename=upload_file.filename,
                content=content
            )
            
            # Build response with file metadata
            uploaded_files.append(UploadedFileInfo(
                filename=upload_file.filename,
                size=len(content),
                file_id=file_id,
                format=metadata.get('format') if metadata else None,
                width=metadata.get('width') if metadata else None,
                height=metadata.get('height') if metadata else None
            ))
            
        except Exception as e:
            # Collect validation errors instead of failing immediately
            validation_errors.append({
                "filename": upload_file.filename,
                "error": str(e)
            })
    
    # If all files failed validation, return error
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
    
    # If some files failed but others succeeded, include partial success info
    # in a warning header (not blocking the successful upload)
    if validation_errors:
        # Note: In a production system, you might want to include partial errors
        # in the response. For simplicity, we log and continue.
        pass
    
    return UploadResponse(
        status="success",
        job_id=job_id,
        files=uploaded_files
    )
