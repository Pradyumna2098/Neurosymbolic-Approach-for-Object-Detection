"""Unit tests for the storage service."""

import sys
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

# Add backend directory (project_root/backend) to Python path
# Path structure: tests/backend/test_storage_service.py -> tests/ -> project root -> backend/
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from backend.app.services.storage import StorageService, FileValidationError


def create_test_image(width: int, height: int, format: str = "PNG") -> bytes:
    """Helper to create a test image with specified dimensions and format.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        format: Image format (PNG, JPEG, TIFF)
        
    Returns:
        Image data as bytes
    """
    img = Image.new('RGB', (width, height), color='red')
    buffer = BytesIO()
    img.save(buffer, format=format)
    return buffer.getvalue()


@pytest.fixture
def storage_service(tmp_path, monkeypatch):
    """Create a storage service with temporary directories."""
    from backend.app.core import settings
    
    # Mock settings to use temporary directories
    monkeypatch.setattr(settings, "data_root", tmp_path)
    monkeypatch.setattr(settings, "uploads_dir", tmp_path / "uploads")
    monkeypatch.setattr(settings, "jobs_dir", tmp_path / "jobs")
    monkeypatch.setattr(settings, "results_dir", tmp_path / "results")
    monkeypatch.setattr(settings, "visualizations_dir", tmp_path / "visualizations")
    
    service = StorageService()
    return service


class TestFileValidation:
    """Tests for file validation functionality."""
    
    def test_validate_valid_png(self, storage_service):
        """Test validation of a valid PNG image."""
        content = create_test_image(640, 480, "PNG")
        is_valid, error_msg, metadata = storage_service.validate_image_file(
            content, "test.png"
        )
        
        assert is_valid is True
        assert error_msg is None
        assert metadata is not None
        assert metadata['width'] == 640
        assert metadata['height'] == 480
        assert metadata['format'] == 'PNG'
    
    def test_validate_valid_jpeg(self, storage_service):
        """Test validation of a valid JPEG image."""
        content = create_test_image(800, 600, "JPEG")
        is_valid, error_msg, metadata = storage_service.validate_image_file(
            content, "test.jpg"
        )
        
        assert is_valid is True
        assert error_msg is None
        assert metadata is not None
        assert metadata['format'] == 'JPEG'
    
    def test_validate_valid_tiff(self, storage_service):
        """Test validation of a valid TIFF image."""
        content = create_test_image(1024, 768, "TIFF")
        is_valid, error_msg, metadata = storage_service.validate_image_file(
            content, "test.tiff"
        )
        
        assert is_valid is True
        assert error_msg is None
        assert metadata is not None
        assert metadata['format'] == 'TIFF'
    
    def test_validate_valid_bmp(self, storage_service):
        """Test validation of a valid BMP image."""
        content = create_test_image(640, 480, "BMP")
        is_valid, error_msg, metadata = storage_service.validate_image_file(
            content, "test.bmp"
        )
        
        assert is_valid is True
        assert error_msg is None
        assert metadata is not None
        assert metadata['format'] == 'BMP'
    
    def test_validate_unsupported_format(self, storage_service):
        """Test rejection of unsupported file format."""
        content = b"not an image"
        is_valid, error_msg, metadata = storage_service.validate_image_file(
            content, "test.gif"  # GIF is not supported
        )
        
        assert is_valid is False
        assert "INVALID_FORMAT" in error_msg
        assert metadata is None
    
    def test_validate_file_too_small(self, storage_service):
        """Test rejection of files that are too small."""
        content = b"tiny"  # Less than 1KB
        is_valid, error_msg, metadata = storage_service.validate_image_file(
            content, "test.png"
        )
        
        assert is_valid is False
        assert "FILE_TOO_SMALL" in error_msg
        assert metadata is None
    
    def test_validate_file_too_large(self, storage_service):
        """Test rejection of files exceeding size limit."""
        # Create content larger than 50MB
        large_content = b"x" * (51 * 1024 * 1024)
        is_valid, error_msg, metadata = storage_service.validate_image_file(
            large_content, "test.png"
        )
        
        assert is_valid is False
        assert "FILE_TOO_LARGE" in error_msg
        assert "50MB" in error_msg
        assert metadata is None
    
    def test_validate_dimensions_too_small(self, storage_service):
        """Test rejection of images with dimensions too small."""
        # Create a larger image (in bytes) but with small dimensions
        # Use TIFF format which creates larger files
        content = create_test_image(50, 50, "TIFF")  # Below 64x64 minimum
        is_valid, error_msg, metadata = storage_service.validate_image_file(
            content, "test.tiff"
        )
        
        assert is_valid is False
        assert "DIMENSIONS_TOO_SMALL" in error_msg
        assert metadata is None
    
    def test_validate_dimensions_too_large(self, storage_service):
        """Test rejection of images with dimensions exceeding maximum."""
        content = create_test_image(9000, 9000, "PNG")  # Above 8192x8192 max
        is_valid, error_msg, metadata = storage_service.validate_image_file(
            content, "test.png"
        )
        
        assert is_valid is False
        assert "DIMENSIONS_EXCEEDED" in error_msg
        assert metadata is None
    
    def test_validate_corrupted_file(self, storage_service):
        """Test rejection of corrupted image files."""
        content = b"corrupted image data that is not a real image but looks big" * 100
        is_valid, error_msg, metadata = storage_service.validate_image_file(
            content, "test.png"
        )
        
        assert is_valid is False
        assert "CORRUPTED_FILE" in error_msg
        assert metadata is None
    
    def test_validate_format_mismatch(self, storage_service):
        """Test rejection when file extension doesn't match content."""
        # Create a PNG but name it as JPEG
        content = create_test_image(640, 480, "PNG")
        is_valid, error_msg, metadata = storage_service.validate_image_file(
            content, "test.jpg"  # Wrong extension
        )
        
        assert is_valid is False
        assert "INVALID_FORMAT" in error_msg
        assert "does not match" in error_msg
        assert metadata is None


class TestJobManagement:
    """Tests for job management functionality."""
    
    def test_create_job(self, storage_service):
        """Test creating a new job."""
        job_id = storage_service.create_job(config={"model": "yolo"})
        
        assert job_id is not None
        assert len(job_id) == 36  # UUID format
        
        # Verify job was saved
        job = storage_service.get_job(job_id)
        assert job is not None
        assert job["job_id"] == job_id
        assert job["status"] == "queued"
        assert job["config"]["model"] == "yolo"
        assert "created_at" in job
        assert job["files"] == []
        assert job["progress"] == {}
        assert job["error"] is None
    
    def test_create_job_creates_directories(self, storage_service, tmp_path):
        """Test that job creation creates required directories."""
        job_id = storage_service.create_job()
        
        # Check that all directories were created
        assert (tmp_path / "uploads" / job_id).exists()
        assert (tmp_path / "visualizations" / job_id).exists()
        assert (tmp_path / "results" / job_id / "raw").exists()
        assert (tmp_path / "results" / job_id / "nms").exists()
        assert (tmp_path / "results" / job_id / "refined").exists()
    
    def test_get_nonexistent_job(self, storage_service):
        """Test getting a job that doesn't exist."""
        job = storage_service.get_job("nonexistent-id")
        assert job is None
    
    def test_update_job_status(self, storage_service):
        """Test updating job status."""
        job_id = storage_service.create_job()
        
        success = storage_service.update_job(job_id, status="processing")
        assert success is True
        
        job = storage_service.get_job(job_id)
        assert job["status"] == "processing"
        assert "updated_at" in job
    
    def test_update_job_progress(self, storage_service):
        """Test updating job progress."""
        job_id = storage_service.create_job()
        
        progress = {"stage": "nms", "percent": 50}
        success = storage_service.update_job(job_id, progress=progress)
        assert success is True
        
        job = storage_service.get_job(job_id)
        assert job["progress"] == progress
    
    def test_update_job_error(self, storage_service):
        """Test updating job with error."""
        job_id = storage_service.create_job()
        
        error_msg = "Model failed to load"
        success = storage_service.update_job(
            job_id, 
            status="failed", 
            error=error_msg
        )
        assert success is True
        
        job = storage_service.get_job(job_id)
        assert job["status"] == "failed"
        assert job["error"] == error_msg
    
    def test_update_nonexistent_job(self, storage_service):
        """Test updating a job that doesn't exist."""
        success = storage_service.update_job("nonexistent-id", status="done")
        assert success is False
    
    def test_list_jobs(self, storage_service):
        """Test listing all jobs."""
        import time
        
        # Create multiple jobs
        job_ids = []
        for i in range(3):
            job_id = storage_service.create_job(config={"index": i})
            job_ids.append(job_id)
            time.sleep(0.01)  # Small delay for timestamp ordering
        
        # List jobs
        jobs = storage_service.list_jobs()
        assert len(jobs) == 3
        
        # Verify jobs are present
        retrieved_ids = {job["job_id"] for job in jobs}
        assert retrieved_ids == set(job_ids)
    
    def test_list_jobs_with_limit(self, storage_service):
        """Test listing jobs with a limit."""
        # Create multiple jobs
        for i in range(5):
            storage_service.create_job()
        
        # List with limit
        jobs = storage_service.list_jobs(limit=2)
        assert len(jobs) == 2


class TestFileManagement:
    """Tests for file upload and management functionality."""
    
    def test_save_upload_with_validation(self, storage_service):
        """Test saving an uploaded file with validation."""
        job_id = storage_service.create_job()
        content = create_test_image(640, 480, "PNG")
        
        file_id, file_path, metadata = storage_service.save_upload(
            job_id, "test.png", content, validate=True
        )
        
        assert file_id is not None
        assert len(file_id) == 36  # UUID format
        assert file_path.exists()
        assert file_path.name.endswith(".png")
        assert metadata is not None
        assert metadata['width'] == 640
        assert metadata['height'] == 480
        
        # Verify file was added to job
        job = storage_service.get_job(job_id)
        assert len(job["files"]) == 1
        assert job["files"][0]["file_id"] == file_id
        assert job["files"][0]["filename"] == "test.png"
    
    def test_save_upload_without_validation(self, storage_service):
        """Test saving a file without validation."""
        job_id = storage_service.create_job()
        content = b"any content"
        
        file_id, file_path, metadata = storage_service.save_upload(
            job_id, "test.dat", content, validate=False
        )
        
        assert file_id is not None
        assert file_path.exists()
        assert metadata is None  # No metadata when validation is disabled
    
    def test_save_upload_invalid_file(self, storage_service):
        """Test that invalid files are rejected."""
        job_id = storage_service.create_job()
        # Create content that is large enough to pass size check but corrupted
        content = b"invalid image data" * 1000  # Over 1KB but not a valid image
        
        with pytest.raises(FileValidationError) as exc_info:
            storage_service.save_upload(job_id, "test.png", content, validate=True)
        
        assert "CORRUPTED_FILE" in str(exc_info.value)
    
    def test_save_upload_with_invalid_filename(self, storage_service):
        """Test that filenames with shell metacharacters or invalid patterns are rejected."""
        job_id = storage_service.create_job()
        content = create_test_image(640, 480, "PNG")
        
        # Test filenames that should be rejected (after basename extraction)
        # Note: Path traversal (../) is handled by Path().name extraction
        malicious_filenames = [
            "file;with;semicolon.png",  # Shell metacharacter
            "file|pipe.png",            # Pipe character
            "file&ampersand.png",       # Ampersand
            ".hidden.png",              # Starts with dot
            "noextension",              # No extension
            "file with spaces.png",     # Spaces not allowed
            "file$dollar.png",          # Dollar sign
        ]
        
        for filename in malicious_filenames:
            with pytest.raises(FileValidationError) as exc_info:
                storage_service.save_upload(job_id, filename, content, validate=True)
            assert "Invalid filename" in str(exc_info.value)
    
    def test_save_upload_sanitizes_path_traversal(self, storage_service):
        """Test that path traversal in filenames is safely handled."""
        job_id = storage_service.create_job()
        content = create_test_image(640, 480, "PNG")
        
        # Path traversal attempts - basename extraction makes them safe
        # The sanitize function extracts only the basename, preventing directory traversal
        file_id, file_path, metadata = storage_service.save_upload(
            job_id, "../../../etc/passwd.png", content, validate=True
        )
        
        # Verify the file was saved with only the basename (passwd.png)
        job = storage_service.get_job(job_id)
        assert job["files"][0]["filename"] == "passwd.png"  # Path stripped
        assert file_path.exists()
        # Verify it's in the correct job directory, not in /etc/
        assert str(job_id) in str(file_path)
    
    def test_save_upload_with_invalid_job_id(self, storage_service):
        """Test that invalid job_id is rejected to prevent path traversal."""
        content = create_test_image(640, 480, "PNG")
        
        # Test various malicious job_ids
        malicious_job_ids = [
            "../../../etc",
            "../../data/evil",
            "not-a-uuid",
            "path/traversal",
        ]
        
        for job_id in malicious_job_ids:
            with pytest.raises(ValueError) as exc_info:
                storage_service.save_upload(job_id, "test.png", content, validate=True)
            assert "Invalid job_id" in str(exc_info.value) or "must be a valid UUID" in str(exc_info.value)
    
    def test_get_upload_path(self, storage_service):
        """Test retrieving upload path by file_id."""
        job_id = storage_service.create_job()
        content = create_test_image(640, 480, "PNG")
        
        file_id, saved_path, _ = storage_service.save_upload(
            job_id, "test.png", content
        )
        
        # Retrieve path
        retrieved_path = storage_service.get_upload_path(job_id, file_id)
        assert retrieved_path is not None
        assert retrieved_path == saved_path
        assert retrieved_path.exists()
    
    def test_get_upload_path_nonexistent(self, storage_service):
        """Test retrieving path for nonexistent file."""
        job_id = storage_service.create_job()
        path = storage_service.get_upload_path(job_id, "nonexistent-id")
        assert path is None
    
    def test_list_job_files(self, storage_service):
        """Test listing all files for a job."""
        job_id = storage_service.create_job()
        content = create_test_image(640, 480, "PNG")
        
        # Upload multiple files
        for i in range(3):
            storage_service.save_upload(job_id, f"test{i}.png", content)
        
        # List files
        files = storage_service.list_job_files(job_id)
        assert len(files) == 3
        assert all("file_id" in f for f in files)
        assert all("filename" in f for f in files)


class TestResultsManagement:
    """Tests for results storage functionality."""
    
    def test_save_result_raw_stage(self, storage_service):
        """Test saving raw prediction results."""
        job_id = storage_service.create_job()
        result_data = {
            "detections": [
                {"class": "car", "confidence": 0.95, "bbox": [10, 20, 100, 50]}
            ]
        }
        
        result_file = storage_service.save_result(job_id, result_data, stage="raw")
        
        assert result_file.exists()
        assert "raw" in str(result_file)
        
        # Verify result can be retrieved
        retrieved = storage_service.get_result(job_id, stage="raw")
        assert retrieved is not None
        assert len(retrieved["detections"]) == 1
        assert retrieved["detections"][0]["class"] == "car"
    
    def test_save_result_nms_stage(self, storage_service):
        """Test saving NMS-filtered results."""
        job_id = storage_service.create_job()
        result_data = {"detections": []}
        
        result_file = storage_service.save_result(job_id, result_data, stage="nms")
        
        assert result_file.exists()
        assert "nms" in str(result_file)
    
    def test_save_result_refined_stage(self, storage_service):
        """Test saving refined results."""
        job_id = storage_service.create_job()
        result_data = {"detections": []}
        
        result_file = storage_service.save_result(job_id, result_data, stage="refined")
        
        assert result_file.exists()
        assert "refined" in str(result_file)
    
    def test_get_result_default_stage(self, storage_service):
        """Test getting results defaults to refined stage."""
        job_id = storage_service.create_job()
        result_data = {"final": True}
        
        storage_service.save_result(job_id, result_data, stage="refined")
        
        # Get without specifying stage (should default to 'refined')
        retrieved = storage_service.get_result(job_id)
        assert retrieved is not None
        assert retrieved["final"] is True
    
    def test_get_nonexistent_result(self, storage_service):
        """Test getting results for a job that has no results."""
        job_id = storage_service.create_job()
        result = storage_service.get_result(job_id, stage="raw")
        assert result is None


class TestVisualizationManagement:
    """Tests for visualization storage functionality."""
    
    def test_save_visualization(self, storage_service):
        """Test saving visualization image."""
        job_id = storage_service.create_job()
        image_data = create_test_image(800, 600, "PNG")
        
        viz_path = storage_service.save_visualization(job_id, image_data)
        
        assert viz_path.exists()
        assert viz_path.name == "annotated.png"
        assert viz_path.read_bytes() == image_data
    
    def test_save_visualization_custom_filename(self, storage_service):
        """Test saving visualization with custom filename."""
        job_id = storage_service.create_job()
        image_data = create_test_image(800, 600, "PNG")
        
        viz_path = storage_service.save_visualization(
            job_id, image_data, filename="custom_viz.png"
        )
        
        assert viz_path.exists()
        assert viz_path.name == "custom_viz.png"
    
    def test_get_visualization_path(self, storage_service):
        """Test retrieving visualization path."""
        job_id = storage_service.create_job()
        image_data = create_test_image(800, 600, "PNG")
        
        saved_path = storage_service.save_visualization(job_id, image_data)
        
        # Retrieve path
        retrieved_path = storage_service.get_visualization_path(job_id)
        assert retrieved_path is not None
        assert retrieved_path == saved_path
        assert retrieved_path.exists()
    
    def test_get_visualization_path_nonexistent(self, storage_service):
        """Test retrieving path for nonexistent visualization."""
        job_id = storage_service.create_job()
        path = storage_service.get_visualization_path(job_id)
        assert path is None


class TestJobJSONSchema:
    """Tests to verify job JSON schema compliance."""
    
    def test_job_schema_has_required_fields(self, storage_service):
        """Test that created jobs have all required schema fields."""
        job_id = storage_service.create_job()
        job = storage_service.get_job(job_id)
        
        # Required fields per specification
        required_fields = [
            "job_id", "status", "created_at", 
            "config", "files", "progress", "error"
        ]
        
        for field in required_fields:
            assert field in job, f"Missing required field: {field}"
    
    def test_job_status_values(self, storage_service):
        """Test valid job status transitions."""
        job_id = storage_service.create_job()
        
        valid_statuses = ["queued", "processing", "completed", "failed"]
        
        for status in valid_statuses:
            success = storage_service.update_job(job_id, status=status)
            assert success is True
            
            job = storage_service.get_job(job_id)
            assert job["status"] == status
    
    def test_job_timestamps(self, storage_service):
        """Test that jobs have proper timestamp formats."""
        job_id = storage_service.create_job()
        job = storage_service.get_job(job_id)
        
        # Verify created_at is ISO format
        from datetime import datetime
        created_at = datetime.fromisoformat(job["created_at"])
        assert created_at is not None
        
        # Update job and verify updated_at
        storage_service.update_job(job_id, status="processing")
        job = storage_service.get_job(job_id)
        
        updated_at = datetime.fromisoformat(job["updated_at"])
        assert updated_at is not None
        assert updated_at >= created_at



