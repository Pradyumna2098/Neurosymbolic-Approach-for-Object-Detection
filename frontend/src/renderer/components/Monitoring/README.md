# Monitoring Dashboard Component

## Overview

The Monitoring Dashboard provides real-time performance metrics and system logs for the Neurosymbolic Object Detection application. It is a collapsible panel at the bottom of the application interface.

## Features

### 1. Performance Metrics Tab
Displays key performance indicators including:
- **Inference Time**: Time taken for detection inference (ms/s)
- **Total Detections**: Number of objects detected across all images
- **Average Confidence**: Mean confidence score of all detections
- **Processing Speed**: Images processed per second
- **Progress Bar**: Visual indicator of current processing status

### 2. System Logs Tab
Shows chronological system logs with:
- **Log Levels**: Info, Success, Warning, Error
- **Log Filtering**: Filter by level or search text
- **Auto-scroll**: Automatically scrolls to latest log entry
- **Source Tracking**: Shows which component generated the log
- **Timestamp**: Precise time of each log entry

### 3. Collapsible Panel
- Expandable/collapsible to save screen space
- Shows summary when collapsed (inference time, detections, log count)
- Keyboard accessible (Enter/Space to toggle)

## Components

### MonitoringDashboard (`index.tsx`)
Main component that orchestrates the dashboard:
- Manages tabbed interface (Metrics/Logs)
- Handles expand/collapse state
- Integrates with Redux state
- Provides collapsed state summary

### PerformanceMetrics (`PerformanceMetrics.tsx`)
Displays real-time performance metrics:
- Grid layout with 4 metric cards
- Progress bar for active processing
- Responsive design (stacks on mobile)
- Color-coded metrics with icons

### SystemLogs (`SystemLogs.tsx`)
Displays and manages system logs:
- Log entry list with timestamps
- Filter by log level (All/Info/Success/Warning/Error)
- Search functionality
- Clear logs button
- Auto-scroll to latest
- Shows log count

## Redux Integration

### State Structure (`monitoringSlice.ts`)
```typescript
interface MonitoringState {
  logs: LogEntry[];           // Array of log entries
  metrics: PerformanceMetrics; // Current metrics
  isExpanded: boolean;         // Panel expand state
  maxLogs: number;            // Max logs to retain (100)
}
```

### Actions
- `addLog`: Add a new log entry
- `updateMetrics`: Update performance metrics
- `clearLogs`: Clear all logs
- `clearMetrics`: Reset metrics
- `toggleExpanded`: Toggle panel expansion
- `setExpanded`: Set specific expansion state
- `resetMonitoring`: Reset to initial state

### Middleware (`monitoringMiddleware.ts`)
Automatically captures and logs events from other Redux slices:
- **Detection events**: Start, progress, complete, error, cancel
- **Upload events**: File add, remove, clear
- **Results events**: Results loaded
- **Config events**: Config updates

Automatically calculates metrics:
- Inference time from start/complete timestamps
- Processing speed from time and image count
- Progress percentage from detection updates
- Average confidence from results

## Usage

### Manual Logging
```typescript
import { addLog } from './store/slices/monitoringSlice';

// In your component
dispatch(addLog({
  level: 'info',
  message: 'Operation completed successfully',
  source: 'MyComponent'
}));
```

### Manual Metrics Update
```typescript
import { updateMetrics } from './store/slices/monitoringSlice';

// In your component
dispatch(updateMetrics({
  inferenceTime: 1500, // milliseconds
  totalDetections: 42,
  averageConfidence: 0.85
}));
```

### Accessing State
```typescript
import { useAppSelector } from './store/hooks';

const { logs, metrics, isExpanded } = useAppSelector((state) => state.monitoring);
```

## Automatic Event Logging

The monitoring middleware automatically logs these events:

### Detection Events
- `detection/startDetection` → Info log: "Detection started for job: {id}"
- `detection/updateProgress` → Info log with progress message
- `detection/completeDetection` → Success log: "Detection completed successfully"
- `detection/setDetectionError` → Error log with error message
- `detection/cancelDetection` → Warning log: "Detection cancelled by user"

### Upload Events
- `upload/addFiles` → Info log: "{count} file(s) uploaded"
- `upload/removeFile` → Info log: "File removed from upload list"
- `upload/clearFiles` → Info log: "Upload list cleared"

### Results Events
- `results/setResults` → Success log with detection count
- Automatically updates totalDetections and averageConfidence metrics

### Config Events
- `config/updateConfig` → Info log: "Configuration updated"
- `config/resetConfig` → Info log: "Configuration reset to defaults"

## Styling

The component uses Material-UI theming and follows the application's design system:
- Dark/Light theme support via AppShell theme provider
- Consistent color palette
- Responsive layout (mobile, tablet, desktop)
- Accessible keyboard navigation
- Icon-based visual indicators

## Future Enhancements

### Prometheus Integration (Optional)
For production deployments, the dashboard can be extended to include:
- Prometheus metrics endpoint configuration
- Time-series charts (mAP trend, GPU utilization)
- Custom PromQL queries
- Historical metrics visualization
- Alerting based on thresholds

See `docs/feature_implementation/PROMETHEUS_INTEGRATION_GUIDE.md` for details.

## Testing

To test the monitoring dashboard:

1. **Start the application**:
   ```bash
   cd frontend && npm start
   ```

2. **Upload images** - Should see log: "X file(s) uploaded"

3. **Run detection** - Should see:
   - Log: "Detection started for job: {id}"
   - Progress metrics updating in real-time
   - Log: "Detection completed successfully"
   - Final metrics displayed (inference time, detections, etc.)

4. **Test filtering**:
   - Switch to System Logs tab
   - Click different level filters (Info, Success, Warning, Error)
   - Use search box to filter logs

5. **Test collapse**:
   - Click expand/collapse icon
   - Verify collapsed summary shows current state

## Known Limitations

1. **Log retention**: Only last 100 logs are kept in memory
2. **No persistence**: Logs and metrics are lost on page refresh
3. **Real-time only**: No historical data storage
4. **Basic metrics**: Advanced metrics (GPU usage, memory) require Prometheus

## Dependencies

- `@mui/material` - UI components
- `@mui/icons-material` - Icons
- `@reduxjs/toolkit` - State management
- `react` - Component framework
- `react-redux` - Redux React bindings

## Files

```
frontend/src/renderer/
├── components/
│   └── Monitoring/
│       ├── index.tsx                    # Main dashboard component
│       ├── PerformanceMetrics.tsx       # Metrics display
│       └── SystemLogs.tsx               # Logs display
└── store/
    ├── slices/
    │   └── monitoringSlice.ts           # Redux slice
    └── middleware/
        └── monitoringMiddleware.ts      # Auto-logging middleware
```
