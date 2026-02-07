/**
 * Redux async thunks for detection operations
 * Handles API calls for inference triggering and status polling
 */

import { createAsyncThunk } from '@reduxjs/toolkit';
import apiService from '../../services/api';
import { InferenceConfig as APIInferenceConfig } from '../../services/api/types';
import { DetectionConfig } from '../../types';
import { parseApiError } from '../../utils/errorHandling';
import { showError, showSuccess, showInfo } from './notificationSlice';

/**
 * Transform frontend DetectionConfig to backend InferenceConfig
 */
function transformConfig(config: DetectionConfig): APIInferenceConfig {
  return {
    model_path: config.modelPath,
    confidence_threshold: config.confidence,
    iou_threshold: config.iouThreshold,
    sahi: {
      enabled: true, // Always enabled for better results
      slice_width: config.sliceWidth,
      slice_height: config.sliceHeight,
      overlap_ratio: config.overlapHeight, // Use one overlap value
    },
    symbolic_reasoning: {
      enabled: config.enableProlog,
      rules_file: config.prologRulesPath,
    },
    visualization: {
      enabled: true, // Always generate visualizations
      show_labels: true,
      confidence_display: true,
    },
  };
}

/**
 * Start detection/inference job
 * 
 * Accepts job_id from upload and detection configuration,
 * triggers inference on backend
 */
export const startDetectionThunk = createAsyncThunk(
  'detection/startDetection',
  async (
    { jobId, config }: { jobId: string; config: DetectionConfig },
    { rejectWithValue, dispatch }
  ) => {
    try {
      // Transform frontend config to backend format
      const apiConfig = transformConfig(config);
      
      // Call API to start detection
      const response = await apiService.runDetection(jobId, apiConfig);
      
      // Show success notification
      dispatch(showInfo('Detection job started. Processing images...'));
      
      return {
        jobId: response.job_id,
        jobStatus: response.job_status,
        message: response.message,
      };
    } catch (error: any) {
      console.error('[Detection Thunk] Start failed:', error);
      
      // Parse error and show notification
      const parsedError = parseApiError(error);
      dispatch(
        showError({
          message: parsedError.message,
          errorCode: parsedError.code,
          canRetry: parsedError.canRetry,
        })
      );
      
      return rejectWithValue(parsedError.message);
    }
  }
);

/**
 * Poll job status
 * 
 * Retrieves current status and progress for a running job
 */
export const pollStatusThunk = createAsyncThunk(
  'detection/pollStatus',
  async (jobId: string, { rejectWithValue, dispatch }) => {
    try {
      const response = await apiService.getJobStatus(jobId);
      
      // Show notification when job completes
      if (response.data.status === 'completed') {
        dispatch(showSuccess('Detection completed successfully!'));
      } else if (response.data.status === 'failed' && response.data.error) {
        dispatch(
          showError({
            message: `Job failed: ${response.data.error.message}`,
            errorCode: response.data.error.code as any,
            canRetry: false,
          })
        );
      }
      
      return {
        status: response.data.status,
        progress: response.data.progress,
        summary: response.data.summary,
        error: response.data.error,
        completedAt: response.data.completed_at,
      };
    } catch (error: any) {
      console.error('[Detection Thunk] Poll status failed:', error);
      
      // Don't show notification for poll errors (they're silent)
      // The polling will retry automatically
      
      return rejectWithValue(error.message || 'Failed to get job status');
    }
  }
);
