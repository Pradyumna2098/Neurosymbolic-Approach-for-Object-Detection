"""Visualization service for generating annotated images with bounding boxes.

This service provides functionality to draw bounding boxes and labels on images
for object detection visualization. Currently supports YOLO normalized format
with axis-aligned bounding boxes.
"""

import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

from app.core import settings

# Logger
logger = logging.getLogger(__name__)

# Type aliases
Detection = Dict[str, Any]
Color = Tuple[int, int, int]

# DOTA dataset class color palette (per visualization_color_schemes.md)
CLASS_COLORS = {
    'plane': (255, 0, 0),           # Red
    'ship': (0, 255, 0),            # Green
    'storage_tank': (0, 0, 255),    # Blue
    'storage-tank': (0, 0, 255),    # Alternate naming
    'baseball_diamond': (255, 255, 0),      # Yellow
    'baseball-diamond': (255, 255, 0),      # Alternate naming
    'tennis_court': (255, 0, 255),          # Magenta
    'tennis-court': (255, 0, 255),          # Alternate naming
    'basketball_court': (0, 255, 255),      # Cyan
    'basketball-court': (0, 255, 255),      # Alternate naming
    'ground_track_field': (255, 128, 0),    # Orange
    'ground-track-field': (255, 128, 0),    # Alternate naming
    'harbor': (128, 0, 255),        # Purple
    'bridge': (0, 128, 255),        # Light Blue
    'large_vehicle': (255, 128, 128),       # Light Red
    'large-vehicle': (255, 128, 128),       # Alternate naming
    'small_vehicle': (128, 255, 128),       # Light Green
    'small-vehicle': (128, 255, 128),       # Alternate naming
    'helicopter': (128, 128, 255),          # Light Purple
    'roundabout': (192, 192, 0),    # Dark Yellow
    'soccer_ball_field': (192, 0, 192),     # Dark Magenta
    'soccer-ball-field': (192, 0, 192),     # Alternate naming
    'swimming_pool': (0, 192, 192), # Dark Cyan
    'swimming-pool': (0, 192, 192), # Alternate naming
}

# Default class mapping for DOTA dataset (class_id -> class_name)
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


class VisualizationError(Exception):
    """Raised when visualization operations fail."""
    
    pass


def generate_color_from_name(class_name: str) -> Color:
    """Generate a deterministic color from class name using MD5 hash.
    
    Args:
        class_name: Object class name
        
    Returns:
        RGB tuple (r, g, b) with values 0-255
    """
    # Create hash from class name
    hash_object = hashlib.md5(class_name.encode())
    hash_hex = hash_object.hexdigest()
    hash_int = int(hash_hex, 16)
    
    # Extract RGB components
    r = (hash_int >> 16) & 0xFF
    g = (hash_int >> 8) & 0xFF
    b = hash_int & 0xFF
    
    # Ensure minimum brightness (avoid very dark colors)
    min_brightness = 64
    r = max(r, min_brightness)
    g = max(g, min_brightness)
    b = max(b, min_brightness)
    
    return (r, g, b)


def get_class_color(class_name: str) -> Color:
    """Get color for a class name from palette or generate deterministically.
    
    Args:
        class_name: Name of object class
        
    Returns:
        RGB tuple (r, g, b)
    """
    # Normalize class name (handle variations)
    normalized = class_name.lower().replace('_', '-')
    
    # Check palette first
    if normalized in CLASS_COLORS:
        return CLASS_COLORS[normalized]
    
    # Also check original name
    if class_name.lower() in CLASS_COLORS:
        return CLASS_COLORS[class_name.lower()]
    
    # Generate deterministic color for unknown classes
    return generate_color_from_name(class_name)


def get_line_width(confidence: float, base_width: int = 2, max_width: int = 4) -> int:
    """Calculate line width based on confidence level.
    
    High confidence = Thicker lines
    Low confidence = Thinner lines
    
    Args:
        confidence: Detection confidence (0.0 to 1.0)
        base_width: Base line width
        max_width: Maximum line width to prevent excessive thickness
        
    Returns:
        Line width in pixels (capped at max_width)
    """
    if confidence >= 0.9:
        width = base_width * 2      # Very confident
    elif confidence >= 0.7:
        width = base_width          # Confident
    elif confidence >= 0.5:
        width = max(1, base_width - 1)  # Moderately confident
    else:
        width = 1                   # Low confidence
    
    return min(width, max_width)


def adapt_style_to_image_size(img_width: int, img_height: int) -> Dict[str, int]:
    """Adapt visual style based on image dimensions.
    
    Larger images → Thicker lines, larger text
    Smaller images → Thinner lines, smaller text
    
    Args:
        img_width: Image width in pixels
        img_height: Image height in pixels
        
    Returns:
        Style configuration dictionary
    """
    max_dim = max(img_width, img_height)
    
    if max_dim <= 640:
        return {
            'line_width': 1,
            'font_size': 10,
            'label_padding': 2,
        }
    elif max_dim <= 1280:
        return {
            'line_width': 2,
            'font_size': 14,
            'label_padding': 3,
        }
    elif max_dim <= 2048:
        return {
            'line_width': 3,
            'font_size': 18,
            'label_padding': 4,
        }
    else:  # > 2048
        return {
            'line_width': 4,
            'font_size': 24,
            'label_padding': 6,
        }


def parse_yolo_predictions(prediction_file: Path, class_map: Dict[int, str] = None) -> List[Detection]:
    """Parse YOLO format predictions from text file.
    
    Format: class_id x_center y_center width height confidence
    All coordinates are normalized to [0, 1].
    
    Args:
        prediction_file: Path to .txt prediction file
        class_map: Optional mapping from class_id to class_name
        
    Returns:
        List of detection dictionaries
    """
    if class_map is None:
        class_map = DEFAULT_CLASS_MAP
    
    detections = []
    
    if not prediction_file.exists():
        logger.warning(f"Prediction file not found: {prediction_file}")
        return detections
    
    with open(prediction_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 6:
                continue
            
            try:
                class_id = int(parts[0])
                x_center = float(parts[1])
                y_center = float(parts[2])
                width = float(parts[3])
                height = float(parts[4])
                confidence = float(parts[5])
                
                # Get class name from mapping
                class_name = class_map.get(class_id, f"class_{class_id}")
                
                detection = {
                    'class_id': class_id,
                    'class_name': class_name,
                    'x_center': x_center,
                    'y_center': y_center,
                    'width': width,
                    'height': height,
                    'confidence': confidence,
                    'format': 'yolo'
                }
                detections.append(detection)
                
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse line: {line.strip()} - {e}")
                continue
    
    return detections


def yolo_to_pixel_coords(detection: Detection, img_width: int, img_height: int) -> Tuple[int, int, int, int]:
    """Convert YOLO normalized coordinates to pixel coordinates.
    
    Args:
        detection: Detection dict with normalized coords
        img_width: Image width in pixels
        img_height: Image height in pixels
        
    Returns:
        Tuple of (x_min, y_min, x_max, y_max) in pixel coordinates
    """
    cx = detection['x_center'] * img_width
    cy = detection['y_center'] * img_height
    w = detection['width'] * img_width
    h = detection['height'] * img_height
    
    x_min = int(cx - w / 2)
    y_min = int(cy - h / 2)
    x_max = int(cx + w / 2)
    y_max = int(cy + h / 2)
    
    return (x_min, y_min, x_max, y_max)


def draw_bbox(draw: ImageDraw.ImageDraw, bbox: Tuple[int, int, int, int], color: Color, line_width: int = 2) -> None:
    """Draw an axis-aligned bounding box.
    
    Args:
        draw: PIL ImageDraw object
        bbox: Tuple of (x_min, y_min, x_max, y_max) in pixel coordinates
        color: RGB tuple (r, g, b)
        line_width: Width of box lines
    """
    x_min, y_min, x_max, y_max = bbox
    draw.rectangle([x_min, y_min, x_max, y_max], outline=color, width=line_width)


def draw_label(
    draw: ImageDraw.ImageDraw, 
    detection: Detection, 
    position: Tuple[int, int], 
    color: Color,
    font: Optional[ImageFont.FreeTypeFont] = None,
    show_confidence: bool = True,
    label_padding: int = 3
) -> None:
    """Draw a label with class name and confidence score.
    
    Args:
        draw: PIL ImageDraw object
        detection: Detection dict with class_name and confidence
        position: (x, y) tuple for label placement
        color: Text color RGB tuple
        font: Optional font object
        show_confidence: Whether to display confidence score
        label_padding: Padding around label text
    """
    # Format label text
    if show_confidence:
        label = f"{detection['class_name']} {detection['confidence']:.2f}"
    else:
        label = detection['class_name']
    
    # Use default font if not provided
    if font is None:
        font = ImageFont.load_default()
    
    # Get text bounding box
    bbox = draw.textbbox(position, label, font=font)
    
    # Draw background rectangle for better readability (black background)
    background_color = (0, 0, 0)
    draw.rectangle(
        [bbox[0] - label_padding, bbox[1] - label_padding, 
         bbox[2] + label_padding, bbox[3] + label_padding],
        fill=background_color
    )
    
    # Draw text
    draw.text(position, label, fill=color, font=font)


def get_label_position(bbox: Tuple[int, int, int, int], image_height: int) -> Tuple[int, int]:
    """Determine optimal label position relative to bounding box.
    
    Args:
        bbox: Bounding box as (x_min, y_min, x_max, y_max)
        image_height: Height of image in pixels
        
    Returns:
        (x, y) tuple for label placement
    """
    x_min, y_min, x_max, y_max = bbox
    
    # Place label above the box if there's space
    label_offset = 5
    if y_min > 20:  # Enough space above
        return (x_min, y_min - 20)
    else:  # Place inside/below the box
        return (x_min + label_offset, y_min + label_offset)


def load_font(font_size: int) -> ImageFont.FreeTypeFont:
    """Load a TrueType font with fallback to default.
    
    Args:
        font_size: Font size in pixels
        
    Returns:
        Font object
    """
    # Try common font paths
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:\\Windows\\Fonts\\arial.ttf",
    ]
    
    for font_path in font_paths:
        try:
            return ImageFont.truetype(font_path, size=font_size)
        except (IOError, OSError):
            continue
    
    # Fallback to default font
    logger.warning(f"Could not load TrueType font, using default")
    return ImageFont.load_default()


class VisualizationService:
    """Service for generating annotated images with bounding boxes.
    
    This service handles:
    - Loading original images
    - Parsing prediction files (YOLO format)
    - Drawing bounding boxes with class colors
    - Adding labels with class names and confidence
    - Saving annotated images
    """
    
    def __init__(self):
        """Initialize the visualization service."""
        pass
    
    def visualize_image(
        self,
        image_path: Path,
        prediction_file: Path,
        output_path: Path,
        class_map: Optional[Dict[int, str]] = None,
        show_labels: bool = True,
        show_confidence: bool = True
    ) -> Dict[str, Any]:
        """Generate visualization for a single image with its predictions.
        
        Args:
            image_path: Path to original image
            prediction_file: Path to prediction text file
            output_path: Path to save annotated image
            class_map: Optional mapping from class_id to class_name
            show_labels: Whether to show class labels
            show_confidence: Whether to show confidence scores
            
        Returns:
            Dictionary with visualization statistics
            
        Raises:
            VisualizationError: If visualization fails
        """
        try:
            # Load original image
            if not image_path.exists():
                raise VisualizationError(f"Image file not found: {image_path}")
            
            # Use context manager to ensure file is closed
            with Image.open(image_path) as img:
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    image = img.convert('RGB')
                else:
                    # Copy image so we can close the file handle
                    image = img.copy()
            
            img_width, img_height = image.size
            
            # Parse predictions
            detections = parse_yolo_predictions(prediction_file, class_map)
            
            if not detections:
                logger.info(f"No detections found for {image_path.name}, saving original image")
                # Save original image if no detections
                output_path.parent.mkdir(parents=True, exist_ok=True)
                image.save(output_path)
                return {
                    'image_name': image_path.name,
                    'detection_count': 0,
                    'image_width': img_width,
                    'image_height': img_height
                }
            
            # Adapt style based on image size
            style = adapt_style_to_image_size(img_width, img_height)
            
            # Load font
            font = load_font(style['font_size'])
            
            # Create drawing context
            draw = ImageDraw.Draw(image)
            
            # Draw each detection
            for detection in detections:
                # Get class color
                color = get_class_color(detection['class_name'])
                
                # Convert normalized coordinates to pixels
                bbox = yolo_to_pixel_coords(detection, img_width, img_height)
                
                # Get line width based on confidence
                line_width = get_line_width(detection['confidence'], style['line_width'])
                
                # Draw bounding box
                draw_bbox(draw, bbox, color, line_width)
                
                # Draw label if enabled
                if show_labels:
                    label_pos = get_label_position(bbox, img_height)
                    draw_label(
                        draw,
                        detection,
                        label_pos,
                        color,
                        font,
                        show_confidence,
                        style['label_padding']
                    )
            
            # Save annotated image
            output_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(output_path)
            
            logger.info(f"Saved visualization with {len(detections)} detections to {output_path}")
            
            return {
                'image_name': image_path.name,
                'detection_count': len(detections),
                'image_width': img_width,
                'image_height': img_height,
                'output_path': str(output_path)
            }
            
        except Exception as e:
            logger.error(f"Visualization failed for {image_path}: {e}", exc_info=True)
            raise VisualizationError(f"Visualization failed: {e}") from e
    
    def visualize_job(
        self,
        job_id: str,
        stage: str = "refined",
        show_labels: bool = True,
        show_confidence: bool = True,
        storage_service: Any = None
    ) -> Dict[str, Any]:
        """Generate visualizations for all images in a job.
        
        Args:
            job_id: Job identifier
            stage: Processing stage to visualize ('raw', 'nms', or 'refined')
            show_labels: Whether to show class labels
            show_confidence: Whether to show confidence scores
            storage_service: Storage service instance for file operations
            
        Returns:
            Dictionary with visualization statistics
            
        Raises:
            VisualizationError: If visualization generation fails
        """
        try:
            logger.info(f"[Job {job_id}] Starting visualization generation for stage: {stage}")
            
            # Get directories
            upload_dir = settings.uploads_dir / job_id
            predictions_dir = settings.results_dir / job_id / stage
            viz_dir = settings.visualizations_dir / job_id
            
            # Ensure directories exist
            if not upload_dir.exists():
                raise VisualizationError(f"Upload directory not found: {upload_dir}")
            
            if not predictions_dir.exists():
                raise VisualizationError(f"Predictions directory not found: {predictions_dir}")
            
            viz_dir.mkdir(parents=True, exist_ok=True)
            
            # Get job data to find uploaded files
            if storage_service:
                job_data = storage_service.get_job(job_id)
                if not job_data or not job_data.get('files'):
                    raise VisualizationError(f"No files found for job {job_id}")
                uploaded_files = job_data['files']
            else:
                # Fallback: Find all images in upload directory
                uploaded_files = []
                for img_path in upload_dir.glob("*"):
                    if img_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp']:
                        uploaded_files.append({
                            'stored_filename': img_path.name,
                            'file_id': img_path.stem
                        })
            
            # Process each image
            total_images = len(uploaded_files)
            processed_count = 0
            total_detections = 0
            
            for file_info in uploaded_files:
                stored_filename = file_info['stored_filename']
                file_id = file_info.get('file_id', Path(stored_filename).stem)
                
                # Find image file
                image_path = upload_dir / stored_filename
                if not image_path.exists():
                    logger.warning(f"[Job {job_id}] Image not found: {image_path}")
                    continue
                
                # Find prediction file (should match file_id)
                prediction_file = predictions_dir / f"{file_id}.txt"
                if not prediction_file.exists():
                    logger.warning(f"[Job {job_id}] Prediction file not found: {prediction_file}")
                    continue
                
                # Generate output filename
                output_filename = f"{file_id}{image_path.suffix}"
                output_path = viz_dir / output_filename
                
                # Visualize image
                try:
                    stats = self.visualize_image(
                        image_path,
                        prediction_file,
                        output_path,
                        show_labels=show_labels,
                        show_confidence=show_confidence
                    )
                    
                    processed_count += 1
                    total_detections += stats['detection_count']
                    
                    logger.info(
                        f"[Job {job_id}] [{processed_count}/{total_images}] "
                        f"Visualized {stats['detection_count']} detections in {stored_filename}"
                    )
                    
                except Exception as e:
                    logger.error(
                        f"[Job {job_id}] Failed to visualize {stored_filename}: {e}",
                        exc_info=True
                    )
                    continue
            
            # Generate statistics
            viz_stats = {
                'total_images': total_images,
                'visualized_images': processed_count,
                'failed_images': total_images - processed_count,
                'total_detections': total_detections,
                'avg_detections_per_image': total_detections / processed_count if processed_count > 0 else 0,
                'output_directory': str(viz_dir)
            }
            
            logger.info(
                f"[Job {job_id}] Visualization complete. "
                f"Processed {processed_count}/{total_images} images, "
                f"visualized {total_detections} detections"
            )
            
            return viz_stats
            
        except Exception as e:
            logger.error(f"[Job {job_id}] Visualization generation failed: {e}", exc_info=True)
            raise VisualizationError(f"Visualization generation failed: {e}") from e


# Global visualization service instance
visualization_service = VisualizationService()
