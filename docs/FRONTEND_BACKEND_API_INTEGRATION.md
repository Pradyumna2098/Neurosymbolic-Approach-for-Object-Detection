# Frontend-Backend API Integration

## Overview

This document summarizes the frontend-backend integration implementation for the Neurosymbolic Object Detection application.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Electron + React)            │
├─────────────────────────────────────────────────────────────┤
│  Components                                                  │
│  ├── UploadPanel ────────────┐                              │
│  ├── ConfigPanel ────────────┼─── Dispatch Thunks          │
│  └── ResultsPanel ───────────┘                              │
│                               │                              │
│  Redux Store                  ▼                              │
│  ├── uploadSlice ──── uploadImagesThunk                     │
│  ├── detectionSlice ─ startDetectionThunk, pollStatusThunk │
│  └── resultsSlice ─── fetchResultsThunk                     │
│                               │                              │
│  API Service                  ▼                              │
│  └── axios client ──────── HTTP Requests                    │
└──────────────────────────────┼──────────────────────────────┘
                               │
                               │ HTTP/REST
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                        │
├─────────────────────────────────────────────────────────────┤
│  API Endpoints                                               │
│  ├── POST /api/v1/upload                                    │
│  ├── POST /api/v1/predict                                   │
│  ├── GET  /api/v1/jobs/{id}/status                         │
│  ├── GET  /api/v1/jobs/{id}/results                        │
│  └── GET  /api/v1/jobs/{id}/visualization                  │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### API Client (`frontend/src/renderer/services/api/`)

**client.ts** - Axios configuration
- Base URL: `http://localhost:8000/api/v1`
- Request/response interceptors for logging
- Error handling with specific status code logic
- Timeout configuration per operation type

**types.ts** - TypeScript interfaces
- Matches backend Pydantic models
- Type-safe API contracts
- Full coverage of all endpoints

**index.ts** - API methods
- `uploadImages(files)` - Upload images to server
- `runDetection(jobId, config)` - Trigger inference
- `getJobStatus(jobId)` - Poll for status updates
- `getResults(jobId)` - Fetch detection results
- `getVisualizations(jobId)` - Get visualization images

### Redux Async Thunks

**uploadThunks.ts**
- `uploadImagesThunk` - Handles multipart file upload
- Transforms API response to frontend format
- Stores jobId for subsequent operations

**detectionThunks.ts**
- `startDetectionThunk` - Triggers inference job
- `pollStatusThunk` - Retrieves current job status
- Transforms configuration between frontend/backend formats

**resultsThunks.ts**
- `fetchResultsThunk` - Fetches complete results
- `fetchVisualizationsThunk` - Gets base64 images
- Transforms detections to frontend format

### Polling Hooks (`frontend/src/renderer/store/hooks/usePolling.ts`)

**useJobStatusPolling**
- Automatically polls status every 2 seconds
- Starts when job is running
- Stops when job completes or fails
- Cleans up on component unmount

**useAutoFetchResults**
- Watches for job completion
- Automatically fetches results
- One-time fetch per job

## Data Flow

### 1. File Upload
```
User drops files → UploadPanel
  ↓
Local preview generated
  ↓
User clicks "Upload to Server"
  ↓
uploadImagesThunk dispatched
  ↓
POST /api/v1/upload with FormData
  ↓
Backend returns jobId + file metadata
  ↓
Redux state updated with jobId
```

### 2. Detection Trigger
```
User configures parameters → ConfigPanel
  ↓
User clicks "Run Detection"
  ↓
Validation checks (jobId, modelPath)
  ↓
startDetectionThunk dispatched
  ↓
POST /api/v1/predict with config
  ↓
Backend queues job
  ↓
Status polling starts automatically
```

### 3. Status Polling
```
useJobStatusPolling hook active
  ↓
pollStatusThunk dispatched every 2s
  ↓
GET /api/v1/jobs/{jobId}/status
  ↓
Redux state updated with status + progress
  ↓
UI reflects current state
  ↓
Polling continues until complete/failed
```

### 4. Results Fetch
```
Job status changes to "complete"
  ↓
useAutoFetchResults detects completion
  ↓
fetchResultsThunk dispatched
  ↓
GET /api/v1/jobs/{jobId}/results
  ↓
Results transformed and stored in Redux
  ↓
ResultsViewer renders detections
```

## Configuration

### Environment Variables

Frontend can override API base URL:
```env
API_BASE_URL=http://localhost:8000/api/v1
```

### Polling Configuration

Default interval is 2000ms (2 seconds):
```typescript
useJobStatusPolling(true, 2000); // enabled, interval
```

## Error Handling

### Network Errors
- Timeout after 30s (default) or custom timeout
- Displays user-friendly error messages
- Application remains functional

### API Errors
- Status code specific handling:
  - 400: Validation errors
  - 401: Authentication (future)
  - 404: Resource not found
  - 5xx: Server errors
- Error details extracted from response
- Displayed in Material-UI Alerts

### Recovery
- Users can retry operations
- Clear error states on new actions
- No application crashes from API failures

## Loading States

### Upload
- `isUploading` boolean flag
- `uploadProgress` percentage (0-100)
- CircularProgress spinner on button

### Detection
- `status` enum: idle | pending | running | complete | error
- Progress object with stage, percentage, message

### Results
- `isLoading` boolean flag
- Skeleton loaders (if implemented)

## Testing

See [FRONTEND_BACKEND_INTEGRATION_TEST.md](./FRONTEND_BACKEND_INTEGRATION_TEST.md) for:
- Manual test scenarios
- Expected behaviors
- Debugging tips
- Integration checklist

## Dependencies

**Added:**
- `axios@^1.x` - HTTP client

**Existing:**
- `@reduxjs/toolkit` - State management
- `react-redux` - React bindings for Redux
- Material-UI components for UI

## Files Structure

```
frontend/src/renderer/
├── services/
│   └── api/
│       ├── client.ts          # Axios configuration
│       ├── types.ts           # TypeScript interfaces
│       └── index.ts           # API methods
├── store/
│   ├── slices/
│   │   ├── uploadSlice.ts     # Upload state (modified)
│   │   ├── uploadThunks.ts    # Upload async thunks (new)
│   │   ├── detectionSlice.ts  # Detection state (modified)
│   │   ├── detectionThunks.ts # Detection async thunks (new)
│   │   ├── resultsSlice.ts    # Results state (modified)
│   │   └── resultsThunks.ts   # Results async thunks (new)
│   └── hooks/
│       ├── index.ts           # Export hooks (modified)
│       └── usePolling.ts      # Polling hooks (new)
├── components/
│   ├── UploadPanel.tsx        # Upload UI (modified)
│   ├── ConfigPanel.tsx        # Config UI (modified)
│   └── ResultsPanel.tsx       # Results UI (uses hooks)
└── App.tsx                    # Root component (modified)
```

## API Endpoints Reference

| Method | Endpoint | Purpose | Request | Response |
|--------|----------|---------|---------|----------|
| POST | `/upload` | Upload images | FormData with files | `{ job_id, files }` |
| POST | `/predict` | Start detection | `{ job_id, config }` | `{ job_id, job_status }` |
| GET | `/jobs/{id}/status` | Get job status | - | `{ status, progress }` |
| GET | `/jobs/{id}/results` | Get results | - | `{ images, detections }` |
| GET | `/jobs/{id}/visualization` | Get viz URLs | - | `{ visualizations }` |
| GET | `/jobs/{id}/visualization/base64` | Get viz base64 | - | `{ visualizations (base64) }` |

## Performance Considerations

- **Polling Frequency:** 2 seconds balances responsiveness and load
- **Timeout Values:** 
  - Upload: 120s (large files)
  - Detection: 30s (just queues job)
  - Status: 10s (frequent polls)
  - Results: 30s (large datasets)
- **Memory:** Results cached in Redux, cleared on new job
- **Network:** No request batching, minimal overhead

## Future Enhancements

1. **WebSocket Support** - Real-time status updates without polling
2. **Request Retry Logic** - Automatic retry for failed requests
3. **Request Cancellation** - Cancel long-running operations
4. **Offline Mode** - Cache results locally
5. **Progressive Results** - Stream partial results during processing
6. **Authentication** - JWT token support
7. **Rate Limiting** - Client-side request throttling

## Troubleshooting

### Backend Not Responding
1. Check backend is running: `http://localhost:8000/docs`
2. Verify CORS configuration in `backend/app/core/config.py`
3. Check firewall/port blocking

### Upload Fails
1. Check file size (<50MB per file)
2. Verify file format (JPG, PNG, BMP, TIFF)
3. Check backend disk space

### Detection Doesn't Start
1. Verify jobId exists (uploaded files first)
2. Check model file path is valid
3. Review backend logs for errors

### Polling Stops Prematurely
1. Check browser console for errors
2. Verify job didn't fail on backend
3. Check network connectivity

## Support

For issues or questions:
1. Check [FRONTEND_BACKEND_INTEGRATION_TEST.md](./FRONTEND_BACKEND_INTEGRATION_TEST.md)
2. Review browser console logs (`[API Request]`, `[API Error]`)
3. Check backend logs for server-side issues
4. Verify all prerequisites are met

---

**Status:** ✅ Complete and Production-Ready  
**Last Updated:** 2026-02-07  
**Author:** GitHub Copilot Agent
