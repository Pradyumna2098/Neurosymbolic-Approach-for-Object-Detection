import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { UploadedFile } from '../../types';

interface UploadState {
  files: UploadedFile[];
  isUploading: boolean;
  uploadProgress: number;
  error: string | null;
}

const initialState: UploadState = {
  files: [],
  isUploading: false,
  uploadProgress: 0,
  error: null,
};

const uploadSlice = createSlice({
  name: 'upload',
  initialState,
  reducers: {
    addFiles(state, action: PayloadAction<UploadedFile[]>) {
      // Add new files to the list
      state.files = [...state.files, ...action.payload];
      state.error = null;
    },
    removeFile(state, action: PayloadAction<string>) {
      // Remove file by id
      state.files = state.files.filter((file) => file.id !== action.payload);
    },
    clearFiles(state) {
      state.files = [];
      state.error = null;
    },
    setUploading(state, action: PayloadAction<boolean>) {
      state.isUploading = action.payload;
      if (!action.payload) {
        state.uploadProgress = 0;
      }
    },
    setUploadProgress(state, action: PayloadAction<number>) {
      state.uploadProgress = action.payload;
    },
    setUploadError(state, action: PayloadAction<string>) {
      state.error = action.payload;
      state.isUploading = false;
      state.uploadProgress = 0;
    },
    clearUploadError(state) {
      state.error = null;
    },
  },
});

export const {
  addFiles,
  removeFile,
  clearFiles,
  setUploading,
  setUploadProgress,
  setUploadError,
  clearUploadError,
} = uploadSlice.actions;

export default uploadSlice.reducer;
