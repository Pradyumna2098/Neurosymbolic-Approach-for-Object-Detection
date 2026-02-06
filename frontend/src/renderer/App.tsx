import React from 'react';
import { useAppSelector } from './store/hooks';
import './App.css';

const App: React.FC = () => {
  // Demonstrate Redux connection by reading from store
  const uploadedFilesCount = useAppSelector((state) => state.upload.files.length);
  const detectionStatus = useAppSelector((state) => state.detection.status);
  const resultsCount = useAppSelector((state) => state.results.results.length);

  return (
    <div className="app">
      <header className="app-header">
        <h1>Neurosymbolic Object Detection</h1>
        <p>Electron + React + TypeScript + Redux Application</p>
      </header>
      <main className="app-main">
        <div className="welcome-message">
          <h2>Welcome to the Application</h2>
          <p>The Electron desktop application is running successfully.</p>
          <ul>
            <li>✅ Electron is running</li>
            <li>✅ React is rendering</li>
            <li>✅ TypeScript is compiled</li>
            <li>✅ Hot reload is active in development</li>
            <li>✅ Redux store is configured</li>
            <li>✅ Redux DevTools enabled</li>
          </ul>
          <div style={{ marginTop: '20px', padding: '15px', background: '#f0f0f0', borderRadius: '5px' }}>
            <h3>Redux State (Demo)</h3>
            <p>Uploaded Files: {uploadedFilesCount}</p>
            <p>Detection Status: {detectionStatus}</p>
            <p>Results: {resultsCount}</p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;
