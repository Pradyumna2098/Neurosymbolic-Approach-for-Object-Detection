"""Inference service for SAHI-based object detection.

This service provides YOLO model loading, SAHI sliced prediction,
NMS post-processing, and result saving functionality for the
neurosymbolic object detection pipeline.
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
from PIL import Image

from app.core import settings
from pipeline.core.utils import (
    parse_predictions_for_nms,
    pre_filter_with_nms,
    save_predictions_to_file,
)

# Logger
logger = logging.getLogger(__name__)

# Type aliases for better readability
PredictionDict = Dict[str, Any]
JobProgress = Dict[str, Any]


class InferenceError(Exception):
    """Raised when inference operations fail."""
    
    pass


class InferenceService:
    """Service for running SAHI-based YOLO inference on uploaded images.
    
    This service handles:
    - Model loading with GPU/CPU fallback
    - SAHI sliced prediction for high-resolution images
    - Progress tracking during inference
    - Prediction saving in YOLO normalized format
    
    Attributes:
        _model_cache: Dictionary caching loaded models by path
    """
    
    def __init__(self):
        """Initialize the inference service."""
        self._model_cache: Dict[str, Any] = {}
    
    def _detect_device(self) -> str:
        """Detect available device (CUDA GPU or CPU).
        
        Returns:
            Device string ('cuda' or 'cpu')
        """
        if torch.cuda.is_available():
            device = 'cuda'
            logger.info(f"GPU detected: {torch.cuda.get_device_name(0)}")
        else:
            device = 'cpu'
            logger.info("No GPU detected, using CPU")
        
        return device
    
    def load_model(self, model_path: str, force_reload: bool = False) -> Any:
        """Load YOLO model from path with caching.
        
        Args:
            model_path: Path to trained YOLO model weights (.pt file)
            force_reload: If True, bypass cache and reload model
            
        Returns:
            Loaded SAHI AutoDetectionModel instance
            
        Raises:
            InferenceError: If model loading fails
        """
        # Check cache first
        if not force_reload and model_path in self._model_cache:
            logger.info(f"Using cached model from {model_path}")
            return self._model_cache[model_path]
        
        # Validate model path exists
        model_file = Path(model_path)
        if not model_file.exists():
            raise InferenceError(f"Model file not found: {model_path}")
        
        if not model_file.suffix == '.pt':
            raise InferenceError(f"Invalid model file extension. Expected .pt, got {model_file.suffix}")
        
        # Detect device
        device = self._detect_device()
        
        try:
            # Import SAHI here to avoid import errors if not installed
            from sahi import AutoDetectionModel
            
            # Load model with SAHI
            detection_model = AutoDetectionModel.from_pretrained(
                model_type='yolov8',  # YOLOv11 uses yolov8 architecture
                model_path=str(model_path),
                confidence_threshold=0.01,  # Low threshold, will filter later
                device=device,
            )
            
            logger.info(f"Successfully loaded YOLO model from {model_path} on {device}")
            
            # Cache the model
            self._model_cache[model_path] = detection_model
            
            return detection_model
            
        except ImportError as e:
            raise InferenceError(f"SAHI library not installed: {e}") from e
        except Exception as e:
            raise InferenceError(f"Failed to load model: {e}") from e
    
    def apply_nms_post_processing(
        self,
        job_id: str,
        iou_threshold: float,
        storage_service: Any,
    ) -> Dict[str, Any]:
        """Apply class-wise NMS to raw predictions and save filtered results.
        
        Args:
            job_id: Job identifier
            iou_threshold: IoU threshold for NMS filtering
            storage_service: Storage service instance for file operations
            
        Returns:
            Dictionary with NMS statistics (before/after counts, reduction percentage)
            
        Raises:
            InferenceError: If NMS processing fails
        """
        start_time = time.time()
        
        try:
            logger.info(f"[Job {job_id}] Starting NMS post-processing with IoU threshold {iou_threshold}")
            
            # Update job progress
            storage_service.update_job(
                job_id,
                progress={
                    "stage": "nms_filtering",
                    "message": "Applying NMS filtering to detections",
                    "percentage": 92
                }
            )
            
            # Get directories
            raw_dir = settings.results_dir / job_id / "raw"
            nms_dir = settings.results_dir / job_id / "nms"
            nms_dir.mkdir(parents=True, exist_ok=True)
            
            if not raw_dir.exists():
                raise InferenceError(f"Raw predictions directory not found: {raw_dir}")
            
            # Load raw predictions
            logger.info(f"[Job {job_id}] Loading raw predictions from {raw_dir}")
            raw_predictions = parse_predictions_for_nms(raw_dir)
            
            if not raw_predictions:
                logger.warning(f"[Job {job_id}] No raw predictions found")
                elapsed_time_seconds = round(time.time() - start_time, 2)
                return {
                    "total_before": 0,
                    "total_after": 0,
                    "reduction_count": 0,
                    "reduction_percentage": 0.0,
                    "elapsed_time_seconds": elapsed_time_seconds
                }
            
            # Apply NMS per image
            nms_predictions = {}
            total_before = 0
            total_after = 0
            
            for image_name, objects in raw_predictions.items():
                total_before += len(objects)
                
                # Apply class-wise NMS
                filtered = pre_filter_with_nms(objects, iou_threshold)
                total_after += len(filtered)
                
                if filtered:
                    nms_predictions[image_name] = filtered
            
            # Save NMS-filtered predictions
            logger.info(f"[Job {job_id}] Saving NMS-filtered predictions to {nms_dir}")
            save_predictions_to_file(nms_predictions, nms_dir)
            
            # Calculate statistics
            elapsed_time = time.time() - start_time
            reduction_count = total_before - total_after
            reduction_percentage = (reduction_count / total_before * 100) if total_before > 0 else 0.0
            
            nms_stats = {
                "total_before": total_before,
                "total_after": total_after,
                "reduction_count": reduction_count,
                "reduction_percentage": round(reduction_percentage, 2),
                "elapsed_time_seconds": round(elapsed_time, 2)
            }
            
            logger.info(
                f"[Job {job_id}] NMS completed. "
                f"Reduced detections from {total_before} to {total_after} "
                f"({reduction_percentage:.1f}% reduction) in {elapsed_time:.2f}s"
            )
            
            return nms_stats
            
        except Exception as e:
            logger.error(f"[Job {job_id}] NMS post-processing failed: {e}", exc_info=True)
            raise InferenceError(f"NMS post-processing failed: {e}") from e
    
    def run_inference(
        self,
        job_id: str,
        model_path: str,
        confidence_threshold: float,
        iou_threshold: float,
        sahi_config: Dict[str, Any],
        storage_service: Any,
        symbolic_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run SAHI sliced inference on all images in job.
        
        Args:
            job_id: Job identifier
            model_path: Path to trained YOLO model
            confidence_threshold: Minimum confidence threshold for detections
            iou_threshold: IoU threshold for NMS
            sahi_config: SAHI configuration dict with slice_width, slice_height, overlap_ratio
            storage_service: Storage service instance for file operations
            symbolic_config: Optional symbolic reasoning configuration
            
        Returns:
            Dictionary with inference results and statistics
            
        Raises:
            InferenceError: If inference fails
        """
        start_time = time.time()
        
        try:
            # Load model
            logger.info(f"[Job {job_id}] Loading model from {model_path}")
            storage_service.update_job(
                job_id,
                status="processing",
                progress={
                    "stage": "loading_model",
                    "message": "Loading YOLO model",
                    "percentage": 5
                }
            )
            
            detection_model = self.load_model(model_path)
            
            # Get uploaded images
            logger.info(f"[Job {job_id}] Loading uploaded images")
            job_data = storage_service.get_job(job_id)
            if not job_data or not job_data.get('files'):
                raise InferenceError(f"No files found for job {job_id}")
            
            uploaded_files = job_data['files']
            total_images = len(uploaded_files)
            logger.info(f"[Job {job_id}] Processing {total_images} images")
            
            # Get upload directory
            upload_dir = settings.uploads_dir / job_id
            results_dir = settings.results_dir / job_id / "raw"
            results_dir.mkdir(parents=True, exist_ok=True)
            
            # Import SAHI prediction function
            from sahi.predict import get_sliced_prediction
            
            # Process each image
            processed_count = 0
            total_detections = 0
            
            for idx, file_info in enumerate(uploaded_files, start=1):
                stored_filename = file_info['stored_filename']
                original_filename = file_info['filename']
                image_path = upload_dir / stored_filename
                
                if not image_path.exists():
                    logger.warning(f"[Job {job_id}] Image not found: {image_path}")
                    continue
                
                # Update progress
                percentage = int(10 + (idx / total_images) * 80)  # 10-90%
                storage_service.update_job(
                    job_id,
                    progress={
                        "stage": "inference",
                        "message": f"Processing image {idx}/{total_images}: {original_filename}",
                        "percentage": percentage,
                        "images_processed": idx,
                        "total_images": total_images
                    }
                )
                
                logger.info(f"[Job {job_id}] [{idx}/{total_images}] Processing: {original_filename}")
                
                try:
                    # Run SAHI sliced prediction
                    result = get_sliced_prediction(
                        str(image_path),
                        detection_model,
                        slice_height=sahi_config.get('slice_height', 640),
                        slice_width=sahi_config.get('slice_width', 640),
                        overlap_height_ratio=sahi_config.get('overlap_ratio', 0.2),
                        overlap_width_ratio=sahi_config.get('overlap_ratio', 0.2),
                        postprocess_type="GREEDYNMM",
                        postprocess_match_metric="IOU",
                        postprocess_match_threshold=iou_threshold,
                        verbose=0,
                    )
                    
                    # Save predictions in YOLO normalized format
                    detections = self._extract_predictions(
                        result,
                        confidence_threshold
                    )
                    
                    # Save to text file
                    output_filename = Path(original_filename).stem + ".txt"
                    output_path = results_dir / output_filename
                    self._save_predictions_to_txt(detections, output_path)
                    
                    processed_count += 1
                    total_detections += len(detections)
                    
                    logger.info(
                        f"[Job {job_id}] [{idx}/{total_images}] "
                        f"Saved {len(detections)} detections to {output_filename}"
                    )
                    
                except Exception as e:
                    logger.error(
                        f"[Job {job_id}] Error processing {original_filename}: {e}",
                        exc_info=True
                    )
                    # Continue with next image
                    continue
            
            # Calculate final statistics
            elapsed_time = time.time() - start_time
            avg_time_per_image = elapsed_time / processed_count if processed_count > 0 else 0
            
            inference_stats = {
                "total_images": total_images,
                "processed_images": processed_count,
                "failed_images": total_images - processed_count,
                "total_detections": total_detections,
                "avg_detections_per_image": total_detections / processed_count if processed_count > 0 else 0,
                "elapsed_time_seconds": round(elapsed_time, 2),
                "avg_time_per_image_seconds": round(avg_time_per_image, 2),
            }
            
            logger.info(
                f"[Job {job_id}] Inference complete. "
                f"Processed {processed_count}/{total_images} images, "
                f"found {total_detections} detections in {elapsed_time:.2f}s"
            )
            
            # Apply NMS post-processing
            logger.info(f"[Job {job_id}] Applying NMS post-processing")
            try:
                nms_stats = self.apply_nms_post_processing(
                    job_id,
                    iou_threshold,
                    storage_service
                )
                inference_stats["nms"] = nms_stats
                logger.info(
                    f"[Job {job_id}] NMS reduced detections from "
                    f"{nms_stats['total_before']} to {nms_stats['total_after']}"
                )
            except Exception as e:
                logger.error(f"[Job {job_id}] NMS post-processing failed: {e}", exc_info=True)
                # Don't fail the entire job if NMS fails
                inference_stats["nms"] = {
                    "error": str(e),
                    "total_before": 0,
                    "total_after": 0
                }
            
            # Apply symbolic reasoning if enabled
            if symbolic_config and symbolic_config.get('enabled', False):
                logger.info(f"[Job {job_id}] Applying symbolic reasoning")
                try:
                    from app.services.symbolic import symbolic_reasoning_service
                    
                    # Get rules file from config or use default
                    rules_file = symbolic_config.get('rules_file')
                    if rules_file:
                        rules_file = Path(rules_file)
                    
                    symbolic_stats = symbolic_reasoning_service.apply_symbolic_reasoning(
                        job_id=job_id,
                        rules_file=rules_file,
                        storage_service=storage_service
                    )
                    inference_stats["symbolic_reasoning"] = symbolic_stats
                    
                    if symbolic_stats.get('skipped'):
                        logger.warning(
                            f"[Job {job_id}] Symbolic reasoning skipped: "
                            f"{symbolic_stats.get('reason', 'Unknown reason')}"
                        )
                    else:
                        logger.info(
                            f"[Job {job_id}] Symbolic reasoning completed. "
                            f"Applied {symbolic_stats.get('total_adjustments', 0)} adjustments"
                        )
                except Exception as e:
                    logger.error(f"[Job {job_id}] Symbolic reasoning failed: {e}", exc_info=True)
                    # Don't fail the entire job if symbolic reasoning fails
                    inference_stats["symbolic_reasoning"] = {
                        "error": str(e),
                        "skipped": True,
                        "reason": "Error during processing"
                    }
            else:
                logger.info(f"[Job {job_id}] Symbolic reasoning disabled")
                inference_stats["symbolic_reasoning"] = {
                    "skipped": True,
                    "reason": "Disabled in configuration"
                }
            
            # Update job with completion
            storage_service.update_job(
                job_id,
                status="completed",
                progress={
                    "stage": "completed",
                    "message": "Inference completed successfully",
                    "percentage": 100,
                    "images_processed": processed_count,
                    "total_images": total_images,
                },
                inference_stats=inference_stats
            )
            
            return inference_stats
            
        except Exception as e:
            logger.error(f"[Job {job_id}] Inference failed: {e}", exc_info=True)
            raise InferenceError(f"Inference failed: {e}") from e
    
    def _extract_predictions(
        self,
        sahi_result: Any,
        confidence_threshold: float
    ) -> List[PredictionDict]:
        """Extract predictions from SAHI result and convert to YOLO format.
        
        Args:
            sahi_result: SAHI prediction result object
            confidence_threshold: Minimum confidence to include
            
        Returns:
            List of prediction dictionaries with normalized coordinates
        """
        predictions = []
        
        img_h = sahi_result.image_height
        img_w = sahi_result.image_width
        
        for pred in sahi_result.object_prediction_list:
            # Filter by confidence
            if pred.score.value < confidence_threshold:
                continue
            
            # Get bounding box in VOC format (x1, y1, x2, y2)
            x1, y1, x2, y2 = pred.bbox.to_voc_bbox()
            
            # Convert to YOLO normalized format (cx, cy, w, h)
            dw = 1.0 / img_w
            dh = 1.0 / img_h
            
            x_center = (x1 + x2) / 2.0
            y_center = (y1 + y2) / 2.0
            width = x2 - x1
            height = y2 - y1
            
            x_center_norm = x_center * dw
            y_center_norm = y_center * dh
            width_norm = width * dw
            height_norm = height * dh
            
            predictions.append({
                'class_id': pred.category.id,
                'x_center': x_center_norm,
                'y_center': y_center_norm,
                'width': width_norm,
                'height': height_norm,
                'confidence': pred.score.value
            })
        
        return predictions
    
    def _save_predictions_to_txt(
        self,
        predictions: List[PredictionDict],
        output_path: Path
    ) -> None:
        """Save predictions to YOLO format text file.
        
        Format: class_id x_center y_center width height confidence
        All coordinates are normalized to [0, 1].
        
        Args:
            predictions: List of prediction dictionaries
            output_path: Path to output text file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            for pred in predictions:
                line = (
                    f"{pred['class_id']} "
                    f"{pred['x_center']:.6f} "
                    f"{pred['y_center']:.6f} "
                    f"{pred['width']:.6f} "
                    f"{pred['height']:.6f} "
                    f"{pred['confidence']:.6f}\n"
                )
                f.write(line)
        
        logger.debug(f"Saved {len(predictions)} predictions to {output_path}")


# Global inference service instance
inference_service = InferenceService()
