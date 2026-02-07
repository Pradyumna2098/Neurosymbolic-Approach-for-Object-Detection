/**
 * Redux async thunks for upload operations
 * Handles API calls for image upload
 */

import { createAsyncThunk } from '@reduxjs/toolkit';
import apiService from '../../services/api';
import { UploadedFile } from '../../types';

/**
 * Upload images to backend API
 * 
 * Accepts File[] from drag-and-drop or file picker,
 * uploads to backend, and returns job_id and file metadata
 */
export const uploadImagesThunk = createAsyncThunk(
  'upload/uploadImages',
  async (files: File[], { rejectWithValue }) => {
    try {
      // Call API service to upload files
      const response = await apiService.uploadImages(files);
      
      // Transform API response to match frontend UploadedFile type
      const uploadedFiles: UploadedFile[] = response.files.map((file) => ({
        id: file.file_id || `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        name: file.filename,
        size: file.size,
        path: file.filename, // Backend doesn't return full path in prototype
        uploadedAt: new Date(),
        // Note: Backend doesn't return preview/thumbnail in current implementation
        // Frontend generates previews locally before upload
      }));

      return {
        jobId: response.job_id,
        files: uploadedFiles,
        warnings: response.warnings,
      };
    } catch (error: any) {
      console.error('[Upload Thunk] Failed:', error);
      return rejectWithValue(error.message || 'Upload failed');
    }
  }
);
