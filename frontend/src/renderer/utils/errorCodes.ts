/**
 * Error codes matching backend error codes
 * Synced with backend/app/core/errors.py
 */

export enum ErrorCode {
  // General errors
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  INVALID_REQUEST = 'INVALID_REQUEST',
  VALIDATION_ERROR = 'VALIDATION_ERROR',

  // File/Upload errors
  FILE_NOT_FOUND = 'FILE_NOT_FOUND',
  FILE_TOO_LARGE = 'FILE_TOO_LARGE',
  INVALID_FILE_FORMAT = 'INVALID_FILE_FORMAT',
  UPLOAD_FAILED = 'UPLOAD_FAILED',

  // Job errors
  JOB_NOT_FOUND = 'JOB_NOT_FOUND',
  JOB_ALREADY_RUNNING = 'JOB_ALREADY_RUNNING',
  JOB_FAILED = 'JOB_FAILED',
  INVALID_JOB_STATUS = 'INVALID_JOB_STATUS',
  NO_FILES = 'NO_FILES',
  INVALID_STATUS = 'INVALID_STATUS',

  // Model/Inference errors
  MODEL_NOT_FOUND = 'MODEL_NOT_FOUND',
  MODEL_LOAD_ERROR = 'MODEL_LOAD_ERROR',
  INFERENCE_ERROR = 'INFERENCE_ERROR',
  INVALID_CONFIG = 'INVALID_CONFIG',

  // Resource errors
  STORAGE_ERROR = 'STORAGE_ERROR',
  MEMORY_ERROR = 'MEMORY_ERROR',
  CUDA_OOM = 'CUDA_OOM',

  // Results errors
  RESULTS_NOT_FOUND = 'RESULTS_NOT_FOUND',
  RESULTS_NOT_READY = 'RESULTS_NOT_READY',
  VISUALIZATION_ERROR = 'VISUALIZATION_ERROR',
  VISUALIZATIONS_NOT_READY = 'VISUALIZATIONS_NOT_READY',
  VISUALIZATIONS_NOT_FOUND = 'VISUALIZATIONS_NOT_FOUND',
  VISUALIZATION_NOT_FOUND = 'VISUALIZATION_NOT_FOUND',
  NO_VISUALIZATIONS = 'NO_VISUALIZATIONS',
  ORIGINAL_IMAGE_NOT_FOUND = 'ORIGINAL_IMAGE_NOT_FOUND',
  ANNOTATED_IMAGE_NOT_FOUND = 'ANNOTATED_IMAGE_NOT_FOUND',
  INVALID_FORMAT = 'INVALID_FORMAT',

  // Rate limiting
  RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED',

  // Network errors (client-side only)
  NETWORK_ERROR = 'NETWORK_ERROR',
  TIMEOUT_ERROR = 'TIMEOUT_ERROR',
}

/**
 * User-friendly error messages for each error code
 */
export const ERROR_MESSAGES: Record<ErrorCode, string> = {
  [ErrorCode.INTERNAL_ERROR]: 'An internal server error occurred. Please try again later.',
  [ErrorCode.INVALID_REQUEST]: 'The request is invalid or malformed.',
  [ErrorCode.VALIDATION_ERROR]: 'One or more fields failed validation.',

  [ErrorCode.FILE_NOT_FOUND]: 'The requested file was not found.',
  [ErrorCode.FILE_TOO_LARGE]: 'The uploaded file exceeds the maximum allowed size.',
  [ErrorCode.INVALID_FILE_FORMAT]: 'The file format is not supported. Please upload a valid image file.',
  [ErrorCode.UPLOAD_FAILED]: 'File upload failed. Please check your connection and try again.',

  [ErrorCode.JOB_NOT_FOUND]: 'The requested job was not found.',
  [ErrorCode.JOB_ALREADY_RUNNING]: 'A detection job is already running for these files.',
  [ErrorCode.JOB_FAILED]: 'The detection job failed to complete.',
  [ErrorCode.INVALID_JOB_STATUS]: 'The job is not in a valid state for this operation.',
  [ErrorCode.NO_FILES]: 'The job has no uploaded files.',
  [ErrorCode.INVALID_STATUS]: 'The job status is invalid for this operation.',

  [ErrorCode.MODEL_NOT_FOUND]: 'The requested model was not found.',
  [ErrorCode.MODEL_LOAD_ERROR]: 'Failed to load the detection model. Please check the model path.',
  [ErrorCode.INFERENCE_ERROR]: 'An error occurred during object detection.',
  [ErrorCode.INVALID_CONFIG]: 'The inference configuration is invalid.',

  [ErrorCode.STORAGE_ERROR]: 'Failed to access or write to storage.',
  [ErrorCode.MEMORY_ERROR]: 'Insufficient memory to process the request.',
  [ErrorCode.CUDA_OOM]: 'GPU memory exceeded. Try reducing batch size or image resolution.',

  [ErrorCode.RESULTS_NOT_FOUND]: 'Results for this job were not found.',
  [ErrorCode.RESULTS_NOT_READY]: 'Results are not yet available. The job may still be processing.',
  [ErrorCode.VISUALIZATION_ERROR]: 'Failed to generate visualization images.',
  [ErrorCode.VISUALIZATIONS_NOT_READY]: 'Visualizations are not yet available. The job may still be processing.',
  [ErrorCode.VISUALIZATIONS_NOT_FOUND]: 'No visualizations were found for this job.',
  [ErrorCode.VISUALIZATION_NOT_FOUND]: 'The requested visualization was not found.',
  [ErrorCode.NO_VISUALIZATIONS]: 'No visualizations are available for this job.',
  [ErrorCode.ORIGINAL_IMAGE_NOT_FOUND]: 'The original image was not found.',
  [ErrorCode.ANNOTATED_IMAGE_NOT_FOUND]: 'The annotated image was not found.',
  [ErrorCode.INVALID_FORMAT]: 'Invalid format parameter specified.',

  [ErrorCode.RATE_LIMIT_EXCEEDED]: 'Too many requests. Please wait before trying again.',

  [ErrorCode.NETWORK_ERROR]: 'Network connection failed. Please check your connection and try again.',
  [ErrorCode.TIMEOUT_ERROR]: 'The request timed out. Please try again.',
};

/**
 * Determines if an error should trigger a retry
 */
export function shouldRetry(errorCode: ErrorCode): boolean {
  const retriableErrors: ErrorCode[] = [
    ErrorCode.INTERNAL_ERROR,
    ErrorCode.STORAGE_ERROR,
    ErrorCode.MEMORY_ERROR,
    ErrorCode.CUDA_OOM,
    ErrorCode.RATE_LIMIT_EXCEEDED,
    ErrorCode.INFERENCE_ERROR,
    ErrorCode.NETWORK_ERROR,
    ErrorCode.TIMEOUT_ERROR,
  ];

  return retriableErrors.includes(errorCode);
}

/**
 * Get retry delay in seconds based on error code and attempt number
 * Uses exponential backoff for most errors
 */
export function getRetryDelay(errorCode: ErrorCode, attempt: number): number {
  if (errorCode === ErrorCode.RATE_LIMIT_EXCEEDED) {
    return 60; // Fixed 60 second delay for rate limiting
  }

  // Exponential backoff: 5s, 15s, 45s
  const baseDelay = 5;
  return baseDelay * Math.pow(3, attempt - 1);
}

/**
 * Maximum number of retry attempts
 */
export const MAX_RETRY_ATTEMPTS = 3;
