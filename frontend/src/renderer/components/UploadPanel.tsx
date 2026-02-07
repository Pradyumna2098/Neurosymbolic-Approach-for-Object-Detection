import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Typography,
  Paper,
  Button,
  List,
  Alert,
  CircularProgress,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CloudDoneIcon from '@mui/icons-material/CloudDone';
import FolderIcon from '@mui/icons-material/Folder';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../store';
import {
  addFiles,
  removeFile,
  clearFiles,
  setUploadError,
  clearUploadError,
} from '../store/slices/uploadSlice';
import { uploadImagesThunk } from '../store/slices/uploadThunks';
import { UploadedFile } from '../types';
import FileListItem from './FileListItem';

// Supported image formats
const ACCEPTED_FORMATS = {
  'image/jpeg': ['.jpg', '.jpeg'],
  'image/png': ['.png'],
  'image/bmp': ['.bmp'],
  'image/tiff': ['.tiff', '.tif'],
};

// Maximum file size: 50MB
const MAX_FILE_SIZE = 50 * 1024 * 1024;

/**
 * Upload Panel - Image upload with drag-and-drop functionality
 * Features:
 * - Drag-and-drop file upload
 * - Click to browse files
 * - Thumbnail gallery
 * - File validation
 * - Upload to server
 * - Clear/remove files
 * Location: Top-left panel
 */
const UploadPanel: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { files, jobId, isUploading, error } = useSelector((state: RootState) => state.upload);
  const [rawFiles, setRawFiles] = useState<File[]>([]); // Store raw File objects for upload

  /**
   * Handle file drop/selection
   * Validates files and creates preview thumbnails
   */
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      // Clear any previous errors
      dispatch(clearUploadError());

      // Store raw File objects for later upload
      setRawFiles((prev) => [...prev, ...acceptedFiles]);

      // Validate and process accepted files
      const validFiles: UploadedFile[] = [];
      const errors: string[] = [];

      acceptedFiles.forEach((file) => {
        // Check file size
        if (file.size > MAX_FILE_SIZE) {
          errors.push(`${file.name} exceeds 50MB limit`);
          return;
        }

        // Create preview thumbnail
        const reader = new FileReader();
        reader.onload = () => {
          const uploadedFile: UploadedFile = {
            id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            name: file.name,
            size: file.size,
            path: file.name,
            preview: reader.result as string,
            uploadedAt: new Date(),
          };
          validFiles.push(uploadedFile);

          // Dispatch only when all files are processed
          if (validFiles.length === acceptedFiles.length - errors.length) {
            dispatch(addFiles(validFiles));
          }
        };
        reader.readAsDataURL(file);
      });

      // Report validation errors
      if (errors.length > 0) {
        dispatch(setUploadError(errors.join(', ')));
      }
    },
    [dispatch],
  );

  // Configure dropzone with validation
  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: ACCEPTED_FORMATS,
    multiple: true,
    maxSize: MAX_FILE_SIZE,
  });

  // Handle file rejections
  React.useEffect(() => {
    if (fileRejections.length > 0) {
      const errorMessages = fileRejections
        .map((rejection) => {
          const errors = rejection.errors.map((e) => e.message).join(', ');
          return `${rejection.file.name}: ${errors}`;
        })
        .join('; ');
      dispatch(setUploadError(errorMessages));
    }
  }, [fileRejections, dispatch]);

  /**
   * Handle removing a single file
   */
  const handleRemoveFile = (fileId: string) => {
    dispatch(removeFile(fileId));
  };

  /**
   * Handle clearing all files
   */
  const handleClearAll = () => {
    dispatch(clearFiles());
    setRawFiles([]);
  };

  /**
   * Handle uploading files to server
   */
  const handleUploadToServer = async () => {
    if (rawFiles.length === 0) {
      dispatch(setUploadError('No files to upload'));
      return;
    }

    try {
      await dispatch(uploadImagesThunk(rawFiles)).unwrap();
      // Success - jobId is stored in Redux state
      console.log('[Upload] Files uploaded successfully');
    } catch (error: any) {
      console.error('[Upload] Upload failed:', error);
      // Error is already set in Redux state
    }
  };

  return (
    <Paper
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        p: 2,
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <CloudUploadIcon sx={{ mr: 1 }} />
        <Typography variant="h6">Upload Images</Typography>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert
          severity="error"
          onClose={() => dispatch(clearUploadError())}
          sx={{ mb: 2 }}
        >
          {error}
        </Alert>
      )}

      {/* Drop Zone */}
      <Box
        {...getRootProps()}
        sx={{
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'divider',
          borderRadius: 2,
          p: 3,
          textAlign: 'center',
          cursor: 'pointer',
          bgcolor: isDragActive ? 'action.hover' : 'background.default',
          mb: 2,
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            borderColor: 'primary.main',
            bgcolor: 'action.hover',
          },
        }}
      >
        <input {...getInputProps()} />
        <CloudUploadIcon
          sx={{
            fontSize: 48,
            color: isDragActive ? 'primary.main' : 'text.secondary',
            mb: 1,
          }}
        />
        <Typography variant="body1" gutterBottom>
          {isDragActive
            ? 'Drop files here...'
            : 'Drag & drop files here or click to browse'}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Supported formats: JPG, PNG, BMP, TIFF (Max: 50MB)
        </Typography>
      </Box>

      {/* Upload to Server Button */}
      {files.length > 0 && !jobId && (
        <Button
          variant="contained"
          color="primary"
          fullWidth
          disabled={isUploading}
          onClick={handleUploadToServer}
          startIcon={isUploading ? <CircularProgress size={20} /> : <CloudUploadIcon />}
          sx={{ mb: 2 }}
        >
          {isUploading ? 'Uploading...' : 'Upload to Server'}
        </Button>
      )}

      {/* Upload Success Message */}
      {jobId && (
        <Alert severity="success" sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CloudDoneIcon />
            <Typography variant="body2">
              Files uploaded successfully! Job ID: {jobId.slice(0, 8)}...
            </Typography>
          </Box>
        </Alert>
      )}

      {/* File List */}
      {files.length > 0 && (
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="subtitle2">
              Uploaded Images ({files.length})
            </Typography>
            <Button
              size="small"
              variant="text"
              color="error"
              onClick={handleClearAll}
            >
              Clear All
            </Button>
          </Box>
          <List
            dense
            sx={{
              flex: 1,
              overflow: 'auto',
              '&::-webkit-scrollbar': {
                width: '8px',
              },
              '&::-webkit-scrollbar-track': {
                background: 'transparent',
              },
              '&::-webkit-scrollbar-thumb': {
                background: 'divider',
                borderRadius: '4px',
              },
            }}
          >
            {files.map((file) => (
              <FileListItem
                key={file.id}
                file={file}
                onRemove={() => handleRemoveFile(file.id)}
              />
            ))}
          </List>
        </Box>
      )}

      {/* Empty State */}
      {files.length === 0 && (
        <Box
          sx={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Typography variant="body2" color="text.secondary">
            No files uploaded yet
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default UploadPanel;
