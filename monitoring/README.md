# Monitoring

This directory contains monitoring infrastructure for tracking metrics, logs, and system performance.

## Structure

```
monitoring/
├── metrics/        # Performance metrics and statistics
└── logs/           # Application and system logs
```

## Planned Features

### Metrics (`metrics/`)

Track and store:
- **Model Performance**: mAP, precision, recall, F1 scores
- **Training Metrics**: Loss curves, learning rates, epoch times
- **Inference Metrics**: Processing time per image, throughput
- **Pipeline Metrics**: Stage execution times, success/failure rates
- **System Metrics**: GPU/CPU utilization, memory usage

### Logs (`logs/`)

Collect and organize:
- **Application Logs**: Pipeline execution logs, errors, warnings
- **Training Logs**: Model checkpoints, hyperparameters, configurations
- **API Logs**: Request/response logs, error traces
- **System Logs**: Resource usage, performance bottlenecks

## Implementation Guidelines

### Metrics Collection

Use standard tools:
- **Prometheus**: For time-series metrics
- **Grafana**: For visualization dashboards
- **MLflow**: For experiment tracking
- **Weights & Biases**: Alternative for ML experiment tracking

Example metric structure:
```
metrics/
├── training/
│   ├── experiment_001.json
│   └── experiment_002.json
├── evaluation/
│   ├── model_v1_results.json
│   └── model_v2_results.json
└── inference/
    ├── daily_performance.csv
    └── weekly_summary.json
```

### Logging Configuration

Use Python's logging module with structured logging:

```python
import logging
import json

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring/logs/app.log'),
        logging.StreamHandler()
    ]
)
```

Example log structure:
```
logs/
├── application/
│   ├── pipeline.log
│   ├── training.log
│   └── inference.log
├── errors/
│   └── error.log
└── system/
    ├── gpu_usage.log
    └── memory.log
```

## Key Metrics to Track

### Training Phase
- Training loss per epoch
- Validation loss per epoch
- Learning rate schedule
- Training time per epoch
- GPU memory usage

### Evaluation Phase
- mAP@50, mAP@75, mAP@50:95
- Per-class precision and recall
- Inference time per image
- NMS effectiveness (detections before/after)

### Symbolic Pipeline
- Confidence adjustment statistics
- Prolog query execution time
- Detection count per stage
- Rule application frequency

### System Performance
- CPU/GPU utilization
- Memory consumption
- Disk I/O
- Network bandwidth (if distributed)

## Alerting (Future)

Set up alerts for:
- Model performance degradation
- Training failures or abnormal loss values
- System resource exhaustion
- API endpoint failures

## Integration with Subprojects

- **Pipeline**: Emits metrics during training, inference, and evaluation
- **Backend**: Logs API requests and provides metrics endpoints
- **Frontend**: Displays metrics in dashboards

## Best Practices

1. Use structured logging (JSON format)
2. Include timestamps and context in all logs
3. Rotate log files to prevent disk space issues
4. Set appropriate log levels (DEBUG, INFO, WARNING, ERROR)
5. Store metrics in a queryable format (JSON, CSV, database)
6. Implement retention policies for old logs/metrics
7. Secure sensitive information in logs

## Example Usage

```python
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Log metrics
metrics = {
    'timestamp': datetime.now().isoformat(),
    'model': 'yolov11m-obb',
    'mAP@50': 0.756,
    'mAP@75': 0.632,
    'inference_time_ms': 45.2
}

logger.info(f"Evaluation metrics: {json.dumps(metrics)}")

# Save to file
with open('monitoring/metrics/evaluation_results.json', 'w') as f:
    json.dump(metrics, f, indent=2)
```

## Related Documentation

- See `docs/` for monitoring setup guides
- Check main README for system requirements
