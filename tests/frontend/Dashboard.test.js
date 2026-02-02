import { render, screen, waitFor } from '@testing-library/react';
import Dashboard from '../../frontend/src/components/Dashboard';
import axios from 'axios';

jest.mock('axios');

test('renders dashboard header', () => {
  axios.get.mockResolvedValue({ data: { jobs: [] } });
  render(<Dashboard />);
  const headerElement = screen.getByText(/Training Dashboard/i);
  expect(headerElement).toBeInTheDocument();
});

test('displays empty state when no jobs', async () => {
  axios.get.mockResolvedValue({ data: { jobs: [] } });
  render(<Dashboard />);
  
  await waitFor(() => {
    const emptyState = screen.getByText(/No jobs yet/i);
    expect(emptyState).toBeInTheDocument();
  });
});
