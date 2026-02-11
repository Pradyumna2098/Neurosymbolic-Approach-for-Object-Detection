# Getting Started Guide

This guide will walk you through setting up and running the Neurosymbolic Approach for Object Detection repository on your local machine.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
   - [Linux/macOS](#linuxmacos)
   - [Windows](#windows)
4. [Component Setup](#component-setup)
   - [Pipeline (Core AI/ML)](#1-pipeline-core-aiml)
   - [Backend (API Server)](#2-backend-api-server)
   - [Frontend (Desktop Application)](#3-frontend-desktop-application)
5. [Quick Start Examples](#quick-start-examples)
6. [Verification](#verification)
7. [Common Issues](#common-issues)
8. [Next Steps](#next-steps)

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

### Required Software

1. **Git** (version 2.x or higher)
   - Download from [git-scm.com](https://git-scm.com/)
   - Verify: `git --version`

2. **Python** (version 3.10 or 3.11 recommended)
   - Download from [python.org](https://www.python.org/)
   - **Important**: PyTorch/Ultralytics currently support Python 3.8-3.11
   - Verify: `python --version` or `python3 --version`

3. **pip** (Python package manager, usually comes with Python)
   - Verify: `pip --version` or `pip3 --version`
   - Upgrade: `python -m pip install --upgrade pip`

### Optional but Recommended

4. **NVIDIA GPU with CUDA** (for training and fast inference)
   - Check GPU: `nvidia-smi` (Linux/Windows)
   - CUDA 11.8 or 12.x recommended
   - Without GPU: Training will be very slow, but inference works on CPU

5. **SWI-Prolog** (for symbolic reasoning)
   - **Linux**: `sudo apt-get install swi-prolog swig`
   - **macOS**: `brew install swi-prolog swig`
   - **Windows**: Download from [swi-prolog.org](https://www.swi-prolog.org/download/stable)
   - Verify: `swipl --version`

6. **Node.js and npm** (version 18.x or higher, for frontend)
   - Download from [nodejs.org](https://nodejs.org/)
   - Verify: `node --version` and `npm --version`

---

## System Requirements

### Minimum Requirements (CPU-only)
- **CPU**: 4+ cores
- **RAM**: 8 GB
- **Storage**: 10 GB free space
- **OS**: Ubuntu 20.04+, macOS 11+, Windows 10+

### Recommended Requirements (GPU Training)
- **CPU**: 8+ cores
- **RAM**: 16 GB
- **GPU**: NVIDIA GPU with 8GB+ VRAM (e.g., RTX 3060, RTX 4060, or better)
- **Storage**: 50 GB free space (for datasets and models)
- **OS**: Ubuntu 20.04+, macOS 11+, Windows 10+

---

## Installation

### Clone the Repository

```bash
# Clone the repository
git clone https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection.git

# Navigate to the project directory
cd Neurosymbolic-Approach-for-Object-Detection
```

### Linux/macOS

#### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
# Update package list
sudo apt-get update

# Install Python development headers and build tools
sudo apt-get install -y python3-dev python3-pip python3-venv build-essential

# Install SWI-Prolog and SWIG (for PySwip)
sudo apt-get install -y swi-prolog swig

# Install Node.js and npm (for frontend)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**macOS:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install SWI-Prolog and SWIG
brew install swi-prolog swig

# Install Node.js
brew install node
```

#### 2. Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

#### 3. Install Python Dependencies

**For CPU-only:**
```bash
pip install -r requirements.txt
```

**For GPU (CUDA 11.8):**
```bash
# Install PyTorch with CUDA support first
pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu118

# Then install other requirements (this will skip torch/torchvision since already installed)
pip install -r requirements.txt
```

**For GPU (CUDA 12.x):**
```bash
# Install PyTorch with CUDA 12.x support first
pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu121

# Then install other requirements (this will skip torch/torchvision since already installed)
pip install -r requirements.txt
```

### Windows

#### 1. Install System Dependencies

1. **Install Python 3.10 or 3.11**
   - Download from [python.org](https://www.python.org/downloads/)
   - **Important**: Check "Add Python to PATH" during installation

2. **Install Visual C++ Build Tools** (required for some packages)
   - Download from [Microsoft](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   - Install "Desktop development with C++" workload

3. **Install SWI-Prolog** (optional, for symbolic reasoning)
   - Download from [swi-prolog.org](https://www.swi-prolog.org/download/stable)
   - Add to PATH during installation

4. **Install Node.js** (for frontend)
   - Download from [nodejs.org](https://nodejs.org/)

#### 2. Create Python Virtual Environment

Open PowerShell or Command Prompt:

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment (PowerShell)
.venv\Scripts\Activate.ps1

# OR activate in Command Prompt
.venv\Scripts\activate.bat

# Upgrade pip
python -m pip install --upgrade pip
```

#### 3. Install Python Dependencies

**For CPU-only:**
```powershell
pip install -r requirements.txt
```

**For GPU (CUDA 11.8):**
```powershell
# Install PyTorch with CUDA support first
pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu118

# Then install other requirements (this will skip torch/torchvision since already installed)
pip install -r requirements.txt
```

**For GPU (CUDA 12.x):**
```powershell
# Install PyTorch with CUDA 12.x support first
pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu121

# Then install other requirements (this will skip torch/torchvision since already installed)
pip install -r requirements.txt
```

---

## Component Setup

This repository contains three main components. You can set up all of them or just the ones you need.

### 1. Pipeline (Core AI/ML)

The pipeline is the core component for object detection, symbolic reasoning, and knowledge graph construction.

#### Already Set Up!

If you followed the installation steps above, the pipeline is ready to use. The Python dependencies you installed include all required packages.

#### Verify Installation

```bash
# Activate virtual environment (if not already active)
source .venv/bin/activate  # Linux/macOS
# OR
.venv\Scripts\activate  # Windows

# Check PyTorch installation
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"

# Check CUDA availability (if GPU installed)
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Check Ultralytics installation
python -c "from ultralytics import YOLO; print('Ultralytics YOLO installed successfully')"

# Check PySwip (optional, only if SWI-Prolog installed)
python -c "from pyswip import Prolog; print('PySwip installed successfully')"
```

#### Configure for Your Environment

Copy and edit configuration files for your local environment:

```bash
# Copy example config files
cp shared/configs/training_local.yaml shared/configs/training_custom.yaml
cp shared/configs/pipeline_local.yaml shared/configs/pipeline_custom.yaml
cp shared/configs/prediction_local.yaml shared/configs/prediction_custom.yaml

# Edit the files with your local paths
# Example: change /path/to/... to your actual dataset locations
```

**Important**: Update the following paths in your config files:
- `data_yaml`: Path to your YOLO dataset configuration
- `train_dir`, `val_dir`, `test_dir`: Paths to your image directories
- `output_dir`, `project_dir`: Where to save outputs
- `rules_file`: Path to Prolog rules (usually `pipeline/prolog/rules.pl`)

### 2. Backend (API Server)

The backend provides REST APIs for interacting with the pipeline programmatically.

#### Install Backend Dependencies

```bash
# Navigate to backend directory
cd backend

# Install backend requirements
pip install -r requirements.txt

# Return to project root
cd ..
```

#### Configure Backend

```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit .env file with your settings
nano backend/.env  # or use your preferred editor
```

The `.env.example` file in the backend directory contains the authoritative list of configuration options. Key settings you may want to customize:

```env
# Server Settings
HOST=0.0.0.0
PORT=8000

# CORS Settings (adjust for your frontend)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://localhost:5173

# Storage Paths (relative to project root)
DATA_ROOT=data
UPLOADS_DIR=data/uploads
RESULTS_DIR=data/results

# File Upload Settings
MAX_UPLOAD_SIZE=10485760  # 10 MB in bytes
```

See `backend/.env.example` for all available configuration options.

#### Run Backend Server

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# OR
.venv\Scripts\activate  # Windows

# Start backend server (from project root)
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend API will be available at `http://localhost:8000`. API documentation is available at `http://localhost:8000/docs`.

### 3. Frontend (Desktop Application)

The frontend is an Electron-based desktop application for visualizing results and interacting with the pipeline.

#### Install Frontend Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies (this may take a few minutes)
npm install

# Return to project root
cd ..
```

#### Run Frontend in Development Mode

```bash
# Navigate to frontend directory
cd frontend

# Start the Electron app in development mode
npm start
```

The desktop application window will open. The app connects to the backend at `http://localhost:8000` by default.

#### Build Frontend for Production

```bash
cd frontend

# Package the application for your platform
npm run package

# Create distributable installer
npm run make
```

Built applications will be in `frontend/out/`.

---

## Quick Start Examples

### Example 1: Test PyTorch Installation

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS

# Test PyTorch
python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU: {torch.cuda.get_device_name(0)}')
"
```

### Example 2: Download a Pre-trained YOLO Model

```bash
# Activate virtual environment
source .venv/bin/activate

# Download YOLOv11n-OBB (smallest, fastest)
python -c "
from ultralytics import YOLO
model = YOLO('yolov11n-obb.pt')
print('Model downloaded successfully!')
"
```

### Example 3: Run Inference on a Sample Image

**Linux/macOS:**
```bash
# Create a test script
cat > test_inference.py << 'EOF'
from ultralytics import YOLO
from pathlib import Path

# Load a pre-trained model
model = YOLO('yolov11n-obb.pt')

# Run inference on an image
results = model.predict(
    source='https://ultralytics.com/images/bus.jpg',
    save=True,
    conf=0.25
)

print(f"Results saved to: {results[0].save_dir}")
print(f"Detected {len(results[0].boxes)} objects")
EOF

# Run the test
python test_inference.py
```

**Windows (create file manually):**
```powershell
# Create test_inference.py with the following content, then run:
python test_inference.py
```

### Example 4: Test Backend API

```bash
# In one terminal, start the backend (from project root)
source .venv/bin/activate
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

# In another terminal, test the API
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/models/list
```

---

## Verification

### Verify Pipeline Setup

Run the test suite to ensure everything is working:

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# OR
.venv\Scripts\activate  # Windows

# Run pipeline tests
pytest tests/pipeline/ -v

# Run all tests (if you want to test everything)
pytest tests/ -v
```

### Verify Backend Setup

```bash
# Test backend API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/models/list

# Or open in browser
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

### Verify Frontend Setup

1. Start the frontend: `cd frontend && npm start`
2. The Electron window should open
3. Check that the UI loads without errors
4. Try uploading a sample image (if backend is running)

---

## Common Issues

### Issue 1: PySwip Installation Fails

**Symptom**: `pip install pyswip` fails with compilation errors

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install swi-prolog swig python3-dev

# macOS
brew install swi-prolog swig

# Windows
# 1. Install SWI-Prolog from https://www.swi-prolog.org/
# 2. Add SWI-Prolog to PATH
# 3. Install Visual C++ Build Tools
# 4. Try: pip install pyswip
```

**Alternative**: Skip PySwip if you don't need symbolic reasoning:
```bash
# Install requirements without pyswip - it will fail during install but other packages will succeed
pip install -r requirements.txt
# Or manually install packages listed in requirements.txt except pyswip
# Skip the symbolic reasoning stage in your pipeline
```

### Issue 2: CUDA Not Detected

**Symptom**: `torch.cuda.is_available()` returns `False`

**Solution**:
```bash
# 1. Check NVIDIA driver is installed
nvidia-smi

# 2. Reinstall PyTorch with CUDA support
pip uninstall torch torchvision
pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu118

# 3. Verify
python -c "import torch; print(torch.cuda.is_available())"
```

### Issue 3: Permission Denied Errors (Linux/macOS)

**Symptom**: Cannot run scripts or access files

**Solution**:
```bash
# Make scripts executable
chmod +x *.sh

# Don't use sudo with pip in virtual environment
# Always activate venv first: source .venv/bin/activate
```

### Issue 4: Module Not Found Errors

**Symptom**: `ModuleNotFoundError: No module named 'package_name'`

**Solution**:
```bash
# 1. Ensure virtual environment is activated
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate  # Windows

# 2. Reinstall requirements
pip install -r requirements.txt

# 3. If specific package missing
pip install package_name
```

### Issue 5: Out of Memory Errors During Training

**Symptom**: CUDA out of memory error

**Solution**:
```yaml
# Edit your training config file (e.g., shared/configs/training_custom.yaml)
# Reduce batch_size:
training:
  batch_size: 8  # or even 4 for limited VRAM
  # Or reduce image size
  imgsz: 640  # instead of 1024
```

### Issue 6: Backend Won't Start

**Symptom**: Backend fails to start or crashes

**Solution**:
```bash
# 1. Check if port 8000 is already in use
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# 2. Use a different port (from project root)
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8001

# 3. Check backend logs for specific errors (from project root)
python -m uvicorn backend.app.main:app --reload --log-level debug
```

### Issue 7: Frontend Won't Start

**Symptom**: `npm start` fails

**Solution**:
```bash
# 1. Delete node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# 2. Check Node.js version (should be 18.x or higher)
node --version

# 3. Try clearing npm cache
npm cache clean --force
npm install
```

### Issue 8: Dataset Not Found Errors

**Symptom**: Cannot find dataset or images

**Solution**:
1. Verify dataset directory structure:
```
dataset/
├── train/
│   ├── images/
│   └── labels/
├── val/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```

2. Check config file paths are absolute:
```yaml
# Use absolute paths, not relative
data_yaml: /home/user/datasets/dota/dota.yaml
train_dir: /home/user/datasets/dota/train/images
```

3. Ensure labels are in YOLO format (normalized coordinates)

---

## Next Steps

### For Machine Learning / Research

1. **Prepare Your Dataset**
   - Convert your dataset to YOLO format
   - See [Dataset Preparation Guide](../README.md#dataset-preparation)

2. **Train a Model**
   - Edit `shared/configs/training_custom.yaml`
   - Run: `python pipeline/training/training.py --config shared/configs/training_custom.yaml`
   - See in-code documentation in `pipeline/training/training.py`

3. **Run Inference**
   - Use SAHI for large images: `python pipeline/inference/sahi_yolo_prediction.py --config shared/configs/prediction_custom.yaml`

4. **Apply Symbolic Reasoning**
   - Run the full pipeline: `python -m pipeline.core.run_pipeline --config shared/configs/pipeline_custom.yaml`

5. **Build Knowledge Graphs**
   - Extract spatial relationships: `python pipeline/inference/weighted_kg_sahi.py --config shared/configs/knowledge_graph_custom.yaml`

### For Application Development

1. **Start the Full Stack**
   ```bash
   # Terminal 1: Backend (from project root)
   source .venv/bin/activate
   python -m uvicorn backend.app.main:app --reload

   # Terminal 2: Frontend
   cd frontend
   npm start
   ```

2. **Explore the API**
   - Open `http://localhost:8000/docs` for interactive API documentation
   - See [Backend README](../backend/README.md) for API details

3. **Customize the Frontend**
   - See [Frontend README](../frontend/README.md) for component architecture
   - Edit components in `frontend/src/`

### Additional Resources

- **[README.md](../README.md)** - Project overview and quick reference
- **[docs/STRUCTURE.md](STRUCTURE.md)** - Detailed repository structure
- **[docs/CICD.md](CICD.md)** - CI/CD pipeline documentation
- **[.github/copilot-instructions.md](../.github/copilot-instructions.md)** - Contribution guidelines

---

## Getting Help

If you encounter issues not covered in this guide:

1. **Check existing documentation**:
   - [README.md](../README.md)
   - [Troubleshooting section](../README.md#troubleshooting)

2. **Search GitHub Issues**:
   - [Open Issues](https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection/issues)
   - [Closed Issues](https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection/issues?q=is%3Aissue+is%3Aclosed)

3. **Create a New Issue**:
   - Include your OS, Python version, and error messages
   - Provide steps to reproduce the problem
   - [Create Issue](https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection/issues/new)

---

## Summary Checklist

Before you start working with the repository, ensure you have:

- [ ] Cloned the repository
- [ ] Installed Python 3.10 or 3.11
- [ ] Created and activated a virtual environment
- [ ] Installed Python dependencies with `pip install -r requirements.txt`
- [ ] (Optional) Installed SWI-Prolog for symbolic reasoning
- [ ] (Optional) Verified CUDA/GPU availability for training
- [ ] (Optional) Installed Node.js and frontend dependencies
- [ ] Configured at least one config file with your local paths
- [ ] Verified installation with `pytest tests/pipeline/` or a simple inference test

**You're all set!** 🎉 Proceed to the [Quick Start Examples](#quick-start-examples) or [Next Steps](#next-steps) to begin using the repository.
