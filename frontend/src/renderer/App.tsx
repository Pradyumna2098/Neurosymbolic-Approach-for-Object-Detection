import React from 'react';
import './App.css';

const App: React.FC = () => {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Neurosymbolic Object Detection</h1>
        <p>Electron + React + TypeScript Application</p>
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
          </ul>
        </div>
      </main>
    </div>
  );
};

export default App;
