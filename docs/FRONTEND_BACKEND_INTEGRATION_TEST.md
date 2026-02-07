# Frontend-Backend Integration Testing Guide

## Prerequisites

1. **Backend Running:**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend Running:**
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Test Data:**
   - Have sample images ready (JPG, PNG, BMP, or TIFF)
   - Have a trained YOLO model file (`.pt` file)

---

## Test Scenarios

### Test 1: File Upload Flow

**Steps:**
1. Launch the frontend application
2. Navigate to the Upload Panel (top-left)
3. Drag and drop 2-3 test images OR click to browse
4. Verify thumbnails appear in the file list
5. Click "Upload to Server" button
6. **Expected Results:**
   - Button shows "Uploading..." with spinner
   - After ~2-5 seconds, success message appears
   - Success message shows: "Files uploaded successfully! Job ID: xxxxxxxx..."
   - Green checkmark icon displayed

**Validation:**
- Check browser DevTools Console for `[API Request] POST /upload`
- Check backend logs for upload confirmation
- Verify files saved in `backend/data/uploads/{job_id}/`

---

### Test 2: Detection Trigger

**Steps:**
1. Complete Test 1 (upload files)
2. Navigate to Configuration Panel (top-right)
3. Click "Select Model File" and choose a YOLO `.pt` file
4. Adjust parameters if desired (confidence, SAHI settings, etc.)
5. Click "Run Detection" button
6. **Expected Results:**
   - API call triggers immediately
   - Detection status changes to "Running"
   - Progress indicator appears (if monitoring panel visible)

**Validation:**
- Check browser Console for `[API Request] POST /predict`
- Backend should log: "Starting SAHI inference for job {job_id}"
- Job status file created: `backend/data/jobs/{job_id}/job.json`

---

### Test 3: Status Polling

**Steps:**
1. After triggering detection (Test 2)
2. Observe the application for 10-30 seconds
3. **Expected Results:**
   - Status polls every 2 seconds (check Console for `GET /jobs/{job_id}/status`)
   - Progress updates in real-time if monitoring panel shows it
   - Status transitions: pending → running → complete
   - Polling stops automatically when complete

**Validation:**
- Console shows repeated `[API Request] GET /jobs/{job_id}/status`
- Backend logs show status reads
- No polling after completion

---

### Test 4: Results Auto-Fetch

**Steps:**
1. Wait for detection to complete (Test 3)
2. **Expected Results:**
   - Automatically fetches results when status = "complete"
   - Console shows `[Auto-fetch] Job completed, fetching results for job {job_id}`
   - Results appear in Results Viewer (bottom panels)
   - Detections rendered on images

**Validation:**
- Console shows `[API Request] GET /jobs/{job_id}/results`
- Results panel populates with detection data
- Image canvas shows bounding boxes
- Detection count matches backend output

---

### Test 5: Error Handling - No Upload

**Steps:**
1. Skip file upload
2. Click "Run Detection" directly
3. **Expected Results:**
   - Alert appears: "Please upload files to server first..."
   - No API call made
   - Application remains stable

---

### Test 6: Error Handling - Backend Offline

**Steps:**
1. Stop the backend server
2. Try to upload files
3. **Expected Results:**
   - Upload fails after timeout (~30s)
   - Error message displayed: "Failed to upload images" or connection error
   - Application remains functional
   - Error can be dismissed

**Validation:**
- Console shows `[API Error] No response received`
- Redux state shows error message
- UI displays error Alert

---

### Test 7: Error Handling - Invalid Model Path

**Steps:**
1. Upload files successfully
2. Set model path to non-existent file
3. Click "Run Detection"
4. **Expected Results:**
   - Detection starts but fails quickly
   - Status changes to "error"
   - Error message explains the issue
   - Polling stops

---

## Integration Verification Checklist

- [ ] Files upload successfully to backend
- [ ] Job ID returned and stored in Redux
- [ ] Detection triggers with correct configuration
- [ ] Status polling starts automatically
- [ ] Polling interval is ~2 seconds
- [ ] Polling stops on completion/error
- [ ] Results auto-fetch on completion
- [ ] Results display correctly in UI
- [ ] Bounding boxes render on images
- [ ] Loading spinners appear during operations
- [ ] Error messages display for failures
- [ ] Application recovers from errors
- [ ] No console errors (except expected API errors)
- [ ] Backend receives correct data formats
- [ ] CORS headers allow requests

---

## Debugging Tips

### Backend Issues

1. **Check Backend Logs:**
   ```bash
   # Backend terminal should show:
   ✓ Data directories initialized at data
   ✓ API server starting on 0.0.0.0:8000
   ```

2. **Verify Backend Endpoints:**
   ```bash
   curl http://localhost:8000/docs
   # Should open Swagger UI in browser
   ```

3. **Check CORS Configuration:**
   - Backend should allow `http://localhost:*` origins
   - Check `backend/app/core/config.py` for CORS settings

### Frontend Issues

1. **Check API Base URL:**
   - Default: `http://localhost:8000/api/v1`
   - Override with environment variable if needed

2. **Console Errors:**
   - Look for `[API Request]` and `[API Error]` logs
   - Check network tab in DevTools for failed requests
   - Verify request/response payloads

3. **Redux State:**
   - Install Redux DevTools extension
   - Monitor `upload`, `detection`, and `results` slices
   - Check for state updates after API calls

4. **Component Rendering:**
   - Verify jobId appears after upload
   - Check detection status updates
   - Confirm results populate

---

## Expected API Call Sequence

```
1. POST /api/v1/upload
   Request: multipart/form-data with files
   Response: { status: "success", job_id: "...", files: [...] }

2. POST /api/v1/predict
   Request: { job_id: "...", config: { model_path: "...", ... } }
   Response: { status: "accepted", job_id: "...", job_status: "queued" }

3. GET /api/v1/jobs/{job_id}/status (repeated every 2s)
   Response: { status: "success", data: { status: "processing", progress: {...} } }

4. GET /api/v1/jobs/{job_id}/results (when status = "completed")
   Response: { status: "success", data: { images: [...], total_detections: N } }

5. GET /api/v1/jobs/{job_id}/visualization (optional)
   Response: { status: "success", data: { visualizations: [...] } }
```

---

## Performance Expectations

- **Upload:** 1-5 seconds for 10 images (~10MB total)
- **Detection Start:** <1 second (just triggers backend job)
- **Status Polling:** 2 second intervals
- **Detection Processing:** Varies by image count and size (1-5 min for 10 images)
- **Results Fetch:** 1-3 seconds for 10 images with detections

---

## Success Criteria

✅ **Integration is successful if:**
1. Files upload to backend and return job ID
2. Detection triggers and job processes
3. Status polls automatically and updates UI
4. Results fetch automatically when complete
5. All data displays correctly in UI
6. Errors are handled gracefully
7. No unhandled exceptions or crashes

---

## Known Limitations

1. Backend must be running locally on port 8000
2. CORS only configured for localhost development
3. No authentication/authorization implemented
4. File size limited to 50MB per file
5. Maximum 100 files per upload
6. Polling interval not configurable from UI
7. No retry logic for failed API calls
8. Results not persisted across app restarts (stored in memory)

---

## Next Steps

After verifying integration:
1. Add automated E2E tests with Playwright or Cypress
2. Implement retry logic for failed API calls
3. Add request cancellation for long operations
4. Implement progressive result streaming for large jobs
5. Add offline mode with local storage fallback
6. Optimize polling strategy (exponential backoff)
7. Add WebSocket support for real-time updates
