"""Unit tests for local storage service."""

import json
import sys
from pathlib import Path

import pytest

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from app.storage import LocalStorageService


@pytest.fixture
def storage_service(tmp_path):
    """Create a storage service with temporary directories."""
    # Mock settings for testing
    from app.core import settings
    settings.data_root = tmp_path
    settings.uploads_dir = tmp_path / "uploads"
    settings.jobs_dir = tmp_path / "jobs"
    settings.results_dir = tmp_path / "results"
    settings.visualizations_dir = tmp_path / "visualizations"
    
    service = LocalStorageService()
    return service


def test_create_job(storage_service):
    """Test creating a new job."""
    job_data = {"type": "inference", "image": "test.jpg"}
    job_id = storage_service.create_job(job_data)
    
    assert job_id is not None
    assert len(job_id) == 36  # UUID format
    
    # Verify job was saved
    job = storage_service.get_job(job_id)
    assert job is not None
    assert job["job_id"] == job_id
    assert job["type"] == "inference"
    assert job["status"] == "created"
    assert "created_at" in job


def test_get_nonexistent_job(storage_service):
    """Test getting a job that doesn't exist."""
    job = storage_service.get_job("nonexistent-id")
    assert job is None


def test_update_job(storage_service):
    """Test updating job data."""
    job_id = storage_service.create_job({"status": "created"})
    
    # Update the job
    success = storage_service.update_job(job_id, {"status": "processing"})
    assert success is True
    
    # Verify update
    job = storage_service.get_job(job_id)
    assert job["status"] == "processing"
    assert "updated_at" in job


def test_update_nonexistent_job(storage_service):
    """Test updating a job that doesn't exist."""
    success = storage_service.update_job("nonexistent-id", {"status": "done"})
    assert success is False


def test_list_jobs(storage_service):
    """Test listing all jobs."""
    import time
    
    # Create multiple jobs with slight delays to ensure different timestamps
    job_ids = []
    for i in range(3):
        job_id = storage_service.create_job({"index": i})
        job_ids.append(job_id)
        time.sleep(0.01)  # Small delay to ensure different mtimes
    
    # List jobs
    jobs = storage_service.list_jobs()
    assert len(jobs) == 3
    
    # Verify all jobs are present (order may vary slightly on fast systems)
    indices = {job["index"] for job in jobs}
    assert indices == {0, 1, 2}


def test_save_upload(storage_service):
    """Test saving an uploaded file."""
    filename = "test_image.jpg"
    content = b"fake image data"
    
    file_path = storage_service.save_upload(filename, content)
    
    assert file_path.exists()
    assert file_path.name.endswith("test_image.jpg")
    assert file_path.read_bytes() == content


def test_save_result(storage_service):
    """Test saving prediction results."""
    job_id = storage_service.create_job({"type": "inference"})
    result_data = {
        "detections": [
            {"class": "car", "confidence": 0.95}
        ]
    }
    
    result_file = storage_service.save_result(job_id, result_data)
    
    assert result_file.exists()
    
    # Verify result can be retrieved
    retrieved = storage_service.get_result(job_id)
    assert retrieved is not None
    assert len(retrieved["detections"]) == 1
    assert retrieved["detections"][0]["class"] == "car"


def test_get_nonexistent_result(storage_service):
    """Test getting results for a job that has no results."""
    result = storage_service.get_result("nonexistent-id")
    assert result is None


def test_save_visualization(storage_service):
    """Test saving visualization image."""
    job_id = storage_service.create_job({"type": "inference"})
    image_data = b"fake png data"
    
    viz_path = storage_service.save_visualization(job_id, image_data)
    
    assert viz_path.exists()
    assert viz_path.read_bytes() == image_data
    
    # Test with suffix
    viz_path2 = storage_service.save_visualization(job_id, image_data, "_annotated")
    assert viz_path2.exists()
    assert "_annotated" in viz_path2.name
