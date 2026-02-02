import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import './Results.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function Results() {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [jobDetails, setJobDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchJobs();
  }, []);

  useEffect(() => {
    if (selectedJob) {
      fetchJobDetails(selectedJob);
    }
  }, [selectedJob]);

  const fetchJobs = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/results`);
      setJobs(response.data.jobs.filter(job => job.status === 'completed'));
      setError(null);
    } catch (err) {
      setError('Failed to fetch results');
      console.error('Error fetching results:', err);
    }
  };

  const fetchJobDetails = async (jobId) => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/results/${jobId}`);
      setJobDetails(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch job details');
      setLoading(false);
      console.error('Error fetching job details:', err);
    }
  };

  const renderMetricsChart = () => {
    if (!jobDetails || !jobDetails.metrics) return null;

    const chartData = Object.entries(jobDetails.metrics)
      .filter(([key, value]) => typeof value === 'number' && key !== 'duration_seconds')
      .map(([key, value]) => ({
        metric: key.toUpperCase(),
        value: (value * 100).toFixed(2)
      }));

    return (
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="metric" />
          <YAxis domain={[0, 100]} label={{ value: 'Percentage (%)', angle: -90, position: 'insideLeft' }} />
          <Tooltip formatter={(value) => `${value}%`} />
          <Legend />
          <Bar dataKey="value" fill="#667eea" />
        </BarChart>
      </ResponsiveContainer>
    );
  };

  return (
    <div className="results">
      <h2>Training Results</h2>

      {error && <div className="error-message">{error}</div>}

      {jobs.length === 0 ? (
        <div className="empty-state-container">
          <p className="empty-state">No completed training jobs yet.</p>
        </div>
      ) : (
        <div className="results-grid">
          <div className="results-sidebar">
            <h3>Completed Jobs</h3>
            <div className="results-list">
              {jobs.map(job => (
                <div
                  key={job.job_id}
                  className={`result-card ${selectedJob === job.job_id ? 'selected' : ''}`}
                  onClick={() => setSelectedJob(job.job_id)}
                >
                  <div className="result-id">{job.job_id}</div>
                  <div className="result-time">
                    {new Date(job.created_at).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="results-content">
            {loading ? (
              <div className="loading">Loading...</div>
            ) : jobDetails ? (
              <>
                <div className="results-header">
                  <h3>Job: {selectedJob}</h3>
                  <span className="status-badge completed">Completed</span>
                </div>

                {jobDetails.metrics && (
                  <div className="metrics-section">
                    <h4>Performance Metrics</h4>
                    <div className="metrics-grid">
                      {Object.entries(jobDetails.metrics)
                        .filter(([key, value]) => typeof value === 'number')
                        .map(([key, value]) => (
                          <div key={key} className="metric-card">
                            <div className="metric-label">{key.replace(/_/g, ' ').toUpperCase()}</div>
                            <div className="metric-value">
                              {key === 'duration_seconds' 
                                ? `${value.toFixed(2)}s` 
                                : `${(value * 100).toFixed(2)}%`
                              }
                            </div>
                          </div>
                        ))}
                    </div>
                    
                    <div className="chart-container">
                      {renderMetricsChart()}
                    </div>
                  </div>
                )}

                {jobDetails.logs && jobDetails.logs.length > 0 && (
                  <div className="logs-section">
                    <h4>Training Logs</h4>
                    <div className="logs-container">
                      {jobDetails.logs.map((log, index) => (
                        <div key={index} className="log-entry">
                          <span className="log-index">{index + 1}</span>
                          <span className="log-message">{log}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {jobDetails.error && (
                  <div className="error-section">
                    <h4>Error Details</h4>
                    <pre className="error-text">{jobDetails.error}</pre>
                  </div>
                )}
              </>
            ) : (
              <p className="empty-state">Select a job to view results</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default Results;
