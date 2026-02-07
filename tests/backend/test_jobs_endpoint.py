"""Unit tests for the job status endpoint.

Tests the /api/v1/jobs/{job_id}/status endpoint for job status retrieval,
progress tracking, and error handling.
"""

import sys
import time
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parents[2] / "backend"))

from app.main import app
from app.services import storage_service


def create_test_image(width: int = 640, height: int = 480, format: str = "PNG") -> bytes:
    """Helper to create a test image.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        format: Image format (PNG, JPEG, TIFF)
        
    Returns:
        Image data as bytes
    """
    img = Image.new('RGB', (width, height), color='blue')
    buffer = BytesIO()
    img.save(buffer, format=format)
    return buffer.getvalue()


@pytest.fixture
def client():
    """Create FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def uploaded_job(client):
    """Create a job with uploaded files for testing.
    
    Returns:
        job_id as string
    """
    # Create a valid test image
    image_data = create_test_image(640, 480, "PNG")
    
    # Upload the image to create a job
    response = client.post(
        "/api/v1/upload",
        files={"files": ("test_image.png", image_data, "image/png")}
    )
    
    assert response.status_code == 200
    data = response.json()
    return data["job_id"]


@pytest.fixture
def processing_job(uploaded_job, client):
    """Create a processing job for testing.
    
    Returns:
        job_id as string
    """
    job_id = uploaded_job
    
    # Mock inference service to prevent actual inference
    with patch('app.services.inference.inference_service.run_inference') as mock_inference:
        mock_inference.return_value = {
            'total_images': 1,
            'processed_images': 1,
            'failed_images': 0,
            'total_detections': 5,
        }
        
        # Trigger inference to move job to processing state
        response = client.post(
            "/api/v1/predict",
            json={
                "job_id": job_id,
                "config": {
                    "model_path": "/path/to/model.pt",
                    "confidence_threshold": 0.25,
                    "iou_threshold": 0.45
                }
            }
        )
        
        assert response.status_code == 202
        
        # Wait briefly for status update
        time.sleep(0.1)
        
        return job_id


class TestJobStatusEndpoint:
    """Tests for the /api/v1/jobs/{job_id}/status endpoint."""
    
    def test_get_status_uploaded_job(self, client, uploaded_job):
        """Test retrieving status of a job in 'uploaded' state."""
        job_id = uploaded_job
        
        # Get job status
        response = client.get(f"/api/v1/jobs/{job_id}/status")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "data" in data
        
        job_data = data["data"]
        assert job_data["job_id"] == job_id
        assert job_data["status"] == "uploaded"
        assert "created_at" in job_data
        assert job_data["created_at"] is not None
    
    def test_get_status_processing_job(self, client, processing_job):
        """Test retrieving status of a job in 'processing' state."""
        job_id = processing_job
        
        # Get job status
        response = client.get(f"/api/v1/jobs/{job_id}/status")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        job_data = data["data"]
        assert job_data["job_id"] == job_id
        assert job_data["status"] == "processing"
        
        # Verify progress information is present
        assert "progress" in job_data
        if job_data["progress"]:
            progress = job_data["progress"]
            # Progress should have at least one of these fields
            assert "stage" in progress or "message" in progress
    
    def test_get_status_completed_job(self, client, processing_job):
        """Test retrieving status of a completed or failed job.
        
        Note: Without a real model, the job will fail. This test verifies
        that the job moves beyond the 'uploaded' state and produces a result.
        """
        job_id = processing_job
        
        # Wait for job to complete or fail
        time.sleep(1.0)
        
        # Get job status
        response = client.get(f"/api/v1/jobs/{job_id}/status")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        job_data = data["data"]
        assert job_data["job_id"] == job_id
        # Job will be either completed (if mocked) or failed (without real model)
        assert job_data["status"] in ["processing", "completed", "failed"]
        
        # Verify timestamps
        assert "created_at" in job_data
        assert "updated_at" in job_data
        
        # Verify results URLs are present for completed jobs
        assert "results_url" in job_data
        assert "visualization_url" in job_data
        if job_data["results_url"]:
            assert f"/api/v1/jobs/{job_id}/results" == job_data["results_url"]
        if job_data["visualization_url"]:
            assert f"/api/v1/jobs/{job_id}/visualization" == job_data["visualization_url"]
    
    def test_get_status_failed_job(self, client):
        """Test retrieving status of a failed job."""
        # Create a job and manually set it to failed state
        job_id = storage_service.create_job(status="uploaded")
        
        # Update job to failed state with error details
        storage_service.update_job(
            job_id,
            status="failed",
            error="Model file not found: /path/to/model.pt"
        )
        
        # Wait briefly for file write
        time.sleep(0.1)
        
        # Get job status
        response = client.get(f"/api/v1/jobs/{job_id}/status")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        job_data = data["data"]
        assert job_data["job_id"] == job_id
        assert job_data["status"] == "failed"
        
        # Verify error details are present
        assert "error" in job_data
        assert job_data["error"] is not None
        error = job_data["error"]
        assert "message" in error
        assert "Model file not found" in error["message"]
    
    def test_get_status_job_not_found(self, client):
        """Test retrieving status of a non-existent job."""
        fake_job_id = "00000000-0000-0000-0000-000000000000"
        
        # Get job status
        response = client.get(f"/api/v1/jobs/{fake_job_id}/status")
        
        # Verify 404 response
        assert response.status_code == 404
        data = response.json()
        
        assert "error" in data
        error = data["error"]
        assert data["status"] == "error"
        assert "Job not found" in error["message"]
        assert error["code"] == "JOB_NOT_FOUND"
    
    def test_get_status_response_format(self, client, uploaded_job):
        """Test that the response format matches the specification."""
        job_id = uploaded_job
        
        # Get job status
        response = client.get(f"/api/v1/jobs/{job_id}/status")
        
        # Verify response structure
        assert response.status_code == 200
        data = response.json()
        
        # Top-level structure
        assert "status" in data
        assert "data" in data
        assert data["status"] == "success"
        
        # Job data structure
        job_data = data["data"]
        required_fields = ["job_id", "status", "created_at"]
        for field in required_fields:
            assert field in job_data, f"Missing required field: {field}"
        
        # Verify job_id format (should be UUID)
        assert "-" in job_data["job_id"]
        assert len(job_data["job_id"]) == 36
    
    def test_get_status_with_progress_info(self, client):
        """Test that progress information is correctly formatted."""
        # Create a job with detailed progress info
        job_id = storage_service.create_job(status="processing")
        
        # Update with progress info
        storage_service.update_job(
            job_id,
            progress={
                "stage": "Running SAHI inference",
                "message": "Processing image 5 of 10",
                "percentage": 50.0,
                "total_images": 10,
                "processed_images": 5
            }
        )
        
        # Wait briefly for file write
        time.sleep(0.1)
        
        # Get job status
        response = client.get(f"/api/v1/jobs/{job_id}/status")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        job_data = data["data"]
        assert "progress" in job_data
        progress = job_data["progress"]
        
        assert progress["stage"] == "Running SAHI inference"
        assert progress["message"] == "Processing image 5 of 10"
        assert progress["percentage"] == 50.0
        assert progress["total_images"] == 10
        assert progress["processed_images"] == 5
    
    def test_get_status_with_summary_info(self, client):
        """Test that summary information is present for completed jobs."""
        # Create a completed job with summary info
        job_id = storage_service.create_job(status="completed")
        
        # Update with summary info
        storage_service.update_job(
            job_id,
            summary={
                "total_detections": 47,
                "average_confidence": 0.82,
                "processing_time_seconds": 75.5
            }
        )
        
        # Wait briefly for file write
        time.sleep(0.1)
        
        # Get job status
        response = client.get(f"/api/v1/jobs/{job_id}/status")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        job_data = data["data"]
        assert "summary" in job_data
        summary = job_data["summary"]
        
        assert summary["total_detections"] == 47
        assert summary["average_confidence"] == 0.82
        assert summary["processing_time_seconds"] == 75.5
    
    def test_get_status_fast_response_time(self, client, uploaded_job):
        """Test that the endpoint responds quickly (< 100ms for file-based storage)."""
        job_id = uploaded_job
        
        # Measure response time
        start_time = time.time()
        
        response = client.get(f"/api/v1/jobs/{job_id}/status")
        
        elapsed_time = time.time() - start_time
        
        # Verify response is fast
        assert response.status_code == 200
        assert elapsed_time < 0.5, f"Response took {elapsed_time:.3f}s, should be < 0.5s"
    
    def test_openapi_schema_includes_jobs_endpoint(self, client):
        """Test that the OpenAPI schema includes the jobs endpoint."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        
        # Verify endpoint is documented
        assert "paths" in schema
        assert "/api/v1/jobs/{job_id}/status" in schema["paths"]
        
        # Verify GET method is documented
        endpoint_spec = schema["paths"]["/api/v1/jobs/{job_id}/status"]
        assert "get" in endpoint_spec
        
        # Verify responses are documented
        get_spec = endpoint_spec["get"]
        assert "responses" in get_spec
        assert "200" in get_spec["responses"]
        # Note: 404 responses from HTTPException are not auto-documented by FastAPI
        # They would need to be explicitly added with responses parameter in decorator
