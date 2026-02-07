import React from 'react';
import { Group, Rect, Text } from 'react-konva';
import { Detection } from '../../types';

interface BoundingBoxProps {
  detection: Detection;
  isSelected: boolean;
  isHovered: boolean;
  showLabels: boolean;
  showConfidence: boolean;
  onClick: () => void;
  onMouseEnter: () => void;
  onMouseLeave: () => void;
}

/**
 * BoundingBox - Konva component for rendering a detection bounding box
 * Features:
 * - Colored rectangle with stroke
 * - Label background and text
 * - Hover and selection states
 * - Click handling
 */
const BoundingBox: React.FC<BoundingBoxProps> = ({
  detection,
  isSelected,
  isHovered,
  showLabels,
  showConfidence,
  onClick,
  onMouseEnter,
  onMouseLeave,
}) => {
  const { bbox, className, confidence, classId } = detection;

  // Color scheme based on class (can be enhanced with a proper color palette)
  const getColorForClass = (id: number): string => {
    const colors = [
      '#FF6B6B', // Red
      '#4ECDC4', // Teal
      '#45B7D1', // Blue
      '#FFA07A', // Light Salmon
      '#98D8C8', // Mint
      '#F7DC6F', // Yellow
      '#BB8FCE', // Purple
      '#85C1E2', // Sky Blue
      '#F8B739', // Orange
      '#52B788', // Green
    ];
    return colors[id % colors.length];
  };

  const color = getColorForClass(classId);
  const strokeWidth = isSelected ? 4 : isHovered ? 3 : 2;
  const strokeColor = isSelected ? '#FF0000' : isHovered ? '#FFFF00' : color;

  // Build label text
  const labelText = React.useMemo(() => {
    if (!showLabels && !showConfidence) return '';
    
    const parts: string[] = [];
    if (showLabels) parts.push(className);
    if (showConfidence) parts.push(`${(confidence * 100).toFixed(1)}%`);
    
    return parts.join(' ');
  }, [showLabels, showConfidence, className, confidence]);

  const padding = 4;
  const fontSize = 14;
  const labelHeight = 20;

  return (
    <Group>
      {/* Bounding Box Rectangle */}
      <Rect
        x={bbox.x}
        y={bbox.y}
        width={bbox.width}
        height={bbox.height}
        stroke={strokeColor}
        strokeWidth={strokeWidth}
        fill="transparent"
        onClick={onClick}
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
        onTap={onClick}
        hitStrokeWidth={10} // Larger hit area for easier interaction
      />

      {/* Label Background and Text */}
      {labelText && (
        <>
          <Rect
            x={bbox.x}
            y={bbox.y - labelHeight}
            width={labelText.length * 7 + padding * 2} // Approximate width
            height={labelHeight}
            fill={strokeColor}
            opacity={0.8}
          />
          <Text
            x={bbox.x + padding}
            y={bbox.y - labelHeight + 3}
            text={labelText}
            fontSize={fontSize}
            fontFamily="Arial"
            fill="#FFFFFF"
            fontStyle="bold"
          />
        </>
      )}
    </Group>
  );
};

export default BoundingBox;
