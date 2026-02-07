/**
 * Redux async thunks for detection operations
 * Handles API calls for inference triggering and status polling
 */

import { createAsyncThunk } from '@reduxjs/toolkit';
import apiService from '../../services/api';
import { InferenceConfig as APIInferenceConfig } from '../../services/api/types';
import { DetectionConfig } from '../../types';

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
    { rejectWithValue }
  ) => {
    try {
      // Transform frontend config to backend format
      const apiConfig = transformConfig(config);
      
      // Call API to start detection
      const response = await apiService.runDetection(jobId, apiConfig);
      
      return {
        jobId: response.job_id,
        jobStatus: response.job_status,
        message: response.message,
      };
    } catch (error: any) {
      console.error('[Detection Thunk] Start failed:', error);
      return rejectWithValue(error.message || 'Failed to start detection');
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
  async (jobId: string, { rejectWithValue }) => {
    try {
      const response = await apiService.getJobStatus(jobId);
      
      return {
        status: response.data.status,
        progress: response.data.progress,
        summary: response.data.summary,
        error: response.data.error,
        completedAt: response.data.completed_at,
      };
    } catch (error: any) {
      console.error('[Detection Thunk] Poll status failed:', error);
      return rejectWithValue(error.message || 'Failed to get job status');
    }
  }
);
