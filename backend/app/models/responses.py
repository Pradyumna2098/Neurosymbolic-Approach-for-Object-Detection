"""Pydantic models for API request/response schemas."""

from datetime import datetime
from typing import Any, Dict, Optional

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
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class ErrorResponse(BaseModel):
    """Standard error response format."""
    
    status: str = Field(default="error", description="Response status")
    error: ErrorDetail = Field(..., description="Error details")


class SuccessResponse(BaseModel):
    """Generic success response."""
    
    status: str = Field(default="success", description="Response status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Optional response data")
