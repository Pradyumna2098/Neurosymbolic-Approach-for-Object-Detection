/**
 * Custom React hook for polling job status
 * 
 * Automatically polls the backend API at regular intervals
 * to update job status and progress until completion or failure
 */

import { useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '..';
import { pollStatusThunk } from '../slices/detectionThunks';
import { fetchResultsThunk } from '../slices/resultsThunks';

/**
 * Hook to poll job status at regular intervals
 * 
 * @param enabled - Whether polling is enabled
 * @param intervalMs - Polling interval in milliseconds (default: 2000ms)
 */
export function useJobStatusPolling(enabled = true, intervalMs = 2000) {
  const dispatch = useDispatch<AppDispatch>();
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  
  const { jobId, status } = useSelector((state: RootState) => state.detection);

  useEffect(() => {
    // Clear any existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    // Don't start polling if:
    // - Polling is disabled
    // - No job ID
    // - Job is in terminal state (complete or error)
    if (
      !enabled ||
      !jobId ||
      status === 'complete' ||
      status === 'error' ||
      status === 'idle'
    ) {
      return;
    }

    // Start polling
    console.log(`[Polling] Starting status polling for job ${jobId} (interval: ${intervalMs}ms)`);
    
    // Poll immediately on start
    dispatch(pollStatusThunk(jobId));

    // Set up interval for subsequent polls
    intervalRef.current = setInterval(() => {
      dispatch(pollStatusThunk(jobId));
    }, intervalMs);

    // Cleanup on unmount or dependency change
    return () => {
      if (intervalRef.current) {
        console.log('[Polling] Stopping status polling');
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [dispatch, enabled, jobId, status, intervalMs]);

  return { isPolling: !!intervalRef.current };
}

/**
 * Hook to automatically fetch results when job completes
 */
export function useAutoFetchResults() {
  const dispatch = useDispatch<AppDispatch>();
  const { jobId, status } = useSelector((state: RootState) => state.detection);
  const resultsLoaded = useSelector((state: RootState) => state.results.results.length > 0);
  
  const prevStatusRef = useRef<string | null>(null);

  useEffect(() => {
    // Detect status change to 'complete'
    if (
      status === 'complete' &&
      prevStatusRef.current !== 'complete' &&
      jobId &&
      !resultsLoaded
    ) {
      console.log(`[Auto-fetch] Job completed, fetching results for job ${jobId}`);
      dispatch(fetchResultsThunk(jobId));
    }

    prevStatusRef.current = status;
  }, [dispatch, status, jobId, resultsLoaded]);
}
