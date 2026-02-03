# Windows Executable User Guide - Neurosymbolic Object Detection

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Common Workflows](#common-workflows)
7. [Troubleshooting](#troubleshooting)
8. [Performance Tips](#performance-tips)
9. [Monitoring](#monitoring)
10. [FAQ](#faq)
11. [Getting Help](#getting-help)

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **Operating System** | Windows 10 (64-bit) or later |
| **Processor** | Intel Core i5 or AMD Ryzen 5 (4+ cores) |
| **RAM** | 8 GB |
| **Storage** | 10 GB free space |
| **Display** | 1280x720 resolution |

### Recommended Requirements

| Component | Requirement |
|-----------|-------------|
| **Operating System** | Windows 11 (64-bit) |
| **Processor** | Intel Core i7/i9 or AMD Ryzen 7/9 (8+ cores) |
| **RAM** | 16 GB or more |
| **GPU** | NVIDIA GPU with 6GB+ VRAM (RTX 3060 or better) |
| **Storage** | 20 GB free space (SSD recommended) |
| **Display** | 1920x1080 or higher resolution |

### External Dependencies

#### **SWI-Prolog (REQUIRED)**

The application requires SWI-Prolog for symbolic reasoning capabilities.

- **Version**: 8.4.x or later
- **Download**: https://www.swi-prolog.org/download/stable
- **Size**: ~150 MB
- **Installation Time**: 2-5 minutes

#### **NVIDIA GPU Drivers (Optional, for GPU acceleration)**

For GPU-accelerated inference:

- **NVIDIA Driver**: Latest stable version for your GPU
- **Download**: https://www.nvidia.com/Download/index.aspx
- **CUDA Support**: Version 11.8 or 12.1 recommended

### Disk Space Breakdown

- **Application**: 800 MB - 2 GB (depending on CPU vs GPU version)
- **SWI-Prolog**: ~150 MB
- **Models** (not included): 100-500 MB per model
- **Datasets** (not included): Varies by dataset size
- **Working Files**: 1-5 GB (predictions, knowledge graphs, logs)

**Total Recommended**: 10-20 GB free space

---

## Installation

### Step 1: Download the Application

1. Download the latest release package:
   - **CPU Version**: `NeurosymbolicApp_CPU_v1.0.zip` (~800 MB)
   - **GPU Version**: `NeurosymbolicApp_GPU_v1.0.zip` (~2 GB)

2. Verify download integrity (optional but recommended):
   ```batch
   certutil -hashfile NeurosymbolicApp_CPU_v1.0.zip SHA256
   ```
   Compare with published checksum.

3. Extract to your preferred location:
   - Right-click → "Extract All..."
   - Choose destination (e.g., `C:\Programs\NeurosymbolicApp\`)
   - Click "Extract"

### Step 2: Install SWI-Prolog

**CRITICAL**: The application will not work without SWI-Prolog.

1. **Download SWI-Prolog**:
   - Visit: https://www.swi-prolog.org/download/stable
   - Download Windows 64-bit installer: `swipl-X.Y.Z-1.x64.exe`

2. **Run the Installer**:
   - Double-click the downloaded `.exe` file
   - Click "Next" through the wizard
   - **IMPORTANT**: Check "Add swipl to the system PATH for all users"
   - Click "Install"
   - Wait for installation to complete (~2-5 minutes)
   - Click "Finish"

3. **Verify Installation**:
   - Open Command Prompt (Win+R, type `cmd`, Enter)
   - Type: `swipl --version`
   - You should see output like: `SWI-Prolog version 8.4.3`
   
   **If error occurs**, see [Troubleshooting - SWI-Prolog Not Found](#swiprolog-not-found)

### Step 3: Install GPU Drivers (Optional)

**Only for GPU version and if you have an NVIDIA GPU**:

1. **Check Current Driver**:
   - Open NVIDIA Control Panel or GeForce Experience
   - Note your current driver version

2. **Update if Needed**:
   - Visit: https://www.nvidia.com/Download/index.aspx
   - Select your GPU model
   - Download and install latest driver
   - Restart computer after installation

3. **Verify CUDA**:
   - Open Command Prompt
   - Navigate to application folder:
     ```batch
     cd C:\Programs\NeurosymbolicApp
     ```
   - Run verification (if provided):
     ```batch
     neurosymbolic-pipeline.exe --check-gpu
     ```

### Step 4: Prepare Workspace

1. **Create Data Directories**:
   ```batch
   mkdir C:\NeurosymbolicData\datasets
   mkdir C:\NeurosymbolicData\models
   mkdir C:\NeurosymbolicData\predictions
   mkdir C:\NeurosymbolicData\results
   ```

2. **Copy Sample Configuration**:
   - Navigate to installation folder
   - Open `configs\` folder
   - Copy `pipeline_example.yaml` to `C:\NeurosymbolicData\my_config.yaml`

3. **Download Models** (if needed):
   - Download pre-trained YOLOv11 models
   - Place in `C:\NeurosymbolicData\models\`

---

## Quick Start

### First-Time Setup

1. **Open Command Prompt**:
   - Press Win+R
   - Type `cmd` and press Enter

2. **Navigate to Application**:
   ```batch
   cd C:\Programs\NeurosymbolicApp
   ```

3. **Verify Installation**:
   ```batch
   neurosymbolic-pipeline.exe --help
   ```
   
   You should see the help message with available commands.

### Running Your First Pipeline

1. **Prepare Configuration**:
   
   Edit `C:\NeurosymbolicData\my_config.yaml`:
   ```yaml
   # Input/Output Paths
   raw_predictions_dir: C:\NeurosymbolicData\predictions\raw
   nms_predictions_dir: C:\NeurosymbolicData\predictions\nms
   refined_predictions_dir: C:\NeurosymbolicData\predictions\refined
   ground_truth_dir: C:\NeurosymbolicData\datasets\test\labels
   
   # Prolog Rules
   rules_file: C:\Programs\NeurosymbolicApp\pipeline\prolog\rules.pl
   
   # Output
   report_file: C:\NeurosymbolicData\results\report.csv
   
   # Parameters
   nms_iou_threshold: 0.5
   ```

2. **Run Pipeline**:
   ```batch
   cd C:\Programs\NeurosymbolicApp
   neurosymbolic-pipeline.exe --config C:\NeurosymbolicData\my_config.yaml
   ```

3. **Check Results**:
   - Open `C:\NeurosymbolicData\results\report.csv`
   - View processed predictions in output folders

---

## Configuration

### Configuration File Structure

Configuration files use YAML format. Create or edit with a text editor (Notepad++, VS Code, or even Notepad).

### Example Training Configuration

`training_config.yaml`:
```yaml
# Model Configuration
model:
  architecture: yolov11
  variant: yolov11m-obb  # Options: yolov11n, s, m, l, x
  weights: null           # null for training from scratch

# Dataset Paths (use absolute paths)
data:
  yaml_path: C:\NeurosymbolicData\datasets\dota.yaml
  train_dir: C:\NeurosymbolicData\datasets\train\images
  val_dir: C:\NeurosymbolicData\datasets\val\images

# Training Parameters
training:
  epochs: 100
  batch_size: 16  # Reduce if out of memory
  learning_rate: 0.001
  device: cuda    # Change to 'cpu' if no GPU
  seed: 42        # For reproducible results

# Output Paths
output:
  project_dir: C:\NeurosymbolicData\training_output
  experiment_name: my_experiment_001
```

### Example Inference Configuration

`prediction_config.yaml`:
```yaml
# Model Path
model:
  model_path: C:\NeurosymbolicData\models\best.pt
  confidence_threshold: 0.25
  iou_threshold: 0.45

# SAHI Settings (for large images)
sahi:
  slice_width: 640
  slice_height: 640
  overlap_ratio: 0.2

# Input/Output
data:
  test_images_dir: C:\NeurosymbolicData\datasets\test\images
  output_predictions_dir: C:\NeurosymbolicData\predictions\raw

# Device
inference:
  device: cuda  # or 'cpu'
  batch_size: 8
```

### Configuration Best Practices

1. **Use Absolute Paths**: Always use full paths (e.g., `C:\Path\To\File`)
   - ❌ Bad: `../data/images`
   - ✅ Good: `C:\NeurosymbolicData\datasets\images`

2. **Create Directories First**: Ensure all paths exist before running
   ```batch
   mkdir C:\NeurosymbolicData\predictions\raw
   ```

3. **Backslashes in Paths**: Windows uses backslashes (`\`)
   - YAML accepts both `\` and `/`
   - Forward slashes work: `C:/Data/images`

4. **Check File Locations**: Verify model files exist at specified paths

5. **GPU vs CPU**: Set `device: cpu` if you don't have NVIDIA GPU

---

## Running the Application

### Command-Line Interface

The application is command-line based. All operations are performed via Command Prompt.

#### Opening Command Prompt

**Method 1**: Windows Search
- Press Win key
- Type "cmd" or "Command Prompt"
- Press Enter

**Method 2**: Run Dialog
- Press Win+R
- Type `cmd`
- Press Enter

**Method 3**: From File Explorer
- Navigate to `C:\Programs\NeurosymbolicApp`
- Click in the address bar
- Type `cmd` and press Enter

### Available Commands

#### 1. Training Command

Train a new YOLO model:

```batch
cd C:\Programs\NeurosymbolicApp
neurosymbolic-training.exe --config C:\NeurosymbolicData\training_config.yaml
```

**Duration**: Several hours (depends on dataset size and GPU)

**Output**: 
- Trained model weights
- Training logs
- Loss curves
- Validation metrics

#### 2. Inference Command

Run predictions on images:

```batch
neurosymbolic-prediction.exe --config C:\NeurosymbolicData\prediction_config.yaml
```

**Duration**: Seconds to minutes (depends on image count and size)

**Output**:
- YOLO format predictions (.txt files)
- One file per image

#### 3. Symbolic Pipeline Command

Apply NMS filtering and Prolog reasoning:

```batch
neurosymbolic-pipeline.exe --config C:\NeurosymbolicData\pipeline_config.yaml
```

**Stages**:
1. **Preprocess**: NMS filtering
2. **Symbolic**: Prolog confidence adjustment
3. **Evaluation**: Compute mAP metrics

**Duration**: Minutes (depends on prediction count)

**Output**:
- Filtered predictions
- Refined predictions
- Evaluation report

#### 4. Knowledge Graph Command

Extract spatial relationships:

```batch
neurosymbolic-kg.exe --config C:\NeurosymbolicData\kg_config.yaml
```

**Output**:
- Prolog facts
- Graph visualizations
- Relationship statistics

### Command-Line Arguments

#### Global Arguments

All commands support:

```batch
--help          # Display help message
--version       # Show version information
--config PATH   # Path to configuration file
--verbose       # Enable verbose output
--quiet         # Suppress non-error output
```

#### Examples

**Display Help**:
```batch
neurosymbolic-pipeline.exe --help
```

**Verbose Execution**:
```batch
neurosymbolic-pipeline.exe --config config.yaml --verbose
```

**Check Version**:
```batch
neurosymbolic-pipeline.exe --version
```

### Progress Monitoring

During execution, you'll see:

```
[INFO] Starting neurosymbolic pipeline...
[INFO] Loading configuration from: C:\NeurosymbolicData\pipeline_config.yaml
[INFO] Stage 1/3: Preprocessing
[INFO] Applying NMS filtering...
[INFO] Processed 150 images
[INFO] Stage 2/3: Symbolic Reasoning
[INFO] Loading Prolog rules...
[INFO] Adjusting confidence scores...
[INFO] Stage 3/3: Evaluation
[INFO] Computing mAP metrics...
[INFO] mAP@50: 0.756
[INFO] Pipeline completed successfully!
```

### Stopping Execution

To stop a running command:

- Press **Ctrl+C** in the Command Prompt window
- Confirm termination if prompted
- Wait for graceful shutdown

---

## Common Workflows

### Workflow 1: Training a Model from Scratch

**Time Required**: 3-8 hours (GPU), 1-3 days (CPU)

**Steps**:

1. **Prepare Dataset**:
   - Organize images and labels in YOLO format
   - Create `dota.yaml` configuration file
   - Validate dataset structure

2. **Create Training Config**:
   ```yaml
   # training_config.yaml
   model:
     architecture: yolov11
     variant: yolov11m-obb
   
   data:
     yaml_path: C:\NeurosymbolicData\datasets\dota.yaml
   
   training:
     epochs: 100
     batch_size: 16
     device: cuda
   
   output:
     project_dir: C:\NeurosymbolicData\training
     experiment_name: exp001
   ```

3. **Start Training**:
   ```batch
   neurosymbolic-training.exe --config training_config.yaml
   ```

4. **Monitor Progress**:
   - Watch console output for loss values
   - Check `training\exp001\` for intermediate results
   - Training checkpoints saved every N epochs

5. **Retrieve Trained Model**:
   - Best model: `training\exp001\weights\best.pt`
   - Last model: `training\exp001\weights\last.pt`

### Workflow 2: Running Inference on Test Images

**Time Required**: 5-30 minutes (depends on image count)

**Steps**:

1. **Prepare Images**:
   - Place test images in a folder
   - Example: `C:\NeurosymbolicData\test_images\`

2. **Create Prediction Config**:
   ```yaml
   # prediction_config.yaml
   model:
     model_path: C:\NeurosymbolicData\models\best.pt
     confidence_threshold: 0.25
   
   data:
     test_images_dir: C:\NeurosymbolicData\test_images
     output_predictions_dir: C:\NeurosymbolicData\predictions\raw
   
   inference:
     device: cuda
   ```

3. **Run Inference**:
   ```batch
   neurosymbolic-prediction.exe --config prediction_config.yaml
   ```

4. **Check Results**:
   - Predictions: `predictions\raw\image001.txt`
   - Format: `class_id cx cy width height confidence`

### Workflow 3: Full Symbolic Pipeline

**Time Required**: 10-60 minutes

**Steps**:

1. **Run Inference** (if not done):
   - Generate predictions as in Workflow 2
   - Ensure predictions in `predictions\raw\`

2. **Prepare Ground Truth**:
   - Place ground truth labels in folder
   - Same format as predictions (YOLO)

3. **Create Pipeline Config**:
   ```yaml
   # pipeline_config.yaml
   raw_predictions_dir: C:\NeurosymbolicData\predictions\raw
   nms_predictions_dir: C:\NeurosymbolicData\predictions\nms
   refined_predictions_dir: C:\NeurosymbolicData\predictions\refined
   ground_truth_dir: C:\NeurosymbolicData\datasets\test\labels
   rules_file: C:\Programs\NeurosymbolicApp\pipeline\prolog\rules.pl
   report_file: C:\NeurosymbolicData\results\report.csv
   nms_iou_threshold: 0.5
   ```

4. **Run Pipeline**:
   ```batch
   neurosymbolic-pipeline.exe --config pipeline_config.yaml
   ```

5. **Review Results**:
   - NMS filtered: `predictions\nms\`
   - Refined: `predictions\refined\`
   - Evaluation: `results\report.csv`

### Workflow 4: Knowledge Graph Construction

**Time Required**: 5-20 minutes

**Steps**:

1. **Prepare Predictions**:
   - Use NMS-filtered or refined predictions
   - Ensure predictions available

2. **Create KG Config**:
   ```yaml
   # kg_config.yaml
   predictions_dir: C:\NeurosymbolicData\predictions\nms
   output_dir: C:\NeurosymbolicData\knowledge_graphs
   prolog_facts_dir: C:\NeurosymbolicData\prolog_facts
   visualization_dir: C:\NeurosymbolicData\visualizations
   ```

3. **Run KG Builder**:
   ```batch
   neurosymbolic-kg.exe --config kg_config.yaml
   ```

4. **Explore Outputs**:
   - Prolog facts: `prolog_facts\image001_facts.pl`
   - Visualizations: `visualizations\image001_graph.png`
   - Statistics: `knowledge_graphs\statistics.json`

---

## Troubleshooting

### SWI-Prolog Not Found

**Symptom**: 
```
Error: SWI-Prolog not found. Please install SWI-Prolog.
```

**Solutions**:

1. **Verify Installation**:
   ```batch
   where swipl
   ```
   Should show: `C:\Program Files\swipl\bin\swipl.exe`

2. **Add to PATH Manually**:
   - Open System Properties → Advanced → Environment Variables
   - Edit "Path" variable
   - Add: `C:\Program Files\swipl\bin`
   - Click OK
   - **Restart Command Prompt**

3. **Reinstall SWI-Prolog**:
   - Uninstall current version
   - Download fresh installer
   - During installation, check "Add to PATH"

4. **Verify After Fix**:
   ```batch
   swipl --version
   ```

### CUDA Not Available (GPU Version)

**Symptom**:
```
Warning: CUDA not available, falling back to CPU
```

**Solutions**:

1. **Check GPU Exists**:
   - Open Task Manager → Performance tab
   - Verify GPU is listed and working

2. **Update NVIDIA Drivers**:
   - Download from: https://www.nvidia.com/Download/index.aspx
   - Install latest driver
   - Restart computer

3. **Verify CUDA Installation**:
   ```batch
   nvidia-smi
   ```
   Should show GPU information

4. **Use CPU Version** (if GPU not available):
   - Edit configuration: `device: cpu`
   - Performance will be slower but functional

### Out of Memory Errors

**Symptom**:
```
RuntimeError: CUDA out of memory
```
or
```
MemoryError: Unable to allocate array
```

**Solutions**:

1. **Reduce Batch Size**:
   - Edit config: `batch_size: 8` → `batch_size: 4` or `batch_size: 1`

2. **Use CPU for Large Batches**:
   - Edit config: `device: cpu`

3. **Close Other Applications**:
   - Close browser, applications using memory
   - Free up RAM/VRAM

4. **Restart Computer**:
   - Fresh start releases all memory

5. **Process Images in Smaller Batches**:
   - Split test images into multiple folders
   - Process each folder separately

### Configuration File Errors

**Symptom**:
```
Error: Unable to parse configuration file
YAMLError: Invalid syntax at line 15
```

**Solutions**:

1. **Check YAML Syntax**:
   - Use proper indentation (2 spaces)
   - No tabs, only spaces
   - Colons followed by space: `key: value`

2. **Validate Paths**:
   - Use absolute paths
   - Check paths exist: `dir C:\Path\To\Folder`

3. **Use Text Editor**:
   - Edit with Notepad++, VS Code, or Sublime
   - Avoid Microsoft Word (adds formatting)

4. **Check Example Config**:
   - Compare with provided examples
   - Copy structure, change only paths

### File Not Found Errors

**Symptom**:
```
FileNotFoundError: Model file not found: C:\...\best.pt
```

**Solutions**:

1. **Verify File Exists**:
   ```batch
   dir C:\NeurosymbolicData\models\best.pt
   ```

2. **Check Path in Config**:
   - Ensure path is correct
   - Check for typos

3. **Use Absolute Paths**:
   - Don't use relative paths like `..\models\best.pt`
   - Use full path: `C:\NeurosymbolicData\models\best.pt`

### Slow Performance

**Symptom**: Inference/training very slow

**Solutions**:

1. **Enable GPU**:
   - Check config: `device: cuda`
   - Verify GPU working: `nvidia-smi`

2. **Use Smaller Model**:
   - `yolov11n` (fastest) instead of `yolov11x` (most accurate)

3. **Reduce Image Size**:
   - Resize large images before processing

4. **Close Background Apps**:
   - Free up CPU/GPU resources

5. **Use SSD**:
   - Store data on SSD instead of HDD

### Application Won't Start

**Symptom**: Double-clicking `.exe` does nothing or crashes immediately

**Solutions**:

1. **Run from Command Prompt**:
   - See error messages in console
   - Don't double-click, use `cmd`

2. **Check Antivirus**:
   - Antivirus may block executable
   - Add exception for application folder

3. **Missing Dependencies**:
   - Install SWI-Prolog
   - Install Microsoft Visual C++ Redistributable
   - Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe

4. **Run as Administrator**:
   - Right-click executable
   - Select "Run as administrator"

### Predictions are Empty

**Symptom**: Prediction files are empty or contain no detections

**Solutions**:

1. **Lower Confidence Threshold**:
   - Edit config: `confidence_threshold: 0.25` → `0.1`

2. **Check Model**:
   - Verify model is trained on similar data
   - Check model file is not corrupted

3. **Verify Input Images**:
   - Images are readable
   - Images are in supported format (JPG, PNG)

4. **Check Image Size**:
   - Very large images may need SAHI slicing
   - Very small images may not work well

---

## Performance Tips

### For Training

1. **Use GPU**: 10-50x faster than CPU
   - `device: cuda` in config

2. **Optimal Batch Size**: 
   - GPU: 16-32 (adjust based on VRAM)
   - CPU: 4-8

3. **Enable Mixed Precision**:
   - Faster training, less memory
   - Automatically used with modern GPUs

4. **Use SSD Storage**:
   - Faster data loading
   - Significant improvement for large datasets

5. **Close Unnecessary Applications**:
   - Free up GPU/CPU resources

### For Inference

1. **Batch Processing**:
   - Process multiple images at once
   - `batch_size: 8` or higher

2. **Use Appropriate Model Size**:
   - `yolov11n`: Fastest, less accurate
   - `yolov11m`: Balanced
   - `yolov11x`: Slowest, most accurate

3. **Adjust SAHI Settings**:
   - Larger slices = faster, may miss small objects
   - `slice_width: 1024` instead of `640`

4. **Lower Resolution**:
   - Resize images to 1024px or 1280px max dimension
   - Maintains good accuracy with faster processing

### For Large Datasets

1. **Process in Batches**:
   - Split dataset into folders (1000 images each)
   - Process each folder separately

2. **Use SSD for Working Files**:
   - Store predictions and intermediate files on SSD

3. **Increase RAM**:
   - 16GB+ recommended for large datasets

4. **Monitor Resources**:
   - Use Task Manager to check CPU/GPU/Memory usage

---

## Monitoring

### Application Logs

Logs are saved to:
```
C:\Programs\NeurosymbolicApp\logs\app.log
```

View recent logs:
```batch
type C:\Programs\NeurosymbolicApp\logs\app.log
```

View last 50 lines:
```batch
powershell Get-Content C:\Programs\NeurosymbolicApp\logs\app.log -Tail 50
```

### Prometheus Metrics (Optional)

If Prometheus integration is enabled:

1. **Access Metrics**:
   - Open browser: http://localhost:8000/metrics
   - View raw metrics in Prometheus format

2. **Install Prometheus Server** (separate):
   - Download from: https://prometheus.io/download/
   - Configure to scrape application metrics
   - View dashboards in Grafana

3. **Key Metrics to Monitor**:
   - Training loss and validation mAP
   - Inference time and throughput
   - GPU memory usage
   - Error rates

See [PROMETHEUS_INTEGRATION_GUIDE.md](PROMETHEUS_INTEGRATION_GUIDE.md) for detailed setup.

### Task Manager Monitoring

Monitor resource usage:

1. **Open Task Manager**: Ctrl+Shift+Esc

2. **Performance Tab**:
   - CPU usage
   - Memory usage
   - GPU usage (under GPU 0)

3. **Processes Tab**:
   - Find `neurosymbolic-pipeline.exe`
   - Check memory and CPU usage

### GPU Monitoring

For NVIDIA GPUs:

```batch
nvidia-smi
```

Shows:
- GPU utilization
- Memory usage
- Temperature
- Running processes

Continuous monitoring:
```batch
nvidia-smi -l 1
```
Updates every second (Ctrl+C to stop)

---

## FAQ

### Q1: Do I need programming knowledge to use this application?

**A**: No programming knowledge is required for basic usage. You need to:
- Edit text configuration files (similar to editing a document)
- Run commands in Command Prompt (copy-paste commands)
- Understand file paths and folder structures

### Q2: Can I use this on Windows 7 or 8?

**A**: No, Windows 10 64-bit or later is required. Some dependencies don't support older Windows versions.

### Q3: How large can my dataset be?

**A**: There's no hard limit, but consider:
- **Small** (100-1000 images): Works on any configuration
- **Medium** (1000-10000 images): Recommended 16GB RAM
- **Large** (10000+ images): Consider processing in batches, 32GB+ RAM recommended

### Q4: Can I train on CPU?

**A**: Yes, but it's very slow:
- GPU: 2-8 hours for typical training
- CPU: 1-3 days for same training

CPU is fine for small experiments, not practical for production.

### Q5: What image formats are supported?

**A**: Supported formats:
- JPG/JPEG (recommended)
- PNG
- BMP
- TIFF

### Q6: How do I update the application?

**A**: 
1. Download new version
2. Extract to new folder (or replace old files)
3. Keep your data and config files separate
4. Test with sample data before full migration

### Q7: Can I run multiple instances simultaneously?

**A**: Yes, but:
- Use different configuration files
- Use different output directories
- Monitor resource usage (GPU/CPU/Memory)
- Batch size should be reduced if running multiple instances

### Q8: Is internet connection required?

**A**: No, once installed and models downloaded:
- Application runs offline
- No data is sent to external servers
- Prometheus metrics are local only

### Q9: Where is my data stored?

**A**: All data stays on your computer:
- Application: Installation folder
- Your data: Locations specified in config files
- No cloud upload or external storage

### Q10: Can I use custom YOLO models?

**A**: Yes! Use any YOLOv11-OBB model:
- Trained by you
- Downloaded from others
- Pre-trained models
- Just specify path in config: `model_path: C:\Path\To\your_model.pt`

---

## Getting Help

### Documentation

- **Windows Packaging Guide**: [WINDOWS_PACKAGING_GUIDE.md](WINDOWS_PACKAGING_GUIDE.md)
- **Prometheus Integration**: [PROMETHEUS_INTEGRATION_GUIDE.md](PROMETHEUS_INTEGRATION_GUIDE.md)
- **Full Repository README**: https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection

### Common Issues

Check [Troubleshooting](#troubleshooting) section first for:
- Installation problems
- Configuration errors
- Performance issues
- Error messages

### Support Channels

1. **GitHub Issues**: 
   - Report bugs: https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection/issues
   - Search existing issues first
   - Provide error messages and configuration

2. **Discussions**:
   - General questions
   - Feature requests
   - Share experiences

### Providing Debug Information

When reporting issues, include:

1. **System Information**:
   ```batch
   systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
   ```

2. **Application Version**:
   ```batch
   neurosymbolic-pipeline.exe --version
   ```

3. **Error Message**:
   - Copy full error text
   - Include preceding context

4. **Configuration** (remove sensitive paths):
   - Anonymize personal information
   - Include relevant config sections

5. **SWI-Prolog Version**:
   ```batch
   swipl --version
   ```

6. **GPU Info** (if using GPU):
   ```batch
   nvidia-smi
   ```

### Best Practices for Reporting Issues

✅ **Good Bug Report**:
```
**Environment:**
- Windows 11 64-bit
- Application version: 1.0.0
- SWI-Prolog version: 8.4.3
- GPU: NVIDIA RTX 3060

**Issue:**
Application crashes during symbolic pipeline stage with error:
"PrologError: rule file not found"

**Configuration:**
rules_file: C:\App\pipeline\prolog\rules.pl

**Steps to Reproduce:**
1. Run: neurosymbolic-pipeline.exe --config my_config.yaml
2. Crashes at "Stage 2: Symbolic Reasoning"

**Expected:** Pipeline should complete successfully
**Actual:** Crashes with error message

**Logs:** (attached)
```

❌ **Poor Bug Report**:
```
It doesn't work. Help!
```

---

## Appendix: Keyboard Shortcuts

### Command Prompt

- **Ctrl+C**: Stop running command
- **Ctrl+A**: Select all text
- **Ctrl+F**: Find text (Windows 10+)
- **Ctrl+V**: Paste text
- **↑ / ↓**: Navigate command history
- **Tab**: Auto-complete file/folder names

### Windows File Explorer

- **Ctrl+C**: Copy
- **Ctrl+V**: Paste
- **Ctrl+X**: Cut
- **Ctrl+A**: Select all
- **F2**: Rename
- **Delete**: Move to Recycle Bin
- **Shift+Delete**: Permanent delete (careful!)

---

## Appendix: Quick Command Reference

### Navigation
```batch
# Change directory
cd C:\Programs\NeurosymbolicApp

# Go up one level
cd ..

# List files in current directory
dir

# Create directory
mkdir my_folder
```

### File Operations
```batch
# Copy file
copy source.txt destination.txt

# Move file
move source.txt C:\Destination\

# Delete file
del unwanted_file.txt

# View file contents
type file.txt
```

### Application Commands
```batch
# Help
neurosymbolic-pipeline.exe --help

# Training
neurosymbolic-training.exe --config training_config.yaml

# Inference
neurosymbolic-prediction.exe --config prediction_config.yaml

# Pipeline
neurosymbolic-pipeline.exe --config pipeline_config.yaml

# Knowledge Graph
neurosymbolic-kg.exe --config kg_config.yaml

# Version
neurosymbolic-pipeline.exe --version
```

---

## Conclusion

This guide covered the essential information for installing, configuring, and running the Neurosymbolic Object Detection application on Windows.

**Key Takeaways**:
- ✅ Install SWI-Prolog (required)
- ✅ Use absolute paths in configuration files
- ✅ Run commands from Command Prompt
- ✅ Check troubleshooting section for common issues
- ✅ GPU is optional but highly recommended
- ✅ All data stays on your local machine

For advanced packaging or integration, see:
- [WINDOWS_PACKAGING_GUIDE.md](WINDOWS_PACKAGING_GUIDE.md) - For developers packaging the application
- [PROMETHEUS_INTEGRATION_GUIDE.md](PROMETHEUS_INTEGRATION_GUIDE.md) - For monitoring and metrics

**Happy Detecting! 🚀**
