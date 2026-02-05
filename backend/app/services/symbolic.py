"""Symbolic reasoning service using Prolog for confidence adjustment.

This service provides Prolog-based symbolic reasoning to refine
object detection predictions using domain knowledge rules.
"""

import csv
import logging
import math
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.core import settings

# Logger
logger = logging.getLogger(__name__)

# Type aliases
PredictionDict = Dict[str, Any]

# Default class mapping for DOTA dataset
DEFAULT_CLASS_MAP = {
    0: "plane",
    1: "ship",
    2: "storage_tank",
    3: "baseball_diamond",
    4: "tennis_court",
    5: "basketball_court",
    6: "Ground_Track_Field",
    7: "harbor",
    8: "Bridge",
    9: "large_vehicle",
    10: "small_vehicle",
    11: "helicopter",
    12: "roundabout",
    13: "soccer_ball_field",
    14: "swimming_pool",
}


class SymbolicReasoningError(Exception):
    """Raised when symbolic reasoning operations fail."""
    
    pass


class SymbolicReasoningService:
    """Service for applying Prolog-based symbolic reasoning to detections.
    
    This service handles:
    - Loading Prolog rules from configured file
    - Converting detections to Prolog-compatible format
    - Applying confidence modifiers based on spatial relationships
    - Saving refined predictions
    - Generating explainability reports
    
    Attributes:
        _prolog_cache: Cached Prolog engine instance
    """
    
    def __init__(self):
        """Initialize the symbolic reasoning service."""
        self._prolog_cache: Optional[Any] = None
    
    def _load_prolog_engine(self, rules_file: Path) -> Any:
        """Load Prolog engine and consult rules file.
        
        Args:
            rules_file: Path to Prolog rules file
            
        Returns:
            Initialized Prolog engine
            
        Raises:
            SymbolicReasoningError: If Prolog engine or rules cannot be loaded
        """
        try:
            from pyswip import Prolog
            
            if not rules_file.exists():
                raise SymbolicReasoningError(f"Prolog rules file not found: {rules_file}")
            
            prolog = Prolog()
            prolog.consult(str(rules_file))
            
            logger.info(f"Successfully loaded Prolog rules from {rules_file}")
            return prolog
            
        except ImportError as e:
            raise SymbolicReasoningError(f"PySwip library not installed: {e}") from e
        except Exception as e:
            raise SymbolicReasoningError(f"Failed to load Prolog rules: {e}") from e
    
    def _load_modifier_map(self, prolog_engine: Any) -> Dict[Tuple[str, str], float]:
        """Extract confidence modifier rules from Prolog engine.
        
        Args:
            prolog_engine: Initialized Prolog engine with rules loaded
            
        Returns:
            Dictionary mapping (class_a, class_b) pairs to modifier weights
        """
        modifier_map: Dict[Tuple[str, str], float] = {}
        
        try:
            # Query all confidence_modifier facts
            for solution in prolog_engine.query("confidence_modifier(A, B, Weight)"):
                class_a = str(solution["A"])  # Ensure string type
                class_b = str(solution["B"])  # Ensure string type
                weight = float(solution["Weight"])  # Ensure float type
                modifier_map[(class_a, class_b)] = weight
            
            logger.info(f"Loaded {len(modifier_map)} confidence modifier rules from Prolog")
            return modifier_map
            
        except Exception as e:
            logger.warning(f"Failed to load modifier rules from Prolog: {e}")
            return {}
    
    def _parse_predictions(self, predictions_dir: Path) -> Dict[str, List[PredictionDict]]:
        """Load YOLO-format predictions from directory.
        
        Args:
            predictions_dir: Directory containing .txt prediction files
            
        Returns:
            Dictionary mapping image names to lists of predictions
        """
        predictions: Dict[str, List[PredictionDict]] = {}
        
        if not predictions_dir.exists():
            logger.warning(f"Predictions directory not found: {predictions_dir}")
            return predictions
        
        for pred_file in predictions_dir.iterdir():
            if pred_file.suffix.lower() != ".txt":
                continue
            
            image_name = pred_file.stem
            image_predictions = []
            
            with pred_file.open("r", encoding="utf-8") as f:
                for idx, line in enumerate(f):
                    parts = line.strip().split()
                    if len(parts) != 6:
                        continue
                    
                    category_id, cx, cy, width, height, confidence = map(float, parts)
                    
                    # Convert to VOC format for spatial calculations
                    x_min = cx - width / 2
                    y_min = cy - height / 2
                    x_max = cx + width / 2
                    y_max = cy + height / 2
                    
                    image_predictions.append({
                        "id": f"det_{idx}",
                        "category_id": int(category_id),
                        "bbox": [x_min, y_min, x_max, y_max],
                        "bbox_yolo": [cx, cy, width, height],
                        "confidence": confidence,
                    })
            
            if image_predictions:
                predictions[image_name] = image_predictions
        
        return predictions
    
    def _get_bbox_center(self, bbox: List[float]) -> Tuple[float, float]:
        """Get center coordinates of a bounding box.
        
        Args:
            bbox: Bounding box in VOC format [x_min, y_min, x_max, y_max]
            
        Returns:
            Tuple of (center_x, center_y)
        """
        x_min, y_min, x_max, y_max = bbox
        return (x_min + x_max) / 2, (y_min + y_max) / 2
    
    def _get_distance(self, bbox_a: List[float], bbox_b: List[float]) -> float:
        """Calculate Euclidean distance between centers of two boxes.
        
        Args:
            bbox_a: First bounding box in VOC format
            bbox_b: Second bounding box in VOC format
            
        Returns:
            Distance between box centers
        """
        center_a = self._get_bbox_center(bbox_a)
        center_b = self._get_bbox_center(bbox_b)
        
        return math.hypot(center_a[0] - center_b[0], center_a[1] - center_b[1])
    
    def _get_bbox_diagonal(self, bbox: List[float]) -> float:
        """Calculate diagonal length of a bounding box.
        
        Args:
            bbox: Bounding box in VOC format
            
        Returns:
            Diagonal length
        """
        x_min, y_min, x_max, y_max = bbox
        return math.hypot(x_max - x_min, y_max - y_min)
    
    def _get_bbox_area(self, bbox: List[float]) -> float:
        """Calculate area of a bounding box.
        
        Args:
            bbox: Bounding box in VOC format
            
        Returns:
            Box area
        """
        x_min, y_min, x_max, y_max = bbox
        return max(0.0, x_max - x_min) * max(0.0, y_max - y_min)
    
    def _get_intersection_area(self, bbox_a: List[float], bbox_b: List[float]) -> float:
        """Calculate intersection area between two bounding boxes.
        
        Args:
            bbox_a: First bounding box
            bbox_b: Second bounding box
            
        Returns:
            Intersection area
        """
        x1a, y1a, x2a, y2a = bbox_a
        x1b, y1b, x2b, y2b = bbox_b
        
        ix1, iy1 = max(x1a, x1b), max(y1a, y1b)
        ix2, iy2 = min(x2a, x2b), min(y2a, y2b)
        
        return max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    
    def _apply_modifiers(
        self,
        objects: List[PredictionDict],
        modifier_map: Dict[Tuple[str, str], float],
        class_map: Dict[int, str]
    ) -> Tuple[List[PredictionDict], List[Dict[str, Any]]]:
        """Apply symbolic modifiers to object confidences.
        
        This method implements the core symbolic reasoning logic:
        - Boost confidence for objects with positive co-occurrence patterns
        - Penalize confidence for implausible object combinations
        
        Args:
            objects: List of detection dictionaries
            modifier_map: Mapping of class pairs to modifier weights
            class_map: Mapping of category IDs to class names
            
        Returns:
            Tuple of (modified_objects, explainability_log)
        """
        # Create mutable copies of objects
        modified_objects = {obj["id"]: dict(obj) for obj in objects}
        change_log: List[Dict[str, Any]] = []
        
        obj_ids = list(modified_objects.keys())
        
        # Compare each pair of objects
        for i in range(len(obj_ids)):
            for j in range(i + 1, len(obj_ids)):
                id_a, id_b = obj_ids[i], obj_ids[j]
                
                if id_a not in modified_objects or id_b not in modified_objects:
                    continue
                
                obj_a = modified_objects[id_a]
                obj_b = modified_objects[id_b]
                
                # Get class names
                class_a = class_map.get(obj_a["category_id"], f"class_{obj_a['category_id']}")
                class_b = class_map.get(obj_b["category_id"], f"class_{obj_b['category_id']}")
                
                # Check for modifier rule
                weight = modifier_map.get((class_a, class_b)) or modifier_map.get((class_b, class_a))
                
                if weight is None:
                    continue
                
                # Store original confidences
                original_conf_a = obj_a["confidence"]
                original_conf_b = obj_b["confidence"]
                
                log_entry = None
                
                # Apply boost for positive correlations (weight > 1.0)
                if weight > 1.0:
                    # Check proximity - objects must be close to each other
                    avg_diag = (self._get_bbox_diagonal(obj_a["bbox"]) + 
                               self._get_bbox_diagonal(obj_b["bbox"])) / 2
                    distance = self._get_distance(obj_a["bbox"], obj_b["bbox"])
                    
                    if distance < 2 * avg_diag:
                        # Boost confidences
                        obj_a["confidence"] = min(1.0, original_conf_a * weight)
                        obj_b["confidence"] = min(1.0, original_conf_b * weight)
                        
                        log_entry = {
                            "action": "BOOST",
                            "rule_pair": f"{class_a}<->{class_b}",
                            "object_1": class_a,
                            "conf_1_before": f"{original_conf_a:.2f}",
                            "conf_1_after": f"{obj_a['confidence']:.2f}",
                            "object_2": class_b,
                            "conf_2_before": f"{original_conf_b:.2f}",
                            "conf_2_after": f"{obj_b['confidence']:.2f}",
                        }
                
                # Apply penalty for implausible combinations (weight < 1.0)
                elif weight < 1.0:
                    # Check overlap - objects must significantly overlap
                    intersection = self._get_intersection_area(obj_a["bbox"], obj_b["bbox"])
                    min_area = min(self._get_bbox_area(obj_a["bbox"]), 
                                  self._get_bbox_area(obj_b["bbox"]))
                    
                    if min_area > 0 and intersection / min_area > 0.5:
                        # Penalize the lower confidence object
                        if obj_a["confidence"] > obj_b["confidence"]:
                            suppressed_obj, kept_obj = obj_b, obj_a
                        else:
                            suppressed_obj, kept_obj = obj_a, obj_b
                        
                        original_suppressed_conf = suppressed_obj["confidence"]
                        suppressed_obj["confidence"] *= weight
                        
                        log_entry = {
                            "action": "PENALTY",
                            "rule_pair": f"{class_a}<->{class_b}",
                            "object_1": class_a,
                            "conf_1_before": f"{original_conf_a:.2f}",
                            "conf_1_after": f"{obj_a['confidence']:.2f}",
                            "object_2": class_b,
                            "conf_2_before": f"{original_conf_b:.2f}",
                            "conf_2_after": f"{obj_b['confidence']:.2f}",
                            "suppressed_object": class_map.get(
                                suppressed_obj["category_id"],
                                f"class_{suppressed_obj['category_id']}",
                            ),
                            "conf_before": f"{original_suppressed_conf:.2f}",
                            "conf_after": f"{suppressed_obj['confidence']:.2f}",
                            "kept_object": class_map.get(
                                kept_obj["category_id"],
                                f"class_{kept_obj['category_id']}",
                            ),
                            "kept_object_conf": f"{kept_obj['confidence']:.2f}",
                        }
                
                if log_entry:
                    change_log.append(log_entry)
        
        return list(modified_objects.values()), change_log
    
    def _save_predictions(
        self,
        predictions: Dict[str, List[PredictionDict]],
        output_dir: Path
    ) -> None:
        """Save predictions to YOLO format text files.
        
        Args:
            predictions: Dictionary mapping image names to prediction lists
            output_dir: Directory to save prediction files
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for image_name, objects in predictions.items():
            output_file = output_dir / f"{image_name}.txt"
            
            with output_file.open("w", encoding="utf-8") as f:
                for obj in objects:
                    cx, cy, width, height = obj["bbox_yolo"]
                    line = (
                        f"{obj['category_id']} "
                        f"{cx:.6f} "
                        f"{cy:.6f} "
                        f"{width:.6f} "
                        f"{height:.6f} "
                        f"{obj['confidence']:.6f}\n"
                    )
                    f.write(line)
        
        logger.debug(f"Saved {len(predictions)} prediction files to {output_dir}")
    
    def _save_explainability_report(
        self,
        report: List[Dict[str, Any]],
        report_file: Path
    ) -> None:
        """Save explainability report to CSV file.
        
        Args:
            report: List of explainability log entries
            report_file: Path to output CSV file
        """
        if not report:
            logger.info("No symbolic reasoning actions logged, skipping report")
            return
        
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        fieldnames = [
            "image_name",
            "action",
            "rule_pair",
            "object_1",
            "conf_1_before",
            "conf_1_after",
            "object_2",
            "conf_2_before",
            "conf_2_after",
            "suppressed_object",
            "kept_object",
            "kept_object_conf",
        ]
        
        with report_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(report)
        
        logger.info(f"Saved explainability report with {len(report)} entries to {report_file}")
    
    def apply_symbolic_reasoning(
        self,
        job_id: str,
        rules_file: Optional[Path] = None,
        class_map: Optional[Dict[int, str]] = None,
        storage_service: Any = None,
    ) -> Dict[str, Any]:
        """Apply Prolog-based symbolic reasoning to NMS-filtered predictions.
        
        This is the main entry point for the symbolic reasoning stage:
        1. Load NMS-filtered predictions from data/results/{job_id}/nms/
        2. Load Prolog rules and extract modifiers
        3. Apply confidence adjustments based on spatial relationships
        4. Save refined predictions to data/results/{job_id}/refined/
        5. Generate explainability report
        
        Args:
            job_id: Job identifier
            rules_file: Optional path to Prolog rules file (default: pipeline/prolog/rules.pl)
            class_map: Optional class mapping (default: DOTA dataset classes)
            storage_service: Optional storage service for job updates
            
        Returns:
            Dictionary with symbolic reasoning statistics
            
        Raises:
            SymbolicReasoningError: If symbolic reasoning fails
        """
        start_time = time.time()
        
        try:
            logger.info(f"[Job {job_id}] Starting symbolic reasoning stage")
            
            # Update job progress
            if storage_service:
                storage_service.update_job(
                    job_id,
                    progress={
                        "stage": "symbolic_reasoning",
                        "message": "Applying Prolog-based confidence adjustment",
                        "percentage": 94
                    }
                )
            
            # Use default rules file if not provided
            if rules_file is None:
                rules_file = Path("pipeline/prolog/rules.pl")
            
            # Use default class map if not provided
            if class_map is None:
                class_map = DEFAULT_CLASS_MAP
            
            # Validate rules file exists
            if not rules_file.exists():
                logger.warning(
                    f"[Job {job_id}] Prolog rules file not found: {rules_file}. "
                    "Skipping symbolic reasoning."
                )
                return {
                    "skipped": True,
                    "reason": "Rules file not found",
                    "elapsed_time_seconds": 0
                }
            
            # Load Prolog engine and rules
            logger.info(f"[Job {job_id}] Loading Prolog rules from {rules_file}")
            prolog = self._load_prolog_engine(rules_file)
            modifier_map = self._load_modifier_map(prolog)
            
            if not modifier_map:
                logger.warning(f"[Job {job_id}] No modifier rules found, skipping symbolic reasoning")
                return {
                    "skipped": True,
                    "reason": "No modifier rules found",
                    "elapsed_time_seconds": round(time.time() - start_time, 2)
                }
            
            # Get directories
            nms_dir = settings.results_dir / job_id / "nms"
            refined_dir = settings.results_dir / job_id / "refined"
            
            if not nms_dir.exists():
                raise SymbolicReasoningError(f"NMS predictions directory not found: {nms_dir}")
            
            # Load NMS-filtered predictions
            logger.info(f"[Job {job_id}] Loading NMS-filtered predictions from {nms_dir}")
            nms_predictions = self._parse_predictions(nms_dir)
            
            if not nms_predictions:
                logger.warning(f"[Job {job_id}] No NMS predictions found")
                elapsed_time = time.time() - start_time
                return {
                    "total_images": 0,
                    "total_adjustments": 0,
                    "elapsed_time_seconds": round(elapsed_time, 2)
                }
            
            # Apply symbolic reasoning to each image
            refined_predictions: Dict[str, List[PredictionDict]] = {}
            full_report: List[Dict[str, Any]] = []
            total_adjustments = 0
            
            for image_name, objects in nms_predictions.items():
                if not objects:
                    continue
                
                # Apply modifiers
                refined_objs, change_log = self._apply_modifiers(objects, modifier_map, class_map)
                
                if refined_objs:
                    refined_predictions[image_name] = refined_objs
                
                # Add image name to each log entry
                for entry in change_log:
                    entry["image_name"] = image_name
                    full_report.append(entry)
                
                total_adjustments += len(change_log)
            
            # Save refined predictions
            logger.info(f"[Job {job_id}] Saving refined predictions to {refined_dir}")
            self._save_predictions(refined_predictions, refined_dir)
            
            # Save explainability report
            report_file = settings.results_dir / job_id / "symbolic_reasoning_report.csv"
            self._save_explainability_report(full_report, report_file)
            
            # Calculate statistics
            elapsed_time = time.time() - start_time
            
            stats = {
                "total_images": len(nms_predictions),
                "refined_images": len(refined_predictions),
                "total_adjustments": total_adjustments,
                "modifier_rules_loaded": len(modifier_map),
                "elapsed_time_seconds": round(elapsed_time, 2)
            }
            
            logger.info(
                f"[Job {job_id}] Symbolic reasoning completed. "
                f"Processed {len(nms_predictions)} images, "
                f"applied {total_adjustments} confidence adjustments "
                f"in {elapsed_time:.2f}s"
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"[Job {job_id}] Symbolic reasoning failed: {e}", exc_info=True)
            raise SymbolicReasoningError(f"Symbolic reasoning failed: {e}") from e


# Global symbolic reasoning service instance
symbolic_reasoning_service = SymbolicReasoningService()
