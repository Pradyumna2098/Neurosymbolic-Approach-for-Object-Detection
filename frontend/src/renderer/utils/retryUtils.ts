/**
 * Retry utilities for handling transient errors with exponential backoff
 */

import { ErrorCode, getRetryDelay, MAX_RETRY_ATTEMPTS, shouldRetry } from './errorCodes';
import { parseApiError, ParsedError } from './errorHandling';

/**
 * Options for retry behavior
 */
export interface RetryOptions {
  maxAttempts?: number;
  onRetry?: (attempt: number, error: ParsedError) => void;
  shouldRetry?: (error: ParsedError) => boolean;
}

/**
 * Retry a promise-based function with exponential backoff
 * 
 * @param fn - The async function to retry
 * @param options - Retry configuration options
 * @returns Promise with the function result
 * @throws The last error if all retries fail
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const {
    maxAttempts = MAX_RETRY_ATTEMPTS,
    onRetry,
    shouldRetry: customShouldRetry,
  } = options;

  let lastError: ParsedError | undefined;
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = parseApiError(error);
      
      // Check if we should retry this error
      const shouldRetryError = customShouldRetry
        ? customShouldRetry(lastError)
        : lastError.canRetry;
      
      // Don't retry if this is the last attempt or error is not retriable
      if (attempt >= maxAttempts || !shouldRetryError) {
        throw error;
      }
      
      // Call retry callback
      if (onRetry) {
        onRetry(attempt, lastError);
      }
      
      // Calculate delay based on error code and attempt
      const delay = getRetryDelay(lastError.code, attempt);
      
      // Wait before retrying
      await sleep(delay * 1000);
    }
  }
  
  // This shouldn't be reached, but TypeScript needs it
  throw new Error('Retry loop exhausted');
}

/**
 * Sleep for a specified duration
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Create a retry wrapper for an async function
 * 
 * @param fn - The async function to wrap
 * @param options - Retry configuration options
 * @returns A wrapped function that retries on failure
 */
export function createRetryWrapper<T extends any[], R>(
  fn: (...args: T) => Promise<R>,
  options: RetryOptions = {}
): (...args: T) => Promise<R> {
  return async (...args: T): Promise<R> => {
    return retryWithBackoff(() => fn(...args), options);
  };
}

/**
 * Check if a specific error code should trigger a retry
 */
export function isRetriableError(errorCode: ErrorCode): boolean {
  return shouldRetry(errorCode);
}

/**
 * Format retry delay for display
 */
export function formatRetryDelay(seconds: number): string {
  if (seconds < 60) {
    return `${seconds}s`;
  }
  
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  
  if (remainingSeconds === 0) {
    return `${minutes}m`;
  }
  
  return `${minutes}m ${remainingSeconds}s`;
}
