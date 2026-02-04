#!/usr/bin/env python3
"""Demonstration of the StorageService functionality.

This script demonstrates the key features of the file storage service:
- Creating jobs
- Validating and saving image files
- Storing predictions at different stages
- Managing job status
"""

import sys
from io import BytesIO
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from PIL import Image

from app.services.storage import StorageService, FileValidationError


def create_sample_image(width: int, height: int, color: str = "blue") -> bytes:
    """Create a sample image for testing.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        color: Image color
        
    Returns:
        Image data as bytes
    """
    img = Image.new('RGB', (width, height), color=color)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def main():
    """Demonstrate StorageService functionality."""
    print("=" * 70)
    print("StorageService Demonstration")
    print("=" * 70)
    
    # Initialize service
    service = StorageService()
    print("\n✓ Initialized StorageService")
    
    # Create a new job
    print("\n--- Creating New Job ---")
    job_id = service.create_job(config={
        "model": "yolov11m-obb",
        "confidence_threshold": 0.25,
        "iou_threshold": 0.45
    })
    print(f"✓ Created job with ID: {job_id}")
    
    # Upload a valid image
    print("\n--- Uploading Valid Image ---")
    image_data = create_sample_image(800, 600, "green")
    print(f"  Created test image: 800x600 pixels, {len(image_data)} bytes")
    
    try:
        file_id, file_path, metadata = service.save_upload(
            job_id, "test_image.png", image_data, validate=True
        )
        print(f"✓ Image validated and saved")
        print(f"  File ID: {file_id}")
        print(f"  Path: {file_path}")
        print(f"  Metadata: {metadata}")
    except FileValidationError as e:
        print(f"✗ Validation failed: {e}")
        return
    
    # Try to upload an invalid image (too small)
    print("\n--- Attempting to Upload Invalid Image ---")
    invalid_data = b"not enough data"
    try:
        service.save_upload(job_id, "invalid.png", invalid_data, validate=True)
        print("✗ Should have rejected invalid image!")
    except FileValidationError as e:
        print(f"✓ Correctly rejected invalid image")
        print(f"  Reason: {str(e)[:80]}...")
    
    # Update job status
    print("\n--- Updating Job Status ---")
    service.update_job(job_id, status="processing", progress={"stage": "inference", "percent": 0})
    print("✓ Updated job status to 'processing'")
    
    # Save raw predictions
    print("\n--- Saving Predictions (Raw Stage) ---")
    predictions_raw = {
        "detections": [
            {"class_id": 0, "class_name": "plane", "confidence": 0.95, "bbox": [100, 100, 200, 150]},
            {"class_id": 1, "class_name": "ship", "confidence": 0.87, "bbox": [300, 250, 400, 350]}
        ],
        "num_detections": 2
    }
    service.save_result(job_id, predictions_raw, stage="raw")
    print("✓ Saved raw predictions")
    
    # Save NMS-filtered predictions
    print("\n--- Saving Predictions (NMS Stage) ---")
    predictions_nms = {
        "detections": [
            {"class_id": 0, "class_name": "plane", "confidence": 0.95, "bbox": [100, 100, 200, 150]}
        ],
        "num_detections": 1,
        "note": "One overlapping detection removed by NMS"
    }
    service.save_result(job_id, predictions_nms, stage="nms")
    print("✓ Saved NMS-filtered predictions")
    
    # Save refined predictions
    print("\n--- Saving Predictions (Refined Stage) ---")
    predictions_refined = {
        "detections": [
            {"class_id": 0, "class_name": "plane", "confidence": 0.98, "bbox": [100, 100, 200, 150],
             "note": "Confidence boosted by symbolic reasoning"}
        ],
        "num_detections": 1
    }
    service.save_result(job_id, predictions_refined, stage="refined")
    print("✓ Saved refined predictions")
    
    # Save visualization
    print("\n--- Saving Visualization ---")
    viz_image = create_sample_image(800, 600, "red")
    service.save_visualization(job_id, viz_image, filename="annotated.png")
    print("✓ Saved visualization image")
    
    # Complete the job
    print("\n--- Completing Job ---")
    service.update_job(job_id, status="completed", progress={"stage": "done", "percent": 100})
    print("✓ Job marked as completed")
    
    # Retrieve and display job info
    print("\n--- Final Job Status ---")
    job = service.get_job(job_id)
    print(f"  Job ID: {job['job_id']}")
    print(f"  Status: {job['status']}")
    print(f"  Created: {job['created_at']}")
    print(f"  Updated: {job.get('updated_at', 'N/A')}")
    print(f"  Files uploaded: {len(job['files'])}")
    print(f"  Progress: {job['progress']}")
    
    # List all files
    print("\n--- Files in Job ---")
    files = service.list_job_files(job_id)
    for i, file_info in enumerate(files, 1):
        print(f"  {i}. {file_info['filename']}")
        print(f"     File ID: {file_info['file_id']}")
        print(f"     Size: {file_info['size_bytes']} bytes")
        if file_info.get('metadata'):
            print(f"     Dimensions: {file_info['metadata']['width']}x{file_info['metadata']['height']}")
    
    # Retrieve results
    print("\n--- Retrieving Results ---")
    result_refined = service.get_result(job_id, stage="refined")
    print(f"  Refined predictions: {result_refined['num_detections']} detections")
    
    print("\n" + "=" * 70)
    print("Demonstration Complete!")
    print("=" * 70)
    print(f"\nJob data stored in: data/jobs/{job_id}.json")
    print(f"Uploaded files in: data/uploads/{job_id}/")
    print(f"Results in: data/results/{job_id}/")
    print(f"Visualizations in: data/visualizations/{job_id}/")


if __name__ == "__main__":
    main()
