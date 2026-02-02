"""Unit tests for backend API endpoints."""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys
import importlib.util

# Load the backend module dynamically
repo_root = Path(__file__).resolve().parents[2]
backend_main_path = repo_root / "backend" / "app" / "main.py"

spec = importlib.util.spec_from_file_location("backend_main", backend_main_path)
backend_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend_main)

# Extract what we need
app = backend_main.app
training_jobs = backend_main.training_jobs
results_cache = backend_main.results_cache


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up state between tests."""
    training_jobs.clear()
    results_cache.clear()
    yield
    training_jobs.clear()
    results_cache.clear()


def test_root_endpoint(client):
    """Test root endpoint returns service information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "status" in data
    assert data["status"] == "healthy"


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_train_endpoint_missing_config(client):
    """Test training endpoint with missing config file."""
    response = client.post(
        "/train",
        json={"config_path": "/nonexistent/config.yaml"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_train_endpoint_valid_request(client, tmp_path):
    """Test training endpoint with valid config."""
    # Create temporary config file
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text("epochs: 10\n")
    
    response = client.post(
        "/train",
        json={"config_path": str(config_file)}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"
    assert "train_" in data["job_id"]


def test_results_endpoint_job_not_found(client):
    """Test results endpoint with nonexistent job ID."""
    response = client.get("/results/nonexistent_job")
    assert response.status_code == 404


def test_results_endpoint_job_exists(client):
    """Test results endpoint with existing job."""
    # Create a mock job
    job_id = "test_job_123"
    training_jobs[job_id] = {
        "status": "completed",
        "created_at": "2024-01-01T00:00:00",
        "results": {"mAP": 0.85},
        "logs": ["Training started", "Training completed"]
    }
    
    response = client.get(f"/results/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert data["status"] == "completed"
    assert data["metrics"]["mAP"] == 0.85
    assert len(data["logs"]) == 2


def test_list_results_empty(client):
    """Test listing results when no jobs exist."""
    response = client.get("/results")
    assert response.status_code == 200
    data = response.json()
    assert data["total_jobs"] == 0
    assert len(data["jobs"]) == 0


def test_list_results_with_jobs(client):
    """Test listing results with multiple jobs."""
    # Create mock jobs
    training_jobs["job1"] = {
        "status": "completed",
        "created_at": "2024-01-01T00:00:00"
    }
    training_jobs["job2"] = {
        "status": "running",
        "created_at": "2024-01-01T01:00:00"
    }
    
    response = client.get("/results")
    assert response.status_code == 200
    data = response.json()
    assert data["total_jobs"] == 2
    assert len(data["jobs"]) == 2


def test_metrics_endpoint(client):
    """Test Prometheus metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    # Check for some expected metrics
    content = response.text
    assert "train_requests_total" in content or "python_info" in content
