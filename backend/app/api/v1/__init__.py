"""API v1 router aggregation."""

from fastapi import APIRouter

from .health import router as health_router
from .upload import router as upload_router
from .predict import router as predict_router
from .jobs import router as jobs_router
from .files import router as files_router

# Create the main v1 API router
api_router = APIRouter()

# Include all v1 endpoint routers
api_router.include_router(health_router, prefix="", tags=["health"])
api_router.include_router(upload_router, prefix="", tags=["upload"])
api_router.include_router(predict_router, prefix="", tags=["inference"])
api_router.include_router(jobs_router, prefix="", tags=["jobs"])
api_router.include_router(files_router, prefix="", tags=["files"])
