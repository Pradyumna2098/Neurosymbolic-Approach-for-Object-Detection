/**
 * ExportService - Handles exporting of detection results and metrics
 * Supports multiple formats: JPG, PNG, CSV, JSON
 */

import { DetectionResult, Detection, ExportOptions, ExportProgress } from '../types';

/**
 * Escapes a string for CSV output by doubling quotes and wrapping in quotes if needed
 */
const escapeCsvField = (value: string | number): string => {
  const str = String(value);
  // If the field contains quotes, commas, or newlines, it needs to be quoted and quotes doubled
  if (str.includes('"') || str.includes(',') || str.includes('\n')) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  // Otherwise, just wrap in quotes for safety
  return `"${str}"`;
};

/**
 * Converts detections data to CSV format
 */
export const exportToCSV = (
  results: DetectionResult[],
  singleFile: boolean = true
): string => {
  const headers = [
    'Image Name',
    'Detection ID',
    'Class ID',
    'Class Name',
    'Confidence',
    'BBox X',
    'BBox Y',
    'BBox Width',
    'BBox Height',
    'Processing Time (ms)',
    'Timestamp',
  ];

  const rows: string[] = [headers.join(',')];

  results.forEach((result) => {
    result.detections.forEach((detection) => {
      const row = [
        escapeCsvField(result.imageName),
        escapeCsvField(detection.id),
        detection.classId,
        escapeCsvField(detection.className),
        detection.confidence.toFixed(4),
        detection.bbox.x.toFixed(2),
        detection.bbox.y.toFixed(2),
        detection.bbox.width.toFixed(2),
        detection.bbox.height.toFixed(2),
        result.metadata.processingTime,
        new Date(result.metadata.timestamp).toISOString(),
      ];
      rows.push(row.join(','));
    });
  });

  return rows.join('\n');
};

/**
 * Converts detections data to JSON format
 */
export const exportToJSON = (results: DetectionResult[]): string => {
  const exportData = results.map((result) => ({
    imageId: result.imageId,
    imageName: result.imageName,
    imagePath: result.imagePath,
    detections: result.detections.map((detection) => ({
      id: detection.id,
      classId: detection.classId,
      className: detection.className,
      confidence: detection.confidence,
      bbox: detection.bbox,
    })),
    metadata: {
      processingTime: result.metadata.processingTime,
      totalDetections: result.metadata.totalDetections,
      timestamp: result.metadata.timestamp,
    },
  }));

  return JSON.stringify(exportData, null, 2);
};

/**
 * Exports aggregated metrics across all detection results
 */
export const exportMetricsToJSON = (results: DetectionResult[]): string => {
  // Use classId as key, store className in the value object
  const classStats = new Map<number, { className: string; count: number; totalConfidence: number }>();
  let totalDetections = 0;
  let totalProcessingTime = 0;

  results.forEach((result) => {
    totalProcessingTime += result.metadata.processingTime;
    totalDetections += result.detections.length;

    result.detections.forEach((detection) => {
      const stats = classStats.get(detection.classId) || { 
        className: detection.className, 
        count: 0, 
        totalConfidence: 0 
      };
      stats.count++;
      stats.totalConfidence += detection.confidence;
      classStats.set(detection.classId, stats);
    });
  });

  const metrics = {
    summary: {
      totalImages: results.length,
      totalDetections,
      averageDetectionsPerImage: results.length > 0 
        ? (totalDetections / results.length).toFixed(2) 
        : '0.00',
      averageProcessingTime: results.length > 0 
        ? (totalProcessingTime / results.length).toFixed(2) 
        : '0.00',
    },
    classCounts: Array.from(classStats.entries()).map(([classId, stats]) => {
      return {
        classId,
        className: stats.className,
        count: stats.count,
        averageConfidence: (stats.totalConfidence / stats.count).toFixed(4),
      };
    }),
    images: results.map((result) => ({
      imageName: result.imageName,
      detectionCount: result.detections.length,
      processingTime: result.metadata.processingTime,
      timestamp: result.metadata.timestamp,
    })),
  };

  return JSON.stringify(metrics, null, 2);
};

/**
 * Exports metrics to CSV format
 */
export const exportMetricsToCSV = (results: DetectionResult[]): string => {
  // Use classId as key, store className in the value object
  const classStats = new Map<number, { className: string; count: number; totalConfidence: number }>();
  let totalDetections = 0;

  results.forEach((result) => {
    totalDetections += result.detections.length;
    result.detections.forEach((detection) => {
      const stats = classStats.get(detection.classId) || { 
        className: detection.className, 
        count: 0, 
        totalConfidence: 0 
      };
      stats.count++;
      stats.totalConfidence += detection.confidence;
      classStats.set(detection.classId, stats);
    });
  });

  const rows: string[] = ['Class ID,Class Name,Count,Average Confidence'];

  Array.from(classStats.entries()).forEach(([classId, stats]) => {
    const avgConfidence = (stats.totalConfidence / stats.count).toFixed(4);
    rows.push(`${classId},${escapeCsvField(stats.className)},${stats.count},${avgConfidence}`);
  });

  return rows.join('\n');
};

/**
 * Renders detections on canvas and exports as image
 */
export const exportImageWithDetections = (
  imageUrl: string,
  detections: Detection[],
  options: ExportOptions,
  canvas: HTMLCanvasElement
): Promise<Blob> => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    
    img.onload = () => {
      try {
        // Set canvas size to match image
        canvas.width = img.width;
        canvas.height = img.height;
        
        const ctx = canvas.getContext('2d');
        if (!ctx) {
          reject(new Error('Failed to get canvas context'));
          return;
        }

        // Draw the base image
        ctx.drawImage(img, 0, 0);

        // Draw detections if overlays are enabled
        if (options.includeOverlays) {
          detections.forEach((detection) => {
            const { x, y, width, height } = detection.bbox;
            
            // Draw bounding box
            ctx.strokeStyle = getColorForClass(detection.classId);
            ctx.lineWidth = 3;
            ctx.strokeRect(x, y, width, height);

            // Draw label background
            if (options.includeLabels) {
              const labelText = options.includeConfidence
                ? `${detection.className} ${(detection.confidence * 100).toFixed(1)}%`
                : detection.className;
              
              ctx.font = '16px Arial';
              const textMetrics = ctx.measureText(labelText);
              const textHeight = 20;
              const padding = 4;
              
              ctx.fillStyle = getColorForClass(detection.classId);
              ctx.fillRect(
                x,
                y - textHeight - padding,
                textMetrics.width + padding * 2,
                textHeight + padding
              );

              // Draw label text
              ctx.fillStyle = '#FFFFFF';
              ctx.fillText(labelText, x + padding, y - padding - 2);
            }
          });
        }

        // Convert canvas to blob
        canvas.toBlob(
          (blob) => {
            if (blob) {
              resolve(blob);
            } else {
              reject(new Error('Failed to create blob from canvas'));
            }
          },
          options.format === 'png' ? 'image/png' : 'image/jpeg',
          0.95
        );
      } catch (error) {
        reject(error);
      }
    };

    img.onerror = () => {
      reject(new Error('Failed to load image'));
    };

    img.src = imageUrl;
  });
};

/**
 * Get color for a given class ID
 */
const getColorForClass = (classId: number): string => {
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
  return colors[classId % colors.length];
};

/**
 * Helper to determine MIME type from file name
 */
const getMimeTypeFromFileName = (fileName: string): string => {
  const extension = fileName.split('.').pop()?.toLowerCase();
  switch (extension) {
    case 'csv':
      return 'text/csv;charset=utf-8';
    case 'json':
      return 'application/json;charset=utf-8';
    case 'png':
      return 'image/png';
    case 'jpg':
    case 'jpeg':
      return 'image/jpeg';
    default:
      return 'text/plain;charset=utf-8';
  }
};

/**
 * Helper to trigger browser download
 */
export const triggerDownload = (content: string | Blob, fileName: string): void => {
  const blob = typeof content === 'string'
    ? new Blob([content], { type: getMimeTypeFromFileName(fileName) })
    : content;

  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Batch export with progress tracking
 */
export const batchExportImages = async (
  results: DetectionResult[],
  options: ExportOptions,
  onProgress?: (progress: ExportProgress) => void
): Promise<void> => {
  const canvas = document.createElement('canvas');
  
  for (let i = 0; i < results.length; i++) {
    const result = results[i];
    
    try {
      if (onProgress) {
        onProgress({
          current: i + 1,
          total: results.length,
          fileName: result.imageName,
          completed: false,
        });
      }

      const blob = await exportImageWithDetections(
        result.imagePath,
        result.detections,
        options,
        canvas
      );

      const extension = options.format === 'png' ? 'png' : 'jpg';
      const fileName = result.imageName.replace(/\.[^/.]+$/, '') + `_annotated.${extension}`;
      
      triggerDownload(blob, fileName);

      // Small delay between downloads to prevent browser blocking
      if (i < results.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    } catch (error) {
      if (onProgress) {
        onProgress({
          current: i + 1,
          total: results.length,
          fileName: result.imageName,
          completed: false,
          error: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    }
  }

  if (onProgress) {
    onProgress({
      current: results.length,
      total: results.length,
      fileName: 'All files',
      completed: true,
    });
  }
};
