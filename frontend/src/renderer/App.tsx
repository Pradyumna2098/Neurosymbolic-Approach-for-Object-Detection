import React from 'react';
import AppShell from './components/AppShell';
import GlobalNotifications from './components/GlobalNotifications';
import { useJobStatusPolling, useAutoFetchResults } from './store/hooks';

/**
 * Main App component - Entry point for the renderer process
 * Renders the AppShell with four-panel layout and theme support
 * Manages background job polling and auto-fetch results
 */
const App: React.FC = () => {
  // Enable automatic job status polling
  useJobStatusPolling(true, 2000); // Poll every 2 seconds
  
  // Enable automatic results fetching when job completes
  useAutoFetchResults();

  return (
    <GlobalNotifications>
      <AppShell />
    </GlobalNotifications>
  );
};

export default App;
