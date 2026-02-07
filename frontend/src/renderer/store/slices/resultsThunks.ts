/**
 * Redux async thunks for results operations
 * Handles API calls for fetching detection results and visualizations
 */

import { createAsyncThunk } from '@reduxjs/toolkit';
import apiService from '../../services/api';
import { DetectionResult, Detection, BoundingBox } from '../../types';
import { parseApiError } from '../../utils/errorHandling';
import { showError, showWarning } from './notificationSlice';

/**
 * Transform backend detection format to frontend format
 */
function transformDetection(
  detection: any,
  imageId: string,
  imageName: string
): Detection {
  // Extract bounding box based on format
  let bbox: BoundingBox;
  
  if (detection.bbox.format === 'yolo' && detection.bbox.center_x !== undefined) {
    // Convert normalized YOLO format to absolute coordinates
    // Note: We need image dimensions for proper conversion
    // For now, use normalized values (0-1 range)
    bbox = {
      x: (detection.bbox.center_x - detection.bbox.width / 2),
      y: (detection.bbox.center_y - detection.bbox.height / 2),
      width: detection.bbox.width,
      height: detection.bbox.height,
    };
  } else if (detection.bbox.format === 'xyxy') {
    // Use absolute coordinates directly
    bbox = {
      x: detection.bbox.x_min,
      y: detection.bbox.y_min,
      width: detection.bbox.x_max - detection.bbox.x_min,
      height: detection.bbox.y_max - detection.bbox.y_min,
    };
  } else {
    // Fallback
    bbox = { x: 0, y: 0, width: 0, height: 0 };
  }

  return {
    id: `${imageId}-${detection.class_id}-${Math.random().toString(36).substr(2, 9)}`,
    classId: detection.class_id,
    className: detection.class_name || `Class ${detection.class_id}`,
    confidence: detection.confidence,
    bbox,
    imageId,
  };
}

/**
 * Fetch detection results for a completed job
 * 
 * Retrieves all detections, transforms to frontend format
 */
export const fetchResultsThunk = createAsyncThunk(
  'results/fetchResults',
  async (jobId: string, { rejectWithValue, dispatch }) => {
    try {
      const response = await apiService.getResults(jobId);
      
      // Transform backend results to frontend DetectionResult format
      const results: DetectionResult[] = response.data.images.map((image) => {
        const imageId = image.file_id;
        const imageName = image.filename;
        
        const detections = image.detections.map((det) =>
          transformDetection(det, imageId, imageName)
        );

        return {
          imageId,
          imageName,
          imagePath: `/api/v1/files/${jobId}/${image.file_id}`, // Construct path
          detections,
          metadata: {
            processingTime: response.data.processing_time_seconds || 0,
            totalDetections: detections.length,
            timestamp: new Date(),
          },
        };
      });

      return {
        results,
        summary: {
          totalDetections: response.data.total_detections,
          averageConfidence: response.data.average_confidence,
          processingTime: response.data.processing_time_seconds,
        },
      };
    } catch (error: any) {
      console.error('[Results Thunk] Fetch failed:', error);
      
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
 * Fetch visualization images (base64-encoded) for embedding in UI
 */
export const fetchVisualizationsThunk = createAsyncThunk(
  'results/fetchVisualizations',
  async (jobId: string, { rejectWithValue, dispatch }) => {
    try {
      const response = await apiService.getBase64Visualizations(jobId);
      
      // Return base64 image data for direct embedding
      const visualizations = response.data.visualizations.map((viz) => ({
        fileId: viz.file_id,
        filename: viz.filename,
        base64Data: viz.base64_data,
        mimeType: viz.mime_type,
      }));

      return visualizations;
    } catch (error: any) {
      console.error('[Results Thunk] Fetch visualizations failed:', error);
      
      // Show warning but don't fail - visualizations are optional
      const parsedError = parseApiError(error);
      dispatch(
        showWarning(`Failed to load visualizations: ${parsedError.message}`)
      );
      
      // Return empty array instead of failing
      return [];
    }
  }
);
