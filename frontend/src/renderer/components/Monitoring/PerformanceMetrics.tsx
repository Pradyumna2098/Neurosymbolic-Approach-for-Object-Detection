import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  LinearProgress,
} from '@mui/material';
import SpeedIcon from '@mui/icons-material/Speed';
import TimerIcon from '@mui/icons-material/Timer';
import ImageIcon from '@mui/icons-material/Image';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { PerformanceMetrics as MetricsType } from '../../store/slices/monitoringSlice';

interface PerformanceMetricsProps {
  metrics: MetricsType;
}

/**
 * Performance Metrics Display Component
 * Shows key performance indicators for detection pipeline
 */
const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({ metrics }) => {
  const formatDuration = (ms?: number): string => {
    if (ms === undefined || ms === null) return 'N/A';
    if (ms < 1000) return `${ms.toFixed(0)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const formatNumber = (num?: number): string => {
    if (num === undefined || num === null) return 'N/A';
    return num.toFixed(2);
  };

  const progressPercentage = 
    metrics.totalImages && metrics.imagesProcessed
      ? (metrics.imagesProcessed / metrics.totalImages) * 100
      : 0;

  return (
    <Box sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <SpeedIcon sx={{ mr: 1, color: 'primary.main' }} />
        <Typography variant="h6">Performance Metrics</Typography>
      </Box>

      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: {
          xs: '1fr',
          sm: 'repeat(2, 1fr)',
          md: 'repeat(4, 1fr)'
        },
        gap: 2
      }}>
        {/* Inference Time */}
        <Card variant="outlined" sx={{ height: '100%' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <TimerIcon sx={{ mr: 1, fontSize: '1.2rem', color: 'primary.main' }} />
              <Typography variant="body2" color="text.secondary">
                Inference Time
              </Typography>
            </Box>
            <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
              {formatDuration(metrics.inferenceTime)}
            </Typography>
          </CardContent>
        </Card>

        {/* Total Detections */}
        <Card variant="outlined" sx={{ height: '100%' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <CheckCircleIcon sx={{ mr: 1, fontSize: '1.2rem', color: 'success.main' }} />
              <Typography variant="body2" color="text.secondary">
                Total Detections
              </Typography>
            </Box>
            <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
              {metrics.totalDetections ?? 'N/A'}
            </Typography>
          </CardContent>
        </Card>

        {/* Average Confidence */}
        <Card variant="outlined" sx={{ height: '100%' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <SpeedIcon sx={{ mr: 1, fontSize: '1.2rem', color: 'info.main' }} />
              <Typography variant="body2" color="text.secondary">
                Avg Confidence
              </Typography>
            </Box>
            <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
              {formatNumber(metrics.averageConfidence)}
            </Typography>
          </CardContent>
        </Card>

        {/* Processing Speed */}
        <Card variant="outlined" sx={{ height: '100%' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <ImageIcon sx={{ mr: 1, fontSize: '1.2rem', color: 'warning.main' }} />
              <Typography variant="body2" color="text.secondary">
                Processing Speed
              </Typography>
            </Box>
            <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
              {metrics.processingSpeed 
                ? `${formatNumber(metrics.processingSpeed)} img/s`
                : 'N/A'
              }
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Progress Bar (if processing) */}
      {metrics.totalImages !== undefined && metrics.imagesProcessed !== undefined && (
        <Box sx={{ mt: 2 }}>
          <Card variant="outlined">
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Processing Progress
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {metrics.imagesProcessed} / {metrics.totalImages} images
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={progressPercentage} 
                sx={{ height: 8, borderRadius: 1 }}
              />
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 0.5 }}>
                <Chip 
                  label={`${progressPercentage.toFixed(1)}%`}
                  size="small"
                  color="primary"
                />
              </Box>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Last Updated */}
      {metrics.lastUpdated && (
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'right', mt: 2 }}>
          Last updated: {new Date(metrics.lastUpdated).toLocaleTimeString()}
        </Typography>
      )}
    </Box>
  );
};

export default PerformanceMetrics;
