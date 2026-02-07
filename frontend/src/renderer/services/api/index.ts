/**
 * API Service - Main interface for backend communication
 * 
 * Provides methods for:
 * - File upload
 * - Inference triggering
 * - Job status polling
 * - Results retrieval
 * - Visualization fetching
 */

import { AxiosError } from 'axios';
import apiClient from './client';
import {
  UploadResponse,
  PredictRequest,
  PredictResponse,
  JobStatusResponse,
  JobResultsResponse,
  VisualizationResponse,
  Base64VisualizationResponse,
  InferenceConfig,
} from './types';

/**
 * Upload images to the backend
 * 
 * @param files - Array of File objects to upload
 * @returns Promise with upload response containing job_id and file metadata
 * @throws Error if upload fails
 */
export async function uploadImages(files: File[]): Promise<UploadResponse> {
  try {
    // Create FormData for multipart/form-data upload
    const formData = new FormData();
    
    // Add all files to FormData
    files.forEach((file) => {
      formData.append('files', file);
    });

    // Send POST request with multipart/form-data
    const response = await apiClient.post<UploadResponse>(
      '/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        // Increase timeout for large file uploads
        timeout: 120000, // 2 minutes
      }
    );

    return response.data;
  } catch (error) {
    console.error('[API] Upload failed:', error);
    
    // Extract error message
    const axiosError = error as AxiosError<any>;
    const errorMessage = 
      axiosError.response?.data?.detail?.message || 
      axiosError.response?.data?.message ||
      axiosError.message ||
      'Failed to upload images';

    throw new Error(errorMessage);
  }
}

/**
 * Trigger inference on uploaded images
 * 
 * @param jobId - Job identifier from upload response
 * @param config - Inference configuration (model path, thresholds, SAHI settings, etc.)
 * @returns Promise with predict response
 * @throws Error if inference trigger fails
 */
export async function runDetection(
  jobId: string,
  config: InferenceConfig
): Promise<PredictResponse> {
  try {
    const requestBody: PredictRequest = {
      job_id: jobId,
      config,
    };

    const response = await apiClient.post<PredictResponse>(
      '/predict',
      requestBody,
      {
        // Inference triggers background job, so short timeout is fine
        timeout: 30000, // 30 seconds
      }
    );

    return response.data;
  } catch (error) {
    console.error('[API] Run detection failed:', error);
    
    const axiosError = error as AxiosError<any>;
    const errorMessage = 
      axiosError.response?.data?.detail?.message || 
      axiosError.response?.data?.message ||
      axiosError.message ||
      'Failed to start detection';

    throw new Error(errorMessage);
  }
}

/**
 * Poll job status
 * 
 * @param jobId - Job identifier
 * @returns Promise with job status response
 * @throws Error if status retrieval fails
 */
export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  try {
    const response = await apiClient.get<JobStatusResponse>(
      `/jobs/${jobId}/status`,
      {
        timeout: 10000, // 10 seconds
      }
    );

    return response.data;
  } catch (error) {
    console.error('[API] Get job status failed:', error);
    
    const axiosError = error as AxiosError<any>;
    const errorMessage = 
      axiosError.response?.data?.detail?.message || 
      axiosError.response?.data?.message ||
      axiosError.message ||
      'Failed to get job status';

    throw new Error(errorMessage);
  }
}

/**
 * Retrieve detection results for a completed job
 * 
 * @param jobId - Job identifier
 * @returns Promise with results response containing all detections
 * @throws Error if results retrieval fails
 */
export async function getResults(jobId: string): Promise<JobResultsResponse> {
  try {
    const response = await apiClient.get<JobResultsResponse>(
      `/jobs/${jobId}/results`,
      {
        timeout: 30000, // 30 seconds (results can be large)
      }
    );

    return response.data;
  } catch (error) {
    console.error('[API] Get results failed:', error);
    
    const axiosError = error as AxiosError<any>;
    const errorMessage = 
      axiosError.response?.data?.detail?.message || 
      axiosError.response?.data?.message ||
      axiosError.message ||
      'Failed to retrieve results';

    throw new Error(errorMessage);
  }
}

/**
 * Retrieve visualization URLs for a completed job
 * 
 * @param jobId - Job identifier
 * @returns Promise with visualization response containing image URLs
 * @throws Error if visualization retrieval fails
 */
export async function getVisualizations(
  jobId: string
): Promise<VisualizationResponse> {
  try {
    const response = await apiClient.get<VisualizationResponse>(
      `/jobs/${jobId}/visualization`,
      {
        timeout: 30000, // 30 seconds
      }
    );

    return response.data;
  } catch (error) {
    console.error('[API] Get visualizations failed:', error);
    
    const axiosError = error as AxiosError<any>;
    const errorMessage = 
      axiosError.response?.data?.detail?.message || 
      axiosError.response?.data?.message ||
      axiosError.message ||
      'Failed to retrieve visualizations';

    throw new Error(errorMessage);
  }
}

/**
 * Retrieve base64-encoded visualizations for embedding in UI
 * 
 * @param jobId - Job identifier
 * @returns Promise with base64 visualization response
 * @throws Error if visualization retrieval fails
 */
export async function getBase64Visualizations(
  jobId: string
): Promise<Base64VisualizationResponse> {
  try {
    const response = await apiClient.get<Base64VisualizationResponse>(
      `/jobs/${jobId}/visualization/base64`,
      {
        timeout: 60000, // 60 seconds (base64 encoding can be slow)
      }
    );

    return response.data;
  } catch (error) {
    console.error('[API] Get base64 visualizations failed:', error);
    
    const axiosError = error as AxiosError<any>;
    const errorMessage = 
      axiosError.response?.data?.detail?.message || 
      axiosError.response?.data?.message ||
      axiosError.message ||
      'Failed to retrieve visualizations';

    throw new Error(errorMessage);
  }
}

/**
 * Download a specific visualization image
 * 
 * @param url - Full URL to the visualization image
 * @returns Promise with blob data
 * @throws Error if download fails
 */
export async function downloadVisualization(url: string): Promise<Blob> {
  try {
    const response = await apiClient.get<Blob>(url, {
      responseType: 'blob',
      timeout: 30000, // 30 seconds
    });

    return response.data;
  } catch (error) {
    console.error('[API] Download visualization failed:', error);
    throw new Error('Failed to download visualization');
  }
}

// Export all functions as default service object
const apiService = {
  uploadImages,
  runDetection,
  getJobStatus,
  getResults,
  getVisualizations,
  getBase64Visualizations,
  downloadVisualization,
};

export default apiService;
