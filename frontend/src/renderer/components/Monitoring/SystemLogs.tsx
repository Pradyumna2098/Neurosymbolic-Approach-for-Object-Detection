import React, { useRef, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  IconButton,
  Tooltip,
  TextField,
  InputAdornment,
  Chip,
} from '@mui/material';
import ClearIcon from '@mui/icons-material/Clear';
import SearchIcon from '@mui/icons-material/Search';
import InfoIcon from '@mui/icons-material/Info';
import WarningIcon from '@mui/icons-material/Warning';
import ErrorIcon from '@mui/icons-material/Error';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { LogEntry } from '../../store/slices/monitoringSlice';

interface SystemLogsProps {
  logs: LogEntry[];
  onClearLogs: () => void;
}

/**
 * System Logs Display Component
 * Shows chronological log entries with filtering capabilities
 */
const SystemLogs: React.FC<SystemLogsProps> = ({ logs, onClearLogs }) => {
  const [searchFilter, setSearchFilter] = React.useState('');
  const [levelFilter, setLevelFilter] = React.useState<string | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  const getLogIcon = (level: LogEntry['level']) => {
    switch (level) {
      case 'info':
        return <InfoIcon fontSize="small" sx={{ color: 'info.main' }} />;
      case 'warning':
        return <WarningIcon fontSize="small" sx={{ color: 'warning.main' }} />;
      case 'error':
        return <ErrorIcon fontSize="small" sx={{ color: 'error.main' }} />;
      case 'success':
        return <CheckCircleIcon fontSize="small" sx={{ color: 'success.main' }} />;
      default:
        return <InfoIcon fontSize="small" />;
    }
  };

  const getLogColor = (level: LogEntry['level']) => {
    switch (level) {
      case 'info':
        return 'info.light';
      case 'warning':
        return 'warning.light';
      case 'error':
        return 'error.light';
      case 'success':
        return 'success.light';
      default:
        return 'grey.300';
    }
  };

  const filteredLogs = logs.filter((log) => {
    const matchesSearch = log.message.toLowerCase().includes(searchFilter.toLowerCase()) ||
                         (log.source?.toLowerCase().includes(searchFilter.toLowerCase()) ?? false);
    const matchesLevel = levelFilter === null || log.level === levelFilter;
    return matchesSearch && matchesLevel;
  });

  return (
    <Box sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">System Logs</Typography>
        <Tooltip title="Clear all logs">
          <IconButton size="small" onClick={onClearLogs}>
            <ClearIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Filters */}
      <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
        <TextField
          size="small"
          placeholder="Search logs..."
          value={searchFilter}
          onChange={(e) => setSearchFilter(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
          }}
          sx={{ flexGrow: 1, minWidth: 200 }}
        />
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Chip
            label="All"
            size="small"
            onClick={() => setLevelFilter(null)}
            color={levelFilter === null ? 'primary' : 'default'}
            variant={levelFilter === null ? 'filled' : 'outlined'}
          />
          <Chip
            label="Info"
            size="small"
            onClick={() => setLevelFilter('info')}
            color={levelFilter === 'info' ? 'info' : 'default'}
            variant={levelFilter === 'info' ? 'filled' : 'outlined'}
          />
          <Chip
            label="Success"
            size="small"
            onClick={() => setLevelFilter('success')}
            color={levelFilter === 'success' ? 'success' : 'default'}
            variant={levelFilter === 'success' ? 'filled' : 'outlined'}
          />
          <Chip
            label="Warning"
            size="small"
            onClick={() => setLevelFilter('warning')}
            color={levelFilter === 'warning' ? 'warning' : 'default'}
            variant={levelFilter === 'warning' ? 'filled' : 'outlined'}
          />
          <Chip
            label="Error"
            size="small"
            onClick={() => setLevelFilter('error')}
            color={levelFilter === 'error' ? 'error' : 'default'}
            variant={levelFilter === 'error' ? 'filled' : 'outlined'}
          />
        </Box>
      </Box>

      {/* Logs Display */}
      <Paper
        variant="outlined"
        sx={{
          flexGrow: 1,
          overflow: 'auto',
          p: 1,
          backgroundColor: 'background.default',
          fontFamily: 'monospace',
        }}
      >
        {filteredLogs.length === 0 ? (
          <Box
            sx={{
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Typography variant="body2" color="text.secondary">
              {logs.length === 0 ? 'No logs yet' : 'No logs match the current filter'}
            </Typography>
          </Box>
        ) : (
          filteredLogs.map((log) => (
            <Box
              key={log.id}
              sx={{
                display: 'flex',
                alignItems: 'flex-start',
                p: 1,
                mb: 0.5,
                borderRadius: 1,
                borderLeft: 3,
                borderColor: getLogColor(log.level),
                backgroundColor: 'background.paper',
                '&:hover': {
                  backgroundColor: 'action.hover',
                },
              }}
            >
              <Box sx={{ mr: 1, mt: 0.25 }}>
                {getLogIcon(log.level)}
              </Box>
              <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
                  <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </Typography>
                  {log.source && (
                    <Chip
                      label={log.source}
                      size="small"
                      sx={{ height: 16, fontSize: '0.65rem' }}
                    />
                  )}
                </Box>
                <Typography
                  variant="body2"
                  sx={{
                    fontFamily: 'monospace',
                    fontSize: '0.875rem',
                    wordBreak: 'break-word',
                  }}
                >
                  {log.message}
                </Typography>
              </Box>
            </Box>
          ))
        )}
        <div ref={logsEndRef} />
      </Paper>

      {/* Footer Info */}
      <Box sx={{ mt: 1, display: 'flex', justifyContent: 'space-between' }}>
        <Typography variant="caption" color="text.secondary">
          Showing {filteredLogs.length} of {logs.length} logs
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Max {100} logs retained
        </Typography>
      </Box>
    </Box>
  );
};

export default SystemLogs;
