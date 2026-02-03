# Prometheus Integration Guide for Neurosymbolic Object Detection

## Table of Contents

1. [Overview](#overview)
2. [Prometheus Basics](#prometheus-basics)
3. [Integration Architecture](#integration-architecture)
4. [Metrics to Track](#metrics-to-track)
5. [Implementation Guide](#implementation-guide)
6. [Configuration](#configuration)
7. [Packaging with Prometheus](#packaging-with-prometheus)
8. [Grafana Dashboards](#grafana-dashboards)
9. [Alerting Rules](#alerting-rules)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## Overview

This guide provides comprehensive instructions for integrating Prometheus monitoring into the Neurosymbolic Object Detection application. Prometheus will collect metrics from training, inference, and symbolic reasoning stages to provide observability into application performance and behavior.

### What is Prometheus?

**Prometheus** is an open-source monitoring and alerting toolkit designed for reliability and scalability:

- **Time-Series Database**: Stores metrics with timestamps
- **Pull-Based Model**: Scrapes metrics from applications
- **Powerful Queries**: PromQL query language for analysis
- **Alerting**: Built-in alert manager for notifications
- **Visualization**: Integrates with Grafana for dashboards

### Why Prometheus for This Application?

1. **ML/AI Monitoring**: Track model performance, training progress
2. **Performance Metrics**: Monitor inference time, GPU utilization
3. **Resource Monitoring**: CPU, memory, disk usage
4. **Pipeline Observability**: Track each pipeline stage
5. **Historical Analysis**: Analyze trends over time
6. **Production Readiness**: Industry-standard monitoring solution

---

## Prometheus Basics

### Core Concepts

#### 1. Metrics Types

**Counter**: Cumulative metric that only increases
```python
# Example: Total predictions made
predictions_total = Counter('predictions_total', 'Total predictions made')
predictions_total.inc()  # Increment by 1
```

**Gauge**: Metric that can go up or down
```python
# Example: Current GPU memory usage
gpu_memory_usage = Gauge('gpu_memory_mb', 'GPU memory usage in MB')
gpu_memory_usage.set(1500)  # Set to 1500 MB
```

**Histogram**: Samples observations and counts them in buckets
```python
# Example: Inference time distribution
inference_duration = Histogram('inference_duration_seconds', 
                               'Time spent on inference')
with inference_duration.time():
    model.predict(image)
```

**Summary**: Similar to histogram but provides quantiles
```python
# Example: mAP score distribution
map_score = Summary('map_score', 'Mean Average Precision')
map_score.observe(0.756)  # Record mAP value
```

#### 2. Labels

Labels add dimensions to metrics:
```python
predictions_total = Counter('predictions_total', 
                           'Total predictions',
                           ['model', 'stage'])
predictions_total.labels(model='yolov11m', stage='inference').inc()
```

#### 3. Scraping

Prometheus periodically "scrapes" (pulls) metrics from application endpoints:
- Application exposes metrics at `/metrics` endpoint
- Prometheus scrapes every N seconds (default: 15s)
- Metrics stored in time-series database

---

## Integration Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Neurosymbolic Application                    │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐        │
│  │  Training   │  │  Inference  │  │  Symbolic    │        │
│  │   Module    │  │   Module    │  │   Pipeline   │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘        │
│         │                 │                 │                 │
│         └────────┬────────┴────────┬────────┘                │
│                  │                  │                         │
│         ┌────────▼──────────────────▼────────┐               │
│         │   Prometheus Client Library        │               │
│         │   (prometheus_client)              │               │
│         └────────┬───────────────────────────┘               │
│                  │                                            │
│         ┌────────▼──────────────┐                            │
│         │  Metrics HTTP Server   │  ← :8000/metrics          │
│         └────────┬───────────────┘                            │
└──────────────────┼──────────────────────────────────────────┘
                   │
                   │ HTTP Scrape (every 15s)
                   │
        ┌──────────▼────────────┐
        │   Prometheus Server   │  ← :9090
        └──────────┬────────────┘
                   │
                   │ Query (PromQL)
                   │
        ┌──────────▼────────────┐
        │   Grafana Dashboard   │  ← :3000
        └───────────────────────┘
```

### Components

1. **Application**: Instruments code with Prometheus metrics
2. **Prometheus Client**: Python library (`prometheus_client`)
3. **Metrics Endpoint**: HTTP server exposing `/metrics`
4. **Prometheus Server**: Scrapes and stores metrics
5. **Grafana**: Visualizes metrics in dashboards

### Integration Points

#### Training Stage (`pipeline/training/training.py`)
- Training loss per epoch
- Validation metrics (mAP, precision, recall)
- Training duration
- GPU utilization
- Model checkpoint events

#### Inference Stage (`pipeline/inference/sahi_yolo_prediction.py`)
- Inference time per image
- Detections per image
- SAHI slice count
- Batch processing throughput

#### Symbolic Pipeline (`pipeline/core/run_pipeline.py`)
- NMS filtering statistics
- Prolog query execution time
- Confidence adjustment distribution
- Pipeline stage duration

#### Knowledge Graph (`pipeline/inference/weighted_kg_sahi.py`)
- Relationship extraction count
- Graph construction time
- Node and edge statistics

---

## Metrics to Track

### 1. Training Metrics

#### Essential Metrics

```python
# Training loss
training_loss = Gauge('training_loss', 'Training loss', ['epoch', 'model'])

# Validation mAP
validation_map = Gauge('validation_map', 'Validation mAP', 
                       ['iou_threshold', 'model'])

# Training duration
training_duration = Histogram('training_duration_seconds',
                             'Training time per epoch',
                             ['model'])

# Learning rate
learning_rate = Gauge('learning_rate', 'Current learning rate', ['model'])

# Batch processing time
batch_time = Histogram('batch_processing_seconds',
                      'Batch processing time',
                      ['model', 'phase'])
```

#### GPU Metrics

```python
# GPU memory usage
gpu_memory_allocated = Gauge('gpu_memory_allocated_mb',
                            'GPU memory allocated in MB')

gpu_memory_reserved = Gauge('gpu_memory_reserved_mb',
                           'GPU memory reserved in MB')

# GPU utilization
gpu_utilization = Gauge('gpu_utilization_percent',
                       'GPU utilization percentage')
```

### 2. Inference Metrics

```python
# Inference time
inference_time = Histogram('inference_time_seconds',
                          'Inference time per image',
                          buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0])

# Detections count
detections_count = Histogram('detections_per_image',
                            'Number of detections per image',
                            buckets=[0, 10, 50, 100, 200, 500, 1000])

# Confidence scores
confidence_distribution = Histogram('confidence_scores',
                                   'Detection confidence distribution',
                                   buckets=[0.1, 0.3, 0.5, 0.7, 0.9, 0.95])

# SAHI slices
sahi_slices = Histogram('sahi_slices_per_image',
                       'SAHI slices per image')

# Images processed
images_processed = Counter('images_processed_total',
                          'Total images processed',
                          ['stage'])
```

### 3. Symbolic Pipeline Metrics

```python
# NMS filtering
nms_filtering_time = Histogram('nms_filtering_seconds',
                               'NMS filtering duration')

detections_before_nms = Gauge('detections_before_nms',
                              'Detections before NMS')

detections_after_nms = Gauge('detections_after_nms',
                             'Detections after NMS')

# Prolog reasoning
prolog_query_time = Histogram('prolog_query_seconds',
                              'Prolog query execution time')

confidence_adjustments = Histogram('confidence_adjustments',
                                   'Confidence adjustment delta',
                                   buckets=[-0.5, -0.2, -0.1, 0, 0.1, 0.2, 0.5])

# Pipeline stages
pipeline_stage_duration = Histogram('pipeline_stage_duration_seconds',
                                    'Pipeline stage duration',
                                    ['stage'])
```

### 4. Knowledge Graph Metrics

```python
# Graph construction
graph_construction_time = Histogram('graph_construction_seconds',
                                    'Graph construction time')

# Graph statistics
graph_nodes = Gauge('graph_nodes_count', 'Number of nodes in graph')
graph_edges = Gauge('graph_edges_count', 'Number of edges in graph')

# Relationship extraction
relationships_extracted = Counter('relationships_extracted_total',
                                 'Total relationships extracted',
                                 ['relationship_type'])
```

### 5. System Metrics

```python
# CPU usage
cpu_usage_percent = Gauge('cpu_usage_percent', 'CPU usage percentage')

# Memory usage
memory_usage_mb = Gauge('memory_usage_mb', 'Memory usage in MB')
memory_available_mb = Gauge('memory_available_mb', 'Available memory in MB')

# Disk I/O
disk_read_mb = Counter('disk_read_mb_total', 'Total disk read in MB')
disk_write_mb = Counter('disk_write_mb_total', 'Total disk write in MB')

# Application uptime
app_uptime_seconds = Gauge('app_uptime_seconds', 'Application uptime')
```

### 6. Error Metrics

```python
# Errors by type
errors_total = Counter('errors_total', 'Total errors', ['error_type', 'stage'])

# Failed operations
failed_predictions = Counter('failed_predictions_total',
                            'Total failed predictions')

failed_prolog_queries = Counter('failed_prolog_queries_total',
                               'Total failed Prolog queries')
```

---

## Implementation Guide

### Step 1: Install Prometheus Client

Add to `requirements.txt`:
```
prometheus_client==0.19.0
```

Install:
```bash
pip install prometheus_client==0.19.0
```

### Step 2: Create Metrics Module

Create `monitoring/metrics/prometheus_metrics.py`:

```python
"""Prometheus metrics definitions for the neurosymbolic pipeline."""

from prometheus_client import Counter, Gauge, Histogram, Summary, Info
import time
import functools


# ============================================================================
# Training Metrics
# ============================================================================

training_loss = Gauge(
    'training_loss',
    'Training loss per epoch',
    ['model', 'epoch']
)

validation_map = Gauge(
    'validation_map',
    'Validation mean Average Precision',
    ['model', 'iou_threshold']
)

training_duration = Histogram(
    'training_duration_seconds',
    'Time spent training per epoch',
    ['model'],
    buckets=[60, 300, 600, 1800, 3600, 7200]  # 1min to 2 hours
)

learning_rate = Gauge(
    'learning_rate',
    'Current learning rate',
    ['model']
)

# ============================================================================
# Inference Metrics
# ============================================================================

inference_time = Histogram(
    'inference_time_seconds',
    'Time spent on inference per image',
    ['model', 'use_sahi'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

detections_count = Histogram(
    'detections_per_image',
    'Number of detections per image',
    ['model'],
    buckets=[0, 10, 25, 50, 100, 200, 500, 1000]
)

images_processed = Counter(
    'images_processed_total',
    'Total number of images processed',
    ['stage', 'status']  # status: success, failed
)

# ============================================================================
# Symbolic Pipeline Metrics
# ============================================================================

nms_filtering_time = Histogram(
    'nms_filtering_seconds',
    'Time spent on NMS filtering',
    buckets=[0.001, 0.01, 0.1, 1.0, 5.0]
)

detections_before_nms = Gauge(
    'detections_before_nms',
    'Number of detections before NMS',
    ['image_id']
)

detections_after_nms = Gauge(
    'detections_after_nms',
    'Number of detections after NMS',
    ['image_id']
)

prolog_query_time = Histogram(
    'prolog_query_seconds',
    'Prolog query execution time',
    buckets=[0.0001, 0.001, 0.01, 0.1, 1.0]
)

confidence_adjustments = Histogram(
    'confidence_adjustment_delta',
    'Confidence score adjustment delta',
    buckets=[-0.5, -0.3, -0.1, -0.05, 0, 0.05, 0.1, 0.3, 0.5]
)

pipeline_stage_duration = Histogram(
    'pipeline_stage_duration_seconds',
    'Duration of each pipeline stage',
    ['stage'],  # preprocess, symbolic, eval
    buckets=[1, 5, 10, 30, 60, 300, 600]
)

# ============================================================================
# Knowledge Graph Metrics
# ============================================================================

graph_construction_time = Histogram(
    'graph_construction_seconds',
    'Time to construct knowledge graph',
    buckets=[0.1, 0.5, 1, 5, 10, 30]
)

graph_nodes = Gauge(
    'graph_nodes_count',
    'Number of nodes in knowledge graph',
    ['image_id']
)

graph_edges = Gauge(
    'graph_edges_count',
    'Number of edges in knowledge graph',
    ['image_id']
)

relationships_extracted = Counter(
    'relationships_extracted_total',
    'Total relationships extracted',
    ['relationship_type']  # spatial_left, spatial_right, etc.
)

# ============================================================================
# System Metrics
# ============================================================================

gpu_memory_allocated = Gauge(
    'gpu_memory_allocated_mb',
    'GPU memory allocated in MB',
    ['device_id']
)

gpu_memory_reserved = Gauge(
    'gpu_memory_reserved_mb',
    'GPU memory reserved in MB',
    ['device_id']
)

gpu_utilization = Gauge(
    'gpu_utilization_percent',
    'GPU utilization percentage',
    ['device_id']
)

cpu_usage = Gauge(
    'cpu_usage_percent',
    'CPU usage percentage'
)

memory_usage = Gauge(
    'memory_usage_mb',
    'Memory usage in MB'
)

# ============================================================================
# Error Metrics
# ============================================================================

errors_total = Counter(
    'errors_total',
    'Total number of errors',
    ['error_type', 'stage']
)

# ============================================================================
# Application Info
# ============================================================================

app_info = Info(
    'app_info',
    'Application information'
)

# Set application metadata
app_info.info({
    'app_name': 'neurosymbolic-object-detection',
    'version': '1.0.0',
    'python_version': '3.10'
})


# ============================================================================
# Decorator Utilities
# ============================================================================

def track_time(metric, labels=None):
    """Decorator to track execution time of functions.
    
    Args:
        metric: Histogram or Summary metric to record time
        labels: Dictionary of label values
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if labels:
                metric_instance = metric.labels(**labels)
            else:
                metric_instance = metric
            
            start = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                metric_instance.observe(duration)
        return wrapper
    return decorator


def count_calls(metric, labels=None):
    """Decorator to count function calls.
    
    Args:
        metric: Counter metric to increment
        labels: Dictionary of label values
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if labels:
                metric_instance = metric.labels(**labels)
            else:
                metric_instance = metric
            
            try:
                result = func(*args, **kwargs)
                metric_instance.inc()
                return result
            except Exception as e:
                # Don't increment counter on exception
                raise
        return wrapper
    return decorator
```

### Step 3: Create Metrics Server

Create `monitoring/metrics/metrics_server.py`:

```python
"""HTTP server for exposing Prometheus metrics."""

from prometheus_client import start_http_server, generate_latest, REGISTRY
from prometheus_client.core import CollectorRegistry
import logging
import threading
import time

logger = logging.getLogger(__name__)


class MetricsServer:
    """HTTP server for Prometheus metrics endpoint."""
    
    def __init__(self, port=8000, addr='0.0.0.0'):
        """Initialize metrics server.
        
        Args:
            port: Port to listen on (default: 8000)
            addr: Address to bind to (default: 0.0.0.0 for all interfaces)
        """
        self.port = port
        self.addr = addr
        self.server_thread = None
        self._started = False
    
    def start(self):
        """Start the metrics server in background thread."""
        if self._started:
            logger.warning("Metrics server already started")
            return
        
        try:
            # Start HTTP server
            start_http_server(port=self.port, addr=self.addr)
            self._started = True
            logger.info(f"Metrics server started on http://{self.addr}:{self.port}/metrics")
        except OSError as e:
            logger.error(f"Failed to start metrics server: {e}")
            raise
    
    def is_running(self):
        """Check if metrics server is running."""
        return self._started


# Global metrics server instance
_metrics_server = None


def get_metrics_server(port=8000, addr='0.0.0.0'):
    """Get or create global metrics server instance.
    
    Args:
        port: Port for metrics server
        addr: Address to bind to
        
    Returns:
        MetricsServer instance
    """
    global _metrics_server
    if _metrics_server is None:
        _metrics_server = MetricsServer(port=port, addr=addr)
    return _metrics_server


def start_metrics_server(port=8000):
    """Convenience function to start metrics server.
    
    Args:
        port: Port to expose metrics on (default: 8000)
    """
    server = get_metrics_server(port=port)
    server.start()


def get_metrics_text():
    """Get current metrics in Prometheus text format.
    
    Returns:
        Metrics as text string
    """
    return generate_latest(REGISTRY).decode('utf-8')
```

### Step 4: Instrument Training Code

Modify `pipeline/training/training.py`:

```python
"""Training script with Prometheus metrics."""

# Add these imports at the top
from monitoring.metrics import prometheus_metrics as pm
from monitoring.metrics.metrics_server import start_metrics_server
import torch

# Start metrics server in main function
def main():
    # ... existing code ...
    
    # Start Prometheus metrics server
    start_metrics_server(port=8000)
    
    # ... rest of training code ...
    
    # Instrument training loop
    for epoch in range(num_epochs):
        # Record learning rate
        pm.learning_rate.labels(model=model_name).set(optimizer.param_groups[0]['lr'])
        
        # Time training epoch
        epoch_start = time.time()
        
        # Training step
        loss = train_one_epoch(model, dataloader, optimizer)
        
        # Record training loss
        pm.training_loss.labels(model=model_name, epoch=str(epoch)).set(loss)
        
        # Record epoch duration
        epoch_duration = time.time() - epoch_start
        pm.training_duration.labels(model=model_name).observe(epoch_duration)
        
        # Validation
        if epoch % val_frequency == 0:
            map_50 = validate(model, val_dataloader)
            pm.validation_map.labels(model=model_name, iou_threshold='0.5').set(map_50)
        
        # Track GPU memory
        if torch.cuda.is_available():
            pm.gpu_memory_allocated.labels(device_id='0').set(
                torch.cuda.memory_allocated() / 1024 / 1024  # Convert to MB
            )
            pm.gpu_memory_reserved.labels(device_id='0').set(
                torch.cuda.memory_reserved() / 1024 / 1024
            )
```

### Step 5: Instrument Inference Code

Modify `pipeline/inference/sahi_yolo_prediction.py`:

```python
"""SAHI prediction with Prometheus metrics."""

from monitoring.metrics import prometheus_metrics as pm

def predict_image(model, image_path):
    """Run inference on single image with metrics."""
    
    # Track inference time
    with pm.inference_time.labels(
        model=model.model_name,
        use_sahi='true'
    ).time():
        results = model.predict(image_path)
    
    # Count detections
    num_detections = len(results.boxes)
    pm.detections_count.labels(model=model.model_name).observe(num_detections)
    
    # Increment processed images
    pm.images_processed.labels(stage='inference', status='success').inc()
    
    return results
```

### Step 6: Instrument Symbolic Pipeline

Modify `pipeline/core/preprocess.py`:

```python
"""NMS preprocessing with metrics."""

from monitoring.metrics import prometheus_metrics as pm

def apply_nms(detections, iou_threshold):
    """Apply NMS with metrics tracking."""
    
    before_count = len(detections)
    pm.detections_before_nms.labels(image_id='current').set(before_count)
    
    # Time NMS operation
    with pm.nms_filtering_time.time():
        filtered = nms_filter(detections, iou_threshold)
    
    after_count = len(filtered)
    pm.detections_after_nms.labels(image_id='current').set(after_count)
    
    return filtered
```

### Step 7: System Metrics Collection

Create `monitoring/metrics/system_metrics.py`:

```python
"""System metrics collector."""

import psutil
import torch
import time
import threading
from monitoring.metrics import prometheus_metrics as pm


class SystemMetricsCollector:
    """Collects system metrics periodically."""
    
    def __init__(self, interval=15):
        """Initialize collector.
        
        Args:
            interval: Collection interval in seconds (default: 15)
        """
        self.interval = interval
        self.running = False
        self.thread = None
    
    def collect_once(self):
        """Collect metrics once."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        pm.cpu_usage.set(cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        pm.memory_usage.set(memory.used / 1024 / 1024)  # MB
        
        # GPU metrics (if available)
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                allocated = torch.cuda.memory_allocated(i) / 1024 / 1024
                reserved = torch.cuda.memory_reserved(i) / 1024 / 1024
                
                pm.gpu_memory_allocated.labels(device_id=str(i)).set(allocated)
                pm.gpu_memory_reserved.labels(device_id=str(i)).set(reserved)
                
                # GPU utilization (requires nvidia-ml-py3)
                try:
                    import pynvml
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    pm.gpu_utilization.labels(device_id=str(i)).set(util.gpu)
                except:
                    pass  # GPU utilization not available
    
    def _collect_loop(self):
        """Background collection loop."""
        while self.running:
            try:
                self.collect_once()
            except Exception as e:
                print(f"Error collecting system metrics: {e}")
            time.sleep(self.interval)
    
    def start(self):
        """Start background collection."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._collect_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop background collection."""
        self.running = False
        if self.thread:
            self.thread.join()


# Global collector instance
_collector = None


def start_system_metrics_collection(interval=15):
    """Start collecting system metrics.
    
    Args:
        interval: Collection interval in seconds
    """
    global _collector
    if _collector is None:
        _collector = SystemMetricsCollector(interval=interval)
    _collector.start()
```

---

## Configuration

### Prometheus Server Configuration

Create `monitoring/prometheus.yml`:

```yaml
# Prometheus configuration file

global:
  scrape_interval: 15s       # How often to scrape targets
  evaluation_interval: 15s   # How often to evaluate rules
  
  external_labels:
    cluster: 'neurosymbolic-app'
    env: 'production'

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
          # - 'alertmanager:9093'

# Load rules once and periodically evaluate them
rule_files:
  - 'alert_rules.yml'

# Scrape configurations
scrape_configs:
  # Neurosymbolic application metrics
  - job_name: 'neurosymbolic-app'
    static_configs:
      - targets: ['localhost:8000']
        labels:
          app: 'neurosymbolic'
          component: 'main'
  
  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  # Node exporter (system metrics)
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
```

### Alert Rules

Create `monitoring/alert_rules.yml`:

```yaml
# Prometheus alerting rules

groups:
  - name: training_alerts
    interval: 30s
    rules:
      - alert: TrainingLossHigh
        expr: training_loss > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Training loss is high"
          description: "Training loss for {{ $labels.model }} is {{ $value }}"
      
      - alert: ValidationMAPLow
        expr: validation_map < 0.3
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Validation mAP is low"
          description: "mAP for {{ $labels.model }} is {{ $value }}"
  
  - name: inference_alerts
    interval: 30s
    rules:
      - alert: InferenceTimeSlow
        expr: histogram_quantile(0.95, inference_time_seconds_bucket) > 5.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Inference time is slow"
          description: "95th percentile inference time is {{ $value }} seconds"
      
      - alert: HighErrorRate
        expr: rate(errors_total[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/second"
  
  - name: system_alerts
    interval: 30s
    rules:
      - alert: HighCPUUsage
        expr: cpu_usage_percent > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is {{ $value }}%"
      
      - alert: HighGPUMemory
        expr: gpu_memory_allocated_mb / gpu_memory_reserved_mb > 0.95
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High GPU memory usage"
          description: "GPU {{ $labels.device_id }} memory usage is {{ $value }}%"
      
      - alert: LowMemory
        expr: memory_available_mb < 1000
        for: 3m
        labels:
          severity: critical
        annotations:
          summary: "Low available memory"
          description: "Only {{ $value }} MB of memory available"
```

---

## Packaging with Prometheus

### Option 1: Embedded Metrics Server (Recommended)

**Best for**: Windows executables where Prometheus server runs separately

#### Advantages
- ✅ Lightweight (only client library bundled)
- ✅ No external Prometheus server in executable
- ✅ Flexible deployment (Prometheus can be anywhere)

#### Implementation
Already shown in previous sections. Application exposes `/metrics` endpoint, separate Prometheus server scrapes it.

#### Packaging Steps

1. **Include client library**:
   ```bash
   pip install prometheus_client==0.19.0
   ```

2. **Add to PyInstaller** (already in `requirements.txt`):
   - Library automatically bundled
   - Metrics endpoint starts on port 8000

3. **Distribute with instructions**:
   - Provide Prometheus server installation guide
   - Include sample `prometheus.yml`

### Option 2: Bundled Prometheus Server

**Best for**: All-in-one deployments, demos

#### Advantages
- ✅ Complete monitoring solution
- ✅ No separate Prometheus installation
- ✅ Ready to use out-of-box

#### Disadvantages
- ❌ Much larger package (~150MB extra)
- ❌ Runs additional process
- ❌ More complex configuration

#### Implementation

Create `monitoring/bundled_prometheus.py`:

```python
"""Manage bundled Prometheus server."""

import subprocess
import os
import sys
from pathlib import Path


class BundledPrometheus:
    """Manages bundled Prometheus server process."""
    
    def __init__(self, config_file='prometheus.yml', data_dir='prometheus_data'):
        self.config_file = config_file
        self.data_dir = data_dir
        self.process = None
    
    def start(self):
        """Start Prometheus server."""
        if sys.platform == 'win32':
            prometheus_exe = 'prometheus.exe'
        else:
            prometheus_exe = 'prometheus'
        
        cmd = [
            prometheus_exe,
            f'--config.file={self.config_file}',
            f'--storage.tsdb.path={self.data_dir}',
            '--web.listen-address=:9090',
        ]
        
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    def stop(self):
        """Stop Prometheus server."""
        if self.process:
            self.process.terminate()
            self.process.wait()
```

#### Bundling Steps

1. **Download Prometheus**:
   - Windows: https://prometheus.io/download/
   - Extract `prometheus.exe`

2. **Add to PyInstaller spec**:
   ```python
   datas = [
       ('prometheus.exe', '.'),
       ('prometheus.yml', '.'),
   ]
   ```

3. **Start in application**:
   ```python
   from monitoring.bundled_prometheus import BundledPrometheus
   
   prom = BundledPrometheus()
   prom.start()
   ```

### Option 3: Docker Container

**Best for**: Server deployments, cloud

#### Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  neurosymbolic-app:
    build: .
    ports:
      - "8000:8000"  # Metrics endpoint
    volumes:
      - ./data:/app/data
      - ./models:/app/models
    environment:
      - PROMETHEUS_PORT=8000
    networks:
      - monitoring
  
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./monitoring/alert_rules.yml:/etc/prometheus/alert_rules.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - monitoring
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    networks:
      - monitoring

networks:
  monitoring:
    driver: bridge

volumes:
  prometheus-data:
  grafana-data:
```

---

## Grafana Dashboards

### Setting Up Grafana

1. **Install Grafana**: https://grafana.com/grafana/download
2. **Access**: http://localhost:3000 (default login: admin/admin)
3. **Add Prometheus datasource**:
   - Configuration → Data Sources → Add data source
   - Select Prometheus
   - URL: http://localhost:9090
   - Save & Test

### Dashboard Configuration

Create `monitoring/grafana/dashboards/neurosymbolic_dashboard.json`:

```json
{
  "dashboard": {
    "title": "Neurosymbolic Object Detection",
    "panels": [
      {
        "title": "Training Loss",
        "targets": [
          {
            "expr": "training_loss",
            "legendFormat": "{{model}} - Epoch {{epoch}}"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Validation mAP",
        "targets": [
          {
            "expr": "validation_map",
            "legendFormat": "{{model}} @ IoU {{iou_threshold}}"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Inference Time (95th percentile)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, inference_time_seconds_bucket)",
            "legendFormat": "{{model}}"
          }
        ],
        "type": "gauge"
      },
      {
        "title": "Images Processed",
        "targets": [
          {
            "expr": "rate(images_processed_total[5m])",
            "legendFormat": "{{stage}}"
          }
        ],
        "type": "graph"
      },
      {
        "title": "GPU Memory Usage",
        "targets": [
          {
            "expr": "gpu_memory_allocated_mb",
            "legendFormat": "GPU {{device_id}}"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(errors_total[5m])",
            "legendFormat": "{{error_type}}"
          }
        ],
        "type": "graph"
      }
    ]
  }
}
```

### Key Dashboard Panels

1. **Training Progress**
   - Training loss over time
   - Validation mAP over time
   - Learning rate schedule

2. **Inference Performance**
   - Inference time percentiles (50th, 95th, 99th)
   - Throughput (images/second)
   - Detections distribution

3. **System Resources**
   - CPU usage
   - Memory usage
   - GPU utilization and memory

4. **Pipeline Metrics**
   - NMS filtering efficiency
   - Prolog query times
   - Stage-wise duration

5. **Error Monitoring**
   - Error rates by type
   - Failed operations count
   - Alert status

---

## Alerting Rules

Configure alerts in `monitoring/alert_rules.yml` (shown in Configuration section).

### Alert Routing

Create `monitoring/alertmanager.yml`:

```yaml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'email-notifications'
  
  routes:
    - match:
        severity: critical
      receiver: 'pager-duty'
      continue: true
    
    - match:
        severity: warning
      receiver: 'email-notifications'

receivers:
  - name: 'email-notifications'
    email_configs:
      - to: 'alerts@example.com'
        from: 'prometheus@example.com'
        smarthost: 'smtp.example.com:587'
        auth_username: 'prometheus@example.com'
        auth_password: 'password'
  
  - name: 'pager-duty'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'
```

---

## Best Practices

### 1. Metric Naming
- Use base unit (seconds, bytes, not milliseconds, megabytes)
- Append unit to metric name (`_seconds`, `_bytes`)
- Use clear, descriptive names
- Follow Prometheus naming conventions

### 2. Label Usage
- Keep cardinality low (don't use unique IDs as labels)
- Use consistent label names across metrics
- Avoid high-cardinality labels (e.g., timestamps, URLs)

### 3. Performance
- Don't create metrics in hot loops
- Use histograms for distributions, not multiple gauges
- Batch metric updates when possible
- Consider metric collection overhead

### 4. Instrumentation
- Instrument at application boundaries (HTTP handlers, function calls)
- Track both successes and failures
- Include context labels (model name, stage)
- Log metric collection errors

### 5. Retention
- Configure appropriate data retention in Prometheus
- Archive important historical data
- Use recording rules for expensive queries

---

## Troubleshooting

### Metrics Not Appearing

**Check**:
1. Metrics server running: http://localhost:8000/metrics
2. Prometheus scraping: Check Prometheus UI → Status → Targets
3. Firewall rules allow port 8000

### High Memory Usage

**Solutions**:
1. Reduce metric cardinality (fewer labels)
2. Decrease scrape frequency
3. Shorten retention period
4. Use recording rules for aggregations

### Slow Queries

**Solutions**:
1. Use recording rules for complex queries
2. Optimize label selection
3. Reduce time range
4. Use `rate()` instead of `increase()` for counters

### Missing System Metrics

**Check**:
1. Install `psutil`: `pip install psutil`
2. For GPU metrics: `pip install pynvml nvidia-ml-py3`
3. Permissions for system information access

---

## Conclusion

Prometheus provides comprehensive monitoring for the Neurosymbolic Object Detection application across all pipeline stages. The client-library approach is recommended for Windows packaging, with a separate Prometheus server installation. For server deployments, use Docker Compose for a complete monitoring stack with Grafana visualization.

**Key Takeaways**:
- ✅ Embed prometheus_client in executable
- ✅ Expose metrics on port 8000
- ✅ Run Prometheus server separately for scraping
- ✅ Use Grafana for visualization
- ✅ Configure alerts for critical metrics
- ✅ Monitor training, inference, and system resources

For Windows packaging, see [WINDOWS_PACKAGING_GUIDE.md](WINDOWS_PACKAGING_GUIDE.md).

For end-user instructions, see [WINDOWS_EXECUTABLE_USER_GUIDE.md](WINDOWS_EXECUTABLE_USER_GUIDE.md).
