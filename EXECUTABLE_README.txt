# Neurosymbolic Object Detection - Standalone Executable

This is a standalone distribution of the Neurosymbolic Object Detection Backend API, packaged with PyInstaller.

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11 (64-bit)
- **RAM**: 8 GB (16 GB recommended for GPU)
- **Disk Space**: 5 GB free space
- **Python**: NOT required (bundled in executable)

### External Dependencies (REQUIRED)

#### SWI-Prolog (Required for Symbolic Reasoning)
**Version**: 8.4.x or later

**Download**: https://www.swi-prolog.org/download/stable

**Installation**:
1. Download the Windows installer: `swipl-X.Y.Z-1.x64.exe`
2. Run the installer
3. **IMPORTANT**: Check "Add to PATH" during installation
4. Verify installation: Open Command Prompt and type `swipl --version`

**Why Required**: The symbolic reasoning component uses Prolog for confidence adjustment. This cannot be bundled in the executable and must be installed separately.

### Optional Dependencies

#### NVIDIA GPU Drivers (Optional, for GPU Acceleration)
**Required For**: GPU-accelerated inference (faster processing)

**Download**: https://www.nvidia.com/Download/index.aspx

**Minimum Driver Version**:
- For CUDA 11.8: Driver 450.80.02 or later
- For CUDA 12.1: Driver 525.60.13 or later

**Note**: Only needed if you have an NVIDIA GPU and want to use GPU acceleration. The application works fine on CPU.

#### Microsoft Visual C++ Redistributable
Usually pre-installed on Windows. If you get DLL errors, download from:
https://aka.ms/vs/17/release/vc_redist.x64.exe

---

## Quick Start

### 1. Install SWI-Prolog
Download and install from https://www.swi-prolog.org/download/stable

### 2. Run the Application

**Option A: Default Configuration**
```batch
neurosymbolic-backend.exe
```

The API will start on `http://localhost:8000`

**Option B: Custom Configuration**
```batch
# Set environment variables
set DATA_ROOT=C:\path\to\data
set MODEL_PATH=C:\path\to\model.pt
set PORT=8080

neurosymbolic-backend.exe
```

**Option C: Using .env File**
1. Copy `.env.example` to `.env`
2. Edit `.env` with your settings
3. Run: `neurosymbolic-backend.exe`

### 3. Verify Installation

Open your browser and go to:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health

---

## Directory Structure

```
neurosymbolic-backend/
├── neurosymbolic-backend.exe    # Main executable
├── _internal/                    # Bundled dependencies (DO NOT MODIFY)
├── backend/                      # Application code and configs
├── shared/                       # Shared configuration files
├── pipeline/                     # Pipeline components
├── data/                         # Working directory (created on first run)
│   ├── uploads/                  # Uploaded images
│   ├── results/                  # Processing results
│   └── visualizations/           # Output images
├── models/                       # YOLO model files (place your models here)
├── logs/                         # Application logs
└── .env.example                  # Example configuration file
```

---

## Configuration

### Environment Variables

Create a `.env` file in the same directory as the executable:

```env
# Application Settings
APP_NAME=Neurosymbolic Object Detection API
APP_VERSION=1.0.0
HOST=0.0.0.0
PORT=8000

# Data Storage
DATA_ROOT=./data

# Model Configuration
MODEL_PATH=./models/best.pt
CONFIDENCE_THRESHOLD=0.25
IOU_THRESHOLD=0.45

# GPU Settings
DEVICE=cuda  # or 'cpu' for CPU-only

# Symbolic Reasoning
ENABLE_SYMBOLIC=true
PROLOG_RULES_PATH=./pipeline/prolog/rules.pl

# CORS (for frontend integration)
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

### Model Files

Place your trained YOLO model files in the `models/` directory:

```
models/
├── best.pt              # Your trained model
├── yolov11m-obb.pt     # Pre-trained model (optional)
└── custom_model.pt     # Any other models
```

Update `MODEL_PATH` in `.env` to point to your model:
```env
MODEL_PATH=./models/best.pt
```

---

## Usage Examples

### Using the API

Once the application is running, you can use the REST API:

**Upload an image for detection:**
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@image.jpg"
```

**Start inference:**
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{"job_id": "job_001", "image_ids": ["img_001"]}'
```

**Check job status:**
```bash
curl "http://localhost:8000/api/v1/jobs/job_001/status"
```

**Get results:**
```bash
curl "http://localhost:8000/api/v1/jobs/job_001/results"
```

For full API documentation, visit: http://localhost:8000/docs

---

## Troubleshooting

### Issue: "SWI-Prolog not found"

**Symptom**: Error message about missing SWI-Prolog

**Solution**:
1. Verify SWI-Prolog is installed: `swipl --version`
2. Check it's in PATH: `where swipl` (should show install path)
3. Restart Command Prompt after installation
4. If still not working, set `ENABLE_SYMBOLIC=false` in `.env` to disable symbolic reasoning

### Issue: "Model file not found"

**Symptom**: Error loading YOLO model

**Solution**:
1. Check model file exists in `models/` directory
2. Verify `MODEL_PATH` in `.env` points to correct file
3. Use absolute path if needed: `MODEL_PATH=C:\full\path\to\model.pt`

### Issue: "CUDA not available" (GPU mode)

**Symptom**: Warning about CUDA not being available

**Solution**:
1. Check NVIDIA driver is installed: `nvidia-smi`
2. Use CPU mode by setting `DEVICE=cpu` in `.env`
3. GPU acceleration is optional - CPU mode works fine

### Issue: "Port already in use"

**Symptom**: Error starting server on port 8000

**Solution**:
1. Change port in `.env`: `PORT=8080`
2. Or kill process using port: 
   ```batch
   netstat -ano | findstr :8000
   taskkill /PID <process_id> /F
   ```

### Issue: "Permission denied" or "Access denied"

**Symptom**: Cannot create directories or write files

**Solution**:
1. Run as Administrator (right-click executable → Run as administrator)
2. Check antivirus isn't blocking the application
3. Ensure you have write permissions to the installation directory

### Issue: Antivirus flags the executable

**Symptom**: Antivirus software quarantines or blocks the executable

**Solution**:
1. This is a false positive (common with PyInstaller executables)
2. Add the executable to antivirus exclusions
3. Run `build.py` script yourself to build from source if concerned

---

## Performance Tips

### For Faster Inference

1. **Use GPU**: Set `DEVICE=cuda` if you have NVIDIA GPU
2. **Adjust Batch Size**: Process multiple images at once
3. **Reduce Image Size**: Resize large images before upload
4. **Disable Visualization**: Set `GENERATE_VISUALIZATIONS=false` if not needed

### For Smaller Memory Usage

1. **Use CPU Mode**: Set `DEVICE=cpu`
2. **Close Other Applications**: Free up RAM
3. **Process Smaller Batches**: Reduce concurrent jobs

---

## Logging

Application logs are saved to the `logs/` directory:

```
logs/
├── app.log              # Main application log
├── inference.log        # Inference operations
└── errors.log          # Error log
```

Enable debug logging by setting `LOG_LEVEL=DEBUG` in `.env`.

---

## Updating the Application

To update to a new version:

1. Download the new version
2. Stop the running application
3. Copy your `data/`, `models/`, `.env` files to the new version
4. Run the new executable

**Note**: Keep your model files and configuration separate from the executable directory for easier updates.

---

## Known Limitations

1. **SWI-Prolog Required**: Cannot be bundled, must be installed separately
2. **Large Size**: Executable bundle is 500MB-2GB depending on PyTorch version
3. **Slow Startup**: First launch may take 10-30 seconds due to unpacking
4. **Windows Only**: This build is for Windows. Linux/Mac users should run from source
5. **GPU Drivers**: GPU support requires NVIDIA drivers to be installed separately

---

## Support and Documentation

- **Full Documentation**: See `docs/` directory in source repository
- **API Reference**: http://localhost:8000/docs (when running)
- **GitHub Repository**: https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection
- **Issues**: Report bugs on GitHub Issues

---

## License

See LICENSE.txt file included with this distribution.

---

## Building from Source

If you prefer to build the executable yourself:

1. Clone the repository
2. Install Python 3.10 or 3.11
3. Run the build script:
   ```batch
   # Windows
   build_windows.bat
   
   # Or cross-platform
   python build.py
   ```

The build process is fully automated and documented in the source repository.

---

## Credits

- **YOLO**: Ultralytics YOLOv11
- **SAHI**: Sliced Aided Hyper Inference
- **PyTorch**: Deep learning framework
- **SWI-Prolog**: Logic programming engine
- **FastAPI**: Web framework

---

**Version**: 1.0.0  
**Build Date**: 2026-02-07  
**Python Version**: 3.10/3.11  
**PyTorch Version**: 2.6.0
