# Backend API Quick Reference

**Version:** 1.0  
**Date:** February 2, 2026  

This is a quick reference guide for navigating the backend API documentation. For complete details, see the full documents.

---

## 📚 Documentation Index

### 1. [Backend API Architecture](backend_api_architecture.md) (48 pages)
**Purpose**: Complete API specification  
**What's Inside**:
- API design justification (REST vs gRPC)
- Technology stack (FastAPI, Celery, Redis, PostgreSQL)
- System architecture diagrams
- Complete endpoint specifications with examples
- Prometheus integration
- Security and performance considerations

**When to Use**: Reference for implementing endpoints or understanding system design

---

### 2. [Backend API Workflows](backend_api_workflows.md) (57 pages)
**Purpose**: Detailed workflow diagrams  
**What's Inside**:
- End-to-end inference workflow
- File upload and validation flow
- Inference execution with Celery
- Job status polling loop
- Results retrieval process
- Error handling at each stage
- Monitoring data flow
- State transition diagrams
- Complete sequence diagrams

**When to Use**: Understanding how components interact or debugging issues

---

### 3. [Backend API Design Summary](backend_api_design_summary.md) (19 pages)
**Purpose**: Executive summary and quick overview  
**What's Inside**:
- Key design decisions with rationale
- Technology stack summary
- API endpoints overview
- Integration points
- Next steps

**When to Use**: Quick reference or stakeholder presentations

---

## 🚀 Quick Start

### For Backend Developers
1. Start with [Design Summary](backend_api_design_summary.md) for overview
2. Read [Architecture](backend_api_architecture.md) sections:
   - API Design Justification
   - Technology Stack
   - API Endpoints Specification
3. Reference [Workflows](backend_api_workflows.md) for implementation details

### For Frontend Developers
1. Review [Architecture](backend_api_architecture.md) sections:
   - API Endpoints Specification (all 6 endpoints)
   - Request/Response Formats
   - Error Handling Strategy
2. Check [Workflows](backend_api_workflows.md) for:
   - Complete End-to-End Workflow
   - Client-side Error Handling

### For Product Managers
1. Read [Design Summary](backend_api_design_summary.md) - complete overview
2. Review [Architecture](backend_api_architecture.md):
   - Overview
   - System Architecture
3. Check [Workflows](backend_api_workflows.md):
   - Complete End-to-End Workflow diagram

---

## 🔍 Find Information Fast

### "How do I upload images?"
→ [Architecture: Endpoint 1 - Upload Image(s)](backend_api_architecture.md#endpoint-1-upload-images)  
→ [Workflows: File Upload Workflow](backend_api_workflows.md#file-upload-workflow)

### "How does inference work?"
→ [Architecture: Endpoint 2 - Trigger Inference](backend_api_architecture.md#endpoint-2-trigger-inference)  
→ [Workflows: Inference Execution Workflow](backend_api_workflows.md#inference-execution-workflow)

### "How do I check job status?"
→ [Architecture: Endpoint 3 - Check Job Status](backend_api_architecture.md#endpoint-3-check-job-status)  
→ [Workflows: Job Status Polling Workflow](backend_api_workflows.md#job-status-polling-workflow)

### "How do I get results?"
→ [Architecture: Endpoint 4 - Get Prediction Results](backend_api_architecture.md#endpoint-4-get-prediction-results-textlabels)  
→ [Architecture: Endpoint 5 - Get Visualization Images](backend_api_architecture.md#endpoint-5-get-visualization-images)  
→ [Workflows: Results Retrieval Workflow](backend_api_workflows.md#results-retrieval-workflow)

### "How does Prometheus integration work?"
→ [Architecture: Prometheus Integration](backend_api_architecture.md#prometheus-integration)  
→ [Workflows: Monitoring Data Flow](backend_api_workflows.md#monitoring-data-flow)

### "How are errors handled?"
→ [Architecture: Error Handling Strategy](backend_api_architecture.md#error-handling-strategy)  
→ [Workflows: Error Handling Workflows](backend_api_workflows.md#error-handling-workflows)

### "Why was REST chosen over gRPC?"
→ [Architecture: API Design Justification](backend_api_architecture.md#api-design-justification)  
→ [Design Summary: API Architecture Decision](backend_api_design_summary.md#1-api-architecture-restful-httpjson)

### "What technology stack is used?"
→ [Architecture: Technology Stack](backend_api_architecture.md#technology-stack)  
→ [Design Summary: Technology Stack Summary](backend_api_design_summary.md#technology-stack-summary)

---

## 📊 API Endpoints At a Glance

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/inference/upload` | POST | Upload images (multipart/form-data) |
| `/api/v1/inference/predict` | POST | Trigger inference (returns job_id) |
| `/api/v1/jobs/{job_id}/status` | GET | Check job status (queued/processing/completed/failed) |
| `/api/v1/jobs/{job_id}/results` | GET | Get predictions (JSON or YOLO format) |
| `/api/v1/jobs/{job_id}/visualization` | GET | Get annotated images (URLs or base64) |
| `/metrics` | GET | Prometheus metrics endpoint |

---

## 🔄 Typical Workflow

```
1. Upload Images
   POST /api/v1/inference/upload
   → Returns: upload_id, file_ids

2. Trigger Inference
   POST /api/v1/inference/predict
   Body: {upload_id, file_ids, config}
   → Returns: job_id (202 Accepted)

3. Poll Status (every 2-5 seconds)
   GET /api/v1/jobs/{job_id}/status
   → Returns: status (queued → processing → completed)

4. Get Results
   GET /api/v1/jobs/{job_id}/results
   → Returns: predictions (JSON)
   
   GET /api/v1/jobs/{job_id}/visualization
   → Returns: image URLs

5. Display in UI
   Fetch images via URLs
   Display bounding boxes and labels
```

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| API Framework | FastAPI |
| Task Queue | Celery |
| Message Broker | Redis |
| Database | PostgreSQL |
| File Storage | Filesystem / MinIO |
| Monitoring | Prometheus + Grafana |
| ML Framework | PyTorch + Ultralytics YOLO |

---

## 🎯 Key Design Decisions

1. **RESTful API**: Universal compatibility, simple integration
2. **Async Processing**: Celery handles long-running inference without blocking
3. **Multi-tier Storage**: PostgreSQL (metadata), filesystem (files), Redis (cache)
4. **Prometheus Monitoring**: Industry standard metrics collection
5. **Structured Errors**: Machine-readable codes for client handling

---

## 📈 Performance Targets

| Metric | Target |
|--------|--------|
| API Response Time (p95) | < 200ms |
| File Upload (10MB) | < 3s |
| Inference (per image) | 30-120s |
| Status Poll Latency | < 100ms |
| Throughput | 100+ images/hour |

---

## 🔐 Security Highlights

- **Input Validation**: File format, size, dimensions
- **Path Sanitization**: Prevent directory traversal
- **Rate Limiting**: 100 requests/minute per IP
- **JWT Authentication**: Phase 2 (production)
- **HTTPS**: Required for production

---

## 📞 Support

For questions or clarifications:
1. Check the full documentation linked above
2. Review workflow diagrams for visual understanding
3. Create a GitHub issue for specific questions

---

**Last Updated**: February 2, 2026  
**Maintained By**: Backend Engineering Team
