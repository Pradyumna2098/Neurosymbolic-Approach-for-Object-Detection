# Neurosymbolic Approach for Object Detection

[![CI Pipeline](https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection/workflows/CI%20Pipeline/badge.svg)](https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection/actions)

A production-ready mono-repository combining YOLO-based neural detectors with symbolic reasoning and a knowledge-graph layer for explainability and downstream analytics. This repository includes a complete backend API, frontend dashboard, ML pipeline, and monitoring infrastructure.

## 🏗️ Repository Structure

This is a **mono-repository** organized into distinct subprojects:

```
.
├── backend/              # FastAPI backend for pipeline APIs
│   ├── app/             # Application code
│   ├── tests/           # Backend tests
│   ├── Dockerfile       # Backend containerization
│   └── requirements.txt # Backend dependencies
│
├── frontend/            # React-based visualization dashboard
│   ├── src/            # React components and app logic
│   ├── public/         # Static assets
│   ├── Dockerfile      # Frontend containerization
│   └── package.json    # Frontend dependencies
│
├── pipeline/            # Core AI/ML pipeline
│   ├── preprocess.py   # Stage 1: Data preprocessing & NMS
│   ├── symbolic.py     # Stage 2: Symbolic reasoning
│   ├── eval.py         # Stage 3: Model evaluation
│   └── run_pipeline.py # Pipeline orchestrator
│
├── shared/              # Shared configurations (YAML files)
│   └── *.yaml          # Configuration files for different environments
│
├── monitoring/          # Prometheus & Grafana monitoring
│   ├── prometheus.yml         # Prometheus configuration
│   ├── grafana-dashboard.json # Pre-configured dashboard
│   └── grafana-datasource.yml # Grafana data source config
│
├── tests/               # Comprehensive test suite
│   ├── backend/        # Backend API tests
│   ├── frontend/       # Frontend component tests
│   └── pipeline/       # Pipeline unit tests
│
├── docker-compose.yml   # Complete stack orchestration
├── instructions.md      # Development guidelines & best practices
└── README.md           # This file
```

## ✨ Key Features

- **🎯 Neurosymbolic AI Pipeline**: Combines deep learning with symbolic reasoning for explainable object detection
- **🚀 RESTful API**: FastAPI backend for training, inference, and results retrieval
- **📊 Interactive Dashboard**: React-based UI for real-time monitoring and visualization
- **📈 Monitoring & Metrics**: Prometheus metrics collection with Grafana dashboards
- **🐳 Containerized**: Full Docker support with docker-compose orchestration
- **✅ Comprehensive Testing**: Unit and integration tests across all components
- **🔄 CI/CD**: Automated linting, testing, and Docker builds via GitHub Actions

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose**: For containerized deployment
- **Python 3.10+**: For local development
- **Node.js 18+**: For frontend development
- **CUDA-capable GPU**: Strongly recommended for training (optional for inference)

### Option 1: Docker Compose (Recommended)

Run the entire stack with a single command:

```bash
# Clone the repository
git clone https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection.git
cd Neurosymbolic-Approach-for-Object-Detection

# Start all services
docker-compose up -d

# Access the services:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3001 (admin/admin)
```

### Option 2: Local Development

#### Backend Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install system dependencies (Ubuntu/Debian)
sudo apt-get install swi-prolog

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Run the backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Frontend will be available at http://localhost:3000
```

#### Pipeline Setup

```bash
# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run individual pipeline stages
python -m pipeline.preprocess --config shared/pipeline_local.yaml
python -m pipeline.symbolic --config shared/pipeline_local.yaml
python -m pipeline.eval --config shared/pipeline_local.yaml

# Or run the full pipeline
python -m pipeline.run_pipeline --config shared/pipeline_local.yaml
```

## 📚 Documentation

### For Developers

- **[instructions.md](instructions.md)**: Comprehensive guide covering:
  - Python best practices (PEP 8, docstrings, type hints)
  - ML lifecycle guidelines (reproducibility, versioning)
  - SDLC principles (Git workflow, commit conventions)
  - Code review standards

### API Documentation

- **Interactive API Docs**: Visit `http://localhost:8000/docs` when backend is running
- **OpenAPI Spec**: Available at `http://localhost:8000/openapi.json`

### Key API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API health check |
| `/train` | POST | Start a training job |
| `/results/{job_id}` | GET | Get job results and metrics |
| `/results` | GET | List all jobs |
| `/metrics` | GET | Prometheus metrics |

## 🧪 Testing

### Run All Tests

```bash
# Backend tests
pytest tests/backend/ -v --cov=backend

# Pipeline tests
pytest tests/pipeline/ -v --cov=pipeline

# Frontend tests
cd frontend && npm test
```

### Test Coverage

We aim for **80%+ code coverage** across all components. Coverage reports are generated automatically in CI/CD.

## 🔍 Monitoring

### Prometheus Metrics

The backend exposes the following metrics at `/metrics`:

- `train_requests_total`: Total training requests
- `train_duration_seconds`: Training duration histogram
- `prediction_requests_total`: Total prediction requests
- `pipeline_errors_total`: Pipeline error counter
- `preprocessing_duration_seconds`: Preprocessing time
- `inference_duration_seconds`: Inference time
- `evaluation_duration_seconds`: Evaluation time

### Grafana Dashboard

Access Grafana at `http://localhost:3001` (default credentials: admin/admin)

Pre-configured dashboard includes:
- Training request rate
- Duration percentiles (p50, p95)
- Error rate tracking
- Stage-wise performance metrics

## 🔄 CI/CD Pipeline

Our GitHub Actions workflows automatically:

1. **Linting**: Enforce PEP 8 (Python) and Prettier (JavaScript)
2. **Testing**: Run all test suites with coverage reporting
3. **Docker Builds**: Build and validate Docker images
4. **Security**: Dependency vulnerability scanning

Workflows trigger on:
- Push to `main`, `master`, or `develop`
- Pull requests to these branches

## 📦 Dataset Preparation

1. Prepare DOTA-style dataset in YOLO format with `images/` and `labels/` folders
2. Update dataset YAML files in `shared/` directory with your paths
3. Ensure labels use YOLO normalized coordinates

Example config structure:
```yaml
train: /path/to/train/images
val: /path/to/val/images
test: /path/to/test/images
nc: 15  # number of classes
names: ['plane', 'ship', 'storage-tank', ...]
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation
- **Prometheus Client**: Metrics collection
- **Uvicorn**: ASGI server

### Frontend
- **React 18**: UI library
- **Recharts**: Data visualization
- **Axios**: HTTP client

### ML Pipeline
- **PyTorch**: Deep learning framework
- **Ultralytics YOLOv11**: Object detection
- **SAHI**: Sliced inference
- **PySwip**: Prolog integration
- **TorchMetrics**: Evaluation metrics

### Monitoring
- **Prometheus**: Metrics collection
- **Grafana**: Visualization

### DevOps
- **Docker & Docker Compose**: Containerization
- **GitHub Actions**: CI/CD
- **Nginx**: Frontend web server

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Read** [instructions.md](instructions.md) for coding standards
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Make** changes following our guidelines
4. **Test** your changes: Ensure all tests pass
5. **Commit** using conventional commits: `feat: add new feature`
6. **Push** and create a Pull Request

### Code Review Checklist

Before requesting review, ensure:
- [ ] Code follows PEP 8 and project style
- [ ] All functions have docstrings
- [ ] Tests are written and passing (80%+ coverage)
- [ ] Documentation is updated
- [ ] CI/CD pipeline passes
- [ ] No sensitive data in commits

## 📊 Workflow Overview

### Neural Stage
1. Train YOLOv11 OBB detector (`training.py`)
2. Generate high-resolution predictions with SAHI (`src/sahi_yolo_prediction.py`)

### Symbolic Stage
1. Clean predictions with NMS (`pipeline.preprocess`)
2. Apply Prolog-based confidence modifiers (`pipeline.symbolic`)
3. Evaluate with TorchMetrics mAP (`pipeline.eval`)

### Knowledge Graph Stage
Build weighted co-occurrence and spatial-relation graphs (`src/weighted_kg_sahi.py`)

## 🔧 Configuration

Configuration files in `shared/` directory support both Kaggle and local environments:

- `training_*.yaml`: Training configuration
- `pipeline_*.yaml`: Pipeline configuration
- `prediction_*.yaml`: SAHI prediction configuration
- `knowledge_graph_*.yaml`: KG construction configuration

Adjust paths in these files for your environment.

## 🐛 Troubleshooting

### Common Issues

**Missing folders**: Create required directories or update config paths
```bash
mkdir -p /path/to/output/dir
```

**Prolog not found**: Install SWI-Prolog
```bash
# Ubuntu/Debian
sudo apt-get install swi-prolog

# macOS
brew install swi-prolog
```

**GPU not detected**: Verify CUDA installation
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

**Port already in use**: Change ports in `docker-compose.yml`

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This project builds upon:
- **Ultralytics YOLO**: Object detection framework
- **SAHI**: Sliced inference library
- **FastAPI**: Web framework
- **React**: Frontend library

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection/discussions)

---

**Built with ❤️ for Explainable AI**
