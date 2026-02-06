/**
 * Simple validation script to test Redux store setup
 * This can be run in the browser console or as a Node script
 */

import { store } from './store';
import {
  addFiles,
  removeFile,
  clearFiles,
} from './store/slices/uploadSlice';
import { updateConfig } from './store/slices/configSlice';
import { startDetection } from './store/slices/detectionSlice';
import { setResults } from './store/slices/resultsSlice';

// Test the store configuration
console.log('Testing Redux store...');

// Check initial state
console.log('Initial state:', store.getState());

// Test upload slice
store.dispatch(
  addFiles([
    {
      id: 'test-1',
      name: 'test-image.jpg',
      size: 1024000,
      path: '/path/to/test-image.jpg',
      uploadedAt: new Date(),
    },
  ])
);
console.log('After adding file:', store.getState().upload);

// Test config slice
store.dispatch(
  updateConfig({
    confidence: 0.5,
    iouThreshold: 0.4,
  })
);
console.log('After updating config:', store.getState().config);

// Test detection slice
store.dispatch(startDetection('test-job-123'));
console.log('After starting detection:', store.getState().detection);

// Test results slice
store.dispatch(
  setResults([
    {
      imageId: 'img-1',
      imageName: 'test.jpg',
      imagePath: '/path/to/test.jpg',
      detections: [],
      metadata: {
        processingTime: 1000,
        totalDetections: 0,
        timestamp: new Date(),
      },
    },
  ])
);
console.log('After setting results:', store.getState().results);

// Test clearing
store.dispatch(clearFiles());
console.log('After clearing files:', store.getState().upload);

console.log('✅ All Redux store operations completed successfully!');
console.log('✅ Redux DevTools should be available in browser extension');
