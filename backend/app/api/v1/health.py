"""Health check endpoint for API v1."""

from datetime import datetime, timezone

from fastapi import APIRouter

from backend.app.core import settings
from backend.app.models import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Check if the API service is healthy and running.
    
    Returns:
        HealthResponse: Service health status with timestamp and version
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        version=settings.app_version,
        message="Service is healthy"
    )

