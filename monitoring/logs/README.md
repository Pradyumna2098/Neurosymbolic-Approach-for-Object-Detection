# Logs Directory

This directory stores application logs, error traces, and system logs for debugging and monitoring.

## Purpose

Capture and organize:
- Application execution logs
- Error traces and stack traces
- System resource logs
- API request/response logs
- Pipeline stage execution logs

## Proposed Structure

```
logs/
├── application/
│   ├── pipeline.log
│   ├── training.log
│   ├── inference.log
│   └── symbolic.log
├── errors/
│   ├── error.log
│   └── critical.log
├── api/
│   ├── access.log
│   └── api_errors.log
├── system/
│   ├── gpu.log
│   ├── memory.log
│   └── disk_io.log
└── archived/
    └── YYYY-MM-DD/
```

## Log Levels

Use standard Python logging levels:
- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potentially harmful situations
- **ERROR**: Error messages for failures that don't stop execution
- **CRITICAL**: Critical errors that may cause program termination

## Log Format

### Structured Logging (Recommended)
```
2024-01-15 10:30:45,123 - pipeline.core.preprocess - INFO - Processing 150 images
2024-01-15 10:30:46,456 - pipeline.core.preprocess - INFO - NMS completed: 1243 -> 856 detections
2024-01-15 10:30:50,789 - pipeline.core.symbolic - INFO - Applied 23 confidence adjustments
2024-01-15 10:30:55,012 - pipeline.core.eval - INFO - mAP@50: 0.756, mAP@75: 0.632
```

### JSON Structured Logging (Alternative)
```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "module": "pipeline.core.preprocess",
  "message": "Processing 150 images",
  "context": {
    "batch_size": 16,
    "device": "cuda:0"
  }
}
```

## Configuration

### Python Logging Setup
```python
import logging
from pathlib import Path

def setup_logging(log_dir='monitoring/logs'):
    """Configure logging for the application."""
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path / 'application' / 'app.log'),
            logging.StreamHandler()  # Also print to console
        ]
    )
    
    # Create separate logger for errors
    error_logger = logging.getLogger('errors')
    error_handler = logging.FileHandler(log_path / 'errors' / 'error.log')
    error_handler.setLevel(logging.ERROR)
    error_logger.addHandler(error_handler)
```

### Usage in Code
```python
import logging

logger = logging.getLogger(__name__)

def process_pipeline(config):
    """Execute pipeline with logging."""
    logger.info(f"Starting pipeline with config: {config['name']}")
    
    try:
        # Pipeline execution
        result = run_preprocessing(config)
        logger.info(f"Preprocessing completed: {len(result)} detections")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        raise
    
    logger.info("Pipeline completed successfully")
    return result
```

## Log Rotation

Prevent log files from growing indefinitely:

```python
from logging.handlers import RotatingFileHandler

# Rotate when file reaches 10MB, keep 5 backup files
handler = RotatingFileHandler(
    'monitoring/logs/application/app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

Or use time-based rotation:

```python
from logging.handlers import TimedRotatingFileHandler

# Rotate daily, keep 30 days of logs
handler = TimedRotatingFileHandler(
    'monitoring/logs/application/app.log',
    when='midnight',
    interval=1,
    backupCount=30
)
```

## Log Analysis

### Searching Logs
```bash
# Find all errors
grep "ERROR" monitoring/logs/application/pipeline.log

# Find specific issues
grep "FileNotFoundError" monitoring/logs/errors/error.log

# Count occurrences
grep -c "CRITICAL" monitoring/logs/application/app.log
```

### Monitoring Patterns
```bash
# Watch logs in real-time
tail -f monitoring/logs/application/pipeline.log

# Filter for specific level
tail -f monitoring/logs/application/app.log | grep "ERROR"
```

## What to Log

### Training Stage
- Model configuration loaded
- Training start/end times
- Epoch progress and metrics
- Checkpoint saves
- Validation results
- Early stopping triggers

### Inference Stage
- Model loading
- Batch processing progress
- Per-image inference time
- Total detections count
- Output file generation

### Pipeline Stage
- Configuration loaded
- Each stage start/end
- Detection counts per stage
- Prolog query results
- Evaluation metrics

### Errors to Log
- File not found errors
- Configuration errors
- Model loading failures
- Out of memory errors
- CUDA errors
- Prolog query failures
- Unexpected exceptions

## Security Considerations

- **Never log sensitive data**: API keys, passwords, tokens
- **Sanitize user input** in logs to prevent injection
- **Limit personal information** (PII) in logs
- **Secure log files** with appropriate permissions

## Monitoring and Alerts

Set up alerts for:
- Critical errors appearing in logs
- High error rates
- Unusual patterns (e.g., repeated failures)
- Performance degradation

## Related

- See [Monitoring README](../README.md) for overall strategy
- See [Metrics README](../metrics/README.md) for performance metrics
- See Python's [logging documentation](https://docs.python.org/3/library/logging.html)
