import { configureStore } from '@reduxjs/toolkit';
import uploadReducer from './slices/uploadSlice';
import configReducer from './slices/configSlice';
import detectionReducer from './slices/detectionSlice';
import resultsReducer from './slices/resultsSlice';

export const store = configureStore({
  reducer: {
    upload: uploadReducer,
    config: configReducer,
    detection: detectionReducer,
    results: resultsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types with non-serializable values (Date, File objects)
        ignoredActions: [
          'upload/addFiles',
          'detection/startDetection',
          'detection/completeDetection',
          'detection/setDetectionError',
        ],
        // Ignore these field paths in all actions
        ignoredActionPaths: ['payload.uploadedAt', 'payload.timestamp'],
        // Ignore these paths in the state
        ignoredPaths: [
          'upload.files',
          'detection.startedAt',
          'detection.completedAt',
          'results.results',
        ],
      },
    }),
  devTools: process.env.NODE_ENV !== 'production',
});

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
