"""FastAPI application initialization and configuration.

This is the main entry point for the neurosymbolic object detection API.
This prototype uses local filesystem storage instead of PostgreSQL/Redis.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.
    
    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup: Ensure all required directories exist
    settings.ensure_directories()
    print(f"✓ Data directories initialized at {settings.data_root}")
    print(f"✓ API server starting on {settings.host}:{settings.port}")
    
    yield
    
    # Shutdown
    print("✓ API server shutting down")


# Initialize FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="REST API for neurosymbolic object detection inference and automation",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS middleware for Electron app
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 routes with versioning prefix
app.include_router(api_router, prefix=settings.api_v1_prefix)


# Root endpoint for API discovery
@app.get("/", tags=["Root"])
async def root():
    """API root endpoint.
    
    Returns basic information about the API and available endpoints.
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "health": f"{settings.api_v1_prefix}/health",
    }
