# Quick Start Guide

Get started with the Neurosymbolic Object Detection platform in under 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- 8GB RAM minimum (16GB recommended)
- NVIDIA GPU with CUDA support (optional, for training)

## 1. Clone the Repository

```bash
git clone https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection.git
cd Neurosymbolic-Approach-for-Object-Detection
```

## 2. Start the Platform

```bash
# Start all services
docker compose up -d

# Check status
docker compose ps
```

Expected output:
```
NAME                           STATUS   PORTS
neurosymbolic-backend          Up       0.0.0.0:8000->8000/tcp
neurosymbolic-frontend         Up       0.0.0.0:3000->80/tcp
neurosymbolic-prometheus       Up       0.0.0.0:9090->9090/tcp
neurosymbolic-grafana          Up       0.0.0.0:3001->3000/tcp
```

## 3. Access the Services

Open your browser and navigate to:

- **Frontend Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (login: admin/admin)

## 4. Try It Out

### Option A: Using the Web Interface

1. Go to http://localhost:3000
2. Click "Start Training" button
3. Watch real-time metrics in the Dashboard
4. View results in the Results tab

### Option B: Using the API

```bash
# Health check
curl http://localhost:8000/health

# Start a training job
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d '{
    "config_path": "/app/shared/pipeline_local.yaml"
  }'

# Get results (replace JOB_ID with the returned job_id)
curl http://localhost:8000/results/JOB_ID

# List all jobs
curl http://localhost:8000/results
```

### Option C: Using Python

```python
import requests

# Start training
response = requests.post(
    "http://localhost:8000/train",
    json={"config_path": "/app/shared/pipeline_local.yaml"}
)
job_id = response.json()["job_id"]
print(f"Job started: {job_id}")

# Check results
results = requests.get(f"http://localhost:8000/results/{job_id}")
print(results.json())
```

## 5. View Monitoring Data

### Prometheus
1. Go to http://localhost:9090
2. Try these queries:
   ```promql
   rate(train_requests_total[5m])
   histogram_quantile(0.95, rate(train_duration_seconds_bucket[5m]))
   ```

### Grafana
1. Go to http://localhost:3001
2. Login: admin/admin
3. Navigate to Dashboards → Neurosymbolic Pipeline Monitoring
4. Watch real-time metrics as you use the platform

## 6. Stop the Platform

```bash
# Stop all services
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v
```

## Troubleshooting

### Services won't start
```bash
# Check Docker is running
docker ps

# Check logs
docker compose logs -f

# Restart services
docker compose restart
```

### Port already in use
Edit `docker-compose.yml` and change the port mappings:
```yaml
ports:
  - "3001:80"  # Change 3001 to another port
```

### Out of memory
Increase Docker memory limit:
- Docker Desktop → Settings → Resources → Memory

## Next Steps

### For Development
1. Read [CONTRIBUTING.md](CONTRIBUTING.md)
2. Follow [instructions.md](instructions.md) for coding standards
3. Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design

### For Production Deployment
1. Review [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
2. Configure authentication
3. Set up proper secrets management
4. Configure backups

### For ML Pipeline
1. Prepare your dataset (see README.md)
2. Update configs in `shared/` directory
3. Run training with custom parameters

## Common Tasks

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
```

### Restart a Service
```bash
docker compose restart backend
```

### Update Code
```bash
git pull
docker compose down
docker compose up -d --build
```

### Run Tests
```bash
# Backend tests
make test-backend

# All tests
make test
```

### Check API Health
```bash
curl http://localhost:8000/health
```

## Resources

- Full Documentation: [README.md](README.md)
- API Reference: http://localhost:8000/docs
- Contributing Guide: [CONTRIBUTING.md](CONTRIBUTING.md)
- Architecture Overview: [ARCHITECTURE.md](ARCHITECTURE.md)

## Getting Help

- 📖 Read the full documentation
- 💬 Check [GitHub Discussions](https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection/discussions)
- 🐛 Report issues on [GitHub Issues](https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection/issues)

---

**Happy Coding! 🚀**
