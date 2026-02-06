import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Slider,
  Button,
  FormControl,
  FormControlLabel,
  Select,
  MenuItem,
  Switch,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  InputAdornment,
} from '@mui/material';
import SettingsIcon from '@mui/icons-material/Settings';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import SaveIcon from '@mui/icons-material/Save';
import DeleteIcon from '@mui/icons-material/Delete';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import {
  updateConfig,
  loadPreset,
  savePreset,
  deletePreset,
} from '../store/slices/configSlice';
import { startDetection } from '../store/slices/detectionSlice';

/**
 * Configuration Panel - Full implementation for detection parameter configuration
 * Implements model selection, parameter controls, preset management, and Run Detection
 * Per frontend_ui_design.md specifications
 */
const ConfigPanel: React.FC = () => {
  const dispatch = useAppDispatch();
  const config = useAppSelector((state: any) => state.config);
  const uploadedFiles = useAppSelector((state: any) => state.upload.files);
  const jobStatus = useAppSelector((state: any) => state.detection.jobStatus);

  const [presetDialogOpen, setPresetDialogOpen] = useState(false);
  const [newPresetName, setNewPresetName] = useState('');
  const [savePresetDialogOpen, setSavePresetDialogOpen] = useState(false);

  // Handler for model file selection
  const handleModelSelect = async () => {
    const modelPath = await window.electronAPI.openModelFile();
    if (modelPath) {
      dispatch(updateConfig({ modelPath }));
    }
  };

  // Handler for Prolog rules file selection
  const handlePrologFileSelect = async () => {
    const prologPath = await window.electronAPI.openPrologFile();
    if (prologPath) {
      dispatch(updateConfig({ prologRulesPath: prologPath }));
    }
  };

  // Handler for confidence slider
  const handleConfidenceChange = (_event: Event, newValue: number | number[]) => {
    dispatch(updateConfig({ confidence: newValue as number }));
  };

  // Handler for IoU slider
  const handleIouChange = (_event: Event, newValue: number | number[]) => {
    dispatch(updateConfig({ iouThreshold: newValue as number }));
  };

  // Handler for overlap height slider
  const handleOverlapHeightChange = (_event: Event, newValue: number | number[]) => {
    dispatch(updateConfig({ overlapHeight: newValue as number }));
  };

  // Handler for overlap width slider
  const handleOverlapWidthChange = (_event: Event, newValue: number | number[]) => {
    dispatch(updateConfig({ overlapWidth: newValue as number }));
  };

  // Handler for numeric text field changes
  const handleNumericChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(event.target.value, 10);
    if (!isNaN(value)) {
      dispatch(updateConfig({ [field]: value }));
    }
  };

  // Handler for device selection
  const handleDeviceChange = (event: any) => {
    dispatch(updateConfig({ device: event.target.value as 'cuda' | 'cpu' }));
  };

  // Handler for toggles
  const handleToggleChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    dispatch(updateConfig({ [field]: event.target.checked }));
  };

  // Handler for Run Detection button
  const handleRunDetection = () => {
    if (uploadedFiles.length === 0) {
      alert('Please upload at least one image first.');
      return;
    }
    if (!config.modelPath) {
      alert('Please select a YOLO model file first.');
      return;
    }
    dispatch(startDetection());
  };

  // Handler for saving preset
  const handleSavePreset = () => {
    if (newPresetName.trim()) {
      dispatch(
        savePreset({
          name: newPresetName.trim(),
          config: {
            modelPath: config.modelPath,
            confidence: config.confidence,
            iouThreshold: config.iouThreshold,
            sliceHeight: config.sliceHeight,
            sliceWidth: config.sliceWidth,
            overlapHeight: config.overlapHeight,
            overlapWidth: config.overlapWidth,
            device: config.device,
            batchSize: config.batchSize,
            enableProlog: config.enableProlog,
            prologRulesPath: config.prologRulesPath,
            enableNMS: config.enableNMS,
          },
        })
      );
      setNewPresetName('');
      setSavePresetDialogOpen(false);
    }
  };

  // Handler for loading preset
  const handleLoadPreset = (presetName: string) => {
    dispatch(loadPreset(presetName));
    setPresetDialogOpen(false);
  };

  // Handler for deleting preset
  const handleDeletePreset = (presetName: string) => {
    if (confirm(`Delete preset "${presetName}"?`)) {
      dispatch(deletePreset(presetName));
    }
  };

  // Get shortened model path for display
  const getModelFileName = (path: string) => {
    if (!path) return 'No model selected';
    const parts = path.split(/[\\/]/);
    return parts[parts.length - 1];
  };

  const isRunDisabled = uploadedFiles.length === 0 || !config.modelPath || jobStatus === 'running';

  return (
    <Paper
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'auto',
      }}
    >
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          p: 2,
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <SettingsIcon sx={{ mr: 1 }} />
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Configuration
        </Typography>
        <Tooltip title="Load Preset">
          <IconButton size="small" onClick={() => setPresetDialogOpen(true)}>
            <BookmarkIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Scrollable Content */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        {/* Model Selection */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom fontWeight="bold">
            Model
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
            <Button
              variant="outlined"
              startIcon={<FolderOpenIcon />}
              onClick={handleModelSelect}
              fullWidth
            >
              Select Model
            </Button>
          </Box>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
            {getModelFileName(config.modelPath)}
          </Typography>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* YOLO Parameters */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom fontWeight="bold">
            YOLO Parameters
          </Typography>

          {/* Confidence Threshold */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" gutterBottom>
              Confidence: {config.confidence.toFixed(2)}
            </Typography>
            <Slider
              value={config.confidence}
              onChange={handleConfidenceChange}
              min={0.01}
              max={1.0}
              step={0.01}
              valueLabelDisplay="auto"
              size="small"
            />
          </Box>

          {/* IoU Threshold */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" gutterBottom>
              IoU Threshold: {config.iouThreshold.toFixed(2)}
            </Typography>
            <Slider
              value={config.iouThreshold}
              onChange={handleIouChange}
              min={0.01}
              max={1.0}
              step={0.01}
              valueLabelDisplay="auto"
              size="small"
            />
          </Box>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* SAHI Parameters */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom fontWeight="bold">
            SAHI Parameters
          </Typography>

          {/* Slice Height */}
          <TextField
            label="Slice Height"
            type="number"
            value={config.sliceHeight}
            onChange={handleNumericChange('sliceHeight')}
            size="small"
            fullWidth
            sx={{ mb: 2 }}
            InputProps={{
              endAdornment: <InputAdornment position="end">px</InputAdornment>,
            }}
            inputProps={{ min: 256, max: 2048, step: 64 }}
          />

          {/* Slice Width */}
          <TextField
            label="Slice Width"
            type="number"
            value={config.sliceWidth}
            onChange={handleNumericChange('sliceWidth')}
            size="small"
            fullWidth
            sx={{ mb: 2 }}
            InputProps={{
              endAdornment: <InputAdornment position="end">px</InputAdornment>,
            }}
            inputProps={{ min: 256, max: 2048, step: 64 }}
          />

          {/* Overlap Height Ratio */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" gutterBottom>
              Overlap Height: {config.overlapHeight.toFixed(2)}
            </Typography>
            <Slider
              value={config.overlapHeight}
              onChange={handleOverlapHeightChange}
              min={0.0}
              max={0.5}
              step={0.05}
              valueLabelDisplay="auto"
              size="small"
            />
          </Box>

          {/* Overlap Width Ratio */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" gutterBottom>
              Overlap Width: {config.overlapWidth.toFixed(2)}
            </Typography>
            <Slider
              value={config.overlapWidth}
              onChange={handleOverlapWidthChange}
              min={0.0}
              max={0.5}
              step={0.05}
              valueLabelDisplay="auto"
              size="small"
            />
          </Box>
        </Box>

        {/* Advanced Options */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle2" fontWeight="bold">
              Advanced Options
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box>
              {/* Device Selection */}
              <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                <Typography variant="body2" gutterBottom>
                  Device
                </Typography>
                <Select value={config.device} onChange={handleDeviceChange}>
                  <MenuItem value="cuda">CUDA (GPU)</MenuItem>
                  <MenuItem value="cpu">CPU</MenuItem>
                </Select>
              </FormControl>

              {/* Batch Size */}
              <TextField
                label="Batch Size"
                type="number"
                value={config.batchSize}
                onChange={handleNumericChange('batchSize')}
                size="small"
                fullWidth
                sx={{ mb: 2 }}
                inputProps={{ min: 1, max: 32, step: 1 }}
              />

              {/* Enable NMS */}
              <FormControlLabel
                control={
                  <Switch
                    checked={config.enableNMS}
                    onChange={handleToggleChange('enableNMS')}
                    size="small"
                  />
                }
                label="Enable NMS"
                sx={{ mb: 1, display: 'block' }}
              />

              {/* Enable Symbolic Reasoning */}
              <FormControlLabel
                control={
                  <Switch
                    checked={config.enableProlog}
                    onChange={handleToggleChange('enableProlog')}
                    size="small"
                  />
                }
                label="Enable Symbolic Reasoning"
                sx={{ mb: 2, display: 'block' }}
              />

              {/* Prolog Rules File (conditional) */}
              {config.enableProlog && (
                <Box sx={{ mb: 2 }}>
                  <Button
                    variant="outlined"
                    startIcon={<FolderOpenIcon />}
                    onClick={handlePrologFileSelect}
                    fullWidth
                    size="small"
                  >
                    Select Prolog Rules
                  </Button>
                  {config.prologRulesPath && (
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                      {getModelFileName(config.prologRulesPath)}
                    </Typography>
                  )}
                </Box>
              )}
            </Box>
          </AccordionDetails>
        </Accordion>
      </Box>

      {/* Footer with Actions */}
      <Box
        sx={{
          p: 2,
          borderTop: 1,
          borderColor: 'divider',
          display: 'flex',
          gap: 1,
        }}
      >
        <Button
          variant="outlined"
          startIcon={<SaveIcon />}
          onClick={() => setSavePresetDialogOpen(true)}
          size="small"
        >
          Save Preset
        </Button>
        <Button
          variant="contained"
          startIcon={<PlayArrowIcon />}
          onClick={handleRunDetection}
          disabled={isRunDisabled}
          fullWidth
          size="small"
        >
          Run Detection
        </Button>
      </Box>

      {/* Preset Management Dialog */}
      <Dialog open={presetDialogOpen} onClose={() => setPresetDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Load Preset</DialogTitle>
        <DialogContent>
          {config.presets.length === 0 ? (
            <Typography variant="body2" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
              No saved presets. Save your current configuration to create one.
            </Typography>
          ) : (
            <List>
              {config.presets.map((preset: any) => (
                <React.Fragment key={preset.name}>
                  <ListItem
                    button
                    onClick={() => handleLoadPreset(preset.name)}
                    selected={config.currentPreset === preset.name}
                  >
                    <ListItemText
                      primary={preset.name}
                      secondary={`Conf: ${preset.config.confidence.toFixed(2)}, IoU: ${preset.config.iouThreshold.toFixed(2)}`}
                    />
                    <ListItemSecondaryAction>
                      <IconButton
                        edge="end"
                        aria-label="delete"
                        onClick={(e: React.MouseEvent) => {
                          e.stopPropagation();
                          handleDeletePreset(preset.name);
                        }}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPresetDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Save Preset Dialog */}
      <Dialog open={savePresetDialogOpen} onClose={() => setSavePresetDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Save Preset</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Preset Name"
            type="text"
            fullWidth
            value={newPresetName}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewPresetName(e.target.value)}
            onKeyPress={(e: React.KeyboardEvent) => {
              if (e.key === 'Enter') {
                handleSavePreset();
              }
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSavePresetDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSavePreset} variant="contained" disabled={!newPresetName.trim()}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default ConfigPanel;
