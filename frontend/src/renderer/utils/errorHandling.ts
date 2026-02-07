/**
 * Error handling utilities for API error processing
 */

import { AxiosError } from 'axios';
import { ErrorCode, ERROR_MESSAGES, shouldRetry } from './errorCodes';

/**
 * Parsed error information from API responses
 */
export interface ParsedError {
  code: ErrorCode;
  message: string;
  details?: string;
  fieldErrors?: Array<{
    field: string;
    message: string;
  }>;
  canRetry: boolean;
  statusCode?: number;
}

/**
 * Parse an Axios error into a standardized ParsedError object
 */
export function parseApiError(error: unknown): ParsedError {
  // Default error
  const defaultError: ParsedError = {
    code: ErrorCode.INTERNAL_ERROR,
    message: ERROR_MESSAGES[ErrorCode.INTERNAL_ERROR],
    canRetry: false,
  };

  // Handle Axios errors
  if (error && typeof error === 'object' && 'isAxiosError' in error) {
    const axiosError = error as AxiosError<any>;

    // Network error (no response received)
    if (!axiosError.response) {
      if (axiosError.code === 'ECONNABORTED' || axiosError.message.includes('timeout')) {
        return {
          code: ErrorCode.TIMEOUT_ERROR,
          message: ERROR_MESSAGES[ErrorCode.TIMEOUT_ERROR],
          canRetry: true,
        };
      }

      return {
        code: ErrorCode.NETWORK_ERROR,
        message: ERROR_MESSAGES[ErrorCode.NETWORK_ERROR],
        canRetry: true,
      };
    }

    // Server responded with error
    const { response } = axiosError;
    const data = response.data;

    // Check if response has standardized error format
    if (data && data.error) {
      // Validate that we have a known error code, otherwise fall back to INTERNAL_ERROR
      let errorCode = ErrorCode.INTERNAL_ERROR;
      const rawCode = data.error.code;
      
      if (rawCode && Object.values(ErrorCode).includes(rawCode as ErrorCode)) {
        errorCode = rawCode as ErrorCode;
      }
      
      // Always ensure message is non-empty
      const message = data.error.message || ERROR_MESSAGES[errorCode] || 'An unexpected error occurred.';
      
      return {
        code: errorCode,
        message,
        details: data.error.details,
        fieldErrors: data.field_errors,
        canRetry: shouldRetry(errorCode),
        statusCode: response.status,
      };
    }

    // Fallback: try to extract error from common formats
    const errorMessage =
      data?.detail?.message ||
      data?.message ||
      data?.detail ||
      axiosError.message ||
      'An unexpected error occurred';

    // Map status code to error code
    let errorCode = ErrorCode.INTERNAL_ERROR;
    if (response.status === 404) {
      errorCode = ErrorCode.FILE_NOT_FOUND;
    } else if (response.status === 400) {
      errorCode = ErrorCode.INVALID_REQUEST;
    } else if (response.status === 422) {
      errorCode = ErrorCode.VALIDATION_ERROR;
    } else if (response.status === 429) {
      errorCode = ErrorCode.RATE_LIMIT_EXCEEDED;
    } else if (response.status >= 500) {
      errorCode = ErrorCode.INTERNAL_ERROR;
    }

    return {
      code: errorCode,
      message: errorMessage,
      canRetry: shouldRetry(errorCode),
      statusCode: response.status,
    };
  }

  // Handle native Error objects
  if (error instanceof Error) {
    return {
      ...defaultError,
      message: error.message || defaultError.message,
    };
  }

  // Handle string errors
  if (typeof error === 'string') {
    return {
      ...defaultError,
      message: error,
    };
  }

  // Unknown error type
  return defaultError;
}

/**
 * Format validation field errors for display
 */
export function formatFieldErrors(
  fieldErrors?: Array<{ field: string; message: string }>
): string {
  if (!fieldErrors || fieldErrors.length === 0) {
    return '';
  }

  const formattedErrors = fieldErrors
    .map((err) => `${err.field}: ${err.message}`)
    .join(', ');

  return formattedErrors;
}

/**
 * Check if an error is a network connectivity issue
 */
export function isNetworkError(error: ParsedError): boolean {
  return (
    error.code === ErrorCode.NETWORK_ERROR ||
    error.code === ErrorCode.TIMEOUT_ERROR ||
    !error.statusCode // No status code means no response
  );
}

/**
 * Check if an error is a validation error
 */
export function isValidationError(error: ParsedError): boolean {
  return error.code === ErrorCode.VALIDATION_ERROR && !!error.fieldErrors;
}

/**
 * Get a user-friendly error title based on error code
 */
export function getErrorTitle(errorCode: ErrorCode): string {
  const titles: Partial<Record<ErrorCode, string>> = {
    [ErrorCode.NETWORK_ERROR]: 'Connection Error',
    [ErrorCode.TIMEOUT_ERROR]: 'Request Timeout',
    [ErrorCode.VALIDATION_ERROR]: 'Validation Error',
    [ErrorCode.FILE_TOO_LARGE]: 'File Too Large',
    [ErrorCode.INVALID_FILE_FORMAT]: 'Invalid File Format',
    [ErrorCode.MODEL_LOAD_ERROR]: 'Model Error',
    [ErrorCode.INFERENCE_ERROR]: 'Detection Error',
    [ErrorCode.RATE_LIMIT_EXCEEDED]: 'Rate Limit Exceeded',
  };

  return titles[errorCode] || 'Error';
}
