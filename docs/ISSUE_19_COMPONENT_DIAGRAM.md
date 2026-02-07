# ImageCanvas Component Architecture

## Component Hierarchy

```
ResultsViewer
├── Tabs (Input/Labels/Output/Compare)
├── FilterControls
├── PanelGroup (Resizable Layout)
│   ├── Panel (Image Canvas Area)
│   │   └── ImageCanvas ⭐ NEW
│   │       ├── Stage (Konva)
│   │       │   └── Layer
│   │       │       ├── KonvaImage (base image)
│   │       │       └── BoundingBox[] (detections) ⭐ NEW
│   │       │           ├── Group
│   │       │           ├── Rect (bounding box)
│   │       │           └── Label (Rect + Text)
│   │       └── ZoomControls (UI Overlay)
│   │           ├── ZoomIn Button
│   │           ├── Reset Button
│   │           ├── ZoomOut Button
│   │           └── Zoom Percentage
│   └── Panel (Info Sidebar)
│       └── InfoPanel
└── DetectionStats
```

## Data Flow

```
Redux Store
  ├── results.results[currentImageIndex]
  │   ├── imagePath → ImageCanvas.imageUrl
  │   └── detections[] → BoundingBox[]
  ├── results.filters
  │   ├── classIds → filter detections
  │   ├── minConfidence → filter detections
  │   ├── maxConfidence → filter detections
  │   ├── showLabels → BoundingBox.showLabels
  │   └── showConfidence → BoundingBox.showConfidence
  └── results.selectedDetectionIds
      └── BoundingBox.isSelected

User Interactions
  ├── Mouse Wheel → zoom (pointer-based)
  ├── Click + Drag → pan
  ├── Hover Box → setHoveredDetectionId
  └── Click Box → dispatch(toggleDetectionSelection)
```

## State Management

### Local State (ImageCanvas)
```typescript
const [zoom, setZoom] = useState(1);
const [position, setPosition] = useState({ x: 0, y: 0 });
const [hoveredDetectionId, setHoveredDetectionId] = useState<string | null>(null);
const [stageDimensions, setStageDimensions] = useState({ width: 800, height: 600 });
```

### Redux State (Consumed)
```typescript
const results = useAppSelector(state => state.results.results);
const currentImageIndex = useAppSelector(state => state.results.currentImageIndex);
const filters = useAppSelector(state => state.results.filters);
const selectedDetectionIds = useAppSelector(state => state.results.selectedDetectionIds);
```

### Redux Actions (Dispatched)
```typescript
dispatch(toggleDetectionSelection(detectionId));
```

## Event Handlers

### ImageCanvas Events
- `handleWheel(e)` - Mouse wheel zoom with pointer tracking
- `handleZoomIn()` - Increase zoom by 25%
- `handleZoomOut()` - Decrease zoom by 25%
- `handleZoomReset()` - Reset to auto-fit zoom
- `handleDetectionClick(id)` - Toggle detection selection
- `handleDetectionMouseEnter(id)` - Set hovered state
- `handleDetectionMouseLeave()` - Clear hovered state

### Konva Stage Events
- `onWheel` → handleWheel
- `draggable={true}` → built-in pan
- `onDragEnd` → update position state

### BoundingBox Events
- `onClick` → handleDetectionClick
- `onMouseEnter` → handleDetectionMouseEnter
- `onMouseLeave` → handleDetectionMouseLeave

## Props Interface

### ImageCanvas Props
```typescript
interface ImageCanvasProps {
  imageUrl: string;                    // Path to image file
  viewMode: 'input' | 'labels' | 'output' | 'compare';
  showLabels?: boolean;                // Default: true
  showConfidence?: boolean;            // Default: true
}
```

### BoundingBox Props
```typescript
interface BoundingBoxProps {
  detection: Detection;                // Full detection object
  isSelected: boolean;                 // Selection state
  isHovered: boolean;                  // Hover state
  showLabels: boolean;                 // Display class name
  showConfidence: boolean;             // Display confidence %
  onClick: () => void;                 // Selection handler
  onMouseEnter: () => void;            // Hover enter handler
  onMouseLeave: () => void;            // Hover leave handler
}
```

## Detection Interface (from types/index.ts)

```typescript
interface Detection {
  id: string;                          // Unique identifier
  classId: number;                     // Class numeric ID
  className: string;                   // Human-readable name
  confidence: number;                  // 0.0 - 1.0
  bbox: BoundingBox;                   // Bounding box coords
  imageId: string;                     // Parent image ID
}

interface BoundingBox {
  x: number;                           // Top-left X
  y: number;                           // Top-left Y
  width: number;                       // Box width
  height: number;                      // Box height
}
```

## Konva Component Mapping

| React Component | Konva Element | Purpose |
|----------------|---------------|---------|
| Stage | <Stage> | Canvas container |
| Layer | <Layer> | Rendering layer |
| KonvaImage | <Image> | Display image |
| Group | <Group> | Box grouping |
| Rect | <Rect> | Box & label bg |
| Text | <Text> | Label text |

## Visual States

### Bounding Box Colors

| State | Stroke Color | Stroke Width |
|-------|-------------|--------------|
| Normal | Class Color | 2px |
| Hover | Yellow (#FFFF00) | 3px |
| Selected | Red (#FF0000) | 4px |

### Class Color Palette

| Class ID % 10 | Color | Hex |
|---------------|-------|-----|
| 0 | Red | #FF6B6B |
| 1 | Teal | #4ECDC4 |
| 2 | Blue | #45B7D1 |
| 3 | Light Salmon | #FFA07A |
| 4 | Mint | #98D8C8 |
| 5 | Yellow | #F7DC6F |
| 6 | Purple | #BB8FCE |
| 7 | Sky Blue | #85C1E2 |
| 8 | Orange | #F8B739 |
| 9 | Green | #52B788 |

## Zoom Behavior

```
User Action          → Effect
─────────────────────────────────────────
Wheel Up            → Zoom in at cursor
Wheel Down          → Zoom out at cursor
Zoom In Button      → Zoom in * 1.25
Zoom Out Button     → Zoom out / 1.25
Reset Button        → Auto-fit + center
Image Load          → Auto-fit + center

Zoom Range: 10% - 500%
```

## Pan Behavior

```
User Action          → Effect
─────────────────────────────────────────
Click + Drag        → Pan image
Release             → Update position

Pan Range: Unlimited
Cursor: grab / grabbing
```

## Filter Application

```
Filter Change → useMemo recalculates → Re-render BoundingBox[]

Filters Applied:
├── classIds (multi-select)
├── minConfidence (range slider)
└── maxConfidence (range slider)

Display Toggles:
├── showLabels (switch)
└── showConfidence (switch)
```

## Performance Characteristics

| Aspect | Implementation | Performance |
|--------|----------------|-------------|
| Image Loading | use-image hook | Cached, fast |
| Detection Filtering | useMemo | Only on filter change |
| Zoom/Pan State | Local state | No Redux overhead |
| Hit Detection | 10px stroke | Easier clicking |
| Rendering | Konva | Hardware accelerated |

## Dependencies

```json
{
  "konva": "9.3.15",              // Canvas library
  "react-konva": "18.2.10",       // React bindings
  "use-image": "^1.1.4",          // Image loading hook
  "@mui/material": "^7.3.7",      // UI components
  "@mui/icons-material": "^7.3.7", // Icons
  "react-redux": "^9.2.0",        // Redux hooks
  "@reduxjs/toolkit": "^2.11.2"   // Redux state
}
```
