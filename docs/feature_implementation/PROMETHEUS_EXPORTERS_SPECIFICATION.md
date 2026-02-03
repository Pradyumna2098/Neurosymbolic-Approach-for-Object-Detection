# Prometheus Metrics Exporters Specification

**Document Version:** 1.0.0  
**Last Updated:** February 2026  
**Status:** Planning Documentation - No Implementation Required

---

## Table of Contents

1. [Overview](#overview)
2. [Export Architecture](#export-architecture)
3. [Prometheus Client Library](#prometheus-client-library)
4. [Metrics Endpoint Specification](#metrics-endpoint-specification)
5. [Implementation Examples](#implementation-examples)
6. [Integration Patterns](#integration-patterns)
7. [Performance Considerations](#performance-considerations)
8. [Security and Access Control](#security-and-access-control)
9. [Testing Metrics Export](#testing-metrics-export)

---

## Overview

This document specifies how metrics will be exported from the Neurosymbolic Object Detection application using the Python `prometheus_client` library. It details endpoint structures, export formats, and implementation patterns for exposing metrics to Prometheus.

### Export Strategy

**Approach**: HTTP Pull Model
- Application exposes metrics via HTTP endpoint
- Prometheus server scrapes metrics at configured intervals
- Standard Prometheus text format
- No external dependencies beyond `prometheus_client`

### Key Components

1. **Metrics Registry**: Central repository for all metrics
2. **Metrics Server**: HTTP server exposing `/metrics` endpoint
3. **Instrumentation Code**: Application code that updates metrics
4. **System Collectors**: Automated collectors for system resources

---

## Export Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Application Components                      │
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐│
│  │ Training │  │Inference │  │ Symbolic │  │  Knowledge  ││
│  │  Stage   │  │  Stage   │  │ Pipeline │  │    Graph    ││
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬──────┘│
│       │             │              │                │        │
│       └─────────────┴──────────────┴────────────────┘        │
│                             │                                 │
│                             ▼                                 │
│                  ┌─────────────────────┐                     │
│                  │  Metrics Registry   │                     │
│                  │ (prometheus_client) │                     │
│                  └──────────┬──────────┘                     │
│                             │                                 │
│                             ▼                                 │
│                  ┌─────────────────────┐                     │
│                  │   Metrics Server    │                     │
│                  │  (HTTP :8000/metrics)│                     │
│                  └──────────┬──────────┘                     │
└─────────────────────────────┼─────────────────────────────────┘
                              │
                              │ HTTP GET
                              ▼
                    ┌──────────────────┐
                    │ Prometheus Server │
                    │   (Scrapes :8000)│
                    └──────────────────┘
```

### Data Flow

1. **Metric Update**: Application code updates metric values
   ```python
   inference_time.labels(model="yolov11m").observe(0.45)
   ```

2. **Registry Storage**: Metrics stored in in-memory registry

3. **Scrape Request**: Prometheus sends HTTP GET to `/metrics`

4. **Metrics Generation**: Registry serializes all metrics to text format

5. **Response**: Application returns metrics in Prometheus format

---

## Prometheus Client Library

### Installation

**File**: `requirements.txt`
```text
prometheus_client==0.19.0
```

**Installation Command**:
```bash
pip install prometheus_client==0.19.0
```

### Core Components

#### 1. Metric Types

```python
from prometheus_client import Counter, Gauge, Histogram, Summary, Info

# Counter - monotonically increasing value
counter = Counter('requests_total', 'Total requests', ['method', 'endpoint'])

# Gauge - value that can go up or down
gauge = Gauge('memory_usage_bytes', 'Memory usage in bytes')

# Histogram - samples observations (e.g., request durations)
histogram = Histogram('request_duration_seconds', 'Request duration',
                     buckets=[0.1, 0.5, 1.0, 2.0, 5.0])

# Summary - similar to histogram, provides quantiles
summary = Summary('response_size_bytes', 'Response size')

# Info - key-value information
info = Info('app_info', 'Application information')
info.info({'version': '1.0.0', 'environment': 'production'})
```

#### 2. Registry

```python
from prometheus_client import CollectorRegistry, REGISTRY

# Use default registry (recommended for single application)
from prometheus_client import Counter
counter = Counter('my_counter', 'My counter')  # Automatically registered

# Or create custom registry
custom_registry = CollectorRegistry()
counter = Counter('my_counter', 'My counter', registry=custom_registry)
```

#### 3. HTTP Server

```python
from prometheus_client import start_http_server

# Start metrics server on port 8000
start_http_server(8000)
```

---

## Metrics Endpoint Specification

### Endpoint Details

**URL**: `http://localhost:8000/metrics`  
**Method**: `GET`  
**Content-Type**: `text/plain; version=0.0.4; charset=utf-8`

### Response Format

Prometheus Text Format (0.0.4):

```text
# HELP training_loss Training loss per epoch
# TYPE training_loss gauge
training_loss{model="yolov11m-obb",epoch="1"} 0.345

# HELP validation_map Validation mean Average Precision
# TYPE validation_map gauge
validation_map{model="yolov11m-obb",iou_threshold="0.5"} 0.756

# HELP inference_time_seconds Time spent on inference per image
# TYPE inference_time_seconds histogram
inference_time_seconds_bucket{model="yolov11m-obb",use_sahi="true",le="0.01"} 0
inference_time_seconds_bucket{model="yolov11m-obb",use_sahi="true",le="0.05"} 5
inference_time_seconds_bucket{model="yolov11m-obb",use_sahi="true",le="0.1"} 25
inference_time_seconds_bucket{model="yolov11m-obb",use_sahi="true",le="0.5"} 150
inference_time_seconds_bucket{model="yolov11m-obb",use_sahi="true",le="+Inf"} 200
inference_time_seconds_sum{model="yolov11m-obb",use_sahi="true"} 45.5
inference_time_seconds_count{model="yolov11m-obb",use_sahi="true"} 200

# HELP images_processed_total Total number of images processed
# TYPE images_processed_total counter
images_processed_total{stage="inference",status="success"} 1523
images_processed_total{stage="inference",status="failed"} 7
```

### Format Specification

#### HELP Line
```text
# HELP <metric_name> <description>
```
- Describes what the metric measures
- One HELP line per metric (not per label combination)

#### TYPE Line
```text
# TYPE <metric_name> <metric_type>
```
- Metric type: `counter`, `gauge`, `histogram`, `summary`, `info`
- One TYPE line per metric

#### Sample Lines
```text
<metric_name>{<label_name>="<label_value>",...} <value> [<timestamp>]
```
- Metric name and labels
- Current value
- Optional timestamp (usually omitted for pull model)

#### Histogram Specifics
Histograms generate multiple time series:
- `<name>_bucket{le="<upper_bound>"}`: Cumulative counters for each bucket
- `<name>_sum`: Total sum of all observations
- `<name>_count`: Total number of observations
- `le="+Inf"` bucket contains all observations

---

## Implementation Examples

### 1. Basic Metrics Module

**File**: `monitoring/metrics/prometheus_metrics.py`

```python
"""Prometheus metrics definitions for neurosymbolic pipeline."""

from prometheus_client import Counter, Gauge, Histogram, Info

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
    'Training time per epoch',
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
    'Inference time per image',
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
    'Total images processed',
    ['stage', 'status']
)

# ============================================================================
# System Metrics
# ============================================================================

gpu_memory_allocated = Gauge(
    'gpu_memory_allocated_bytes',
    'GPU memory allocated',
    ['device_id']
)

cpu_usage = Gauge(
    'cpu_usage_percent',
    'CPU usage percentage'
)

memory_usage = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes'
)

# ============================================================================
# Application Info
# ============================================================================

app_info = Info('app_info', 'Application information')
app_info.info({
    'version': '1.0.0',
    'python_version': '3.10',
    'model': 'yolov11m-obb'
})
```

### 2. Metrics Server Module

**File**: `monitoring/metrics/metrics_server.py`

```python
"""HTTP server for exposing Prometheus metrics."""

from prometheus_client import start_http_server, generate_latest, REGISTRY
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
        self._started = False
    
    def start(self):
        """Start the metrics server in background thread."""
        if self._started:
            logger.warning("Metrics server already started")
            return
        
        try:
            # Start HTTP server (runs in background thread)
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
    
    Useful for debugging or manual inspection.
    
    Returns:
        Metrics as text string
    """
    return generate_latest(REGISTRY).decode('utf-8')


if __name__ == '__main__':
    # Test server
    logging.basicConfig(level=logging.INFO)
    start_metrics_server(port=8000)
    
    print("Metrics server running at http://localhost:8000/metrics")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
```

### 3. System Metrics Collector

**File**: `monitoring/metrics/system_metrics.py`

```python
"""System metrics collector for CPU, memory, and GPU."""

import psutil
import time
import threading
import logging
from typing import Optional

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False

from monitoring.metrics import prometheus_metrics as pm

logger = logging.getLogger(__name__)


class SystemMetricsCollector:
    """Collects system metrics periodically."""
    
    def __init__(self, interval=15):
        """Initialize collector.
        
        Args:
            interval: Collection interval in seconds (default: 15)
        """
        self.interval = interval
        self._thread = None
        self._stop_flag = threading.Event()
        
        # Initialize NVML for GPU metrics
        if PYNVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.gpu_count = pynvml.nvmlDeviceGetCount()
                logger.info(f"Initialized GPU monitoring ({self.gpu_count} GPUs)")
            except Exception as e:
                logger.warning(f"Failed to initialize NVML: {e}")
                PYNVML_AVAILABLE = False
    
    def start(self):
        """Start collecting metrics in background thread."""
        if self._thread is not None:
            logger.warning("System metrics collector already started")
            return
        
        self._stop_flag.clear()
        self._thread = threading.Thread(target=self._collect_loop, daemon=True)
        self._thread.start()
        logger.info(f"System metrics collector started (interval: {self.interval}s)")
    
    def stop(self):
        """Stop collecting metrics."""
        if self._thread is None:
            return
        
        self._stop_flag.set()
        self._thread.join(timeout=self.interval + 5)
        self._thread = None
        logger.info("System metrics collector stopped")
    
    def _collect_loop(self):
        """Main collection loop."""
        while not self._stop_flag.is_set():
            try:
                self._collect_once()
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
            
            self._stop_flag.wait(self.interval)
    
    def _collect_once(self):
        """Collect all system metrics once."""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        pm.cpu_usage.set(cpu_percent)
        
        # Memory metrics
        mem = psutil.virtual_memory()
        pm.memory_usage.set(mem.used)
        pm.memory_available.set(mem.available)
        
        # Disk I/O metrics
        disk_io = psutil.disk_io_counters()
        if disk_io:
            pm.disk_read_total.inc(disk_io.read_bytes)
            pm.disk_write_total.inc(disk_io.write_bytes)
        
        # GPU metrics (PyTorch)
        if TORCH_AVAILABLE and torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                allocated = torch.cuda.memory_allocated(i)
                reserved = torch.cuda.memory_reserved(i)
                pm.gpu_memory_allocated.labels(device_id=str(i)).set(allocated)
                pm.gpu_memory_reserved.labels(device_id=str(i)).set(reserved)
        
        # GPU utilization (NVML)
        if PYNVML_AVAILABLE:
            for i in range(self.gpu_count):
                try:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    pm.gpu_utilization.labels(device_id=str(i)).set(util.gpu)
                except Exception as e:
                    logger.debug(f"Failed to get GPU {i} utilization: {e}")


# Global collector instance
_collector = None


def start_system_metrics_collector(interval=15):
    """Start system metrics collection.
    
    Args:
        interval: Collection interval in seconds
    """
    global _collector
    if _collector is None:
        _collector = SystemMetricsCollector(interval=interval)
    _collector.start()


def stop_system_metrics_collector():
    """Stop system metrics collection."""
    global _collector
    if _collector is not None:
        _collector.stop()
```

### 4. Decorator Utilities

**File**: `monitoring/metrics/decorators.py`

```python
"""Metric decorator utilities."""

import time
import functools
import logging

logger = logging.getLogger(__name__)


def track_time(metric, labels=None):
    """Decorator to track execution time of functions.
    
    Args:
        metric: Histogram or Summary metric to record time
        labels: Dictionary of label values
        
    Example:
        @track_time(inference_time, labels={'model': 'yolov11m'})
        def run_inference(image):
            # ... inference code ...
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


def count_calls(metric, labels=None, count_exceptions=False):
    """Decorator to count function calls.
    
    Args:
        metric: Counter metric to increment
        labels: Dictionary of label values
        count_exceptions: If True, count even if exception raised
        
    Example:
        @count_calls(images_processed, labels={'stage': 'inference'})
        def process_image(image):
            # ... processing code ...
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
                if count_exceptions:
                    metric_instance.inc()
                raise
        return wrapper
    return decorator


def track_exceptions(error_metric, labels=None):
    """Decorator to track exceptions.
    
    Args:
        error_metric: Counter metric for errors
        labels: Dictionary of label values (can include 'error_type')
        
    Example:
        @track_exceptions(errors_total, labels={'stage': 'inference'})
        def risky_operation():
            # ... code that might fail ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Add error type to labels
                error_labels = (labels or {}).copy()
                error_labels['error_type'] = type(e).__name__
                
                error_metric.labels(**error_labels).inc()
                logger.error(f"Exception in {func.__name__}: {e}")
                raise
        return wrapper
    return decorator
```

---

## Integration Patterns

### Pattern 1: Training Script Integration

**File**: `pipeline/training/training.py`

```python
"""Training script with metrics."""

import torch
from ultralytics import YOLO
import time

# Import metrics
from monitoring.metrics import prometheus_metrics as pm
from monitoring.metrics.metrics_server import start_metrics_server
from monitoring.metrics.system_metrics import start_system_metrics_collector


def train_model(config):
    """Train YOLO model with Prometheus metrics."""
    
    # Start metrics server (once at application start)
    start_metrics_server(port=8000)
    
    # Start system metrics collector
    start_system_metrics_collector(interval=15)
    
    # Load model
    model_name = config['model']['variant']
    model = YOLO(model_name)
    
    # Training loop
    num_epochs = config['training']['epochs']
    
    for epoch in range(num_epochs):
        epoch_start = time.time()
        
        # Set learning rate metric
        lr = optimizer.param_groups[0]['lr']
        pm.learning_rate.labels(model=model_name).set(lr)
        
        # Training epoch
        train_loss = train_one_epoch(model, train_loader)
        
        # Record training loss
        pm.training_loss.labels(model=model_name, epoch=str(epoch)).set(train_loss)
        
        # Record epoch duration
        epoch_duration = time.time() - epoch_start
        pm.training_duration.labels(model=model_name).observe(epoch_duration)
        
        # Validation
        if epoch % val_frequency == 0:
            map_50 = validate(model, val_loader)
            pm.validation_map.labels(
                model=model_name,
                iou_threshold='0.5'
            ).set(map_50)
        
        # Update GPU metrics
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / (1024 ** 3)  # GB
            pm.gpu_memory_allocated.labels(device_id='0').set(allocated * 1024 ** 3)


if __name__ == '__main__':
    # Parse config and start training
    train_model(config)
```

### Pattern 2: Inference Integration

**File**: `pipeline/inference/sahi_yolo_prediction.py`

```python
"""SAHI prediction with metrics."""

import time
from pathlib import Path
from ultralytics import YOLO

from monitoring.metrics import prometheus_metrics as pm
from monitoring.metrics.decorators import track_time, count_calls


@count_calls(pm.images_processed, labels={'stage': 'inference', 'status': 'success'})
@track_time(pm.inference_time, labels={'model': 'yolov11m', 'use_sahi': 'true'})
def predict_image(model, image_path):
    """Run inference on single image with metrics."""
    
    # Run prediction
    results = model.predict(image_path)
    
    # Count detections
    num_detections = len(results[0].boxes)
    pm.detections_count.labels(model='yolov11m').observe(num_detections)
    
    # Record confidence scores
    for box in results[0].boxes:
        conf = float(box.conf)
        pm.confidence_scores.labels(model='yolov11m').observe(conf)
    
    return results


def predict_batch(model, image_paths):
    """Predict on batch of images."""
    
    for image_path in image_paths:
        try:
            results = predict_image(model, image_path)
        except Exception as e:
            # Count failed predictions
            pm.images_processed.labels(
                stage='inference',
                status='failed'
            ).inc()
            pm.errors_total.labels(
                error_type=type(e).__name__,
                stage='inference'
            ).inc()
            raise
```

### Pattern 3: Context Manager for Timing

```python
"""Context manager for timing operations."""

import time
from contextlib import contextmanager


@contextmanager
def track_time_context(histogram_metric, labels=None):
    """Context manager to track execution time.
    
    Example:
        with track_time_context(pm.nms_filtering_time):
            apply_nms(detections)
    """
    start = time.time()
    try:
        yield
    finally:
        duration = time.time() - start
        if labels:
            histogram_metric.labels(**labels).observe(duration)
        else:
            histogram_metric.observe(duration)


# Usage in pipeline
def apply_nms(detections, iou_threshold):
    """Apply NMS with timing."""
    
    before_count = len(detections)
    pm.detections_before_nms.labels(image_id='current').set(before_count)
    
    with track_time_context(pm.nms_filtering_time):
        filtered = nms_filter(detections, iou_threshold)
    
    after_count = len(filtered)
    pm.detections_after_nms.labels(image_id='current').set(after_count)
    
    return filtered
```

---

## Performance Considerations

### 1. Minimize Overhead

**Good Practices**:
- Update metrics outside hot loops
- Use labels efficiently (low cardinality)
- Batch metric updates when possible

**Example**:
```python
# Good - update once per image
total_detections = len(all_detections)
pm.detections_count.observe(total_detections)

# Bad - update per detection (hot loop)
for detection in all_detections:
    pm.detections_count.observe(1)  # Too frequent!
```

### 2. Label Cardinality

**Keep cardinality low**:
- ✅ Model names (5-10 values)
- ✅ Pipeline stages (6 values)
- ✅ Status codes (2-3 values)
- ❌ Image IDs (thousands of values)
- ❌ Timestamps (infinite values)

**High cardinality impact**:
- Increases memory usage
- Slows down queries
- Can cause Prometheus to crash

### 3. Scrape Frequency

**Recommendations**:
- Training: 30-60 seconds (slower changes)
- Inference: 10-15 seconds (faster changes)
- System metrics: 15 seconds (standard)

**Configure in Prometheus**:
```yaml
scrape_configs:
  - job_name: 'neurosymbolic'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8000']
```

### 4. Memory Management

**Registry size**: Metrics stored in memory
- Each unique label combination = new time series
- Monitor Prometheus memory usage
- Use recording rules for aggregations

---

## Security and Access Control

### 1. Network Security

**Bind to localhost** (development):
```python
start_http_server(port=8000, addr='127.0.0.1')
```

**Bind to all interfaces** (production):
```python
start_http_server(port=8000, addr='0.0.0.0')
```

### 2. Firewall Rules

**Development**:
- Allow: localhost only
- Block: external access

**Production**:
- Allow: Prometheus server IP
- Block: public internet
- Use VPN or private network

### 3. Authentication

Prometheus Client library doesn't support auth directly.

**Options**:
1. **Network isolation**: Only Prometheus server can reach metrics endpoint
2. **Reverse proxy**: Use nginx/Apache with auth
3. **VPN**: Metrics endpoint only accessible via VPN

**Nginx example**:
```nginx
server {
    listen 8443 ssl;
    server_name metrics.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /metrics {
        auth_basic "Prometheus Metrics";
        auth_basic_user_file /etc/nginx/.htpasswd;
        
        proxy_pass http://localhost:8000/metrics;
    }
}
```

---

## Testing Metrics Export

### 1. Manual Testing

**Test metrics endpoint**:
```bash
# Check if server is running
curl http://localhost:8000/metrics

# Pretty print (requires jq)
curl -s http://localhost:8000/metrics | head -20

# Check specific metric
curl -s http://localhost:8000/metrics | grep "training_loss"
```

### 2. Automated Testing

**File**: `tests/monitoring/test_metrics_export.py`

```python
"""Tests for metrics export."""

import pytest
import requests
from monitoring.metrics.metrics_server import start_metrics_server
from monitoring.metrics import prometheus_metrics as pm


@pytest.fixture
def metrics_server():
    """Start metrics server for testing."""
    start_metrics_server(port=8001)  # Use different port for tests
    yield
    # Server runs in background thread, no cleanup needed


def test_metrics_endpoint_accessible(metrics_server):
    """Test that metrics endpoint is accessible."""
    response = requests.get('http://localhost:8001/metrics')
    assert response.status_code == 200
    assert 'text/plain' in response.headers['Content-Type']


def test_metrics_format(metrics_server):
    """Test that metrics are in Prometheus format."""
    response = requests.get('http://localhost:8001/metrics')
    text = response.text
    
    # Should have HELP lines
    assert '# HELP' in text
    
    # Should have TYPE lines
    assert '# TYPE' in text
    
    # Should have metric values
    assert '\n' in text
    lines = text.split('\n')
    assert len(lines) > 5


def test_metrics_updated(metrics_server):
    """Test that metrics can be updated and exported."""
    # Update a metric
    pm.images_processed.labels(stage='test', status='success').inc()
    
    # Fetch metrics
    response = requests.get('http://localhost:8001/metrics')
    text = response.text
    
    # Check metric appears
    assert 'images_processed_total' in text
    assert 'stage="test"' in text


def test_histogram_buckets(metrics_server):
    """Test that histogram exports buckets correctly."""
    # Record some observations
    pm.inference_time.labels(model='test', use_sahi='false').observe(0.5)
    pm.inference_time.labels(model='test', use_sahi='false').observe(1.0)
    
    response = requests.get('http://localhost:8001/metrics')
    text = response.text
    
    # Should have bucket lines
    assert 'inference_time_seconds_bucket' in text
    assert 'le=' in text  # Bucket labels
    assert 'inference_time_seconds_sum' in text
    assert 'inference_time_seconds_count' in text
```

### 3. Integration Testing

**Test with real Prometheus**:

1. Start application with metrics
2. Start Prometheus pointing to application
3. Query metrics via PromQL
4. Verify data correctness

**Example Prometheus config** (`prometheus.yml`):
```yaml
global:
  scrape_interval: 5s  # Fast for testing

scrape_configs:
  - job_name: 'test-app'
    static_configs:
      - targets: ['localhost:8000']
```

**Test queries**:
```bash
# Query via Prometheus API
curl 'http://localhost:9090/api/v1/query?query=training_loss'

# Check targets status
curl 'http://localhost:9090/api/v1/targets'
```

---

## Next Steps

1. **Implement**: Use code examples to instrument application
2. **Test**: Verify metrics export with manual and automated tests
3. **Deploy**: Set up Prometheus server to scrape metrics
4. **Dashboard**: Create Grafana dashboards (see [PROMETHEUS_DASHBOARD_GUIDE.md](PROMETHEUS_DASHBOARD_GUIDE.md))
5. **Monitor**: Review metrics and adjust as needed

---

## References

- [prometheus_client Documentation](https://github.com/prometheus/client_python)
- [Prometheus Exposition Formats](https://prometheus.io/docs/instrumenting/exposition_formats/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/instrumentation/)
- [PROMETHEUS_METRICS_CATALOG.md](PROMETHEUS_METRICS_CATALOG.md) - Complete metrics reference
- [PROMETHEUS_INTEGRATION_GUIDE.md](PROMETHEUS_INTEGRATION_GUIDE.md) - Integration guide

---

**Document Status**: ✅ Planning Complete - Ready for Implementation  
**Last Review**: February 2026  
**Next Review**: After implementation phase
