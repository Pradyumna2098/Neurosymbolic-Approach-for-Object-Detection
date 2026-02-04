"""Unit tests for the image upload endpoint.

Tests the /api/v1/upload endpoint for file uploads, validation,
and job creation.
"""

import sys
from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parents[2] / "backend"))

from app.main import app


def create_test_image(width: int, height: int, format: str = "PNG") -> bytes:
    """Helper to create a test image with specified dimensions and format.
    
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


class TestUploadEndpoint:
    """Tests for the /api/v1/upload endpoint."""
    
    def test_upload_single_valid_image(self, client):
        """Test uploading a single valid image."""
        # Create a valid test image
        image_data = create_test_image(640, 480, "PNG")
        
        # Upload the image
        response = client.post(
            "/api/v1/upload",
            files={"files": ("test_image.png", image_data, "image/png")}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "job_id" in data
        assert len(data["files"]) == 1
        
        # Verify file metadata
        file_info = data["files"][0]
        assert file_info["filename"] == "test_image.png"
        assert file_info["size"] > 0
        assert "file_id" in file_info
        assert file_info["format"] == "PNG"
        assert file_info["width"] == 640
        assert file_info["height"] == 480
    
    def test_upload_multiple_valid_images(self, client):
        """Test uploading multiple valid images."""
        # Create multiple test images
        image1 = create_test_image(640, 480, "PNG")
        image2 = create_test_image(800, 600, "JPEG")
        
        # Upload both images
        response = client.post(
            "/api/v1/upload",
            files=[
                ("files", ("image1.png", image1, "image/png")),
                ("files", ("image2.jpg", image2, "image/jpeg"))
            ]
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "job_id" in data
        assert len(data["files"]) == 2
        
        # Verify both files are present
        filenames = [f["filename"] for f in data["files"]]
        assert "image1.png" in filenames
        assert "image2.jpg" in filenames
    
    def test_upload_no_files(self, client):
        """Test uploading with no files."""
        # Attempt upload with no files
        response = client.post("/api/v1/upload")
        
        # Should return 422 (Unprocessable Entity) due to missing required field
        assert response.status_code == 422
    
    def test_upload_invalid_format(self, client):
        """Test uploading an unsupported file format."""
        # Create a text file (invalid format)
        text_data = b"This is not an image file"
        
        # Attempt upload
        response = client.post(
            "/api/v1/upload",
            files={"files": ("document.txt", text_data, "text/plain")}
        )
        
        # Should return 400 with validation error
        assert response.status_code == 400
        data = response.json()
        
        assert data["detail"]["status"] == "error"
        assert "validation" in data["detail"]["message"].lower()
    
    def test_upload_image_too_small(self, client):
        """Test uploading an image that's too small."""
        # Create a very small image (below minimum)
        small_image = create_test_image(32, 32, "PNG")
        
        # Attempt upload
        response = client.post(
            "/api/v1/upload",
            files={"files": ("tiny.png", small_image, "image/png")}
        )
        
        # Should return 400 with validation error
        assert response.status_code == 400
        data = response.json()
        
        assert data["detail"]["status"] == "error"
    
    def test_upload_empty_file(self, client):
        """Test uploading an empty file."""
        # Create empty file
        empty_data = b""
        
        # Attempt upload
        response = client.post(
            "/api/v1/upload",
            files={"files": ("empty.png", empty_data, "image/png")}
        )
        
        # Should return 400
        assert response.status_code == 400
        data = response.json()
        
        assert data["detail"]["status"] == "error"
    
    def test_upload_too_many_files(self, client):
        """Test uploading more than the maximum allowed files."""
        # Create 101 files (exceeds limit of 100)
        files = []
        for i in range(101):
            image_data = create_test_image(64, 64, "PNG")
            files.append(("files", (f"image{i}.png", image_data, "image/png")))
        
        # Attempt upload
        response = client.post("/api/v1/upload", files=files)
        
        # Should return 400
        assert response.status_code == 400
        data = response.json()
        
        assert data["detail"]["status"] == "error"
        assert "too many" in data["detail"]["message"].lower()
    
    def test_upload_creates_job(self, client):
        """Test that upload creates a job with correct status."""
        # Create and upload an image
        image_data = create_test_image(640, 480, "PNG")
        
        response = client.post(
            "/api/v1/upload",
            files={"files": ("test.png", image_data, "image/png")}
        )
        
        assert response.status_code == 200
        data = response.json()
        job_id = data["job_id"]
        
        # Verify job_id is a valid UUID format
        import uuid
        try:
            uuid.UUID(job_id)
        except ValueError:
            pytest.fail(f"job_id is not a valid UUID: {job_id}")
        
        # Verify job was created with correct status
        from app.services import storage_service
        job = storage_service.get_job(job_id)
        assert job is not None
        assert job["status"] == "uploaded"
        assert job["job_id"] == job_id
    
    def test_upload_jpeg_format(self, client):
        """Test uploading JPEG format images."""
        image_data = create_test_image(800, 600, "JPEG")
        
        response = client.post(
            "/api/v1/upload",
            files={"files": ("photo.jpg", image_data, "image/jpeg")}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["files"][0]["format"] == "JPEG"
    
    def test_upload_tiff_format(self, client):
        """Test uploading TIFF format images."""
        image_data = create_test_image(1024, 768, "TIFF")
        
        response = client.post(
            "/api/v1/upload",
            files={"files": ("scan.tiff", image_data, "image/tiff")}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["files"][0]["format"] == "TIFF"
    
    def test_upload_preserves_filename(self, client):
        """Test that original filename is preserved in response."""
        image_data = create_test_image(640, 480, "PNG")
        original_filename = "my_special_image.png"
        
        response = client.post(
            "/api/v1/upload",
            files={"files": (original_filename, image_data, "image/png")}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["files"][0]["filename"] == original_filename
