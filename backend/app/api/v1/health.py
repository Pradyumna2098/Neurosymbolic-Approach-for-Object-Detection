"""Health check endpoint for API v1."""

from datetime import datetime

from fastapi import APIRouter

from app.core import settings
from app.models import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Check if the API service is healthy and running.
    
    Returns:
        HealthResponse: Service health status with timestamp and version
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.app_version,
        message="Service is healthy"
    )
