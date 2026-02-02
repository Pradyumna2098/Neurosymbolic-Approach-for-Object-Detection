# Monitoring Setup Guide

This directory contains configuration files for Prometheus and Grafana monitoring.

## Overview

The monitoring stack provides real-time insights into the neurosymbolic pipeline execution:

- **Prometheus**: Collects and stores metrics from the backend API
- **Grafana**: Visualizes metrics through customizable dashboards

## Quick Start

### Using Docker Compose

The easiest way to start monitoring is using docker-compose:

```bash
# From repository root
docker-compose up -d prometheus grafana
```

Services will be available at:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001

### Default Credentials

- **Grafana Username**: `admin`
- **Grafana Password**: `admin` (you'll be prompted to change on first login)

## Available Metrics

The backend exposes the following Prometheus metrics at `/metrics`:

### Request Metrics
- `train_requests_total`: Counter of training requests
- `prediction_requests_total`: Counter of prediction requests

### Duration Metrics (Histograms)
- `train_duration_seconds`: Total training duration
- `preprocessing_duration_seconds`: Preprocessing stage duration
- `inference_duration_seconds`: Inference stage duration
- `evaluation_duration_seconds`: Evaluation stage duration

### Error Metrics
- `pipeline_errors_total`: Counter of pipeline errors

## Grafana Dashboard

### Pre-configured Dashboard

A pre-configured dashboard is included at `grafana-dashboard.json` with:

1. **Training Requests Rate**: Shows requests per second
2. **Training Duration**: p50 and p95 percentiles
3. **Pipeline Errors**: Error rate over time
4. **Stage Durations**: Comparison of preprocessing, inference, and evaluation times
5. **Total Predictions**: Cumulative prediction count
6. **Error Counter**: Total errors with color-coded thresholds

### Importing the Dashboard

The dashboard is automatically provisioned when using docker-compose. To manually import:

1. Open Grafana at http://localhost:3001
2. Login with admin/admin
3. Go to Dashboards → Import
4. Upload `grafana-dashboard.json`

## Configuration Files

### prometheus.yml

Defines Prometheus scraping configuration:

```yaml
scrape_configs:
  - job_name: 'backend-api'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
```

Prometheus scrapes metrics from the backend every 15 seconds (default).

### grafana-datasource.yml

Configures Prometheus as a Grafana data source:

```yaml
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
```

## Custom Metrics

### Adding New Metrics

To add custom metrics to the backend:

```python
from prometheus_client import Counter, Histogram

# Define metric
my_metric = Counter('my_metric_total', 'Description of my metric')

# Increment in your code
my_metric.inc()

# For histograms
my_duration = Histogram('my_duration_seconds', 'Duration of operation')

with my_duration.time():
    # Your operation here
    pass
```

### Querying Metrics

In Prometheus UI (http://localhost:9090):

```promql
# Rate of training requests over 5 minutes
rate(train_requests_total[5m])

# 95th percentile of training duration
histogram_quantile(0.95, rate(train_duration_seconds_bucket[5m]))

# Error rate
rate(pipeline_errors_total[5m])
```

## Alerting

### Setting Up Alerts

Create `prometheus-rules.yml`:

```yaml
groups:
  - name: pipeline_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(pipeline_errors_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 0.1 per second"
```

Add to `prometheus.yml`:

```yaml
rule_files:
  - "prometheus-rules.yml"
```

## Production Considerations

### Data Retention

By default, Prometheus retains data for 15 days. To change:

```yaml
# In docker-compose.yml
command:
  - '--storage.tsdb.retention.time=30d'
```

### Persistent Storage

Metrics are stored in Docker volumes:
- `prometheus-data`: Prometheus time-series data
- `grafana-data`: Grafana dashboards and settings

To backup:

```bash
docker-compose down
docker run --rm -v neurosymbolic_prometheus-data:/data -v $(pwd):/backup busybox tar czf /backup/prometheus-backup.tar.gz /data
```

### Authentication

For production, enable Grafana authentication and configure Prometheus with basic auth:

```yaml
# In prometheus.yml
basic_auth:
  username: admin
  password: secure_password
```

## Troubleshooting

### Metrics Not Showing

1. **Check backend is running**: `curl http://localhost:8000/metrics`
2. **Check Prometheus targets**: Go to http://localhost:9090/targets
3. **Verify scrape config**: Ensure target URL is correct

### Grafana Can't Connect to Prometheus

1. Check both services are running: `docker-compose ps`
2. Verify network connectivity: `docker-compose exec grafana ping prometheus`
3. Check datasource configuration in Grafana

### High Memory Usage

Prometheus can use significant memory with many metrics:

1. Reduce scrape frequency in `prometheus.yml`
2. Reduce retention time
3. Limit metric cardinality (avoid high-cardinality labels)

## Advanced Usage

### Remote Write

To send metrics to external storage:

```yaml
# In prometheus.yml
remote_write:
  - url: "https://prometheus-remote-write-endpoint"
    basic_auth:
      username: user
      password: pass
```

### Service Discovery

For dynamic environments:

```yaml
scrape_configs:
  - job_name: 'backend-api'
    consul_sd_configs:
      - server: 'consul:8500'
```

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)

## Support

For monitoring-related issues:
1. Check this guide first
2. Review Prometheus/Grafana logs: `docker-compose logs prometheus grafana`
3. Open an issue in the repository
