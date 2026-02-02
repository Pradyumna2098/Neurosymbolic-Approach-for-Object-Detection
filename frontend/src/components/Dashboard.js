import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import './Dashboard.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function Dashboard() {
  const [metrics, setMetrics] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedJob, setSelectedJob] = useState(null);

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedJob) {
      fetchJobDetails(selectedJob);
    }
  }, [selectedJob]);

  const fetchJobs = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/results`);
      setJobs(response.data.jobs);
      setError(null);
    } catch (err) {
      setError('Failed to fetch jobs');
      console.error('Error fetching jobs:', err);
    }
  };

  const fetchJobDetails = async (jobId) => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/results/${jobId}`);
      
      if (response.data.metrics) {
        // Convert metrics to chart data
        const chartData = Object.entries(response.data.metrics)
          .filter(([key]) => typeof response.data.metrics[key] === 'number')
          .map(([key, value], index) => ({
            name: key,
            value: value,
            index: index
          }));
        setMetrics(chartData);
      }
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch job details');
      setLoading(false);
      console.error('Error fetching job details:', err);
    }
  };

  const startTraining = async () => {
    try {
      setLoading(true);
      const response = await axios.post(`${API_BASE_URL}/train`, {
        config_path: '/app/shared/pipeline_local.yaml'
      });
      
      setSelectedJob(response.data.job_id);
      setError(null);
      fetchJobs();
    } catch (err) {
      setError('Failed to start training');
      console.error('Error starting training:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#4caf50';
      case 'running': return '#2196f3';
      case 'failed': return '#f44336';
      case 'queued': return '#ff9800';
      default: return '#9e9e9e';
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Training Dashboard</h2>
        <button onClick={startTraining} disabled={loading} className="btn-primary">
          {loading ? 'Starting...' : 'Start Training'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="dashboard-grid">
        <div className="jobs-panel">
          <h3>Training Jobs</h3>
          {jobs.length === 0 ? (
            <p className="empty-state">No jobs yet. Start training to see results.</p>
          ) : (
            <div className="jobs-list">
              {jobs.map(job => (
                <div
                  key={job.job_id}
                  className={`job-card ${selectedJob === job.job_id ? 'selected' : ''}`}
                  onClick={() => setSelectedJob(job.job_id)}
                >
                  <div className="job-header">
                    <span className="job-id">{job.job_id}</span>
                    <span 
                      className="job-status"
                      style={{ backgroundColor: getStatusColor(job.status) }}
                    >
                      {job.status}
                    </span>
                  </div>
                  <div className="job-time">
                    Created: {new Date(job.created_at).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="metrics-panel">
          <h3>Metrics Visualization</h3>
          {metrics.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={metrics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#667eea" 
                  strokeWidth={2}
                  dot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="empty-state">Select a job to view metrics</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
