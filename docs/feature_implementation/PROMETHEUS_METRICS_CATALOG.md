# Prometheus Metrics Catalog

**Document Version:** 1.0.0  
**Last Updated:** February 2026  
**Status:** Planning Documentation - No Implementation Required

---

## Table of Contents

1. [Overview](#overview)
2. [Metrics Naming Conventions](#metrics-naming-conventions)
3. [Complete Metrics List](#complete-metrics-list)
4. [Metrics by Category](#metrics-by-category)
5. [Label Specifications](#label-specifications)
6. [Metrics Usage Guidelines](#metrics-usage-guidelines)
7. [Integration Points](#integration-points)

---

## Overview

This document provides a comprehensive catalog of all Prometheus metrics that will be collected from the Neurosymbolic Object Detection application. Each metric is designed to provide observability into specific aspects of the ML pipeline, from model training through knowledge graph construction.

### Purpose

- **Complete Reference**: Single source of truth for all metrics
- **Consistency**: Ensures uniform naming and labeling across the application
- **Planning Tool**: Guides implementation and dashboard design
- **Documentation**: Provides context for each metric's purpose and usage

### Metrics Categories

| Category | Count | Purpose |
|----------|-------|---------|
| Training Metrics | 12 | Monitor model training progress and convergence |
| Inference Metrics | 8 | Track prediction performance and throughput |
| Symbolic Pipeline Metrics | 10 | Measure NMS and Prolog reasoning efficiency |
| Knowledge Graph Metrics | 7 | Monitor graph construction and relationships |
| System Resource Metrics | 9 | Track CPU, GPU, memory, and disk usage |
| Error and Health Metrics | 6 | Monitor failures and system health |
| **Total** | **52** | **Complete application observability** |

---

## Metrics Naming Conventions

### Standard Naming Rules

Following Prometheus best practices:

1. **Base Units**: Always use base units in metric names
   - Time: `_seconds` (not milliseconds)
   - Memory: `_bytes` (not MB/GB)
   - Convert to base units when recording

2. **Suffixes by Type**:
   - Counters: `_total` suffix
   - Gauges: No special suffix
   - Histograms: `_seconds`, `_bytes`, etc.
   - Info: `_info` suffix

3. **Snake Case**: Use lowercase with underscores
   - ✅ `training_loss`
   - ❌ `trainingLoss` or `training-loss`

4. **Descriptive Names**: Clear, unambiguous metric names
   - ✅ `gpu_memory_allocated_bytes`
   - ❌ `mem` or `gpu_mem`

### Namespace

All application metrics use the implicit namespace:
- **Application**: `neurosymbolic_object_detection`
- **Namespace prefix**: Not required (single application deployment)

For multi-tenant deployments, consider adding prefix:
- `nsod_training_loss` (namespace: nsod)

---

## Complete Metrics List

### Quick Reference Table

| Metric Name | Type | Unit | Labels | Description |
|-------------|------|------|--------|-------------|
| `training_loss` | Gauge | - | model, epoch | Training loss per epoch |
| `validation_map` | Gauge | - | model, iou_threshold | Validation mean Average Precision |
| `training_duration_seconds` | Histogram | seconds | model | Training time per epoch |
| `learning_rate` | Gauge | - | model | Current learning rate |
| `batch_processing_seconds` | Histogram | seconds | model, phase | Batch processing time |
| `gpu_memory_allocated_bytes` | Gauge | bytes | device_id | GPU memory allocated |
| `gpu_memory_reserved_bytes` | Gauge | bytes | device_id | GPU memory reserved |
| `gpu_utilization_percent` | Gauge | percent | device_id | GPU utilization percentage |
| `inference_time_seconds` | Histogram | seconds | model, use_sahi | Inference time per image |
| `detections_per_image` | Histogram | count | model | Number of detections per image |
| `confidence_scores` | Histogram | - | model | Detection confidence distribution |
| `sahi_slices_per_image` | Histogram | count | - | SAHI slices generated per image |
| `images_processed_total` | Counter | count | stage, status | Total images processed |
| `nms_filtering_seconds` | Histogram | seconds | - | NMS filtering duration |
| `detections_before_nms` | Gauge | count | image_id | Detections before NMS |
| `detections_after_nms` | Gauge | count | image_id | Detections after NMS |
| `prolog_query_seconds` | Histogram | seconds | query_type | Prolog query execution time |
| `confidence_adjustment_delta` | Histogram | - | - | Confidence adjustment magnitude |
| `pipeline_stage_duration_seconds` | Histogram | seconds | stage | Pipeline stage duration |
| `prolog_facts_generated_total` | Counter | count | fact_type | Total Prolog facts generated |
| `graph_construction_seconds` | Histogram | seconds | - | Graph construction time |
| `graph_nodes_count` | Gauge | count | image_id | Nodes in knowledge graph |
| `graph_edges_count` | Gauge | count | image_id | Edges in knowledge graph |
| `relationships_extracted_total` | Counter | count | relationship_type | Relationships extracted |
| `spatial_relationships_total` | Counter | count | spatial_type | Spatial relationship types |
| `cpu_usage_percent` | Gauge | percent | - | CPU usage percentage |
| `memory_usage_bytes` | Gauge | bytes | - | Memory usage |
| `memory_available_bytes` | Gauge | bytes | - | Available memory |
| `disk_read_bytes_total` | Counter | bytes | - | Total disk bytes read |
| `disk_write_bytes_total` | Counter | bytes | - | Total disk bytes written |
| `app_uptime_seconds` | Gauge | seconds | - | Application uptime |
| `errors_total` | Counter | count | error_type, stage | Total errors by type |
| `failed_predictions_total` | Counter | count | reason | Failed predictions |
| `failed_prolog_queries_total` | Counter | count | error_type | Failed Prolog queries |
| `model_load_time_seconds` | Histogram | seconds | model | Time to load model |
| `checkpoint_save_seconds` | Histogram | seconds | - | Checkpoint save duration |
| `app_info` | Info | - | version, python_version | Application information |

---

## Metrics by Category

### 1. Training Metrics

Monitors model training process, convergence, and resource usage during training.

#### 1.1 Loss and Accuracy Metrics

**`training_loss`** (Gauge)
- **Description**: Training loss per epoch
- **Labels**: 
  - `model`: Model architecture (e.g., "yolov11m-obb")
  - `epoch`: Current epoch number (as string)
- **Unit**: Dimensionless (loss value)
- **Usage**: Track training convergence
- **Example Query**: `training_loss{model="yolov11m-obb"}`

**`validation_map`** (Gauge)
- **Description**: Validation mean Average Precision
- **Labels**:
  - `model`: Model architecture
  - `iou_threshold`: IoU threshold (e.g., "0.5", "0.75")
- **Unit**: Dimensionless (0.0 to 1.0)
- **Usage**: Evaluate model accuracy during training
- **Example Query**: `validation_map{model="yolov11m-obb", iou_threshold="0.5"}`

**`learning_rate`** (Gauge)
- **Description**: Current learning rate
- **Labels**:
  - `model`: Model architecture
- **Unit**: Dimensionless (learning rate value)
- **Usage**: Monitor learning rate schedule
- **Example Query**: `learning_rate{model="yolov11m-obb"}`

#### 1.2 Performance Metrics

**`training_duration_seconds`** (Histogram)
- **Description**: Time spent training per epoch
- **Labels**:
  - `model`: Model architecture
- **Unit**: seconds
- **Buckets**: [60, 300, 600, 1800, 3600, 7200] (1 min to 2 hours)
- **Usage**: Measure training efficiency
- **Example Query**: `histogram_quantile(0.95, training_duration_seconds_bucket{model="yolov11m-obb"})`

**`batch_processing_seconds`** (Histogram)
- **Description**: Time to process a single batch
- **Labels**:
  - `model`: Model architecture
  - `phase`: "train" or "validation"
- **Unit**: seconds
- **Buckets**: [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
- **Usage**: Identify bottlenecks in data loading or GPU processing
- **Example Query**: `rate(batch_processing_seconds_sum[5m]) / rate(batch_processing_seconds_count[5m])`

**`model_load_time_seconds`** (Histogram)
- **Description**: Time to load model weights from disk
- **Labels**:
  - `model`: Model architecture
- **Unit**: seconds
- **Buckets**: [0.5, 1.0, 5.0, 10.0, 30.0]
- **Usage**: Monitor model initialization performance
- **Example Query**: `histogram_quantile(0.99, model_load_time_seconds_bucket)`

**`checkpoint_save_seconds`** (Histogram)
- **Description**: Time to save model checkpoint
- **Labels**: None
- **Unit**: seconds
- **Buckets**: [1.0, 5.0, 10.0, 30.0, 60.0]
- **Usage**: Monitor checkpoint I/O performance
- **Example Query**: `checkpoint_save_seconds_sum / checkpoint_save_seconds_count`

#### 1.3 GPU Metrics

**`gpu_memory_allocated_bytes`** (Gauge)
- **Description**: GPU memory actively allocated by PyTorch
- **Labels**:
  - `device_id`: GPU device ID (e.g., "0", "1")
- **Unit**: bytes
- **Usage**: Monitor GPU memory usage
- **Example Query**: `gpu_memory_allocated_bytes / 1024 / 1024 / 1024` (GB)

**`gpu_memory_reserved_bytes`** (Gauge)
- **Description**: GPU memory reserved by PyTorch (including cache)
- **Labels**:
  - `device_id`: GPU device ID
- **Unit**: bytes
- **Usage**: Monitor total GPU memory footprint
- **Example Query**: `gpu_memory_reserved_bytes{device_id="0"}`

**`gpu_utilization_percent`** (Gauge)
- **Description**: GPU compute utilization percentage
- **Labels**:
  - `device_id`: GPU device ID
- **Unit**: percent (0-100)
- **Usage**: Monitor GPU efficiency
- **Example Query**: `gpu_utilization_percent{device_id="0"}`

---

### 2. Inference Metrics

Tracks prediction performance, throughput, and detection quality.

#### 2.1 Timing Metrics

**`inference_time_seconds`** (Histogram)
- **Description**: Time to run inference on a single image
- **Labels**:
  - `model`: Model architecture
  - `use_sahi`: "true" or "false"
- **Unit**: seconds
- **Buckets**: [0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
- **Usage**: Measure inference latency
- **Example Query**: `histogram_quantile(0.95, inference_time_seconds_bucket{use_sahi="true"})`

#### 2.2 Detection Metrics

**`detections_per_image`** (Histogram)
- **Description**: Number of object detections per image
- **Labels**:
  - `model`: Model architecture
- **Unit**: count
- **Buckets**: [0, 10, 25, 50, 100, 200, 500, 1000]
- **Usage**: Understand detection density
- **Example Query**: `histogram_quantile(0.5, detections_per_image_bucket{model="yolov11m-obb"})`

**`confidence_scores`** (Histogram)
- **Description**: Distribution of detection confidence scores
- **Labels**:
  - `model`: Model architecture
- **Unit**: dimensionless (0.0-1.0)
- **Buckets**: [0.1, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]
- **Usage**: Analyze model confidence patterns
- **Example Query**: `histogram_quantile(0.9, confidence_scores_bucket)`

**`sahi_slices_per_image`** (Histogram)
- **Description**: Number of SAHI slices generated per image
- **Labels**: None
- **Unit**: count
- **Buckets**: [1, 4, 9, 16, 25, 36, 49, 64]
- **Usage**: Monitor SAHI slicing overhead
- **Example Query**: `sahi_slices_per_image_sum / sahi_slices_per_image_count`

#### 2.3 Throughput Metrics

**`images_processed_total`** (Counter)
- **Description**: Total number of images processed
- **Labels**:
  - `stage`: "training", "inference", "evaluation"
  - `status`: "success" or "failed"
- **Unit**: count
- **Usage**: Track processing volume and success rate
- **Example Query**: `rate(images_processed_total{stage="inference", status="success"}[5m])`

---

### 3. Symbolic Pipeline Metrics

Measures NMS filtering, Prolog reasoning, and pipeline stage performance.

#### 3.1 NMS Metrics

**`nms_filtering_seconds`** (Histogram)
- **Description**: Time spent on NMS filtering
- **Labels**: None
- **Unit**: seconds
- **Buckets**: [0.001, 0.01, 0.1, 1.0, 5.0]
- **Usage**: Measure NMS performance
- **Example Query**: `histogram_quantile(0.95, nms_filtering_seconds_bucket)`

**`detections_before_nms`** (Gauge)
- **Description**: Number of detections before NMS
- **Labels**:
  - `image_id`: Image identifier
- **Unit**: count
- **Usage**: Track raw detection counts
- **Example Query**: `detections_before_nms`

**`detections_after_nms`** (Gauge)
- **Description**: Number of detections after NMS
- **Labels**:
  - `image_id`: Image identifier
- **Unit**: count
- **Usage**: Measure NMS filtering impact
- **Example Query**: `detections_after_nms`

**NMS Efficiency Calculation**:
```promql
# Percentage of detections kept after NMS
100 * (detections_after_nms / detections_before_nms)
```

#### 3.2 Prolog Reasoning Metrics

**`prolog_query_seconds`** (Histogram)
- **Description**: Prolog query execution time
- **Labels**:
  - `query_type`: Type of query (e.g., "adjust_confidence", "extract_relationship")
- **Unit**: seconds
- **Buckets**: [0.0001, 0.001, 0.01, 0.1, 1.0]
- **Usage**: Monitor Prolog performance
- **Example Query**: `histogram_quantile(0.99, prolog_query_seconds_bucket{query_type="adjust_confidence"})`

**`confidence_adjustment_delta`** (Histogram)
- **Description**: Magnitude of confidence adjustments by Prolog
- **Labels**: None
- **Unit**: dimensionless (adjustment delta)
- **Buckets**: [-0.5, -0.3, -0.1, -0.05, 0, 0.05, 0.1, 0.3, 0.5]
- **Usage**: Analyze symbolic reasoning impact
- **Example Query**: `histogram_quantile(0.5, confidence_adjustment_delta_bucket)`

**`prolog_facts_generated_total`** (Counter)
- **Description**: Total Prolog facts generated
- **Labels**:
  - `fact_type`: Type of fact (e.g., "object", "relationship", "confidence")
- **Unit**: count
- **Usage**: Track symbolic knowledge generation
- **Example Query**: `rate(prolog_facts_generated_total[5m])`

**`failed_prolog_queries_total`** (Counter)
- **Description**: Total failed Prolog queries
- **Labels**:
  - `error_type`: Error category (e.g., "syntax_error", "undefined_predicate")
- **Unit**: count
- **Usage**: Monitor Prolog integration health
- **Example Query**: `failed_prolog_queries_total`

#### 3.3 Pipeline Stage Metrics

**`pipeline_stage_duration_seconds`** (Histogram)
- **Description**: Duration of each pipeline stage
- **Labels**:
  - `stage`: "preprocess", "symbolic", "eval", "kg_construction"
- **Unit**: seconds
- **Buckets**: [1, 5, 10, 30, 60, 300, 600]
- **Usage**: Identify pipeline bottlenecks
- **Example Query**: `histogram_quantile(0.95, pipeline_stage_duration_seconds_bucket{stage="symbolic"})`

---

### 4. Knowledge Graph Metrics

Monitors graph construction and relationship extraction.

#### 4.1 Graph Construction Metrics

**`graph_construction_seconds`** (Histogram)
- **Description**: Time to construct knowledge graph
- **Labels**: None
- **Unit**: seconds
- **Buckets**: [0.1, 0.5, 1, 5, 10, 30]
- **Usage**: Measure graph building performance
- **Example Query**: `histogram_quantile(0.95, graph_construction_seconds_bucket)`

**`graph_nodes_count`** (Gauge)
- **Description**: Number of nodes in knowledge graph
- **Labels**:
  - `image_id`: Image identifier
- **Unit**: count
- **Usage**: Monitor graph size
- **Example Query**: `avg(graph_nodes_count)`

**`graph_edges_count`** (Gauge)
- **Description**: Number of edges in knowledge graph
- **Labels**:
  - `image_id`: Image identifier
- **Unit**: count
- **Usage**: Monitor relationship count
- **Example Query**: `graph_edges_count`

**Graph Density Calculation**:
```promql
# Average edges per node
graph_edges_count / graph_nodes_count
```

#### 4.2 Relationship Metrics

**`relationships_extracted_total`** (Counter)
- **Description**: Total relationships extracted
- **Labels**:
  - `relationship_type`: Relationship category (e.g., "spatial", "containment", "proximity")
- **Unit**: count
- **Usage**: Track relationship extraction volume
- **Example Query**: `rate(relationships_extracted_total[5m])`

**`spatial_relationships_total`** (Counter)
- **Description**: Spatial relationships by type
- **Labels**:
  - `spatial_type`: "left_of", "right_of", "above", "below", "contains", "near"
- **Unit**: count
- **Usage**: Analyze spatial relationship patterns
- **Example Query**: `spatial_relationships_total{spatial_type="contains"}`

---

### 5. System Resource Metrics

Monitors CPU, memory, disk, and application health.

#### 5.1 CPU and Memory Metrics

**`cpu_usage_percent`** (Gauge)
- **Description**: CPU usage percentage
- **Labels**: None
- **Unit**: percent (0-100)
- **Usage**: Monitor CPU load
- **Example Query**: `cpu_usage_percent`

**`memory_usage_bytes`** (Gauge)
- **Description**: Application memory usage
- **Labels**: None
- **Unit**: bytes
- **Usage**: Track memory consumption
- **Example Query**: `memory_usage_bytes / 1024 / 1024 / 1024` (GB)

**`memory_available_bytes`** (Gauge)
- **Description**: Available system memory
- **Labels**: None
- **Unit**: bytes
- **Usage**: Monitor memory availability
- **Example Query**: `memory_available_bytes / 1024 / 1024 / 1024` (GB)

#### 5.2 Disk I/O Metrics

**`disk_read_bytes_total`** (Counter)
- **Description**: Total bytes read from disk
- **Labels**: None
- **Unit**: bytes
- **Usage**: Monitor disk read activity
- **Example Query**: `rate(disk_read_bytes_total[5m])` (bytes/sec)

**`disk_write_bytes_total`** (Counter)
- **Description**: Total bytes written to disk
- **Labels**: None
- **Unit**: bytes
- **Usage**: Monitor disk write activity
- **Example Query**: `rate(disk_write_bytes_total[5m])` (bytes/sec)

#### 5.3 Application Health Metrics

**`app_uptime_seconds`** (Gauge)
- **Description**: Application uptime in seconds
- **Labels**: None
- **Unit**: seconds
- **Usage**: Monitor application availability
- **Example Query**: `app_uptime_seconds / 3600` (hours)

**`app_info`** (Info)
- **Description**: Application metadata
- **Labels**:
  - `version`: Application version
  - `python_version`: Python version
  - `model_version`: Model version (if applicable)
- **Unit**: N/A (informational)
- **Usage**: Track deployment versions
- **Example Query**: `app_info`

---

### 6. Error and Health Metrics

Tracks failures, errors, and system issues.

**`errors_total`** (Counter)
- **Description**: Total errors by type and stage
- **Labels**:
  - `error_type`: "file_not_found", "cuda_error", "inference_error", etc.
  - `stage`: Pipeline stage where error occurred
- **Unit**: count
- **Usage**: Monitor error rates and types
- **Example Query**: `rate(errors_total[5m])`

**`failed_predictions_total`** (Counter)
- **Description**: Total failed prediction attempts
- **Labels**:
  - `reason`: Failure reason (e.g., "timeout", "memory_error", "invalid_input")
- **Unit**: count
- **Usage**: Track prediction failures
- **Example Query**: `failed_predictions_total{reason="timeout"}`

---

## Label Specifications

### Standard Labels

#### `model` Label
- **Values**: "yolov11n-obb", "yolov11s-obb", "yolov11m-obb", "yolov11l-obb", "yolov11x-obb"
- **Usage**: Differentiate metrics by model architecture
- **Cardinality**: Low (5 values)

#### `stage` Label
- **Values**: "training", "inference", "preprocess", "symbolic", "eval", "kg_construction"
- **Usage**: Track metrics by pipeline stage
- **Cardinality**: Low (6 values)

#### `device_id` Label
- **Values**: "0", "1", "2", ... (GPU device IDs)
- **Usage**: Track per-GPU metrics
- **Cardinality**: Low (typically 1-8 GPUs)

#### `status` Label
- **Values**: "success", "failed"
- **Usage**: Differentiate successful vs failed operations
- **Cardinality**: Very low (2 values)

### Cardinality Warnings

⚠️ **Avoid High-Cardinality Labels**:
- Don't use `image_id` as a label in production (use sparingly in development)
- Don't use timestamps as labels
- Don't use user IDs or request IDs as labels
- High cardinality can cause memory issues and slow queries

**Safe approach for image-specific metrics**:
- Use aggregated metrics without image_id
- For debugging, temporarily add image_id label
- Remove image_id label in production

---

## Metrics Usage Guidelines

### When to Use Each Metric Type

#### Counters
**Use when**: Value only increases (never decreases)
- Total images processed
- Total errors
- Total relationships extracted

**Query with**: `rate()` or `increase()`

**Example**:
```promql
# Images per second
rate(images_processed_total{status="success"}[5m])
```

#### Gauges
**Use when**: Value can increase or decrease
- Current GPU memory usage
- Current CPU usage
- Number of detections in current image

**Query with**: Direct value or aggregations

**Example**:
```promql
# Average GPU memory
avg(gpu_memory_allocated_bytes)
```

#### Histograms
**Use when**: Measuring distributions (latency, sizes)
- Inference time
- Detection counts
- Confidence scores

**Query with**: `histogram_quantile()` for percentiles

**Example**:
```promql
# 95th percentile inference time
histogram_quantile(0.95, inference_time_seconds_bucket)
```

### Recording Rules

For frequently-used complex queries, create recording rules:

```yaml
groups:
  - name: neurosymbolic_rules
    interval: 30s
    rules:
      # Average inference time
      - record: job:inference_time_seconds:mean
        expr: rate(inference_time_seconds_sum[5m]) / rate(inference_time_seconds_count[5m])
      
      # Success rate
      - record: job:images_processed:success_rate
        expr: |
          rate(images_processed_total{status="success"}[5m]) 
          / 
          rate(images_processed_total[5m])
      
      # NMS filtering efficiency
      - record: job:nms:efficiency_percent
        expr: 100 * (detections_after_nms / detections_before_nms)
```

---

## Integration Points

### Training Integration

**File**: `pipeline/training/training.py`

**Metrics Updated**:
- `training_loss` (per epoch)
- `validation_map` (per validation)
- `training_duration_seconds` (per epoch)
- `learning_rate` (per optimizer step)
- `gpu_memory_allocated_bytes` (continuous)
- `gpu_utilization_percent` (continuous)

**Collection Points**:
- Start of training: Initialize metrics server
- Per epoch: Record loss, duration
- Per validation: Record mAP
- Per batch: Update GPU metrics

### Inference Integration

**File**: `pipeline/inference/sahi_yolo_prediction.py`

**Metrics Updated**:
- `inference_time_seconds` (per image)
- `detections_per_image` (per image)
- `confidence_scores` (per detection)
- `sahi_slices_per_image` (per image)
- `images_processed_total` (per image)

**Collection Points**:
- Per image inference: Time and count detections
- Per SAHI slice: Count slices
- Per detection: Record confidence

### Symbolic Pipeline Integration

**Files**: 
- `pipeline/core/preprocess.py`
- `pipeline/core/symbolic.py`
- `pipeline/core/eval.py`

**Metrics Updated**:
- `nms_filtering_seconds` (per image)
- `detections_before_nms` (per image)
- `detections_after_nms` (per image)
- `prolog_query_seconds` (per query)
- `confidence_adjustment_delta` (per adjustment)
- `pipeline_stage_duration_seconds` (per stage)

**Collection Points**:
- NMS stage: Time filtering, count detections
- Symbolic stage: Time Prolog queries, record adjustments
- Eval stage: Measure stage duration

### Knowledge Graph Integration

**File**: `pipeline/inference/weighted_kg_sahi.py`

**Metrics Updated**:
- `graph_construction_seconds` (per graph)
- `graph_nodes_count` (per graph)
- `graph_edges_count` (per graph)
- `relationships_extracted_total` (per relationship)
- `spatial_relationships_total` (per relationship)

**Collection Points**:
- Graph construction: Time building
- Node/edge creation: Count elements
- Relationship extraction: Categorize and count

---

## Next Steps

1. **Review**: Validate metrics catalog with stakeholders
2. **Implement**: Follow [PROMETHEUS_EXPORTERS_SPECIFICATION.md](PROMETHEUS_EXPORTERS_SPECIFICATION.md)
3. **Dashboard**: Create visualizations using [PROMETHEUS_DASHBOARD_GUIDE.md](PROMETHEUS_DASHBOARD_GUIDE.md)
4. **Deploy**: Set up monitoring infrastructure per [PROMETHEUS_INTEGRATION_GUIDE.md](PROMETHEUS_INTEGRATION_GUIDE.md)

---

## References

- [Prometheus Metric Types](https://prometheus.io/docs/concepts/metric_types/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/naming/)
- [PromQL Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [PROMETHEUS_INTEGRATION_GUIDE.md](PROMETHEUS_INTEGRATION_GUIDE.md) - Complete integration guide

---

**Document Status**: ✅ Planning Complete - Ready for Implementation  
**Last Review**: February 2026  
**Next Review**: After implementation phase
