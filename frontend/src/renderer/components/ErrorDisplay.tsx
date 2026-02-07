/**
 * ErrorDisplay component
 * 
 * Displays detailed error information with retry options and field validation errors
 */

import React from 'react';
import {
  Alert,
  AlertTitle,
  Box,
  Button,
  Collapse,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Typography,
} from '@mui/material';
import {
  Error as ErrorIcon,
  ExpandMore as ExpandMoreIcon,
  Refresh as RefreshIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { ParsedError, getErrorTitle } from '../utils/errorHandling';

interface ErrorDisplayProps {
  error: ParsedError | null;
  onRetry?: () => void;
  onDismiss?: () => void;
  compact?: boolean;
}

export default function ErrorDisplay({
  error,
  onRetry,
  onDismiss,
  compact = false,
}: ErrorDisplayProps) {
  const [expanded, setExpanded] = React.useState(false);

  if (!error) {
    return null;
  }

  const hasDetails = !!error.details || (error.fieldErrors && error.fieldErrors.length > 0);
  const showRetry = error.canRetry && onRetry;

  if (compact) {
    return (
      <Alert
        severity="error"
        icon={<ErrorIcon />}
        action={
          <Box display="flex" gap={1}>
            {showRetry && (
              <Button size="small" color="inherit" onClick={onRetry} startIcon={<RefreshIcon />}>
                Retry
              </Button>
            )}
            {onDismiss && (
              <IconButton size="small" color="inherit" onClick={onDismiss}>
                <CloseIcon fontSize="small" />
              </IconButton>
            )}
          </Box>
        }
      >
        {error.message}
      </Alert>
    );
  }

  return (
    <Alert
      severity="error"
      icon={<ErrorIcon />}
      action={
        <Box display="flex" gap={1}>
          {showRetry && (
            <Button size="small" color="inherit" onClick={onRetry} startIcon={<RefreshIcon />}>
              Retry
            </Button>
          )}
          {onDismiss && (
            <IconButton size="small" color="inherit" onClick={onDismiss}>
              <CloseIcon fontSize="small" />
            </IconButton>
          )}
        </Box>
      }
    >
      <AlertTitle>{getErrorTitle(error.code)}</AlertTitle>
      <Typography variant="body2">{error.message}</Typography>

      {hasDetails && (
        <Box mt={1}>
          <Button
            size="small"
            onClick={() => setExpanded(!expanded)}
            endIcon={
              <ExpandMoreIcon
                sx={{
                  transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
                  transition: 'transform 0.3s',
                }}
              />
            }
          >
            {expanded ? 'Hide' : 'Show'} Details
          </Button>

          <Collapse in={expanded}>
            <Box mt={1}>
              {error.details && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  {error.details}
                </Typography>
              )}

              {error.fieldErrors && error.fieldErrors.length > 0 && (
                <Box mt={1}>
                  <Typography variant="subtitle2" gutterBottom>
                    Field Errors:
                  </Typography>
                  <List dense disablePadding>
                    {error.fieldErrors.map((fieldError, index) => (
                      <ListItem key={index} disablePadding sx={{ pl: 2 }}>
                        <ListItemText
                          primary={fieldError.field}
                          secondary={fieldError.message}
                          primaryTypographyProps={{ variant: 'body2', fontWeight: 'medium' }}
                          secondaryTypographyProps={{ variant: 'caption' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {error.statusCode && (
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  Error Code: {error.code} (HTTP {error.statusCode})
                </Typography>
              )}
            </Box>
          </Collapse>
        </Box>
      )}
    </Alert>
  );
}
