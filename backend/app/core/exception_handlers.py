"""Exception handler middleware for FastAPI.

This module provides centralized exception handling for the API,
converting exceptions to standardized ErrorResponse format.
"""

import logging
from datetime import datetime, timezone
from typing import Union

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.errors import ErrorCode, get_error_message
from app.models.responses import ErrorDetail, ErrorResponse

# Set up logger
logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPException and convert to standardized ErrorResponse.
    
    Args:
        request: The FastAPI request
        exc: The HTTPException that was raised
        
    Returns:
        JSONResponse with ErrorResponse format
    """
    # Try to extract error code from exception detail
    error_code = ErrorCode.INTERNAL_ERROR
    error_message = str(exc.detail)
    error_details = None
    
    # Check if detail is a dict with error info
    if isinstance(exc.detail, dict):
        # Support both "code" and legacy "error_code" keys and handle unknown values safely
        raw_code = exc.detail.get("code")
        if raw_code is None:
            raw_code = exc.detail.get("error_code")
        
        if isinstance(raw_code, ErrorCode):
            error_code = raw_code
        elif raw_code is not None:
            try:
                error_code = ErrorCode(raw_code)
            except (ValueError, TypeError):
                error_code = ErrorCode.INTERNAL_ERROR
        
        # Prefer explicit message, otherwise fall back to default for the resolved error_code
        error_message = exc.detail.get("message") or get_error_message(error_code)
        error_details = exc.detail.get("details")
    elif isinstance(exc.detail, str):
        # Try to map common HTTP status codes to error codes
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            if "job" in error_message.lower():
                error_code = ErrorCode.JOB_NOT_FOUND
            elif "file" in error_message.lower():
                error_code = ErrorCode.FILE_NOT_FOUND
            elif "result" in error_message.lower():
                error_code = ErrorCode.RESULTS_NOT_FOUND
        elif exc.status_code == status.HTTP_400_BAD_REQUEST:
            error_code = ErrorCode.INVALID_REQUEST
        elif exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            error_code = ErrorCode.RATE_LIMIT_EXCEEDED
        elif exc.status_code >= 500:
            error_code = ErrorCode.INTERNAL_ERROR
    
    error_response = ErrorResponse(
        status="error",
        error=ErrorDetail(
            code=error_code,
            message=error_message,
            details=error_details,
            timestamp=datetime.now(timezone.utc)
        )
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(mode="json")
    )


async def validation_exception_handler(
    request: Request, 
    exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    """Handle validation errors and convert to standardized ErrorResponse.
    
    Args:
        request: The FastAPI request
        exc: The validation error that was raised
        
    Returns:
        JSONResponse with ErrorResponse format and field-level errors
    """
    # Extract validation errors
    errors = []
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field_path,
            "message": error["msg"],
            "type": error["type"]
        })
    
    # Create detailed error message
    error_details = f"Validation failed for {len(errors)} field(s): " + ", ".join(
        f"{err['field']} ({err['message']})" for err in errors[:3]
    )
    
    if len(errors) > 3:
        error_details += f" and {len(errors) - 3} more"
    
    error_response = ErrorResponse(
        status="error",
        error=ErrorDetail(
            code=ErrorCode.VALIDATION_ERROR,
            message=get_error_message(ErrorCode.VALIDATION_ERROR),
            details=error_details,
            field=None,  # Multiple fields
            timestamp=datetime.now(timezone.utc)
        )
    )
    
    # Add field errors to response
    response_data = error_response.model_dump(mode="json")
    response_data["field_errors"] = errors
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_data
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle any uncaught exceptions.
    
    Args:
        request: The FastAPI request
        exc: The exception that was raised
        
    Returns:
        JSONResponse with ErrorResponse format
    """
    # Log the exception for debugging
    logger.exception("Uncaught exception in request handler")
    
    error_response = ErrorResponse(
        status="error",
        error=ErrorDetail(
            code=ErrorCode.INTERNAL_ERROR,
            message=get_error_message(ErrorCode.INTERNAL_ERROR),
            details=f"Exception type: {type(exc).__name__}",
            timestamp=datetime.now(timezone.utc)
        )
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(mode="json")
    )


def create_http_exception(
    status_code: int,
    error_code: ErrorCode,
    custom_message: str = None,
    details: str = None
) -> HTTPException:
    """Create an HTTPException with standardized error format.
    
    Args:
        status_code: HTTP status code
        error_code: Application error code
        custom_message: Optional custom message to append
        details: Optional additional details
        
    Returns:
        HTTPException with structured detail
    """
    return HTTPException(
        status_code=status_code,
        detail={
            "code": error_code.value,
            "message": get_error_message(error_code, custom_message),
            "details": details
        }
    )
