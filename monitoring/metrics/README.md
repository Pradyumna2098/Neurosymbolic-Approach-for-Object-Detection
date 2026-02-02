# Metrics Directory

This directory stores performance metrics and statistics for the neurosymbolic pipeline.

## Purpose

Track and analyze:
- Model training metrics
- Inference performance
- Pipeline execution statistics
- System resource utilization

## Proposed Structure

```
metrics/
├── training/
│   ├── experiment_001/
│   │   ├── loss_curves.json
│   │   ├── validation_metrics.json
│   │   └── hyperparameters.yaml
│   └── experiment_002/
│       └── ...
├── inference/
│   ├── daily_stats.csv
│   ├── weekly_summary.json
│   └── model_performance.json
├── evaluation/
│   ├── map_scores.json
│   ├── per_class_metrics.json
│   └── confusion_matrices/
└── system/
    ├── gpu_utilization.csv
    └── memory_usage.csv
```

## Metrics to Track

### Training Metrics
- Loss per epoch (training and validation)
- Learning rate schedule
- mAP scores over time
- Training time per epoch
- Batch processing time
- GPU memory usage

### Inference Metrics
- Inference time per image
- Throughput (images/second)
- Detection count statistics
- Confidence score distributions
- NMS effectiveness

### Evaluation Metrics
- mAP@50, mAP@75, mAP@50:95
- Precision and recall per class
- F1 scores
- True/false positive rates
- Confusion matrices

### Pipeline Metrics
- Stage execution times
- End-to-end processing time
- Prolog query performance
- Symbolic rule application frequency
- Success/failure rates

## File Formats

### JSON Format (Recommended)
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "model": "yolov11m-obb",
  "experiment_id": "exp_001",
  "metrics": {
    "mAP@50": 0.756,
    "mAP@75": 0.632,
    "mAP@50:95": 0.543,
    "inference_time_ms": 45.2,
    "detection_count": 127
  }
}
```

### CSV Format (For Time Series)
```csv
timestamp,model,epoch,train_loss,val_loss,mAP@50,learning_rate
2024-01-15 10:00:00,yolov11m,1,0.532,0.498,0.421,0.001
2024-01-15 10:15:00,yolov11m,2,0.456,0.423,0.512,0.001
```

## Usage Examples

### Logging Metrics (Python)
```python
import json
from datetime import datetime
from pathlib import Path

def log_evaluation_metrics(metrics_dict, output_dir='monitoring/metrics/evaluation'):
    """Log evaluation metrics to JSON file."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().isoformat()
    metrics_dict['timestamp'] = timestamp
    
    filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_path / filename, 'w') as f:
        json.dump(metrics_dict, f, indent=2)
```

### Reading Metrics
```python
import json
from pathlib import Path

def load_latest_metrics(metrics_dir='monitoring/metrics/evaluation'):
    """Load the most recent metrics file."""
    metrics_path = Path(metrics_dir)
    metric_files = sorted(metrics_path.glob('*.json'))
    
    if not metric_files:
        return None
    
    with open(metric_files[-1], 'r') as f:
        return json.load(f)
```

## Visualization

Metrics can be visualized using:
- **Matplotlib**: For static plots
- **Plotly**: For interactive dashboards
- **TensorBoard**: For training visualization
- **Grafana**: For real-time monitoring

## Integration Points

- **Pipeline**: Emits metrics after each stage
- **Training**: Logs metrics every epoch
- **Evaluation**: Saves comprehensive evaluation results
- **Backend**: Provides API endpoints to query metrics
- **Frontend**: Displays metrics in dashboards

## Retention Policy

Recommended retention:
- **Recent metrics**: Keep all data for last 30 days
- **Historical metrics**: Aggregate to daily summaries after 30 days
- **Long-term storage**: Keep monthly summaries indefinitely

## Related

- See [Monitoring README](../README.md) for overall monitoring strategy
- See [Backend README](../../backend/README.md) for metrics API endpoints
- See [Frontend README](../../frontend/README.md) for visualization
