"""Unit tests for the job results endpoint.

Tests the /api/v1/jobs/{job_id}/results endpoint for retrieving detection
predictions from local files.
"""

import sys
from io import BytesIO
from pathlib import Path

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
    img = Image.new('RGB', (width, height), color='blue')
    buffer = BytesIO()
    img.save(buffer, format=format)
    return buffer.getvalue()


@pytest.fixture
def client():
    """Create FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def completed_job_with_results():
    """Create a completed job with mock prediction files.
    
    Returns:
        job_id as string
    """
    # Create job
    job_id = storage_service.create_job(status="completed")
    
    # Add mock file to job
    file_id = "test-file-id-001"
    storage_service.update_job(
        job_id,
        files=[{
            "file_id": file_id,
            "filename": "test_image.png",
            "stored_filename": f"{file_id}.png",
            "size_bytes": 1024,
            "uploaded_at": "2026-02-04T00:00:00Z"
        }]
    )
    
    # Create mock prediction file in refined results directory
    results_dir = storage_service._get_job_results_dir(job_id, stage="refined")
    pred_file = results_dir / f"{file_id}.txt"
    
    # Write YOLO format predictions
    # Format: class_id center_x center_y width height confidence
    predictions = [
        "0 0.5 0.5 0.2 0.3 0.95",  # High confidence detection
        "1 0.3 0.7 0.15 0.25 0.87",  # Second detection
        "0 0.8 0.2 0.1 0.1 0.76"  # Another class 0 detection
    ]
    
    with open(pred_file, "w") as f:
        f.write("\n".join(predictions) + "\n")
    
    return job_id


@pytest.fixture
def completed_job_no_results():
    """Create a completed job without prediction files.
    
    Returns:
        job_id as string
    """
    job_id = storage_service.create_job(status="completed")
    # Results directory exists but is empty
    storage_service._get_job_results_dir(job_id, stage="refined")
    return job_id


@pytest.fixture
def processing_job():
    """Create a processing job.
    
    Returns:
        job_id as string
    """
    job_id = storage_service.create_job(status="processing")
    return job_id


class TestJobResultsEndpoint:
    """Tests for the /api/v1/jobs/{job_id}/results endpoint."""
    
    def test_get_results_completed_job(self, client, completed_job_with_results):
        """Test retrieving results for a completed job with predictions."""
        job_id = completed_job_with_results
        
        # Get results
        response = client.get(f"/api/v1/jobs/{job_id}/results")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Check top-level structure
        assert data["status"] == "success"
        assert "data" in data
        
        results_data = data["data"]
        assert results_data["job_id"] == job_id
        assert results_data["format"] == "json"
        assert results_data["total_images"] == 1
        assert results_data["total_detections"] == 3
        
        # Check results array
        assert len(results_data["results"]) == 1
        image_result = results_data["results"][0]
        assert image_result["file_id"] == "test-file-id-001"
        assert image_result["filename"] == "test_image.png"
        assert image_result["detection_count"] == 3
        assert len(image_result["detections"]) == 3
    
    def test_get_results_detection_format(self, client, completed_job_with_results):
        """Test that detections are correctly parsed and formatted."""
        job_id = completed_job_with_results
        
        # Get results
        response = client.get(f"/api/v1/jobs/{job_id}/results")
        
        assert response.status_code == 200
        data = response.json()
        
        detections = data["data"]["results"][0]["detections"]
        
        # Check first detection (class 0, 0.95 confidence)
        det1 = detections[0]
        assert det1["class_id"] == 0
        assert det1["confidence"] == 0.95
        assert det1["bbox"]["format"] == "yolo"
        assert det1["bbox"]["center_x"] == 0.5
        assert det1["bbox"]["center_y"] == 0.5
        assert det1["bbox"]["width"] == 0.2
        assert det1["bbox"]["height"] == 0.3
        
        # Check second detection (class 1, 0.87 confidence)
        det2 = detections[1]
        assert det2["class_id"] == 1
        assert det2["confidence"] == 0.87
        
        # Check third detection (class 0, 0.76 confidence)
        det3 = detections[2]
        assert det3["class_id"] == 0
        assert det3["confidence"] == 0.76
    
    def test_get_results_class_distribution(self, client, completed_job_with_results):
        """Test that class distribution is correctly calculated."""
        job_id = completed_job_with_results
        
        # Get results
        response = client.get(f"/api/v1/jobs/{job_id}/results")
        
        assert response.status_code == 200
        data = response.json()
        
        class_dist = data["data"]["class_distribution"]
        
        # Should have 2 classes (0 and 1)
        assert len(class_dist) == 2
        
        # Class 0: 2 detections with avg confidence (0.95 + 0.76) / 2 = 0.855
        class_0 = next(c for c in class_dist if c["class_id"] == 0)
        assert class_0["count"] == 2
        assert abs(class_0["average_confidence"] - 0.855) < 0.001
        
        # Class 1: 1 detection with confidence 0.87
        class_1 = next(c for c in class_dist if c["class_id"] == 1)
        assert class_1["count"] == 1
        assert class_1["average_confidence"] == 0.87
    
    def test_get_results_job_not_found(self, client):
        """Test 404 response for non-existent job."""
        fake_job_id = "00000000-0000-0000-0000-000000000000"
        
        # Get results
        response = client.get(f"/api/v1/jobs/{fake_job_id}/results")
        
        # Verify 404 response
        assert response.status_code == 404
        data = response.json()
        
        assert "error" in data
        error = data["error"]
        assert data["status"] == "error"
        assert "Job not found" in error["message"]
        assert error["code"] == "JOB_NOT_FOUND"
    
    def test_get_results_job_not_completed(self, client, processing_job):
        """Test 404 response for incomplete job."""
        job_id = processing_job
        
        # Get results
        response = client.get(f"/api/v1/jobs/{job_id}/results")
        
        # Verify 404 response
        assert response.status_code == 404
        data = response.json()
        
        assert "error" in data
        error = data["error"]
        assert data["status"] == "error"
        assert "Results not available" in error["message"]
        assert error["code"] == "RESULTS_NOT_READY"
        assert "processing" in error["details"]
    
    def test_get_results_no_prediction_files(self, client, completed_job_no_results):
        """Test 404 response when no prediction files exist."""
        job_id = completed_job_no_results
        
        # Get results
        response = client.get(f"/api/v1/jobs/{job_id}/results")
        
        # Verify 404 response
        assert response.status_code == 404
        data = response.json()
        
        assert "error" in data
        error = data["error"]
        assert data["status"] == "error"
        assert "Results not available" in error["message"]
        assert error["code"] == "RESULTS_NOT_FOUND"
    
    def test_get_results_response_schema(self, client, completed_job_with_results):
        """Test that response matches the expected schema."""
        job_id = completed_job_with_results
        
        # Get results
        response = client.get(f"/api/v1/jobs/{job_id}/results")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required top-level fields
        assert "status" in data
        assert "data" in data
        
        results_data = data["data"]
        
        # Check required data fields
        required_fields = [
            "job_id", "format", "total_images", "total_detections",
            "class_distribution", "results"
        ]
        for field in required_fields:
            assert field in results_data, f"Missing required field: {field}"
        
        # Check image result structure
        assert len(results_data["results"]) > 0
        image_result = results_data["results"][0]
        assert "file_id" in image_result
        assert "filename" in image_result
        assert "detections" in image_result
        assert "detection_count" in image_result
        
        # Check detection structure
        assert len(image_result["detections"]) > 0
        detection = image_result["detections"][0]
        assert "class_id" in detection
        assert "confidence" in detection
        assert "bbox" in detection
        
        # Check bbox structure
        bbox = detection["bbox"]
        assert "format" in bbox
        assert bbox["format"] == "yolo"
        assert "center_x" in bbox
        assert "center_y" in bbox
        assert "width" in bbox
        assert "height" in bbox
    
    def test_get_results_multiple_images(self, client):
        """Test results with multiple images."""
        # Create job with multiple prediction files
        job_id = storage_service.create_job(status="completed")
        
        results_dir = storage_service._get_job_results_dir(job_id, stage="refined")
        
        # Create predictions for 3 different images
        for i in range(3):
            file_id = f"image-{i:03d}"
            pred_file = results_dir / f"{file_id}.txt"
            
            # Add file info to job
            job_data = storage_service.get_job(job_id)
            files = job_data.get("files", [])
            files.append({
                "file_id": file_id,
                "filename": f"image_{i}.png",
                "stored_filename": f"{file_id}.png",
                "size_bytes": 1024,
                "uploaded_at": "2026-02-04T00:00:00Z"
            })
            storage_service.update_job(job_id, files=files)
            
            # Write predictions (1 per image for simplicity)
            with open(pred_file, "w") as f:
                f.write(f"{i} 0.5 0.5 0.2 0.2 0.9\n")
        
        # Get results
        response = client.get(f"/api/v1/jobs/{job_id}/results")
        
        assert response.status_code == 200
        data = response.json()
        
        results_data = data["data"]
        assert results_data["total_images"] == 3
        assert results_data["total_detections"] == 3
        assert len(results_data["results"]) == 3
        
        # Verify each image has 1 detection
        for result in results_data["results"]:
            assert result["detection_count"] == 1
            assert len(result["detections"]) == 1
    
    def test_get_results_invalid_lines_skipped(self, client):
        """Test that invalid prediction lines are skipped gracefully."""
        # Create job with malformed predictions
        job_id = storage_service.create_job(status="completed")
        
        file_id = "test-file-malformed"
        storage_service.update_job(
            job_id,
            files=[{
                "file_id": file_id,
                "filename": "test.png",
                "stored_filename": f"{file_id}.png",
                "size_bytes": 1024
            }]
        )
        
        results_dir = storage_service._get_job_results_dir(job_id, stage="refined")
        pred_file = results_dir / f"{file_id}.txt"
        
        # Write predictions with some invalid lines
        with open(pred_file, "w") as f:
            f.write("0 0.5 0.5 0.2 0.2 0.95\n")  # Valid
            f.write("invalid line here\n")  # Invalid - wrong format
            f.write("0 0.5 0.5\n")  # Invalid - too few values
            f.write("1 0.3 0.7 0.15 0.25 0.87\n")  # Valid
            f.write("\n")  # Empty line
        
        # Get results
        response = client.get(f"/api/v1/jobs/{job_id}/results")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only have 2 valid detections
        results_data = data["data"]
        assert results_data["total_detections"] == 2
        assert len(results_data["results"][0]["detections"]) == 2
    
    def test_openapi_schema_includes_results_endpoint(self, client):
        """Test that the OpenAPI schema includes the results endpoint."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        
        # Verify endpoint is documented
        assert "paths" in schema
        assert "/api/v1/jobs/{job_id}/results" in schema["paths"]
        
        # Verify GET method is documented
        endpoint_spec = schema["paths"]["/api/v1/jobs/{job_id}/results"]
        assert "get" in endpoint_spec
        
        # Verify responses are documented
        get_spec = endpoint_spec["get"]
        assert "responses" in get_spec
        assert "200" in get_spec["responses"]



