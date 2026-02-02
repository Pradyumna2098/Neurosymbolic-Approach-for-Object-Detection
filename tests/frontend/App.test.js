import { render, screen } from '@testing-library/react';
import App from '../App';

test('renders app header', () => {
  render(<App />);
  const headerElement = screen.getByText(/Neurosymbolic Object Detection/i);
  expect(headerElement).toBeInTheDocument();
});

test('renders navigation tabs', () => {
  render(<App />);
  const dashboardTab = screen.getByText('Dashboard');
  const resultsTab = screen.getByText('Results');
  expect(dashboardTab).toBeInTheDocument();
  expect(resultsTab).toBeInTheDocument();
});
