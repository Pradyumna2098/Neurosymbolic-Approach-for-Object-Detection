import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

/**
 * Upload Panel - Placeholder component for image upload functionality
 * Location: Top-left panel
 * Future: Will contain file browser, drag-drop, preview list
 */
const UploadPanel: React.FC = () => {
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
        <CloudUploadIcon sx={{ mr: 1 }} />
        <Typography variant="h6">Upload Panel</Typography>
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
          Upload functionality coming soon...
        </Typography>
      </Box>
    </Paper>
  );
};

export default UploadPanel;
