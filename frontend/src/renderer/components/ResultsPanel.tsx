import React from 'react';
import ResultsViewer from './Results/ResultsViewer';

/**
 * Results Panel - Detection results visualization wrapper
 * Location: Main content area (center-right)
 * Contains full ResultsViewer component with tabs for Input, Labels, Output, Compare views
 */
const ResultsPanel: React.FC = () => {
  return <ResultsViewer />;
};

export default ResultsPanel;
