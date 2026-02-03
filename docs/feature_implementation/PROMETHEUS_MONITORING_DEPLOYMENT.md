# Prometheus Monitoring Deployment Guide

**Document Version:** 1.0.0  
**Last Updated:** February 2026  
**Status:** Planning Documentation - No Implementation Required

---

## Table of Contents

1. [Overview](#overview)
2. [Deployment Architecture](#deployment-architecture)
3. [User Access Methods](#user-access-methods)
4. [Setup Instructions](#setup-instructions)
5. [Viewing Metrics](#viewing-metrics)
6. [Developer Workflow](#developer-workflow)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)

---

## Overview

This guide describes how users and developers can view and interact with Prometheus metrics from the Neurosymbolic Object Detection application. It covers different deployment scenarios and access methods for various user types.

### Target Audience

| User Type | Primary Interest | Access Method |
|-----------|------------------|---------------|
| **End Users** | Application status, success rates | Embedded GUI widgets |
| **Data Scientists** | Model performance, accuracy metrics | Grafana dashboards |
| **DevOps/ML Engineers** | System health, resource usage | Grafana + Prometheus UI |
| **Developers** | Debugging, detailed metrics | Prometheus UI, API |

---

## Deployment Architecture

### Three Deployment Options

#### Option 1: Standalone Application (Embedded Metrics)

**Best for**: Desktop applications, single-user deployments

```
┌─────────────────────────────────┐
│   Neurosymbolic Application     │
│                                  │
│  ┌───────────────────────────┐  │
│  │  ML Pipeline Components   │  │
│  └───────────┬───────────────┘  │
│              │                   │
│  ┌───────────▼───────────────┐  │
│  │  Prometheus Client        │  │
│  │  (embedded, port 8000)    │  │
│  └───────────┬───────────────┘  │
│              │                   │
│  ┌───────────▼───────────────┐  │
│  │  GUI Monitoring Widgets   │  │
│  │  (reads metrics directly) │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

**Characteristics**:
- Metrics client embedded in application
- Minimal setup required
- GUI reads metrics directly from client
- No external dependencies
- Limited historical data

**Access**: Via application GUI only

#### Option 2: Application + External Prometheus

**Best for**: Development, small team deployments

```
┌─────────────────────────────┐     ┌──────────────────┐
│  Neurosymbolic Application  │     │  Prometheus      │
│                              │     │  Server          │
│  ┌───────────────────────┐  │     │                  │
│  │  ML Pipeline          │  │     │  - Stores data   │
│  └────────┬──────────────┘  │     │  - Queries       │
│           │                  │     │  - Alerts        │
│  ┌────────▼──────────────┐  │     │                  │
│  │ Metrics Client        │◄─┼─────┤  Scrapes :8000   │
│  │ HTTP Server :8000     │  │     │                  │
│  └───────────────────────┘  │     └────────┬─────────┘
└─────────────────────────────┘              │
                                              │
                                  ┌───────────▼──────────┐
                                  │  Grafana Dashboards  │
                                  │  (visualization)     │
                                  └──────────────────────┘
```

**Characteristics**:
- Separate Prometheus server
- Historical data retention (days/weeks)
- Advanced querying capabilities
- Grafana integration
- Requires Prometheus installation

**Access**: Prometheus UI (port 9090), Grafana (port 3000)

#### Option 3: Full Monitoring Stack (Docker)

**Best for**: Production, cloud deployments, CI/CD

```
┌──────────────────────────────────────────────────────────┐
│                    Docker Compose Stack                   │
│                                                            │
│  ┌─────────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │ Application     │  │ Prometheus   │  │  Grafana    │ │
│  │ Container       │  │ Container    │  │  Container  │ │
│  │                 │  │              │  │             │ │
│  │ Metrics :8000   │◄─┤ Scraper      │◄─┤ Dashboards  │ │
│  └─────────────────┘  └──────────────┘  └─────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │           Shared Network: monitoring-net              │ │
│  └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

**Characteristics**:
- Complete monitoring infrastructure
- Easy deployment with docker-compose
- Persistent storage for metrics
- Production-ready configuration
- Scalable architecture

**Access**: Via web browsers, API, or integrated dashboards

---

## User Access Methods

### Method 1: Application GUI (End Users)

**For**: Non-technical users running the desktop application

#### Access Points

1. **Monitoring Panel** in main application window
   - Real-time metrics display
   - Simple statistics (throughput, success rate)
   - Status indicators (green/yellow/red)
   - No Prometheus knowledge required

2. **Progress Bars** during operations
   - Training progress (epochs, loss, mAP)
   - Inference progress (images processed)
   - Pipeline stage indicators

#### Example GUI Layout

```
┌────────────────────────────────────────────────┐
│  Neurosymbolic Object Detection               │
├────────────────────────────────────────────────┤
│  [Upload] [Configure] [Results] [Monitoring]  │
├────────────────────────────────────────────────┤
│                                                 │
│  Current Status: Processing                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━ 67%              │
│                                                 │
│  📊 Quick Stats                                │
│  ├─ Images Processed: 1,234                    │
│  ├─ Success Rate: 98.5%                        │
│  ├─ Avg Processing Time: 0.45s                 │
│  └─ Detections Found: 15,678                   │
│                                                 │
│  🔧 System Status                               │
│  ├─ CPU Usage: ▓▓▓▓▓▓▓░░░ 65%                 │
│  ├─ Memory: ▓▓▓▓▓░░░░░ 47%                    │
│  └─ GPU Usage: ▓▓▓▓▓▓▓▓░░ 82%                 │
│                                                 │
└────────────────────────────────────────────────┘
```

**Implementation**: See [PROMETHEUS_DASHBOARD_GUIDE.md](PROMETHEUS_DASHBOARD_GUIDE.md#gui-integration)

### Method 2: Prometheus Web UI (Developers)

**For**: Developers debugging or exploring metrics

#### Access
- **URL**: http://localhost:9090
- **Features**:
  - Execute PromQL queries
  - View raw metric values
  - Graph time series
  - Check scrape targets
  - View alert status

#### Common Tasks

**1. Check Application Health**
```
Navigate to: Status → Targets
Look for: neurosymbolic job (should be "UP")
```

**2. Query Metrics**
```
Navigate to: Graph
Enter query: training_loss{model="yolov11m-obb"}
Click: Execute
```

**3. View Alerts**
```
Navigate to: Alerts
Check: Active alerts and their status
```

#### Example Queries

```promql
# Current training loss
training_loss

# Inference throughput
rate(images_processed_total[5m])

# GPU memory usage
gpu_memory_allocated_bytes / 1024 / 1024 / 1024
```

### Method 3: Grafana Dashboards (Data Scientists & Engineers)

**For**: Data scientists, ML engineers, ops teams

#### Access
- **URL**: http://localhost:3000
- **Default Login**: admin / admin (change on first login)

#### Pre-built Dashboards

1. **Training Overview**
   - Training loss curves
   - Validation mAP over time
   - Learning rate schedule
   - GPU memory usage

2. **Inference Performance**
   - Latency percentiles (p50, p95, p99)
   - Throughput graphs
   - Detection distributions
   - Success rate gauges

3. **System Resources**
   - CPU/Memory/GPU utilization
   - Disk I/O rates
   - Network traffic (if applicable)

4. **Pipeline Monitoring**
   - Stage durations
   - NMS efficiency
   - Prolog query times
   - Confidence adjustments

5. **Error Dashboard**
   - Error rates by type
   - Failed operations
   - Alert status

#### Interacting with Dashboards

**Time Range Selection**:
- Top-right corner: Select time range
- Options: Last 5m, 15m, 1h, 6h, 24h, 7d, custom
- Auto-refresh: 5s, 10s, 30s, 1m, 5m

**Panel Interactions**:
- Click legend: Toggle series visibility
- Drag to select: Zoom into time range
- Click panel title → View: See query details
- Click panel title → Edit: Customize panel

### Method 4: API Access (Programmatic)

**For**: Custom integrations, automation scripts

#### Prometheus API

**Query Endpoint**:
```bash
curl 'http://localhost:9090/api/v1/query?query=training_loss'
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "resultType": "vector",
    "result": [
      {
        "metric": {
          "model": "yolov11m-obb",
          "epoch": "10"
        },
        "value": [1707858000, "0.345"]
      }
    ]
  }
}
```

**Range Query**:
```bash
curl 'http://localhost:9090/api/v1/query_range?query=training_loss&start=1707854400&end=1707858000&step=60s'
```

#### Python Client Example

```python
import requests

class PrometheusClient:
    def __init__(self, base_url='http://localhost:9090'):
        self.base_url = base_url
    
    def query(self, query):
        """Execute instant query."""
        response = requests.get(
            f'{self.base_url}/api/v1/query',
            params={'query': query}
        )
        return response.json()
    
    def get_training_loss(self, model='yolov11m-obb'):
        """Get current training loss."""
        result = self.query(f'training_loss{{model="{model}"}}')
        if result['data']['result']:
            return float(result['data']['result'][0]['value'][1])
        return None

# Usage
client = PrometheusClient()
loss = client.get_training_loss()
print(f"Current loss: {loss}")
```

---

## Setup Instructions

### Setup 1: Embedded Metrics Only

**For**: Simple desktop deployment

#### Steps

1. **Install prometheus_client**:
   ```bash
   pip install prometheus_client==0.19.0
   ```

2. **Start metrics server in application**:
   ```python
   from monitoring.metrics.metrics_server import start_metrics_server
   
   start_metrics_server(port=8000)
   ```

3. **View metrics**:
   ```bash
   curl http://localhost:8000/metrics
   ```

**No additional setup required!**

### Setup 2: With Prometheus Server

**For**: Development, team environments

#### Prerequisites
- Prometheus server installed
- Application running with metrics enabled

#### Steps

1. **Download Prometheus**:
   - Visit: https://prometheus.io/download/
   - Download appropriate version for your OS
   - Extract to desired location

2. **Configure Prometheus**:
   
   Create `prometheus.yml`:
   ```yaml
   global:
     scrape_interval: 15s
     evaluation_interval: 15s
   
   scrape_configs:
     - job_name: 'neurosymbolic'
       static_configs:
         - targets: ['localhost:8000']
   ```

3. **Start Prometheus**:
   ```bash
   ./prometheus --config.file=prometheus.yml
   ```

4. **Verify**:
   - Open http://localhost:9090
   - Go to Status → Targets
   - Check "neurosymbolic" job is UP

5. **Query metrics**:
   - Go to Graph tab
   - Enter: `training_loss`
   - Click Execute

### Setup 3: Full Stack with Docker

**For**: Production, cloud deployments

#### Prerequisites
- Docker installed
- Docker Compose installed

#### Steps

1. **Create `docker-compose.yml`**:
   
   ```yaml
   version: '3.8'
   
   services:
     app:
       build: .
       ports:
         - "8000:8000"
       volumes:
         - ./data:/app/data
         - ./models:/app/models
       networks:
         - monitoring
     
     prometheus:
       image: prom/prometheus:latest
       ports:
         - "9090:9090"
       volumes:
         - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
         - prometheus-data:/prometheus
       networks:
         - monitoring
     
     grafana:
       image: grafana/grafana:latest
       ports:
         - "3000:3000"
       environment:
         - GF_SECURITY_ADMIN_PASSWORD=admin
       volumes:
         - grafana-data:/var/lib/grafana
       networks:
         - monitoring
   
   networks:
     monitoring:
   
   volumes:
     prometheus-data:
     grafana-data:
   ```

2. **Create Prometheus config** (`monitoring/prometheus.yml`):
   
   ```yaml
   global:
     scrape_interval: 15s
   
   scrape_configs:
     - job_name: 'neurosymbolic'
       static_configs:
         - targets: ['app:8000']
   ```

3. **Start stack**:
   ```bash
   docker-compose up -d
   ```

4. **Access services**:
   - Application: http://localhost:8000
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000

5. **Configure Grafana**:
   - Login: admin / admin
   - Add Prometheus datasource: http://prometheus:9090
   - Import dashboards (see dashboard guide)

---

## Viewing Metrics

### For End Users

#### During Training

**What to watch**:
1. **Training Loss**: Should decrease over time
2. **Validation mAP**: Should increase over time
3. **GPU Usage**: Should be high (70-100%) during training
4. **ETA**: Estimated time remaining

**Example Display**:
```
Training in Progress...

Epoch: 15/100
Loss: 0.345 (▼ improving)
mAP: 0.756 (▲ improving)

GPU Usage: ████████░░ 82%
Memory: ████░░░░░░ 45%

ETA: 2h 35m
```

#### During Inference

**What to watch**:
1. **Images Processed**: Running count
2. **Processing Speed**: Images/second
3. **Success Rate**: Percentage successful
4. **Detections**: Objects found

**Example Display**:
```
Processing Images...

Progress: ███████░░░░░ 654 / 1000
Speed: 2.3 images/sec
Success: 98.5%

Total Detections: 8,456
Avg per Image: 12.9
```

### For Data Scientists

#### Monitoring Training

**Key Metrics**:
1. **Loss Curves**: Check for convergence
2. **Validation mAP**: Track accuracy improvements
3. **Learning Rate**: Verify schedule
4. **Overfitting**: Compare train vs validation

**Grafana Dashboard**: Training Overview

**What to look for**:
- ✅ Steady loss decrease
- ✅ mAP increasing
- ⚠️ Loss plateaus → may need learning rate adjustment
- ⚠️ Validation worse than training → overfitting

#### Analyzing Inference

**Key Metrics**:
1. **Latency Percentiles**: p50, p95, p99
2. **Throughput**: Images/second
3. **Detection Quality**: Confidence distribution
4. **SAHI Impact**: With vs without slicing

**Grafana Dashboard**: Inference Performance

**What to look for**:
- ✅ Consistent latency
- ✅ High throughput
- ⚠️ High tail latency (p99) → optimization needed
- ⚠️ Low confidence scores → model issues

### For DevOps Engineers

#### System Health Monitoring

**Key Metrics**:
1. **Resource Utilization**: CPU, GPU, memory
2. **Error Rates**: Errors per second
3. **Throughput**: Processing rates
4. **Application Uptime**: Service availability

**Grafana Dashboard**: System Resources

**Alert Conditions**:
- 🔴 CPU > 90% for 5min
- 🔴 Memory < 1GB available
- 🔴 GPU memory > 90%
- 🔴 Error rate > 1/sec
- 🔴 Application down

#### Troubleshooting

**Check Targets**:
```
Prometheus UI → Status → Targets
Verify: neurosymbolic job is UP
```

**Check Metrics**:
```
Prometheus UI → Graph
Query: up{job="neurosymbolic"}
Should return: 1
```

**Check Logs**:
```bash
# Application logs
docker logs neurosymbolic-app

# Prometheus logs
docker logs prometheus
```

---

## Developer Workflow

### During Development

1. **Start Application** with metrics:
   ```bash
   python training.py --config config.yaml
   # Metrics available at :8000/metrics
   ```

2. **Verify Metrics Endpoint**:
   ```bash
   curl http://localhost:8000/metrics | grep training_loss
   ```

3. **Start Prometheus** (optional):
   ```bash
   ./prometheus --config.file=prometheus.yml
   ```

4. **Query Metrics**:
   ```bash
   # Via Prometheus API
   curl 'http://localhost:9090/api/v1/query?query=training_loss'
   
   # Or via Prometheus UI
   # Open http://localhost:9090 in browser
   ```

### Testing New Metrics

1. **Add Metric** in `prometheus_metrics.py`:
   ```python
   new_metric = Histogram('new_metric', 'Description', ['label'])
   ```

2. **Update Code** to record metric:
   ```python
   from monitoring.metrics import prometheus_metrics as pm
   pm.new_metric.labels(label='value').observe(123)
   ```

3. **Check Metric Appears**:
   ```bash
   curl http://localhost:8000/metrics | grep new_metric
   ```

4. **Query in Prometheus**:
   ```promql
   new_metric{label="value"}
   ```

### Debugging Metrics Issues

**Metric Not Appearing**:
1. Check metric is registered (imported in metrics module)
2. Verify code is updating metric
3. Check Prometheus scrape config
4. View Prometheus logs for errors

**Wrong Values**:
1. Check label values (case-sensitive)
2. Verify aggregation functions (sum, avg, rate)
3. Check time range in query
4. Inspect raw metric values

---

## Production Deployment

### Deployment Checklist

- [ ] Metrics server starts automatically with application
- [ ] Prometheus configured with correct scrape targets
- [ ] Grafana dashboards imported and configured
- [ ] Alert rules configured and tested
- [ ] Alertmanager set up for notifications
- [ ] Metrics retention policy configured
- [ ] Backup strategy for Prometheus data
- [ ] Monitoring for monitoring (meta-monitoring)
- [ ] Documentation for ops team
- [ ] Runbooks for common alerts

### Configuration Recommendations

**Prometheus**:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

# Data retention
storage:
  tsdb:
    retention.time: 30d  # Keep 30 days
    retention.size: 10GB  # Or 10GB max
```

**Grafana**:
- Enable anonymous access for read-only dashboards (optional)
- Configure SMTP for alert emails
- Set up data source with authentication
- Create organization/teams for access control

### Security Considerations

1. **Network Isolation**:
   - Metrics endpoint on private network only
   - Use firewall rules to restrict access
   - VPN for remote access

2. **Authentication**:
   - Prometheus: Use reverse proxy with auth
   - Grafana: Enable authentication, use strong passwords
   - API: Use API keys for programmatic access

3. **Data Privacy**:
   - Don't log sensitive data in metrics
   - Sanitize labels (no PII)
   - Secure Prometheus data storage

---

## Troubleshooting

### Common Issues

#### Issue: Metrics Endpoint Not Accessible

**Symptoms**:
- `curl http://localhost:8000/metrics` fails
- Prometheus target shows DOWN

**Solutions**:
1. Check application is running
2. Verify metrics server started:
   ```python
   from monitoring.metrics.metrics_server import start_metrics_server
   start_metrics_server(port=8000)
   ```
3. Check firewall allows port 8000
4. Verify correct address (0.0.0.0 vs 127.0.0.1)

#### Issue: No Data in Grafana

**Symptoms**:
- Grafana panels show "No data"
- Metrics appear in Prometheus but not Grafana

**Solutions**:
1. Check Grafana datasource configured correctly
2. Verify Prometheus URL in datasource
3. Test datasource connection (should show green)
4. Check query syntax in panel
5. Verify time range includes data

#### Issue: High Memory Usage

**Symptoms**:
- Prometheus consuming lots of RAM
- System slowing down

**Solutions**:
1. Reduce retention period
2. Decrease scrape frequency
3. Reduce label cardinality
4. Enable query caching
5. Use recording rules for expensive queries

#### Issue: Metrics Not Updating

**Symptoms**:
- Metric values stale or not changing
- Old values persist

**Solutions**:
1. Verify code is actually calling metric updates
2. Check for exceptions in metric update code
3. Ensure metrics server is running
4. Check Prometheus scraping (Status → Targets)
5. Verify scrape interval not too long

---

## Additional Resources

### Documentation
- [PROMETHEUS_METRICS_CATALOG.md](PROMETHEUS_METRICS_CATALOG.md) - Complete metrics reference
- [PROMETHEUS_EXPORTERS_SPECIFICATION.md](PROMETHEUS_EXPORTERS_SPECIFICATION.md) - Implementation guide
- [PROMETHEUS_DASHBOARD_GUIDE.md](PROMETHEUS_DASHBOARD_GUIDE.md) - Query examples and dashboards
- [PROMETHEUS_INTEGRATION_GUIDE.md](PROMETHEUS_INTEGRATION_GUIDE.md) - Detailed integration guide

### External Links
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)

### Support
- **GitHub Issues**: For bugs and feature requests
- **Community Forums**: For general questions
- **Team Slack**: For internal support

---

**Document Status**: ✅ Planning Complete - Ready for Implementation  
**Last Review**: February 2026  
**Next Review**: After production deployment
