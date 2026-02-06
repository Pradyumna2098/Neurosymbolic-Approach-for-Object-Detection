import React from 'react';
import { Box, Typography, Paper, IconButton, Collapse } from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

/**
 * Monitoring Panel - Placeholder component for Prometheus metrics and logs
 * Location: Bottom panel (collapsible)
 * Future: Will contain Prometheus metrics, performance stats, and logs
 */
const MonitoringPanel: React.FC = () => {
  const [expanded, setExpanded] = React.useState(true);

  const handleToggle = () => {
    setExpanded(!expanded);
  };

  return (
    <Paper
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        borderTop: 1,
        borderColor: 'divider',
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          p: 2,
          cursor: 'pointer',
        }}
        onClick={handleToggle}
        role="button"
        tabIndex={0}
        onKeyDown={(e: React.KeyboardEvent) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleToggle();
          }
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <VisibilityIcon sx={{ mr: 1 }} />
          <Typography variant="h6">Monitoring Dashboard</Typography>
        </Box>
        <IconButton
          size="small"
          aria-label="toggle monitoring panel"
          onClick={(event: React.MouseEvent) => {
            event.stopPropagation();
            handleToggle();
          }}
        >
          {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </IconButton>
      </Box>
      <Collapse in={expanded}>
        <Box
          sx={{
            height: 200,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderTop: 1,
            borderColor: 'divider',
          }}
        >
          <Typography variant="body2" color="text.secondary">
            Monitoring dashboard coming soon...
          </Typography>
        </Box>
      </Collapse>
    </Paper>
  );
};

export default MonitoringPanel;
