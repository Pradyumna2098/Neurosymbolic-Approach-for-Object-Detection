/**
 * JobErrorCard component
 * 
 * Displays detailed error information for failed detection jobs
 */

import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Box,
  Chip,
  Divider,
} from '@mui/material';
import {
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { JobError } from '../services/api/types';
import { ErrorCode } from '../utils/errorCodes';

interface JobErrorCardProps {
  jobId: string;
  error: JobError;
  onRetry?: () => void;
  onDismiss?: () => void;
  timestamp?: string;
}

export default function JobErrorCard({
  jobId,
  error,
  onRetry,
  onDismiss,
  timestamp,
}: JobErrorCardProps) {
  const errorCode = error.code as ErrorCode;
  
  // Determine if this error is retriable
  const isRetriable = [
    ErrorCode.INTERNAL_ERROR,
    ErrorCode.INFERENCE_ERROR,
    ErrorCode.MEMORY_ERROR,
    ErrorCode.CUDA_OOM,
  ].includes(errorCode);

  const showRetry = isRetriable && onRetry;

  return (
    <Card
      variant="outlined"
      sx={{
        borderColor: 'error.main',
        borderWidth: 2,
        backgroundColor: 'error.light',
        backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.9))',
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="flex-start" gap={2}>
          <ErrorIcon color="error" sx={{ mt: 0.5 }} />
          <Box flex={1}>
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <Typography variant="h6" color="error.main">
                Job Failed
              </Typography>
              <Chip
                label={error.code}
                size="small"
                color="error"
                variant="outlined"
              />
            </Box>

            <Typography variant="body2" color="text.secondary" gutterBottom>
              Job ID: {jobId}
            </Typography>

            <Typography variant="body1" sx={{ mt: 1, mb: 1 }}>
              {error.message}
            </Typography>

            {error.details && (
              <>
                <Divider sx={{ my: 1 }} />
                <Typography variant="body2" color="text.secondary">
                  <strong>Details:</strong> {error.details}
                </Typography>
              </>
            )}

            {timestamp && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Failed at: {new Date(timestamp).toLocaleString()}
              </Typography>
            )}
          </Box>
        </Box>
      </CardContent>

      {(showRetry || onDismiss) && (
        <CardActions sx={{ justifyContent: 'flex-end', pt: 0 }}>
          {showRetry && (
            <Button
              size="small"
              color="primary"
              startIcon={<RefreshIcon />}
              onClick={onRetry}
              variant="contained"
            >
              Retry Job
            </Button>
          )}
          {onDismiss && (
            <Button
              size="small"
              color="inherit"
              startIcon={<CloseIcon />}
              onClick={onDismiss}
            >
              Dismiss
            </Button>
          )}
        </CardActions>
      )}
    </Card>
  );
}
