# Results Components

This directory contains components for visualizing detection results.

## Components

### ResultsViewer
Main component that orchestrates the results display with tabs, filtering, and statistics.

**Features:**
- Tab navigation: Input, Labels, Output, Compare
- Image navigation (previous/next)
- Loading and error states
- Resizable panel layout

**Props:** None (uses Redux state)

### FilterControls
Filter controls for detections.

**Features:**
- Multi-select class filter
- Confidence range slider (min/max)
- Show labels toggle
- Show confidence toggle
- Reset filters button

**Props:** None (uses Redux state)

### ImageCanvas
Interactive canvas for displaying images with detection overlays.

**Features:**
- Zoom controls (+/-, reset)
- Pan with mouse drag
- Bounding box overlays
- Click to select detections
- View mode dependent rendering

**Props:**
- `imageUrl: string` - Image URL to display
- `viewMode: 'input' | 'labels' | 'output' | 'compare'` - Current view mode
- `showLabels?: boolean` - Show class labels (default: true)
- `showConfidence?: boolean` - Show confidence scores (default: true)

### InfoPanel
Sidebar panel showing details of the selected detection.

**Features:**
- Class name and confidence
- Bounding box coordinates
- Area and aspect ratio
- Pipeline stages visualization

**Props:** None (uses Redux state)

### DetectionStats
Statistics footer displaying aggregate detection information.

**Features:**
- Total detections count
- Number of unique classes
- Average confidence score
- Top 5 classes breakdown

**Props:** None (uses Redux state)

## Usage

```tsx
import ResultsPanel from './components/ResultsPanel';

// In AppShell or parent component
<ResultsPanel />
```

The ResultsPanel internally uses ResultsViewer, which manages all sub-components.

## Redux State

All components connect to `resultsSlice`:

```typescript
{
  results: DetectionResult[];
  currentImageIndex: number;
  selectedDetectionIds: string[];
  filters: {
    classIds: number[];
    minConfidence: number;
    maxConfidence: number;
  };
  isLoading: boolean;
  error: string | null;
}
```

## Actions

- `nextImage()` / `previousImage()` - Navigate images
- `setCurrentImageIndex(index)` - Jump to specific image
- `updateFilters(filters)` - Update filter criteria
- `resetFilters()` - Reset filters to defaults
- `toggleDetectionSelection(id)` - Toggle detection selection
- `clearSelection()` - Clear all selections

## Styling

Components use Material-UI `sx` prop for styling:
- Dark/light theme support via ThemeProvider
- Responsive layout with flexbox
- Consistent spacing using theme units
- Color scheme following design guidelines
