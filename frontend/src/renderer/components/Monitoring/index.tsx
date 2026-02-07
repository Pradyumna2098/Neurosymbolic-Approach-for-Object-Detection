import React from 'react';
import { Box, Paper, IconButton, Collapse, Tabs, Tab, Divider } from '@mui/material';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { useAppSelector, useAppDispatch } from '../../store/hooks';
import { toggleExpanded, clearLogs } from '../../store/slices/monitoringSlice';
import PerformanceMetrics from './PerformanceMetrics';
import SystemLogs from './SystemLogs';

/**
 * Monitoring Dashboard Component
 * Main component that displays performance metrics and system logs
 * Includes collapsible panel and tabbed interface
 */
const MonitoringDashboard: React.FC = () => {
  const dispatch = useAppDispatch();
  const { logs, metrics, isExpanded } = useAppSelector((state) => state.monitoring);
  const [activeTab, setActiveTab] = React.useState(0);

  const handleToggle = () => {
    dispatch(toggleExpanded());
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleClearLogs = () => {
    dispatch(clearLogs());
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
      {/* Header with Toggle */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          px: 2,
          py: 1,
          borderBottom: 1,
          borderColor: 'divider',
          backgroundColor: 'background.paper',
        }}
      >
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          aria-label="monitoring dashboard tabs"
          sx={{ minHeight: 40 }}
        >
          <Tab label="Performance Metrics" sx={{ minHeight: 40, py: 1 }} />
          <Tab label="System Logs" sx={{ minHeight: 40, py: 1 }} />
        </Tabs>
        <IconButton
          size="small"
          aria-label="toggle monitoring panel"
          onClick={handleToggle}
        >
          {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </IconButton>
      </Box>

      {/* Content Area */}
      <Collapse in={isExpanded}>
        <Box
          sx={{
            height: 300,
            overflow: 'auto',
          }}
        >
          {activeTab === 0 && <PerformanceMetrics metrics={metrics} />}
          {activeTab === 1 && <SystemLogs logs={logs} onClearLogs={handleClearLogs} />}
        </Box>
      </Collapse>

      {/* Collapsed State Summary */}
      {!isExpanded && (
        <Box
          sx={{
            px: 2,
            py: 1,
            display: 'flex',
            alignItems: 'center',
            gap: 2,
            fontSize: '0.875rem',
            color: 'text.secondary',
          }}
        >
          <span>
            {metrics.inferenceTime 
              ? `Inference: ${(metrics.inferenceTime / 1000).toFixed(2)}s`
              : 'Ready'
            }
          </span>
          <Divider orientation="vertical" flexItem />
          <span>
            {metrics.totalDetections !== undefined 
              ? `Detections: ${metrics.totalDetections}`
              : 'No data'
            }
          </span>
          <Divider orientation="vertical" flexItem />
          <span>
            {logs.length > 0 
              ? `${logs.length} log${logs.length !== 1 ? 's' : ''}`
              : 'No logs'
            }
          </span>
        </Box>
      )}
    </Paper>
  );
};

export default MonitoringDashboard;
