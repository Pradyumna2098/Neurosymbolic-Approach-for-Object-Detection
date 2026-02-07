import React from 'react';
import {
  Box,
  Paper,
  Tabs,
  Tab,
  CircularProgress,
  Typography,
  Alert,
  IconButton,
  Button,
  useTheme,
} from '@mui/material';
import NavigateBeforeIcon from '@mui/icons-material/NavigateBefore';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import { Panel, Group as PanelGroup, Separator as PanelResizeHandle } from 'react-resizable-panels';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import {
  nextImage,
  previousImage,
} from '../../store/slices/resultsSlice';
import FilterControls from './FilterControls';
import ImageCanvas from './ImageCanvas';
import InfoPanel from './InfoPanel';
import DetectionStats from './DetectionStats';
import ExportDialog from './ExportDialog';

type ViewMode = 'input' | 'labels' | 'output' | 'compare';

/**
 * ResultsViewer - Main component for displaying detection results
 * Features:
 * - Tab navigation (Input/Labels/Output/Compare)
 * - Progress indicator during processing
 * - Filter controls
 * - Detection info panel
 * - Statistics footer
 */
const ResultsViewer: React.FC = () => {
  const dispatch = useAppDispatch();
  const theme = useTheme();
  const [viewMode, setViewMode] = React.useState<ViewMode>('input');
  const [exportDialogOpen, setExportDialogOpen] = React.useState(false);

  const results = useAppSelector((state) => state.results.results);
  const currentImageIndex = useAppSelector(
    (state) => state.results.currentImageIndex
  );
  const isLoading = useAppSelector((state) => state.results.isLoading);
  const error = useAppSelector((state) => state.results.error);
  const showLabels = useAppSelector((state) => state.results.filters.showLabels);
  const showConfidence = useAppSelector(
    (state) => state.results.filters.showConfidence
  );

  const currentResult = results[currentImageIndex];

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    const modes: ViewMode[] = ['input', 'labels', 'output', 'compare'];
    setViewMode(modes[newValue]);
  };

  const handlePreviousImage = () => {
    dispatch(previousImage());
  };

  const handleNextImage = () => {
    dispatch(nextImage());
  };

  // Empty state - no results
  if (results.length === 0 && !isLoading && !error) {
    return (
      <Paper
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={0} aria-label="result tabs">
            <Tab label="Input" disabled />
            <Tab label="Labels" disabled />
            <Tab label="Output" disabled />
            <Tab label="Compare" disabled />
          </Tabs>
        </Box>
        <Box
          sx={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            p: 3,
          }}
        >
          <Typography variant="body1" color="text.secondary">
            Upload images and run detection to see results
          </Typography>
        </Box>
      </Paper>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <Paper
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={0} aria-label="result tabs">
            <Tab label="Input" disabled />
            <Tab label="Labels" disabled />
            <Tab label="Output" disabled />
            <Tab label="Compare" disabled />
          </Tabs>
        </Box>
        <Box
          sx={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 2,
            p: 3,
          }}
        >
          <CircularProgress size={60} />
          <Typography variant="body1" color="text.secondary">
            Processing detections...
          </Typography>
        </Box>
      </Paper>
    );
  }

  // Error state
  if (error) {
    return (
      <Paper
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={0} aria-label="result tabs">
            <Tab label="Input" disabled />
            <Tab label="Labels" disabled />
            <Tab label="Output" disabled />
            <Tab label="Compare" disabled />
          </Tabs>
        </Box>
        <Box
          sx={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            p: 3,
          }}
        >
          <Alert severity="error" sx={{ maxWidth: 500 }}>
            <Typography variant="body1" fontWeight="bold" gutterBottom>
              Error processing detections
            </Typography>
            <Typography variant="body2">{error}</Typography>
          </Alert>
        </Box>
      </Paper>
    );
  }

  // Results view
  return (
    <Paper
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Tab Navigation */}
      <Box
        sx={{
          borderBottom: 1,
          borderColor: 'divider',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <Tabs
          value={['input', 'labels', 'output', 'compare'].indexOf(viewMode)}
          onChange={handleTabChange}
          aria-label="result tabs"
        >
          <Tab label="Input" />
          <Tab label="Labels" />
          <Tab label="Output" />
          <Tab label="Compare" />
        </Tabs>

        {/* Image Navigation */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, pr: 2 }}>
          <Button
            variant="outlined"
            size="small"
            startIcon={<FileDownloadIcon />}
            onClick={() => setExportDialogOpen(true)}
            sx={{ mr: 2 }}
          >
            Export
          </Button>
          <IconButton
            size="small"
            onClick={handlePreviousImage}
            disabled={currentImageIndex === 0}
            aria-label="Previous image"
          >
            <NavigateBeforeIcon />
          </IconButton>
          <Typography variant="body2">
            {currentImageIndex + 1} / {results.length}
          </Typography>
          <IconButton
            size="small"
            onClick={handleNextImage}
            disabled={currentImageIndex === results.length - 1}
            aria-label="Next image"
          >
            <NavigateNextIcon />
          </IconButton>
        </Box>
      </Box>

      {/* Filter Controls */}
      {viewMode !== 'input' && <FilterControls />}

      {/* Main Content Area */}
      <Box sx={{ flex: 1, overflow: 'hidden' }}>
        <PanelGroup orientation="horizontal">
          {/* Image Canvas */}
          <Panel defaultSize={75} minSize={50}>
            <Box sx={{ height: '100%', p: 2 }}>
              {currentResult && (
                <ImageCanvas
                  imageUrl={currentResult.imagePath}
                  viewMode={viewMode}
                  showLabels={showLabels}
                  showConfidence={showConfidence}
                />
              )}
            </Box>
          </Panel>

          <PanelResizeHandle
            style={{
              width: '4px',
              background: theme.palette.divider,
              cursor: 'col-resize',
            }}
          />

          {/* Info Panel */}
          {viewMode !== 'input' && (
            <Panel defaultSize={25} minSize={20}>
              <Box sx={{ height: '100%', p: 2 }}>
                <InfoPanel />
              </Box>
            </Panel>
          )}
        </PanelGroup>
      </Box>

      {/* Statistics Footer */}
      {viewMode !== 'input' && <DetectionStats />}

      {/* Export Dialog */}
      <ExportDialog
        open={exportDialogOpen}
        onClose={() => setExportDialogOpen(false)}
        results={results}
        currentResult={currentResult}
      />
    </Paper>
  );
};

export default ResultsViewer;
