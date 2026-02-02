# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              React Frontend (Port 3000)                   │  │
│  │  - Dashboard.js: Real-time training metrics              │  │
│  │  - Results.js: Training results visualization            │  │
│  │  - API Communication via Axios                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND API LAYER                            │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              FastAPI Backend (Port 8000)                  │  │
│  │                                                            │  │
│  │  Endpoints:                                                │  │
│  │  - POST /train: Start training job                        │  │
│  │  - GET  /results/{id}: Get job results                    │  │
│  │  - GET  /results: List all jobs                           │  │
│  │  - GET  /metrics: Prometheus metrics                      │  │
│  │                                                            │  │
│  │  Features:                                                 │  │
│  │  - Background task processing                             │  │
│  │  - Job state management                                    │  │
│  │  - Metrics collection                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Function Calls
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ML PIPELINE LAYER                              │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Neurosymbolic Pipeline                    │  │
│  │                                                            │  │
│  │  Stage 1: Preprocessing (pipeline/preprocess.py)          │  │
│  │  - Load YOLO predictions                                   │  │
│  │  - Apply NMS (Non-Maximum Suppression)                     │  │
│  │  - Clean and filter detections                             │  │
│  │                                                            │  │
│  │  Stage 2: Symbolic Reasoning (pipeline/symbolic.py)       │  │
│  │  - Load Prolog rules                                       │  │
│  │  - Apply confidence modifiers                              │  │
│  │  - Generate explainability reports                         │  │
│  │                                                            │  │
│  │  Stage 3: Evaluation (pipeline/eval.py)                   │  │
│  │  - Compute mAP with TorchMetrics                           │  │
│  │  - Generate performance metrics                            │  │
│  │  - Compare prediction sets                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Training Module (training.py)                 │  │
│  │  - YOLOv11 OBB model training                              │  │
│  │  - GPU-accelerated when available                          │  │
│  │  - Checkpoint management                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         SAHI Inference (src/sahi_yolo_prediction.py)       │  │
│  │  - Sliced inference for large images                       │  │
│  │  - Dense prediction generation                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │    Knowledge Graph (src/weighted_kg_sahi.py)              │  │
│  │  - Spatial relation extraction                             │  │
│  │  - Co-occurrence graph construction                        │  │
│  │  - Prolog fact generation                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Metrics Export
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MONITORING LAYER                               │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            Prometheus (Port 9090)                          │  │
│  │  - Scrapes metrics from backend /metrics endpoint          │  │
│  │  - Time-series data storage                                │  │
│  │  - Query interface (PromQL)                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              │ Data Source                       │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Grafana (Port 3001)                           │  │
│  │  - Pre-configured dashboards                               │  │
│  │  - Real-time metric visualization                          │  │
│  │  - Alerting capabilities                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (React)

**Technology**: React 18, Recharts, Axios

**Responsibilities**:
- User interface for monitoring training jobs
- Real-time data visualization
- Job submission and status tracking
- Results presentation

**Key Files**:
- `frontend/src/App.js`: Main application component
- `frontend/src/components/Dashboard.js`: Training dashboard
- `frontend/src/components/Results.js`: Results visualization

### Backend (FastAPI)

**Technology**: FastAPI, Uvicorn, Pydantic, Prometheus Client

**Responsibilities**:
- RESTful API for pipeline operations
- Job queue management
- Background task processing
- Metrics collection and export

**Key Files**:
- `backend/app/main.py`: Main API application
- `backend/Dockerfile`: Container definition

**Metrics Collected**:
- Request counters (train, predict)
- Duration histograms (train, preprocess, inference, eval)
- Error counters

### Pipeline (Neurosymbolic ML)

**Technology**: PyTorch, Ultralytics YOLO, PySwip, TorchMetrics

**Responsibilities**:
- Neural object detection (YOLO)
- Symbolic reasoning (Prolog)
- Performance evaluation
- Knowledge graph construction

**Key Files**:
- `pipeline/preprocess.py`: NMS and cleaning
- `pipeline/symbolic.py`: Rule-based reasoning
- `pipeline/eval.py`: Metrics computation
- `pipeline/run_pipeline.py`: Orchestrator

### Monitoring (Prometheus + Grafana)

**Technology**: Prometheus, Grafana

**Responsibilities**:
- Metric collection and storage
- Time-series visualization
- Dashboard creation
- Alert management

**Key Files**:
- `monitoring/prometheus.yml`: Scraping configuration
- `monitoring/grafana-dashboard.json`: Dashboard definition
- `monitoring/grafana-datasource.yml`: Data source config

## Data Flow

### Training Flow

1. User clicks "Start Training" in frontend
2. Frontend sends POST request to `/train` endpoint
3. Backend creates job and queues background task
4. Background task executes pipeline stages:
   - Preprocessing: Load and clean predictions
   - Symbolic: Apply Prolog rules
   - Evaluation: Compute metrics
5. Results stored in backend job state
6. Frontend polls `/results/{job_id}` for updates
7. Completed results displayed in dashboard

### Metrics Flow

1. Backend operations increment Prometheus metrics
2. Prometheus scrapes `/metrics` endpoint every 15s
3. Metrics stored in Prometheus time-series database
4. Grafana queries Prometheus for visualization
5. Dashboards update in real-time

## Technology Stack Summary

### Languages
- **Python 3.10+**: Backend, ML pipeline
- **JavaScript (React)**: Frontend
- **Prolog**: Symbolic reasoning rules

### Frameworks & Libraries

**Backend**:
- FastAPI: Web framework
- Pydantic: Data validation
- Uvicorn: ASGI server
- Prometheus Client: Metrics

**ML/AI**:
- PyTorch: Deep learning
- Ultralytics: YOLO implementation
- SAHI: Sliced inference
- TorchMetrics: Evaluation
- PySwip: Prolog integration

**Frontend**:
- React 18: UI framework
- Recharts: Charting library
- Axios: HTTP client

**Infrastructure**:
- Docker: Containerization
- Docker Compose: Orchestration
- Prometheus: Metrics collection
- Grafana: Visualization

### Development Tools
- pytest: Python testing
- Jest: JavaScript testing
- flake8: Python linting
- black: Python formatting
- prettier: JavaScript formatting
- GitHub Actions: CI/CD

## Deployment Architecture

### Docker Compose Setup

```yaml
services:
  backend:    # FastAPI API (port 8000)
  frontend:   # React UI (port 3000)
  prometheus: # Metrics DB (port 9090)
  grafana:    # Dashboards (port 3001)

volumes:
  prometheus-data: # Persistent metrics
  grafana-data:    # Persistent dashboards

networks:
  neurosymbolic-network: # Internal communication
```

### Port Mapping

- **3000**: Frontend (React)
- **8000**: Backend API (FastAPI)
- **9090**: Prometheus
- **3001**: Grafana

## Security Considerations

### Current Implementation
- CORS enabled for development (restrict in production)
- Default Grafana credentials (change in production)
- No authentication on API endpoints (add for production)

### Production Recommendations
1. Enable HTTPS/TLS
2. Implement API authentication (JWT, OAuth)
3. Restrict CORS origins
4. Use secrets management (e.g., Docker secrets)
5. Enable Prometheus basic auth
6. Configure Grafana with proper user roles
7. Regular security scanning

## Scalability Considerations

### Current Limitations
- Single backend instance
- In-memory job state (use Redis/database for production)
- No load balancing

### Scaling Options
1. **Horizontal Scaling**: Multiple backend replicas with load balancer
2. **Job Queue**: Use Celery + Redis for distributed task processing
3. **Database**: PostgreSQL for persistent state
4. **Object Storage**: S3/MinIO for model artifacts
5. **Kubernetes**: Container orchestration for auto-scaling

## Development Workflow

1. **Setup**: `./setup.sh` or `docker-compose up`
2. **Development**: Make changes with hot-reload enabled
3. **Testing**: `make test` or `pytest tests/`
4. **Linting**: `make lint` or `flake8` / `prettier`
5. **Build**: `make docker-build`
6. **Deploy**: `make docker-up`

## Monitoring Metrics

### Key Metrics to Watch

**Performance**:
- Training duration (p50, p95, p99)
- Stage-wise timings
- Request rate

**Reliability**:
- Error rate
- Success rate
- Queue depth

**Resource**:
- Memory usage (container metrics)
- CPU usage
- Disk I/O

## Future Enhancements

### Short Term
- [ ] Add user authentication
- [ ] Implement model versioning
- [ ] Add more comprehensive tests
- [ ] Enhance error handling

### Medium Term
- [ ] Multi-user support
- [ ] Experiment tracking (MLflow integration)
- [ ] Advanced visualization options
- [ ] Model comparison features

### Long Term
- [ ] Distributed training support
- [ ] Auto-scaling infrastructure
- [ ] Advanced monitoring and alerting
- [ ] Production-grade deployment templates
