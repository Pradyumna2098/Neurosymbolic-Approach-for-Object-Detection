import React from 'react';
import { Box, Typography, Paper, Tabs, Tab } from '@mui/material';
import ImageIcon from '@mui/icons-material/Image';

/**
 * Results Panel - Placeholder component for detection results visualization
 * Location: Main content area (center-right)
 * Future: Will contain tabs for Input, Labels, Output, Compare views with image canvas
 */
const ResultsPanel: React.FC = () => {
  const [selectedTab, setSelectedTab] = React.useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  return (
    <Paper
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={selectedTab} onChange={handleTabChange} aria-label="result tabs">
          <Tab label="Input" />
          <Tab label="Labels" />
          <Tab label="Output" />
          <Tab label="Compare" />
        </Tabs>
      </Box>
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: 3,
        }}
      >
        <Box sx={{ textAlign: 'center' }}>
          <ImageIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="body2" color="text.secondary">
            Results visualization coming soon...
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};

export default ResultsPanel;
