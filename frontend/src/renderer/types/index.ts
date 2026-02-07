/**
 * Shared TypeScript interfaces and types for Redux state management
 */

// Upload-related types
export interface UploadedFile {
  id: string;
  name: string;
  size: number;
  path: string;
  preview?: string; // Base64 thumbnail
  uploadedAt: Date;
}

// Detection configuration types
export interface DetectionConfig {
  // Model configuration
  modelPath: string;
  
  // YOLO parameters
  confidence: number; // 0.01 - 1.0
  iouThreshold: number; // 0.01 - 1.0
  
  // SAHI parameters
  sliceHeight: number;
  sliceWidth: number;
  overlapHeight: number; // 0.0 - 0.5
  overlapWidth: number; // 0.0 - 0.5
  
  // Advanced options
  device: 'cuda' | 'cpu';
  batchSize?: number;
  enableProlog: boolean;
  prologRulesPath?: string;
  enableNMS: boolean;
}

// Detection results types
export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Detection {
  id: string;
  classId: number;
  className: string;
  confidence: number;
  bbox: BoundingBox;
  imageId: string;
}

export interface DetectionResult {
  imageId: string;
  imageName: string;
  imagePath: string;
  detections: Detection[];
  metadata: {
    processingTime: number;
    totalDetections: number;
    timestamp: Date;
  };
}

// Job status types
export type JobStatus = 'idle' | 'uploading' | 'pending' | 'running' | 'complete' | 'error';

export interface JobProgress {
  stage: string;
  progress: number; // 0-100
  message: string;
}

// Export-related types
export type ExportFormat = 'jpg' | 'png' | 'csv' | 'json';

export interface ExportOptions {
  format: ExportFormat;
  includeOverlays?: boolean; // For image exports
  includeLabels?: boolean; // For image exports
  includeConfidence?: boolean; // For image exports
  singleFile?: boolean; // For batch exports (aggregate vs individual)
}

export interface ExportProgress {
  current: number;
  total: number;
  fileName: string;
  completed: boolean;
  error?: string;
}
