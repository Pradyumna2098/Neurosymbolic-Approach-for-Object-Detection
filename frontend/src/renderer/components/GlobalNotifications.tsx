/**
 * GlobalNotifications component
 * 
 * Manages toast notifications using notistack and Redux state.
 * Displays error, success, warning, and info messages with retry options.
 */

import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { SnackbarProvider, useSnackbar, SnackbarKey } from 'notistack';
import { IconButton, Button } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import RefreshIcon from '@mui/icons-material/Refresh';
import { RootState } from '../store';
import {
  closeNotification,
  removeNotification,
} from '../store/slices/notificationSlice';

/**
 * Notifier component that consumes notifications from Redux store
 */
function Notifier() {
  const dispatch = useDispatch();
  const notifications = useSelector(
    (state: RootState) => state.notification.notifications
  );
  const { enqueueSnackbar, closeSnackbar } = useSnackbar();
  const displayedRef = React.useRef<SnackbarKey[]>([]);

  useEffect(() => {
    notifications.forEach((notification) => {
      // Don't show if already displayed
      if (displayedRef.current.includes(notification.key)) {
        return;
      }

      // Mark as displayed
      displayedRef.current.push(notification.key);

      // Create action buttons
      const action = (snackbarKey: SnackbarKey) => (
        <>
          {notification.canRetry && notification.retryAction && (
            <Button
              size="small"
              color="inherit"
              startIcon={<RefreshIcon />}
              onClick={() => {
                notification.retryAction?.();
                closeSnackbar(snackbarKey);
                dispatch(closeNotification(notification.key));
              }}
            >
              Retry
            </Button>
          )}
          <IconButton
            size="small"
            aria-label="close"
            color="inherit"
            onClick={() => {
              closeSnackbar(snackbarKey);
              dispatch(closeNotification(notification.key));
            }}
          >
            <CloseIcon fontSize="small" />
          </IconButton>
        </>
      );

      // Enqueue snackbar with notistack
      enqueueSnackbar(notification.message, {
        key: notification.key,
        variant: notification.type,
        action,
        ...notification.options,
        onExited: () => {
          // Remove from store when animation completes
          dispatch(removeNotification(notification.key));
          displayedRef.current = displayedRef.current.filter(
            (key) => key !== notification.key
          );
        },
      });
    });
  }, [notifications, enqueueSnackbar, closeSnackbar, dispatch]);

  return null;
}

/**
 * GlobalNotifications component
 * 
 * Wraps the application with SnackbarProvider and manages notification display
 */
interface GlobalNotificationsProps {
  children: React.ReactNode;
}

export default function GlobalNotifications({ children }: GlobalNotificationsProps) {
  return (
    <SnackbarProvider
      maxSnack={3}
      anchorOrigin={{
        vertical: 'bottom',
        horizontal: 'right',
      }}
      autoHideDuration={5000}
      preventDuplicate
      dense
    >
      <Notifier />
      {children}
    </SnackbarProvider>
  );
}
