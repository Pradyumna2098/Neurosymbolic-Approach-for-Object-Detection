# Bounding Box Visualization Logic Design

## Overview

This document defines the logic and algorithms required to visualize detected object bounding boxes and labels on input images. The visualization pipeline reads model output text files containing object detections and overlays them onto images to create annotated outputs for analysis and presentation.

## Table of Contents

1. [Prediction File Format](#prediction-file-format)
2. [Visualization Pipeline](#visualization-pipeline)
3. [Overlay Logic](#overlay-logic)
4. [Library Recommendations](#library-recommendations)
5. [Color Schemes](#color-schemes)
6. [Label Formatting](#label-formatting)
7. [Output Conventions](#output-conventions)
8. [Implementation Guidelines](#implementation-guidelines)
9. [Error Handling](#error-handling)
10. [Performance Considerations](#performance-considerations)

---

## 1. Prediction File Format

### File Structure

Model predictions are stored in text files with one detection per line. The repository supports two primary formats:

#### Format 1: Oriented Bounding Box (OBB) Format
Used for rotated objects, common in aerial/satellite imagery.

```
<class_name> <confidence> <x1> <y1> <x2> <y2> <x3> <y3> <x4> <y4>
```

**Example:**
```
large_vehicle 0.8962 439.81 694.77 456.92 678.36 389.50 608.07 372.39 624.49
small_vehicle 0.8136 172.64 316.18 172.99 297.57 132.63 296.81 132.28 315.41
```

**Field Descriptions:**
- `class_name`: String label for the detected object class (e.g., "large_vehicle", "small_vehicle")
- `confidence`: Float value between 0.0 and 1.0 representing detection confidence
- `x1, y1, x2, y2, x3, y3, x4, y4`: Eight coordinate values representing the four corners of the oriented bounding box in pixel coordinates

**Corner Order:**
The four corners are typically ordered as follows (clockwise or counter-clockwise):
```
(x1, y1) --- (x2, y2)
   |            |
(x4, y4) --- (x3, y3)
```

#### Format 2: YOLO Normalized Format
Used internally in preprocessing stages.

```
<class_id> <cx> <cy> <width> <height> <confidence>
```

**Example:**
```
0 0.5 0.5 0.2 0.3 0.95
1 0.3 0.7 0.15 0.25 0.87
```

**Field Descriptions:**
- `class_id`: Integer class identifier (0-indexed)
- `cx, cy`: Normalized center coordinates (0.0 to 1.0)
- `width, height`: Normalized box dimensions (0.0 to 1.0)
- `confidence`: Detection confidence score (0.0 to 1.0)

**Coordinate System:**
- All values are normalized to [0, 1] relative to image dimensions
- Origin (0, 0) is at top-left corner
- (1, 1) is at bottom-right corner

### Format Detection Logic

```python
def detect_prediction_format(line: str) -> str:
    """
    Detect the format of a prediction line.
    
    Args:
        line: Single line from prediction file
    
    Returns:
        'obb' for oriented bounding boxes
        'yolo' for YOLO normalized format
    """
    parts = line.strip().split()
    
    # OBB format: class_name conf x1 y1 x2 y2 x3 y3 x4 y4 (10 parts)
    if len(parts) == 10 and not parts[0].isdigit():
        return 'obb'
    
    # YOLO format: class_id cx cy w h conf (6 parts)
    elif len(parts) == 6 and parts[0].isdigit():
        return 'yolo'
    
    else:
        raise ValueError(f"Unknown prediction format: {line}")
```

---

## 2. Visualization Pipeline

### High-Level Workflow

```
┌─────────────────────┐
│  Prediction File    │
│   (.txt format)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Parse Predictions  │
│  - Read text file   │
│  - Extract fields   │
│  - Validate format  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Load Input Image   │
│   (Original PNG)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Draw Bounding      │
│  Boxes & Labels     │
│  - Draw polygons    │
│  - Add class names  │
│  - Show confidence  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Save Visualized    │
│  Image (output PNG) │
└─────────────────────┘
```

### Detailed Process Steps

#### Step 1: File Input and Parsing

**Input Requirements:**
- Prediction text file (e.g., `P0006.txt`)
- Corresponding input image (e.g., `P0006og.png` or `P0006.png`)
- Class mapping file (optional, for converting class IDs to names)

**Parsing Logic:**

```python
def parse_obb_predictions(prediction_file: Path) -> List[Dict]:
    """
    Parse oriented bounding box predictions.
    
    Args:
        prediction_file: Path to .txt prediction file
    
    Returns:
        List of detection dictionaries with keys:
        - 'class_name': str
        - 'confidence': float
        - 'polygon': List of (x, y) tuples for 4 corners
    """
    detections = []
    
    with open(prediction_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 10:
                continue
            
            detection = {
                'class_name': parts[0],
                'confidence': float(parts[1]),
                'polygon': [
                    (float(parts[2]), float(parts[3])),  # (x1, y1)
                    (float(parts[4]), float(parts[5])),  # (x2, y2)
                    (float(parts[6]), float(parts[7])),  # (x3, y3)
                    (float(parts[8]), float(parts[9]))   # (x4, y4)
                ]
            }
            detections.append(detection)
    
    return detections
```

#### Step 2: Image Loading

```python
def load_image(image_path: Path):
    """
    Load the input image for visualization.
    
    Args:
        image_path: Path to input image file
    
    Returns:
        Image object (PIL.Image or numpy array)
    """
    # Using PIL
    from PIL import Image
    img = Image.open(image_path)
    
    # Convert to RGB if needed (handle grayscale or RGBA)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    return img
```

#### Step 3: Coordinate Transformation (if needed)

For YOLO format, convert normalized coordinates to pixel coordinates:

```python
def yolo_to_pixel_coords(bbox_yolo, img_width, img_height):
    """
    Convert YOLO normalized bbox to pixel coordinates.
    
    Args:
        bbox_yolo: [cx, cy, width, height] in normalized coords
        img_width: Image width in pixels
        img_height: Image height in pixels
    
    Returns:
        [x_min, y_min, x_max, y_max] in pixel coordinates
    """
    cx, cy, w, h = bbox_yolo
    
    # Convert to pixel coordinates
    cx_px = cx * img_width
    cy_px = cy * img_height
    w_px = w * img_width
    h_px = h * img_height
    
    # Calculate corners
    x_min = cx_px - w_px / 2
    y_min = cy_px - h_px / 2
    x_max = cx_px + w_px / 2
    y_max = cy_px + h_px / 2
    
    return [x_min, y_min, x_max, y_max]
```

---

## 3. Overlay Logic

### Drawing Bounding Boxes

#### For Oriented Bounding Boxes (OBB)

```python
def draw_obb(image, detection, color, line_width=2):
    """
    Draw an oriented bounding box on the image.
    
    Args:
        image: PIL Image or numpy array
        detection: Dict with 'polygon' key containing 4 (x, y) tuples
        color: RGB tuple (r, g, b)
        line_width: Width of the bounding box lines
    """
    from PIL import ImageDraw
    
    draw = ImageDraw.Draw(image)
    polygon = detection['polygon']
    
    # Draw the polygon
    # Connect all four corners and close the loop
    draw.polygon(polygon, outline=color, width=line_width)
    
    # Alternative: Draw lines between consecutive points
    # for i in range(len(polygon)):
    #     start = polygon[i]
    #     end = polygon[(i + 1) % len(polygon)]
    #     draw.line([start, end], fill=color, width=line_width)
```

#### For Axis-Aligned Bounding Boxes

```python
def draw_bbox(image, bbox, color, line_width=2):
    """
    Draw an axis-aligned bounding box.
    
    Args:
        image: PIL Image
        bbox: [x_min, y_min, x_max, y_max] in pixel coordinates
        color: RGB tuple (r, g, b)
        line_width: Width of box lines
    """
    from PIL import ImageDraw
    
    draw = ImageDraw.Draw(image)
    x_min, y_min, x_max, y_max = bbox
    
    # Draw rectangle
    draw.rectangle([x_min, y_min, x_max, y_max], 
                   outline=color, 
                   width=line_width)
```

### Drawing Labels

Labels should be positioned near the bounding box and include:
1. Class name
2. Confidence score (formatted)

```python
def draw_label(image, detection, position, color, background_color=None):
    """
    Draw a label with class name and confidence score.
    
    Args:
        image: PIL Image
        detection: Detection dict with 'class_name' and 'confidence'
        position: (x, y) tuple for label placement
        color: Text color RGB tuple
        background_color: Optional background box color
    """
    from PIL import ImageDraw, ImageFont
    
    draw = ImageDraw.Draw(image)
    
    # Format label text
    label = f"{detection['class_name']} {detection['confidence']:.2f}"
    
    # Try to load a font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", size=14)
    except:
        font = ImageFont.load_default()
    
    # Get text bounding box
    bbox = draw.textbbox(position, label, font=font)
    
    # Draw background rectangle for better readability
    if background_color:
        padding = 2
        draw.rectangle(
            [bbox[0] - padding, bbox[1] - padding, 
             bbox[2] + padding, bbox[3] + padding],
            fill=background_color
        )
    
    # Draw text
    draw.text(position, label, fill=color, font=font)
```

### Label Placement Strategy

```python
def get_label_position(polygon, image_height):
    """
    Determine optimal label position relative to bounding box.
    
    Args:
        polygon: List of (x, y) tuples for box corners
        image_height: Height of image in pixels
    
    Returns:
        (x, y) tuple for label placement
    """
    # Find the top-left most point
    min_y = min(pt[1] for pt in polygon)
    min_x = min(pt[0] for pt in polygon)
    
    # Place label above the box if there's space
    label_offset = 5
    if min_y > 20:  # Enough space above
        return (min_x, min_y - 20)
    else:  # Place inside/below the box
        return (min_x + label_offset, min_y + label_offset)
```

---

## 4. Library Recommendations

### Primary Library: Pillow (PIL)

**Advantages:**
- Pure Python, easy to install
- Good performance for drawing operations
- Flexible image format support
- Active maintenance and community support

**Installation:**
```bash
pip install Pillow
```

**Basic Usage:**
```python
from PIL import Image, ImageDraw, ImageFont

# Load image
img = Image.open("input.png")

# Create drawing context
draw = ImageDraw.Draw(img)

# Draw shapes
draw.rectangle([x1, y1, x2, y2], outline=(255, 0, 0), width=2)
draw.polygon([(x1, y1), (x2, y2), (x3, y3), (x4, y4)], 
             outline=(0, 255, 0), width=2)

# Save result
img.save("output.png")
```

### Alternative: OpenCV (cv2)

**Advantages:**
- High performance for large images
- Advanced drawing capabilities
- Built-in geometric transformations
- Already used in many ML pipelines

**Installation:**
```bash
pip install opencv-python
```

**Basic Usage:**
```python
import cv2
import numpy as np

# Load image
img = cv2.imread("input.png")

# Draw polygon
points = np.array([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], np.int32)
cv2.polylines(img, [points], isClosed=True, 
              color=(0, 255, 0), thickness=2)

# Add text
cv2.putText(img, "label", (x, y), cv2.FONT_HERSHEY_SIMPLEX,
            0.5, (255, 0, 0), 2)

# Save result
cv2.imwrite("output.png", img)
```

### Alternative: Matplotlib

**Advantages:**
- Excellent for interactive visualization
- Publication-quality output
- Easy integration with Jupyter notebooks

**Disadvantages:**
- Slower for batch processing
- More memory-intensive

**Usage:**
```python
import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(1)
img = plt.imread("input.png")
ax.imshow(img)

# Add polygon patch
polygon = patches.Polygon([(x1, y1), (x2, y2), (x3, y3), (x4, y4)],
                          linewidth=2, edgecolor='r', facecolor='none')
ax.add_patch(polygon)

plt.savefig("output.png", dpi=300, bbox_inches='tight')
```

### Recommendation

**For production implementation: Use Pillow (PIL)**
- Balances performance and ease of use
- Lightweight dependency
- Suitable for batch processing
- Already used in SAHI and other components

---

## 5. Color Schemes

### Color Selection Strategy

#### Per-Class Color Mapping

Assign a unique, distinctive color to each object class for easy visual identification.

```python
# Predefined color palette (RGB tuples)
CLASS_COLORS = {
    'plane': (255, 0, 0),           # Red
    'ship': (0, 255, 0),            # Green
    'storage-tank': (0, 0, 255),    # Blue
    'baseball-diamond': (255, 255, 0),  # Yellow
    'tennis-court': (255, 0, 255),  # Magenta
    'basketball-court': (0, 255, 255),  # Cyan
    'ground-track-field': (255, 128, 0),  # Orange
    'harbor': (128, 0, 255),        # Purple
    'bridge': (0, 128, 255),        # Light Blue
    'large-vehicle': (255, 128, 128),  # Light Red
    'small-vehicle': (128, 255, 128),  # Light Green
    'helicopter': (128, 128, 255),  # Light Blue
    'roundabout': (192, 192, 0),    # Dark Yellow
    'soccer-ball-field': (192, 0, 192),  # Dark Magenta
    'swimming-pool': (0, 192, 192), # Dark Cyan
}

def get_class_color(class_name: str) -> tuple[int, int, int]:
    """
    Get the color for a given class name.
    
    Args:
        class_name: Name of the object class
    
    Returns:
        RGB tuple (r, g, b)
    """
    if class_name in CLASS_COLORS:
        return CLASS_COLORS[class_name]
    else:
        # Generate a deterministic color from class name hash
        import hashlib
        hash_value = int(hashlib.md5(class_name.encode()).hexdigest(), 16)
        r = (hash_value >> 16) & 0xFF
        g = (hash_value >> 8) & 0xFF
        b = hash_value & 0xFF
        return (r, g, b)
```

#### Confidence-Based Color Intensity

Alternative approach: Use color intensity or saturation to represent confidence levels.

```python
def get_confidence_color(confidence: float, base_color=(0, 255, 0)):
    """
    Adjust color intensity based on confidence score.
    
    Args:
        confidence: Detection confidence (0.0 to 1.0)
        base_color: Base RGB color
    
    Returns:
        RGB tuple with adjusted intensity
    """
    r, g, b = base_color
    alpha = confidence  # Use confidence as alpha/intensity
    
    # Blend with white for low confidence
    r_adjusted = int(r * alpha + 255 * (1 - alpha))
    g_adjusted = int(g * alpha + 255 * (1 - alpha))
    b_adjusted = int(b * alpha + 255 * (1 - alpha))
    
    return (r_adjusted, g_adjusted, b_adjusted)
```

### Recommended Color Schemes

#### Scheme 1: High Contrast (Default)
- Use bright, saturated colors from different hue families
- Suitable for: Dense scenes, overlapping objects
- Example: Red, Green, Blue, Yellow, Cyan, Magenta

#### Scheme 2: Pastel Colors
- Use desaturated colors for subtle visualization
- Suitable for: Presentation, less cluttered scenes
- Example: Light blue, light green, light pink, light yellow

#### Scheme 3: Diverging Palette
- Use color gradients based on properties (e.g., confidence)
- Suitable for: Emphasizing high-confidence detections
- Example: Red (low) → Yellow (medium) → Green (high)

### Line Width Recommendations

```python
def get_line_width(image_size, base_width=2):
    """
    Calculate appropriate line width based on image size.
    
    Args:
        image_size: (width, height) tuple
        base_width: Base line width for standard images
    
    Returns:
        Adjusted line width
    """
    width, height = image_size
    max_dim = max(width, height)
    
    # Scale line width with image size
    if max_dim <= 640:
        return base_width
    elif max_dim <= 1280:
        return base_width * 1.5
    elif max_dim <= 2048:
        return base_width * 2
    else:
        return base_width * 3
```

---

## 6. Label Formatting

### Label Content

Each label should display:
1. **Class Name**: Human-readable object class
2. **Confidence Score**: Formatted to 2-3 decimal places

### Format Templates

```python
# Standard format
label = f"{class_name} {confidence:.2f}"
# Example: "large_vehicle 0.89"

# Percentage format
label = f"{class_name} {confidence*100:.1f}%"
# Example: "large_vehicle 89.6%"

# Short format (high-density scenes)
label = f"{class_name[:3]} {confidence:.2f}"
# Example: "lar 0.89"

# Verbose format (analysis/debugging)
label = f"{class_name}\nConf: {confidence:.3f}\nID: {det_id}"
# Example: "large_vehicle\nConf: 0.896\nID: 42"
```

### Font Specifications

```python
LABEL_FONT_CONFIG = {
    'family': 'Arial',           # Or 'DejaVuSans', 'Liberation Sans'
    'size': 14,                  # Scale with image size
    'weight': 'bold',            # 'normal' or 'bold'
    'color': (255, 255, 255),    # White text
    'background': (0, 0, 0),     # Black background
    'background_alpha': 0.7      # Semi-transparent background
}

def get_font_size(image_size):
    """Calculate appropriate font size based on image dimensions."""
    width, height = image_size
    max_dim = max(width, height)
    
    if max_dim <= 640:
        return 12
    elif max_dim <= 1280:
        return 14
    elif max_dim <= 2048:
        return 18
    else:
        return 24
```

### Text Readability Enhancements

1. **Background Box**: Draw semi-transparent rectangle behind text
2. **Text Outline**: Add dark outline around light text (or vice versa)
3. **Shadow Effect**: Offset duplicate text in contrasting color

```python
def draw_text_with_background(draw, position, text, font, 
                              text_color=(255, 255, 255),
                              bg_color=(0, 0, 0)):
    """
    Draw text with a background rectangle for better readability.
    
    Args:
        draw: PIL ImageDraw object
        position: (x, y) tuple
        text: String to draw
        font: PIL ImageFont object
        text_color: RGB tuple for text
        bg_color: RGB tuple for background
    """
    # Get text bounding box
    bbox = draw.textbbox(position, text, font=font)
    
    # Add padding
    padding = 3
    bg_bbox = [
        bbox[0] - padding,
        bbox[1] - padding,
        bbox[2] + padding,
        bbox[3] + padding
    ]
    
    # Draw background
    draw.rectangle(bg_bbox, fill=bg_color)
    
    # Draw text
    draw.text(position, text, fill=text_color, font=font)
```

---

## 7. Output Conventions

### File Naming Convention

Follow a consistent naming pattern for output files:

```
<input_name>_<suffix>.<extension>

Where:
- input_name: Original image filename without extension
- suffix: Descriptive suffix indicating the output type
- extension: Image format (png, jpg, etc.)
```

#### Recommended Suffixes

```python
OUTPUT_SUFFIXES = {
    'pred': 'predictions only',          # P0006pred.png
    'gt': 'ground truth annotations',    # P0006gt.png
    'compare': 'side-by-side comparison', # P0006compare.png
    'overlay': 'overlay on original',    # P0006overlay.png
    'viz': 'general visualization',      # P0006viz.png
    'annotated': 'annotated output'      # P0006annotated.png
}

def generate_output_filename(input_path: Path, suffix: str = 'pred') -> str:
    """
    Generate output filename based on input and suffix.
    
    Args:
        input_path: Path to input image
        suffix: Output type suffix
    
    Returns:
        Output filename string
    """
    stem = input_path.stem  # Filename without extension
    return f"{stem}{suffix}.png"
```

### Directory Structure

Organize output files in a clear directory hierarchy:

```
project_root/
├── data/
│   └── images/
│       └── val/
│           └── P0006og.png        # Original images
├── predictions/
│   └── raw/
│       └── P0006.txt              # Prediction text files
└── visualizations/
    ├── pred/
    │   └── P0006pred.png          # Visualized predictions
    ├── gt/
    │   └── P0006gt.png            # Visualized ground truth
    └── compare/
        └── P0006compare.png       # Side-by-side comparison
```

### Configuration Example

```yaml
# visualization_config.yaml
visualization:
  input_images_dir: /path/to/data/images/val
  predictions_dir: /path/to/predictions/raw
  output_dir: /path/to/visualizations/pred
  
  output_format: png                # png, jpg, or jpeg
  output_suffix: pred               # Appended to input filename
  output_quality: 95                # For JPEG, 1-100
  
  bbox_line_width: 2                # Bounding box line width
  label_font_size: 14               # Label text font size
  
  color_scheme: per_class           # per_class, confidence, or fixed
  show_confidence: true             # Include confidence in labels
  confidence_decimals: 2            # Decimal places for confidence
  
  filter_low_confidence: false      # Filter detections below threshold
  min_confidence: 0.25              # Minimum confidence to visualize
```

### Metadata File

Generate a JSON metadata file alongside visualizations for tracking:

```json
{
  "image_name": "P0006pred.png",
  "source_image": "P0006og.png",
  "prediction_file": "P0006.txt",
  "num_detections": 149,
  "class_distribution": {
    "large_vehicle": 147,
    "small_vehicle": 2
  },
  "confidence_range": [0.5334, 0.8962],
  "timestamp": "2024-01-15T10:30:00Z",
  "config": {
    "line_width": 2,
    "font_size": 14,
    "color_scheme": "per_class"
  }
}
```

---

## 8. Implementation Guidelines

### Complete Implementation Example

```python
#!/usr/bin/env python3
"""
Visualization script for object detection predictions.
"""

from pathlib import Path
from typing import Dict, List, Tuple
from PIL import Image, ImageDraw, ImageFont


def parse_obb_predictions(pred_file: Path) -> List[Dict]:
    """Parse OBB format predictions from text file."""
    detections = []
    
    with open(pred_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 10:
                continue
            
            detection = {
                'class_name': parts[0],
                'confidence': float(parts[1]),
                'polygon': [
                    (float(parts[2]), float(parts[3])),
                    (float(parts[4]), float(parts[5])),
                    (float(parts[6]), float(parts[7])),
                    (float(parts[8]), float(parts[9]))
                ]
            }
            detections.append(detection)
    
    return detections


def get_class_color(class_name: str) -> tuple[int, int, int]:
    """Return consistent color for each class."""
    colors = {
        'large-vehicle': (255, 0, 0),      # Red
        'small-vehicle': (0, 255, 0),      # Green
        'plane': (0, 0, 255),              # Blue
        'ship': (255, 255, 0),             # Yellow
    }
    return colors.get(class_name, (255, 255, 255))  # Default white


def draw_detection(draw: ImageDraw.Draw, detection: Dict, 
                  font: ImageFont.FreeTypeFont):
    """Draw a single detection on the image."""
    # Get color for this class
    color = get_class_color(detection['class_name'])
    
    # Draw polygon
    polygon = detection['polygon']
    draw.polygon(polygon, outline=color, width=2)
    
    # Prepare label
    label = f"{detection['class_name']} {detection['confidence']:.2f}"
    
    # Get label position (top-left of bounding box)
    min_x = min(pt[0] for pt in polygon)
    min_y = min(pt[1] for pt in polygon)
    label_pos = (min_x, max(0, min_y - 20))
    
    # Draw text background
    bbox = draw.textbbox(label_pos, label, font=font)
    draw.rectangle(bbox, fill=(0, 0, 0))
    
    # Draw text
    draw.text(label_pos, label, fill=color, font=font)


def visualize_predictions(image_path: Path, pred_path: Path, 
                         output_path: Path):
    """
    Main visualization function.
    
    Args:
        image_path: Path to input image
        pred_path: Path to predictions text file
        output_path: Path to save output image
    """
    # Load image
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Parse predictions
    detections = parse_obb_predictions(pred_path)
    
    # Create drawing context
    draw = ImageDraw.Draw(img)
    
    # Load font
    try:
        font = ImageFont.truetype("arial.ttf", size=14)
    except:
        font = ImageFont.load_default()
    
    # Draw each detection
    for detection in detections:
        draw_detection(draw, detection, font)
    
    # Save output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, quality=95)
    
    print(f"Saved visualization to {output_path}")
    print(f"Drew {len(detections)} detections")


def main():
    """Example usage."""
    # Define paths
    image_path = Path("data/images/P0006og.png")
    pred_path = Path("predictions/P0006.txt")
    output_path = Path("visualizations/P0006pred.png")
    
    # Visualize
    visualize_predictions(image_path, pred_path, output_path)


if __name__ == "__main__":
    main()
```

### Batch Processing

```python
def batch_visualize(images_dir: Path, predictions_dir: Path, 
                   output_dir: Path):
    """
    Visualize predictions for all images in a directory.
    
    Args:
        images_dir: Directory containing input images
        predictions_dir: Directory containing prediction text files
        output_dir: Directory to save visualized images
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all prediction files
    pred_files = list(predictions_dir.glob("*.txt"))
    
    print(f"Found {len(pred_files)} prediction files")
    
    for pred_file in pred_files:
        # Find corresponding image
        image_name = pred_file.stem + "og.png"  # Or just .stem + ".png"
        image_path = images_dir / image_name
        
        if not image_path.exists():
            # Try alternative naming
            image_path = images_dir / (pred_file.stem + ".png")
        
        if not image_path.exists():
            print(f"Warning: Image not found for {pred_file.name}")
            continue
        
        # Generate output path
        output_path = output_dir / (pred_file.stem + "pred.png")
        
        # Visualize
        try:
            visualize_predictions(image_path, pred_file, output_path)
        except Exception as e:
            print(f"Error processing {pred_file.name}: {e}")
```

---

## 9. Error Handling

### Common Issues and Solutions

#### Issue 1: Missing or Invalid Prediction File

```python
def safe_parse_predictions(pred_file: Path) -> List[Dict]:
    """Parse predictions with error handling."""
    if not pred_file.exists():
        raise FileNotFoundError(f"Prediction file not found: {pred_file}")
    
    detections = []
    
    try:
        with open(pred_file, 'r') as f:
            for line_num, line in enumerate(f, start=1):
                parts = line.strip().split()
                
                if len(parts) != 10:
                    print(f"Warning: Line {line_num} has {len(parts)} parts, expected 10")
                    continue
                
                try:
                    detection = {
                        'class_name': parts[0],
                        'confidence': float(parts[1]),
                        'polygon': [
                            (float(parts[2]), float(parts[3])),
                            (float(parts[4]), float(parts[5])),
                            (float(parts[6]), float(parts[7])),
                            (float(parts[8]), float(parts[9]))
                        ]
                    }
                    detections.append(detection)
                    
                except ValueError as e:
                    print(f"Warning: Invalid values on line {line_num}: {e}")
                    continue
                    
    except Exception as e:
        raise RuntimeError(f"Error reading prediction file: {e}")
    
    return detections
```

#### Issue 2: Image Format or Loading Errors

```python
def safe_load_image(image_path: Path) -> Image.Image:
    """Load image with error handling."""
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    try:
        img = Image.open(image_path)
        
        # Convert to RGB if needed
        if img.mode not in ('RGB', 'RGBA'):
            print(f"Converting image from {img.mode} to RGB")
            img = img.convert('RGB')
        
        return img
        
    except Exception as e:
        raise RuntimeError(f"Error loading image {image_path}: {e}")
```

#### Issue 3: Out-of-Bounds Coordinates

```python
def validate_polygon(polygon: list[tuple[float, float]], 
                    img_width: int, img_height: int) -> bool:
    """Check if polygon coordinates are within image bounds."""
    for x, y in polygon:
        if x < 0 or x > img_width or y < 0 or y > img_height:
            return False
    return True


def clip_polygon(polygon: list[tuple[float, float]], 
                img_width: int, img_height: int) -> list[tuple[float, float]]:
    """Clip polygon coordinates to image bounds."""
    clipped = []
    for x, y in polygon:
        x_clipped = max(0, min(x, img_width))
        y_clipped = max(0, min(y, img_height))
        clipped.append((x_clipped, y_clipped))
    return clipped
```

### Logging Best Practices

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def visualize_with_logging(image_path: Path, pred_path: Path, 
                          output_path: Path):
    """Visualization with comprehensive logging."""
    logger.info(f"Starting visualization for {image_path.name}")
    
    try:
        # Load image
        logger.debug(f"Loading image from {image_path}")
        img = safe_load_image(image_path)
        logger.info(f"Image loaded: {img.size[0]}x{img.size[1]}")
        
        # Parse predictions
        logger.debug(f"Parsing predictions from {pred_path}")
        detections = safe_parse_predictions(pred_path)
        logger.info(f"Found {len(detections)} detections")
        
        # Draw detections
        logger.debug("Drawing detections")
        # ... drawing code ...
        
        # Save output
        logger.debug(f"Saving to {output_path}")
        img.save(output_path)
        logger.info(f"Successfully saved visualization to {output_path}")
        
    except Exception as e:
        logger.error(f"Visualization failed: {e}", exc_info=True)
        raise
```

---

## 10. Performance Considerations

### Optimization Strategies

#### 1. Batch Processing with Multiprocessing

```python
from multiprocessing import Pool
from functools import partial


def process_single_image(pred_file: Path, images_dir: Path, 
                        output_dir: Path) -> str:
    """Process a single image (for parallel execution)."""
    image_path = images_dir / (pred_file.stem + "og.png")
    output_path = output_dir / (pred_file.stem + "pred.png")
    
    visualize_predictions(image_path, pred_file, output_path)
    return f"Processed {pred_file.name}"


def parallel_batch_visualize(predictions_dir: Path, images_dir: Path,
                            output_dir: Path, num_workers: int = 4):
    """Visualize predictions using multiple processes."""
    pred_files = list(predictions_dir.glob("*.txt"))
    
    # Create partial function with fixed arguments
    process_func = partial(
        process_single_image,
        images_dir=images_dir,
        output_dir=output_dir
    )
    
    # Process in parallel
    with Pool(num_workers) as pool:
        results = pool.map(process_func, pred_files)
    
    print(f"Completed {len(results)} visualizations")
```

#### 2. Memory-Efficient Large Image Handling

```python
def visualize_large_image(image_path: Path, pred_path: Path, 
                         output_path: Path, max_dimension: int = 4096):
    """
    Visualize predictions on large images with downsampling if needed.
    """
    img = Image.open(image_path)
    orig_size = img.size
    
    # Downsample if image is too large
    if max(img.size) > max_dimension:
        scale_factor = max_dimension / max(img.size)
        new_size = (int(img.size[0] * scale_factor), 
                   int(img.size[1] * scale_factor))
        img = img.resize(new_size, Image.LANCZOS)
        print(f"Downsampled from {orig_size} to {new_size}")
    else:
        scale_factor = 1.0
    
    # Parse and scale coordinates
    detections = parse_obb_predictions(pred_path)
    
    if scale_factor != 1.0:
        for det in detections:
            det['polygon'] = [(x * scale_factor, y * scale_factor) 
                            for x, y in det['polygon']]
    
    # Draw detections
    draw = ImageDraw.Draw(img)
    # ... drawing code ...
    
    img.save(output_path)
```

#### 3. Caching Font Objects

```python
class VisualizationCache:
    """Cache expensive objects for reuse."""
    
    def __init__(self):
        self._fonts = {}
        self._colors = {}
    
    def get_font(self, font_name: str, size: int):
        """Get or create font object."""
        key = (font_name, size)
        if key not in self._fonts:
            try:
                self._fonts[key] = ImageFont.truetype(font_name, size)
            except:
                self._fonts[key] = ImageFont.load_default()
        return self._fonts[key]
    
    def get_color(self, class_name: str):
        """Get or generate color for class."""
        if class_name not in self._colors:
            self._colors[class_name] = get_class_color(class_name)
        return self._colors[class_name]


# Usage
cache = VisualizationCache()

def visualize_with_cache(image_path, pred_path, output_path, cache):
    # ... load image and predictions ...
    
    font = cache.get_font("arial.ttf", 14)
    
    for detection in detections:
        color = cache.get_color(detection['class_name'])
        # ... draw detection ...
```

### Performance Benchmarks

Expected performance metrics (approximate):

| Image Size | Detections | Processing Time | Memory Usage |
|-----------|-----------|-----------------|--------------|
| 640x640   | 50        | ~50ms          | ~50MB        |
| 1024x1024 | 100       | ~100ms         | ~100MB       |
| 2048x2048 | 200       | ~250ms         | ~200MB       |
| 4096x4096 | 400       | ~800ms         | ~500MB       |

---

## Conclusion

This document provides comprehensive specifications for implementing bounding box visualization logic. The design emphasizes:

1. **Flexibility**: Support for multiple prediction formats (OBB, YOLO)
2. **Clarity**: Clear visual distinction between classes and confidence levels
3. **Robustness**: Error handling for edge cases
4. **Performance**: Optimizations for batch processing
5. **Maintainability**: Well-structured, documented code

### Next Steps

1. Implement visualization script based on these specifications
2. Test with sample images and predictions
3. Integrate with existing pipeline (symbolic reasoning, evaluation)
4. Create user-facing CLI tool or API endpoint
5. Generate documentation and usage examples

### References

- PIL/Pillow Documentation: https://pillow.readthedocs.io/
- OpenCV Documentation: https://docs.opencv.org/
- YOLO Format Specification: https://docs.ultralytics.com/
- DOTA Dataset Paper: https://arxiv.org/abs/1711.10398
