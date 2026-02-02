# Backend API Architecture for Prediction Automation

**Version:** 1.0  
**Date:** February 2, 2026  
**Status:** Design Specification  

## Table of Contents
1. [Overview](#overview)
2. [API Design Justification](#api-design-justification)
3. [Technology Stack](#technology-stack)
4. [System Architecture](#system-architecture)
5. [API Endpoints Specification](#api-endpoints-specification)
6. [Workflow Documentation](#workflow-documentation)
7. [Prometheus Integration](#prometheus-integration)
8. [Error Handling Strategy](#error-handling-strategy)
9. [Security Considerations](#security-considerations)
10. [Performance and Scalability](#performance-and-scalability)
11. [Future Enhancements](#future-enhancements)

---

## Overview

### Purpose
This document specifies the backend API architecture for automating the neurosymbolic object detection pipeline. The API provides a programmatic interface for the Windows desktop application to upload images, trigger inference, retrieve prediction results, and monitor system performance.

### Key Objectives
- **Asynchronous Processing**: Handle long-running inference tasks without blocking
- **File Management**: Efficient upload, storage, and retrieval of images and results
- **Real-time Monitoring**: Expose performance metrics via Prometheus
- **Scalability**: Support concurrent inference requests and batch processing
- **Reliability**: Robust error handling and status tracking
- **Extensibility**: Modular design for future feature additions

### Scope
This specification covers:
- API endpoint definitions and contracts
- Request/response formats and validation
- Workflow orchestration between components
- Integration points for monitoring
- Error handling and recovery strategies

**Out of Scope:**
- Implementation code (deferred to development phase)
- Database schema details (separate document)
- Frontend integration specifics (covered in frontend docs)

---

## API Design Justification

### REST vs gRPC Analysis

| Criterion | REST | gRPC | Decision |
|-----------|------|------|----------|
| **Client Compatibility** | Universal (HTTP/JSON) | Requires client generation | ✅ REST |
| **Ease of Development** | Simple, well-known | More complex setup | ✅ REST |
| **Browser Support** | Native | Limited (requires gRPC-web) | ✅ REST |
| **Performance** | Good for most use cases | Better for high-throughput | REST (sufficient) |
| **File Upload** | Multipart form data | Streaming | REST (simpler) |
| **Documentation** | OpenAPI/Swagger | Protocol buffers | ✅ REST |
| **Debugging** | cURL, Postman, browser | Specialized tools | ✅ REST |
| **Streaming** | SSE/WebSockets | Bi-directional native | REST (SSE adequate) |

### Selected Approach: RESTful API

**Rationale:**
1. **Universal Client Support**: The Windows desktop application (Electron-based) can easily consume REST APIs using standard HTTP clients (fetch, axios)
2. **Simplicity**: REST's stateless, resource-oriented design aligns well with our use case (upload images, run inference, retrieve results)
3. **Tooling Ecosystem**: Rich ecosystem of documentation (Swagger/OpenAPI), testing (Postman), and monitoring tools
4. **File Handling**: Multipart form data is mature and well-supported for image uploads
5. **Prometheus Integration**: REST endpoints can easily expose `/metrics` endpoint in Prometheus text format
6. **Development Velocity**: Team familiarity with REST reduces development and debugging time

**When gRPC Would Be Better:**
- High-frequency, low-latency microservice communication (not our primary use case)
- Bi-directional streaming requirements (our inference is request-response)
- Polyglot service mesh with strong type contracts (single backend for now)

**Alternative Protocols Considered:**
- **GraphQL**: Overly complex for our needs; REST resources map cleanly to our domain
- **WebSockets**: Useful for real-time updates but REST + Server-Sent Events (SSE) suffice for job status polling

---

## Technology Stack

### Backend Framework: **FastAPI**

**Justification:**
- **Performance**: ASGI-based, async support for handling concurrent requests
- **Type Safety**: Built-in Pydantic validation reduces bugs
- **Documentation**: Auto-generates OpenAPI/Swagger docs
- **Modern Python**: Native async/await, type hints, Python 3.10+ features
- **Ecosystem**: Rich plugin ecosystem (CORS, authentication, rate limiting)

**Alternative Considered:**
- **Flask**: Mature but lacks native async support and automatic API docs
- **Django REST Framework**: Too heavyweight for our API-focused use case

### Task Queue: **Celery + Redis**

**Why:**
- **Asynchronous Processing**: Offload long-running inference tasks from request handlers
- **Reliability**: Task retries, failure handling, result persistence
- **Scalability**: Horizontal scaling with multiple workers
- **Monitoring**: Built-in Flower dashboard + Prometheus integration

**Flow:**
1. API receives inference request
2. Creates Celery task and returns job ID immediately
3. Celery worker picks up task and runs YOLO/SAHI inference
4. Client polls status endpoint with job ID
5. Upon completion, client retrieves results via result endpoints

### Storage Layer

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Metadata** | PostgreSQL | Job status, user info, model metadata |
| **File Storage** | Local Filesystem / MinIO (S3-compatible) | Images, predictions, labels, visualizations |
| **Cache** | Redis | Job status cache, rate limiting |

**File Storage Decision:**
- **Phase 1 (MVP)**: Local filesystem for simplicity
- **Phase 2 (Production)**: MinIO (S3-compatible) for scalability and redundancy

### Monitoring Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Metrics** | Prometheus | Time-series metrics collection |
| **Visualization** | Grafana | Dashboards and alerting |
| **Logging** | Structured logging (JSON) | Application and error logs |
| **Tracing** | OpenTelemetry (future) | Distributed tracing |

### Additional Components

- **API Documentation**: Swagger UI (auto-generated by FastAPI)
- **Authentication**: JWT tokens (future phase)
- **Rate Limiting**: slowapi (FastAPI rate limiter)
- **CORS**: FastAPI CORS middleware
- **Validation**: Pydantic models

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Windows Desktop App                       │
│                      (Electron + React)                          │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ HTTP/JSON (REST API)
                 │
┌────────────────▼────────────────────────────────────────────────┐
│                        Backend API Server                        │
│                         (FastAPI)                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Endpoints                                            │  │
│  │  ├─ /api/v1/inference/upload                             │  │
│  │  ├─ /api/v1/inference/predict                            │  │
│  │  ├─ /api/v1/jobs/{job_id}/status                         │  │
│  │  ├─ /api/v1/jobs/{job_id}/results                        │  │
│  │  ├─ /api/v1/jobs/{job_id}/visualization                  │  │
│  │  └─ /metrics (Prometheus)                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────┐         ┌─────────────────────────────┐  │
│  │  Request Handler │────────▶│  Celery Task Queue          │  │
│  │  (Validation)    │         │  (Redis Broker)             │  │
│  └──────────────────┘         └─────────────────────────────┘  │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│                     Celery Workers                               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Inference Pipeline                                       │  │
│  │  ├─ Load YOLO Model                                      │  │
│  │  ├─ Run SAHI Sliced Prediction                           │  │
│  │  ├─ Apply NMS (Preprocessing)                            │  │
│  │  ├─ Symbolic Reasoning (Prolog)                          │  │
│  │  └─ Generate Visualizations                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│                     Storage Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐ │
│  │ PostgreSQL   │  │ File Storage │  │ Redis Cache           │ │
│  │ (Metadata)   │  │ (Images/     │  │ (Job Status)          │ │
│  │              │  │  Results)    │  │                       │ │
│  └──────────────┘  └──────────────┘  └───────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     Monitoring Stack                             │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐ │
│  │ Prometheus   │  │ Grafana      │  │ Log Aggregator        │ │
│  │ (Metrics)    │◀─│ (Dashboard)  │  │ (Future)              │ │
│  └──────────────┘  └──────────────┘  └───────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

#### 1. API Server (FastAPI)
- **Request Validation**: Validate file formats, parameters, job IDs
- **Authentication**: Verify JWT tokens (future phase)
- **Rate Limiting**: Prevent API abuse
- **Job Submission**: Create Celery tasks and return job IDs
- **Result Retrieval**: Serve completed predictions and visualizations
- **Metrics Exposure**: Expose `/metrics` endpoint for Prometheus

#### 2. Celery Workers
- **Model Loading**: Load YOLO models from disk/cache
- **Inference Execution**: Run SAHI sliced prediction pipeline
- **Symbolic Processing**: Apply NMS and Prolog reasoning
- **Visualization**: Generate annotated images with bounding boxes
- **Result Storage**: Save predictions, labels, and images
- **Status Updates**: Update job status in Redis/PostgreSQL

#### 3. Storage Layer
- **PostgreSQL**: Store job metadata, user info, model registry
- **File Storage**: Store uploaded images and generated results
- **Redis**: Cache job status for fast polling

#### 4. Monitoring
- **Prometheus**: Scrape `/metrics` endpoint for API and pipeline metrics
- **Grafana**: Visualize dashboards for system health and performance

---

## API Endpoints Specification

### Base URL
```
http://localhost:8000/api/v1
```

### API Versioning Strategy
- Use URL path versioning (`/api/v1`, `/api/v2`)
- Maintain backward compatibility within major versions
- Deprecation notices in response headers

---

### Endpoint 1: Upload Image(s)

**Purpose**: Upload one or more images for inference

```http
POST /api/v1/inference/upload
Content-Type: multipart/form-data
```

**Request Body (multipart/form-data):**
```
files: [file, file, ...] (required) - Image files (JPEG, PNG, TIFF)
```

**Example Request (cURL):**
```bash
curl -X POST http://localhost:8000/api/v1/inference/upload \
  -F "files=@image1.jpg" \
  -F "files=@image2.png"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "2 images uploaded successfully",
  "data": {
    "upload_id": "upl_a1b2c3d4e5f6",
    "uploaded_files": [
      {
        "filename": "image1.jpg",
        "file_id": "img_x1y2z3",
        "size_bytes": 2048576,
        "format": "JPEG",
        "dimensions": [1920, 1080]
      },
      {
        "filename": "image2.png",
        "file_id": "img_a2b3c4",
        "size_bytes": 3145728,
        "format": "PNG",
        "dimensions": [2048, 1536]
      }
    ]
  }
}
```

**Response (400 Bad Request):**
```json
{
  "status": "error",
  "message": "Invalid file format",
  "errors": [
    {
      "filename": "document.pdf",
      "error": "Unsupported file format. Allowed: JPEG, PNG, TIFF"
    }
  ]
}
```

**Validation Rules:**
- **File Size**: Maximum 50 MB per file
- **File Formats**: JPEG, PNG, TIFF
- **Batch Limit**: Maximum 100 files per upload
- **Dimensions**: Minimum 64x64, maximum 8192x8192

**Storage:**
- Files stored in `storage/uploads/{upload_id}/{file_id}.{ext}`
- Metadata saved to PostgreSQL `uploaded_files` table

---

### Endpoint 2: Trigger Inference

**Purpose**: Start inference job for uploaded images

```http
POST /api/v1/inference/predict
Content-Type: application/json
```

**Request Body (JSON):**
```json
{
  "upload_id": "upl_a1b2c3d4e5f6",
  "file_ids": ["img_x1y2z3", "img_a2b3c4"],
  "config": {
    "model_path": "/path/to/best.pt",
    "confidence_threshold": 0.25,
    "iou_threshold": 0.45,
    "sahi": {
      "enabled": true,
      "slice_width": 640,
      "slice_height": 640,
      "overlap_ratio": 0.2
    },
    "symbolic_reasoning": {
      "enabled": true,
      "rules_file": "/path/to/rules.pl"
    },
    "visualization": {
      "enabled": true,
      "show_labels": true,
      "confidence_display": true
    }
  }
}
```

**Example Request (cURL):**
```bash
curl -X POST http://localhost:8000/api/v1/inference/predict \
  -H "Content-Type: application/json" \
  -d '{
    "upload_id": "upl_a1b2c3d4e5f6",
    "file_ids": ["img_x1y2z3"],
    "config": {
      "confidence_threshold": 0.25,
      "sahi": {"enabled": true}
    }
  }'
```

**Response (202 Accepted):**
```json
{
  "status": "accepted",
  "message": "Inference job created",
  "data": {
    "job_id": "job_abc123xyz789",
    "status": "queued",
    "created_at": "2026-02-02T18:54:57.324Z",
    "estimated_completion": "2026-02-02T18:56:30.000Z",
    "file_count": 2,
    "status_url": "/api/v1/jobs/job_abc123xyz789/status"
  }
}
```

**Response (400 Bad Request):**
```json
{
  "status": "error",
  "message": "Invalid configuration",
  "errors": [
    {
      "field": "config.confidence_threshold",
      "error": "Must be between 0.0 and 1.0"
    }
  ]
}
```

**Validation Rules:**
- `upload_id` must exist and belong to the user
- `file_ids` must be from the specified upload
- `confidence_threshold`: 0.0 to 1.0
- `iou_threshold`: 0.0 to 1.0
- `slice_width`, `slice_height`: 256 to 2048
- `overlap_ratio`: 0.0 to 0.5

**Processing:**
1. Validate request and create job record in PostgreSQL
2. Create Celery task with job_id and configuration
3. Return job_id immediately (202 Accepted)
4. Celery worker processes task asynchronously

---

### Endpoint 3: Check Job Status

**Purpose**: Poll inference job status

```http
GET /api/v1/jobs/{job_id}/status
```

**Path Parameters:**
- `job_id` (string, required) - Job identifier from predict endpoint

**Example Request:**
```bash
curl http://localhost:8000/api/v1/jobs/job_abc123xyz789/status
```

**Response (200 OK) - Queued:**
```json
{
  "status": "success",
  "data": {
    "job_id": "job_abc123xyz789",
    "status": "queued",
    "created_at": "2026-02-02T18:54:57.324Z",
    "updated_at": "2026-02-02T18:54:57.324Z",
    "progress": {
      "total_images": 2,
      "processed_images": 0,
      "percentage": 0
    }
  }
}
```

**Response (200 OK) - Processing:**
```json
{
  "status": "success",
  "data": {
    "job_id": "job_abc123xyz789",
    "status": "processing",
    "created_at": "2026-02-02T18:54:57.324Z",
    "updated_at": "2026-02-02T18:55:30.124Z",
    "started_at": "2026-02-02T18:55:00.000Z",
    "progress": {
      "total_images": 2,
      "processed_images": 1,
      "percentage": 50,
      "current_stage": "Running SAHI inference",
      "estimated_completion": "2026-02-02T18:56:30.000Z"
    }
  }
}
```

**Response (200 OK) - Completed:**
```json
{
  "status": "success",
  "data": {
    "job_id": "job_abc123xyz789",
    "status": "completed",
    "created_at": "2026-02-02T18:54:57.324Z",
    "updated_at": "2026-02-02T18:56:15.500Z",
    "started_at": "2026-02-02T18:55:00.000Z",
    "completed_at": "2026-02-02T18:56:15.500Z",
    "progress": {
      "total_images": 2,
      "processed_images": 2,
      "percentage": 100
    },
    "summary": {
      "total_detections": 47,
      "average_confidence": 0.82,
      "processing_time_seconds": 75.5
    },
    "results_url": "/api/v1/jobs/job_abc123xyz789/results",
    "visualization_url": "/api/v1/jobs/job_abc123xyz789/visualization"
  }
}
```

**Response (200 OK) - Failed:**
```json
{
  "status": "success",
  "data": {
    "job_id": "job_abc123xyz789",
    "status": "failed",
    "created_at": "2026-02-02T18:54:57.324Z",
    "updated_at": "2026-02-02T18:55:45.200Z",
    "started_at": "2026-02-02T18:55:00.000Z",
    "failed_at": "2026-02-02T18:55:45.200Z",
    "error": {
      "code": "MODEL_LOAD_ERROR",
      "message": "Failed to load YOLO model",
      "details": "Model file not found: /path/to/best.pt"
    }
  }
}
```

**Job Status Values:**
- `queued`: Job created, waiting for worker
- `processing`: Worker actively processing
- `completed`: Successfully finished
- `failed`: Error occurred
- `cancelled`: User cancelled (future)

**Response (404 Not Found):**
```json
{
  "status": "error",
  "message": "Job not found",
  "error_code": "JOB_NOT_FOUND"
}
```

---

### Endpoint 4: Get Prediction Results (Text/Labels)

**Purpose**: Retrieve text predictions and bounding box labels

```http
GET /api/v1/jobs/{job_id}/results
```

**Query Parameters:**
- `format` (string, optional) - Output format: `json` (default), `yolo`, `coco`
- `file_id` (string, optional) - Filter results for specific image

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/jobs/job_abc123xyz789/results?format=json"
```

**Response (200 OK) - JSON Format:**
```json
{
  "status": "success",
  "data": {
    "job_id": "job_abc123xyz789",
    "format": "json",
    "results": [
      {
        "file_id": "img_x1y2z3",
        "filename": "image1.jpg",
        "detections": [
          {
            "class_id": 0,
            "class_name": "plane",
            "confidence": 0.95,
            "bbox": {
              "format": "xyxy",
              "x_min": 100,
              "y_min": 150,
              "x_max": 300,
              "y_max": 250
            },
            "bbox_normalized": {
              "format": "yolo",
              "center_x": 0.104,
              "center_y": 0.185,
              "width": 0.104,
              "height": 0.093
            }
          }
        ],
        "detection_count": 1
      }
    ]
  }
}
```

**Response (200 OK) - YOLO Format:**
```json
{
  "status": "success",
  "data": {
    "job_id": "job_abc123xyz789",
    "format": "yolo",
    "files": [
      {
        "file_id": "img_x1y2z3",
        "filename": "image1.jpg",
        "label_content": "0 0.104 0.185 0.104 0.093 0.95\n1 0.523 0.678 0.089 0.123 0.87\n",
        "download_url": "/api/v1/jobs/job_abc123xyz789/results/img_x1y2z3/labels.txt"
      }
    ]
  }
}
```

**Response (404 Not Found):**
```json
{
  "status": "error",
  "message": "Results not available",
  "error_code": "RESULTS_NOT_READY",
  "details": "Job is still processing or failed"
}
```

---

### Endpoint 5: Get Visualization Images

**Purpose**: Retrieve annotated images with bounding boxes

```http
GET /api/v1/jobs/{job_id}/visualization
```

**Query Parameters:**
- `file_id` (string, optional) - Get specific image visualization
- `format` (string, optional) - `url` (default), `base64`

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/jobs/job_abc123xyz789/visualization"
```

**Response (200 OK) - URL Format:**
```json
{
  "status": "success",
  "data": {
    "job_id": "job_abc123xyz789",
    "visualizations": [
      {
        "file_id": "img_x1y2z3",
        "filename": "image1.jpg",
        "original_url": "/api/v1/files/img_x1y2z3/original",
        "annotated_url": "/api/v1/files/img_x1y2z3/annotated",
        "thumbnail_url": "/api/v1/files/img_x1y2z3/thumbnail",
        "detection_count": 15
      }
    ]
  }
}
```

**Response (200 OK) - Single File with Base64:**
```json
{
  "status": "success",
  "data": {
    "file_id": "img_x1y2z3",
    "filename": "image1.jpg",
    "format": "base64",
    "original_image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "annotated_image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "detection_count": 15
  }
}
```

**Serving Static Files:**
```http
GET /api/v1/files/{file_id}/original
GET /api/v1/files/{file_id}/annotated
GET /api/v1/files/{file_id}/thumbnail

Response: Binary image data (image/jpeg, image/png)
```

---

### Endpoint 6: Prometheus Metrics

**Purpose**: Expose metrics for Prometheus scraping

```http
GET /metrics
```

**Response (200 OK) - Prometheus Text Format:**
```
# HELP api_requests_total Total number of API requests
# TYPE api_requests_total counter
api_requests_total{method="POST",endpoint="/api/v1/inference/predict",status="202"} 342
api_requests_total{method="GET",endpoint="/api/v1/jobs/status",status="200"} 1567

# HELP inference_jobs_total Total number of inference jobs
# TYPE inference_jobs_total counter
inference_jobs_total{status="completed"} 298
inference_jobs_total{status="failed"} 12
inference_jobs_total{status="processing"} 5

# HELP inference_duration_seconds Duration of inference jobs
# TYPE inference_duration_seconds histogram
inference_duration_seconds_bucket{le="10"} 45
inference_duration_seconds_bucket{le="30"} 128
inference_duration_seconds_bucket{le="60"} 245
inference_duration_seconds_bucket{le="+Inf"} 310
inference_duration_seconds_sum 8234.5
inference_duration_seconds_count 310

# HELP model_inference_time_seconds Time taken for model inference per image
# TYPE model_inference_time_seconds histogram
model_inference_time_seconds_bucket{model="yolov11m-obb",le="0.5"} 123
model_inference_time_seconds_bucket{model="yolov11m-obb",le="1.0"} 456
model_inference_time_seconds_bucket{model="yolov11m-obb",le="+Inf"} 512

# HELP uploaded_files_total Total number of uploaded files
# TYPE uploaded_files_total counter
uploaded_files_total 1024

# HELP detection_count_total Total number of objects detected
# TYPE detection_count_total counter
detection_count_total{class="plane"} 4523
detection_count_total{class="ship"} 3211

# HELP active_workers Number of active Celery workers
# TYPE active_workers gauge
active_workers 4

# HELP queue_length Number of jobs in queue
# TYPE queue_length gauge
queue_length{queue="inference"} 5
```

**Metrics Exposed:**

| Metric | Type | Description |
|--------|------|-------------|
| `api_requests_total` | Counter | Total API requests by endpoint/method/status |
| `inference_jobs_total` | Counter | Total inference jobs by status |
| `inference_duration_seconds` | Histogram | Job completion time distribution |
| `model_inference_time_seconds` | Histogram | Per-image inference time |
| `uploaded_files_total` | Counter | Total uploaded images |
| `detection_count_total` | Counter | Objects detected by class |
| `active_workers` | Gauge | Active Celery workers |
| `queue_length` | Gauge | Jobs in queue |
| `cpu_usage_percent` | Gauge | CPU utilization |
| `memory_usage_bytes` | Gauge | Memory consumption |
| `gpu_utilization_percent` | Gauge | GPU usage (if available) |

---

## Workflow Documentation

### Workflow 1: End-to-End Inference

```
┌─────────────┐
│   Client    │
│  (Windows   │
│    App)     │
└──────┬──────┘
       │
       │ 1. POST /api/v1/inference/upload
       │    (multipart/form-data: images)
       │
       ▼
┌──────────────────┐
│   API Server     │
│  (FastAPI)       │
│                  │
│  - Validate      │      ┌─────────────────┐
│  - Save files    │─────▶│  File Storage   │
│  - Return IDs    │      └─────────────────┘
└──────┬───────────┘
       │
       │ 2. Response: upload_id, file_ids
       │
       ▼
┌─────────────┐
│   Client    │
│             │
│ 3. POST /api/v1/inference/predict
│    {upload_id, file_ids, config}
│             │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│   API Server     │
│                  │
│  - Validate      │
│  - Create job    │──────▶┌─────────────────┐
│  - Queue task    │       │   PostgreSQL    │
└──────┬───────────┘       │  (Job metadata) │
       │                   └─────────────────┘
       │
       │                   ┌─────────────────┐
       │──────────────────▶│  Celery Queue   │
       │  (Task enqueued)  │    (Redis)      │
       │                   └────────┬────────┘
       │                            │
       │ 4. Response: job_id        │
       │                            │
       ▼                            ▼
┌─────────────┐          ┌──────────────────┐
│   Client    │          │  Celery Worker   │
│             │          │                  │
│ 5. Poll:    │          │  - Load model    │
│  GET /jobs/ │          │  - Run SAHI      │
│  {job_id}/  │          │  - Apply NMS     │
│  status     │          │  - Prolog reason │
│             │          │  - Visualize     │
└──────┬──────┘          └────────┬─────────┘
       │                          │
       │                          │ Update status
       │                          ▼
       │                 ┌─────────────────┐
       │◀────────────────│     Redis       │
       │  Status updates │   (Job status)  │
       │                 └─────────────────┘
       │
       │ 6. Status: completed
       │
       ▼
┌─────────────┐
│   Client    │
│             │
│ 7. GET /jobs/{job_id}/results
│    GET /jobs/{job_id}/visualization
│             │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│   API Server     │
│                  │      ┌─────────────────┐
│  - Fetch results │─────▶│  File Storage   │
│  - Return data   │      │  (predictions,  │
└──────┬───────────┘      │   images)       │
       │                  └─────────────────┘
       │ 8. Response: predictions, images
       │
       ▼
┌─────────────┐
│   Client    │
│  (Display   │
│   results)  │
└─────────────┘
```

**Timeline:**
1. **Upload** (0s): Client uploads images → API returns upload_id
2. **Predict** (1s): Client triggers inference → API returns job_id (202 Accepted)
3. **Polling** (2-60s): Client polls status every 2-5 seconds
4. **Processing** (10-120s): Worker runs YOLO inference
5. **Completion** (60s): Status becomes "completed"
6. **Retrieval** (61s): Client fetches results and visualizations

---

### Workflow 2: File Upload and Validation

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ POST /api/v1/inference/upload
       │ Content-Type: multipart/form-data
       │ files: [image1.jpg, image2.png, invalid.pdf]
       │
       ▼
┌──────────────────────────────────────────┐
│   API Server - Upload Endpoint           │
│                                           │
│  ┌─────────────────────────────────────┐ │
│  │  1. Validate Request                │ │
│  │     - Check content type            │ │
│  │     - Count files (<= 100)          │ │
│  └──────────────┬──────────────────────┘ │
│                 │                         │
│                 ▼                         │
│  ┌─────────────────────────────────────┐ │
│  │  2. Validate Each File              │ │
│  │     For each file:                  │ │
│  │     - Check file extension          │ │
│  │     - Check file size (<= 50MB)     │ │
│  │     - Read image headers            │ │
│  │     - Validate dimensions           │ │
│  │     - Collect errors                │ │
│  └──────────────┬──────────────────────┘ │
│                 │                         │
│                 ▼                         │
│  ┌─────────────────────────────────────┐ │
│  │  3. Check Validation Results        │ │
│  │     - Any errors?                   │ │
│  └──────┬────────────────┬─────────────┘ │
│         │ YES            │ NO            │
│         │                │               │
│         ▼                ▼               │
│  ┌─────────────┐  ┌──────────────────┐  │
│  │ Return 400  │  │ 4. Generate IDs  │  │
│  │ with errors │  │    - upload_id   │  │
│  └─────────────┘  │    - file_ids    │  │
│                   └────────┬─────────┘  │
│                            │             │
│                            ▼             │
│                   ┌──────────────────┐  │
│                   │ 5. Save Files    │  │
│                   │    storage/      │  │
│                   │    uploads/      │  │
│                   │    {upload_id}/  │  │
│                   └────────┬─────────┘  │
│                            │             │
│                            ▼             │
│                   ┌──────────────────┐  │
│                   │ 6. Save Metadata │──┼─▶ PostgreSQL
│                   │    (table:       │  │   uploaded_files
│                   │     uploads)     │  │
│                   └────────┬─────────┘  │
│                            │             │
│                            ▼             │
│                   ┌──────────────────┐  │
│                   │ 7. Return 200 OK │  │
│                   │    with file IDs │  │
│                   └──────────────────┘  │
└─────────────────────────────────────────┘
```

**Validation Rules:**

| Check | Criteria | Error Code |
|-------|----------|------------|
| File format | JPEG, PNG, TIFF | INVALID_FORMAT |
| File size | <= 50 MB | FILE_TOO_LARGE |
| Dimensions | 64x64 to 8192x8192 | INVALID_DIMENSIONS |
| Batch size | <= 100 files | TOO_MANY_FILES |
| Content type | Valid image | CORRUPTED_FILE |

---

### Workflow 3: Error Handling Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Error Handling Strategy                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────┐
│   Client    │
│  Request    │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│  API Validation  │─── FAIL ───▶ 400 Bad Request
└──────┬───────────┘              {errors: [...]}
       │ PASS
       │
       ▼
┌──────────────────┐
│ Authentication   │─── FAIL ───▶ 401 Unauthorized
└──────┬───────────┘              {error: "Invalid token"}
       │ PASS
       │
       ▼
┌──────────────────┐
│  Authorization   │─── FAIL ───▶ 403 Forbidden
└──────┬───────────┘              {error: "Access denied"}
       │ PASS
       │
       ▼
┌──────────────────┐
│  Rate Limiting   │─── FAIL ───▶ 429 Too Many Requests
└──────┬───────────┘              {error: "Rate limit exceeded"}
       │ PASS
       │
       ▼
┌──────────────────┐
│  Create Job &    │
│  Queue Task      │
└──────┬───────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│              Celery Worker Processing                     │
│                                                           │
│  ┌────────────────┐                                      │
│  │ Model Loading  │─── FAIL ───▶ Update job status:     │
│  └────────┬───────┘              status="failed"         │
│           │ PASS                 error_code="MODEL_ERROR"│
│           │                                               │
│           ▼                                               │
│  ┌────────────────┐                                      │
│  │ File Reading   │─── FAIL ───▶ Update job status:     │
│  └────────┬───────┘              status="failed"         │
│           │ PASS                 error_code="FILE_ERROR" │
│           │                                               │
│           ▼                                               │
│  ┌────────────────┐                                      │
│  │ Inference      │─── FAIL ───▶ Update job status:     │
│  └────────┬───────┘              status="failed"         │
│           │ PASS                 error_code="INFERENCE_ERROR" │
│           │                                               │
│           ▼                                               │
│  ┌────────────────┐                                      │
│  │ Save Results   │─── FAIL ───▶ Update job status:     │
│  └────────┬───────┘              status="failed"         │
│           │ PASS                 error_code="STORAGE_ERROR" │
│           │                                               │
│           ▼                                               │
│  ┌────────────────┐                                      │
│  │ Mark Complete  │                                      │
│  └────────────────┘                                      │
└──────────────────────────────────────────────────────────┘
```

**Error Response Format:**

```json
{
  "status": "error",
  "message": "Human-readable error message",
  "error_code": "MACHINE_READABLE_CODE",
  "details": "Additional context",
  "timestamp": "2026-02-02T18:54:57.324Z",
  "request_id": "req_abc123"
}
```

**Common Error Codes:**

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_FORMAT` | 400 | Invalid file format |
| `FILE_TOO_LARGE` | 400 | File exceeds size limit |
| `INVALID_CONFIG` | 400 | Invalid configuration parameters |
| `UPLOAD_NOT_FOUND` | 404 | Upload ID doesn't exist |
| `JOB_NOT_FOUND` | 404 | Job ID doesn't exist |
| `RESULTS_NOT_READY` | 404 | Results not available yet |
| `MODEL_LOAD_ERROR` | 500 | Failed to load YOLO model |
| `INFERENCE_ERROR` | 500 | Inference pipeline failed |
| `STORAGE_ERROR` | 500 | File save/read failed |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |

**Retry Strategy:**

- **Client Retries**: 4xx errors should NOT be retried (client error)
- **Client Retries**: 5xx errors can be retried with exponential backoff
- **Celery Retries**: Failed tasks retry 3 times with delays: 60s, 300s, 900s

---

### Workflow 4: Monitoring Integration

```
┌─────────────────────────────────────────────────────────────┐
│              Prometheus Monitoring Architecture              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────┐
│   API Server    │
│                 │
│  Every request: │
│  - Counter++    │
│  - Histogram    │
│    (latency)    │
└────────┬────────┘
         │
         │ Exposes /metrics endpoint
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                      /metrics Endpoint                       │
│                                                              │
│  Aggregates metrics from:                                   │
│  - API request counters                                     │
│  - Job status gauges                                        │
│  - Queue length (from Redis)                                │
│  - Worker status (from Celery)                              │
│  - System metrics (CPU, memory, GPU)                        │
└────────┬────────────────────────────────────────────────────┘
         │
         │ Scrape every 15s
         │
         ▼
┌─────────────────┐
│   Prometheus    │
│    Server       │
│                 │
│  - Scrapes      │
│  - Stores TSDB  │
│  - Evaluates    │
│    alerts       │
└────────┬────────┘
         │
         │ Query API
         │
         ▼
┌─────────────────┐
│    Grafana      │
│   Dashboard     │
│                 │
│  Panels:        │
│  - Request rate │
│  - Job status   │
│  - Queue length │
│  - Worker health│
│  - Inference    │
│    latency      │
└─────────────────┘

┌─────────────────────────────────────────────────────────────┐
│          Windows App: Monitoring Dashboard Panel            │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Real-time Metrics (fetched from Prometheus API)       │ │
│  │                                                         │ │
│  │  Current Job: Processing (50% complete)                │ │
│  │  Queue Length: 3 jobs                                  │ │
│  │  Active Workers: 4                                     │ │
│  │  Avg Inference Time: 45.2s                             │ │
│  │                                                         │ │
│  │  [Chart: Job completion rate over time]                │ │
│  │  [Chart: Queue length over time]                       │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Metrics Collection Points:**

1. **API Endpoint Middleware**: Wrap each endpoint to record request metrics
2. **Celery Task Decorator**: Record task start, completion, failure
3. **Model Inference Hook**: Record per-image inference time
4. **System Monitor**: Periodically sample CPU/memory/GPU
5. **Redis Query**: Fetch queue length on-demand

**Frontend Integration:**

```javascript
// Windows app fetches metrics from Prometheus API
const response = await fetch('http://localhost:9090/api/v1/query', {
  method: 'POST',
  body: 'query=queue_length{queue="inference"}'
});
const data = await response.json();
displayQueueLength(data.result);
```

---

## Prometheus Integration

### Metrics Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Metrics Collection Pipeline                 │
└─────────────────────────────────────────────────────────────┘

Application Layer               Metrics Layer
─────────────────               ─────────────

┌─────────────────┐
│  API Request    │──▶ prometheus_client.Counter
│  (endpoint hit) │    ▸ api_requests_total
└─────────────────┘

┌─────────────────┐
│  Job Created    │──▶ prometheus_client.Counter
│                 │    ▸ inference_jobs_total{status="queued"}
└─────────────────┘

┌─────────────────┐
│  Job Started    │──▶ prometheus_client.Gauge
│                 │    ▸ active_jobs{status="processing"}
└─────────────────┘

┌─────────────────┐
│  Job Completed  │──▶ prometheus_client.Histogram
│  (duration)     │    ▸ inference_duration_seconds
└─────────────────┘

┌─────────────────┐
│  Model          │──▶ prometheus_client.Histogram
│  Inference      │    ▸ model_inference_time_seconds
└─────────────────┘

┌─────────────────┐
│  Queue Status   │──▶ prometheus_client.Gauge
│  (from Redis)   │    ▸ queue_length
└─────────────────┘

┌─────────────────┐
│  Worker Health  │──▶ prometheus_client.Gauge
│  (from Celery)  │    ▸ active_workers
└─────────────────┘
```

### Instrumentation Example (FastAPI)

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import FastAPI, Request
import time

app = FastAPI()

# Define metrics
REQUEST_COUNT = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'api_request_duration_seconds',
    'API request latency',
    ['method', 'endpoint']
)

JOB_COUNT = Counter(
    'inference_jobs_total',
    'Total inference jobs',
    ['status']
)

ACTIVE_JOBS = Gauge(
    'active_jobs',
    'Currently processing jobs'
)

QUEUE_LENGTH = Gauge(
    'queue_length',
    'Number of jobs in queue',
    ['queue']
)

# Middleware to track requests
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

### Prometheus Configuration

**prometheus.yml:**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'inference_api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    
  - job_name: 'celery_workers'
    static_configs:
      - targets: ['localhost:9091']  # Celery exporter
```

### Grafana Dashboard Panels

**Panel 1: API Request Rate**
- Metric: `rate(api_requests_total[5m])`
- Visualization: Time series graph
- Group by: endpoint

**Panel 2: Job Status Distribution**
- Metric: `inference_jobs_total`
- Visualization: Pie chart
- Group by: status

**Panel 3: Queue Length**
- Metric: `queue_length{queue="inference"}`
- Visualization: Gauge
- Alert: > 20 jobs queued

**Panel 4: Worker Health**
- Metric: `active_workers`
- Visualization: Stat panel
- Alert: < 2 workers active

**Panel 5: Inference Latency (p50, p95, p99)**
- Metric: `histogram_quantile(0.95, inference_duration_seconds)`
- Visualization: Time series graph

**Panel 6: Error Rate**
- Metric: `rate(inference_jobs_total{status="failed"}[5m])`
- Visualization: Time series graph
- Alert: > 5% failure rate

### Windows App Integration

The Windows application can display real-time metrics by:

1. **Option A: Query Prometheus API Directly**
   ```javascript
   const response = await fetch('http://localhost:9090/api/v1/query', {
     method: 'POST',
     headers: {'Content-Type': 'application/x-www-form-urlencoded'},
     body: 'query=queue_length'
   });
   ```

2. **Option B: Backend Aggregation Endpoint**
   ```http
   GET /api/v1/monitoring/dashboard
   ```
   Returns aggregated metrics in JSON for easy display

**Recommended**: Option B for better client simplicity

---

## Error Handling Strategy

### Error Classification

| Category | HTTP Status | Retry | Log Level | User Message |
|----------|-------------|-------|-----------|--------------|
| **Validation** | 400 | No | INFO | Show specific field errors |
| **Authentication** | 401 | No | WARNING | "Invalid credentials" |
| **Authorization** | 403 | No | WARNING | "Access denied" |
| **Not Found** | 404 | No | INFO | "Resource not found" |
| **Rate Limit** | 429 | Yes (backoff) | INFO | "Too many requests, try again" |
| **Server Error** | 500 | Yes (limited) | ERROR | "Server error, please retry" |
| **Inference Failure** | 500 | Yes (limited) | ERROR | "Inference failed: <reason>" |

### Structured Error Response

```json
{
  "status": "error",
  "error": {
    "code": "MACHINE_READABLE_ERROR_CODE",
    "message": "Human-readable error description",
    "details": "Additional context or debugging info",
    "field": "field_name",  // For validation errors
    "timestamp": "2026-02-02T18:54:57.324Z",
    "request_id": "req_abc123xyz789",
    "documentation_url": "https://docs.example.com/errors/ERROR_CODE"
  }
}
```

### Task Failure Handling

**Celery Retry Configuration:**
```python
@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 1 minute
    autoretry_for=(IOError, ConnectionError),
    retry_backoff=True,
    retry_jitter=True
)
def run_inference_task(self, job_id, config):
    try:
        # Inference logic
        pass
    except ModelLoadError as e:
        # Don't retry model load errors
        mark_job_failed(job_id, error_code="MODEL_LOAD_ERROR", message=str(e))
        raise
    except InferenceError as e:
        # Retry inference errors
        mark_job_failed(job_id, error_code="INFERENCE_ERROR", message=str(e))
        raise self.retry(exc=e)
```

### Client Error Handling (Windows App)

```javascript
async function triggerInference(uploadId, config) {
  try {
    const response = await fetch('/api/v1/inference/predict', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({upload_id: uploadId, config})
    });
    
    if (!response.ok) {
      const error = await response.json();
      
      // Handle specific error codes
      switch (error.error.code) {
        case 'UPLOAD_NOT_FOUND':
          showError('Upload expired, please re-upload images');
          break;
        case 'INVALID_CONFIG':
          showValidationErrors(error.error.details);
          break;
        default:
          showError(error.error.message);
      }
      return null;
    }
    
    return await response.json();
  } catch (e) {
    showError('Network error, please check connection');
    return null;
  }
}
```

---

## Security Considerations

### Authentication & Authorization

**Phase 1 (MVP)**: No authentication (local deployment only)

**Phase 2 (Production)**:
- **JWT Tokens**: Issue upon login, include in `Authorization: Bearer <token>` header
- **API Keys**: For programmatic access
- **Rate Limiting**: Prevent abuse (100 requests/minute per IP)
- **CORS**: Whitelist only Windows app origin

### Input Validation

- **File Upload**: Validate magic bytes, not just extension
- **Path Traversal**: Sanitize filenames, prevent directory escaping
- **SQL Injection**: Use parameterized queries (handled by ORM)
- **XSS**: Escape user input in error messages

### Data Protection

- **File Cleanup**: Delete uploaded files after 7 days
- **Secure Storage**: Ensure file permissions prevent unauthorized access
- **Logging**: Sanitize sensitive data from logs (file paths, configs)

### HTTPS

- **Production**: Enforce HTTPS with valid SSL certificate
- **Development**: HTTP acceptable for localhost

---

## Performance and Scalability

### Performance Targets

| Metric | Target |
|--------|--------|
| **API Latency** (p95) | < 200ms |
| **File Upload** (10MB) | < 3s |
| **Inference** (single image) | < 60s |
| **Concurrent Jobs** | 10+ workers |
| **Throughput** | 100+ images/hour |

### Optimization Strategies

1. **Async API**: FastAPI handles concurrent requests efficiently
2. **Celery Workers**: Scale horizontally with multiple workers
3. **Redis Caching**: Cache job status to reduce PostgreSQL load
4. **File Streaming**: Stream large files instead of loading into memory
5. **Model Caching**: Keep YOLO model loaded in worker memory
6. **Connection Pooling**: Reuse database connections

### Scalability Plan

**Phase 1: Single Server**
- API + 4 Celery workers + PostgreSQL + Redis on one machine
- Supports: 100 images/hour

**Phase 2: Horizontal Scaling**
- Load balancer → Multiple API servers
- Shared Redis + PostgreSQL
- Worker pool: 10+ workers on separate machines
- S3-compatible storage (MinIO)
- Supports: 1000+ images/hour

**Phase 3: Distributed System**
- Kubernetes orchestration
- Auto-scaling workers based on queue length
- Cloud storage (AWS S3)
- Managed PostgreSQL (RDS)
- Supports: 10,000+ images/hour

---

## Future Enhancements

### Planned Features

1. **Batch Processing API**
   - Submit entire directories
   - Bulk download results

2. **Webhooks**
   - Notify client when job completes
   - Eliminate polling

3. **Model Management API**
   - Upload custom models
   - Model versioning
   - A/B testing

4. **Advanced Monitoring**
   - Distributed tracing (OpenTelemetry)
   - Custom Grafana dashboards
   - Alerting rules

5. **WebSocket Support**
   - Real-time job progress updates
   - Streaming logs

6. **Authentication**
   - User accounts
   - API key management
   - Role-based access control

7. **Export Options**
   - COCO format export
   - Pascal VOC export
   - Custom annotation formats

8. **Comparison API**
   - Compare two inference runs
   - Side-by-side visualization

---

## Appendix

### API Versioning Policy

- **URL Versioning**: `/api/v1`, `/api/v2`
- **Backward Compatibility**: v1 maintained for 1 year after v2 release
- **Deprecation Notices**: Announced 6 months in advance
- **Response Headers**: Include `X-API-Version: 1.0`

### Testing Strategy

1. **Unit Tests**: Test each endpoint in isolation with mocked dependencies
2. **Integration Tests**: Test end-to-end flows with test database
3. **Load Tests**: Use Locust to simulate 1000 concurrent users
4. **Contract Tests**: Ensure API contract matches OpenAPI spec

### Documentation Standards

- **OpenAPI Spec**: Auto-generated by FastAPI
- **Swagger UI**: Available at `/docs`
- **ReDoc**: Alternative docs at `/redoc`
- **Postman Collection**: Export for client developers

---

**Document Status**: Complete ✅  
**Next Steps**: Implementation planning and development kickoff  
**Maintained By**: Backend Engineering Team  
**Last Updated**: February 2, 2026
