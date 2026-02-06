import React from 'react';
import { Box, Paper, Typography, Grid, Chip, Divider } from '@mui/material';
import { useAppSelector } from '../../store/hooks';

/**
 * DetectionStats - Display statistics footer for current results
 * Shows:
 * - Total objects detected
 * - Number of classes
 * - Average confidence
 * - Per-class breakdown
 */
const DetectionStats: React.FC = () => {
  const results = useAppSelector((state) => state.results.results);
  const currentImageIndex = useAppSelector(
    (state) => state.results.currentImageIndex
  );
  const filters = useAppSelector((state) => state.results.filters);

  const stats = React.useMemo(() => {
    if (!results[currentImageIndex]) {
      return {
        totalDetections: 0,
        numClasses: 0,
        avgConfidence: 0,
        classCounts: {} as Record<string, number>,
      };
    }

    const detections = results[currentImageIndex].detections;

    // Apply filters
    const filteredDetections = detections.filter((d) => {
      // Class filter
      if (filters.classIds.length > 0 && !filters.classIds.includes(d.classId)) {
        return false;
      }

      // Confidence filter
      if (
        d.confidence < filters.minConfidence ||
        d.confidence > filters.maxConfidence
      ) {
        return false;
      }

      return true;
    });

    // Calculate stats
    const classCounts: Record<string, number> = {};
    let totalConfidence = 0;

    filteredDetections.forEach((d) => {
      classCounts[d.className] = (classCounts[d.className] || 0) + 1;
      totalConfidence += d.confidence;
    });

    return {
      totalDetections: filteredDetections.length,
      numClasses: Object.keys(classCounts).length,
      avgConfidence:
        filteredDetections.length > 0
          ? totalConfidence / filteredDetections.length
          : 0,
      classCounts,
    };
  }, [results, currentImageIndex, filters]);

  return (
    <Paper
      sx={{
        borderTop: 1,
        borderColor: 'divider',
        p: 2,
      }}
    >
      <Grid container spacing={2} alignItems="center">
        {/* Overall Stats */}
        <Grid item>
          <Typography variant="body2" color="text.secondary">
            Total Objects:
          </Typography>
          <Typography variant="h6" fontWeight="bold">
            {stats.totalDetections}
          </Typography>
        </Grid>

        <Grid item>
          <Divider orientation="vertical" flexItem />
        </Grid>

        <Grid item>
          <Typography variant="body2" color="text.secondary">
            Classes:
          </Typography>
          <Typography variant="h6" fontWeight="bold">
            {stats.numClasses}
          </Typography>
        </Grid>

        <Grid item>
          <Divider orientation="vertical" flexItem />
        </Grid>

        <Grid item>
          <Typography variant="body2" color="text.secondary">
            Avg Confidence:
          </Typography>
          <Typography variant="h6" fontWeight="bold">
            {(stats.avgConfidence * 100).toFixed(1)}%
          </Typography>
        </Grid>

        <Grid item>
          <Divider orientation="vertical" flexItem />
        </Grid>

        {/* Per-Class Breakdown */}
        <Grid item xs>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {Object.entries(stats.classCounts)
              .sort(([, a], [, b]) => b - a)
              .slice(0, 5)
              .map(([className, count]) => (
                <Chip
                  key={className}
                  label={`${className}: ${count}`}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              ))}
            {Object.keys(stats.classCounts).length > 5 && (
              <Chip
                label={`+${Object.keys(stats.classCounts).length - 5} more`}
                size="small"
                variant="outlined"
              />
            )}
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default DetectionStats;
