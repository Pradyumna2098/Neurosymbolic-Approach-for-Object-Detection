import React from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Typography,
  FormControlLabel,
  Switch,
  Chip,
  SelectChangeEvent,
} from '@mui/material';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { updateFilters, resetFilters } from '../../store/slices/resultsSlice';

/**
 * FilterControls - Controls for filtering detections
 * Features:
 * - Class filter (multi-select)
 * - Confidence threshold slider
 * - Toggle for showing labels
 * - Toggle for showing confidence scores
 */
const FilterControls: React.FC = () => {
  const dispatch = useAppDispatch();
  const filters = useAppSelector((state) => state.results.filters);
  const results = useAppSelector((state) => state.results.results);

  // Extract unique classes from current results
  const availableClasses = React.useMemo(() => {
    const classSet = new Set<string>();
    results.forEach((result) => {
      result.detections.forEach((detection) => {
        classSet.add(`${detection.classId}:${detection.className}`);
      });
    });
    return Array.from(classSet).map((item) => {
      const [id, name] = item.split(':');
      return { id: parseInt(id), name };
    });
  }, [results]);

  const [showLabels, setShowLabels] = React.useState(true);
  const [showConfidence, setShowConfidence] = React.useState(true);

  const handleClassChange = (event: SelectChangeEvent<number[]>) => {
    const value = event.target.value;
    const classIds = typeof value === 'string' ? [] : value;
    dispatch(updateFilters({ classIds }));
  };

  const handleConfidenceChange = (_event: Event, value: number | number[]) => {
    if (typeof value === 'number') {
      dispatch(updateFilters({ minConfidence: value }));
    } else if (Array.isArray(value) && value.length === 2) {
      dispatch(
        updateFilters({
          minConfidence: value[0],
          maxConfidence: value[1],
        })
      );
    }
  };

  const handleResetFilters = () => {
    dispatch(resetFilters());
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: 2,
        p: 2,
        borderBottom: 1,
        borderColor: 'divider',
        alignItems: 'center',
      }}
    >
      {/* Class Filter */}
      <FormControl sx={{ minWidth: 200 }} size="small">
        <InputLabel id="class-filter-label">Filter by Class</InputLabel>
        <Select
          labelId="class-filter-label"
          id="class-filter"
          multiple
          value={filters.classIds}
          onChange={handleClassChange}
          label="Filter by Class"
          renderValue={(selected) => (
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {selected.map((classId) => {
                const cls = availableClasses.find((c) => c.id === classId);
                return (
                  <Chip
                    key={classId}
                    label={cls?.name || `Class ${classId}`}
                    size="small"
                  />
                );
              })}
            </Box>
          )}
        >
          <MenuItem value={-1} disabled>
            <em>Select classes...</em>
          </MenuItem>
          {availableClasses.map((cls) => (
            <MenuItem key={cls.id} value={cls.id}>
              {cls.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {/* Confidence Slider */}
      <Box sx={{ minWidth: 250 }}>
        <Typography variant="body2" gutterBottom>
          Confidence: {filters.minConfidence.toFixed(2)} -{' '}
          {filters.maxConfidence.toFixed(2)}
        </Typography>
        <Slider
          value={[filters.minConfidence, filters.maxConfidence]}
          onChange={handleConfidenceChange}
          valueLabelDisplay="auto"
          min={0}
          max={1}
          step={0.01}
          marks={[
            { value: 0, label: '0' },
            { value: 0.5, label: '0.5' },
            { value: 1, label: '1' },
          ]}
          size="small"
        />
      </Box>

      {/* Show Labels Toggle */}
      <FormControlLabel
        control={
          <Switch
            checked={showLabels}
            onChange={(e) => setShowLabels(e.target.checked)}
            size="small"
          />
        }
        label="Show Labels"
      />

      {/* Show Confidence Toggle */}
      <FormControlLabel
        control={
          <Switch
            checked={showConfidence}
            onChange={(e) => setShowConfidence(e.target.checked)}
            size="small"
          />
        }
        label="Show Confidence"
      />

      {/* Reset Button */}
      {(filters.classIds.length > 0 ||
        filters.minConfidence > 0 ||
        filters.maxConfidence < 1) && (
        <Chip
          label="Reset Filters"
          onClick={handleResetFilters}
          onDelete={handleResetFilters}
          color="primary"
          variant="outlined"
          size="small"
        />
      )}
    </Box>
  );
};

export default FilterControls;
