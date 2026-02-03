# Prometheus Dashboard and Visualization Guide

**Document Version:** 1.0.0  
**Last Updated:** February 2026  
**Status:** Planning Documentation - No Implementation Required

---

## Table of Contents

1. [Overview](#overview)
2. [Dashboard Architecture](#dashboard-architecture)
3. [Prometheus Query Examples](#prometheus-query-examples)
4. [Grafana Dashboard Specifications](#grafana-dashboard-specifications)
5. [GUI Integration](#gui-integration)
6. [Custom Visualizations](#custom-visualizations)
7. [Alerting and Notifications](#alerting-and-notifications)
8. [Query Optimization](#query-optimization)

---

## Overview

This document provides comprehensive guidance on visualizing Prometheus metrics from the Neurosymbolic Object Detection application. It includes Prometheus query examples, Grafana dashboard configurations, and integration patterns for displaying metrics in custom GUIs.

### Visualization Options

| Method | Use Case | Complexity | Real-time |
|--------|----------|------------|-----------|
| **Grafana Dashboards** | Production monitoring, ops teams | Low | Yes |
| **Prometheus UI** | Quick queries, debugging | Low | Yes |
| **Custom GUI Integration** | End-user application | Medium | Yes |
| **Export Reports** | Historical analysis, reporting | Low | No |

---

## Dashboard Architecture

### Three-Tier Monitoring Approach

```
┌───────────────────────────────────────────────────────────────┐
│                    Tier 1: Operational Dashboards              │
│                  (For DevOps/ML Engineers)                     │
├───────────────────────────────────────────────────────────────┤
│  • Real-time system health                                     │
│  • Training progress monitoring                                │
│  • Error rates and alerts                                      │
│  • Resource utilization                                        │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│                    Tier 2: Performance Dashboards              │
│                 (For Data Scientists/Researchers)              │
├───────────────────────────────────────────────────────────────┤
│  • Model accuracy metrics (mAP, precision, recall)             │
│  • Inference latency percentiles                               │
│  • Detection quality distributions                             │
│  • Pipeline stage performance                                  │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│                    Tier 3: Business Dashboards                 │
│                    (For End Users/Managers)                    │
├───────────────────────────────────────────────────────────────┤
│  • Images processed count                                      │
│  • Success/failure rates                                       │
│  • Average processing time                                     │
│  • Simple status indicators                                    │
└───────────────────────────────────────────────────────────────┘
```

---

## Prometheus Query Examples

### Basic Query Syntax

```promql
# Instant query - current value
metric_name{label="value"}

# Range query - over time period
metric_name{label="value"}[5m]

# Aggregation
sum(metric_name) by (label)

# Rate calculation (for counters)
rate(counter_metric_total[5m])
```

### Training Metrics Queries

#### Current Training Loss
```promql
# Latest training loss for a specific model
training_loss{model="yolov11m-obb", epoch=~".+"}

# Training loss over time
training_loss{model="yolov11m-obb"}[1h]

# Average training loss across all models
avg(training_loss)
```

#### Validation mAP
```promql
# Current validation mAP at IoU 0.5
validation_map{model="yolov11m-obb", iou_threshold="0.5"}

# mAP improvement over time
delta(validation_map{iou_threshold="0.5"}[1h])

# Compare mAP across different IoU thresholds
validation_map{model="yolov11m-obb"}
```

#### Learning Rate Schedule
```promql
# Current learning rate
learning_rate{model="yolov11m-obb"}

# Learning rate changes
changes(learning_rate{model="yolov11m-obb"}[1h])
```

#### Training Duration
```promql
# Average epoch duration (minutes)
avg(training_duration_seconds{model="yolov11m-obb"}) / 60

# 95th percentile epoch duration
histogram_quantile(0.95, training_duration_seconds_bucket{model="yolov11m-obb"})

# Total training time
sum(training_duration_seconds{model="yolov11m-obb"})
```

### Inference Metrics Queries

#### Inference Latency
```promql
# Median inference time (50th percentile)
histogram_quantile(0.5, 
  sum(rate(inference_time_seconds_bucket{use_sahi="true"}[5m])) by (le)
)

# 95th percentile inference time
histogram_quantile(0.95, 
  sum(rate(inference_time_seconds_bucket{use_sahi="true"}[5m])) by (le)
)

# 99th percentile (tail latency)
histogram_quantile(0.99, 
  sum(rate(inference_time_seconds_bucket{use_sahi="true"}[5m])) by (le)
)

# Average inference time
rate(inference_time_seconds_sum[5m]) / rate(inference_time_seconds_count[5m])

# Compare SAHI vs non-SAHI
rate(inference_time_seconds_sum[5m]) by (use_sahi) / 
rate(inference_time_seconds_count[5m]) by (use_sahi)
```

#### Throughput
```promql
# Images processed per second (successful)
rate(images_processed_total{stage="inference", status="success"}[5m])

# Total images processed today
increase(images_processed_total{stage="inference", status="success"}[24h])

# Processing rate by stage
rate(images_processed_total[5m]) by (stage)
```

#### Detection Quality
```promql
# Average detections per image
rate(detections_per_image_sum[5m]) / rate(detections_per_image_count[5m])

# Median detection count
histogram_quantile(0.5, sum(rate(detections_per_image_bucket[5m])) by (le))

# Images with high detection counts (>100 detections)
sum(detections_per_image_bucket{le="100"}) - 
sum(detections_per_image_bucket{le="200"})
```

#### Confidence Distribution
```promql
# Average confidence score
rate(confidence_scores_sum[5m]) / rate(confidence_scores_count[5m])

# High-confidence detections (>0.9)
rate(confidence_scores_bucket{le="0.9"}[5m])

# Confidence score quantiles
histogram_quantile(0.9, sum(rate(confidence_scores_bucket[5m])) by (le))
```

### Pipeline Metrics Queries

#### NMS Efficiency
```promql
# NMS filtering rate (detections kept)
100 * (detections_after_nms / detections_before_nms)

# Average NMS filtering time
rate(nms_filtering_seconds_sum[5m]) / rate(nms_filtering_seconds_count[5m])

# 95th percentile NMS time
histogram_quantile(0.95, rate(nms_filtering_seconds_bucket[5m]))

# Detections filtered by NMS (%)
100 * (1 - detections_after_nms / detections_before_nms)
```

#### Prolog Reasoning
```promql
# Average Prolog query time
rate(prolog_query_seconds_sum{query_type="adjust_confidence"}[5m]) / 
rate(prolog_query_seconds_count{query_type="adjust_confidence"}[5m])

# Prolog queries per second
rate(prolog_query_seconds_count[5m])

# Failed Prolog queries
rate(failed_prolog_queries_total[5m])

# Prolog failure rate
rate(failed_prolog_queries_total[5m]) / rate(prolog_query_seconds_count[5m])
```

#### Confidence Adjustments
```promql
# Average confidence adjustment
rate(confidence_adjustment_delta_sum[5m]) / 
rate(confidence_adjustment_delta_count[5m])

# Positive adjustments (increased confidence)
sum(confidence_adjustment_delta_bucket{le="0"}) by (le)

# Large adjustments (|delta| > 0.2)
rate(confidence_adjustment_delta_bucket{le="-0.2"}[5m]) + 
rate(confidence_adjustment_delta_bucket{le="0.2"}[5m])
```

#### Pipeline Stages
```promql
# Average stage duration
avg(pipeline_stage_duration_seconds) by (stage)

# Total pipeline time
sum(pipeline_stage_duration_seconds)

# Slowest stage
max(pipeline_stage_duration_seconds) by (stage)

# Stage duration 95th percentile
histogram_quantile(0.95, 
  sum(rate(pipeline_stage_duration_seconds_bucket[5m])) by (stage, le)
)
```

### Knowledge Graph Queries

#### Graph Construction
```promql
# Average graph construction time
rate(graph_construction_seconds_sum[5m]) / 
rate(graph_construction_seconds_count[5m])

# Average graph size (nodes)
avg(graph_nodes_count)

# Average graph density (edges per node)
avg(graph_edges_count / graph_nodes_count)

# Large graphs (>100 nodes)
count(graph_nodes_count > 100)
```

#### Relationships
```promql
# Relationships extracted per second
rate(relationships_extracted_total[5m])

# Most common relationship types
topk(5, sum(rate(relationships_extracted_total[5m])) by (relationship_type))

# Spatial relationships breakdown
sum(spatial_relationships_total) by (spatial_type)

# Relationship extraction rate
rate(relationships_extracted_total[5m]) by (relationship_type)
```

### System Metrics Queries

#### CPU and Memory
```promql
# Current CPU usage
cpu_usage_percent

# Average CPU usage over 5 minutes
avg_over_time(cpu_usage_percent[5m])

# Memory usage (GB)
memory_usage_bytes / 1024 / 1024 / 1024

# Memory usage percentage
100 * (memory_usage_bytes / (memory_usage_bytes + memory_available_bytes))

# Available memory (GB)
memory_available_bytes / 1024 / 1024 / 1024
```

#### GPU Metrics
```promql
# GPU memory usage by device (GB)
gpu_memory_allocated_bytes / 1024 / 1024 / 1024

# GPU memory utilization (%)
100 * (gpu_memory_allocated_bytes / gpu_memory_reserved_bytes)

# GPU compute utilization
gpu_utilization_percent{device_id="0"}

# Total GPU memory across all devices (GB)
sum(gpu_memory_allocated_bytes) / 1024 / 1024 / 1024
```

#### Disk I/O
```promql
# Disk read rate (MB/s)
rate(disk_read_bytes_total[5m]) / 1024 / 1024

# Disk write rate (MB/s)
rate(disk_write_bytes_total[5m]) / 1024 / 1024

# Total I/O (read + write) MB/s
(rate(disk_read_bytes_total[5m]) + rate(disk_write_bytes_total[5m])) / 1024 / 1024

# Disk write to read ratio
rate(disk_write_bytes_total[5m]) / rate(disk_read_bytes_total[5m])
```

### Error and Health Queries

#### Error Rates
```promql
# Total error rate
rate(errors_total[5m])

# Errors by type
sum(rate(errors_total[5m])) by (error_type)

# Errors by stage
sum(rate(errors_total[5m])) by (stage)

# Error spike detection (>10 errors/min)
rate(errors_total[5m]) > 10
```

#### Success Rates
```promql
# Overall success rate (%)
100 * (
  rate(images_processed_total{status="success"}[5m]) / 
  rate(images_processed_total[5m])
)

# Failed predictions rate
rate(failed_predictions_total[5m])

# Failure percentage
100 * (
  rate(images_processed_total{status="failed"}[5m]) / 
  rate(images_processed_total[5m])
)
```

#### Application Health
```promql
# Uptime (hours)
app_uptime_seconds / 3600

# Uptime (days)
app_uptime_seconds / 86400

# Is application running (1 = yes, 0 = no)
up{job="neurosymbolic"}

# Application restart detection
resets(app_uptime_seconds[1h])
```

---

## Grafana Dashboard Specifications

### Dashboard 1: Training Overview

**Purpose**: Monitor model training progress in real-time

#### Panel 1: Training Loss
```json
{
  "title": "Training Loss",
  "type": "graph",
  "targets": [{
    "expr": "training_loss{model=\"yolov11m-obb\"}",
    "legendFormat": "Epoch {{epoch}}"
  }],
  "yaxes": [{
    "label": "Loss",
    "format": "short"
  }],
  "xaxis": {
    "mode": "time"
  }
}
```

#### Panel 2: Validation mAP
```json
{
  "title": "Validation mAP",
  "type": "graph",
  "targets": [
    {
      "expr": "validation_map{model=\"yolov11m-obb\", iou_threshold=\"0.5\"}",
      "legendFormat": "mAP@0.5"
    },
    {
      "expr": "validation_map{model=\"yolov11m-obb\", iou_threshold=\"0.75\"}",
      "legendFormat": "mAP@0.75"
    }
  ],
  "yaxes": [{
    "label": "mAP",
    "format": "percentunit",
    "max": 1.0,
    "min": 0.0
  }]
}
```

#### Panel 3: Learning Rate
```json
{
  "title": "Learning Rate",
  "type": "graph",
  "targets": [{
    "expr": "learning_rate{model=\"yolov11m-obb\"}",
    "legendFormat": "Learning Rate"
  }],
  "yaxes": [{
    "label": "Learning Rate",
    "format": "short",
    "logBase": 10
  }]
}
```

#### Panel 4: GPU Memory Usage
```json
{
  "title": "GPU Memory Usage",
  "type": "graph",
  "targets": [{
    "expr": "gpu_memory_allocated_bytes / 1024 / 1024 / 1024",
    "legendFormat": "GPU {{device_id}} Allocated (GB)"
  }],
  "yaxes": [{
    "label": "Memory (GB)",
    "format": "short"
  }]
}
```

#### Panel 5: Epoch Duration
```json
{
  "title": "Epoch Duration",
  "type": "stat",
  "targets": [{
    "expr": "avg(training_duration_seconds{model=\"yolov11m-obb\"}) / 60",
    "legendFormat": "Avg Minutes per Epoch"
  }],
  "format": "short",
  "unit": "m"
}
```

### Dashboard 2: Inference Performance

**Purpose**: Monitor real-time inference metrics and throughput

#### Panel 1: Inference Latency Percentiles
```json
{
  "title": "Inference Latency Percentiles",
  "type": "graph",
  "targets": [
    {
      "expr": "histogram_quantile(0.5, sum(rate(inference_time_seconds_bucket[5m])) by (le))",
      "legendFormat": "p50 (median)"
    },
    {
      "expr": "histogram_quantile(0.95, sum(rate(inference_time_seconds_bucket[5m])) by (le))",
      "legendFormat": "p95"
    },
    {
      "expr": "histogram_quantile(0.99, sum(rate(inference_time_seconds_bucket[5m])) by (le))",
      "legendFormat": "p99"
    }
  ],
  "yaxes": [{
    "label": "Latency (seconds)",
    "format": "s"
  }]
}
```

#### Panel 2: Throughput
```json
{
  "title": "Images Processed per Second",
  "type": "graph",
  "targets": [{
    "expr": "rate(images_processed_total{status=\"success\"}[5m])",
    "legendFormat": "{{stage}}"
  }],
  "yaxes": [{
    "label": "Images/sec",
    "format": "ops"
  }]
}
```

#### Panel 3: Detection Distribution
```json
{
  "title": "Detections per Image",
  "type": "heatmap",
  "targets": [{
    "expr": "sum(rate(detections_per_image_bucket[5m])) by (le)",
    "format": "heatmap",
    "legendFormat": "{{le}}"
  }],
  "dataFormat": "tsbuckets",
  "yAxis": {
    "format": "short",
    "logBase": 1
  }
}
```

#### Panel 4: Success Rate Gauge
```json
{
  "title": "Success Rate",
  "type": "gauge",
  "targets": [{
    "expr": "100 * (rate(images_processed_total{status=\"success\"}[5m]) / rate(images_processed_total[5m]))"
  }],
  "thresholds": [
    { "value": 80, "color": "red" },
    { "value": 95, "color": "yellow" },
    { "value": 99, "color": "green" }
  ],
  "min": 0,
  "max": 100,
  "unit": "percent"
}
```

### Dashboard 3: System Resources

**Purpose**: Monitor system health and resource utilization

#### Panel 1: CPU Usage
```json
{
  "title": "CPU Usage",
  "type": "graph",
  "targets": [{
    "expr": "cpu_usage_percent",
    "legendFormat": "CPU Usage"
  }],
  "yaxes": [{
    "label": "Usage (%)",
    "format": "percent",
    "max": 100,
    "min": 0
  }],
  "alert": {
    "conditions": [
      {
        "evaluator": { "type": "gt", "params": [80] },
        "query": { "model": "A" },
        "reducer": { "type": "avg" }
      }
    ],
    "frequency": "60s",
    "name": "High CPU Usage"
  }
}
```

#### Panel 2: Memory Usage
```json
{
  "title": "Memory Usage",
  "type": "graph",
  "targets": [
    {
      "expr": "memory_usage_bytes / 1024 / 1024 / 1024",
      "legendFormat": "Used (GB)"
    },
    {
      "expr": "memory_available_bytes / 1024 / 1024 / 1024",
      "legendFormat": "Available (GB)"
    }
  ],
  "yaxes": [{
    "label": "Memory (GB)",
    "format": "decgbytes"
  }]
}
```

#### Panel 3: GPU Utilization
```json
{
  "title": "GPU Utilization",
  "type": "graph",
  "targets": [{
    "expr": "gpu_utilization_percent",
    "legendFormat": "GPU {{device_id}}"
  }],
  "yaxes": [{
    "label": "Utilization (%)",
    "format": "percent",
    "max": 100,
    "min": 0
  }]
}
```

#### Panel 4: Disk I/O
```json
{
  "title": "Disk I/O",
  "type": "graph",
  "targets": [
    {
      "expr": "rate(disk_read_bytes_total[5m]) / 1024 / 1024",
      "legendFormat": "Read (MB/s)"
    },
    {
      "expr": "rate(disk_write_bytes_total[5m]) / 1024 / 1024",
      "legendFormat": "Write (MB/s)"
    }
  ],
  "yaxes": [{
    "label": "MB/s",
    "format": "MBs"
  }]
}
```

### Dashboard 4: Pipeline Monitoring

**Purpose**: Track neurosymbolic pipeline stages

#### Panel 1: Stage Duration
```json
{
  "title": "Pipeline Stage Duration",
  "type": "graph",
  "targets": [{
    "expr": "avg(pipeline_stage_duration_seconds) by (stage)",
    "legendFormat": "{{stage}}"
  }],
  "yaxes": [{
    "label": "Duration (seconds)",
    "format": "s"
  }]
}
```

#### Panel 2: NMS Efficiency
```json
{
  "title": "NMS Filtering Efficiency",
  "type": "stat",
  "targets": [{
    "expr": "100 * (detections_after_nms / detections_before_nms)",
    "legendFormat": "Detections Kept (%)"
  }],
  "format": "percent",
  "colorMode": "value",
  "thresholds": [
    { "value": 20, "color": "red" },
    { "value": 50, "color": "yellow" },
    { "value": 70, "color": "green" }
  ]
}
```

#### Panel 3: Prolog Query Time
```json
{
  "title": "Prolog Query Performance",
  "type": "graph",
  "targets": [{
    "expr": "histogram_quantile(0.95, rate(prolog_query_seconds_bucket[5m]))",
    "legendFormat": "p95 Query Time"
  }],
  "yaxes": [{
    "label": "Time (seconds)",
    "format": "s",
    "logBase": 10
  }]
}
```

### Dashboard 5: Error Monitoring

**Purpose**: Track errors and failures

#### Panel 1: Error Rate
```json
{
  "title": "Error Rate",
  "type": "graph",
  "targets": [{
    "expr": "sum(rate(errors_total[5m])) by (error_type)",
    "legendFormat": "{{error_type}}"
  }],
  "yaxes": [{
    "label": "Errors/sec",
    "format": "ops"
  }],
  "alert": {
    "conditions": [
      {
        "evaluator": { "type": "gt", "params": [1] },
        "query": { "model": "A" },
        "reducer": { "type": "avg" }
      }
    ],
    "frequency": "60s",
    "name": "High Error Rate"
  }
}
```

#### Panel 2: Failed Operations
```json
{
  "title": "Failed Operations",
  "type": "stat",
  "targets": [
    {
      "expr": "failed_predictions_total",
      "legendFormat": "Failed Predictions"
    },
    {
      "expr": "failed_prolog_queries_total",
      "legendFormat": "Failed Prolog Queries"
    }
  ],
  "format": "short",
  "colorMode": "background"
}
```

---

## GUI Integration

### Embedding Metrics in Custom GUI

#### Option 1: Query Prometheus Directly

**Python Example**:
```python
"""Query Prometheus from Python GUI."""

import requests
from typing import Dict, Any


class PrometheusClient:
    """Client for querying Prometheus."""
    
    def __init__(self, base_url='http://localhost:9090'):
        """Initialize client.
        
        Args:
            base_url: Prometheus server URL
        """
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
    
    def query(self, query: str) -> Dict[str, Any]:
        """Execute instant query.
        
        Args:
            query: PromQL query string
            
        Returns:
            Query result as dictionary
        """
        response = requests.get(
            f"{self.api_url}/query",
            params={'query': query}
        )
        response.raise_for_status()
        return response.json()
    
    def query_range(self, query: str, start: int, end: int, step: str = '15s'):
        """Execute range query.
        
        Args:
            query: PromQL query
            start: Start timestamp (Unix)
            end: End timestamp (Unix)
            step: Query resolution
            
        Returns:
            Time series data
        """
        response = requests.get(
            f"{self.api_url}/query_range",
            params={
                'query': query,
                'start': start,
                'end': end,
                'step': step
            }
        )
        response.raise_for_status()
        return response.json()


# Usage in GUI
client = PrometheusClient()

# Get current training loss
result = client.query('training_loss{model="yolov11m-obb"}')
current_loss = result['data']['result'][0]['value'][1]

# Get inference time over last hour
import time
end = int(time.time())
start = end - 3600  # 1 hour ago

result = client.query_range(
    'histogram_quantile(0.95, rate(inference_time_seconds_bucket[5m]))',
    start=start,
    end=end,
    step='1m'
)
time_series = result['data']['result'][0]['values']
```

#### Option 2: Direct Metrics Access

**For embedded scenarios** (metrics in same process):

```python
"""Access metrics directly from registry."""

from prometheus_client import REGISTRY
from monitoring.metrics import prometheus_metrics as pm


def get_current_metrics():
    """Get current metric values.
    
    Returns:
        Dictionary of metric names to values
    """
    metrics = {}
    
    # Get sample values from registry
    for metric in REGISTRY.collect():
        for sample in metric.samples:
            metrics[sample.name] = {
                'value': sample.value,
                'labels': sample.labels
            }
    
    return metrics


# Usage
metrics = get_current_metrics()
training_loss = metrics.get('training_loss', {}).get('value')
```

### GUI Widget Examples

#### Training Progress Bar

```python
"""Training progress widget."""

import tkinter as tk
from tkinter import ttk


class TrainingProgressWidget:
    """Widget showing training progress."""
    
    def __init__(self, parent, prom_client):
        self.frame = ttk.Frame(parent)
        self.prom_client = prom_client
        
        # Loss label
        self.loss_label = ttk.Label(self.frame, text="Training Loss: --")
        self.loss_label.pack()
        
        # mAP label
        self.map_label = ttk.Label(self.frame, text="Validation mAP: --")
        self.map_label.pack()
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.frame,
            mode='determinate',
            maximum=100
        )
        self.progress.pack()
        
        # Update periodically
        self.update()
    
    def update(self):
        """Update metrics from Prometheus."""
        try:
            # Get training loss
            result = self.prom_client.query('training_loss')
            if result['data']['result']:
                loss = float(result['data']['result'][0]['value'][1])
                self.loss_label.config(text=f"Training Loss: {loss:.4f}")
            
            # Get validation mAP
            result = self.prom_client.query('validation_map{iou_threshold="0.5"}')
            if result['data']['result']:
                map_val = float(result['data']['result'][0]['value'][1])
                self.map_label.config(text=f"Validation mAP: {map_val:.3f}")
                self.progress['value'] = map_val * 100
        except Exception as e:
            print(f"Error updating metrics: {e}")
        
        # Schedule next update
        self.frame.after(5000, self.update)  # Update every 5 seconds
```

#### Inference Stats Dashboard

```python
"""Inference statistics widget."""

import tkinter as tk
from tkinter import ttk


class InferenceStatsWidget:
    """Widget showing inference statistics."""
    
    def __init__(self, parent, prom_client):
        self.frame = ttk.Frame(parent)
        self.prom_client = prom_client
        
        # Create stats labels
        self.stats = {
            'throughput': ttk.Label(self.frame, text="Throughput: --"),
            'latency_p50': ttk.Label(self.frame, text="Latency (p50): --"),
            'latency_p95': ttk.Label(self.frame, text="Latency (p95): --"),
            'success_rate': ttk.Label(self.frame, text="Success Rate: --"),
        }
        
        for label in self.stats.values():
            label.pack()
        
        self.update()
    
    def update(self):
        """Update statistics."""
        try:
            # Throughput
            result = self.prom_client.query(
                'rate(images_processed_total{status="success"}[5m])'
            )
            if result['data']['result']:
                throughput = float(result['data']['result'][0]['value'][1])
                self.stats['throughput'].config(
                    text=f"Throughput: {throughput:.2f} img/s"
                )
            
            # Latency p50
            result = self.prom_client.query(
                'histogram_quantile(0.5, rate(inference_time_seconds_bucket[5m]))'
            )
            if result['data']['result']:
                latency = float(result['data']['result'][0]['value'][1])
                self.stats['latency_p50'].config(
                    text=f"Latency (p50): {latency*1000:.0f} ms"
                )
            
            # Latency p95
            result = self.prom_client.query(
                'histogram_quantile(0.95, rate(inference_time_seconds_bucket[5m]))'
            )
            if result['data']['result']:
                latency = float(result['data']['result'][0]['value'][1])
                self.stats['latency_p95'].config(
                    text=f"Latency (p95): {latency*1000:.0f} ms"
                )
            
            # Success rate
            result = self.prom_client.query(
                '100 * (rate(images_processed_total{status="success"}[5m]) / rate(images_processed_total[5m]))'
            )
            if result['data']['result']:
                success_rate = float(result['data']['result'][0]['value'][1])
                self.stats['success_rate'].config(
                    text=f"Success Rate: {success_rate:.1f}%"
                )
        except Exception as e:
            print(f"Error updating stats: {e}")
        
        self.frame.after(5000, self.update)
```

---

## Custom Visualizations

### Chart Generation with Matplotlib

```python
"""Generate charts from Prometheus data."""

import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def plot_training_progress(prom_client, model_name='yolov11m-obb'):
    """Plot training loss and validation mAP.
    
    Args:
        prom_client: PrometheusClient instance
        model_name: Model to plot
    """
    # Get data for last 6 hours
    end = int(datetime.now().timestamp())
    start = end - (6 * 3600)
    
    # Query training loss
    loss_data = prom_client.query_range(
        f'training_loss{{model="{model_name}"}}',
        start=start,
        end=end,
        step='5m'
    )
    
    # Query validation mAP
    map_data = prom_client.query_range(
        f'validation_map{{model="{model_name}", iou_threshold="0.5"}}',
        start=start,
        end=end,
        step='5m'
    )
    
    # Extract timestamps and values
    loss_times = [datetime.fromtimestamp(int(v[0])) for v in loss_data['data']['result'][0]['values']]
    loss_values = [float(v[1]) for v in loss_data['data']['result'][0]['values']]
    
    map_times = [datetime.fromtimestamp(int(v[0])) for v in map_data['data']['result'][0]['values']]
    map_values = [float(v[1]) for v in map_data['data']['result'][0]['values']]
    
    # Create plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Training loss
    ax1.plot(loss_times, loss_values, 'b-')
    ax1.set_ylabel('Training Loss')
    ax1.set_title(f'Training Progress - {model_name}')
    ax1.grid(True)
    
    # Validation mAP
    ax2.plot(map_times, map_values, 'g-')
    ax2.set_ylabel('Validation mAP@0.5')
    ax2.set_xlabel('Time')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('training_progress.png')
    plt.close()
```

---

## Alerting and Notifications

### Alert Rules Configuration

**File**: `monitoring/alert_rules.yml`

```yaml
groups:
  - name: neurosymbolic_alerts
    interval: 30s
    rules:
      # Training alerts
      - alert: TrainingStalled
        expr: changes(training_loss[10m]) == 0
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "Training appears stalled"
          description: "Training loss hasn't changed in 30 minutes"
      
      # Inference alerts
      - alert: HighInferenceLatency
        expr: |
          histogram_quantile(0.95, 
            rate(inference_time_seconds_bucket[5m])
          ) > 2.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High inference latency detected"
          description: "95th percentile inference time > 2 seconds"
      
      - alert: LowThroughput
        expr: rate(images_processed_total[5m]) < 0.1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low processing throughput"
          description: "Processing less than 0.1 images/second"
      
      # System alerts
      - alert: HighCPUUsage
        expr: cpu_usage_percent > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"
          description: "CPU usage over 90% for 5 minutes"
      
      - alert: HighGPUMemory
        expr: |
          (gpu_memory_allocated_bytes / gpu_memory_reserved_bytes) > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High GPU memory usage"
          description: "GPU memory usage over 90%"
      
      - alert: DiskSpaceLow
        expr: memory_available_bytes < 1073741824  # 1GB
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Low available memory"
          description: "Less than 1GB memory available"
      
      # Error alerts
      - alert: HighErrorRate
        expr: rate(errors_total[5m]) > 1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate"
          description: "More than 1 error per second"
      
      - alert: ApplicationDown
        expr: up{job="neurosymbolic"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Application is down"
          description: "Cannot scrape metrics from application"
```

---

## Query Optimization

### Performance Tips

#### 1. Use Recording Rules

For expensive queries, pre-calculate results:

```yaml
groups:
  - name: recording_rules
    interval: 30s
    rules:
      # Average inference time
      - record: job:inference_time_seconds:mean
        expr: |
          rate(inference_time_seconds_sum[5m]) / 
          rate(inference_time_seconds_count[5m])
      
      # Success rate
      - record: job:images_processed:success_rate
        expr: |
          rate(images_processed_total{status="success"}[5m]) / 
          rate(images_processed_total[5m])
```

Then query the recorded metric:
```promql
# Instead of complex query
job:inference_time_seconds:mean
```

#### 2. Optimize Time Ranges

- Use shorter time ranges for recent data
- Use recording rules for longer time ranges
- Aggregate before querying long ranges

#### 3. Label Filtering

Filter early in query:
```promql
# Good - filter first
rate(images_processed_total{status="success", stage="inference"}[5m])

# Bad - filter after aggregation
sum(rate(images_processed_total[5m])) by (status) and status="success"
```

---

## Next Steps

1. **Set up Prometheus**: Install and configure Prometheus server
2. **Create Dashboards**: Import or create Grafana dashboards
3. **Configure Alerts**: Set up alerting rules
4. **Integrate GUI**: Add monitoring widgets to custom GUI
5. **Test**: Verify queries and dashboards work correctly

---

## References

- [PromQL Documentation](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Documentation](https://grafana.com/docs/grafana/latest/)
- [Prometheus API](https://prometheus.io/docs/prometheus/latest/querying/api/)
- [PROMETHEUS_METRICS_CATALOG.md](PROMETHEUS_METRICS_CATALOG.md) - Metrics reference
- [PROMETHEUS_EXPORTERS_SPECIFICATION.md](PROMETHEUS_EXPORTERS_SPECIFICATION.md) - Export implementation

---

**Document Status**: ✅ Planning Complete - Ready for Implementation  
**Last Review**: February 2026  
**Next Review**: After dashboard creation
