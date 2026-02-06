import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { DetectionConfig } from '../../types';

interface ConfigState extends DetectionConfig {
  presets: {
    name: string;
    config: DetectionConfig;
  }[];
  currentPreset: string | null;
}

// Default configuration values
const defaultConfig: DetectionConfig = {
  modelPath: '',
  confidence: 0.25,
  iouThreshold: 0.45,
  sliceHeight: 640,
  sliceWidth: 640,
  overlapHeight: 0.2,
  overlapWidth: 0.2,
  device: 'cuda',
  enableProlog: false,
  enableNMS: true,
};

const initialState: ConfigState = {
  ...defaultConfig,
  presets: [],
  currentPreset: null,
};

const configSlice = createSlice({
  name: 'config',
  initialState,
  reducers: {
    updateConfig(state, action: PayloadAction<Partial<DetectionConfig>>) {
      // Update configuration values
      Object.assign(state, action.payload);
      // Clear current preset if config is manually changed
      if (state.currentPreset !== null) {
        state.currentPreset = null;
      }
    },
    loadPreset(state, action: PayloadAction<string>) {
      // Load a saved preset
      const preset = state.presets.find((p) => p.name === action.payload);
      if (preset) {
        Object.assign(state, preset.config);
        state.currentPreset = action.payload;
      }
    },
    savePreset(
      state,
      action: PayloadAction<{ name: string; config: DetectionConfig }>
    ) {
      // Save current config as a preset
      const existingIndex = state.presets.findIndex(
        (p) => p.name === action.payload.name
      );
      if (existingIndex >= 0) {
        state.presets[existingIndex] = action.payload;
      } else {
        state.presets.push(action.payload);
      }
    },
    deletePreset(state, action: PayloadAction<string>) {
      state.presets = state.presets.filter((p) => p.name !== action.payload);
      if (state.currentPreset === action.payload) {
        state.currentPreset = null;
      }
    },
    resetConfig(state) {
      return {
        ...initialState,
        presets: state.presets, // Keep saved presets
      };
    },
  },
});

export const {
  updateConfig,
  loadPreset,
  savePreset,
  deletePreset,
  resetConfig,
} = configSlice.actions;

export default configSlice.reducer;
