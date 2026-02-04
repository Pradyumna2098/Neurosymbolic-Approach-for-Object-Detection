"""Unit tests for FastAPI backend application.

Tests the core FastAPI application, health check endpoint, and basic functionality.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parents[2] / "backend"))

from app.main import app


@pytest.fixture
def client():
    """Create FastAPI test client."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint returns API information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "running"
    assert "docs" in data
    assert "health" in data


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data
    assert "message" in data


def test_swagger_ui_accessible(client):
    """Test that Swagger UI documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_openapi_schema_accessible(client):
    """Test that OpenAPI schema is accessible."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data
    # Verify health endpoint is documented
    assert "/api/v1/health" in data["paths"]


def test_cors_headers_present(client):
    """Test that CORS middleware is configured."""
    # Make a GET request with Origin header
    response = client.get(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
        }
    )
    assert response.status_code == 200
    # TestClient has limited CORS simulation, but we can verify credentials header
    assert "access-control-allow-credentials" in response.headers
    # Note: Full CORS testing requires integration tests with a real server
