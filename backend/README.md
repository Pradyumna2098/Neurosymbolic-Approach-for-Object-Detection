# Backend Subproject

FastAPI-based REST API for the neurosymbolic object detection pipeline.

## Overview

This backend provides a RESTful API for automating object detection inference. The current implementation is a **prototype** using local filesystem storage instead of PostgreSQL and Redis.

## Features

✅ **FastAPI Application** - Modern async Python web framework
✅ **API Versioning** - Endpoints under `/api/v1/`
✅ **Health Check** - Service health monitoring at `/api/v1/health`
✅ **CORS Support** - Configured for Electron desktop applications
✅ **Auto Documentation** - Swagger UI at `/docs`, OpenAPI schema at `/openapi.json`
✅ **Local Storage** - Filesystem-based job tracking and file storage
✅ **Environment Config** - Settings via `.env` file with Pydantic validation
✅ **Test Coverage** - Comprehensive unit tests for all components

## Quick Start

### Installation

```bash
cd backend
pip install -r requirements.txt
```

### Configuration

Copy the example environment file and adjust as needed:

```bash
cp .env.example .env
```

### Running the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **Base URL:** http://localhost:8000
- **API Endpoints:** http://localhost:8000/api/v1/
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json

## API Endpoints

### Root
- `GET /` - API information and endpoint discovery

### Health Check
- `GET /api/v1/health` - Service health status

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application setup
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── health.py    # Health check endpoint
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # Settings and configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── responses.py     # Pydantic response models
│   ├── services/
│   │   └── __init__.py      # Business logic (future)
│   └── storage/
│       ├── __init__.py
│       └── local.py         # Filesystem storage service
├── .env.example             # Environment configuration template
└── requirements.txt         # Python dependencies
```

## Storage Architecture

**Prototype Implementation:**
- Uses local filesystem for all storage
- No database required
- Job status tracked in JSON files

**Storage Directories:**
```
data/
├── uploads/          # Uploaded images
├── jobs/             # Job status JSON files
├── results/          # Prediction results
└── visualizations/   # Annotated images
```

## Development

### Running Tests

```bash
cd ..  # Return to project root
pytest tests/backend/ -v
```

### Code Style

This project follows:
- PEP 8 style guidelines
- Type hints for all functions
- Google-style docstrings
- Async/await patterns for I/O operations

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Web Framework** | FastAPI | 0.109.0 |
| **ASGI Server** | Uvicorn | 0.27.0 |
| **Validation** | Pydantic | 2.5.3 |
| **Config** | python-dotenv | 1.0.0 |
| **Testing** | pytest | 7.4.3 |

## Future Enhancements

The following features are planned for production:

- [ ] **Database Integration** - PostgreSQL for metadata storage
- [ ] **Task Queue** - Celery + Redis for async job processing
- [ ] **Object Storage** - MinIO/S3 for file storage
- [ ] **Authentication** - JWT-based API authentication
- [ ] **Rate Limiting** - Prevent API abuse
- [ ] **Monitoring** - Prometheus metrics endpoint
- [ ] **Inference Endpoints** - Image upload and prediction
- [ ] **Batch Processing** - Multiple image inference
- [ ] **Result Retrieval** - Query and download results

## Related Documentation

- **API Architecture:** `../docs/feature_implementation/backend_api_architecture.md`
- **API Design Summary:** `../docs/feature_implementation/backend_api_design_summary.md`
- **Progress Tracking:** `../docs/feature_implementation_progress/PROGRESS.md`

## Related Subprojects

- **Pipeline** - Core ML pipeline that backend will orchestrate
- **Frontend** - Electron app that consumes this API
- **Monitoring** - Prometheus/Grafana for metrics (future)

## License

See the main project LICENSE file.
