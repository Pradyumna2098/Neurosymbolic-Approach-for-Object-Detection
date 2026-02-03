# Visualization Color Schemes and Output Conventions

## Overview

This document specifies color palettes, visual styling conventions, and output file organization for the bounding box visualization system. It ensures consistent, professional-looking visualizations across the project.

---

## Table of Contents

1. [Color Palettes](#color-palettes)
2. [Class-to-Color Mapping](#class-to-color-mapping)
3. [Confidence-Based Styling](#confidence-based-styling)
4. [Output File Conventions](#output-file-conventions)
5. [Directory Organization](#directory-organization)
6. [Metadata and Documentation](#metadata-and-documentation)
7. [Visual Style Guidelines](#visual-style-guidelines)

---

## 1. Color Palettes

### Primary Palette: DOTA Dataset Classes

Optimized for the 15 classes in the DOTA (Dataset for Object detection in Aerial images) dataset.

| Class Name             | RGB Color       | Hex Code | Visual |
|------------------------|-----------------|----------|--------|
| plane                  | (255, 0, 0)     | #FF0000  | 🟥 Red |
| ship                   | (0, 255, 0)     | #00FF00  | 🟩 Green |
| storage-tank           | (0, 0, 255)     | #0000FF  | 🟦 Blue |
| baseball-diamond       | (255, 255, 0)   | #FFFF00  | 🟨 Yellow |
| tennis-court           | (255, 0, 255)   | #FF00FF  | 🟪 Magenta |
| basketball-court       | (0, 255, 255)   | #00FFFF  | 🔵 Cyan |
| ground-track-field     | (255, 128, 0)   | #FF8000  | 🟧 Orange |
| harbor                 | (128, 0, 255)   | #8000FF  | 🟣 Purple |
| bridge                 | (0, 128, 255)   | #0080FF  | 🔷 Light Blue |
| large-vehicle          | (255, 128, 128) | #FF8080  | 🔴 Light Red |
| small-vehicle          | (128, 255, 128) | #80FF80  | 🟢 Light Green |
| helicopter             | (128, 128, 255) | #8080FF  | 🔵 Light Purple |
| roundabout             | (192, 192, 0)   | #C0C000  | 🟡 Dark Yellow |
| soccer-ball-field      | (192, 0, 192)   | #C000C0  | 🟣 Dark Magenta |
| swimming-pool          | (0, 192, 192)   | #00C0C0  | 🔷 Dark Cyan |

**Color Selection Rationale:**
- **High Contrast:** Colors are maximally separated in RGB space
- **Distinguishable:** Easy to differentiate even for color-blind users
- **Consistent:** Same class always gets the same color across visualizations

### Alternative Palette 1: Pastel Colors

Suitable for presentations, reports, or less cluttered scenes.

| Class Type      | RGB Color       | Hex Code | Use Case |
|-----------------|-----------------|----------|----------|
| Vehicle         | (255, 200, 200) | #FFC8C8  | Subtle visualization |
| Building        | (200, 255, 200) | #C8FFC8  | Clean presentations |
| Infrastructure  | (200, 200, 255) | #C8C8FF  | Report generation |
| Sport Field     | (255, 255, 200) | #FFFFC8  | Academic papers |
| Water Feature   | (200, 255, 255) | #C8FFFF  | Light backgrounds |

### Alternative Palette 2: High Visibility

For dense scenes with many overlapping objects.

| Priority Level  | RGB Color       | Hex Code | Purpose |
|-----------------|-----------------|----------|---------|
| Critical        | (255, 0, 0)     | #FF0000  | Emergency vehicles |
| High            | (255, 128, 0)   | #FF8000  | Large objects |
| Medium          | (255, 255, 0)   | #FFFF00  | Standard detection |
| Low             | (128, 255, 128) | #80FF80  | Background objects |

### Color Generation Algorithm

For classes not in predefined palette:

```python
import hashlib

def generate_color(class_name: str) -> tuple[int, int, int]:
    """
    Generate a deterministic color from class name.
    
    Uses MD5 hash to ensure:
    - Same name always produces same color
    - Distribution across RGB space
    - Reproducible across systems
    
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
```

---

## 2. Class-to-Color Mapping

### Implementation

```python
# Standard color mapping for DOTA classes
CLASS_COLORS = {
    'plane': (255, 0, 0),
    'ship': (0, 255, 0),
    'storage-tank': (0, 0, 255),
    'baseball-diamond': (255, 255, 0),
    'tennis-court': (255, 0, 255),
    'basketball-court': (0, 255, 255),
    'ground-track-field': (255, 128, 0),
    'harbor': (128, 0, 255),
    'bridge': (0, 128, 255),
    'large-vehicle': (255, 128, 128),
    'small-vehicle': (128, 255, 128),
    'helicopter': (128, 128, 255),
    'roundabout': (192, 192, 0),
    'soccer-ball-field': (192, 0, 192),
    'swimming-pool': (0, 192, 192),
}

def get_class_color(class_name: str, 
                   palette: dict = None) -> tuple[int, int, int]:
    """
    Get color for a class name.
    
    Args:
        class_name: Name of object class
        palette: Optional custom color palette
    
    Returns:
        RGB tuple (r, g, b)
    """
    if palette is None:
        palette = CLASS_COLORS
    
    # Normalize class name (handle variations)
    normalized = class_name.lower().replace('_', '-')
    
    if normalized in palette:
        return palette[normalized]
    else:
        # Generate deterministic color
        return generate_color(class_name)
```

### Color Consistency Rules

1. **Same class = Same color** across all visualizations
2. **Persistent mapping** saved to configuration files
3. **User customizable** via YAML configuration
4. **Fallback generation** for unknown classes

---

## 3. Confidence-Based Styling

### Approach 1: Line Width Variation

Vary line thickness based on confidence level.

```python
def get_line_width(confidence: float, 
                   base_width: int = 2) -> int:
    """
    Calculate line width based on confidence.
    
    High confidence = Thicker lines
    Low confidence = Thinner lines
    
    Args:
        confidence: Detection confidence (0.0 to 1.0)
        base_width: Base line width
    
    Returns:
        Line width in pixels
    """
    if confidence >= 0.9:
        return base_width * 2      # Very confident
    elif confidence >= 0.7:
        return base_width          # Confident
    elif confidence >= 0.5:
        return max(1, base_width - 1)  # Moderately confident
    else:
        return 1                   # Low confidence
```

### Approach 2: Color Intensity

Modulate color intensity based on confidence.

```python
def adjust_color_by_confidence(base_color: tuple[int, int, int],
                               confidence: float) -> tuple[int, int, int]:
    """
    Adjust color intensity based on confidence.
    
    High confidence = Full color saturation
    Low confidence = Faded/desaturated color
    
    Args:
        base_color: Base RGB color
        confidence: Detection confidence (0.0 to 1.0)
    
    Returns:
        Adjusted RGB color
    """
    r, g, b = base_color
    
    # Blend with white based on confidence
    # confidence=1.0: full color
    # confidence=0.0: white
    alpha = confidence
    
    r_adj = int(r * alpha + 255 * (1 - alpha))
    g_adj = int(g * alpha + 255 * (1 - alpha))
    b_adj = int(b * alpha + 255 * (1 - alpha))
    
    return (r_adj, g_adj, b_adj)
```

### Approach 3: Dashed Lines

Use dashed lines for low-confidence detections.

```python
def draw_bbox_with_confidence(draw, bbox, confidence, color):
    """
    Draw bounding box with style based on confidence.
    
    High confidence: Solid lines
    Low confidence: Dashed lines
    
    Args:
        draw: PIL ImageDraw object
        bbox: Bounding box coordinates
        confidence: Detection confidence
        color: RGB color tuple
    """
    if confidence >= 0.7:
        # Solid line for high confidence
        draw.rectangle(bbox, outline=color, width=2)
    else:
        # Dashed line for low confidence
        x1, y1, x2, y2 = bbox
        dash_length = 10
        gap_length = 5
        
        # Draw dashed rectangle
        # Top edge
        draw_dashed_line(draw, (x1, y1), (x2, y1), color, dash_length, gap_length)
        # Right edge
        draw_dashed_line(draw, (x2, y1), (x2, y2), color, dash_length, gap_length)
        # Bottom edge
        draw_dashed_line(draw, (x2, y2), (x1, y2), color, dash_length, gap_length)
        # Left edge
        draw_dashed_line(draw, (x1, y2), (x1, y1), color, dash_length, gap_length)
```

### Confidence Threshold Visualization

```python
CONFIDENCE_LEVELS = {
    'very_high': (0.9, 1.0),   # Solid, thick lines
    'high': (0.7, 0.9),        # Solid, normal lines
    'medium': (0.5, 0.7),      # Solid, thin lines
    'low': (0.25, 0.5),        # Dashed lines
    'very_low': (0.0, 0.25),   # Dotted lines or filter out
}

def get_confidence_style(confidence: float) -> dict:
    """
    Get visualization style based on confidence level.
    
    Returns:
        Dictionary with styling parameters
    """
    if confidence >= 0.9:
        return {
            'line_width': 3,
            'line_style': 'solid',
            'color_intensity': 1.0,
            'label_bold': True
        }
    elif confidence >= 0.7:
        return {
            'line_width': 2,
            'line_style': 'solid',
            'color_intensity': 1.0,
            'label_bold': False
        }
    elif confidence >= 0.5:
        return {
            'line_width': 1,
            'line_style': 'solid',
            'color_intensity': 0.8,
            'label_bold': False
        }
    else:
        return {
            'line_width': 1,
            'line_style': 'dashed',
            'color_intensity': 0.6,
            'label_bold': False
        }
```

---

## 4. Output File Conventions

### File Naming Patterns

#### Pattern 1: Standard Suffix

```
<input_stem><suffix>.<extension>

Examples:
- P0006pred.png        # Predictions visualized
- P0006gt.png          # Ground truth visualized
- P0006compare.png     # Side-by-side comparison
```

#### Pattern 2: Stage Indicator

```
<input_stem>_<stage><suffix>.<extension>

Examples:
- P0006_raw_pred.png       # Raw predictions
- P0006_nms_pred.png       # After NMS filtering
- P0006_refined_pred.png   # After symbolic reasoning
```

#### Pattern 3: Timestamp

```
<input_stem>_<timestamp><suffix>.<extension>

Examples:
- P0006_20240115_103045_pred.png   # With date-time
- P0006_v1_pred.png                 # Version number
```

### Suffix Definitions

| Suffix      | Description                          | Use Case |
|-------------|--------------------------------------|----------|
| `pred`      | Predictions only                     | Standard output |
| `gt`        | Ground truth annotations             | Validation |
| `compare`   | Side-by-side comparison              | Analysis |
| `overlay`   | Predictions overlaid on original     | Presentation |
| `annotated` | Full annotations with metadata       | Documentation |
| `debug`     | Debug visualization with extra info  | Development |

### Implementation

```python
from pathlib import Path
from datetime import datetime

def generate_output_filename(input_path: Path,
                            suffix: str = 'pred',
                            add_timestamp: bool = False,
                            extension: str = 'png') -> str:
    """
    Generate standardized output filename.
    
    Args:
        input_path: Path to input image
        suffix: Output type suffix
        add_timestamp: Include timestamp in filename
        extension: Output file extension
    
    Returns:
        Output filename string
    """
    stem = input_path.stem
    
    # Remove common input suffixes if present
    for input_suffix in ['og', 'original', 'input']:
        if stem.endswith(input_suffix):
            stem = stem[:-len(input_suffix)]
    
    # Build output filename
    parts = [stem]
    
    if add_timestamp:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        parts.append(timestamp)
    
    parts.append(suffix)
    
    filename = ''.join(parts) + '.' + extension
    return filename


# Examples:
# generate_output_filename(Path("P0006og.png"))
# → "P0006pred.png"

# generate_output_filename(Path("P0006.png"), suffix='compare')
# → "P0006compare.png"

# generate_output_filename(Path("P0006.png"), add_timestamp=True)
# → "P0006_20240115_103045pred.png"
```

---

## 5. Directory Organization

### Standard Directory Structure

```
project_root/
├── data/
│   └── images/
│       ├── train/           # Training images
│       ├── val/             # Validation images
│       │   ├── P0001og.png
│       │   ├── P0002og.png
│       │   └── ...
│       └── test/            # Test images
│
├── predictions/
│   ├── raw/                 # Raw model predictions
│   │   ├── P0001.txt
│   │   ├── P0002.txt
│   │   └── ...
│   ├── nms/                 # After NMS filtering
│   └── refined/             # After symbolic reasoning
│
└── visualizations/
    ├── raw/                 # Raw predictions visualized
    │   ├── P0001pred.png
    │   ├── P0002pred.png
    │   └── ...
    ├── nms/                 # NMS predictions visualized
    ├── refined/             # Refined predictions visualized
    ├── ground_truth/        # Ground truth visualized
    ├── comparison/          # Side-by-side comparisons
    │   ├── P0001compare.png
    │   └── ...
    └── reports/             # Generated reports
        ├── summary.html
        └── metadata.json
```

### Directory Creation

```python
from pathlib import Path

def setup_output_directories(base_dir: Path,
                            stages: list[str] = None) -> dict[str, Path]:
    """
    Create standardized output directory structure.
    
    Args:
        base_dir: Base output directory
        stages: List of pipeline stages to create dirs for
    
    Returns:
        Dictionary mapping stage names to paths
    """
    if stages is None:
        stages = ['raw', 'nms', 'refined', 'ground_truth', 'comparison']
    
    directories = {}
    
    for stage in stages:
        stage_dir = base_dir / stage
        stage_dir.mkdir(parents=True, exist_ok=True)
        directories[stage] = stage_dir
    
    # Create reports directory
    reports_dir = base_dir / 'reports'
    reports_dir.mkdir(exist_ok=True)
    directories['reports'] = reports_dir
    
    return directories


# Usage:
# dirs = setup_output_directories(Path("visualizations"))
# # Creates: visualizations/raw/, visualizations/nms/, etc.
```

---

## 6. Metadata and Documentation

### Visualization Metadata Format

For each visualized image, generate a JSON metadata file.

```json
{
  "visualization_metadata": {
    "image_name": "P0006pred.png",
    "source_image": "P0006og.png",
    "prediction_file": "P0006.txt",
    "timestamp": "2024-01-15T10:30:45Z",
    "pipeline_stage": "refined",
    
    "detections": {
      "total_count": 149,
      "class_distribution": {
        "large_vehicle": 147,
        "small_vehicle": 2
      },
      "confidence_stats": {
        "min": 0.5334,
        "max": 0.8962,
        "mean": 0.8521,
        "median": 0.8650
      }
    },
    
    "visualization_config": {
      "color_scheme": "per_class",
      "bbox_line_width": 2,
      "label_font_size": 14,
      "show_confidence": true,
      "confidence_format": "standard"
    },
    
    "image_properties": {
      "width": 2048,
      "height": 2048,
      "format": "PNG",
      "size_bytes": 1016691
    }
  }
}
```

### Batch Summary Report

After batch processing, generate a summary report.

```json
{
  "batch_summary": {
    "timestamp": "2024-01-15T10:35:00Z",
    "total_images": 500,
    "processed_successfully": 498,
    "failed": 2,
    "processing_time_seconds": 125.3,
    
    "aggregate_stats": {
      "total_detections": 74850,
      "avg_detections_per_image": 150.3,
      "class_distribution": {
        "large_vehicle": 68000,
        "small_vehicle": 4200,
        "plane": 1800,
        "ship": 850
      },
      "confidence_distribution": {
        "0.9-1.0": 28000,
        "0.8-0.9": 35000,
        "0.7-0.8": 9000,
        "0.5-0.7": 2850
      }
    },
    
    "output_locations": {
      "visualizations": "visualizations/refined/",
      "metadata": "visualizations/reports/metadata/",
      "summary_report": "visualizations/reports/summary.json"
    }
  }
}
```

---

## 7. Visual Style Guidelines

### Bounding Box Styling

#### Standard Style

```python
STANDARD_STYLE = {
    'bbox': {
        'line_width': 2,
        'line_color': 'class_color',  # Based on class
        'fill': None,                 # No fill
    },
    'label': {
        'font_size': 14,
        'font_family': 'Arial',
        'text_color': 'class_color',
        'background_color': (0, 0, 0),
        'background_alpha': 0.7,
        'padding': 3,
    }
}
```

#### High-Quality Publication Style

```python
PUBLICATION_STYLE = {
    'bbox': {
        'line_width': 3,
        'line_color': 'class_color',
        'line_style': 'solid',
    },
    'label': {
        'font_size': 16,
        'font_family': 'Arial Bold',
        'text_color': (255, 255, 255),
        'background_color': 'class_color',
        'background_alpha': 0.8,
        'padding': 5,
        'rounded_corners': True,
    },
    'output': {
        'dpi': 300,
        'format': 'PNG',
        'quality': 100,
    }
}
```

#### Minimal Style (for cluttered scenes)

```python
MINIMAL_STYLE = {
    'bbox': {
        'line_width': 1,
        'line_color': 'class_color',
        'line_style': 'solid',
    },
    'label': {
        'show': False,  # No labels
    }
}
```

### Label Formatting Standards

#### Standard Format

```
<class_name> <confidence>

Examples:
- "large_vehicle 0.89"
- "plane 0.95"
```

#### Compact Format (for dense scenes)

```
<class_abbrev> <conf>

Examples:
- "LV 0.89"  (Large Vehicle)
- "SV 0.85"  (Small Vehicle)
- "PL 0.95"  (Plane)
```

#### Verbose Format (for analysis)

```
<class_name>
Confidence: <confidence>
ID: <detection_id>

Examples:
large_vehicle
Confidence: 0.896
ID: 42
```

### Size Adaptation

```python
def adapt_style_to_image_size(img_width: int, 
                              img_height: int) -> dict:
    """
    Adapt visual style based on image dimensions.
    
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
```

---

## Summary

This document establishes:

1. **Color Palettes**: Standardized colors for DOTA classes and alternatives
2. **Confidence Styling**: Visual indicators for detection confidence
3. **Output Conventions**: Consistent file naming and directory organization
4. **Metadata Standards**: JSON format for tracking visualizations
5. **Style Guidelines**: Professional, adaptable visual styling

These conventions ensure:
- **Consistency** across all visualizations
- **Professional appearance** suitable for publications
- **Easy interpretation** of detection results
- **Reproducibility** of visual outputs

---

## Implementation Checklist

When implementing visualization:

- [ ] Use standard DOTA color palette
- [ ] Support confidence-based styling
- [ ] Follow file naming conventions
- [ ] Create standard directory structure
- [ ] Generate metadata JSON files
- [ ] Adapt style to image size
- [ ] Allow user customization via config
- [ ] Document custom color mappings
- [ ] Generate batch summary reports
- [ ] Support multiple output formats (PNG, JPEG)

---

## References

- Color theory for data visualization: [ColorBrewer](https://colorbrewer2.org/)
- Accessibility guidelines: [WCAG 2.1](https://www.w3.org/WAI/WCAG21/quickref/)
- PIL/Pillow documentation: https://pillow.readthedocs.io/
- DOTA dataset paper: https://arxiv.org/abs/1711.10398
