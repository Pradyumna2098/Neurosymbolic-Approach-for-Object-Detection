import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { JobStatus, JobProgress } from '../../types';
import { startDetectionThunk, pollStatusThunk } from './detectionThunks';

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
  extraReducers: (builder) => {
    builder
      // Start detection thunk
      .addCase(startDetectionThunk.pending, (state) => {
        state.status = 'pending';
        state.error = null;
      })
      .addCase(startDetectionThunk.fulfilled, (state, action) => {
        state.jobId = action.payload.jobId;
        state.status = 'running';
        state.startedAt = new Date();
        state.progress = {
          stage: 'Starting',
          progress: 0,
          message: action.payload.message || 'Detection started',
        };
      })
      .addCase(startDetectionThunk.rejected, (state, action) => {
        state.status = 'error';
        state.error = (action.payload as string) || 'Failed to start detection';
        state.completedAt = new Date();
      })
      
      // Poll status thunk
      .addCase(pollStatusThunk.fulfilled, (state, action) => {
        const { status, progress, summary, error: jobError, completedAt } = action.payload;
        
        // Map backend status to frontend JobStatus
        if (status === 'completed') {
          state.status = 'complete';
          state.completedAt = completedAt ? new Date(completedAt) : new Date();
          state.progress = {
            stage: 'Complete',
            progress: 100,
            message: 'Detection completed successfully',
          };
        } else if (status === 'failed') {
          state.status = 'error';
          state.error = jobError?.message || 'Detection failed';
          state.completedAt = completedAt ? new Date(completedAt) : new Date();
        } else if (status === 'processing') {
          state.status = 'running';
          if (progress) {
            state.progress = {
              stage: progress.stage || 'Processing',
              progress: progress.percentage || 0,
              message: progress.message || '',
            };
          }
        } else if (status === 'queued') {
          state.status = 'pending';
        }
      })
      .addCase(pollStatusThunk.rejected, (state, action) => {
        // Don't fail the whole detection on poll error
        // Just log and continue polling
        console.warn('[Detection] Poll status failed:', action.payload);
      });
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
