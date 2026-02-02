# Frontend UI Implementation Guide

**Version:** 1.0  
**Date:** February 2, 2026  
**Related:** [Frontend UI Design](frontend_ui_design.md)

## Table of Contents
1. [Implementation Roadmap](#implementation-roadmap)
2. [Technology Stack Details](#technology-stack-details)
3. [Development Setup](#development-setup)
4. [Component Implementation](#component-implementation)
5. [Backend Integration](#backend-integration)
6. [Prometheus Integration](#prometheus-integration)
7. [Testing Strategy](#testing-strategy)
8. [Deployment](#deployment)
9. [Maintenance and Updates](#maintenance-and-updates)

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
**Goal:** Set up project structure and basic UI shell

**Tasks:**
- [ ] Initialize Electron + React + TypeScript project
- [ ] Set up development environment and tooling
- [ ] Implement application shell with layout
- [ ] Create basic panel components (empty containers)
- [ ] Set up routing and navigation
- [ ] Configure state management (Redux Toolkit)
- [ ] Set up build and packaging pipeline

**Deliverables:**
- Working Electron app that launches
- Basic panel layout with resizable panels
- Dark/light theme support
- Development hot-reload working

### Phase 2: Core Features (Weeks 3-5)
**Goal:** Implement upload and configuration functionality

**Tasks:**
- [ ] Implement Upload Panel
  - File upload component
  - Drag-and-drop functionality
  - File validation
  - Thumbnail generation
- [ ] Implement Configuration Panel
  - Parameter input controls
  - Sliders and numeric inputs
  - Model file selection
  - Preset management
- [ ] Implement basic Results Viewer
  - Image display canvas
  - Tab navigation
- [ ] Connect to mock backend API
- [ ] Implement basic error handling

**Deliverables:**
- Users can upload images
- Users can configure parameters
- UI properly validates inputs
- Mock detection can be triggered

### Phase 3: Results Visualization (Weeks 6-8)
**Goal:** Implement interactive results display

**Tasks:**
- [ ] Canvas-based image rendering
- [ ] Bounding box visualization
- [ ] Interactive box selection
- [ ] Zoom and pan functionality
- [ ] Filter controls (class, confidence)
- [ ] Info panel for selected detections
- [ ] Multi-image navigation
- [ ] Compare mode implementation

**Deliverables:**
- Interactive visualization of detection results
- Smooth zoom/pan experience
- Filtering works correctly
- Side-by-side comparison mode

### Phase 4: Monitoring Integration (Weeks 9-10)
**Goal:** Integrate Prometheus monitoring

**Tasks:**
- [ ] Prometheus client integration
- [ ] Metrics dashboard components
- [ ] Real-time metric streaming
- [ ] Chart visualizations (time-series)
- [ ] Log viewer component
- [ ] Custom PromQL query interface
- [ ] Alert indicators

**Deliverables:**
- Live metrics display
- Historical charts
- Custom metric queries
- Real-time log streaming

### Phase 5: Export & Polish (Weeks 11-12)
**Goal:** Complete remaining features and polish

**Tasks:**
- [ ] Export functionality
  - Image export with annotations
  - Metrics CSV/JSON export
  - PDF report generation
- [ ] Progress indicators for long operations
- [ ] Keyboard shortcuts
- [ ] Accessibility improvements
- [ ] Performance optimization
- [ ] Error handling refinement
- [ ] User documentation
- [ ] Demo video/screenshots

**Deliverables:**
- Complete export functionality
- Polished, responsive UI
- Comprehensive user documentation
- Installation package

### Phase 6: Testing & Release (Weeks 13-14)
**Goal:** Thorough testing and production release

**Tasks:**
- [ ] Integration testing
- [ ] End-to-end testing
- [ ] Performance testing
- [ ] Accessibility testing
- [ ] User acceptance testing
- [ ] Bug fixes
- [ ] Release notes
- [ ] Package for Windows distribution

**Deliverables:**
- Test coverage >80%
- Windows installer (.exe)
- User manual
- Release announcement

---

## Technology Stack Details

### Core Technologies

#### Electron
**Version:** 28.x or latest stable  
**Purpose:** Cross-platform desktop application framework

**Key Dependencies:**
```json
{
  "electron": "^28.0.0",
  "electron-builder": "^24.0.0",
  "electron-updater": "^6.0.0"
}
```

**Configuration:**
- Main process: Node.js backend for file system, IPC
- Renderer process: React UI with context isolation
- Preload script: Secure IPC bridge

#### React
**Version:** 18.x  
**Purpose:** UI component framework

**Key Dependencies:**
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.20.0"
}
```

**Features Used:**
- Hooks (useState, useEffect, useCallback, useMemo)
- Context API for theme
- Error boundaries
- Concurrent features

#### TypeScript
**Version:** 5.x  
**Purpose:** Type safety and better developer experience

**Configuration:**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "lib": ["ES2020", "DOM"],
    "jsx": "react-jsx",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

### State Management

#### Redux Toolkit
**Version:** 2.x  
**Purpose:** Centralized state management

**Key Features:**
- Slice pattern for modular state
- RTK Query for API calls
- Redux DevTools integration
- Persistence with redux-persist

**Store Structure:**
```typescript
import { configureStore } from '@reduxjs/toolkit';
import uploadReducer from './slices/uploadSlice';
import configReducer from './slices/configSlice';
import detectionReducer from './slices/detectionSlice';
import resultsReducer from './slices/resultsSlice';
import monitoringReducer from './slices/monitoringSlice';

export const store = configureStore({
  reducer: {
    upload: uploadReducer,
    config: configReducer,
    detection: detectionReducer,
    results: resultsReducer,
    monitoring: monitoringReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false, // For File objects
    }),
});
```

### UI Components

#### Material-UI (MUI)
**Version:** 5.x  
**Purpose:** Comprehensive React component library

**Key Components:**
- Button, IconButton, Tooltip
- Slider, TextField, Select
- Dialog, Snackbar, Alert
- Tabs, Drawer, AppBar
- Grid, Box, Stack

**Theming:**
```typescript
import { createTheme, ThemeProvider } from '@mui/material';

const theme = createTheme({
  palette: {
    mode: 'dark', // or 'light'
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
  },
});
```

### Canvas & Visualization

#### Konva.js
**Version:** 9.x  
**Purpose:** Canvas manipulation for image and bounding boxes

**Features:**
- High-performance rendering
- Interactive elements (drag, click)
- Layering support
- Transforms (zoom, pan)

**Basic Usage:**
```typescript
import { Stage, Layer, Image, Rect, Text } from 'react-konva';

function ImageCanvas({ image, detections }) {
  return (
    <Stage width={800} height={600}>
      <Layer>
        <Image image={image} />
        {detections.map((det) => (
          <Rect
            key={det.id}
            x={det.x}
            y={det.y}
            width={det.width}
            height={det.height}
            stroke="red"
            strokeWidth={2}
            onClick={() => handleBoxClick(det)}
          />
        ))}
      </Layer>
    </Stage>
  );
}
```

#### Recharts
**Version:** 2.x  
**Purpose:** React-based charting library for metrics

**Chart Types:**
- LineChart: Time-series metrics
- BarChart: Class distribution
- AreaChart: Confidence distribution
- PieChart: Category breakdown

### API Integration

#### Axios
**Version:** 1.x  
**Purpose:** HTTP client for API calls

**Configuration:**
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle errors globally
    if (error.response?.status === 401) {
      // Handle unauthorized
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## Development Setup

### Prerequisites

1. **Node.js**: Version 18.x or higher
2. **npm or yarn**: Package manager
3. **Git**: Version control
4. **Python**: 3.10+ (for backend)
5. **Visual Studio Code**: Recommended IDE

### Project Initialization

```bash
# Create project directory
mkdir frontend
cd frontend

# Initialize Electron + React + TypeScript project
npx create-electron-app . --template=webpack-typescript

# Install dependencies
npm install react react-dom react-router-dom
npm install @mui/material @emotion/react @emotion/styled
npm install @reduxjs/toolkit react-redux redux-persist
npm install axios
npm install konva react-konva
npm install recharts
npm install date-fns # For date formatting

# Install dev dependencies
npm install -D @types/react @types/react-dom
npm install -D @types/node
npm install -D electron-builder
npm install -D eslint prettier
npm install -D @testing-library/react @testing-library/jest-dom
npm install -D @testing-library/user-event
```

### Project Structure Setup

```bash
# Create directory structure
mkdir -p src/renderer/components/{Upload,Config,Results,Monitoring,Common}
mkdir -p src/renderer/{hooks,services,store,types,utils}
mkdir -p src/main
mkdir -p public/assets
```

### Configuration Files

#### package.json Scripts
```json
{
  "scripts": {
    "start": "electron-forge start",
    "dev": "electron-forge start",
    "build": "electron-forge make",
    "package": "electron-forge package",
    "test": "jest",
    "lint": "eslint src --ext .ts,.tsx",
    "format": "prettier --write \"src/**/*.{ts,tsx,css}\""
  }
}
```

#### ESLint Configuration (.eslintrc.js)
```javascript
module.exports = {
  parser: '@typescript-eslint/parser',
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:@typescript-eslint/recommended',
    'prettier',
  ],
  plugins: ['react', '@typescript-eslint'],
  rules: {
    'react/react-in-jsx-scope': 'off',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
};
```

#### Prettier Configuration (.prettierrc)
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2
}
```

---

## Component Implementation

### Upload Panel Component

**File:** `src/renderer/components/Upload/UploadPanel.tsx`

```typescript
import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Box, Button, Typography, List } from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { addFiles, removeFile, clearFiles } from '../../store/slices/uploadSlice';
import FileListItem from './FileListItem';

const ACCEPTED_FORMATS = {
  'image/jpeg': ['.jpg', '.jpeg'],
  'image/png': ['.png'],
  'image/bmp': ['.bmp'],
  'image/tiff': ['.tiff'],
};

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

export default function UploadPanel() {
  const dispatch = useDispatch();
  const files = useSelector((state) => state.upload.files);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      // Validate files
      const validFiles = acceptedFiles.filter((file) => {
        if (file.size > MAX_FILE_SIZE) {
          // Show error notification
          return false;
        }
        return true;
      });

      dispatch(addFiles(validFiles));
    },
    [dispatch]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_FORMATS,
    multiple: true,
  });

  const handleSelectFolder = async () => {
    // Use Electron IPC to open folder dialog
    const folderPath = await window.electron.selectFolder();
    if (folderPath) {
      const files = await window.electron.getImagesFromFolder(folderPath);
      dispatch(addFiles(files));
    }
  };

  const handleRemoveFile = (fileId: string) => {
    dispatch(removeFile(fileId));
  };

  const handleClearAll = () => {
    dispatch(clearFiles());
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        📁 Upload Images
      </Typography>

      {/* Drop Zone */}
      <Box
        {...getRootProps()}
        sx={{
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.500',
          borderRadius: 2,
          p: 3,
          textAlign: 'center',
          cursor: 'pointer',
          bgcolor: isDragActive ? 'action.hover' : 'background.paper',
          mb: 2,
        }}
      >
        <input {...getInputProps()} />
        <Typography>
          {isDragActive ? 'Drop files here...' : 'Drop files here or click to browse'}
        </Typography>
      </Box>

      {/* Folder Selection */}
      <Button fullWidth variant="outlined" onClick={handleSelectFolder} sx={{ mb: 2 }}>
        📂 Select Folder
      </Button>

      {/* File List */}
      {files.length > 0 && (
        <>
          <Typography variant="subtitle2" gutterBottom>
            Uploaded Images ({files.length}):
          </Typography>
          <List dense>
            {files.map((file) => (
              <FileListItem
                key={file.id}
                file={file}
                onRemove={() => handleRemoveFile(file.id)}
              />
            ))}
          </List>
          <Button fullWidth variant="text" onClick={handleClearAll} color="error">
            Clear All
          </Button>
        </>
      )}
    </Box>
  );
}
```

### Configuration Panel Component

**File:** `src/renderer/components/Config/ConfigPanel.tsx`

```typescript
import React from 'react';
import {
  Box,
  Typography,
  TextField,
  Slider,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Select,
  MenuItem,
} from '@mui/material';
import { ExpandMore as ExpandMoreIcon } from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { updateConfig, loadPreset } from '../../store/slices/configSlice';

export default function ConfigPanel() {
  const dispatch = useDispatch();
  const config = useSelector((state) => state.config);

  const handleModelSelect = async () => {
    const modelPath = await window.electron.selectFile({
      filters: [{ name: 'Model Files', extensions: ['pt', 'pth'] }],
    });
    if (modelPath) {
      dispatch(updateConfig({ modelPath }));
    }
  };

  const handleSliderChange = (field: string) => (event: Event, value: number | number[]) => {
    dispatch(updateConfig({ [field]: value as number }));
  };

  const handleRunDetection = () => {
    // Dispatch action to start detection
    dispatch({ type: 'detection/start' });
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        ⚙️ Configuration
      </Typography>

      {/* Model Selection */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Model
        </Typography>
        <Button variant="outlined" fullWidth onClick={handleModelSelect}>
          {config.modelPath ? config.modelPath.split('/').pop() : 'Select Model...'}
        </Button>
      </Box>

      {/* YOLO Parameters */}
      <Typography variant="subtitle2" gutterBottom>
        YOLO Parameters
      </Typography>

      <Box sx={{ mb: 2 }}>
        <Typography variant="caption">Confidence: {config.confidence}</Typography>
        <Slider
          value={config.confidence}
          onChange={handleSliderChange('confidence')}
          min={0.01}
          max={1.0}
          step={0.01}
          marks={[
            { value: 0.01, label: '0.01' },
            { value: 1.0, label: '1.0' },
          ]}
        />
      </Box>

      <Box sx={{ mb: 2 }}>
        <Typography variant="caption">IoU Threshold: {config.iouThreshold}</Typography>
        <Slider
          value={config.iouThreshold}
          onChange={handleSliderChange('iouThreshold')}
          min={0.01}
          max={1.0}
          step={0.01}
          marks={[
            { value: 0.01, label: '0.01' },
            { value: 1.0, label: '1.0' },
          ]}
        />
      </Box>

      {/* SAHI Parameters */}
      <Typography variant="subtitle2" gutterBottom>
        SAHI Parameters
      </Typography>

      <Box sx={{ mb: 1 }}>
        <TextField
          label="Slice Height"
          type="number"
          value={config.sliceHeight}
          onChange={(e) => dispatch(updateConfig({ sliceHeight: Number(e.target.value) }))}
          fullWidth
          size="small"
        />
      </Box>

      <Box sx={{ mb: 1 }}>
        <TextField
          label="Slice Width"
          type="number"
          value={config.sliceWidth}
          onChange={(e) => dispatch(updateConfig({ sliceWidth: Number(e.target.value) }))}
          fullWidth
          size="small"
        />
      </Box>

      <Box sx={{ mb: 2 }}>
        <Typography variant="caption">Overlap Height: {config.overlapHeight}</Typography>
        <Slider
          value={config.overlapHeight}
          onChange={handleSliderChange('overlapHeight')}
          min={0.0}
          max={0.5}
          step={0.01}
        />
      </Box>

      <Box sx={{ mb: 2 }}>
        <Typography variant="caption">Overlap Width: {config.overlapWidth}</Typography>
        <Slider
          value={config.overlapWidth}
          onChange={handleSliderChange('overlapWidth')}
          min={0.0}
          max={0.5}
          step={0.01}
        />
      </Box>

      {/* Advanced Options */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="subtitle2">Advanced Options</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Select
            label="Device"
            value={config.device}
            onChange={(e) => dispatch(updateConfig({ device: e.target.value }))}
            fullWidth
            size="small"
          >
            <MenuItem value="cuda">CUDA (GPU)</MenuItem>
            <MenuItem value="cpu">CPU</MenuItem>
          </Select>
        </AccordionDetails>
      </Accordion>

      {/* Presets */}
      <Box sx={{ mt: 2, mb: 2, display: 'flex', gap: 1 }}>
        <Button variant="text" size="small">
          Load Preset
        </Button>
        <Button variant="text" size="small">
          Save...
        </Button>
      </Box>

      {/* Run Button */}
      <Button
        variant="contained"
        fullWidth
        size="large"
        onClick={handleRunDetection}
        disabled={!config.modelPath}
        sx={{ mt: 2 }}
      >
        ▶ Run Detection
      </Button>
    </Box>
  );
}
```

### Results Viewer Component

**File:** `src/renderer/components/Results/ResultsViewer.tsx`

```typescript
import React, { useState } from 'react';
import { Box, Tabs, Tab, Typography } from '@mui/material';
import { useSelector } from 'react-redux';
import ImageCanvas from './ImageCanvas';
import FilterControls from './FilterControls';
import InfoPanel from './InfoPanel';

type ViewMode = 'input' | 'labels' | 'output' | 'compare';

export default function ResultsViewer() {
  const [viewMode, setViewMode] = useState<ViewMode>('output');
  const results = useSelector((state) => state.results);
  const detection = useSelector((state) => state.detection);

  if (detection.status === 'idle') {
    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
        }}
      >
        <Typography variant="h6" color="text.secondary">
          Welcome to Object Detection
          <br />
          <br />
          Please upload images to begin
        </Typography>
      </Box>
    );
  }

  if (detection.status === 'running') {
    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
        }}
      >
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h6">⏳ Running Object Detection...</Typography>
          <Typography variant="body2" color="text.secondary">
            {detection.currentStage}
          </Typography>
          <Box sx={{ mt: 2, width: 300 }}>
            {/* Progress bar component */}
          </Box>
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Tabs */}
      <Tabs value={viewMode} onChange={(e, v) => setViewMode(v)}>
        <Tab label="Input" value="input" />
        <Tab label="Labels" value="labels" />
        <Tab label="Output" value="output" />
        <Tab label="Compare" value="compare" />
      </Tabs>

      {/* Filter Controls */}
      <FilterControls />

      {/* Main Canvas Area */}
      <Box sx={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        <Box sx={{ flex: 1 }}>
          <ImageCanvas viewMode={viewMode} />
        </Box>

        {/* Info Panel (sidebar) */}
        {results.selectedDetection && (
          <Box sx={{ width: 250, borderLeft: 1, borderColor: 'divider' }}>
            <InfoPanel detection={results.selectedDetection} />
          </Box>
        )}
      </Box>

      {/* Stats Footer */}
      <Box
        sx={{
          p: 1,
          borderTop: 1,
          borderColor: 'divider',
          display: 'flex',
          justifyContent: 'space-between',
        }}
      >
        <Typography variant="caption">
          Total Objects: {results.detections?.length || 0}
        </Typography>
        <Typography variant="caption">
          Classes: {results.uniqueClasses?.length || 0}
        </Typography>
        <Typography variant="caption">
          Avg Conf: {results.avgConfidence?.toFixed(2) || 'N/A'}
        </Typography>
      </Box>
    </Box>
  );
}
```

---

## Backend Integration

### API Service

**File:** `src/renderer/services/api.ts`

```typescript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for long-running operations
});

export interface DetectionConfig {
  modelPath: string;
  confidence: number;
  iouThreshold: number;
  sliceHeight: number;
  sliceWidth: number;
  overlapHeight: number;
  overlapWidth: number;
  device: 'cuda' | 'cpu';
}

export interface DetectionResult {
  jobId: string;
  imageId: string;
  detections: Detection[];
  metrics: {
    inferenceTime: number;
    totalDetections: number;
    classes: string[];
  };
}

export interface Detection {
  id: string;
  class: string;
  confidence: number;
  bbox: [number, number, number, number]; // x, y, w, h
  area: number;
}

class DetectionAPI {
  /**
   * Upload images to the backend
   */
  async uploadImages(files: File[]): Promise<{ jobId: string }> {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await api.post('/detection/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  /**
   * Start detection with configuration
   */
  async runDetection(jobId: string, config: DetectionConfig): Promise<void> {
    await api.post(`/detection/run`, {
      jobId,
      config,
    });
  }

  /**
   * Get detection status
   */
  async getStatus(jobId: string): Promise<{
    status: 'pending' | 'running' | 'complete' | 'error';
    progress: number;
    stage: string;
  }> {
    const response = await api.get(`/detection/status/${jobId}`);
    return response.data;
  }

  /**
   * Get detection results
   */
  async getResults(jobId: string): Promise<DetectionResult[]> {
    const response = await api.get(`/detection/results/${jobId}`);
    return response.data;
  }

  /**
   * Export results in various formats
   */
  async exportResults(
    jobId: string,
    format: 'images' | 'csv' | 'json' | 'pdf'
  ): Promise<Blob> {
    const response = await api.post(
      `/export`,
      { jobId, format },
      {
        responseType: 'blob',
      }
    );
    return response.data;
  }

  /**
   * List available models
   */
  async listModels(): Promise<Array<{ name: string; path: string; mAP?: number }>> {
    const response = await api.get('/models');
    return response.data;
  }
}

export default new DetectionAPI();
```

### Redux Integration with RTK Query

**File:** `src/renderer/store/slices/detectionSlice.ts`

```typescript
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import detectionAPI, { DetectionResult, DetectionConfig } from '../../services/api';

interface DetectionState {
  jobId: string | null;
  status: 'idle' | 'uploading' | 'running' | 'complete' | 'error';
  progress: number;
  currentStage: string;
  results: DetectionResult[] | null;
  error: string | null;
}

const initialState: DetectionState = {
  jobId: null,
  status: 'idle',
  progress: 0,
  currentStage: '',
  results: null,
  error: null,
};

// Async thunks
export const uploadAndRun = createAsyncThunk(
  'detection/uploadAndRun',
  async (
    { files, config }: { files: File[]; config: DetectionConfig },
    { dispatch }
  ) => {
    // Upload files
    const { jobId } = await detectionAPI.uploadImages(files);

    // Start detection
    await detectionAPI.runDetection(jobId, config);

    // Poll for status
    let status = await detectionAPI.getStatus(jobId);
    while (status.status === 'running' || status.status === 'pending') {
      dispatch(updateProgress({ progress: status.progress, stage: status.stage }));
      await new Promise((resolve) => setTimeout(resolve, 1000)); // Poll every second
      status = await detectionAPI.getStatus(jobId);
    }

    if (status.status === 'error') {
      throw new Error('Detection failed');
    }

    // Get results
    const results = await detectionAPI.getResults(jobId);
    return { jobId, results };
  }
);

const detectionSlice = createSlice({
  name: 'detection',
  initialState,
  reducers: {
    updateProgress(state, action: PayloadAction<{ progress: number; stage: string }>) {
      state.progress = action.payload.progress;
      state.currentStage = action.payload.stage;
    },
    resetDetection(state) {
      return initialState;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(uploadAndRun.pending, (state) => {
        state.status = 'uploading';
        state.error = null;
      })
      .addCase(uploadAndRun.fulfilled, (state, action) => {
        state.status = 'complete';
        state.jobId = action.payload.jobId;
        state.results = action.payload.results;
        state.progress = 100;
      })
      .addCase(uploadAndRun.rejected, (state, action) => {
        state.status = 'error';
        state.error = action.error.message || 'Detection failed';
      });
  },
});

export const { updateProgress, resetDetection } = detectionSlice.actions;
export default detectionSlice.reducer;
```

---

## Prometheus Integration

### Prometheus Client Service

**File:** `src/renderer/services/prometheus.ts`

```typescript
import axios from 'axios';

const PROMETHEUS_URL = process.env.REACT_APP_PROMETHEUS_URL || 'http://localhost:9090';

export interface PrometheusMetric {
  metric: Record<string, string>;
  value: [number, string]; // [timestamp, value]
}

export interface PrometheusQueryResult {
  resultType: 'matrix' | 'vector';
  result: PrometheusMetric[];
}

class PrometheusService {
  /**
   * Execute instant query
   */
  async query(promQL: string): Promise<PrometheusQueryResult> {
    const response = await axios.get(`${PROMETHEUS_URL}/api/v1/query`, {
      params: { query: promQL },
    });

    if (response.data.status !== 'success') {
      throw new Error('Prometheus query failed');
    }

    return response.data.data;
  }

  /**
   * Execute range query for time-series data
   */
  async queryRange(
    promQL: string,
    start: number,
    end: number,
    step: string = '15s'
  ): Promise<PrometheusQueryResult> {
    const response = await axios.get(`${PROMETHEUS_URL}/api/v1/query_range`, {
      params: {
        query: promQL,
        start,
        end,
        step,
      },
    });

    if (response.data.status !== 'success') {
      throw new Error('Prometheus query failed');
    }

    return response.data.data;
  }

  /**
   * Get current inference metrics
   */
  async getCurrentMetrics() {
    const [inferenceTime, objectsDetected, gpuUsage, memoryUsage] = await Promise.all([
      this.query('detection_inference_duration_seconds'),
      this.query('detection_objects_total'),
      this.query('gpu_utilization_percent'),
      this.query('memory_usage_bytes'),
    ]);

    return {
      inferenceTime: parseFloat(inferenceTime.result[0]?.value[1] || '0'),
      objectsDetected: parseInt(inferenceTime.result[0]?.value[1] || '0'),
      gpuUsage: parseFloat(gpuUsage.result[0]?.value[1] || '0'),
      memoryUsage: parseInt(memoryUsage.result[0]?.value[1] || '0'),
    };
  }

  /**
   * Get historical metrics for charts
   */
  async getHistoricalMetrics(metric: string, hours: number = 1) {
    const end = Math.floor(Date.now() / 1000);
    const start = end - hours * 3600;

    return this.queryRange(metric, start, end);
  }

  /**
   * Stream metrics using Server-Sent Events
   */
  streamMetrics(callback: (metrics: any) => void): EventSource {
    const eventSource = new EventSource(`${PROMETHEUS_URL}/api/v1/stream`);

    eventSource.onmessage = (event) => {
      const metrics = JSON.parse(event.data);
      callback(metrics);
    };

    eventSource.onerror = (error) => {
      console.error('Prometheus stream error:', error);
      eventSource.close();
    };

    return eventSource;
  }
}

export default new PrometheusService();
```

### Monitoring Dashboard Component

**File:** `src/renderer/components/Monitoring/MonitoringDashboard.tsx`

```typescript
import React, { useEffect, useState } from 'react';
import { Box, Typography, Grid, Paper } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import prometheusService from '../../services/prometheus';

export default function MonitoringDashboard() {
  const [metrics, setMetrics] = useState<any>(null);
  const [chartData, setChartData] = useState<any[]>([]);

  useEffect(() => {
    // Fetch current metrics
    const fetchMetrics = async () => {
      const data = await prometheusService.getCurrentMetrics();
      setMetrics(data);
    };

    // Fetch historical data for chart
    const fetchChartData = async () => {
      const data = await prometheusService.getHistoricalMetrics(
        'detection_inference_duration_seconds',
        1
      );
      const formatted = data.result[0]?.values.map(([timestamp, value]: any) => ({
        time: new Date(timestamp * 1000).toLocaleTimeString(),
        duration: parseFloat(value),
      }));
      setChartData(formatted || []);
    };

    fetchMetrics();
    fetchChartData();

    // Set up periodic refresh
    const interval = setInterval(() => {
      fetchMetrics();
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  if (!metrics) {
    return <Typography>Loading metrics...</Typography>;
  }

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        📊 Monitoring Dashboard
      </Typography>

      <Grid container spacing={2}>
        {/* Performance Metrics */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle2">Performance Metrics</Typography>
            <Typography variant="body2">
              Inference Time: {metrics.inferenceTime.toFixed(2)}ms
            </Typography>
            <Typography variant="body2">
              GPU Utilization: {metrics.gpuUsage.toFixed(1)}%
            </Typography>
            <Typography variant="body2">
              Memory Usage: {(metrics.memoryUsage / 1024 / 1024 / 1024).toFixed(2)}GB
            </Typography>
          </Paper>
        </Grid>

        {/* Detection Statistics */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle2">Detection Statistics</Typography>
            <Typography variant="body2">
              Total Detections: {metrics.objectsDetected}
            </Typography>
          </Paper>
        </Grid>

        {/* Chart */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Inference Duration (Last Hour)
            </Typography>
            <LineChart width={800} height={300} data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="duration" stroke="#8884d8" />
            </LineChart>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
```

---

## Testing Strategy

### Unit Tests

**Example: Upload Component Test**

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import UploadPanel from '../components/Upload/UploadPanel';

const mockStore = configureStore([]);

describe('UploadPanel', () => {
  let store: any;

  beforeEach(() => {
    store = mockStore({
      upload: {
        files: [],
        uploading: false,
        error: null,
      },
    });
  });

  it('renders upload panel', () => {
    render(
      <Provider store={store}>
        <UploadPanel />
      </Provider>
    );

    expect(screen.getByText('📁 Upload Images')).toBeInTheDocument();
  });

  it('handles file drop', async () => {
    render(
      <Provider store={store}>
        <UploadPanel />
      </Provider>
    );

    const file = new File(['dummy'], 'test.jpg', { type: 'image/jpeg' });
    const dropzone = screen.getByText(/Drop files here/);

    fireEvent.drop(dropzone, { dataTransfer: { files: [file] } });

    await waitFor(() => {
      const actions = store.getActions();
      expect(actions).toContainEqual(
        expect.objectContaining({
          type: 'upload/addFiles',
        })
      );
    });
  });
});
```

### Integration Tests

**Example: Detection Flow Test**

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { store } from '../store/store';
import App from '../App';
import * as api from '../services/api';

jest.mock('../services/api');

describe('Detection Flow Integration', () => {
  it('completes full detection workflow', async () => {
    // Mock API responses
    (api.default.uploadImages as jest.Mock).mockResolvedValue({ jobId: 'test-job-123' });
    (api.default.runDetection as jest.Mock).mockResolvedValue(undefined);
    (api.default.getStatus as jest.Mock).mockResolvedValue({
      status: 'complete',
      progress: 100,
    });
    (api.default.getResults as jest.Mock).mockResolvedValue([
      {
        jobId: 'test-job-123',
        detections: [
          { id: '1', class: 'car', confidence: 0.95, bbox: [10, 20, 50, 60] },
        ],
      },
    ]);

    render(
      <Provider store={store}>
        <App />
      </Provider>
    );

    // Upload file
    const file = new File(['dummy'], 'test.jpg', { type: 'image/jpeg' });
    const input = screen.getByLabelText(/upload/i);
    await userEvent.upload(input, file);

    // Select model
    const modelButton = screen.getByText(/Select Model/);
    fireEvent.click(modelButton);

    // Run detection
    const runButton = screen.getByText(/Run Detection/);
    fireEvent.click(runButton);

    // Wait for completion
    await waitFor(
      () => {
        expect(screen.getByText(/Total Objects: 1/)).toBeInTheDocument();
      },
      { timeout: 5000 }
    );
  });
});
```

### E2E Tests (Playwright)

```typescript
import { test, expect, _electron as electron } from '@playwright/test';

test('E2E: Complete detection workflow', async () => {
  // Launch Electron app
  const app = await electron.launch({ args: ['.'] });
  const window = await app.firstWindow();

  // Upload image
  await window.click('text=Browse Files');
  // Handle file dialog...

  // Configure parameters
  await window.fill('[data-testid="confidence-input"]', '0.5');

  // Run detection
  await window.click('text=Run Detection');

  // Wait for results
  await window.waitForSelector('text=Detection Complete', { timeout: 30000 });

  // Verify results displayed
  const detectionsText = await window.textContent('[data-testid="detections-count"]');
  expect(detectionsText).toContain('Total Objects:');

  await app.close();
});
```

---

## Deployment

### Building for Windows

**electron-builder Configuration**

**File:** `electron-builder.json`

```json
{
  "appId": "com.neurosymbolic.objectdetection",
  "productName": "Object Detection App",
  "directories": {
    "output": "dist"
  },
  "files": [
    "build/**/*",
    "node_modules/**/*",
    "package.json"
  ],
  "win": {
    "target": [
      {
        "target": "nsis",
        "arch": ["x64"]
      },
      {
        "target": "portable",
        "arch": ["x64"]
      }
    ],
    "icon": "public/assets/icon.ico"
  },
  "nsis": {
    "oneClick": false,
    "allowToChangeInstallationDirectory": true,
    "createDesktopShortcut": true,
    "createStartMenuShortcut": true
  }
}
```

**Build Commands**

```bash
# Development build
npm run build

# Production build for Windows
npm run build:win

# Build portable version
npm run build:portable
```

### Distribution

**Package Structure:**
```
ObjectDetectionApp-1.0.0-Setup.exe     # Installer
ObjectDetectionApp-1.0.0-Portable.exe  # Portable version
```

**Installation Package Should Include:**
- Application binaries
- Required DLLs and dependencies
- Desktop shortcut
- Start menu entry
- Uninstaller
- README and license

### Auto-updates

```typescript
// Configure auto-updater in main process
import { autoUpdater } from 'electron-updater';

autoUpdater.checkForUpdatesAndNotify();

autoUpdater.on('update-available', () => {
  // Notify user
});

autoUpdater.on('update-downloaded', () => {
  // Prompt user to restart
});
```

---

## Maintenance and Updates

### Version Management

Follow **Semantic Versioning (SemVer)**:
- **Major (X.0.0)**: Breaking changes
- **Minor (1.X.0)**: New features, backward compatible
- **Patch (1.0.X)**: Bug fixes

### Release Checklist

- [ ] Update version in `package.json`
- [ ] Update CHANGELOG.md
- [ ] Run full test suite
- [ ] Build production packages
- [ ] Test installer on clean Windows machine
- [ ] Create Git tag (`v1.0.0`)
- [ ] Push tag to trigger CI/CD
- [ ] Create GitHub release with binaries
- [ ] Update documentation

### Monitoring Production

- **Error Tracking**: Integrate Sentry or similar
- **Analytics**: Track feature usage (opt-in)
- **Crash Reports**: Electron crash reporter
- **User Feedback**: In-app feedback form

### Future Improvements

1. **Performance Optimization**
   - Lazy load components
   - Virtualize long lists
   - Optimize canvas rendering
   - Reduce bundle size

2. **Feature Additions**
   - Video support
   - Batch processing queue
   - Cloud storage integration
   - Team collaboration

3. **Developer Experience**
   - Storybook for component development
   - E2E test coverage
   - CI/CD pipeline
   - Automated releases

---

## Conclusion

This implementation guide provides a detailed roadmap for building the Windows desktop application for object detection. It covers:

✅ Complete implementation phases  
✅ Technology stack and setup  
✅ Component code examples  
✅ API integration patterns  
✅ Prometheus monitoring integration  
✅ Testing strategies  
✅ Deployment process  
✅ Maintenance guidelines  

Follow this guide alongside the [Frontend UI Design](frontend_ui_design.md) document to ensure a successful implementation that meets all requirements and design specifications.
