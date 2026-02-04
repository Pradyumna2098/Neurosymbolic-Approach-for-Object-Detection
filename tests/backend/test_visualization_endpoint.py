"""Unit tests for the job visualization endpoint.

Tests the /api/v1/jobs/{job_id}/visualization endpoint for retrieving
annotated images with bounding boxes.
"""

import base64
import sys
from io import BytesIO
from pathlib import Path

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
def completed_job_with_visualizations():
    """Create a completed job with mock visualization files.
    
    Returns:
        job_id as string
    """
    # Create job
    job_id = storage_service.create_job(status="completed")
    
    # Add mock files to job
    file_id_1 = "viz-file-001"
    file_id_2 = "viz-file-002"
    
    storage_service.update_job(
        job_id,
        files=[
            {
                "file_id": file_id_1,
                "filename": "test_image1.png",
                "stored_filename": f"{file_id_1}.png",
                "size_bytes": 1024,
                "uploaded_at": "2026-02-04T00:00:00Z"
            },
            {
                "file_id": file_id_2,
                "filename": "test_image2.jpg",
                "stored_filename": f"{file_id_2}.jpg",
                "size_bytes": 2048,
                "uploaded_at": "2026-02-04T00:00:00Z"
            }
        ]
    )
    
    # Create mock prediction files in refined results directory
    results_dir = storage_service._get_job_results_dir(job_id, stage="refined")
    
    # File 1: 3 detections
    pred_file_1 = results_dir / f"{file_id_1}.txt"
    predictions_1 = [
        "0 0.5 0.5 0.2 0.3 0.95",
        "1 0.3 0.7 0.15 0.25 0.87",
        "0 0.8 0.2 0.1 0.1 0.76"
    ]
    with open(pred_file_1, "w") as f:
        f.write("\n".join(predictions_1) + "\n")
    
    # File 2: 2 detections
    pred_file_2 = results_dir / f"{file_id_2}.txt"
    predictions_2 = [
        "1 0.4 0.4 0.3 0.3 0.92",
        "2 0.6 0.6 0.2 0.2 0.88"
    ]
    with open(pred_file_2, "w") as f:
        f.write("\n".join(predictions_2) + "\n")
    
    # Create mock visualization files (annotated images)
    viz_dir = storage_service._get_job_visualization_dir(job_id)
    
    # Create test images for visualizations
    viz_image_1 = create_test_image(640, 480, "PNG")
    viz_file_1 = viz_dir / f"{file_id_1}.png"
    with open(viz_file_1, "wb") as f:
        f.write(viz_image_1)
    
    viz_image_2 = create_test_image(800, 600, "JPEG")
    viz_file_2 = viz_dir / f"{file_id_2}.jpg"
    with open(viz_file_2, "wb") as f:
        f.write(viz_image_2)
    
    # Create mock original uploaded images
    upload_dir = storage_service._get_job_upload_dir(job_id)
    
    orig_image_1 = create_test_image(640, 480, "PNG")
    orig_file_1 = upload_dir / f"{file_id_1}.png"
    with open(orig_file_1, "wb") as f:
        f.write(orig_image_1)
    
    orig_image_2 = create_test_image(800, 600, "JPEG")
    orig_file_2 = upload_dir / f"{file_id_2}.jpg"
    with open(orig_file_2, "wb") as f:
        f.write(orig_image_2)
    
    return job_id


@pytest.fixture
def completed_job_no_visualizations():
    """Create a completed job without visualization files.
    
    Returns:
        job_id as string
    """
    job_id = storage_service.create_job(status="completed")
    # Visualization directory exists but is empty
    storage_service._get_job_visualization_dir(job_id)
    return job_id


@pytest.fixture
def processing_job():
    """Create a processing job.
    
    Returns:
        job_id as string
    """
    job_id = storage_service.create_job(status="processing")
    return job_id


class TestVisualizationEndpoint:
    """Tests for the /api/v1/jobs/{job_id}/visualization endpoint."""
    
    def test_get_visualizations_url_format(self, client, completed_job_with_visualizations):
        """Test retrieving visualizations in URL format (default)."""
        job_id = completed_job_with_visualizations
        
        # Get visualizations
        response = client.get(f"/api/v1/jobs/{job_id}/visualization")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Check top-level structure
        assert data["status"] == "success"
        assert "data" in data
        
        viz_data = data["data"]
        assert viz_data["job_id"] == job_id
        assert "visualizations" in viz_data
        
        # Check visualizations array
        visualizations = viz_data["visualizations"]
        assert len(visualizations) == 2
        
        # Check first visualization
        viz_1 = visualizations[0]
        assert "file_id" in viz_1
        assert viz_1["filename"] in ["test_image1.png", "test_image2.jpg"]
        assert viz_1["original_url"].startswith("/api/v1/files/")
        assert viz_1["annotated_url"].startswith("/api/v1/files/")
        assert "annotated" in viz_1["annotated_url"]
        assert "original" in viz_1["original_url"]
        assert viz_1["detection_count"] > 0
    
    def test_get_visualizations_filter_by_file_id(self, client, completed_job_with_visualizations):
        """Test filtering visualizations by file_id."""
        job_id = completed_job_with_visualizations
        
        # Get job data to find a file_id
        job_data = storage_service.get_job(job_id)
        file_id = job_data["files"][0]["file_id"]
        
        # Get visualizations for specific file
        response = client.get(f"/api/v1/jobs/{job_id}/visualization?file_id={file_id}")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        visualizations = data["data"]["visualizations"]
        assert len(visualizations) == 1
        assert visualizations[0]["file_id"] == file_id
    
    def test_get_visualization_base64_format(self, client, completed_job_with_visualizations):
        """Test retrieving single visualization in base64 format."""
        job_id = completed_job_with_visualizations
        
        # Get job data to find a file_id
        job_data = storage_service.get_job(job_id)
        file_id = job_data["files"][0]["file_id"]
        
        # Get visualization in base64 format
        response = client.get(
            f"/api/v1/jobs/{job_id}/visualization?file_id={file_id}&format=base64"
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert data["status"] == "success"
        assert "data" in data
        
        viz_data = data["data"]
        assert viz_data["file_id"] == file_id
        assert viz_data["format"] == "base64"
        assert viz_data["filename"] in ["test_image1.png", "test_image2.jpg"]
        
        # Check base64 encoded images
        assert "original_image" in viz_data
        assert "annotated_image" in viz_data
        assert viz_data["original_image"].startswith("data:image/")
        assert viz_data["annotated_image"].startswith("data:image/")
        assert ";base64," in viz_data["original_image"]
        assert ";base64," in viz_data["annotated_image"]
        
        # Verify detection count
        assert viz_data["detection_count"] > 0
        
        # Verify base64 data can be decoded
        original_b64 = viz_data["original_image"].split(",", 1)[1]
        annotated_b64 = viz_data["annotated_image"].split(",", 1)[1]
        
        # Should not raise exception
        base64.b64decode(original_b64)
        base64.b64decode(annotated_b64)
    
    def test_get_visualizations_job_not_found(self, client):
        """Test 404 response for non-existent job."""
        fake_job_id = "00000000-0000-0000-0000-000000000000"
        
        # Get visualizations
        response = client.get(f"/api/v1/jobs/{fake_job_id}/visualization")
        
        # Verify 404 response
        assert response.status_code == 404
        data = response.json()
        
        assert "detail" in data
        detail = data["detail"]
        assert detail["status"] == "error"
        assert "Job not found" in detail["message"]
        assert detail["error_code"] == "JOB_NOT_FOUND"
    
    def test_get_visualizations_job_not_completed(self, client, processing_job):
        """Test 404 response for incomplete job."""
        job_id = processing_job
        
        # Get visualizations
        response = client.get(f"/api/v1/jobs/{job_id}/visualization")
        
        # Verify 404 response
        assert response.status_code == 404
        data = response.json()
        
        assert "detail" in data
        detail = data["detail"]
        assert detail["status"] == "error"
        assert "Visualizations not available" in detail["message"]
        assert detail["error_code"] == "VISUALIZATIONS_NOT_READY"
        assert "processing" in detail["details"]
    
    def test_get_visualizations_no_files(self, client, completed_job_no_visualizations):
        """Test 404 response when no visualization files exist."""
        job_id = completed_job_no_visualizations
        
        # Get visualizations
        response = client.get(f"/api/v1/jobs/{job_id}/visualization")
        
        # Verify 404 response
        assert response.status_code == 404
        data = response.json()
        
        assert "detail" in data
        detail = data["detail"]
        assert detail["status"] == "error"
        assert "Visualizations not available" in detail["message"]
        assert detail["error_code"] == "VISUALIZATIONS_NOT_FOUND"
    
    def test_get_visualizations_invalid_format(self, client, completed_job_with_visualizations):
        """Test 400 response for invalid format parameter."""
        job_id = completed_job_with_visualizations
        
        # Get visualizations with invalid format
        response = client.get(f"/api/v1/jobs/{job_id}/visualization?format=invalid")
        
        # Verify 400 response
        assert response.status_code == 400
        data = response.json()
        
        assert "detail" in data
        detail = data["detail"]
        assert detail["status"] == "error"
        assert "Invalid format parameter" in detail["message"]
        assert detail["error_code"] == "INVALID_FORMAT"
    
    def test_get_visualizations_invalid_file_id(self, client, completed_job_with_visualizations):
        """Test 404 response for non-existent file_id."""
        job_id = completed_job_with_visualizations
        fake_file_id = "nonexistent-file-id"
        
        # Get visualizations
        response = client.get(
            f"/api/v1/jobs/{job_id}/visualization?file_id={fake_file_id}"
        )
        
        # Verify 404 response
        assert response.status_code == 404
        data = response.json()
        
        assert "detail" in data
        detail = data["detail"]
        assert detail["status"] == "error"
        assert "Visualization not found" in detail["message"]
        assert detail["error_code"] == "VISUALIZATION_NOT_FOUND"
    
    def test_base64_format_requires_file_id(self, client, completed_job_with_visualizations):
        """Test that base64 format without file_id returns URL format."""
        job_id = completed_job_with_visualizations
        
        # Get visualizations in base64 format without file_id
        # This should fall back to URL format with multiple files
        response = client.get(f"/api/v1/jobs/{job_id}/visualization?format=base64")
        
        # Should return success with URL format (not base64)
        assert response.status_code == 200
        data = response.json()
        
        # Should have visualizations array (URL format)
        assert "visualizations" in data["data"]
        assert len(data["data"]["visualizations"]) > 0


class TestFileServingEndpoints:
    """Tests for the /api/v1/files endpoints."""
    
    def test_get_original_image(self, client, completed_job_with_visualizations):
        """Test serving original uploaded image."""
        job_id = completed_job_with_visualizations
        
        # Get job data to find file_id
        job_data = storage_service.get_job(job_id)
        file_id = job_data["files"][0]["file_id"]
        
        # Get original image
        response = client.get(f"/api/v1/files/{job_id}/{file_id}/original")
        
        # Verify response
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("image/")
        
        # Verify it's a valid image
        img = Image.open(BytesIO(response.content))
        assert img.size[0] > 0  # width
        assert img.size[1] > 0  # height
    
    def test_get_annotated_image(self, client, completed_job_with_visualizations):
        """Test serving annotated image."""
        job_id = completed_job_with_visualizations
        
        # Get job data to find file_id
        job_data = storage_service.get_job(job_id)
        file_id = job_data["files"][0]["file_id"]
        
        # Get annotated image
        response = client.get(f"/api/v1/files/{job_id}/{file_id}/annotated")
        
        # Verify response
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("image/")
        
        # Verify it's a valid image
        img = Image.open(BytesIO(response.content))
        assert img.size[0] > 0
        assert img.size[1] > 0
    
    def test_get_original_image_not_found(self, client):
        """Test 404 for non-existent original image."""
        fake_job_id = "00000000-0000-0000-0000-000000000000"
        fake_file_id = "nonexistent-file"
        
        response = client.get(f"/api/v1/files/{fake_job_id}/{fake_file_id}/original")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error_code"] == "ORIGINAL_IMAGE_NOT_FOUND"
    
    def test_get_annotated_image_not_found(self, client, completed_job_with_visualizations):
        """Test 404 for non-existent annotated image."""
        job_id = completed_job_with_visualizations
        fake_file_id = "nonexistent-file"
        
        response = client.get(f"/api/v1/files/{job_id}/{fake_file_id}/annotated")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        # Should be FILE_NOT_FOUND since file_id doesn't exist in job
        assert data["detail"]["error_code"] == "FILE_NOT_FOUND"
