# ResultsViewer Component Diagram

## Visual Component Hierarchy

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AppShell (App Layout)                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    ResultsPanel (Wrapper)                     │   │
│  │  ┌───────────────────────────────────────────────────────┐   │   │
│  │  │              ResultsViewer (Main Component)            │   │   │
│  │  │                                                         │   │   │
│  │  │  ┌─────────────────────────────────────────────────┐  │   │   │
│  │  │  │ Tab Bar: [Input] [Labels] [Output] [Compare]  │  │   │   │
│  │  │  │           Image: 1 / 5  [◀] [▶]               │  │   │   │
│  │  │  └─────────────────────────────────────────────────┘  │   │   │
│  │  │                                                         │   │   │
│  │  │  ┌─────────────────────────────────────────────────┐  │   │   │
│  │  │  │           FilterControls (if not Input)         │  │   │   │
│  │  │  │  [Class Filter ▼] [Confidence: 0.25 ━●━━━ 1.0] │  │   │   │
│  │  │  │  [☑ Show Labels] [☑ Show Confidence] [Reset]   │  │   │   │
│  │  │  └─────────────────────────────────────────────────┘  │   │   │
│  │  │                                                         │   │   │
│  │  │  ┌──────────────────────┬───────────────────────────┐ │   │   │
│  │  │  │   ImageCanvas        │      InfoPanel            │ │   │   │
│  │  │  │                      │  (if not Input)           │ │   │   │
│  │  │  │  [Zoom Controls]     │                           │ │   │   │
│  │  │  │  [+] [Reset] [-]     │  Selected Detection       │ │   │   │
│  │  │  │                      │  ┌──────────────────┐    │ │   │   │
│  │  │  │  ┌────────────────┐ │  │ Class: Car       │    │ │   │   │
│  │  │  │  │                │ │  │ Confidence: 95%  │    │ │   │   │
│  │  │  │  │   [Image]      │ │  │                  │    │ │   │   │
│  │  │  │  │                │ │  │ BBox Coords:     │    │ │   │   │
│  │  │  │  │  ┌────────┐   │ │  │  X: 100          │    │ │   │   │
│  │  │  │  │  │Car 95% │   │ │  │  Y: 200          │    │ │   │   │
│  │  │  │  │  └────────┘   │ │  │  W: 150          │    │ │   │   │
│  │  │  │  │                │ │  │  H: 200          │    │ │   │   │
│  │  │  │  │                │ │  │                  │    │ │   │   │
│  │  │  │  └────────────────┘ │  │ Area: 30000 px² │    │ │   │   │
│  │  │  │                      │  │ Aspect: 0.75    │    │ │   │   │
│  │  │  │                      │  │                  │    │ │   │   │
│  │  │  │                      │  │ Pipeline:        │    │ │   │   │
│  │  │  │                      │  │ ✓ YOLO          │    │ │   │   │
│  │  │  │                      │  │ ✓ NMS           │    │ │   │   │
│  │  │  │                      │  │ ✓ Symbolic      │    │ │   │   │
│  │  │  │                      │  └──────────────────┘    │ │   │   │
│  │  │  └──────────────────────┴───────────────────────────┘ │   │   │
│  │  │                                                         │   │   │
│  │  │  ┌─────────────────────────────────────────────────┐  │   │   │
│  │  │  │         DetectionStats (if not Input)           │  │   │   │
│  │  │  │  Total: 147 │ Classes: 5 │ Avg Conf: 78%       │  │   │   │
│  │  │  │  [Car: 45] [Person: 28] [Bicycle: 12] [+2 more]│  │   │   │
│  │  │  └─────────────────────────────────────────────────┘  │   │   │
│  │  └───────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## State Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Redux Store                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      resultsSlice                            │   │
│  │  • results: DetectionResult[]                                │   │
│  │  • currentImageIndex: number                                 │   │
│  │  • selectedDetectionIds: string[]                            │   │
│  │  • filters: { classIds, minConfidence, maxConfidence }       │   │
│  │  • isLoading: boolean                                        │   │
│  │  • error: string | null                                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
         │                    ▲                    ▲                ▲
         │ useAppSelector     │ dispatch           │ dispatch       │ dispatch
         ▼                    │                    │                │
┌──────────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  ResultsViewer   │  │FilterControls│  │ ImageCanvas  │  │  InfoPanel   │
│                  │  │              │  │              │  │              │
│ • reads results  │  │• updateFilters│ │• toggleSelect│  │• reads current│
│ • reads loading  │  │• resetFilters│  │              │  │  selection   │
│ • reads error    │  │              │  │              │  │              │
│ • nextImage()    │  │              │  │              │  │              │
│ • previousImage()│  │              │  │              │  │              │
└──────────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

## User Interaction Flow

```
User Action                    Component              Redux Action
──────────────────────────────────────────────────────────────────────

Click "Output" tab      →    ResultsViewer      →    (local state)
                                    ↓
                             FilterControls renders
                             ImageCanvas shows overlays
                             InfoPanel shows
                             DetectionStats shows

Select class "Car"      →    FilterControls     →    updateFilters({ classIds: [0] })
                                    ↓                          ↓
                             Redux updates              Components re-render
                                    ↓                          ↓
                             ImageCanvas filters        DetectionStats updates

Adjust confidence       →    FilterControls     →    updateFilters({ minConfidence: 0.5 })
slider to 0.5                      ↓                          ↓
                             Redux updates              Components re-render

Click bounding box      →    ImageCanvas        →    toggleDetectionSelection(id)
                                    ↓                          ↓
                             Redux updates              Box turns red
                                    ↓                          ↓
                             InfoPanel shows details

Click "Next" button     →    ResultsViewer      →    nextImage()
                                    ↓                          ↓
                             currentImageIndex++        Components re-render
                                    ↓
                             New image loads

Zoom in                 →    ImageCanvas        →    (local state: zoom *= 1.25)
                                    ↓
                             Canvas re-renders

Drag canvas             →    ImageCanvas        →    (local state: pan = { x, y })
                                    ↓
                             Canvas position updates
```

## Component Communication

```
Parent → Child (Props)
══════════════════════
ResultsViewer → ImageCanvas
  • imageUrl: string
  • viewMode: 'input' | 'labels' | 'output' | 'compare'
  • showLabels: boolean (from local state)
  • showConfidence: boolean (from local state)

Child → Parent (Redux)
══════════════════════
FilterControls → Redux → ResultsViewer
  • Filters update
  • All components see new filters
  • Re-render with filtered data

ImageCanvas → Redux → InfoPanel
  • Selection changes
  • InfoPanel shows selected detection details

Sibling Communication (via Redux)
═════════════════════════════════
ImageCanvas ↔ InfoPanel
  • Click in ImageCanvas updates selection
  • InfoPanel reads selection from Redux

FilterControls ↔ DetectionStats
  • Filters update in FilterControls
  • DetectionStats shows filtered counts
```

## Data Flow Example: Filtering Detections

```
1. User drags confidence slider to 0.5
   ↓
2. FilterControls: onChange handler fires
   ↓
3. dispatch(updateFilters({ minConfidence: 0.5 }))
   ↓
4. Redux: resultsSlice.filters.minConfidence = 0.5
   ↓
5. All subscribed components re-render:
   │
   ├─→ ImageCanvas: useMemo recalculates filtered detections
   │   └─→ Only shows boxes with confidence ≥ 0.5
   │
   ├─→ DetectionStats: useMemo recalculates stats
   │   └─→ Shows count of filtered detections
   │
   └─→ InfoPanel: No change (shows selected detection if any)
```

## View Mode States

```
Input View
──────────
┌─────────────────────────────────┐
│ Tabs: [Input*] Labels Output... │
├─────────────────────────────────┤
│                                  │
│         Original Image           │
│         (no overlays)            │
│                                  │
└─────────────────────────────────┘
• No FilterControls
• No InfoPanel
• No DetectionStats
• Just the image


Output View
───────────
┌─────────────────────────────────────────┐
│ Tabs: Input Labels [Output*] Compare    │
├─────────────────────────────────────────┤
│ [Filters] [Class ▼] [Confidence ━●━━━]  │
├──────────────────────┬──────────────────┤
│                      │  Selected:       │
│   Image with boxes   │  Car 95%        │
│   [+] [-] [Reset]    │  Details...     │
│                      │                 │
├──────────────────────┴──────────────────┤
│ Total: 147 │ Classes: 5 │ Avg: 78%     │
└─────────────────────────────────────────┘
• All components visible
• Filters active
• Selection enabled
• Statistics shown
```

## Key Features by Component

```
ResultsViewer (Main Orchestrator)
├─ Tab navigation (4 modes)
├─ Image navigation (prev/next)
├─ Loading state (spinner)
├─ Error state (alert)
├─ Empty state (instructions)
└─ Resizable panel layout

FilterControls
├─ Multi-select class filter
├─ Dual-range confidence slider
├─ Show labels toggle
├─ Show confidence toggle
└─ Reset filters button

ImageCanvas
├─ Canvas-based rendering
├─ Zoom controls (25%-500%)
├─ Pan with mouse drag
├─ Bounding box overlays
├─ Click to select
└─ View mode rendering

InfoPanel
├─ Selected detection details
├─ Class and confidence
├─ Bounding box coordinates
├─ Computed properties
└─ Pipeline stages

DetectionStats
├─ Total detections count
├─ Number of classes
├─ Average confidence
└─ Top 5 classes breakdown
```
