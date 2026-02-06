# Redux Store Architecture

## State Tree Structure

```typescript
RootState {
  upload: {
    files: UploadedFile[]
    isUploading: boolean
    uploadProgress: number
    error: string | null
  }
  
  config: {
    // Model settings
    modelPath: string
    
    // YOLO parameters
    confidence: number
    iouThreshold: number
    
    // SAHI parameters
    sliceHeight: number
    sliceWidth: number
    overlapHeight: number
    overlapWidth: number
    
    // Advanced options
    device: 'cuda' | 'cpu'
    enableProlog: boolean
    enableNMS: boolean
    
    // Presets
    presets: Array<{
      name: string
      config: DetectionConfig
    }>
    currentPreset: string | null
  }
  
  detection: {
    jobId: string | null
    status: 'idle' | 'uploading' | 'pending' | 'running' | 'complete' | 'error'
    progress: {
      stage: string
      progress: number (0-100)
      message: string
    }
    error: string | null
    startedAt: Date | null
    completedAt: Date | null
  }
  
  results: {
    results: DetectionResult[]
    currentImageIndex: number
    selectedDetectionIds: string[]
    filters: {
      classIds: number[]
      minConfidence: number
      maxConfidence: number
    }
    viewMode: 'single' | 'grid' | 'compare'
    compareImageIndices: [number, number] | null
    isLoading: boolean
    error: string | null
  }
}
```

## Action Flow Diagrams

### Upload Flow
```
User Selects Files
      ↓
  addFiles(files)
      ↓
  [Upload Slice]
      ↓
  files: [...new files]
```

### Detection Flow
```
User Starts Detection
        ↓
   startDetection(jobId)
        ↓
   status: 'pending'
        ↓
   [Backend Processing]
        ↓
   updateProgress({stage, progress, message})
        ↓
   status: 'running'
        ↓
   completeDetection()
        ↓
   status: 'complete'
```

### Results Flow
```
Detection Complete
      ↓
  setResults(results)
      ↓
  [Results Slice]
      ↓
  results: [...detections]
  currentImageIndex: 0
      ↓
  User Filters/Selects
      ↓
  updateFilters({...})
  selectDetection(id)
```

## Component Usage Examples

### Upload Component
```typescript
import { useAppDispatch, useAppSelector } from './store/hooks';
import { addFiles } from './store/slices/uploadSlice';

function UploadPanel() {
  const dispatch = useAppDispatch();
  const files = useAppSelector(state => state.upload.files);
  
  const handleUpload = (selectedFiles: File[]) => {
    dispatch(addFiles(selectedFiles.map(f => ({
      id: crypto.randomUUID(),
      name: f.name,
      size: f.size,
      path: f.path,
      uploadedAt: new Date()
    }))));
  };
  
  return <div>Files: {files.length}</div>;
}
```

### Config Component
```typescript
import { useAppDispatch, useAppSelector } from './store/hooks';
import { updateConfig } from './store/slices/configSlice';

function ConfigPanel() {
  const dispatch = useAppDispatch();
  const confidence = useAppSelector(state => state.config.confidence);
  
  const handleConfidenceChange = (value: number) => {
    dispatch(updateConfig({ confidence: value }));
  };
  
  return (
    <Slider 
      value={confidence}
      onChange={handleConfidenceChange}
      min={0.01}
      max={1.0}
      step={0.01}
    />
  );
}
```

### Detection Status Component
```typescript
import { useAppSelector } from './store/hooks';

function DetectionStatus() {
  const { status, progress } = useAppSelector(state => state.detection);
  
  return (
    <div>
      <p>Status: {status}</p>
      <p>Progress: {progress.progress}%</p>
      <p>Stage: {progress.stage}</p>
    </div>
  );
}
```

### Results Viewer Component
```typescript
import { useAppDispatch, useAppSelector } from './store/hooks';
import { nextImage, previousImage } from './store/slices/resultsSlice';

function ResultsViewer() {
  const dispatch = useAppDispatch();
  const { results, currentImageIndex } = useAppSelector(
    state => state.results
  );
  
  const currentResult = results[currentImageIndex];
  
  return (
    <div>
      <img src={currentResult?.imagePath} />
      <button onClick={() => dispatch(previousImage())}>Previous</button>
      <button onClick={() => dispatch(nextImage())}>Next</button>
      <p>Image {currentImageIndex + 1} of {results.length}</p>
    </div>
  );
}
```

## Middleware Configuration

The store is configured with custom middleware to handle non-serializable values:

```typescript
middleware: (getDefaultMiddleware) =>
  getDefaultMiddleware({
    serializableCheck: {
      // Ignore these action types
      ignoredActions: [
        'upload/addFiles',
        'detection/startDetection',
        'detection/completeDetection',
        'detection/setDetectionError',
      ],
      // Ignore these paths in state
      ignoredPaths: [
        'upload.files',
        'detection.startedAt',
        'detection.completedAt',
        'results.results',
      ],
    },
  }),
```

This allows storing File objects and Date objects in the state while maintaining performance.

## Redux DevTools Integration

The store is configured with Redux DevTools for development:

```typescript
devTools: process.env.NODE_ENV !== 'production'
```

Features available:
- 🔍 State inspection
- ⏱️ Time-travel debugging
- 📊 Action history
- 🎯 Action dispatching
- 📸 State snapshots

## Performance Considerations

1. **Selector Optimization**: Use `useAppSelector` with specific selectors instead of selecting entire slices
2. **Component Optimization**: Use `React.memo()` for components that read from store
3. **Action Batching**: Multiple actions in quick succession are automatically batched by React 18
4. **Immutable Updates**: Redux Toolkit uses Immer for immutable updates automatically

## Next Steps

With Redux configured, you can now:

1. **Build Upload Component** - Use `uploadSlice` actions
2. **Build Config Component** - Use `configSlice` for parameter management
3. **Implement Detection Flow** - Use `detectionSlice` for job tracking
4. **Create Results Viewer** - Use `resultsSlice` for visualization
5. **Add API Integration** - Create async thunks for backend communication
6. **Implement Persistence** - Add redux-persist if state needs to survive app restarts

## References

- Redux Toolkit: https://redux-toolkit.js.org/
- React-Redux: https://react-redux.js.org/
- Redux DevTools: https://github.com/reduxjs/redux-devtools
