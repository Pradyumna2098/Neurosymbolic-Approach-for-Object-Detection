import { render, screen } from '@testing-library/react';
import Results from '../../frontend/src/components/Results';
import axios from 'axios';

jest.mock('axios');

test('renders results header', () => {
  axios.get.mockResolvedValue({ data: { jobs: [] } });
  render(<Results />);
  const headerElement = screen.getByText(/Training Results/i);
  expect(headerElement).toBeInTheDocument();
});

test('displays empty state when no completed jobs', async () => {
  axios.get.mockResolvedValue({ data: { jobs: [] } });
  render(<Results />);
  
  const emptyState = await screen.findByText(/No completed training jobs yet/i);
  expect(emptyState).toBeInTheDocument();
});
