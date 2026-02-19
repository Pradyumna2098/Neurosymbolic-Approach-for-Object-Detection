import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { OptionsObject, SnackbarKey } from 'notistack';
import { ErrorCode } from '../../utils/errorCodes';

/**
 * Notification types
 */
export type NotificationType = 'success' | 'error' | 'warning' | 'info';

/**
 * Notification item in the queue
 */
export interface Notification {
  key: SnackbarKey;
  message: string;
  type: NotificationType;
  dismissed?: boolean;
  errorCode?: ErrorCode;
  canRetry?: boolean;
  retryAction?: () => void;
  options?: OptionsObject;
}

interface NotificationState {
  notifications: Notification[];
}

const initialState: NotificationState = {
  notifications: [],
};

const notificationSlice = createSlice({
  name: 'notification',
  initialState,
  reducers: {
    /**
     * Enqueue a new notification
     */
    enqueueNotification(state, action: PayloadAction<Omit<Notification, 'key'>>) {
      const key = new Date().getTime() + Math.random();
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (state.notifications as any).push({
        ...action.payload,
        key,
      });
    },

    /**
     * Close a notification (mark as dismissed)
     */
    closeNotification(state, action: PayloadAction<SnackbarKey>) {
      state.notifications = state.notifications.map((notification) =>
        notification.key === action.payload
          ? { ...notification, dismissed: true }
          : notification
      );
    },

    /**
     * Remove a notification from the store
     */
    removeNotification(state, action: PayloadAction<SnackbarKey>) {
      state.notifications = state.notifications.filter(
        (notification) => notification.key !== action.payload
      );
    },

    /**
     * Clear all notifications
     */
    clearNotifications(state) {
      state.notifications = [];
    },

    /**
     * Show success notification
     */
    showSuccess(state, action: PayloadAction<string>) {
      const key = new Date().getTime() + Math.random();
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (state.notifications as any).push({
        key,
        message: action.payload,
        type: 'success',
        options: {
          autoHideDuration: 4000,
        },
      });
    },

    /**
     * Show error notification
     */
    showError(
      state,
      action: PayloadAction<{
        message: string;
        errorCode?: ErrorCode;
        canRetry?: boolean;
        retryAction?: () => void;
      }>
    ) {
      const key = new Date().getTime() + Math.random();
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (state.notifications as any).push({
        key,
        message: action.payload.message,
        type: 'error',
        errorCode: action.payload.errorCode,
        canRetry: action.payload.canRetry,
        retryAction: action.payload.retryAction,
        options: {
          autoHideDuration: action.payload.canRetry ? null : 6000,
          persist: action.payload.canRetry,
        },
      });
    },

    /**
     * Show warning notification
     */
    showWarning(state, action: PayloadAction<string>) {
      const key = new Date().getTime() + Math.random();
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (state.notifications as any).push({
        key,
        message: action.payload,
        type: 'warning',
        options: {
          autoHideDuration: 5000,
        },
      });
    },

    /**
     * Show info notification
     */
    showInfo(state, action: PayloadAction<string>) {
      const key = new Date().getTime() + Math.random();
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (state.notifications as any).push({
        key,
        message: action.payload,
        type: 'info',
        options: {
          autoHideDuration: 4000,
        },
      });
    },
  },
});

export const {
  enqueueNotification,
  closeNotification,
  removeNotification,
  clearNotifications,
  showSuccess,
  showError,
  showWarning,
  showInfo,
} = notificationSlice.actions;

export default notificationSlice.reducer;
