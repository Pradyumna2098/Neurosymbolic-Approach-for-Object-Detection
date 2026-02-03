# Backend API Design Summary

**Version:** 1.0  
**Date:** February 2, 2026  
**Status:** Design Specification Complete  

## Executive Summary

This document summarizes the key design decisions, architectural choices, and implementation strategy for the backend API that powers the neurosymbolic object detection prediction automation system.

---

## Design Decisions

### 1. API Architecture: RESTful HTTP/JSON

**Decision**: Use RESTful API over gRPC or GraphQL

**Rationale**:
- **Universal client support**: Works seamlessly with Electron-based Windows application
- **Simple integration**: Standard HTTP/JSON is familiar to all developers
- **Rich tooling**: Extensive ecosystem for documentation (Swagger), testing (Postman), and monitoring
- **Adequate performance**: REST is sufficient for our request-response pattern
- **File handling**: Multipart form data is mature and well-supported

**Trade-offs Considered**:
- gRPC would provide better performance but adds complexity and requires client code generation
- GraphQL would provide flexible queries but is overkill for our straightforward CRUD operations

---

### 2. Backend Framework: FastAPI

**Decision**: Use FastAPI as the web framework

**Rationale**:
- **Async support**: Native async/await for handling concurrent requests efficiently
- **Type safety**: Built-in Pydantic validation reduces bugs and improves developer experience
- **Auto-documentation**: Automatically generates OpenAPI/Swagger documentation
- **Performance**: ASGI-based architecture provides excellent throughput
- **Modern Python**: Leverages Python 3.10+ features (type hints, dataclasses)

**Alternatives Considered**:
- **Flask**: Mature but lacks native async support and automatic API documentation
- **Django REST Framework**: Feature-rich but heavyweight for an API-focused application

---

### 3. Asynchronous Processing: Celery + Redis

**Decision**: Use Celery task queue with Redis broker

**Rationale**:
- **Non-blocking API**: Long-running inference tasks don't block HTTP request handlers
- **Scalability**: Multiple workers can process jobs in parallel
- **Reliability**: Automatic task retries on failure with exponential backoff
- **Monitoring**: Built-in Flower dashboard and Prometheus integration
- **Proven technology**: Battle-tested in production environments

**Why Async is Essential**:
- Model inference can take 30-120 seconds per image
- Client receives immediate job ID (202 Accepted) and polls for completion
- API remains responsive to other requests while inference runs

**Flow**:
```
Client → API (creates job, returns immediately)
       → Celery queue (task enqueued)
       → Worker (picks up task, runs inference)
       → Storage (saves results)
Client polls → API (returns status/results)
```

---

### 4. Storage Architecture: Multi-Tier

**Decision**: Use PostgreSQL for metadata, filesystem/MinIO for files, Redis for cache

| Storage Type | Technology | Use Case |
|--------------|-----------|----------|
| **Metadata** | PostgreSQL | Job status, user info, file metadata |
| **Files** | Filesystem (MVP) / MinIO (Prod) | Uploaded images, predictions, visualizations |
| **Cache** | Redis | Job status cache for fast polling |

**Rationale**:
- **Separation of concerns**: Different storage optimized for different data types
- **Performance**: Redis cache eliminates PostgreSQL load from frequent status polling
- **Scalability**: MinIO provides S3-compatible object storage for production scale
- **Cost**: Local filesystem for MVP reduces infrastructure complexity

---

### 5. API Versioning Strategy

**Decision**: URL path versioning (`/api/v1`, `/api/v2`)

**Rationale**:
- **Explicit**: Version is immediately visible in URL
- **Simple**: No custom headers or query parameters required
- **Cacheable**: Different versions can be cached independently
- **Standard**: Widely adopted pattern

**Example**:
```
/api/v1/inference/predict  (current)
/api/v2/inference/predict  (future, with breaking changes)
```

**Backward Compatibility Policy**:
- Maintain v1 for 12 months after v2 release
- Deprecation notices sent via response headers: `X-API-Deprecation: true`

---

### 6. Monitoring: Prometheus + Grafana

**Decision**: Expose `/metrics` endpoint in Prometheus text format, visualize with Grafana

**Rationale**:
- **Industry standard**: Prometheus is the de facto standard for metrics in cloud-native applications
- **Rich ecosystem**: Extensive integrations, exporters, and alerting rules
- **Time-series data**: Perfect for tracking metrics over time (request rates, latencies, etc.)
- **Pull model**: Prometheus scrapes metrics, reducing application complexity

**Key Metrics Exposed**:
- API request counts and latencies (per endpoint)
- Inference job counts (by status: queued, processing, completed, failed)
- Queue length and worker health
- System resources (CPU, memory, GPU utilization)
- Detection statistics (objects detected by class)

**Windows App Integration**:
- App queries backend aggregation endpoint: `GET /api/v1/monitoring/dashboard`
- Backend fetches metrics from Prometheus and returns JSON
- Avoids client-side PromQL complexity

---

### 7. Error Handling Strategy

**Decision**: Structured error responses with machine-readable codes

**Error Response Format**:
```json
{
  "status": "error",
  "error": {
    "code": "MACHINE_READABLE_CODE",
    "message": "Human-readable description",
    "details": "Additional context",
    "field": "field_name",
    "timestamp": "2026-02-02T18:54:57.324Z",
    "request_id": "req_abc123"
  }
}
```

**Benefits**:
- **Client logic**: Clients can handle errors programmatically based on codes
- **Debugging**: Request ID enables tracing through logs
- **User experience**: Human-readable messages for display
- **Validation**: Field-level errors for form validation

**Retry Strategy**:
- **4xx errors**: Don't retry (client error)
- **5xx errors**: Retry with exponential backoff (server error)
- **Celery tasks**: Retry 3 times with delays: 60s, 300s, 900s

---

### 8. Security Approach

**Phase 1 (MVP)**: No authentication (local deployment only)

**Phase 2 (Production)**:
- **JWT tokens**: Issued upon login, included in `Authorization: Bearer <token>` header
- **Rate limiting**: 100 requests/minute per IP to prevent abuse
- **Input validation**: Strict validation of file formats, sizes, and parameters
- **HTTPS**: Enforce TLS encryption for all API communication
- **CORS**: Whitelist only trusted origins (Windows app)

**File Security**:
- Validate file magic bytes (not just extension)
- Sanitize filenames to prevent path traversal attacks
- Set restrictive file permissions on stored files

---

## Technology Stack Summary

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **API Framework** | FastAPI | 0.100+ | REST API server |
| **Task Queue** | Celery | 5.3+ | Async job processing |
| **Message Broker** | Redis | 7.0+ | Celery broker + cache |
| **Database** | PostgreSQL | 15+ | Metadata storage |
| **Object Storage** | MinIO (S3-compatible) | Latest | File storage (production) |
| **ML Framework** | PyTorch | 2.0+ | Model inference |
| **Object Detection** | Ultralytics YOLO | 8.0+ | Detection pipeline |
| **Monitoring** | Prometheus | 2.40+ | Metrics collection |
| **Visualization** | Grafana | 9.0+ | Dashboards |
| **API Docs** | Swagger UI | Auto | Interactive docs |
| **Python** | 3.10+ | - | Runtime |

---

## System Architecture

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
│                                                                  │
│  Endpoints: /upload, /predict, /status, /results, /metrics     │
└────────────────┬────────────────────────────────────────────────┘
                 │
     ┌───────────┴────────────┐
     │                         │
     ▼                         ▼
┌─────────────────┐   ┌─────────────────┐
│  PostgreSQL     │   │  Redis          │
│  (Metadata)     │   │  (Broker+Cache) │
└─────────────────┘   └────────┬────────┘
                               │
                               │ Task Queue
                               │
                      ┌────────▼────────┐
                      │ Celery Workers  │
                      │ (Inference)     │
                      └────────┬────────┘
                               │
                      ┌────────▼────────┐
                      │ File Storage    │
                      │ (Filesystem/    │
                      │  MinIO)         │
                      └─────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     Monitoring Stack                             │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │ Prometheus   │  │ Grafana      │                            │
│  │ (Metrics)    │◀─│ (Dashboard)  │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## API Endpoints Overview

### Base URL: `http://localhost:8000/api/v1`

| Endpoint | Method | Purpose | Response Time |
|----------|--------|---------|---------------|
| `/inference/upload` | POST | Upload images | < 3s |
| `/inference/predict` | POST | Trigger inference | < 200ms (async) |
| `/jobs/{id}/status` | GET | Check job status | < 100ms |
| `/jobs/{id}/results` | GET | Get predictions (text) | < 500ms |
| `/jobs/{id}/visualization` | GET | Get annotated images | < 500ms |
| `/files/{id}/original` | GET | Serve original image | < 200ms |
| `/files/{id}/annotated` | GET | Serve annotated image | < 200ms |
| `/metrics` | GET | Prometheus metrics | < 100ms |
| `/docs` | GET | Swagger UI | < 100ms |

---

## Key Workflows

### 1. Complete Inference Flow

```
User uploads images
  → POST /upload → Returns upload_id, file_ids
  → Configure parameters
  → POST /predict → Returns job_id (202 Accepted)
  → Poll GET /status → Status: queued → processing → completed
  → GET /results → Prediction labels (YOLO format / JSON)
  → GET /visualization → Annotated images
  → Display in Windows app
```

**Timeline**: 0s (upload) → 1s (predict) → 2-60s (polling) → 60s (results)

### 2. Job Status State Machine

```
[CREATED] → queued → processing → completed (final)
                        ↓
                      failed (final)
```

### 3. Error Handling

- **Client-side**: Retry 5xx errors with exponential backoff, don't retry 4xx
- **Server-side**: Celery retries tasks 3 times, then marks job as failed
- **Monitoring**: Alert on high error rates (>5%) or queue backlog (>20 jobs)

---

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| **API Response Time (p95)** | < 200ms | Excluding inference |
| **File Upload (10MB)** | < 3s | Multipart form data |
| **Inference (single image)** | 30-120s | Depends on image size, SAHI slicing |
| **Status Poll Latency** | < 100ms | Cached in Redis |
| **Concurrent Jobs** | 10+ | Limited by worker count |
| **Throughput** | 100+ images/hour | Single server with 4 workers |

---

## Scalability Considerations

### Horizontal Scaling (Future)

```
                    ┌─── API Server 1
Load Balancer  ──── ├─── API Server 2
                    └─── API Server 3
                           │
                           ▼
                    ┌─── Worker 1
                    ├─── Worker 2
  Shared Services   ├─── Worker 3
  (PostgreSQL,      ├─── Worker 4
   Redis, MinIO)    └─── Worker N
```

**Scaling Strategy**:
1. **Phase 1**: Single server (API + 4 workers) → 100 images/hour
2. **Phase 2**: Multiple API servers + worker pool → 1,000 images/hour
3. **Phase 3**: Kubernetes auto-scaling → 10,000+ images/hour

---

## Security Considerations

### Input Validation
- File format: Only JPEG, PNG, TIFF (validated by magic bytes)
- File size: Maximum 50 MB per file
- Batch size: Maximum 100 files per upload
- Image dimensions: 64x64 to 8192x8192
- Config parameters: Validate ranges (confidence: 0.0-1.0, IoU: 0.0-1.0)

### File Handling
- Sanitize filenames to prevent directory traversal
- Generate unique file IDs (UUIDs)
- Store files outside web root
- Set restrictive permissions (0600)

### Error Messages
- Don't expose internal paths or stack traces
- Use generic error messages for 500 errors
- Log detailed errors server-side only

---

## Deployment Strategy

### Development Environment
```bash
# Start backend services
docker-compose up -d postgres redis

# Start API server
uvicorn main:app --reload

# Start Celery worker
celery -A tasks worker --loglevel=info

# Start Prometheus + Grafana
docker-compose up -d prometheus grafana
```

### Production Environment
- **Containerization**: Docker images for API and workers
- **Orchestration**: Kubernetes for scaling and resilience
- **CI/CD**: GitHub Actions for automated testing and deployment
- **Monitoring**: Prometheus + Grafana + alerting rules

---

## Testing Strategy

### Unit Tests
- Test each endpoint with mocked dependencies
- Test Pydantic models and validation
- Test error handling and edge cases

### Integration Tests
- Test complete upload → predict → status → results flow
- Test Celery task execution with test database
- Test file storage and retrieval

### Load Tests
- Use Locust to simulate 100 concurrent users
- Measure API response times under load
- Identify bottlenecks and optimize

### Contract Tests
- Ensure API responses match OpenAPI specification
- Validate request/response schemas

---

## Documentation Deliverables

1. **[Backend API Architecture](backend_api_architecture.md)** (48+ pages)
   - Complete API specification with endpoints, request/response formats
   - Technology stack justification
   - System architecture diagrams
   - Prometheus integration details
   - Security and performance considerations

2. **[Backend API Workflows](backend_api_workflows.md)** (57+ pages)
   - Detailed workflow diagrams for all operations
   - ASCII flow charts and sequence diagrams
   - Error handling workflows
   - State transition diagrams
   - Data transformation flows

3. **[Backend API Design Summary](backend_api_design_summary.md)** (This document)
   - Executive summary of design decisions
   - Rationale for key architectural choices
   - Technology stack overview
   - Quick reference guide

---

## Integration Points

### Frontend Integration
- **API Client**: Fetch/Axios for HTTP requests
- **State Management**: Redux for job tracking and results caching
- **Polling**: useEffect hook with setInterval for status updates
- **Error Handling**: Display user-friendly error messages based on error codes

### Monitoring Integration
- **Prometheus**: Scrapes `/metrics` endpoint every 15 seconds
- **Grafana**: Queries Prometheus for dashboard visualization
- **Windows App**: Fetches aggregated metrics from `/api/v1/monitoring/dashboard`

### ML Pipeline Integration
- **Model Loading**: Celery worker loads YOLO model on startup
- **SAHI Inference**: Uses ultralytics YOLO with SAHI slicing
- **Symbolic Reasoning**: Applies Prolog rules (if enabled in config)
- **Visualization**: Generates annotated images with bounding boxes

---

## Next Steps

### Immediate (Week 1-2)
1. **Review and Approval**
   - Stakeholder review of design specifications
   - Technical review by backend team
   - Finalize any design changes

2. **Environment Setup**
   - Set up development environment (PostgreSQL, Redis, FastAPI)
   - Configure Docker Compose for local development
   - Initialize project structure and dependencies

### Short-term (Week 3-6)
3. **API Implementation**
   - Implement core endpoints (/upload, /predict, /status, /results)
   - Set up Celery worker and task definitions
   - Implement file storage and retrieval

4. **Testing**
   - Write unit tests for all endpoints
   - Write integration tests for complete workflows
   - Set up CI/CD pipeline

### Mid-term (Week 7-12)
5. **Monitoring Implementation**
   - Instrument code with Prometheus metrics
   - Set up Prometheus server and Grafana dashboards
   - Configure alerting rules

6. **Documentation**
   - Generate OpenAPI/Swagger documentation
   - Write API usage guide for frontend developers
   - Create troubleshooting guide

### Long-term (Month 4+)
7. **Production Deployment**
   - Containerize API and workers
   - Deploy to production environment
   - Set up monitoring and alerting

8. **Optimization**
   - Performance testing and optimization
   - Scale workers based on load
   - Implement caching strategies

---

## Success Criteria

The backend API design is considered complete when:

- ✅ All endpoints are specified with request/response formats
- ✅ Workflow diagrams cover all operations and error scenarios
- ✅ Technology stack is justified with clear rationale
- ✅ System architecture is documented with diagrams
- ✅ Prometheus integration is fully specified
- ✅ Security considerations are addressed
- ✅ Performance targets are defined
- ✅ Testing strategy is outlined
- ✅ Documentation is comprehensive and accessible

**Status**: All criteria met ✅

---

## Conclusion

This backend API design provides a solid foundation for automating the neurosymbolic object detection pipeline. The RESTful architecture with asynchronous task processing ensures scalability and responsiveness, while the comprehensive monitoring integration enables observability and performance tracking.

The design prioritizes:
- **Simplicity**: RESTful API with standard HTTP/JSON
- **Scalability**: Asynchronous processing with Celery workers
- **Reliability**: Robust error handling and task retries
- **Observability**: Comprehensive Prometheus metrics
- **Maintainability**: Clear documentation and design rationale

The specifications are now ready for implementation by the backend development team.

---

**Document Status**: Complete ✅  
**Next Phase**: Implementation Planning and Development Kickoff  
**Related Documents**:
- [Backend API Architecture](backend_api_architecture.md)
- [Backend API Workflows](backend_api_workflows.md)
- [Frontend UI Design](frontend_ui_design.md)

**Last Updated**: February 2, 2026  
**Maintained By**: Backend Engineering Team
