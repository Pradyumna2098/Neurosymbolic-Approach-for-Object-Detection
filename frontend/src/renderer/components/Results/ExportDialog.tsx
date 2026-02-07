/**
 * ExportDialog - Dialog component for exporting detection results
 * Supports exporting annotated images and metrics in multiple formats
 */

import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  FormGroup,
  Checkbox,
  Box,
  Typography,
  LinearProgress,
  Alert,
  Divider,
} from '@mui/material';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import { ExportFormat, ExportOptions, DetectionResult, ExportProgress } from '../../types';
import {
  exportToCSV,
  exportToJSON,
  exportMetricsToJSON,
  exportMetricsToCSV,
  triggerDownload,
  batchExportImages,
} from '../../services/ExportService';

interface ExportDialogProps {
  open: boolean;
  onClose: () => void;
  results: DetectionResult[];
  currentResult?: DetectionResult;
}

type ExportType = 'image' | 'metrics';

const ExportDialog: React.FC<ExportDialogProps> = ({
  open,
  onClose,
  results,
  currentResult,
}) => {
  const [exportType, setExportType] = useState<ExportType>('image');
  const [format, setFormat] = useState<ExportFormat>('png');
  const [includeOverlays, setIncludeOverlays] = useState(true);
  const [includeLabels, setIncludeLabels] = useState(true);
  const [includeConfidence, setIncludeConfidence] = useState(true);
  const [exportAll, setExportAll] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [progress, setProgress] = useState<ExportProgress | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleExportTypeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setExportType(event.target.value as ExportType);
    setError(null);
    // Set default format based on export type
    if (event.target.value === 'metrics') {
      setFormat('csv');
    } else {
      setFormat('png');
    }
  };

  const handleFormatChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormat(event.target.value as ExportFormat);
  };

  const handleClose = () => {
    if (!exporting) {
      setError(null);
      setProgress(null);
      onClose();
    }
  };

  const handleExport = async () => {
    setExporting(true);
    setError(null);
    setProgress(null);

    try {
      if (exportType === 'image') {
        await handleImageExport();
      } else {
        await handleMetricsExport();
      }
      
      // Close dialog after successful export
      setTimeout(() => {
        handleClose();
        setExporting(false);
      }, 500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed');
      setExporting(false);
    }
  };

  const handleImageExport = async () => {
    const options: ExportOptions = {
      format: format as 'jpg' | 'png',
      includeOverlays,
      includeLabels,
      includeConfidence,
    };

    const resultsToExport = exportAll ? results : (currentResult ? [currentResult] : []);

    if (resultsToExport.length === 0) {
      throw new Error('No results to export');
    }

    if (resultsToExport.length === 1) {
      // Single image export - use save dialog
      const result = resultsToExport[0];
      const extension = format === 'png' ? 'png' : 'jpg';
      const defaultFileName = result.imageName.replace(/\.[^/.]+$/, '') + `_annotated.${extension}`;
      
      const savePath = await window.electronAPI.saveImage(defaultFileName);
      if (!savePath) {
        throw new Error('Export cancelled');
      }

      // Export single image directly
      const canvas = document.createElement('canvas');
      const { exportImageWithDetections } = await import('../../services/ExportService');
      const blob = await exportImageWithDetections(
        result.imagePath,
        result.detections,
        options,
        canvas
      );
      
      triggerDownload(blob, defaultFileName);
    } else {
      // Batch export with progress
      await batchExportImages(resultsToExport, options, (prog) => {
        setProgress(prog);
      });
    }
  };

  const handleMetricsExport = async () => {
    let content: string;
    let defaultFileName: string;

    if (format === 'csv') {
      content = exportToCSV(results);
      defaultFileName = 'detections.csv';
    } else if (format === 'json') {
      content = exportToJSON(results);
      defaultFileName = 'detections.json';
    } else {
      throw new Error('Invalid format for metrics export');
    }

    // Show save dialog
    const savePath = format === 'csv'
      ? await window.electronAPI.saveCSV(defaultFileName)
      : await window.electronAPI.saveJSON(defaultFileName);

    if (!savePath) {
      throw new Error('Export cancelled');
    }

    // Trigger download
    triggerDownload(content, defaultFileName);
  };

  const getProgressPercentage = (): number => {
    if (!progress) return 0;
    return (progress.current / progress.total) * 100;
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <FileDownloadIcon />
          Export Results
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        {/* Export Type Selection */}
        <FormControl component="fieldset" fullWidth sx={{ mb: 3 }}>
          <FormLabel component="legend">Export Type</FormLabel>
          <RadioGroup
            value={exportType}
            onChange={handleExportTypeChange}
            row
          >
            <FormControlLabel
              value="image"
              control={<Radio />}
              label="Annotated Images"
            />
            <FormControlLabel
              value="metrics"
              control={<Radio />}
              label="Detection Metrics"
            />
          </RadioGroup>
        </FormControl>

        <Divider sx={{ mb: 3 }} />

        {/* Format Selection */}
        <FormControl component="fieldset" fullWidth sx={{ mb: 3 }}>
          <FormLabel component="legend">Format</FormLabel>
          <RadioGroup
            value={format}
            onChange={handleFormatChange}
            row
          >
            {exportType === 'image' ? (
              <>
                <FormControlLabel value="png" control={<Radio />} label="PNG" />
                <FormControlLabel value="jpg" control={<Radio />} label="JPG" />
              </>
            ) : (
              <>
                <FormControlLabel value="csv" control={<Radio />} label="CSV" />
                <FormControlLabel value="json" control={<Radio />} label="JSON" />
              </>
            )}
          </RadioGroup>
        </FormControl>

        {/* Image Export Options */}
        {exportType === 'image' && (
          <>
            <FormControl component="fieldset" fullWidth sx={{ mb: 2 }}>
              <FormLabel component="legend">Display Options</FormLabel>
              <FormGroup>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={includeOverlays}
                      onChange={(e) => setIncludeOverlays(e.target.checked)}
                    />
                  }
                  label="Include bounding boxes"
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={includeLabels}
                      onChange={(e) => setIncludeLabels(e.target.checked)}
                      disabled={!includeOverlays}
                    />
                  }
                  label="Include class labels"
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={includeConfidence}
                      onChange={(e) => setIncludeConfidence(e.target.checked)}
                      disabled={!includeOverlays || !includeLabels}
                    />
                  }
                  label="Include confidence scores"
                />
              </FormGroup>
            </FormControl>

            {results.length > 1 && (
              <FormControl component="fieldset" fullWidth>
                <FormGroup>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={exportAll}
                        onChange={(e) => setExportAll(e.target.checked)}
                      />
                    }
                    label={`Export all images (${results.length} images)`}
                  />
                </FormGroup>
              </FormControl>
            )}
          </>
        )}

        {/* Metrics Export Info */}
        {exportType === 'metrics' && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary">
              {format === 'csv'
                ? 'Export detection data as a CSV file with per-detection statistics.'
                : 'Export detection data as a JSON file with complete detection information.'}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Total images: {results.length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total detections: {results.reduce((sum, r) => sum + r.detections.length, 0)}
            </Typography>
          </Box>
        )}

        {/* Progress Indicator */}
        {exporting && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="body2" gutterBottom>
              {progress?.fileName || 'Exporting...'}
            </Typography>
            <LinearProgress
              variant="determinate"
              value={getProgressPercentage()}
              sx={{ mb: 1 }}
            />
            <Typography variant="caption" color="text.secondary">
              {progress ? `${progress.current} / ${progress.total}` : 'Processing...'}
            </Typography>
          </Box>
        )}

        {/* Error Display */}
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={exporting}>
          Cancel
        </Button>
        <Button
          onClick={handleExport}
          variant="contained"
          startIcon={<FileDownloadIcon />}
          disabled={exporting || results.length === 0}
        >
          Export
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ExportDialog;
