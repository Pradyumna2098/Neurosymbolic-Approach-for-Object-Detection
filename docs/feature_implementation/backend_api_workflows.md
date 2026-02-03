# Backend API Detailed Workflow Diagrams

**Version:** 1.0  
**Date:** February 2, 2026  
**Status:** Design Specification  

## Table of Contents
1. [Overview](#overview)
2. [Complete End-to-End Workflow](#complete-end-to-end-workflow)
3. [File Upload Workflow](#file-upload-workflow)
4. [Inference Execution Workflow](#inference-execution-workflow)
5. [Job Status Polling Workflow](#job-status-polling-workflow)
6. [Results Retrieval Workflow](#results-retrieval-workflow)
7. [Error Handling Workflows](#error-handling-workflows)
8. [Monitoring Data Flow](#monitoring-data-flow)
9. [State Transitions](#state-transitions)
10. [Sequence Diagrams](#sequence-diagrams)

---

## Overview

This document provides detailed workflow diagrams for all backend API operations. Each workflow includes:
- **ASCII flow diagrams** for visual understanding
- **Step-by-step descriptions** of each operation
- **Data transformations** at each stage
- **Error handling** paths
- **Integration points** with external systems

---

## Complete End-to-End Workflow

### High-Level User Journey

```
┌────────────────────────────────────────────────────────────────────────┐
│                    Complete Inference Pipeline                          │
└────────────────────────────────────────────────────────────────────────┘

   USER ACTION                API OPERATION           SYSTEM STATE
   ───────────                ─────────────           ────────────

1. Select Images          ┌──────────────────┐
   from Filesystem  ────▶ │ Validate Files   │
                          │ (client-side)    │
                          └────────┬─────────┘
                                   │
                                   ▼
2. Click Upload           ┌──────────────────┐
                    ────▶ │ POST /upload     │─────▶ Files stored
                          └────────┬─────────┘       upload_id created
                                   │
                                   ▼
                          ┌──────────────────┐
                          │ Return upload_id │
                          │ & file_ids       │
                          └────────┬─────────┘
                                   │
                                   ▼
3. Configure             ┌──────────────────┐
   Parameters      ────▶ │ Set confidence,  │
                          │ SAHI settings    │
                          └────────┬─────────┘
                                   │
                                   ▼
4. Click "Run            ┌──────────────────┐
   Detection"      ────▶ │ POST /predict    │─────▶ Job created
                          │ with config      │       Task queued
                          └────────┬─────────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │ Return job_id    │
                          │ (202 Accepted)   │
                          └────────┬─────────┘
                                   │
                                   ▼
5. Watch Progress        ┌──────────────────┐
   Indicator       ────▶ │ Poll GET /status │─────▶ Status updates:
                          │ every 2-5s       │       queued → processing
                          └────────┬─────────┘       → completed
                                   │
                                   │ (Loop until completed/failed)
                                   │
                                   ▼
6. View Results          ┌──────────────────┐
                    ────▶ │ GET /results     │─────▶ Predictions
                          │ GET /viz         │       Annotated images
                          └────────┬─────────┘
                                   │
                                   ▼
7. Export/Save           ┌──────────────────┐
                    ────▶ │ Download files   │─────▶ Save locally
                          │ Generate reports │
                          └──────────────────┘

Timeline: 0s────10s────30s────60s────90s────120s
          ↑     ↑      ↑      ↑      ↑       ↑
        Upload │   Predict │  Poll  │   Retrieve
             Config      Queue    Process   Results
```

---

## File Upload Workflow

### Detailed Upload Process

```
┌────────────────────────────────────────────────────────────────────────┐
│                        File Upload Workflow                             │
└────────────────────────────────────────────────────────────────────────┘

CLIENT (Windows App)              API SERVER                  STORAGE
────────────────                  ──────────                  ───────

1. User selects files
   ├─ image1.jpg (2MB)
   ├─ image2.png (4MB)
   └─ folder/image3.tiff (10MB)
        │
        │ Pre-flight validation (client-side)
        │ ├─ Check formats
        │ ├─ Check sizes
        │ └─ Count files
        │
        ▼
2. Prepare multipart/form-data
   ┌────────────────────────┐
   │ Content-Type: multipart│
   │ files: [File, File...] │
   └───────────┬────────────┘
               │
               │ HTTP POST
               │
               ▼
        ┌────────────────────────────┐
        │  API: /api/v1/inference/   │
        │         upload              │
        └──────────┬─────────────────┘
                   │
                   ▼
3.          ┌─────────────────────────┐
            │  Parse multipart data   │
            │  Extract files array    │
            └──────────┬──────────────┘
                       │
                       ▼
4.          ┌─────────────────────────┐
            │  For each file:         │
            │                         │
            │  ┌───────────────────┐  │
            │  │ Validate format   │  │
            │  │ - Magic bytes     │  │
            │  │ - Extension       │  │
            │  └─────────┬─────────┘  │
            │            │             │
            │            ▼             │
            │  ┌───────────────────┐  │
            │  │ Validate size     │  │
            │  │ - Check <= 50MB   │  │
            │  └─────────┬─────────┘  │
            │            │             │
            │            ▼             │
            │  ┌───────────────────┐  │
            │  │ Read image header │  │
            │  │ - Get dimensions  │  │
            │  │ - Verify format   │  │
            │  └─────────┬─────────┘  │
            │            │             │
            │  ┌─────────▼─────────┐  │
            │  │ Collect metadata  │  │
            │  │ - filename        │  │
            │  │ - size_bytes      │  │
            │  │ - dimensions      │  │
            │  │ - format          │  │
            │  └───────────────────┘  │
            └─────────────────────────┘
                       │
                       │ All valid?
                       │
        ┌──────────────┴──────────────┐
        │ NO (errors)   │ YES          │
        │               │              │
        ▼               ▼              │
   ┌────────────┐ ┌─────────────────┐ │
   │ Return 400 │ │ Generate IDs:   │ │
   │ Bad Request│ │ - upload_id     │ │
   │            │ │ - file_id (each)│ │
   │ {errors:[]}│ └────────┬────────┘ │
   └────────────┘          │          │
                           ▼          │
                  ┌─────────────────┐ │
                  │ Save files to:  │ │    ┌─────────────┐
                  │ storage/uploads/│─┼───▶│ Filesystem  │
                  │ {upload_id}/    │ │    │             │
                  │ {file_id}.ext   │ │    │ /storage/   │
                  └────────┬────────┘ │    │  uploads/   │
                           │          │    └─────────────┘
                           ▼          │
                  ┌─────────────────┐ │
                  │ Save metadata   │ │    ┌─────────────┐
                  │ to PostgreSQL:  │─┼───▶│ PostgreSQL  │
                  │                 │ │    │             │
                  │ TABLE: uploads  │ │    │ uploads     │
                  │ - upload_id     │ │    │ uploaded_   │
                  │ - user_id       │ │    │   files     │
                  │ - created_at    │ │    └─────────────┘
                  │                 │ │
                  │ TABLE: files    │ │
                  │ - file_id       │ │
                  │ - upload_id (FK)│ │
                  │ - filename      │ │
                  │ - size_bytes    │ │
                  │ - dimensions    │ │
                  │ - format        │ │
                  │ - storage_path  │ │
                  └────────┬────────┘ │
                           │          │
                           ▼          │
                  ┌─────────────────┐ │
                  │ Return 200 OK   │ │
                  │                 │ │
                  │ {               │ │
                  │   upload_id,    │ │
                  │   files: [      │ │
                  │     {file_id,   │ │
                  │      filename,  │ │
                  │      size,      │ │
                  │      dimensions}│ │
                  │   ]             │ │
                  │ }               │ │
                  └────────┬────────┘ │
                           │          │
        ◀──────────────────┘          │
        │                             │
        ▼                             │
   ┌────────────┐                     │
   │ Store IDs  │                     │
   │ in state   │                     │
   │            │                     │
   │ Enable     │                     │
   │ "Run       │                     │
   │ Detection" │                     │
   │ button     │                     │
   └────────────┘                     │
                                      │
```

### Upload Data Flow

```
INPUT                          PROCESSING                      OUTPUT
─────                          ──────────                      ──────

Files from                     Validation                      upload_id
filesystem                     ├─ Format check                 file_ids[]
├─ image1.jpg     ────▶       ├─ Size check        ────▶     storage_paths[]
├─ image2.png                  ├─ Dimension check             metadata
└─ image3.tiff                 └─ Content verification        
                                         │
                                         ▼
                               Storage
                               ├─ Save to disk
                               ├─ Save metadata to DB
                               └─ Generate unique IDs
```

### Error Scenarios

```
ERROR CONDITION              HTTP STATUS    ERROR CODE           USER MESSAGE
───────────────              ───────────    ──────────           ────────────

Invalid file format          400            INVALID_FORMAT       "Only JPEG, PNG, TIFF allowed"
File too large (>50MB)       400            FILE_TOO_LARGE       "File exceeds 50MB limit"
Too many files (>100)        400            TOO_MANY_FILES       "Maximum 100 files per upload"
Invalid dimensions           400            INVALID_DIMENSIONS   "Image must be 64x64 to 8192x8192"
Corrupted file               400            CORRUPTED_FILE       "Unable to read image file"
Disk space full              500            STORAGE_ERROR        "Server storage unavailable"
Database connection error    500            DATABASE_ERROR       "Unable to save metadata"
```

---

## Inference Execution Workflow

### Predict Endpoint to Celery Task

```
┌────────────────────────────────────────────────────────────────────────┐
│                    Inference Execution Workflow                         │
└────────────────────────────────────────────────────────────────────────┘

CLIENT                  API SERVER              CELERY              WORKER
──────                  ──────────              ──────              ──────

1. Prepare config
   ┌─────────────────┐
   │ {               │
   │   upload_id,    │
   │   file_ids: [], │
   │   config: {     │
   │     confidence, │
   │     sahi: {...},│
   │     symbolic...}│
   │ }               │
   └────────┬────────┘
            │
            │ POST /api/v1/inference/predict
            │
            ▼
      ┌─────────────────────┐
      │ Validate request    │
      │ ├─ upload_id exists │
      │ ├─ file_ids valid   │
      │ ├─ config params    │
      │ │  in range         │
      │ └─ model_path exists│
      └──────────┬──────────┘
                 │
                 ▼
      ┌─────────────────────┐
      │ Create job record   │         ┌──────────────┐
      │ in PostgreSQL       │────────▶│ PostgreSQL   │
      │                     │         │              │
      │ INSERT INTO jobs    │         │ jobs table:  │
      │ VALUES (            │         │ - job_id     │
      │   job_id (UUID),    │         │ - upload_id  │
      │   upload_id,        │         │ - status     │
      │   status='queued',  │         │ - config     │
      │   config (JSON),    │         │ - created_at │
      │   created_at        │         └──────────────┘
      │ )                   │
      └──────────┬──────────┘
                 │
                 ▼
      ┌─────────────────────┐
      │ Create Celery task  │
      │                     │
      │ task_id = celery    │
      │   .send_task(       │         ┌──────────────┐
      │     'run_inference',│────────▶│ Redis        │
      │     args=[          │         │ (Broker)     │
      │       job_id,       │         │              │
      │       config        │         │ Queue:       │
      │     ]               │         │ 'inference'  │
      │   )                 │         │              │
      └──────────┬──────────┘         │ Task queued  │
                 │                    └──────────────┘
                 │
                 ▼
      ┌─────────────────────┐
      │ Return 202 Accepted │
      │                     │
      │ {                   │
      │   status: "accepted"│
      │   data: {           │
      │     job_id,         │
      │     status: "queued"│
      │     created_at,     │
      │     status_url      │
      │   }                 │
      │ }                   │
      └──────────┬──────────┘
                 │
    ◀────────────┘
    │
    ▼
┌────────────┐
│ Store      │
│ job_id     │
│            │
│ Start      │
│ polling    │
│ /status    │
└────────────┘

                                          ┌──────────────┐
                                          │ Celery       │
                                          │ Worker       │
                                          │ (awaiting)   │
                                          └──────┬───────┘
                                                 │
                                                 │ Worker picks up task
                                                 │
                                                 ▼
                                       ┌─────────────────────┐
                                       │ run_inference_task  │
                                       │ (job_id, config)    │
                                       └──────────┬──────────┘
                                                  │
                                                  ▼
                                       ┌─────────────────────┐
                                       │ Update job status   │
                                       │ status='processing' │
                                       └──────────┬──────────┘
                                                  │
                                                  ▼
                                       ┌─────────────────────┐
                                       │ Execute pipeline    │
                                       │ (see next diagram)  │
                                       └─────────────────────┘
```

### Worker Inference Pipeline

```
┌────────────────────────────────────────────────────────────────────────┐
│              Celery Worker: Inference Pipeline Execution                │
└────────────────────────────────────────────────────────────────────────┘

INPUT                         PROCESSING                        OUTPUT
─────                         ──────────                        ──────

job_id, config      ┌──────────────────────────┐
                    │ 1. Load Model            │
file_ids  ────────▶ │    - Check cache         │
                    │    - Load YOLO weights   │
storage/uploads/    │    - Warm up (inference) │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ 2. For each file_id:     │
                    │                          │
                    │  ┌────────────────────┐  │
                    │  │ Load image from    │  │
                    │  │ storage            │  │
                    │  └──────────┬─────────┘  │
                    │             │             │
                    │             ▼             │
                    │  ┌────────────────────┐  │
                    │  │ Run SAHI sliced    │  │
                    │  │ prediction         │  │
                    │  │ - Slice image      │  │
                    │  │ - Inference slices │  │
                    │  │ - Merge results    │  │
                    │  └──────────┬─────────┘  │
                    │             │             │
                    │             ▼             │
                    │  ┌────────────────────┐  │
                    │  │ Apply NMS          │  │
                    │  │ (class-wise)       │  │
                    │  └──────────┬─────────┘  │    storage/results/
                    │             │             │    {job_id}/
                    │             ▼             │         │
                    │  ┌────────────────────┐  │         │
                    │  │ Symbolic reasoning │  │         ▼
                    │  │ (if enabled)       │  │    ┌─────────────┐
                    │  │ - Load Prolog rules│  │    │ predictions/│
                    │  │ - Query adjustments│  │    │ {file_id}.txt│
                    │  │ - Update confidence│  │    │             │
                    │  └──────────┬─────────┘  │    │ YOLO format │
                    │             │             │    └─────────────┘
                    │             ▼             │
                    │  ┌────────────────────┐  │         │
                    │  │ Save predictions   │──┼────────▶│
                    │  │ (YOLO format)      │  │         │
                    │  └──────────┬─────────┘  │         ▼
                    │             │             │    ┌─────────────┐
                    │             ▼             │    │visualizations/│
                    │  ┌────────────────────┐  │    │{file_id}.jpg │
                    │  │ Generate viz       │──┼───▶│              │
                    │  │ (if enabled)       │  │    │ Annotated    │
                    │  │ - Draw bboxes      │  │    │ with bboxes  │
                    │  │ - Add labels       │  │    └─────────────┘
                    │  │ - Show confidence  │  │
                    │  └──────────┬─────────┘  │
                    │             │             │
                    │             ▼             │
                    │  ┌────────────────────┐  │
                    │  │ Update progress    │  │
                    │  │ in Redis           │  │
                    │  └────────────────────┘  │
                    │                          │
                    └──────────────────────────┘
                                 │
                                 │ All files processed
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ 3. Compute summary       │
                    │    - Total detections    │
                    │    - Avg confidence      │
                    │    - Processing time     │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ 4. Update job record     │
                    │    status='completed'    │
                    │    completed_at          │
                    │    summary (JSON)        │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ 5. Cache status in Redis │
                    │    (for fast polling)    │
                    └──────────────────────────┘

TIMELINE:
0s──────10s──────30s──────60s──────90s
↑       ↑        ↑        ↑        ↑
Start   Model    SAHI     Symbolic Complete
Task    Load     Infer    Reason   
```

### Error Handling in Worker

```
ERROR AT STAGE         ACTION                              JOB STATUS
──────────────         ──────                              ──────────

Model load fails  ───▶ Update job status='failed'    ───▶  'failed'
                       error_code='MODEL_LOAD_ERROR'       (no retry)

File not found    ───▶ Update job status='failed'    ───▶  'failed'
                       error_code='FILE_NOT_FOUND'         (no retry)

CUDA OOM          ───▶ Retry with CPU fallback      ───▶  'processing'
                       (if retry fails, mark failed)       (retry once)

Inference error   ───▶ Retry task (3 attempts)      ───▶  'processing'
                       Exponential backoff                 (retry 3x)

Storage write err ───▶ Retry task (3 attempts)      ───▶  'processing'
                       Cleanup partial results             (retry 3x)

After 3 retries   ───▶ Update job status='failed'   ───▶  'failed'
                       error_code='MAX_RETRIES'            (permanent)
```

---

## Job Status Polling Workflow

### Client Polling Loop

```
┌────────────────────────────────────────────────────────────────────────┐
│                      Job Status Polling Workflow                        │
└────────────────────────────────────────────────────────────────────────┘

CLIENT                        API SERVER                 STORAGE
──────                        ──────────                 ───────

job_id stored
from /predict
    │
    │ Start polling loop
    │
    ▼
┌─────────────────────┐
│ Wait 2 seconds      │ ◀──────────────────┐
│ (initial) or 5s     │                    │
│ (subsequent)        │                    │
└──────────┬──────────┘                    │
           │                                │
           │ GET /api/v1/jobs/{job_id}/status
           │                                │
           ▼                                │
      ┌─────────────────────┐              │
      │ Fetch job status    │              │
      │                     │              │
      │ 1. Check Redis cache│    ┌──────────────┐
      │    (fast path)      │───▶│ Redis        │
      └──────────┬──────────┘    │              │
                 │                │ Key: job:{id}│
                 │ Cache miss?    │ Value: JSON  │
                 │                └──────────────┘
                 ▼                        │
      ┌─────────────────────┐            │
      │ 2. Query PostgreSQL │            │
      │    (fallback)       │────────────┤
      │                     │            │
      │ SELECT * FROM jobs  │    ┌──────▼──────┐
      │ WHERE job_id = ?    │    │ PostgreSQL  │
      └──────────┬──────────┘    │             │
                 │                │ jobs table  │
                 │                └─────────────┘
                 ▼
      ┌─────────────────────┐
      │ 3. Return status    │
      │                     │
      │ {                   │
      │   job_id,           │
      │   status,           │
      │   progress: {       │
      │     total_images,   │
      │     processed,      │
      │     percentage      │
      │   },                │
      │   ...               │
      │ }                   │
      └──────────┬──────────┘
                 │
    ◀────────────┘
    │
    ▼
┌─────────────────────┐
│ Check status value  │
└──────────┬──────────┘
           │
    ┌──────┴──────────────────┐
    │                          │
    ▼                          ▼
┌─────────┐              ┌─────────┐
│'queued' │              │'failed' │
│   or    │              └────┬────┘
│'processing'│                │
└────┬────┘                   │
     │                        │
     │ Continue polling       │ Stop polling
     │                        │ Show error
     └───────────────────────▶│
                              │
                         ┌────▼────┐
                         │'completed'
                         └────┬────┘
                              │
                              │ Stop polling
                              │ Fetch results
                              │
                              ▼
                    ┌─────────────────┐
                    │ GET /results    │
                    │ GET /visualization
                    └─────────────────┘
```

### Status Response Formats

```
STATUS: 'queued'
──────────────────────────────────────
{
  "job_id": "job_abc123",
  "status": "queued",
  "created_at": "2026-02-02T18:54:57Z",
  "progress": {
    "total_images": 5,
    "processed_images": 0,
    "percentage": 0
  }
}

STATUS: 'processing'
──────────────────────────────────────
{
  "job_id": "job_abc123",
  "status": "processing",
  "created_at": "2026-02-02T18:54:57Z",
  "started_at": "2026-02-02T18:55:00Z",
  "updated_at": "2026-02-02T18:55:30Z",
  "progress": {
    "total_images": 5,
    "processed_images": 2,
    "percentage": 40,
    "current_stage": "Running SAHI inference on image3.jpg",
    "estimated_completion": "2026-02-02T18:57:00Z"
  }
}

STATUS: 'completed'
──────────────────────────────────────
{
  "job_id": "job_abc123",
  "status": "completed",
  "created_at": "2026-02-02T18:54:57Z",
  "started_at": "2026-02-02T18:55:00Z",
  "completed_at": "2026-02-02T18:56:45Z",
  "progress": {
    "total_images": 5,
    "processed_images": 5,
    "percentage": 100
  },
  "summary": {
    "total_detections": 127,
    "average_confidence": 0.84,
    "processing_time_seconds": 105
  },
  "results_url": "/api/v1/jobs/job_abc123/results",
  "visualization_url": "/api/v1/jobs/job_abc123/visualization"
}

STATUS: 'failed'
──────────────────────────────────────
{
  "job_id": "job_abc123",
  "status": "failed",
  "created_at": "2026-02-02T18:54:57Z",
  "started_at": "2026-02-02T18:55:00Z",
  "failed_at": "2026-02-02T18:55:23Z",
  "error": {
    "code": "MODEL_LOAD_ERROR",
    "message": "Failed to load YOLO model",
    "details": "Model file not found. Refer to server logs for more details."
  }
}
```

---

## Results Retrieval Workflow

### Getting Prediction Results

```
┌────────────────────────────────────────────────────────────────────────┐
│                     Results Retrieval Workflow                          │
└────────────────────────────────────────────────────────────────────────┘

CLIENT                     API SERVER                    STORAGE
──────                     ──────────                    ───────

Job completed
status received
    │
    │ GET /api/v1/jobs/{job_id}/results?format=json
    │
    ▼
         ┌─────────────────────┐
         │ Validate job_id     │
         │                     │      ┌──────────────┐
         │ SELECT * FROM jobs  │─────▶│ PostgreSQL   │
         │ WHERE job_id = ?    │      └──────────────┘
         └──────────┬──────────┘
                    │
                    │ Job exists?
                    │
          ┌─────────┴─────────┐
          │ NO                │ YES
          │                   │
          ▼                   ▼
   ┌────────────┐    ┌─────────────────────┐
   │ Return 404 │    │ Check job status    │
   │ JOB_NOT_   │    │                     │
   │ FOUND      │    │ status == 'completed'?
   └────────────┘    └──────────┬──────────┘
                                │
                      ┌─────────┴─────────┐
                      │ NO                │ YES
                      │ (queued/          │
                      │  processing/      │
                      │  failed)          │
                      │                   │
                      ▼                   ▼
               ┌────────────┐    ┌─────────────────────┐
               │ Return 404 │    │ Get file_ids for job│
               │ RESULTS_   │    │                     │
               │ NOT_READY  │    │ SELECT file_id FROM │
               └────────────┘    │ uploaded_files      │
                                 │ WHERE upload_id =   │
                                 │   (SELECT upload_id │
                                 │    FROM jobs        │
                                 │    WHERE job_id=?)  │
                                 └──────────┬──────────┘
                                            │
                                            ▼
                                 ┌─────────────────────┐
                                 │ For each file_id:   │
                                 │                     │
                                 │ Read prediction file│    storage/results/
                                 │ from storage        │──▶ {job_id}/
                                 │                     │    predictions/
                                 │ Path: storage/      │    {file_id}.txt
                                 │ results/{job_id}/   │
                                 │ predictions/        │
                                 │ {file_id}.txt       │
                                 └──────────┬──────────┘
                                            │
                                            ▼
                                 ┌─────────────────────┐
                                 │ Parse YOLO format   │
                                 │                     │
                                 │ For each line:      │
                                 │ class cx cy w h conf│
                                 │                     │
                                 │ Convert to JSON:    │
                                 │ {                   │
                                 │   class_id: 0,      │
                                 │   class_name: "...", │
                                 │   confidence: 0.95, │
                                 │   bbox: {...}       │
                                 │ }                   │
                                 └──────────┬──────────┘
                                            │
                                            ▼
                                 ┌─────────────────────┐
                                 │ Aggregate results   │
                                 │                     │
                                 │ Group by file_id    │
                                 │ Count detections    │
                                 │ Compute statistics  │
                                 └──────────┬──────────┘
                                            │
                                            ▼
                                 ┌─────────────────────┐
                                 │ Return 200 OK       │
                                 │                     │
                                 │ {                   │
                                 │   job_id,           │
                                 │   format: "json",   │
                                 │   results: [        │
                                 │     {               │
                                 │       file_id,      │
                                 │       filename,     │
                                 │       detections: []│
                                 │     }               │
                                 │   ]                 │
                                 │ }                   │
                                 └──────────┬──────────┘
                                            │
                        ◀───────────────────┘
                        │
                        ▼
               ┌─────────────────┐
               │ Display results │
               │ in UI:          │
               │ - Bounding boxes│
               │ - Class labels  │
               │ - Confidence    │
               └─────────────────┘
```

### Getting Visualization Images

```
CLIENT                     API SERVER                    STORAGE
──────                     ──────────                    ───────

    │ GET /api/v1/jobs/{job_id}/visualization
    │
    ▼
         ┌─────────────────────┐
         │ Validate job_id     │
         │ Check status        │
         │ (same as results)   │
         └──────────┬──────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │ Get file_ids        │
         │ for job             │
         └──────────┬──────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │ For each file_id:   │
         │                     │      storage/results/
         │ Build URLs:         │      {job_id}/
         │                     │         │
         │ original_url:       │         ├─ uploads/
         │   /files/{file_id}/ │ ◀───────┤     {file_id}.jpg
         │   original          │         │
         │                     │         ├─ visualizations/
         │ annotated_url:      │ ◀───────┤     {file_id}.jpg
         │   /files/{file_id}/ │         │
         │   annotated         │         └─ thumbnails/
         │                     │ ◀───────      {file_id}.jpg
         │ thumbnail_url:      │
         │   /files/{file_id}/ │
         │   thumbnail         │
         └──────────┬──────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │ Return 200 OK       │
         │                     │
         │ {                   │
         │   visualizations: [ │
         │     {               │
         │       file_id,      │
         │       filename,     │
         │       original_url, │
         │       annotated_url,│
         │       thumbnail_url,│
         │       detection_count│
         │     }               │
         │   ]                 │
         │ }                   │
         └──────────┬──────────┘
                    │
       ◀────────────┘
       │
       ▼
┌──────────────────┐
│ Fetch images via │
│ image URLs       │
│                  │
│ For each file:   │
│ GET /files/      │
│   {file_id}/     │
│   annotated      │
└────────┬─────────┘
         │
         ▼
      ┌──────────────────┐
      │ Serve static file│      storage/results/
      │                  │──────{job_id}/
      │ Read from disk:  │      visualizations/
      │ storage/results/ │      {file_id}.jpg
      │ {job_id}/viz/    │
      │ {file_id}.jpg    │
      │                  │
      │ Response:        │
      │ Content-Type:    │
      │   image/jpeg     │
      │ Binary data      │
      └────────┬─────────┘
               │
  ◀────────────┘
  │
  ▼
┌──────────────────┐
│ Display images   │
│ in results viewer│
└──────────────────┘
```

---

## Error Handling Workflows

### Client-Side Error Handling

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Client Error Handling Strategy                        │
└────────────────────────────────────────────────────────────────────────┘

API CALL                      RESPONSE                      ACTION
────────                      ────────                      ──────

Any Request  ───▶  Network Error             ───▶  Show: "Connection failed"
                   (timeout, DNS, etc.)              Retry: Prompt user

POST /upload ───▶  400 Bad Request           ───▶  Show field errors
                   {errors: [{field, msg}]}         Highlight invalid files
                                                     Don't retry

POST /predict ──▶  400 Bad Request           ───▶  Show config errors
                   INVALID_CONFIG                   Highlight invalid params
                                                     Don't retry

GET /status  ───▶  404 Not Found             ───▶  Show: "Job not found"
                   JOB_NOT_FOUND                    Stop polling
                                                     Don't retry

GET /results ───▶  404 Not Found             ───▶  Show: "Results not ready"
                   RESULTS_NOT_READY                Keep polling status
                                                     Don't retry immediately

POST /predict ──▶  429 Too Many Requests     ───▶  Show: "Rate limited"
                   RATE_LIMIT_EXCEEDED              Wait 60s, retry
                                                     Exponential backoff

Any Request  ───▶  500 Internal Error        ───▶  Show: "Server error"
                   500 Status                       Retry: 3 times
                                                     Exponential backoff:
                                                     5s, 15s, 45s

GET /status  ───▶  200 OK                    ───▶  Check status field
                   {status: "failed"}               Show error.message
                                                     Show error.details
                                                     Offer "Try Again"
```

### Server-Side Error Handling

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Server Error Recovery Strategy                        │
└────────────────────────────────────────────────────────────────────────┘

ERROR SOURCE              DETECTION                  RECOVERY
────────────              ─────────                  ────────

Database connection  ───▶ Connection timeout   ───▶ Retry connection 3x
                          PostgreSQL error          Return 503 if fail
                                                     Log error

Redis connection     ───▶ Connection refused   ───▶ Fallback to PostgreSQL
                          Redis timeout             Log warning
                                                     Continue operation

File not found       ───▶ FileNotFoundError    ───▶ Return 404
                          on disk read              Log error
                                                     No retry

Disk space full      ───▶ OSError: No space   ───▶ Return 500 STORAGE_ERROR
                          on file write             Alert ops team
                                                     Cleanup old files

Model load failure   ───▶ YOLO load error     ───▶ Try CPU fallback
                          CUDA error                If fail, mark job failed
                                                     Don't retry task

Inference OOM        ───▶ CUDA OOM            ───▶ Reduce batch size
                          RuntimeError              Retry once
                                                     If fail, use CPU

Celery worker crash  ───▶ Task timeout        ───▶ Task auto-requeued
                          No heartbeat              Retry 3x
                                                     Max retries → failed
```

---

## Monitoring Data Flow

### Prometheus Metrics Collection

```
┌────────────────────────────────────────────────────────────────────────┐
│                  Prometheus Monitoring Data Flow                        │
└────────────────────────────────────────────────────────────────────────┘

APPLICATION EVENTS           METRICS COLLECTION          PROMETHEUS
──────────────────           ──────────────────          ──────────

API Request arrives
  │
  ├─ Method: POST             Counter.inc()          ┌──────────────┐
  ├─ Endpoint: /predict  ───▶ api_requests_total ───▶│ Prometheus   │
  └─ Status: 202              {method, endpoint}     │ TSDB         │
                                                      └──────────────┘
Job created
  │
  └─ status='queued'     ───▶ Counter.inc()         
                              inference_jobs_total
                              {status="queued"}

Worker picks up task
  │
  ├─ status='processing' ───▶ Gauge.inc()
  │                           active_jobs
  │
  └─ start_time          ───▶ Record start time
                              (for duration calc)

Inference completes
  │
  ├─ duration_seconds    ───▶ Histogram.observe()
  │                           inference_duration_
  │                           seconds
  │
  ├─ total_detections    ───▶ Counter.inc(n)
  │                           detection_count_total
  │
  ├─ status='completed'  ───▶ Counter.inc()
  │                           inference_jobs_total
  │                           {status="completed"}
  │
  └─ active_jobs         ───▶ Gauge.dec()

Queue checked
  │
  └─ queue_length        ───▶ Gauge.set(n)
       from Redis             queue_length
                              {queue="inference"}

System metrics
  │
  ├─ CPU usage           ───▶ Gauge.set(%)
  │                           cpu_usage_percent
  │
  ├─ Memory usage        ───▶ Gauge.set(bytes)
  │                           memory_usage_bytes
  │
  └─ GPU utilization     ───▶ Gauge.set(%)
       (if available)         gpu_utilization_percent


                              ┌──────────────────┐
                              │ /metrics endpoint│
                              │                  │
                              │ Exposes all      │
                              │ collected metrics│
                              │ in Prometheus    │
                              │ text format      │
                              └────────┬─────────┘
                                       │
                                       │ HTTP GET /metrics
                                       │ every 15 seconds
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ Prometheus Server│
                              │                  │
                              │ - Scrapes metrics│
                              │ - Stores in TSDB │
                              │ - Evaluates alerts
                              └────────┬─────────┘
                                       │
                                       │ PromQL queries
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ Grafana Dashboard│
                              │                  │
                              │ - Query          │
                              │   Prometheus API │
                              │ - Render charts  │
                              │ - Display alerts │
                              └──────────────────┘
```

### Windows App Metrics Display

```
┌────────────────────────────────────────────────────────────────────────┐
│          Windows App: Fetching and Displaying Metrics                   │
└────────────────────────────────────────────────────────────────────────┘

USER OPENS                   APP LOGIC                  API/PROMETHEUS
MONITORING TAB               ─────────                  ──────────────
──────────────

Click "Monitoring"
     │
     ▼
┌─────────────────┐
│ Initialize      │
│ monitoring      │
│ dashboard       │
└────────┬────────┘
         │
         │ Start metrics fetching (every 5s)
         │
         ▼
┌─────────────────────────────────────────────────┐
│ Fetch current metrics                           │
│                                                 │
│ GET /api/v1/monitoring/dashboard                │
│                                                 │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
            ┌──────────────────┐
            │ Backend endpoint │      ┌───────────────┐
            │                  │─────▶│ Prometheus    │
            │ Queries:         │      │ HTTP API      │
            │ - queue_length   │      │               │
            │ - active_workers │      │ Execute PromQL│
            │ - job_rate       │      │ queries       │
            │ - avg_duration   │      └───────┬───────┘
            │                  │              │
            │ Aggregates and   │◀─────────────┘
            │ returns JSON     │
            └────────┬─────────┘
                     │
        ◀────────────┘
        │
        ▼
┌─────────────────┐
│ Update UI:      │
│                 │
│ ┌─────────────┐ │
│ │ Queue: 3    │ │
│ │ Workers: 4  │ │
│ │ Avg: 45.2s  │ │
│ └─────────────┘ │
│                 │
│ [Line Chart:    │
│  Job completion │
│  rate over time]│
│                 │
│ [Bar Chart:     │
│  Queue length   │
│  history]       │
└─────────────────┘
```

---

## State Transitions

### Job Status State Machine

```
┌────────────────────────────────────────────────────────────────────────┐
│                      Job Status State Machine                           │
└────────────────────────────────────────────────────────────────────────┘

                              [CREATED]
                                 │
                                 │ POST /predict
                                 │ Job record created
                                 │ Task queued
                                 │
                                 ▼
                              ┌──────┐
                    ┌─────────┤queued├─────────┐
                    │         └──────┘         │
                    │            │              │
                    │            │ Worker       │
                    │            │ picks up     │
                    │            │ task         │
                    │            │              │
        User        │            ▼              │ Timeout
        cancels ────┤      ┌───────────┐       │ (future)
        (future)    │      │processing │       │
                    │      └───────────┘       │
                    │            │              │
                    │            │              │
                    │      ┌─────┴──────┐      │
                    │      │            │      │
                    │      │ Inference  │      │
                    │      │ succeeds   │ fails│
                    │      │            │      │
                    │      ▼            ▼      │
                    │  ┌─────────┐  ┌──────┐  │
                    └─▶│cancelled│  │failed│◀─┘
                       └─────────┘  └──────┘
                          (final)   (final)
                                       │
                           Inference   │
                           succeeds    │
                                       │
                                       ▼
                                  ┌─────────┐
                                  │completed│
                                  └─────────┘
                                    (final)

TRANSITIONS:
──────────────────────────────────────────────────────────────────

State          Event                    Next State      Action
─────          ─────                    ──────────      ──────

[CREATED]      Job record inserted      queued          Celery task created
queued         Worker starts            processing      Update status, started_at
queued         Timeout (5 min)          failed          Mark as failed
queued         User cancels (future)    cancelled       Delete task from queue
processing     Inference succeeds       completed       Save results, update summary
processing     Inference fails          failed          Save error details
processing     Max retries exceeded     failed          Mark permanent failure
processing     User cancels (future)    cancelled       Terminate task
completed      -                        -               Terminal state
failed         -                        -               Terminal state
cancelled      -                        -               Terminal state

TERMINAL STATES (no further transitions):
- completed
- failed
- cancelled
```

---

## Sequence Diagrams

### Complete Upload-to-Results Sequence

```
┌────────────────────────────────────────────────────────────────────────┐
│               Complete Upload-to-Results Sequence Diagram               │
└────────────────────────────────────────────────────────────────────────┘

User    WinApp      API Server     PostgreSQL   Redis    Celery    Storage
────    ──────      ──────────     ──────────   ─────    ──────    ───────

 │         │             │              │          │        │          │
 │ Select  │             │              │          │        │          │
 │ images  │             │              │          │        │          │
 ├────────▶│             │              │          │        │          │
 │         │             │              │          │        │          │
 │         │ POST /upload│              │          │        │          │
 │         ├────────────▶│              │          │        │          │
 │         │             │ Save files   │          │        │          │
 │         │             ├──────────────┼──────────┼────────┼─────────▶│
 │         │             │ Save metadata│          │        │          │
 │         │             ├─────────────▶│          │        │          │
 │         │             │              │          │        │          │
 │         │  upload_id  │              │          │        │          │
 │         │◀────────────┤              │          │        │          │
 │         │             │              │          │        │          │
 │Configure│             │              │          │        │          │
 │ params  │             │              │          │        │          │
 ├────────▶│             │              │          │        │          │
 │         │             │              │          │        │          │
 │         │ POST /predict              │          │        │          │
 │         ├────────────▶│              │          │        │          │
 │         │             │ Create job   │          │        │          │
 │         │             ├─────────────▶│          │        │          │
 │         │             │ Queue task   │          │        │          │
 │         │             ├──────────────┼─────────▶│        │          │
 │         │             │              │          │ Enqueue│          │
 │         │             │              │          ├───────▶│          │
 │         │             │              │          │        │          │
 │         │   job_id    │              │          │        │          │
 │         │◀────────────┤              │          │        │          │
 │         │             │              │          │        │          │
 │         │ GET /status │              │          │        │          │
 │         ├────────────▶│              │          │        │          │
 │         │             │ Check Redis  │          │        │          │
 │         │             ├──────────────┼─────────▶│        │          │
 │         │             │◀─────────────┼──────────┤        │          │
 │         │  queued     │              │          │        │          │
 │         │◀────────────┤              │          │        │          │
 │         │             │              │          │        │          │
 │  Wait   │             │              │          │        │ Worker   │
 │  2s     │             │              │          │        │ picks up │
 │         │             │              │          │        │◀─────────┤
 │         │             │              │          │        │          │
 │         │             │              │          │        │ Update   │
 │         │             │              │          │        │ status   │
 │         │             │              │          │        ├─────────▶│
 │         │             │              │          │        │          │
 │         │             │              │          │        │ Load     │
 │         │             │              │          │        │ model    │
 │         │             │              │          │        │          │
 │         │ GET /status │              │          │        │          │
 │         ├────────────▶│              │          │        │          │
 │         │             │ Check Redis  │          │        │          │
 │         │             ├──────────────┼─────────▶│        │          │
 │         │             │◀─────────────┼──────────┤        │          │
 │         │processing 50%              │          │        │          │
 │         │◀────────────┤              │          │        │          │
 │         │             │              │          │        │ Run      │
 │         │             │              │          │        │ inference│
 │  Wait   │             │              │          │        │          │
 │  5s     │             │              │          │        │ Save     │
 │         │             │              │          │        │ results  │
 │         │             │              │          │        ├─────────▶│
 │         │             │              │          │        │          │
 │         │             │              │          │        │ Mark     │
 │         │             │              │          │        │ complete │
 │         │             │              │          │◀───────┤          │
 │         │             │              │◀─────────┼────────┤          │
 │         │             │              │          │        │          │
 │         │ GET /status │              │          │        │          │
 │         ├────────────▶│              │          │        │          │
 │         │             │ Check Redis  │          │        │          │
 │         │             ├──────────────┼─────────▶│        │          │
 │         │             │◀─────────────┼──────────┤        │          │
 │         │  completed  │              │          │        │          │
 │         │◀────────────┤              │          │        │          │
 │         │             │              │          │        │          │
 │         │ GET /results│              │          │        │          │
 │         ├────────────▶│              │          │        │          │
 │         │             │ Read files   │          │        │          │
 │         │             ├──────────────┼──────────┼────────┼─────────▶│
 │         │             │◀─────────────┼──────────┼────────┼──────────┤
 │         │ predictions │              │          │        │          │
 │         │◀────────────┤              │          │        │          │
 │         │             │              │          │        │          │
 │         │GET /viz     │              │          │        │          │
 │         ├────────────▶│              │          │        │          │
 │         │             │ Read images  │          │        │          │
 │         │             ├──────────────┼──────────┼────────┼─────────▶│
 │         │             │◀─────────────┼──────────┼────────┼──────────┤
 │         │  image URLs │              │          │        │          │
 │         │◀────────────┤              │          │        │          │
 │         │             │              │          │        │          │
 │Display  │             │              │          │        │          │
 │results  │             │              │          │        │          │
 │◀────────┤             │              │          │        │          │
```

---

## Summary

This document provides comprehensive workflow diagrams for all backend API operations:

1. **Complete End-to-End Workflow**: High-level user journey from image selection to results display
2. **File Upload Workflow**: Detailed validation and storage process
3. **Inference Execution Workflow**: Job creation, task queuing, and worker processing
4. **Job Status Polling Workflow**: Client polling loop and status updates
5. **Results Retrieval Workflow**: Fetching predictions and visualizations
6. **Error Handling Workflows**: Client and server-side error recovery strategies
7. **Monitoring Data Flow**: Prometheus metrics collection and display
8. **State Transitions**: Job status state machine and valid transitions
9. **Sequence Diagrams**: Complete interaction sequence between all components

These workflows serve as the specification for implementing the backend API, ensuring consistent behavior, proper error handling, and efficient resource utilization.

---

**Document Status**: Complete ✅  
**Related Documents**:
- [Backend API Architecture](backend_api_architecture.md) - Main API specification
- [Frontend UI Design](frontend_ui_design.md) - Windows app design

**Last Updated**: February 2, 2026  
**Maintained By**: Backend Engineering Team
