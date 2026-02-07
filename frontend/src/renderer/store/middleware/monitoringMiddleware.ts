import { Middleware, UnknownAction } from '@reduxjs/toolkit';
import { addLog, updateMetrics, clearMetrics } from '../slices/monitoringSlice';

/**
 * Redux middleware that automatically logs detection events
 * and updates performance metrics based on state changes
 */
export const monitoringMiddleware: Middleware = (store) => (next) => (action: UnknownAction) => {
  const result = next(action);
  const state = store.getState();

  // Log detection events
  if (action.type.startsWith('detection/')) {
    switch (action.type) {
      case 'detection/startDetection':
        // Reset metrics for new detection run
        store.dispatch(clearMetrics());
        
        store.dispatch(addLog({
          level: 'info',
          message: `Detection started for job: ${(action as any).payload}`,
          source: 'Detection',
        }));
        break;

      case 'detection/updateProgress':
        if ((action as any).payload.message) {
          store.dispatch(addLog({
            level: 'info',
            message: (action as any).payload.message,
            source: 'Detection',
          }));
        }
        
        // Update metrics if we have progress data
        if ((action as any).payload.progress !== undefined) {
          const totalImages = state.upload.files.length;
          const processed = Math.floor(((action as any).payload.progress / 100) * totalImages);
          store.dispatch(updateMetrics({
            imagesProcessed: processed,
            totalImages: totalImages,
          }));
        }
        break;

      case 'detection/completeDetection':
        store.dispatch(addLog({
          level: 'success',
          message: 'Detection completed successfully',
          source: 'Detection',
        }));
        
        // Calculate final metrics
        const completedAt = state.detection.completedAt;
        const startedAt = state.detection.startedAt;
        if (completedAt && startedAt) {
          const inferenceTime = new Date(completedAt).getTime() - new Date(startedAt).getTime();
          
          // Guard against divide-by-zero: only calculate speed if inferenceTime > 0
          if (inferenceTime > 0) {
            const processingSpeed = state.upload.files.length / (inferenceTime / 1000);
            
            store.dispatch(updateMetrics({
              inferenceTime,
              processingSpeed,
              imagesProcessed: state.upload.files.length,
              totalImages: state.upload.files.length,
            }));
          } else {
            // If inferenceTime is 0 or negative, don't calculate speed
            store.dispatch(updateMetrics({
              inferenceTime,
              imagesProcessed: state.upload.files.length,
              totalImages: state.upload.files.length,
            }));
          }
        }
        break;

      case 'detection/setDetectionError':
        store.dispatch(addLog({
          level: 'error',
          message: `Detection failed: ${(action as any).payload}`,
          source: 'Detection',
        }));
        break;

      case 'detection/cancelDetection':
        store.dispatch(addLog({
          level: 'warning',
          message: 'Detection cancelled by user',
          source: 'Detection',
        }));
        break;
    }
  }

  // Log upload events
  if (action.type.startsWith('upload/')) {
    switch (action.type) {
      case 'upload/addFiles':
        store.dispatch(addLog({
          level: 'info',
          message: `${(action as any).payload.length} file(s) uploaded`,
          source: 'Upload',
        }));
        break;

      case 'upload/removeFile':
        store.dispatch(addLog({
          level: 'info',
          message: 'File removed from upload list',
          source: 'Upload',
        }));
        break;

      case 'upload/clearFiles':
        store.dispatch(addLog({
          level: 'info',
          message: 'Upload list cleared',
          source: 'Upload',
        }));
        break;
    }
  }

  // Log results events
  if (action.type.startsWith('results/')) {
    switch (action.type) {
      case 'results/setResults':
        const results = (action as any).payload;
        if (results && results.length > 0) {
          const totalDetections = results.reduce(
            (sum: number, result: any) => sum + (result.detections?.length ?? 0),
            0
          );
          
          // Calculate weighted average confidence: sum of all confidences / total detections
          const totalConfidenceSum = results.reduce(
            (sum: number, result: any) => {
              const detections = result.detections ?? [];
              const confidenceSum = detections.reduce(
                (s: number, d: any) => s + (d.confidence ?? 0),
                0
              );
              return sum + confidenceSum;
            },
            0
          );
          const avgConfidence = totalDetections > 0 ? totalConfidenceSum / totalDetections : 0;

          store.dispatch(updateMetrics({
            totalDetections,
            averageConfidence: avgConfidence,
          }));

          store.dispatch(addLog({
            level: 'success',
            message: `Results loaded: ${totalDetections} detections across ${results.length} images`,
            source: 'Results',
          }));
        }
        break;
    }
  }

  // Log config changes
  if (action.type.startsWith('config/')) {
    switch (action.type) {
      case 'config/updateConfig':
        store.dispatch(addLog({
          level: 'info',
          message: 'Configuration updated',
          source: 'Config',
        }));
        break;

      case 'config/resetConfig':
        store.dispatch(addLog({
          level: 'info',
          message: 'Configuration reset to defaults',
          source: 'Config',
        }));
        break;
    }
  }

  return result;
};
