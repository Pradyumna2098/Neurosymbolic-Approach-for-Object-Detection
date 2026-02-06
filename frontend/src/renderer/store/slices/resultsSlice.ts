import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { DetectionResult } from '../../types';

interface ResultsState {
  results: DetectionResult[];
  currentImageIndex: number;
  selectedDetectionIds: string[];
  filters: {
    classIds: number[];
    minConfidence: number;
    maxConfidence: number;
    showLabels: boolean;
    showConfidence: boolean;
  };
  viewMode: 'single' | 'grid' | 'compare';
  compareImageIndices: [number, number] | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: ResultsState = {
  results: [],
  currentImageIndex: 0,
  selectedDetectionIds: [],
  filters: {
    classIds: [],
    minConfidence: 0.0,
    maxConfidence: 1.0,
    showLabels: true,
    showConfidence: true,
  },
  viewMode: 'single',
  compareImageIndices: null,
  isLoading: false,
  error: null,
};

const resultsSlice = createSlice({
  name: 'results',
  initialState,
  reducers: {
    setResults(state, action: PayloadAction<DetectionResult[]>) {
      state.results = action.payload;
      state.currentImageIndex = 0;
      state.selectedDetectionIds = [];
      state.isLoading = false;
      state.error = null;
    },
    setCurrentImageIndex(state, action: PayloadAction<number>) {
      if (action.payload >= 0 && action.payload < state.results.length) {
        state.currentImageIndex = action.payload;
        state.selectedDetectionIds = [];
      }
    },
    nextImage(state) {
      if (state.currentImageIndex < state.results.length - 1) {
        state.currentImageIndex += 1;
        state.selectedDetectionIds = [];
      }
    },
    previousImage(state) {
      if (state.currentImageIndex > 0) {
        state.currentImageIndex -= 1;
        state.selectedDetectionIds = [];
      }
    },
    selectDetection(state, action: PayloadAction<string>) {
      const id = action.payload;
      if (!state.selectedDetectionIds.includes(id)) {
        state.selectedDetectionIds.push(id);
      }
    },
    deselectDetection(state, action: PayloadAction<string>) {
      state.selectedDetectionIds = state.selectedDetectionIds.filter(
        (id) => id !== action.payload
      );
    },
    toggleDetectionSelection(state, action: PayloadAction<string>) {
      const id = action.payload;
      const index = state.selectedDetectionIds.indexOf(id);
      if (index >= 0) {
        state.selectedDetectionIds.splice(index, 1);
      } else {
        state.selectedDetectionIds.push(id);
      }
    },
    clearSelection(state) {
      state.selectedDetectionIds = [];
    },
    updateFilters(
      state,
      action: PayloadAction<Partial<ResultsState['filters']>>
    ) {
      state.filters = { ...state.filters, ...action.payload };
    },
    resetFilters(state) {
      state.filters = {
        classIds: [],
        minConfidence: 0.0,
        maxConfidence: 1.0,
        showLabels: true,
        showConfidence: true,
      };
    },
    setViewMode(state, action: PayloadAction<ResultsState['viewMode']>) {
      state.viewMode = action.payload;
      if (action.payload !== 'compare') {
        state.compareImageIndices = null;
      }
    },
    setCompareImages(state, action: PayloadAction<[number, number]>) {
      if (state.viewMode === 'compare') {
        state.compareImageIndices = action.payload;
      }
    },
    setLoading(state, action: PayloadAction<boolean>) {
      state.isLoading = action.payload;
    },
    setResultsError(state, action: PayloadAction<string>) {
      state.error = action.payload;
      state.isLoading = false;
    },
    clearResults() {
      return initialState;
    },
  },
});

export const {
  setResults,
  setCurrentImageIndex,
  nextImage,
  previousImage,
  selectDetection,
  deselectDetection,
  toggleDetectionSelection,
  clearSelection,
  updateFilters,
  resetFilters,
  setViewMode,
  setCompareImages,
  setLoading,
  setResultsError,
  clearResults,
} = resultsSlice.actions;

export default resultsSlice.reducer;
