import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Divider,
  Chip,
  Table,
  TableBody,
  TableRow,
  TableCell,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useAppSelector } from '../../store/hooks';
import { Detection } from '../../types';

/**
 * InfoPanel - Display detailed information about selected detection
 * Shows:
 * - Class name and confidence
 * - Bounding box coordinates
 * - Area and aspect ratio
 * - Pipeline stage information
 */
const InfoPanel: React.FC = () => {
  const selectedDetectionIds = useAppSelector(
    (state) => state.results.selectedDetectionIds
  );
  const results = useAppSelector((state) => state.results.results);
  const currentImageIndex = useAppSelector(
    (state) => state.results.currentImageIndex
  );

  // Get the first selected detection
  const selectedDetection = React.useMemo(() => {
    if (
      selectedDetectionIds.length === 0 ||
      !results[currentImageIndex]
    ) {
      return null;
    }

    const currentResult = results[currentImageIndex];
    return currentResult.detections.find((d) =>
      selectedDetectionIds.includes(d.id)
    );
  }, [selectedDetectionIds, results, currentImageIndex]);

  if (!selectedDetection) {
    return (
      <Paper
        sx={{
          height: '100%',
          p: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Typography variant="body2" color="text.secondary">
          Select a detection to view details
        </Typography>
      </Paper>
    );
  }

  const { bbox, className, classId, confidence } = selectedDetection;
  const area = bbox.width * bbox.height;
  const aspectRatio = (bbox.width / bbox.height).toFixed(2);

  return (
    <Paper sx={{ height: '100%', overflow: 'auto' }}>
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Selected Detection
        </Typography>
        <Divider sx={{ mb: 2 }} />

        {/* Class and Confidence */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Class
          </Typography>
          <Chip
            label={`${className} (ID: ${classId})`}
            color="primary"
            size="small"
          />
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Confidence
          </Typography>
          <Typography variant="body1" fontWeight="bold">
            {(confidence * 100).toFixed(1)}%
          </Typography>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Bounding Box Info */}
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Bounding Box
        </Typography>
        <Table size="small">
          <TableBody>
            <TableRow>
              <TableCell>X</TableCell>
              <TableCell align="right">{bbox.x.toFixed(1)}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell>Y</TableCell>
              <TableCell align="right">{bbox.y.toFixed(1)}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell>Width</TableCell>
              <TableCell align="right">{bbox.width.toFixed(1)}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell>Height</TableCell>
              <TableCell align="right">{bbox.height.toFixed(1)}</TableCell>
            </TableRow>
          </TableBody>
        </Table>

        <Divider sx={{ my: 2 }} />

        {/* Computed Properties */}
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Properties
        </Typography>
        <Table size="small">
          <TableBody>
            <TableRow>
              <TableCell>Area</TableCell>
              <TableCell align="right">{area.toFixed(0)} px²</TableCell>
            </TableRow>
            <TableRow>
              <TableCell>Aspect Ratio</TableCell>
              <TableCell align="right">{aspectRatio}</TableCell>
            </TableRow>
          </TableBody>
        </Table>

        <Divider sx={{ my: 2 }} />

        {/* Pipeline Stages */}
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Pipeline Stages
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mt: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CheckCircleIcon color="success" fontSize="small" />
            <Typography variant="body2">YOLO Detection</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CheckCircleIcon color="success" fontSize="small" />
            <Typography variant="body2">NMS Filtering</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CheckCircleIcon color="success" fontSize="small" />
            <Typography variant="body2">Symbolic Reasoning</Typography>
          </Box>
        </Box>
      </Box>
    </Paper>
  );
};

export default InfoPanel;
