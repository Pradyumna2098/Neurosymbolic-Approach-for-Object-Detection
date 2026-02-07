import { createSlice, PayloadAction } from '@reduxjs/toolkit';

/**
 * Log entry for system monitoring
 */
export interface LogEntry {
  id: string;
  timestamp: Date;
  level: 'info' | 'warning' | 'error' | 'success';
  message: string;
  source?: string;
}

/**
 * Performance metrics for monitoring
 */
export interface PerformanceMetrics {
  inferenceTime?: number; // milliseconds
  totalDetections?: number;
  averageConfidence?: number;
  imagesProcessed?: number;
  totalImages?: number;
  processingSpeed?: number; // images per second
  lastUpdated?: Date;
}

/**
 * Monitoring state
 */
interface MonitoringState {
  logs: LogEntry[];
  metrics: PerformanceMetrics;
  isExpanded: boolean;
  maxLogs: number;
}

const initialState: MonitoringState = {
  logs: [],
  metrics: {},
  isExpanded: true,
  maxLogs: 100, // Keep last 100 logs
};

const monitoringSlice = createSlice({
  name: 'monitoring',
  initialState,
  reducers: {
    addLog(state, action: PayloadAction<Omit<LogEntry, 'id' | 'timestamp'>>) {
      const newLog: LogEntry = {
        ...action.payload,
        id: `log-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        timestamp: new Date(),
      };
      
      state.logs.unshift(newLog); // Add to beginning
      
      // Keep only maxLogs entries
      if (state.logs.length > state.maxLogs) {
        state.logs = state.logs.slice(0, state.maxLogs);
      }
    },
    
    updateMetrics(state, action: PayloadAction<Partial<PerformanceMetrics>>) {
      state.metrics = {
        ...state.metrics,
        ...action.payload,
        lastUpdated: new Date(),
      };
    },
    
    clearLogs(state) {
      state.logs = [];
    },
    
    clearMetrics(state) {
      state.metrics = {};
    },
    
    toggleExpanded(state) {
      state.isExpanded = !state.isExpanded;
    },
    
    setExpanded(state, action: PayloadAction<boolean>) {
      state.isExpanded = action.payload;
    },
    
    resetMonitoring() {
      return initialState;
    },
  },
});

export const {
  addLog,
  updateMetrics,
  clearLogs,
  clearMetrics,
  toggleExpanded,
  setExpanded,
  resetMonitoring,
} = monitoringSlice.actions;

export default monitoringSlice.reducer;
