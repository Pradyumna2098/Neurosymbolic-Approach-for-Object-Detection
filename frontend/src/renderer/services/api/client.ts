/**
 * Axios HTTP client configuration for backend API communication
 * 
 * Configures base URL, timeouts, headers, and interceptors for error handling
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

// Default API base URL - using window object for Electron or fallback
const API_BASE_URL = (window as any).API_BASE_URL || 'http://localhost:8000/api/v1';

// Check if we're in development mode
const isDevelopment = (window as any).isDevelopment || false;

// Create axios instance with default configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout for most requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging and auth
apiClient.interceptors.request.use(
  (config) => {
    // Log API requests in development mode
    if (isDevelopment) {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
        params: config.params,
        data: config.data,
      });
    }

    // Add auth token if available (future enhancement)
    const token = localStorage.getItem('auth_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    // Log API responses in development mode
    if (isDevelopment) {
      console.log(`[API Response] ${response.status} ${response.config.url}`, {
        data: response.data,
      });
    }
    return response;
  },
  (error: AxiosError) => {
    // Enhanced error logging
    if (error.response) {
      // Server responded with error status
      console.error('[API Error]', {
        status: error.response.status,
        statusText: error.response.statusText,
        url: error.config?.url,
        data: error.response.data,
      });

      // Handle specific error codes
      if (error.response.status === 401) {
        // Unauthorized - clear auth token
        localStorage.removeItem('auth_token');
        console.warn('[API] Unauthorized - token cleared');
      } else if (error.response.status === 404) {
        console.warn('[API] Resource not found:', error.config?.url);
      } else if (error.response.status >= 500) {
        console.error('[API] Server error:', error.response.status);
      }
    } else if (error.request) {
      // Request made but no response received
      console.error('[API] No response received:', {
        url: error.config?.url,
        message: error.message,
      });
    } else {
      // Error setting up request
      console.error('[API] Request setup error:', error.message);
    }

    return Promise.reject(error);
  }
);

export default apiClient;