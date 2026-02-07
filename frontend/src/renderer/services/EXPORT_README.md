# Export Functionality

This document describes the export functionality implemented for the Neurosymbolic Object Detection application.

## Overview

The export functionality allows users to save detection results in multiple formats:
- **Annotated Images**: Export images with bounding boxes, labels, and confidence scores
- **Detection Metrics**: Export detection data and statistics in structured formats

## Features

### Image Export

Export annotated images with customizable overlays:

- **Formats**: PNG (lossless) or JPG (compressed)
- **Options**:
  - Include/exclude bounding boxes
  - Include/exclude class labels
  - Include/exclude confidence scores
  - Export single or all images

**Use Cases**:
- Share annotated results with team members
- Create visual reports
- Archive detection outputs
- Generate training data for review

### Metrics Export

Export detection metrics in structured data formats:

- **CSV Format**:
  - Per-detection rows with all attributes
  - Columns: Image Name, Detection ID, Class ID, Class Name, Confidence, Bounding Box coordinates, Processing Time, Timestamp
  - Easy to import into Excel, Google Sheets, or data analysis tools

- **JSON Format**:
  - Complete detection data structure
  - Nested format preserving relationships
  - Machine-readable for automated processing
  - Includes aggregated statistics

**Use Cases**:
- Statistical analysis of detection performance
- Integration with other tools and pipelines
- Model evaluation and comparison
- Data archival and backup

## User Guide

### How to Export

1. **Run Detection**: Upload images and run object detection
2. **View Results**: Navigate to the Results Viewer to see detections
3. **Click Export**: Click the "Export" button in the navigation bar
4. **Configure Options**: Choose export type, format, and options
5. **Confirm Download**: Files will be downloaded to your browser's default download location
6. **Export**: Click "Export" to start the export process

### Export Dialog Options

#### Export Type

- **Annotated Images**: Export images with visual overlays
- **Detection Metrics**: Export detection data as CSV or JSON

#### Format Selection

For **Images**:
- **PNG**: Lossless compression, larger file size, best quality
- **JPG**: Lossy compression, smaller file size, good quality

For **Metrics**:
- **CSV**: Tabular format, easy to open in spreadsheet applications
- **JSON**: Structured format, ideal for programmatic processing

#### Display Options (Images Only)

- **Include bounding boxes**: Draw detection boxes on the image
- **Include class labels**: Show class names above bounding boxes
- **Include confidence scores**: Show confidence percentages with labels

#### Batch Export (Images Only)

- **Export current image**: Export only the currently viewed image
- **Export all images**: Export all processed images in sequence

### Progress Tracking

When exporting multiple images:
- Progress bar shows completion percentage
- File count displays current/total (e.g., "3 / 10")
- Current filename being exported is displayed
- Exports run to completion once started (cancellation is not supported in the current version)

## Technical Details

### File Naming Conventions

**Images**:
```
original_filename_annotated.png
original_filename_annotated.jpg
```

**Metrics**:
```
detections.csv (default, can be changed)
detections.json (default, can be changed)
```

### Export Formats

#### CSV Structure

```csv
Image Name,Detection ID,Class ID,Class Name,Confidence,BBox X,BBox Y,BBox Width,BBox Height,Processing Time (ms),Timestamp
"image1.jpg","det-001",0,"car",0.9543,120.50,80.25,200.00,150.00,1234,2026-02-07T12:00:00.000Z
"image1.jpg","det-002",1,"person",0.8876,350.00,100.00,80.00,180.00,1234,2026-02-07T12:00:00.000Z
```

**Columns**:
- `Image Name`: Original image filename
- `Detection ID`: Unique identifier for the detection
- `Class ID`: Numeric class identifier
- `Class Name`: Human-readable class name
- `Confidence`: Detection confidence score (0-1)
- `BBox X`: Bounding box top-left X coordinate
- `BBox Y`: Bounding box top-left Y coordinate
- `BBox Width`: Bounding box width
- `BBox Height`: Bounding box height
- `Processing Time (ms)`: Time taken to process the image
- `Timestamp`: ISO 8601 timestamp of detection

#### JSON Structure

```json
[
  {
    "imageId": "img-001",
    "imageName": "image1.jpg",
    "imagePath": "/path/to/image1.jpg",
    "detections": [
      {
        "id": "det-001",
        "classId": 0,
        "className": "car",
        "confidence": 0.9543,
        "bbox": {
          "x": 120.5,
          "y": 80.25,
          "width": 200,
          "height": 150
        }
      }
    ],
    "metadata": {
      "processingTime": 1234,
      "totalDetections": 2,
      "timestamp": "2026-02-07T12:00:00.000Z"
    }
  }
]
```

**Fields**:
- `imageId`: Unique identifier for the image
- `imageName`: Original filename
- `imagePath`: Full path to the image
- `detections`: Array of detection objects
  - `id`: Unique detection identifier
  - `classId`: Numeric class ID
  - `className`: Class name
  - `confidence`: Confidence score
  - `bbox`: Bounding box coordinates object
- `metadata`: Image-level metadata
  - `processingTime`: Processing time in milliseconds
  - `totalDetections`: Total number of detections
  - `timestamp`: ISO 8601 timestamp

### Color Scheme

Bounding boxes use a consistent color scheme that matches the ImageCanvas viewer:

1. Red (#FF6B6B)
2. Teal (#4ECDC4)
3. Blue (#45B7D1)
4. Light Salmon (#FFA07A)
5. Mint (#98D8C8)
6. Yellow (#F7DC6F)
7. Purple (#BB8FCE)
8. Sky Blue (#85C1E2)
9. Orange (#F8B739)
10. Green (#52B788)

Colors are assigned by class ID using modulo operation.

### Image Rendering

Images are rendered using HTML5 Canvas API:
1. Load the original image
2. Draw image on canvas
3. Optionally draw bounding boxes with class colors
4. Optionally draw labels with background
5. Convert canvas to Blob
6. Trigger browser download

**Quality Settings**:
- PNG: Lossless, no quality parameter
- JPG: 95% quality (0.95 parameter)

## Implementation Details

### Components

**ExportService.ts**:
- Core export logic
- Canvas-based image rendering
- CSV/JSON data formatting
- Batch export orchestration

**ExportDialog.tsx**:
- Material-UI dialog component
- Export configuration interface
- Progress tracking display
- Error handling

**Electron IPC Handlers** (main.ts):
- `dialog:saveFile` - Generic save dialog
- `dialog:saveImage` - Image-specific save dialog
- `dialog:saveCSV` - CSV save dialog
- `dialog:saveJSON` - JSON save dialog

### Dependencies

- **Material-UI**: Dialog, buttons, progress indicators
- **Electron**: Native file save dialogs
- **HTML5 Canvas**: Image rendering
- **React**: Component framework

### Browser Compatibility

The export functionality uses standard web APIs:
- Canvas API (widely supported)
- Blob API (all modern browsers)
- Download attribute (all modern browsers)

## Troubleshooting

### Images Won't Export

**Problem**: Export button is disabled or export fails

**Solutions**:
- Ensure images have been processed (run detection first)
- Check that the ResultsViewer shows detections
- Verify browser console for errors
- Try exporting a single image first

### Large File Sizes

**Problem**: Exported images are too large

**Solutions**:
- Use JPG format instead of PNG (smaller file size)
- Reduce image resolution before upload
- Export without overlays if annotations aren't needed

### CSV/JSON Format Issues

**Problem**: Exported files have incorrect format

**Solutions**:
- Open CSV files with UTF-8 encoding
- Validate JSON files with online validators
- Check for special characters in image filenames
- Ensure consistent timestamp formats

### Batch Export Interrupted

**Problem**: Batch export stops midway

**Solutions**:
- Check available disk space
- Close other memory-intensive applications
- Export in smaller batches
- Check browser console for error messages

## Future Enhancements

Potential improvements for future versions:

1. **PDF Export**: Generate PDF reports with images and statistics
2. **Export Presets**: Save and load export configurations
3. **Export History**: Track previously exported files
4. **Cloud Upload**: Direct export to cloud storage (S3, Google Drive)
5. **Compression Options**: Adjustable quality settings for JPG
6. **Bulk Naming**: Custom naming patterns for batch exports
7. **Format Templates**: Customizable CSV/JSON templates
8. **Export Scheduler**: Automated periodic exports

## API Reference

### ExportService Functions

#### exportToCSV(results, singleFile)
Converts detection results to CSV format.

**Parameters**:
- `results`: Array of DetectionResult objects
- `singleFile`: Boolean (not currently used, reserved for future)

**Returns**: String (CSV content)

#### exportToJSON(results)
Converts detection results to JSON format.

**Parameters**:
- `results`: Array of DetectionResult objects

**Returns**: String (JSON content)

#### exportMetricsToJSON(results)
Generates aggregated metrics in JSON format.

**Parameters**:
- `results`: Array of DetectionResult objects

**Returns**: String (JSON content with statistics)

#### exportMetricsToCSV(results)
Generates class-wise statistics in CSV format.

**Parameters**:
- `results`: Array of DetectionResult objects

**Returns**: String (CSV content with statistics)

#### exportImageWithDetections(imageUrl, detections, options, canvas)
Renders detections on image and exports as Blob.

**Parameters**:
- `imageUrl`: String (image source URL)
- `detections`: Array of Detection objects
- `options`: ExportOptions object
- `canvas`: HTMLCanvasElement

**Returns**: Promise<Blob>

#### batchExportImages(results, options, onProgress)
Exports multiple images with progress tracking.

**Parameters**:
- `results`: Array of DetectionResult objects
- `options`: ExportOptions object
- `onProgress`: Optional callback function

**Returns**: Promise<void>

### TypeScript Interfaces

```typescript
type ExportFormat = 'jpg' | 'png' | 'csv' | 'json';

interface ExportOptions {
  format: ExportFormat;
  includeOverlays?: boolean;
  includeLabels?: boolean;
  includeConfidence?: boolean;
  singleFile?: boolean;
}

interface ExportProgress {
  current: number;
  total: number;
  fileName: string;
  completed: boolean;
  error?: string;
}
```

## Support

For issues or questions about export functionality:
1. Check this documentation
2. Review the Troubleshooting section
3. Check browser console for errors
4. Open an issue on GitHub with:
   - Steps to reproduce
   - Expected vs. actual behavior
   - Browser and OS information
   - Console error messages (if any)

## License

This export functionality is part of the Neurosymbolic Object Detection project and follows the project's license terms.
