import React from 'react';
import { Box, IconButton, Typography, ButtonGroup } from '@mui/material';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import ZoomOutIcon from '@mui/icons-material/ZoomOut';
import ZoomOutMapIcon from '@mui/icons-material/ZoomOutMap';
import { Stage, Layer, Image as KonvaImage } from 'react-konva';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { toggleDetectionSelection } from '../../store/slices/resultsSlice';
import BoundingBox from './BoundingBox';
import useImage from 'use-image';

interface ImageCanvasProps {
  imageUrl: string;
  viewMode: 'input' | 'labels' | 'output' | 'compare';
  showLabels?: boolean;
  showConfidence?: boolean;
}

/**
 * ImageCanvas - Konva-based canvas for displaying images with detection overlays
 * Features:
 * - Image display with zoom and pan
 * - Interactive bounding box overlays with hover/click
 * - Mouse wheel zoom
 * - Click and drag to pan
 * - View mode dependent rendering
 */
const ImageCanvas: React.FC<ImageCanvasProps> = ({
  imageUrl,
  viewMode,
  showLabels = true,
  showConfidence = true,
}) => {
  const dispatch = useAppDispatch();
  const containerRef = React.useRef<HTMLDivElement>(null);
  const stageRef = React.useRef<any>(null); // eslint-disable-line @typescript-eslint/no-explicit-any
  const [zoom, setZoom] = React.useState(1);
  const [position, setPosition] = React.useState({ x: 0, y: 0 });
  const [hoveredDetectionId, setHoveredDetectionId] = React.useState<string | null>(null);
  const [stageDimensions, setStageDimensions] = React.useState({ width: 800, height: 600 });

  const results = useAppSelector((state) => state.results.results);
  const currentImageIndex = useAppSelector(
    (state) => state.results.currentImageIndex
  );
  const filters = useAppSelector((state) => state.results.filters);
  const selectedDetectionIds = useAppSelector(
    (state) => state.results.selectedDetectionIds
  );

  // Load image using use-image hook
  const [image] = useImage(imageUrl, 'anonymous');

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

  // Update stage dimensions on container resize
  React.useEffect(() => {
    const updateSize = () => {
      if (containerRef.current) {
        setStageDimensions({
          width: containerRef.current.offsetWidth,
          height: containerRef.current.offsetHeight,
        });
      }
    };

    updateSize();
    
    // Use ResizeObserver to detect container size changes (not just window resize)
    const resizeObserver = new ResizeObserver(updateSize);
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }

    return () => {
      resizeObserver.disconnect();
    };
  }, []);

  // Center image when it loads
  React.useEffect(() => {
    if (image && containerRef.current) {
      const scale = Math.min(
        stageDimensions.width / image.width,
        stageDimensions.height / image.height,
        1
      );
      setZoom(scale);
      setPosition({
        x: (stageDimensions.width - image.width * scale) / 2,
        y: (stageDimensions.height - image.height * scale) / 2,
      });
    }
  }, [image, stageDimensions]);

  const handleZoomIn = () => {
    setZoom((z) => Math.min(z * 1.25, 5));
  };

  const handleZoomOut = () => {
    setZoom((z) => Math.max(z / 1.25, 0.1));
  };

  const handleZoomReset = () => {
    if (image) {
      const scale = Math.min(
        stageDimensions.width / image.width,
        stageDimensions.height / image.height,
        1
      );
      setZoom(scale);
      setPosition({
        x: (stageDimensions.width - image.width * scale) / 2,
        y: (stageDimensions.height - image.height * scale) / 2,
      });
    }
  };

  const handleWheel = (e: any) => { // eslint-disable-line @typescript-eslint/no-explicit-any
    e.evt.preventDefault();

    const scaleBy = 1.1;
    const stage = stageRef.current;
    if (!stage) return;

    const oldScale = stage.scaleX();
    const pointer = stage.getPointerPosition();
    
    // getPointerPosition() can return null
    if (!pointer) return;

    const mousePointTo = {
      x: (pointer.x - stage.x()) / oldScale,
      y: (pointer.y - stage.y()) / oldScale,
    };

    const newScale = e.evt.deltaY > 0 
      ? Math.max(oldScale / scaleBy, 0.1) 
      : Math.min(oldScale * scaleBy, 5);

    setZoom(newScale);

    const newPos = {
      x: pointer.x - mousePointTo.x * newScale,
      y: pointer.y - mousePointTo.y * newScale,
    };
    setPosition(newPos);
  };

  const handleDetectionClick = (detectionId: string) => {
    if (viewMode !== 'input') {
      dispatch(toggleDetectionSelection(detectionId));
    }
  };

  const handleDetectionMouseEnter = (detectionId: string) => {
    setHoveredDetectionId(detectionId);
  };

  const handleDetectionMouseLeave = () => {
    setHoveredDetectionId(null);
  };

  return (
    <Box ref={containerRef} sx={{ position: 'relative', height: '100%', overflow: 'hidden', bgcolor: '#f0f0f0' }}>
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

      {/* Konva Stage */}
      <Stage
        ref={stageRef}
        width={stageDimensions.width}
        height={stageDimensions.height}
        scaleX={zoom}
        scaleY={zoom}
        x={position.x}
        y={position.y}
        draggable
        onWheel={handleWheel}
        onDragMove={(e) => {
          // Update position during drag to prevent snap-back on re-render
          setPosition({
            x: e.target.x(),
            y: e.target.y(),
          });
        }}
      >
        <Layer>
          {/* Image */}
          {image && (
            <KonvaImage
              image={image}
              width={image.width}
              height={image.height}
            />
          )}

          {/* Bounding Boxes (only if not in input mode) */}
          {viewMode !== 'input' &&
            currentDetections.map((detection) => (
              <BoundingBox
                key={detection.id}
                detection={detection}
                isSelected={selectedDetectionIds.includes(detection.id)}
                isHovered={hoveredDetectionId === detection.id}
                showLabels={showLabels}
                showConfidence={showConfidence}
                onClick={() => handleDetectionClick(detection.id)}
                onMouseEnter={() => handleDetectionMouseEnter(detection.id)}
                onMouseLeave={handleDetectionMouseLeave}
              />
            ))}
        </Layer>
      </Stage>
    </Box>
  );
};

export default ImageCanvas;
