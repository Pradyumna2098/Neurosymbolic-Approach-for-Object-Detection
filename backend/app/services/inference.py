"""Inference service for SAHI + YOLO object detection.

This service provides model loading, SAHI sliced inference, and prediction
storage functionality for the neurosymbolic object detection pipeline.
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction

from app.services import storage_service

logger = logging.getLogger(__name__)


class ModelCache:
    """Cache for loaded YOLO models to avoid repeated loading."""
    
    def __init__(self):
        self._cache: Dict[str, AutoDetectionModel] = {}
    
    def get_or_load(
        self, 
        model_path: str, 
        confidence_threshold: float,
        device: Optional[str] = None
    ) -> AutoDetectionModel:
        """Get cached model or load if not in cache.
        
        Args:
            model_path: Path to YOLO model weights
            confidence_threshold: Minimum confidence threshold
            device: Device to load model on (cuda/cpu)
            
        Returns:
            Loaded AutoDetectionModel instance
        """
        cache_key = f"{model_path}_{confidence_threshold}_{device}"
        
        if cache_key in self._cache:
            logger.info(f"Using cached model for {model_path}")
            return self._cache[cache_key]
        
        logger.info(f"Loading model from {model_path}")
        
        # Determine device
        if device is None:
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Using device: {device}")
        
        try:
            model = AutoDetectionModel.from_pretrained(
                model_type="yolov8",
                model_path=str(model_path),
                confidence_threshold=float(confidence_threshold),
                device=device,
            )
            
            self._cache[cache_key] = model
            logger.info(f"Model loaded successfully from {model_path}")
            
            return model
            
        except Exception as e:
            logger.error(f"Failed to load model from {model_path}: {e}")
            raise RuntimeError(f"Unable to load YOLO model: {e}") from e
    
    def clear(self):
        """Clear the model cache."""
        self._cache.clear()
        logger.info("Model cache cleared")


# Global model cache instance
_model_cache = ModelCache()


class InferenceService:
    """Service for running SAHI + YOLO inference on images."""
    
    def __init__(self, model_cache: Optional[ModelCache] = None):
        """Initialize inference service.
        
        Args:
            model_cache: Optional model cache instance (uses global cache if None)
        """
        self.model_cache = model_cache or _model_cache
    
    def run_inference(
        self,
        job_id: str,
        model_path: str,
        confidence_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        sahi_config: Optional[Dict[str, Any]] = None,
        device: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run SAHI inference on all images in a job.
        
        Args:
            job_id: Job identifier
            model_path: Path to trained YOLO model weights
            confidence_threshold: Minimum confidence threshold
            iou_threshold: IoU threshold for NMS
            sahi_config: SAHI configuration (slice dimensions, overlap)
            device: Device to use (cuda/cpu), auto-detected if None
            
        Returns:
            Dictionary with inference results and statistics
            
        Raises:
            FileNotFoundError: If model or images not found
            RuntimeError: If inference fails
        """
        start_time = time.time()
        
        # Update job status to processing
        storage_service.update_job(
            job_id,
            status="processing",
            progress={
                "stage": "initializing",
                "message": "Validating configuration",
                "percentage": 0
            }
        )
        
        try:
            # Validate model path
            model_path_obj = Path(model_path)
            if not model_path_obj.exists():
                raise FileNotFoundError(f"Model not found: {model_path}")
            
            # Get SAHI configuration with defaults
            sahi_config = sahi_config or {}
            sahi_enabled = sahi_config.get("enabled", True)
            slice_height = sahi_config.get("slice_height", 640)
            slice_width = sahi_config.get("slice_width", 640)
            overlap_ratio = sahi_config.get("overlap_ratio", 0.2)
            # Load model (with caching)
            model = self.model_cache.get_or_load(
                model_path, 
                confidence_threshold,
                device
            )
            
            # Get job files
            job_data = storage_service.get_job(job_id)
            if not job_data:
                raise ValueError(f"Job not found: {job_id}")
            
            files = job_data.get("files", [])
            if not files:
                raise ValueError(f"No files found in job: {job_id}")
            
            total_images = len(files)
            logger.info(f"Processing {total_images} images for job {job_id}")
            
            # Update progress
            storage_service.update_job(
                job_id,
                progress={
                    "stage": "inference",
                    "message": f"Running inference on {total_images} images",
                    "percentage": 5,
                    "total_images": total_images,
                    "processed_images": 0
                }
            )
            
            # Process each image
            all_predictions = {}
            processed_count = 0
            
            for idx, file_info in enumerate(files, 1):
                file_id = file_info["file_id"]
                original_filename = file_info["filename"]
                
                # Get image path
                image_path = storage_service.get_upload_path(job_id, file_id)
                if not image_path or not image_path.exists():
                    logger.warning(f"Image not found: {file_id}, skipping")
                    continue
                
                logger.info(f"Processing image {idx}/{total_images}: {original_filename}")
                
                # Run SAHI prediction
                try:
                    predictions = self._predict_image(
                        image_path=image_path,
                        model=model,
                        sahi_enabled=sahi_enabled,
                        slice_height=slice_height,
                        slice_width=slice_width,
                        overlap_ratio=overlap_ratio,
                        iou_threshold=iou_threshold
                    )
                    
                    # Store predictions keyed by original filename
                    all_predictions[original_filename] = predictions
                    processed_count += 1
                    
                    # Update progress
                    percentage = 5 + int((idx / total_images) * 85)
                    storage_service.update_job(
                        job_id,
                        progress={
                            "stage": "inference",
                            "message": f"Processed {idx}/{total_images} images",
                            "percentage": percentage,
                            "total_images": total_images,
                            "processed_images": idx
                        }
                    )
                    
                except Exception as e:
                    logger.error(f"Error processing image {original_filename}: {e}")
                    # Continue processing other images
                    continue
            
            # Save predictions to raw stage
            logger.info(f"Saving predictions for {processed_count} images")
            self._save_predictions(job_id, all_predictions)
            
            # Calculate statistics
            total_detections = sum(len(preds) for preds in all_predictions.values())
            elapsed_time = time.time() - start_time
            
            # Update job to completed
            storage_service.update_job(
                job_id,
                status="completed",
                progress={
                    "stage": "completed",
                    "message": f"Inference completed successfully",
                    "percentage": 100,
                    "total_images": total_images,
                    "processed_images": processed_count,
                    "total_detections": total_detections,
                    "elapsed_time": elapsed_time
                }
            )
            
            logger.info(
                f"Inference completed for job {job_id}: "
                f"{processed_count} images, {total_detections} detections, "
                f"{elapsed_time:.2f}s"
            )
            
            return {
                "job_id": job_id,
                "processed_images": processed_count,
                "total_detections": total_detections,
                "elapsed_time": elapsed_time
            }
            
        except Exception as e:
            # Update job to failed
            error_message = f"Inference failed: {str(e)}"
            logger.error(f"Inference error for job {job_id}: {error_message}", exc_info=True)
            
            storage_service.update_job(
                job_id,
                status="failed",
                error=error_message,
                progress={
                    "stage": "failed",
                    "message": error_message,
                    "percentage": 0
                }
            )
            
            raise
    
    def _predict_image(
        self,
        image_path: Path,
        model: AutoDetectionModel,
        sahi_enabled: bool = True,
        slice_height: int = 640,
        slice_width: int = 640,
        overlap_ratio: float = 0.2,
        iou_threshold: float = 0.45
    ) -> List[Dict[str, Any]]:
        """Run prediction on a single image using SAHI.
        
        Args:
            image_path: Path to image file
            model: Loaded YOLO model
            sahi_enabled: Whether to use SAHI slicing
            slice_height: Height of each slice
            slice_width: Width of each slice
            overlap_ratio: Overlap ratio between slices
            iou_threshold: IoU threshold for NMS
            
        Returns:
            List of prediction dictionaries in YOLO OBB format
        """
        if not sahi_enabled:
            # Direct prediction without slicing
            # Note: SAHI AutoDetectionModel doesn't have a direct predict method
            # We still use get_sliced_prediction but with large slice dimensions
            logger.debug(f"Running direct prediction (no slicing) on {image_path.name}")
            slice_height = 10000  # Large enough to cover most images
            slice_width = 10000
        
        try:
            result = get_sliced_prediction(
                str(image_path),
                model,
                slice_height=slice_height,
                slice_width=slice_width,
                overlap_height_ratio=overlap_ratio,
                overlap_width_ratio=overlap_ratio,
                postprocess_type="GREEDYNMM",
                postprocess_match_metric="IOU",
                postprocess_match_threshold=iou_threshold,
                verbose=0,
            )
        except Exception as e:
            logger.error(f"SAHI prediction failed for {image_path.name}: {e}")
            raise RuntimeError(f"Prediction failed: {e}") from e
        
        # Convert SAHI results to YOLO normalized format
        predictions = []
        img_height = result.image_height
        img_width = result.image_width
        
        for pred in result.object_prediction_list:
            # Get bounding box in VOC format (x1, y1, x2, y2)
            x1, y1, x2, y2 = pred.bbox.to_voc_bbox()
            
            # Convert to YOLO normalized format
            dw = 1.0 / img_width
            dh = 1.0 / img_height
            x_center = (x1 + x2) / 2.0
            y_center = (y1 + y2) / 2.0
            width = x2 - x1
            height = y2 - y1
            
            x_center_norm = x_center * dw
            y_center_norm = y_center * dh
            width_norm = width * dw
            height_norm = height * dh
            
            predictions.append({
                "class_id": pred.category.id,
                "class_name": pred.category.name,
                "confidence": pred.score.value,
                "bbox_normalized": [
                    x_center_norm,
                    y_center_norm,
                    width_norm,
                    height_norm
                ],
                "bbox_voc": [x1, y1, x2, y2]
            })
        
        return predictions
    
    def _save_predictions(
        self,
        job_id: str,
        predictions: Dict[str, List[Dict[str, Any]]]
    ) -> None:
        """Save predictions to job results directory in YOLO format.
        
        Args:
            job_id: Job identifier
            predictions: Dictionary mapping filenames to prediction lists
        """
        # Get raw results directory
        results_dir = storage_service._get_job_results_dir(job_id, stage="raw")
        
        # Save each image's predictions as a separate .txt file
        for filename, preds in predictions.items():
            # Generate output filename (replace extension with .txt)
            output_filename = Path(filename).stem + ".txt"
            output_path = results_dir / output_filename
            
            # Write predictions in YOLO format
            with open(output_path, "w") as f:
                for pred in preds:
                    # Format: class_id cx cy w h confidence
                    bbox = pred["bbox_normalized"]
                    line = (
                        f"{pred['class_id']} "
                        f"{bbox[0]:.6f} {bbox[1]:.6f} "
                        f"{bbox[2]:.6f} {bbox[3]:.6f} "
                        f"{pred['confidence']:.6f}\n"
                    )
                    f.write(line)
        
        logger.info(f"Saved predictions for {len(predictions)} images to {results_dir}")
        
        # Also save as JSON for easier access by other stages
        storage_service.save_result(job_id, predictions, stage="raw")


# Global inference service instance
inference_service = InferenceService()
