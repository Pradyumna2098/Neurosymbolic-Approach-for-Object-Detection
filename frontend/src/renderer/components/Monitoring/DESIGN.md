# Monitoring Dashboard - Visual Design

## Expanded View - Performance Metrics Tab

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ Monitoring Dashboard                                                         ║
║ ┌─────────────────────────────────────┬──────────────────────────┐         ║
║ │ ⚡ Performance Metrics | System Logs │                    ▼ ▲  │         ║
║ └─────────────────────────────────────┴──────────────────────────┘         ║
║                                                                              ║
║  ⚡ Performance Metrics                                                      ║
║                                                                              ║
║  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌───────────┐║
║  │ ⏱️ Inference    │ │ ✓ Total         │ │ 📊 Avg          │ │ 🖼️ Process│║
║  │    Time         │ │   Detections    │ │   Confidence    │ │   Speed   │║
║  │                 │ │                 │ │                 │ │           │║
║  │   2.34s         │ │      42         │ │     0.85        │ │ 3.2 img/s │║
║  └─────────────────┘ └─────────────────┘ └─────────────────┘ └───────────┘║
║                                                                              ║
║  ┌───────────────────────────────────────────────────────────────────────┐  ║
║  │ Processing Progress                          15 / 20 images           │  ║
║  │ ████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                │  ║
║  │                                                          [ 75.0% ]     │  ║
║  └───────────────────────────────────────────────────────────────────────┘  ║
║                                                                              ║
║                              Last updated: 11:42:15 AM                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Expanded View - System Logs Tab

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ Monitoring Dashboard                                                         ║
║ ┌─────────────────────────────────────┬──────────────────────────┐         ║
║ │ Performance Metrics | 📋 System Logs │                    ▼ ▲  │         ║
║ └─────────────────────────────────────┴──────────────────────────┘         ║
║                                                                              ║
║  📋 System Logs                                                🗑️ Clear    ║
║                                                                              ║
║  ┌─────────────────────────┐  ┌─────────────────────────────────────────┐  ║
║  │ 🔍 Search logs...       │  │ [All] [Info] [Success] [Warning] [Error] │  ║
║  └─────────────────────────┘  └─────────────────────────────────────────┘  ║
║                                                                              ║
║  ┌────────────────────────────────────────────────────────────────────────┐ ║
║  │ ℹ️ 11:42:10 [Detection] Detection started for job: abc-123-def        │ ║
║  │ ℹ️ 11:42:11 [Detection] Loading YOLO model...                         │ ║
║  │ ℹ️ 11:42:12 [Detection] Processing image 1 of 20                      │ ║
║  │ ℹ️ 11:42:13 [Detection] SAHI slicing complete                         │ ║
║  │ ℹ️ 11:42:14 [Detection] Running NMS filtering                         │ ║
║  │ ✓ 11:42:15 [Detection] Detection completed successfully               │ ║
║  │ ✓ 11:42:16 [Results] Results loaded: 42 detections across 20 images  │ ║
║  └────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  Showing 7 of 7 logs                                    Max 100 logs retained║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Collapsed View

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ Monitoring Dashboard  Inference: 2.34s | Detections: 42 | 7 logs      ▲ ▼  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Component Structure

```
MonitoringDashboard
├── Header (with Tabs and Toggle)
│   ├── Tab: Performance Metrics
│   ├── Tab: System Logs
│   └── IconButton: Expand/Collapse
│
├── Collapse Container (expandable)
│   │
│   ├── PerformanceMetrics Component (when tab = 0)
│   │   ├── Header with icon
│   │   ├── Grid/Box Layout (responsive)
│   │   │   ├── Metric Card: Inference Time
│   │   │   ├── Metric Card: Total Detections
│   │   │   ├── Metric Card: Average Confidence
│   │   │   └── Metric Card: Processing Speed
│   │   ├── Progress Bar (conditional)
│   │   └── Last Updated timestamp
│   │
│   └── SystemLogs Component (when tab = 1)
│       ├── Header with Clear button
│       ├── Filter Controls
│       │   ├── Search TextField
│       │   └── Level Filter Chips
│       ├── Logs Container (scrollable)
│       │   └── Log Entry Items
│       │       ├── Icon (by level)
│       │       ├── Timestamp
│       │       ├── Source Chip
│       │       └── Message
│       └── Footer (log count info)
│
└── Collapsed Summary (when not expanded)
    └── Summary Stats (inference, detections, logs)
```

## Color Scheme

- **Info Logs**: Blue (#1976d2)
- **Success Logs**: Green (#2e7d32)
- **Warning Logs**: Orange (#ed6c02)
- **Error Logs**: Red (#d32f2f)
- **Metric Icons**: Primary/Success/Info/Warning colors
- **Progress Bar**: Primary theme color
- **Cards**: Outlined variant with hover effect

## Responsive Behavior

### Desktop (≥960px)
- 4 metric cards in a row
- Full width logs panel
- All features visible

### Tablet (600-959px)
- 2 metric cards per row
- Scrollable logs
- Compact filters

### Mobile (<600px)
- 1 metric card per row (stacked)
- Simplified log view
- Chip filters stack
- Search box full width

## Interaction Patterns

1. **Expand/Collapse**: Click header or toggle button
2. **Tab Switch**: Click tab labels
3. **Log Filtering**: Click level chips or type in search
4. **Clear Logs**: Click trash icon in System Logs header
5. **Auto-scroll**: Logs automatically scroll to latest entry
6. **Keyboard**: Enter/Space to toggle expand/collapse

## State Management

```typescript
// Redux State
state.monitoring = {
  logs: LogEntry[],        // Max 100 entries
  metrics: {
    inferenceTime: number,      // milliseconds
    totalDetections: number,    // count
    averageConfidence: number,  // 0-1
    processingSpeed: number,    // img/s
    imagesProcessed: number,    // current
    totalImages: number,        // total
    lastUpdated: Date
  },
  isExpanded: boolean,
  maxLogs: 100
}
```

## Integration Points

The monitoring dashboard automatically captures events from:

- **Upload Panel**: File add/remove/clear
- **Config Panel**: Configuration changes
- **Detection Process**: Start, progress, complete, error, cancel
- **Results Panel**: Results loaded with metrics

All logging happens automatically via the monitoring middleware - no manual logging required in most cases!
