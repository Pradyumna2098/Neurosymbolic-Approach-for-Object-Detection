"""Local filesystem storage service for prototype implementation.

This service provides file-based storage for jobs, uploads, results, and
visualizations. This is a prototype implementation; production would use
PostgreSQL for metadata and S3/MinIO for files.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core import settings


class LocalStorageService:
    """Service for managing local filesystem storage."""
    
    def __init__(self):
        """Initialize storage service and ensure directories exist."""
        settings.ensure_directories()
    
    # Job Management Methods
    
    def create_job(self, job_data: Dict[str, Any]) -> str:
        """Create a new job with a unique ID.
        
        Args:
            job_data: Dictionary containing job metadata
            
        Returns:
            str: Generated job ID
        """
        job_id = str(uuid.uuid4())
        job_data.update({
            "job_id": job_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "created"
        })
        
        job_file = settings.jobs_dir / f"{job_id}.json"
        with open(job_file, "w") as f:
            json.dump(job_data, f, indent=2)
        
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve job data by ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job data dictionary or None if not found
        """
        job_file = settings.jobs_dir / f"{job_id}.json"
        if not job_file.exists():
            return None
        
        with open(job_file, "r") as f:
            return json.load(f)
    
    def update_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """Update job data.
        
        Args:
            job_id: Job identifier
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False if job not found
        """
        job_data = self.get_job(job_id)
        if job_data is None:
            return False
        
        job_data.update(updates)
        job_data["updated_at"] = datetime.utcnow().isoformat()
        
        job_file = settings.jobs_dir / f"{job_id}.json"
        with open(job_file, "w") as f:
            json.dump(job_data, f, indent=2)
        
        return True
    
    def list_jobs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all jobs.
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of job data dictionaries
        """
        jobs = []
        job_files = sorted(
            settings.jobs_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:limit]
        
        for job_file in job_files:
            with open(job_file, "r") as f:
                jobs.append(json.load(f))
        
        return jobs
    
    # File Management Methods
    
    def save_upload(self, filename: str, content: bytes) -> Path:
        """Save uploaded file to uploads directory.
        
        Args:
            filename: Original filename
            content: File content as bytes
            
        Returns:
            Path to saved file
        """
        # Generate unique filename to avoid collisions
        file_id = uuid.uuid4().hex[:8]
        safe_filename = f"{file_id}_{Path(filename).name}"
        file_path = settings.uploads_dir / safe_filename
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        return file_path
    
    def get_upload_path(self, filename: str) -> Optional[Path]:
        """Get path to uploaded file.
        
        Args:
            filename: Name of uploaded file
            
        Returns:
            Path to file or None if not found
        """
        file_path = settings.uploads_dir / filename
        return file_path if file_path.exists() else None
    
    def save_result(self, job_id: str, result_data: Dict[str, Any]) -> Path:
        """Save prediction results for a job.
        
        Args:
            job_id: Job identifier
            result_data: Prediction results dictionary
            
        Returns:
            Path to saved results file
        """
        result_file = settings.results_dir / f"{job_id}.json"
        with open(result_file, "w") as f:
            json.dump(result_data, f, indent=2)
        
        return result_file
    
    def get_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve prediction results for a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Results dictionary or None if not found
        """
        result_file = settings.results_dir / f"{job_id}.json"
        if not result_file.exists():
            return None
        
        with open(result_file, "r") as f:
            return json.load(f)
    
    def save_visualization(self, job_id: str, image_data: bytes, suffix: str = "") -> Path:
        """Save visualization image for a job.
        
        Args:
            job_id: Job identifier
            image_data: Image content as bytes
            suffix: Optional suffix for filename (e.g., '_annotated')
            
        Returns:
            Path to saved visualization
        """
        viz_file = settings.visualizations_dir / f"{job_id}{suffix}.png"
        with open(viz_file, "wb") as f:
            f.write(image_data)
        
        return viz_file
    
    def get_visualization_path(self, job_id: str, suffix: str = "") -> Optional[Path]:
        """Get path to visualization image.
        
        Args:
            job_id: Job identifier
            suffix: Optional suffix for filename
            
        Returns:
            Path to visualization or None if not found
        """
        viz_file = settings.visualizations_dir / f"{job_id}{suffix}.png"
        return viz_file if viz_file.exists() else None


# Global storage service instance
storage = LocalStorageService()
