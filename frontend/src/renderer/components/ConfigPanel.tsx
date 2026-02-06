import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import SettingsIcon from '@mui/icons-material/Settings';

/**
 * Configuration Panel - Placeholder component for detection parameter configuration
 * Location: Bottom-left panel
 * Future: Will contain YOLO/SAHI parameters (confidence, IoU, slice size, etc.)
 */
const ConfigPanel: React.FC = () => {
  return (
    <Paper
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        p: 3,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <SettingsIcon sx={{ mr: 1 }} />
        <Typography variant="h6">Configuration Panel</Typography>
      </Box>
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          border: '2px dashed',
          borderColor: 'divider',
          borderRadius: 1,
        }}
      >
        <Typography variant="body2" color="text.secondary">
          Configuration options coming soon...
        </Typography>
      </Box>
    </Paper>
  );
};

export default ConfigPanel;
