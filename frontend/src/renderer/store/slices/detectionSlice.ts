import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { JobStatus, JobProgress } from '../../types';

interface DetectionState {
  jobId: string | null;
  status: JobStatus;
  progress: JobProgress;
  error: string | null;
  startedAt: Date | null;
  completedAt: Date | null;
}

const initialState: DetectionState = {
  jobId: null,
  status: 'idle',
  progress: {
    stage: '',
    progress: 0,
    message: '',
  },
  error: null,
  startedAt: null,
  completedAt: null,
};

const detectionSlice = createSlice({
  name: 'detection',
  initialState,
  reducers: {
    startDetection(state, action: PayloadAction<string>) {
      state.jobId = action.payload;
      state.status = 'pending';
      state.progress = {
        stage: 'Initializing',
        progress: 0,
        message: 'Starting detection process...',
      };
      state.error = null;
      state.startedAt = new Date();
      state.completedAt = null;
    },
    updateStatus(state, action: PayloadAction<JobStatus>) {
      state.status = action.payload;
    },
    updateProgress(state, action: PayloadAction<JobProgress>) {
      state.progress = action.payload;
      if (state.status === 'pending' && action.payload.progress > 0) {
        state.status = 'running';
      }
    },
    completeDetection(state) {
      state.status = 'complete';
      state.progress = {
        stage: 'Complete',
        progress: 100,
        message: 'Detection completed successfully',
      };
      state.completedAt = new Date();
    },
    setDetectionError(state, action: PayloadAction<string>) {
      state.status = 'error';
      state.error = action.payload;
      state.progress = {
        stage: 'Error',
        progress: 0,
        message: action.payload,
      };
      state.completedAt = new Date();
    },
    resetDetection() {
      return initialState;
    },
    cancelDetection(state) {
      state.status = 'error';
      state.error = 'Detection cancelled by user';
      state.completedAt = new Date();
    },
  },
});

export const {
  startDetection,
  updateStatus,
  updateProgress,
  completeDetection,
  setDetectionError,
  resetDetection,
  cancelDetection,
} = detectionSlice.actions;

export default detectionSlice.reducer;
