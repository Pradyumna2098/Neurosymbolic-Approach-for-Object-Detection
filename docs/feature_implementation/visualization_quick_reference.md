# Visualization Quick Reference Guide

## Overview

Quick reference for implementing and using the bounding box visualization system. This guide provides code snippets, examples, and configuration templates for rapid development.

---

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [Quick Start Examples](#quick-start-examples)
3. [Code Snippets Library](#code-snippets-library)
4. [Configuration Templates](#configuration-templates)
5. [Common Issues and Solutions](#common-issues-and-solutions)
6. [API Reference](#api-reference)

---

## 1. Installation and Setup

### Required Dependencies

```bash
# Core dependencies
pip install Pillow>=10.0.0

# Optional (for advanced features)
pip install opencv-python>=4.8.0
pip install matplotlib>=3.7.0
```

### Verify Installation

```python
# test_setup.py
from PIL import Image, ImageDraw, ImageFont

print("✓ Pillow installed successfully")

# Test basic functionality
img = Image.new('RGB', (100, 100), color='white')
draw = ImageDraw.Draw(img)
draw.rectangle([10, 10, 90, 90], outline='red', width=2)
img.save('test_output.png')
print("✓ Basic drawing functionality works")
```

---

## 2. Quick Start Examples

### Example 1: Visualize Single Image

```python
#!/usr/bin/env python3
"""Minimal example: Visualize predictions on a single image."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def visualize_single_image(image_path, pred_path, output_path):
    """Visualize predictions on one image."""
    
    # Load image
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    
    # Parse predictions
    with open(pred_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 10:
                continue
            
            class_name = parts[0]
            confidence = float(parts[1])
            points = [
                (float(parts[2]), float(parts[3])),
                (float(parts[4]), float(parts[5])),
                (float(parts[6]), float(parts[7])),
                (float(parts[8]), float(parts[9]))
            ]
            
            # Draw polygon
            draw.polygon(points, outline='red', width=2)
            
            # Draw label
            label = f"{class_name} {confidence:.2f}"
            draw.text((points[0][0], points[0][1] - 15), label, fill='red')
    
    # Save
    img.save(output_path)
    print(f"Saved to {output_path}")


# Usage
if __name__ == "__main__":
    visualize_single_image(
        "data/images/P0006og.png",
        "predictions/P0006.txt",
        "output/P0006pred.png"
    )
```

### Example 2: Batch Process Directory

```python
#!/usr/bin/env python3
"""Batch process all predictions in a directory."""

from pathlib import Path
from PIL import Image, ImageDraw

def batch_visualize(images_dir, preds_dir, output_dir):
    """Process all predictions in directory."""
    
    images_dir = Path(images_dir)
    preds_dir = Path(preds_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all prediction files
    for pred_file in preds_dir.glob("*.txt"):
        print(f"Processing {pred_file.name}...")
        
        # Find matching image
        image_file = images_dir / (pred_file.stem + "og.png")
        if not image_file.exists():
            image_file = images_dir / (pred_file.stem + ".png")
        
        if not image_file.exists():
            print(f"  ✗ Image not found for {pred_file.name}")
            continue
        
        # Generate output path
        output_file = output_dir / (pred_file.stem + "pred.png")
        
        # Visualize
        try:
            visualize_single_image(image_file, pred_file, output_file)
            print(f"  ✓ Saved to {output_file}")
        except Exception as e:
            print(f"  ✗ Error: {e}")


# Usage
if __name__ == "__main__":
    batch_visualize(
        "data/images/val",
        "predictions/refined",
        "visualizations"
    )
```

### Example 3: With Custom Colors

```python
#!/usr/bin/env python3
"""Visualize with class-specific colors."""

CLASS_COLORS = {
    'large-vehicle': (255, 0, 0),      # Red
    'small-vehicle': (0, 255, 0),      # Green
    'plane': (0, 0, 255),              # Blue
    'ship': (255, 255, 0),             # Yellow
    'harbor': (255, 0, 255),           # Magenta
}

def get_color(class_name):
    """Get color for class, or generate one."""
    if class_name in CLASS_COLORS:
        return CLASS_COLORS[class_name]
    
    # Generate color from hash
    import hashlib
    h = int(hashlib.md5(class_name.encode()).hexdigest(), 16)
    return ((h >> 16) & 0xFF, (h >> 8) & 0xFF, h & 0xFF)


def visualize_with_colors(image_path, pred_path, output_path):
    """Visualize with class-specific colors."""
    from PIL import Image, ImageDraw
    
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    
    with open(pred_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 10:
                continue
            
            class_name = parts[0]
            confidence = float(parts[1])
            points = [(float(parts[i]), float(parts[i+1])) 
                     for i in range(2, 10, 2)]
            
            # Get class color
            color = get_color(class_name)
            
            # Draw with class color
            draw.polygon(points, outline=color, width=2)
            
            label = f"{class_name} {confidence:.2f}"
            draw.text((points[0][0], points[0][1] - 15), 
                     label, fill=color)
    
    img.save(output_path)


# Usage
if __name__ == "__main__":
    visualize_with_colors(
        "data/images/P0006og.png",
        "predictions/P0006.txt",
        "output/P0006pred_colored.png"
    )
```

---

## 3. Code Snippets Library

### Snippet: Parse OBB Format

```python
def parse_obb_line(line):
    """Parse single line of OBB prediction."""
    parts = line.strip().split()
    if len(parts) != 10:
        return None
    
    try:
        return {
            'class_name': parts[0],
            'confidence': float(parts[1]),
            'polygon': [
                (float(parts[2]), float(parts[3])),
                (float(parts[4]), float(parts[5])),
                (float(parts[6]), float(parts[7])),
                (float(parts[8]), float(parts[9]))
            ]
        }
    except (ValueError, IndexError):
        return None
```

### Snippet: Parse YOLO Format

```python
def parse_yolo_line(line, img_width, img_height):
    """Parse YOLO normalized format line."""
    parts = line.strip().split()
    if len(parts) != 6:
        return None
    
    try:
        class_id = int(parts[0])
        cx, cy, w, h = map(float, parts[1:5])
        confidence = float(parts[5])
        
        # Convert to pixel coordinates
        cx_px = cx * img_width
        cy_px = cy * img_height
        w_px = w * img_width
        h_px = h * img_height
        
        return {
            'class_id': class_id,
            'confidence': confidence,
            'bbox': [
                cx_px - w_px/2,  # x_min
                cy_px - h_px/2,  # y_min
                cx_px + w_px/2,  # x_max
                cy_px + h_px/2   # y_max
            ]
        }
    except (ValueError, IndexError):
        return None
```

### Snippet: Draw with Background Label

```python
def draw_label_with_background(draw, position, text, 
                               text_color=(255, 255, 255),
                               bg_color=(0, 0, 0),
                               font=None):
    """Draw text with background rectangle."""
    # Get text size
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

### Snippet: Load Font Safely

```python
def load_font(font_name='arial.ttf', size=14):
    """Load font with fallback to default."""
    from PIL import ImageFont
    
    try:
        return ImageFont.truetype(font_name, size=size)
    except IOError:
        # Try common locations
        import os
        font_paths = [
            f'/usr/share/fonts/truetype/dejavu/{font_name}',
            f'C:\\Windows\\Fonts\\{font_name}',
            f'/System/Library/Fonts/{font_name}',
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size=size)
                except:
                    continue
        
        # Fall back to default
        print(f"Warning: Could not load {font_name}, using default font")
        return ImageFont.load_default()
```

### Snippet: Clip Coordinates to Image Bounds

```python
def clip_to_bounds(coords, img_width, img_height):
    """Clip coordinates to image boundaries."""
    x, y = coords
    x_clipped = max(0, min(x, img_width))
    y_clipped = max(0, min(y, img_height))
    return (x_clipped, y_clipped)


def clip_polygon(polygon, img_width, img_height):
    """Clip all points in polygon."""
    return [clip_to_bounds(pt, img_width, img_height) for pt in polygon]
```

### Snippet: Generate Class Color from Hash

```python
def generate_color_from_name(name):
    """Generate consistent color from string."""
    import hashlib
    
    # Hash the name
    hash_value = int(hashlib.md5(name.encode()).hexdigest(), 16)
    
    # Extract RGB components
    r = (hash_value >> 16) & 0xFF
    g = (hash_value >> 8) & 0xFF
    b = hash_value & 0xFF
    
    return (r, g, b)
```

### Snippet: Adjust Line Width by Image Size

```python
def calculate_line_width(img_width, img_height, base_width=2):
    """Calculate line width based on image size."""
    max_dim = max(img_width, img_height)
    
    if max_dim <= 640:
        return base_width
    elif max_dim <= 1280:
        return int(base_width * 1.5)
    elif max_dim <= 2048:
        return base_width * 2
    else:
        return base_width * 3
```

### Snippet: Format Confidence Score

```python
def format_confidence(confidence, style='standard'):
    """Format confidence score for display."""
    if style == 'standard':
        return f"{confidence:.2f}"
    elif style == 'percentage':
        return f"{confidence*100:.1f}%"
    elif style == 'short':
        return f"{confidence:.1f}"
    elif style == 'verbose':
        return f"Conf: {confidence:.3f}"
    else:
        return f"{confidence:.2f}"


# Examples:
# format_confidence(0.8962, 'standard')    → "0.90"
# format_confidence(0.8962, 'percentage')  → "89.6%"
# format_confidence(0.8962, 'short')       → "0.9"
# format_confidence(0.8962, 'verbose')     → "Conf: 0.896"
```

---

## 4. Configuration Templates

### Template 1: Basic Configuration

```yaml
# visualization_basic.yaml
visualization:
  input_images_dir: data/images/val
  predictions_dir: predictions/refined
  output_dir: visualizations
  
  output_format: png
  output_suffix: pred
  
  bbox_line_width: 2
  label_font_size: 14
  show_confidence: true
```

### Template 2: Advanced Configuration

```yaml
# visualization_advanced.yaml
visualization:
  # Input/Output
  input_images_dir: data/images/val
  predictions_dir: predictions/refined
  output_dir: visualizations
  
  # Output settings
  output_format: png          # png, jpg, jpeg
  output_suffix: pred
  output_quality: 95          # For JPEG (1-100)
  
  # Visual settings
  bbox_line_width: 2
  label_font_size: 14
  label_font_family: arial.ttf
  
  # Label content
  show_confidence: true
  confidence_format: standard  # standard, percentage, short, verbose
  confidence_decimals: 2
  
  # Color scheme
  color_scheme: per_class     # per_class, confidence, fixed
  default_color: [255, 0, 0]  # RGB for 'fixed' scheme
  
  # Filtering
  filter_low_confidence: false
  min_confidence: 0.25
  
  # Performance
  parallel: true
  num_workers: 4
  max_image_size: 4096        # Downsample if larger
  
  # Advanced
  draw_filled_boxes: false    # Fill boxes with transparent color
  fill_alpha: 0.3
  highlight_high_conf: true   # Bold lines for high confidence
  high_conf_threshold: 0.8
```

### Template 3: Class-Specific Colors

```yaml
# visualization_colors.yaml
visualization:
  input_images_dir: data/images/val
  predictions_dir: predictions/refined
  output_dir: visualizations
  
  color_scheme: per_class
  
  class_colors:
    plane: [255, 0, 0]              # Red
    ship: [0, 255, 0]               # Green
    storage-tank: [0, 0, 255]       # Blue
    baseball-diamond: [255, 255, 0] # Yellow
    tennis-court: [255, 0, 255]     # Magenta
    basketball-court: [0, 255, 255] # Cyan
    ground-track-field: [255, 128, 0]   # Orange
    harbor: [128, 0, 255]           # Purple
    bridge: [0, 128, 255]           # Light Blue
    large-vehicle: [255, 128, 128]  # Light Red
    small-vehicle: [128, 255, 128]  # Light Green
    helicopter: [128, 128, 255]     # Light Purple
    roundabout: [192, 192, 0]       # Dark Yellow
    soccer-ball-field: [192, 0, 192]    # Dark Magenta
    swimming-pool: [0, 192, 192]    # Dark Cyan
```

### Template 4: Comparison Mode

```yaml
# visualization_comparison.yaml
visualization:
  mode: comparison
  
  input_images_dir: data/images/val
  predictions_dir: predictions/refined
  ground_truth_dir: data/labels/val
  output_dir: visualizations/comparison
  
  layout: side_by_side  # side_by_side, overlay, grid
  
  labels:
    predictions: "Predictions"
    ground_truth: "Ground Truth"
    original: "Original"
  
  colors:
    predictions: [255, 0, 0]     # Red
    ground_truth: [0, 255, 0]    # Green
```

---

## 5. Common Issues and Solutions

### Issue 1: Font Not Found

**Problem:** `IOError: cannot open resource`

**Solution:**
```python
# Use default font as fallback
from PIL import ImageFont

try:
    font = ImageFont.truetype("arial.ttf", size=14)
except IOError:
    font = ImageFont.load_default()
    print("Using default font")
```

### Issue 2: Image Mode Not RGB

**Problem:** Error when drawing on grayscale or RGBA images

**Solution:**
```python
img = Image.open(image_path)
if img.mode != 'RGB':
    img = img.convert('RGB')
```

### Issue 3: Out of Bounds Coordinates

**Problem:** Coordinates outside image boundaries

**Solution:**
```python
def clip_coords(x, y, img_width, img_height):
    x = max(0, min(x, img_width))
    y = max(0, min(y, img_height))
    return x, y
```

### Issue 4: Empty Prediction File

**Problem:** No detections to visualize

**Solution:**
```python
detections = parse_predictions(pred_file)
if not detections:
    print(f"Warning: No detections in {pred_file}")
    # Save original image or skip
    img.save(output_path)
    return
```

### Issue 5: Large Image Memory Issues

**Problem:** Out of memory when processing large images

**Solution:**
```python
MAX_SIZE = 4096

img = Image.open(image_path)
if max(img.size) > MAX_SIZE:
    scale = MAX_SIZE / max(img.size)
    new_size = (int(img.size[0] * scale), int(img.size[1] * scale))
    img = img.resize(new_size, Image.LANCZOS)
    # Scale coordinates accordingly
```

### Issue 6: Slow Batch Processing

**Problem:** Processing many images takes too long

**Solution:**
```python
from multiprocessing import Pool

def process_parallel(file_list, num_workers=4):
    with Pool(num_workers) as pool:
        pool.map(visualize_single_image, file_list)
```

---

## 6. API Reference

### Core Functions

#### `parse_obb_predictions(pred_file: Path) -> List[Dict]`

Parse OBB format prediction file.

**Parameters:**
- `pred_file`: Path to .txt prediction file

**Returns:**
- List of detection dictionaries with keys:
  - `class_name`: str
  - `confidence`: float
  - `polygon`: List of (x, y) tuples

**Example:**
```python
detections = parse_obb_predictions(Path("predictions/P0006.txt"))
for det in detections:
    print(f"{det['class_name']}: {det['confidence']:.2f}")
```

---

#### `visualize_predictions(image_path, pred_path, output_path, config=None)`

Main visualization function.

**Parameters:**
- `image_path`: Path to input image
- `pred_path`: Path to predictions text file
- `output_path`: Path to save output
- `config`: Optional configuration dict

**Example:**
```python
visualize_predictions(
    "data/images/P0006og.png",
    "predictions/P0006.txt",
    "output/P0006pred.png",
    config={'line_width': 3, 'show_confidence': True}
)
```

---

#### `get_class_color(class_name: str) -> Tuple[int, int, int]`

Get RGB color for a class name.

**Parameters:**
- `class_name`: Name of object class

**Returns:**
- RGB tuple (r, g, b)

**Example:**
```python
color = get_class_color("large-vehicle")  # Returns (255, 0, 0)
```

---

#### `draw_detection(draw, detection, color, font, line_width=2)`

Draw a single detection on the image.

**Parameters:**
- `draw`: PIL ImageDraw object
- `detection`: Detection dictionary
- `color`: RGB tuple
- `font`: PIL ImageFont object
- `line_width`: Width of bounding box lines

**Example:**
```python
from PIL import Image, ImageDraw

img = Image.open("image.png")
draw = ImageDraw.Draw(img)

detection = {
    'class_name': 'vehicle',
    'confidence': 0.95,
    'polygon': [(10, 10), (50, 10), (50, 50), (10, 50)]
}

draw_detection(draw, detection, (255, 0, 0), font)
```

---

### Utility Functions

#### `load_config(config_path: Path) -> Dict`

Load configuration from YAML file.

**Example:**
```python
config = load_config(Path("configs/visualization.yaml"))
```

---

#### `batch_process(images_dir, preds_dir, output_dir, config=None)`

Process all images in a directory.

**Example:**
```python
batch_process(
    "data/images/val",
    "predictions/refined",
    "visualizations"
)
```

---

## Command-Line Usage

### Basic Usage

```bash
# Visualize single image
python -m pipeline.visualize \
    --image data/images/P0006og.png \
    --predictions predictions/P0006.txt \
    --output visualizations/P0006pred.png

# Batch process directory
python -m pipeline.visualize \
    --batch \
    --images-dir data/images/val \
    --predictions-dir predictions/refined \
    --output-dir visualizations

# With configuration file
python -m pipeline.visualize \
    --config configs/visualization.yaml
```

### Advanced Options

```bash
# Custom colors and styling
python -m pipeline.visualize \
    --images-dir data/images/val \
    --predictions-dir predictions/ \
    --output-dir viz/ \
    --line-width 3 \
    --font-size 16 \
    --color-scheme per_class

# Parallel processing
python -m pipeline.visualize \
    --batch \
    --workers 8 \
    --images-dir data/images/val \
    --predictions-dir predictions/ \
    --output-dir viz/

# Filter low confidence
python -m pipeline.visualize \
    --images-dir data/images/val \
    --predictions-dir predictions/ \
    --output-dir viz/ \
    --min-confidence 0.5
```

---

## Performance Tips

1. **Use batch processing with multiprocessing** for large datasets
2. **Cache font objects** to avoid repeated loading
3. **Downsample large images** before visualization
4. **Filter low-confidence detections** to reduce clutter
5. **Use PNG format** for lossless output quality
6. **Process in chunks** if memory is limited

---

## Testing

### Unit Test Template

```python
import unittest
from pathlib import Path
from PIL import Image

class TestVisualization(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_image = Path("test_data/test_image.png")
        self.test_pred = Path("test_data/test_pred.txt")
        self.output = Path("test_output/result.png")
    
    def test_parse_predictions(self):
        """Test prediction parsing."""
        detections = parse_obb_predictions(self.test_pred)
        self.assertIsInstance(detections, list)
        self.assertGreater(len(detections), 0)
    
    def test_visualize(self):
        """Test visualization creates output."""
        visualize_predictions(
            self.test_image,
            self.test_pred,
            self.output
        )
        self.assertTrue(self.output.exists())
    
    def tearDown(self):
        """Clean up test outputs."""
        if self.output.exists():
            self.output.unlink()


if __name__ == '__main__':
    unittest.main()
```

---

## Additional Resources

- **Main Design Document:** `visualization_logic_design.md`
- **Workflow Diagrams:** `visualization_workflow.md`
- **Color Schemes:** `visualization_color_schemes.md`
- **PIL Documentation:** https://pillow.readthedocs.io/
- **YOLO Format:** https://docs.ultralytics.com/

---

## Support and Feedback

For issues or feature requests, please refer to the main project repository documentation or contact the development team.
