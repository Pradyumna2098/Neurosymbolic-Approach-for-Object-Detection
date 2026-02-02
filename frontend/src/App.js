import React, { useState } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import Results from './components/Results';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="App">
      <header className="App-header">
        <h1>Neurosymbolic Object Detection</h1>
        <p>Real-time monitoring and results visualization</p>
      </header>
      
      <nav className="nav-tabs">
        <button 
          className={activeTab === 'dashboard' ? 'active' : ''}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
        <button 
          className={activeTab === 'results' ? 'active' : ''}
          onClick={() => setActiveTab('results')}
        >
          Results
        </button>
      </nav>

      <main className="App-main">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'results' && <Results />}
      </main>
    </div>
  );
}

export default App;
