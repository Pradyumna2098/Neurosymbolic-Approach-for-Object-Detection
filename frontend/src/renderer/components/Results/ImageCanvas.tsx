import React from 'react';
import { Box, IconButton, Typography, ButtonGroup } from '@mui/material';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import ZoomOutIcon from '@mui/icons-material/ZoomOut';
import ZoomOutMapIcon from '@mui/icons-material/ZoomOutMap';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { toggleDetectionSelection } from '../../store/slices/resultsSlice';

interface ImageCanvasProps {
  imageUrl: string;
  viewMode: 'input' | 'labels' | 'output' | 'compare';
  showLabels?: boolean;
  showConfidence?: boolean;
}

/**
 * ImageCanvas - Canvas for displaying images with detection overlays
 * Features:
 * - Image display with zoom and pan
 * - Bounding box overlays
 * - Click to select detection
 * - View mode dependent rendering
 */
const ImageCanvas: React.FC<ImageCanvasProps> = ({
  imageUrl,
  viewMode,
  showLabels = true,
  showConfidence = true,
}) => {
  const dispatch = useAppDispatch();
  const canvasRef = React.useRef<HTMLCanvasElement>(null);
  const containerRef = React.useRef<HTMLDivElement>(null);
  const [zoom, setZoom] = React.useState(1);
  const [pan, setPan] = React.useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = React.useState(false);
  const [dragStart, setDragStart] = React.useState({ x: 0, y: 0 });
  const [hasDragged, setHasDragged] = React.useState(false);

  const results = useAppSelector((state) => state.results.results);
  const currentImageIndex = useAppSelector(
    (state) => state.results.currentImageIndex
  );
  const filters = useAppSelector((state) => state.results.filters);
  const selectedDetectionIds = useAppSelector(
    (state) => state.results.selectedDetectionIds
  );

  // Get current detections
  const currentDetections = React.useMemo(() => {
    if (!results[currentImageIndex]) return [];

    const detections = results[currentImageIndex].detections;

    // Apply filters
    return detections.filter((d) => {
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
  }, [results, currentImageIndex, filters]);

  // Load and draw image
  React.useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx) return;

    const img = new Image();
    img.onload = () => {
      // Set canvas size
      canvas.width = img.width;
      canvas.height = img.height;

      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Apply transform
      ctx.save();
      ctx.translate(pan.x, pan.y);
      ctx.scale(zoom, zoom);

      // Draw image
      ctx.drawImage(img, 0, 0);

      // Draw detections based on view mode
      if (viewMode !== 'input') {
        drawDetections(ctx, currentDetections);
      }

      ctx.restore();
    };

    img.src = imageUrl;
  }, [imageUrl, zoom, pan, viewMode, currentDetections]);

  const drawDetections = (
    ctx: CanvasRenderingContext2D,
    detections: typeof currentDetections
  ) => {
    detections.forEach((detection) => {
      const { bbox, className, confidence, id } = detection;
      const isSelected = selectedDetectionIds.includes(id);

      // Draw bounding box
      ctx.strokeStyle = isSelected ? '#ff0000' : '#00ff00';
      ctx.lineWidth = isSelected ? 3 : 2;
      ctx.strokeRect(bbox.x, bbox.y, bbox.width, bbox.height);

      // Draw label background
      if (showLabels || showConfidence) {
        const label = showLabels
          ? showConfidence
            ? `${className} ${(confidence * 100).toFixed(1)}%`
            : className
          : showConfidence
            ? `${(confidence * 100).toFixed(1)}%`
            : '';

        if (label) {
          ctx.font = '14px Arial';
          const textWidth = ctx.measureText(label).width;
          const padding = 4;

          ctx.fillStyle = isSelected ? '#ff0000' : '#00ff00';
          ctx.fillRect(
            bbox.x,
            bbox.y - 20,
            textWidth + padding * 2,
            20
          );

          ctx.fillStyle = '#000000';
          ctx.fillText(label, bbox.x + padding, bbox.y - 5);
        }
      }
    });
  };

  const handleZoomIn = () => {
    setZoom((z) => Math.min(z + 0.25, 5));
  };

  const handleZoomOut = () => {
    setZoom((z) => Math.max(z - 0.25, 0.25));
  };

  const handleZoomReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    setIsDragging(true);
    setHasDragged(false);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (isDragging) {
      const newPan = {
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      };
      // Track if we've moved more than 5 pixels (drag threshold)
      const dragDistance = Math.sqrt(
        Math.pow(newPan.x - pan.x, 2) + Math.pow(newPan.y - pan.y, 2)
      );
      if (dragDistance > 5) {
        setHasDragged(true);
      }
      setPan(newPan);
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    // Don't select if we just dragged or in input mode
    if (hasDragged || viewMode === 'input') return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left - pan.x) / zoom;
    const y = (e.clientY - rect.top - pan.y) / zoom;

    // Find clicked detection
    const clicked = currentDetections.find((d) => {
      const { bbox } = d;
      return (
        x >= bbox.x &&
        x <= bbox.x + bbox.width &&
        y >= bbox.y &&
        y <= bbox.y + bbox.height
      );
    });

    if (clicked) {
      dispatch(toggleDetectionSelection(clicked.id));
    }
  };

  return (
    <Box ref={containerRef} sx={{ position: 'relative', height: '100%', overflow: 'hidden' }}>
      {/* Zoom Controls */}
      <Box
        sx={{
          position: 'absolute',
          top: 16,
          right: 16,
          zIndex: 10,
          display: 'flex',
          flexDirection: 'column',
          gap: 1,
        }}
      >
        <ButtonGroup orientation="vertical" variant="contained" size="small">
          <IconButton onClick={handleZoomIn} size="small" aria-label="Zoom in">
            <ZoomInIcon />
          </IconButton>
          <IconButton onClick={handleZoomReset} size="small" aria-label="Reset zoom">
            <ZoomOutMapIcon />
          </IconButton>
          <IconButton onClick={handleZoomOut} size="small" aria-label="Zoom out">
            <ZoomOutIcon />
          </IconButton>
        </ButtonGroup>
        <Typography
          variant="caption"
          sx={{
            bgcolor: 'background.paper',
            px: 1,
            py: 0.5,
            borderRadius: 1,
            textAlign: 'center',
          }}
        >
          {(zoom * 100).toFixed(0)}%
        </Typography>
      </Box>

      {/* Canvas */}
      <canvas
        ref={canvasRef}
        onClick={handleCanvasClick}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{
          cursor: isDragging ? 'grabbing' : 'grab',
          maxWidth: '100%',
          maxHeight: '100%',
        }}
      />
    </Box>
  );
};

export default ImageCanvas;
