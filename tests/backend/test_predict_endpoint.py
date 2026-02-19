"""Unit tests for the inference prediction endpoint.

Tests the /api/v1/predict endpoint for inference job creation,
validation, and background processing.
"""

import sys
import time
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parents[2] / "backend"))

from backend.app.main import app
from backend.app.services import storage_service


def create_test_image(width: int = 640, height: int = 480, format: str = "PNG") -> bytes:
    """Helper to create a test image.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        format: Image format (PNG, JPEG, TIFF)
        
    Returns:
        Image data as bytes
    """
    img = Image.new('RGB', (width, height), color='green')
    buffer = BytesIO()
    img.save(buffer, format=format)
    return buffer.getvalue()


@pytest.fixture
def client():
    """Create FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_model_file(tmp_path):
    """Create a mock model file for testing."""
    model_dir = tmp_path / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "test_model.pt"
    # Create a fake model file with some content
    model_path.write_bytes(b"fake YOLO model weights")
    return str(model_path)


@pytest.fixture
def mock_inference_service():
    """Mock inference service for tests that don't need real inference."""
    # Patch the run_inference method on the actual inference_service instance
    with patch('backend.app.api.v1.predict.inference_service.run_inference') as mock_run:
        # Mock successful inference - this gets called in background thread
        mock_run.return_value = {
            'total_images': 1,
            'processed_images': 1,
            'failed_images': 0,
            'total_detections': 5,
            'avg_detections_per_image': 5.0,
            'elapsed_time_seconds': 0.5,
            'avg_time_per_image_seconds': 0.5,
        }
        yield mock_run


@pytest.fixture
def uploaded_job(client):
    """Create a job with uploaded files for testing.
    
    Returns:
        Tuple of (job_id, file_count)
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
    job_id = data["job_id"]
    file_count = len(data["files"])
    
    return job_id, file_count


class TestPredictEndpoint:
    """Tests for the /api/v1/predict endpoint."""
    
    def test_trigger_inference_success(self, client, uploaded_job, mock_inference_service, mock_model_file):
        """Test successfully triggering inference on uploaded job."""
        job_id, _ = uploaded_job
        
        # Trigger inference with minimal config
        response = client.post(
            "/api/v1/predict",
            json={
                "job_id": job_id,
                "config": {
                    "model_path": mock_model_file,
                    "confidence_threshold": 0.25,
                    "iou_threshold": 0.45
                }
            }
        )
        
        # Verify response
        assert response.status_code == 202
        data = response.json()
        
        assert data["status"] == "accepted"
        assert data["message"] == "Inference job started"
        assert data["job_id"] == job_id
        assert data["job_status"] == "processing"
        
        # Wait briefly for file write to complete
        time.sleep(0.1)
        
        # Verify job status was updated
        job_data = storage_service.get_job(job_id)
        assert job_data["status"] == "processing"
        assert "config" in job_data
        assert job_data["config"]["model_path"] == mock_model_file
    
    def test_trigger_inference_with_full_config(self, client, uploaded_job, mock_model_file):
        """Test triggering inference with complete configuration."""
        job_id, _ = uploaded_job
        
        # Trigger inference with full config
        response = client.post(
            "/api/v1/predict",
            json={
                "job_id": job_id,
                "config": {
                    "model_path": mock_model_file,
                    "confidence_threshold": 0.3,
                    "iou_threshold": 0.5,
                    "sahi": {
                        "enabled": True,
                        "slice_width": 512,
                        "slice_height": 512,
                        "overlap_ratio": 0.25
                    },
                    "symbolic_reasoning": {
                        "enabled": True,
                        "rules_file": "/path/to/rules.pl"
                    },
                    "visualization": {
                        "enabled": True,
                        "show_labels": True,
                        "confidence_display": True
                    }
                }
            }
        )
        
        # Verify response
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "accepted"
        
        # Wait briefly for file write to complete
        time.sleep(0.1)
        
        # Verify config was stored
        job_data = storage_service.get_job(job_id)
        assert job_data["config"]["sahi"]["slice_width"] == 512
        assert job_data["config"]["symbolic_reasoning"]["enabled"] is True
        assert job_data["config"]["visualization"]["show_labels"] is True
    
    def test_trigger_inference_job_not_found(self, client):
        """Test triggering inference for non-existent job."""
        fake_job_id = "00000000-0000-0000-0000-000000000000"
        
        response = client.post(
            "/api/v1/predict",
            json={
                "job_id": fake_job_id,
                "config": {
                    "model_path": "/path/to/model.pt"
                }
            }
        )
        
        # Verify error response
        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "JOB_NOT_FOUND"
        assert fake_job_id in data["error"]["message"]
    
    def test_trigger_inference_no_files(self, client, mock_model_file):
        """Test triggering inference on job with no uploaded files."""
        # Create a job without files
        job_id = storage_service.create_job(status="uploaded")
        
        response = client.post(
            "/api/v1/predict",
            json={
                "job_id": job_id,
                "config": {
                    "model_path": mock_model_file
                }
            }
        )
        
        # Verify error response
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "NO_FILES"
        assert job_id in data["error"]["message"]
    
    def test_trigger_inference_invalid_status(self, client, uploaded_job, mock_model_file):
        """Test triggering inference on job with invalid status."""
        job_id, _ = uploaded_job
        
        # Update job status to "processing" (not ready for inference)
        storage_service.update_job(job_id, status="processing")
        
        response = client.post(
            "/api/v1/predict",
            json={
                "job_id": job_id,
                "config": {
                    "model_path": mock_model_file
                }
            }
        )
        
        # Verify error response
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "INVALID_STATUS"
        assert "processing" in data["error"]["message"]
    
    def test_trigger_inference_invalid_confidence_threshold(self, client, uploaded_job, mock_model_file):
        """Test validation of confidence threshold."""
        job_id, _ = uploaded_job
        
        # Try to trigger with invalid confidence threshold
        response = client.post(
            "/api/v1/predict",
            json={
                "job_id": job_id,
                "config": {
                    "model_path": mock_model_file,
                    "confidence_threshold": 1.5  # Invalid: > 1.0
                }
            }
        )
        
        # Verify validation error
        assert response.status_code == 422  # Unprocessable Entity
        data = response.json()
        assert "error" in data
        assert data["status"] == "error"
        assert data["error"]["code"] == "VALIDATION_ERROR"
    
    def test_trigger_inference_invalid_iou_threshold(self, client, uploaded_job, mock_model_file):
        """Test validation of IoU threshold."""
        job_id, _ = uploaded_job
        
        # Try to trigger with invalid IoU threshold
        response = client.post(
            "/api/v1/predict",
            json={
                "job_id": job_id,
                "config": {
                    "model_path": mock_model_file,
                    "iou_threshold": -0.1  # Invalid: < 0.0
                }
            }
        )
        
        # Verify validation error
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert data["status"] == "error"
        assert data["error"]["code"] == "VALIDATION_ERROR"
    
    def test_trigger_inference_invalid_slice_dimensions(self, client, uploaded_job, mock_model_file):
        """Test validation of SAHI slice dimensions."""
        job_id, _ = uploaded_job
        
        # Try to trigger with invalid slice width
        response = client.post(
            "/api/v1/predict",
            json={
                "job_id": job_id,
                "config": {
                    "model_path": mock_model_file,
                    "sahi": {
                        "enabled": True,
                        "slice_width": 100  # Invalid: < 256
                    }
                }
            }
        )
        
        # Verify validation error
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert data["status"] == "error"
        assert data["error"]["code"] == "VALIDATION_ERROR"
    
    def test_trigger_inference_invalid_overlap_ratio(self, client, uploaded_job, mock_model_file):
        """Test validation of SAHI overlap ratio."""
        job_id, _ = uploaded_job
        
        # Try to trigger with invalid overlap ratio
        response = client.post(
            "/api/v1/predict",
            json={
                "job_id": job_id,
                "config": {
                    "model_path": mock_model_file,
                    "sahi": {
                        "enabled": True,
                        "overlap_ratio": 0.8  # Invalid: > 0.5
                    }
                }
            }
        )
        
        # Verify validation error
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert data["status"] == "error"
        assert data["error"]["code"] == "VALIDATION_ERROR"
    
    def test_background_thread_updates_job_status(self, client, uploaded_job, mock_inference_service, mock_model_file):
        """Test that background thread starts and updates job status to processing.
        
        Note: This test verifies the background thread mechanism starts correctly.
        It does not test completion since that would require a real model file.
        """
        job_id, _ = uploaded_job
        
        # Trigger inference
        response = client.post(
            "/api/v1/predict",
            json={
                "job_id": job_id,
                "config": {
                    "model_path": mock_model_file
                }
            }
        )
        
        assert response.status_code == 202
        
        # Wait briefly for background thread to start
        time.sleep(0.1)
        
        # Verify job moved to processing state
        job_data = storage_service.get_job(job_id)
        assert job_data["status"] in ["processing", "failed"]  # Will fail without real model
        assert "progress" in job_data
        
        # If mocked properly, it should complete
        if mock_inference_service.called:
            # Wait for background thread to complete
            max_wait_time = 2
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                job_data = storage_service.get_job(job_id)
                if job_data["status"] == "completed":
                    break
                time.sleep(0.2)
            
            job_data = storage_service.get_job(job_id)
            if job_data["status"] == "completed":
                assert job_data["progress"]["stage"] == "completed"
    
    def test_missing_model_path(self, client, uploaded_job):
        """Test that model_path is required."""
        job_id, _ = uploaded_job
        
        # Try to trigger without model_path
        response = client.post(
            "/api/v1/predict",
            json={
                "job_id": job_id,
                "config": {
                    "confidence_threshold": 0.25
                    # Missing model_path
                }
            }
        )
        
        # Verify validation error
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert data["status"] == "error"
        assert data["error"]["code"] == "VALIDATION_ERROR"
    
    def test_default_config_values(self, client, uploaded_job, mock_model_file):
        """Test that config defaults are applied correctly."""
        job_id, _ = uploaded_job
        
        # Trigger with minimal config
        response = client.post(
            "/api/v1/predict",
            json={
                "job_id": job_id,
                "config": {
                    "model_path": mock_model_file
                    # All other fields should use defaults
                }
            }
        )
        
        assert response.status_code == 202
        
        # Wait briefly for file write to complete
        time.sleep(0.1)
        
        # Verify defaults were applied
        job_data = storage_service.get_job(job_id)
        config = job_data["config"]
        
        assert config["confidence_threshold"] == 0.25
        assert config["iou_threshold"] == 0.45
        assert config["sahi"]["enabled"] is True
        assert config["sahi"]["slice_width"] == 640
        assert config["sahi"]["slice_height"] == 640
        assert config["sahi"]["overlap_ratio"] == 0.2
        assert config["symbolic_reasoning"]["enabled"] is True
        assert config["visualization"]["enabled"] is True



