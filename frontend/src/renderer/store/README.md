# Redux State Management

This directory contains the Redux Toolkit state management setup for the Neurosymbolic Object Detection application.

## Overview

Redux Toolkit is used for centralized state management with the following features:
- ✅ Type-safe state management with TypeScript
- ✅ Slice pattern for modular state organization
- ✅ Redux DevTools integration for debugging
- ✅ Optimized middleware configuration

## Directory Structure

```
store/
├── index.ts              # Store configuration
├── hooks/
│   └── index.ts         # Typed hooks (useAppDispatch, useAppSelector)
├── slices/
│   ├── uploadSlice.ts   # Upload state management
│   ├── configSlice.ts   # Configuration state management
│   ├── detectionSlice.ts # Detection job state management
│   └── resultsSlice.ts  # Results and visualization state management
└── testStore.ts         # Store validation script
```

## State Slices

### Upload Slice (`uploadSlice`)
Manages file upload state.

**State:**
- `files: UploadedFile[]` - List of uploaded files
- `isUploading: boolean` - Upload in progress flag
- `uploadProgress: number` - Upload progress (0-100)
- `error: string | null` - Upload error message

**Actions:**
- `addFiles(files)` - Add files to upload list
- `removeFile(id)` - Remove a file by ID
- `clearFiles()` - Clear all files
- `setUploading(boolean)` - Set uploading state
- `setUploadProgress(number)` - Update upload progress
- `setUploadError(message)` - Set upload error

### Config Slice (`configSlice`)
Manages detection configuration parameters.

**State:**
- `modelPath: string` - Path to YOLO model
- `confidence: number` - Confidence threshold (0.01-1.0)
- `iouThreshold: number` - IoU threshold for NMS (0.01-1.0)
- `sliceHeight: number` - SAHI slice height
- `sliceWidth: number` - SAHI slice width
- `overlapHeight: number` - SAHI overlap height ratio (0.0-0.5)
- `overlapWidth: number` - SAHI overlap width ratio (0.0-0.5)
- `device: 'cuda' | 'cpu'` - Computation device
- `enableProlog: boolean` - Enable Prolog reasoning
- `enableNMS: boolean` - Enable NMS post-processing
- `presets: Array` - Saved configuration presets
- `currentPreset: string | null` - Currently active preset

**Actions:**
- `updateConfig(config)` - Update configuration values
- `loadPreset(name)` - Load a saved preset
- `savePreset({name, config})` - Save configuration as preset
- `deletePreset(name)` - Delete a preset
- `resetConfig()` - Reset to default values

### Detection Slice (`detectionSlice`)
Manages detection job status and progress.

**State:**
- `jobId: string | null` - Current job ID
- `status: JobStatus` - Job status ('idle' | 'uploading' | 'pending' | 'running' | 'complete' | 'error')
- `progress: JobProgress` - Progress information
  - `stage: string` - Current processing stage
  - `progress: number` - Progress percentage (0-100)
  - `message: string` - Status message
- `error: string | null` - Error message
- `startedAt: Date | null` - Job start timestamp
- `completedAt: Date | null` - Job completion timestamp

**Actions:**
- `startDetection(jobId)` - Start a detection job
- `updateStatus(status)` - Update job status
- `updateProgress(progress)` - Update job progress
- `completeDetection()` - Mark job as complete
- `setDetectionError(message)` - Set error state
- `resetDetection()` - Reset to initial state
- `cancelDetection()` - Cancel current job

### Results Slice (`resultsSlice`)
Manages detection results and visualization state.

**State:**
- `results: DetectionResult[]` - Array of detection results
- `currentImageIndex: number` - Currently displayed image index
- `selectedDetectionIds: string[]` - Selected detection IDs
- `filters` - Result filtering options
  - `classIds: number[]` - Filter by class IDs
  - `minConfidence: number` - Minimum confidence threshold
  - `maxConfidence: number` - Maximum confidence threshold
- `viewMode: 'single' | 'grid' | 'compare'` - Visualization mode
- `compareImageIndices: [number, number] | null` - Indices for compare mode
- `isLoading: boolean` - Loading state
- `error: string | null` - Error message

**Actions:**
- `setResults(results)` - Set detection results
- `setCurrentImageIndex(index)` - Change current image
- `nextImage()` - Navigate to next image
- `previousImage()` - Navigate to previous image
- `selectDetection(id)` - Select a detection
- `deselectDetection(id)` - Deselect a detection
- `toggleDetectionSelection(id)` - Toggle detection selection
- `clearSelection()` - Clear all selections
- `updateFilters(filters)` - Update result filters
- `resetFilters()` - Reset filters to defaults
- `setViewMode(mode)` - Change visualization mode
- `setCompareImages([index1, index2])` - Set images for compare mode
- `setLoading(boolean)` - Set loading state
- `setResultsError(message)` - Set error state
- `clearResults()` - Clear all results

## Usage

### Importing Hooks

```typescript
import { useAppDispatch, useAppSelector } from './store/hooks';
```

### Using in Components

```typescript
import React from 'react';
import { useAppDispatch, useAppSelector } from './store/hooks';
import { addFiles } from './store/slices/uploadSlice';

function UploadComponent() {
  const dispatch = useAppDispatch();
  const files = useAppSelector((state) => state.upload.files);
  
  const handleFilesSelected = (selectedFiles: File[]) => {
    const uploadedFiles = selectedFiles.map((file) => ({
      id: crypto.randomUUID(),
      name: file.name,
      size: file.size,
      path: file.path,
      uploadedAt: new Date(),
    }));
    
    dispatch(addFiles(uploadedFiles));
  };
  
  return (
    <div>
      <p>Uploaded Files: {files.length}</p>
      {/* ... */}
    </div>
  );
}
```

### Accessing State

```typescript
// Select specific slice
const uploadState = useAppSelector((state) => state.upload);

// Select specific field
const filesCount = useAppSelector((state) => state.upload.files.length);

// Select with transformation
const hasFiles = useAppSelector((state) => state.upload.files.length > 0);
```

### Dispatching Actions

```typescript
const dispatch = useAppDispatch();

// Simple action
dispatch(clearFiles());

// Action with payload
dispatch(updateConfig({ confidence: 0.5 }));

// Multiple actions
dispatch(clearFiles());
dispatch(resetConfig());
dispatch(resetDetection());
```

## Redux DevTools

Redux DevTools is automatically enabled in development mode. To use it:

1. Install Redux DevTools browser extension
   - [Chrome Extension](https://chrome.google.com/webstore/detail/redux-devtools/lmhkpmbekcpmknklioeibfkpmmfibljd)
   - [Firefox Extension](https://addons.mozilla.org/en-US/firefox/addon/reduxdevtools/)

2. Open the DevTools panel in your browser
3. Navigate to the "Redux" tab
4. Inspect state, actions, and time-travel debug

## Type Safety

All state interfaces are defined in `../types/index.ts`:
- `UploadedFile` - File upload metadata
- `DetectionConfig` - Configuration parameters
- `Detection` - Single detection result
- `DetectionResult` - Complete image result
- `JobStatus` - Detection job status enum
- `JobProgress` - Job progress information

## Testing

To manually test the store, you can run the validation script:

```typescript
import './store/testStore';
```

Or test individual actions in the browser console:

```javascript
// Access the store (if exposed to window in dev mode)
store.dispatch({ type: 'upload/addFiles', payload: [...] });
console.log(store.getState());
```

## Best Practices

1. **Always use typed hooks** (`useAppDispatch`, `useAppSelector`) instead of plain Redux hooks
2. **Keep actions small and focused** - Each action should do one thing
3. **Use selectors** - Create reusable selectors for complex state queries
4. **Normalize state** - Keep state flat and normalized when possible
5. **Handle errors** - Always include error states in slices
6. **Document state changes** - Add comments for complex reducers

## Performance Considerations

- The store is configured with `serializableCheck` disabled for File objects and Date objects
- Redux DevTools is only enabled in development mode
- Use `React.memo()` and `useMemo()` in components that read from store frequently
- Consider creating selector hooks for expensive computations

## Future Enhancements

Potential improvements for the state management:
- Add RTK Query for API calls
- Implement redux-persist for state persistence
- Add middleware for analytics
- Create selector functions in separate files
- Add state migration utilities for version updates
