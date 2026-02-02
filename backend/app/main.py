"""Backend API server for the Neurosymbolic Object Detection pipeline."""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import time
import json
from datetime import datetime

# Import pipeline modules
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Neurosymbolic Object Detection API",
    description="RESTful API for training and inference with neurosymbolic object detection",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
train_requests = Counter('train_requests_total', 'Total number of training requests')
train_duration = Histogram('train_duration_seconds', 'Time spent training')
prediction_requests = Counter('prediction_requests_total', 'Total number of prediction requests')
pipeline_errors = Counter('pipeline_errors_total', 'Total number of pipeline errors')
preprocessing_duration = Histogram('preprocessing_duration_seconds', 'Time spent in preprocessing')
inference_duration = Histogram('inference_duration_seconds', 'Time spent in inference')
evaluation_duration = Histogram('evaluation_duration_seconds', 'Time spent in evaluation')

# Training state storage (in production, use a database)
training_jobs: Dict[str, Dict[str, Any]] = {}
results_cache: Dict[str, Dict[str, Any]] = {}


class TrainingRequest(BaseModel):
    """Request model for training endpoint."""
    config_path: str
    epochs: Optional[int] = None
    batch_size: Optional[int] = None
    learning_rate: Optional[float] = None


class PredictionRequest(BaseModel):
    """Request model for prediction endpoint."""
    image_paths: List[str]
    model_path: str
    confidence_threshold: float = 0.5


class TrainingResponse(BaseModel):
    """Response model for training endpoint."""
    job_id: str
    status: str
    message: str


class ResultsResponse(BaseModel):
    """Response model for results endpoint."""
    job_id: str
    status: str
    metrics: Optional[Dict[str, float]] = None
    logs: Optional[List[str]] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "service": "Neurosymbolic Object Detection API",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/train", response_model=TrainingResponse)
async def train_model(request: TrainingRequest, background_tasks: BackgroundTasks):
    """
    Trigger the training pipeline.
    
    Args:
        request: Training configuration parameters
        background_tasks: FastAPI background tasks
        
    Returns:
        TrainingResponse with job ID and status
        
    Raises:
        HTTPException: If configuration is invalid
    """
    train_requests.inc()
    
    # Validate config path exists
    config_path = Path(request.config_path)
    if not config_path.exists():
        pipeline_errors.inc()
        raise HTTPException(status_code=404, detail=f"Configuration file not found: {request.config_path}")
    
    # Generate job ID
    job_id = f"train_{int(time.time() * 1000)}"
    
    # Initialize job status
    training_jobs[job_id] = {
        "status": "queued",
        "config_path": request.config_path,
        "epochs": request.epochs,
        "batch_size": request.batch_size,
        "learning_rate": request.learning_rate,
        "created_at": datetime.now().isoformat(),
        "logs": []
    }
    
    # Queue training task in background
    background_tasks.add_task(run_training_pipeline, job_id, request)
    
    logger.info(f"Training job {job_id} queued")
    
    return TrainingResponse(
        job_id=job_id,
        status="queued",
        message=f"Training job {job_id} has been queued"
    )


async def run_training_pipeline(job_id: str, request: TrainingRequest):
    """
    Execute the training pipeline in the background.
    
    Args:
        job_id: Unique job identifier
        request: Training request parameters
    """
    training_jobs[job_id]["status"] = "running"
    training_jobs[job_id]["started_at"] = datetime.now().isoformat()
    
    start_time = time.time()
    
    try:
        # Import here to avoid import errors at startup
        from pipeline.run_pipeline import main as run_pipeline
        
        logger.info(f"Starting training job {job_id}")
        
        # Run the pipeline with timing
        with train_duration.time():
            # This is a placeholder - actual implementation would call the real pipeline
            # For now, we'll simulate the pipeline execution
            training_jobs[job_id]["logs"].append(f"Loading configuration from {request.config_path}")
            training_jobs[job_id]["logs"].append("Starting preprocessing stage...")
            
            # Simulate preprocessing
            with preprocessing_duration.time():
                time.sleep(1)  # Placeholder
                training_jobs[job_id]["logs"].append("Preprocessing completed")
            
            # Simulate training
            training_jobs[job_id]["logs"].append("Starting training stage...")
            time.sleep(2)  # Placeholder
            training_jobs[job_id]["logs"].append("Training completed")
            
            # Simulate evaluation
            training_jobs[job_id]["logs"].append("Starting evaluation stage...")
            with evaluation_duration.time():
                time.sleep(1)  # Placeholder
                training_jobs[job_id]["logs"].append("Evaluation completed")
        
        # Store results
        duration = time.time() - start_time
        results = {
            "mAP": 0.75,  # Placeholder metrics
            "precision": 0.80,
            "recall": 0.72,
            "duration_seconds": duration
        }
        
        training_jobs[job_id]["status"] = "completed"
        training_jobs[job_id]["completed_at"] = datetime.now().isoformat()
        training_jobs[job_id]["results"] = results
        
        results_cache[job_id] = results
        
        logger.info(f"Training job {job_id} completed successfully")
        
    except Exception as e:
        pipeline_errors.inc()
        logger.error(f"Training job {job_id} failed: {str(e)}")
        
        training_jobs[job_id]["status"] = "failed"
        training_jobs[job_id]["error"] = str(e)
        training_jobs[job_id]["completed_at"] = datetime.now().isoformat()


@app.get("/results/{job_id}", response_model=ResultsResponse)
async def get_results(job_id: str):
    """
    Retrieve results for a training job.
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        ResultsResponse with job status and results
        
    Raises:
        HTTPException: If job ID not found
    """
    if job_id not in training_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job = training_jobs[job_id]
    
    return ResultsResponse(
        job_id=job_id,
        status=job["status"],
        metrics=job.get("results"),
        logs=job.get("logs", []),
        error=job.get("error")
    )


@app.get("/results")
async def list_results():
    """
    List all training jobs and their status.
    
    Returns:
        Dictionary of all jobs with their current status
    """
    return {
        "jobs": [
            {
                "job_id": job_id,
                "status": job["status"],
                "created_at": job["created_at"],
                "completed_at": job.get("completed_at")
            }
            for job_id, job in training_jobs.items()
        ],
        "total_jobs": len(training_jobs)
    }


@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.
    
    Returns:
        Prometheus-formatted metrics
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
