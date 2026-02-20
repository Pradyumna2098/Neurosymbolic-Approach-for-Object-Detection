"""FastAPI application initialization and configuration.

This is the main entry point for the neurosymbolic object detection API.
This prototype uses local filesystem storage instead of PostgreSQL/Redis.
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Add repo root to sys.path so 'pipeline' module can be imported
repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.api.v1 import api_router
from app.core import settings
from app.core.exception_handlers import (
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)


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

# Configure CORS middleware for Electron app and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers for standardized error responses
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

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

