/**
 * TypeScript interfaces for backend API request/response schemas
 * Matches the Pydantic models defined in backend/app/models/responses.py
 */

// Upload-related types
export interface UploadedFileInfo {
  filename: string;
  size: number;
  file_id?: string;
  format?: string;
  width?: number;
  height?: number;
}

export interface FileValidationWarning {
  filename: string;
  error: string;
}

export interface UploadResponse {
  status: string;
  job_id: string;
  files: UploadedFileInfo[];
  warnings?: FileValidationWarning[];
}

// Inference configuration types
export interface SAHIConfig {
  enabled: boolean;
  slice_width: number;
  slice_height: number;
  overlap_ratio: number;
}

export interface SymbolicReasoningConfig {
  enabled: boolean;
  rules_file?: string;
}

export interface VisualizationConfig {
  enabled: boolean;
  show_labels: boolean;
  confidence_display: boolean;
}

export interface InferenceConfig {
  model_path: string;
  confidence_threshold: number;
  iou_threshold: number;
  sahi: SAHIConfig;
  symbolic_reasoning: SymbolicReasoningConfig;
  visualization: VisualizationConfig;
}

export interface PredictRequest {
  job_id: string;
  config: InferenceConfig;
}

export interface PredictResponse {
  status: string;
  message: string;
  job_id: string;
  job_status: string;
}

// Job status types
export interface JobProgress {
  stage?: string;
  message?: string;
  percentage?: number;
  total_images?: number;
  processed_images?: number;
}

export interface JobSummary {
  total_detections?: number;
  average_confidence?: number;
  processing_time_seconds?: number;
}

export interface JobError {
  code: string;
  message: string;
  details?: string;
}

export interface JobStatusData {
  job_id: string;
  status: string; // queued, processing, completed, failed
  created_at: string;
  updated_at?: string;
  started_at?: string;
  completed_at?: string;
  failed_at?: string;
  progress?: JobProgress;
  summary?: JobSummary;
  error?: JobError;
  results_url?: string;
  visualization_url?: string;
}

export interface JobStatusResponse {
  status: string;
  data: JobStatusData;
}

// Results types
export interface DetectionBBox {
  format: string;
  center_x?: number;
  center_y?: number;
  width?: number;
  height?: number;
  x_min?: number;
  y_min?: number;
  x_max?: number;
  y_max?: number;
}

export interface Detection {
  class_id: number;
  class_name?: string;
  confidence: number;
  bbox: DetectionBBox;
}

export interface ImageResult {
  file_id: string;
  filename: string;
  detections: Detection[];
  image_width?: number;
  image_height?: number;
}

export interface ClassSummary {
  class_id: number;
  class_name?: string;
  count: number;
  average_confidence: number;
}

export interface JobResultsData {
  job_id: string;
  total_images: number;
  total_detections: number;
  average_confidence: number;
  processing_time_seconds: number;
  images: ImageResult[];
  class_summary: ClassSummary[];
}

export interface JobResultsResponse {
  status: string;
  data: JobResultsData;
}

// Visualization types
export interface VisualizationItem {
  file_id: string;
  filename: string;
  visualization_path: string;
  url: string;
}

export interface VisualizationData {
  job_id: string;
  visualizations: VisualizationItem[];
}

export interface VisualizationResponse {
  status: string;
  data: VisualizationData;
}

// Base64 visualization for embedding in UI
export interface Base64VisualizationData {
  job_id: string;
  visualizations: Array<{
    file_id: string;
    filename: string;
    base64_data: string;
    mime_type: string;
  }>;
}

export interface Base64VisualizationResponse {
  status: string;
  data: Base64VisualizationData;
}

// Error response type
export interface ErrorDetail {
  code: string;
  message: string;
  details?: string;
  field?: string;
  timestamp: string;
}

export interface ErrorResponse {
  status: string;
  error: ErrorDetail;
}
