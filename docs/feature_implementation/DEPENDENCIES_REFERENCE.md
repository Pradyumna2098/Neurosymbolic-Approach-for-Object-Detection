# Comprehensive Dependency Documentation

## Table of Contents

1. [Overview](#overview)
2. [Core Application Dependencies](#core-application-dependencies)
3. [External System Dependencies](#external-system-dependencies)
4. [Prometheus Monitoring Dependencies](#prometheus-monitoring-dependencies)
5. [Development and Packaging Dependencies](#development-and-packaging-dependencies)
6. [Optional Dependencies](#optional-dependencies)
7. [Dependency Management](#dependency-management)
8. [Security and Updates](#security-and-updates)
9. [Troubleshooting Dependency Issues](#troubleshooting-dependency-issues)

---

## Overview

This document provides a comprehensive reference for all dependencies required by the Neurosymbolic Object Detection application, including core runtime dependencies, external tools, monitoring components, and packaging requirements.

### Dependency Categories

| Category | Purpose | Installation |
|----------|---------|--------------|
| **Python Packages** | Core application functionality | `pip install` |
| **System Tools** | External executables and libraries | System installer |
| **Prometheus Stack** | Metrics and monitoring | Separate installation |
| **Development Tools** | Building and packaging | Development environment |

---

## Core Application Dependencies

### Python Runtime

**Required Python Version**: 3.10 or 3.11

- **Python 3.10**: Recommended (tested)
- **Python 3.11**: Supported
- **Python 3.9**: May work but not officially tested
- **Python 3.12**: Not recommended (compatibility issues with some packages)

**Download**: https://www.python.org/downloads/

**Verification**:
```bash
python --version
# Should show: Python 3.10.x or 3.11.x
```

### Core Python Dependencies

From `requirements.txt` and `requirements/common.txt`:

#### Deep Learning Framework

**PyTorch and TorchVision**

```
torch==2.2.2
torchvision==0.17.2
```

**Purpose**: 
- Neural network training and inference
- GPU acceleration (CUDA support)
- Tensor operations

**Installation**:
```bash
# CPU version (smaller, ~800MB)
pip install torch==2.2.2 torchvision==0.17.2 --index-url https://download.pytorch.org/whl/cpu

# GPU version (larger, ~2.5GB, requires CUDA 11.8)
pip install torch==2.2.2+cu118 torchvision==0.17.2+cu118 --index-url https://download.pytorch.org/whl/cu118

# GPU version (CUDA 12.1)
pip install torch==2.2.2+cu121 torchvision==0.17.2+cu121 --index-url https://download.pytorch.org/whl/cu121
```

**Size**: 
- CPU: ~800 MB
- GPU (CUDA 11.8): ~2.5 GB
- GPU (CUDA 12.1): ~2.6 GB

**Windows Packaging**: 
- Include appropriate wheels in PyInstaller build
- Add DLL files to `_internal/`

---

#### Object Detection Library

**Ultralytics YOLO**

```
ultralytics==8.2.77
```

**Purpose**:
- YOLOv11 model implementation
- Training and inference APIs
- Model export utilities

**Dependencies**: Automatically installs:
- opencv-python
- pillow
- pyyaml
- requests
- scipy
- seaborn

**Size**: ~15 MB

**Windows Packaging**:
- Auto-detected by PyInstaller
- May require manual hidden imports

---

#### Computer Vision Libraries

**OpenCV**

```
opencv-python==4.10.0.84
```

**Purpose**:
- Image loading and preprocessing
- Image transformations
- Visualization

**Size**: ~90 MB (includes binary libraries)

**Windows Packaging**:
- Includes native DLLs
- Automatically bundled by PyInstaller

**SAHI (Sliced Aided Hyper Inference)**

```
sahi==0.11.16
```

**Purpose**:
- Large image slicing for inference
- Improved detection on high-resolution images
- Object detection post-processing

**Size**: ~5 MB

---

#### Scientific Computing

**NumPy**

```
numpy==1.26.4
```

**Purpose**:
- Numerical computations
- Array operations
- Linear algebra

**Size**: ~50 MB

**Note**: Critical dependency for almost all ML packages

**Pandas**

```
pandas==2.2.2
```

**Purpose**:
- Data manipulation
- CSV/Excel file handling
- Evaluation metrics storage

**Size**: ~40 MB

**Matplotlib**

```
matplotlib==3.8.4
```

**Purpose**:
- Plotting and visualization
- Loss curves
- Metric charts

**Size**: ~80 MB

**Dependencies**: Automatically installs:
- pillow
- python-dateutil
- pyparsing

**NetworkX**

```
networkx==3.3
```

**Purpose**:
- Knowledge graph construction
- Graph algorithms
- Spatial relationship representation

**Size**: ~10 MB

---

#### Machine Learning Utilities

**TorchMetrics**

```
torchmetrics==1.4.0.post0
```

**Purpose**:
- Evaluation metrics (mAP, precision, recall)
- Object detection metrics
- Classification metrics

**Size**: ~8 MB

**Note**: Optimized for PyTorch tensors

---

#### Symbolic Reasoning

**PySwip**

```
pyswip==0.2.10
```

**Purpose**:
- Python interface to SWI-Prolog
- Execute Prolog queries
- Load and query knowledge bases

**Size**: ~1 MB (Python package only)

**Critical External Dependency**: Requires SWI-Prolog system installation

**Installation Issues**:
- Requires SWIG and C compiler on some systems
- May need manual compilation on Linux
- Windows: Pre-built wheels usually available

**Windows Packaging**:
- ⚠️ **Cannot bundle SWI-Prolog** - must be installed separately
- Only Python bindings included
- Application checks for SWI-Prolog at runtime

---

#### Configuration and Utilities

**PyYAML**

```
pyyaml==6.0.1
```

**Purpose**:
- YAML configuration file parsing
- Settings management

**Size**: ~1 MB

**tqdm**

```
tqdm==4.66.4
```

**Purpose**:
- Progress bars for loops
- Training progress display
- File processing progress

**Size**: ~1 MB

---

### Dependency Summary Table

| Package | Version | Size | GPU Support | Bundled in Exe |
|---------|---------|------|-------------|----------------|
| torch | 2.2.2 | 800MB-2.5GB | Yes (optional) | Yes |
| torchvision | 0.17.2 | Included in torch | Yes | Yes |
| ultralytics | 8.2.77 | 15MB | Via PyTorch | Yes |
| opencv-python | 4.10.0.84 | 90MB | No | Yes |
| numpy | 1.26.4 | 50MB | No | Yes |
| pandas | 2.2.2 | 40MB | No | Yes |
| matplotlib | 3.8.4 | 80MB | No | Yes |
| sahi | 0.11.16 | 5MB | No | Yes |
| torchmetrics | 1.4.0.post0 | 8MB | No | Yes |
| networkx | 3.3 | 10MB | No | Yes |
| pyswip | 0.2.10 | 1MB | No | Yes (needs SWI-Prolog) |
| pyyaml | 6.0.1 | 1MB | No | Yes |
| tqdm | 4.66.4 | 1MB | No | Yes |

**Total Size (CPU version)**: ~1.1 GB  
**Total Size (GPU version)**: ~2.8 GB

---

## External System Dependencies

### SWI-Prolog (REQUIRED)

**Version**: 8.4.x or later (8.4.3 recommended)

**Purpose**: 
- Symbolic reasoning engine
- Prolog query execution
- Knowledge base management

**Download**: https://www.swi-prolog.org/download/stable

**Installation**:

**Windows**:
```batch
# Download installer: swipl-8.4.3-1.x64.exe
# Run installer
# IMPORTANT: Check "Add to PATH" during installation
```

**Verify Installation**:
```batch
swipl --version
# Should show: SWI-Prolog version 8.4.3
```

**Size**: ~150 MB

**Components**:
- Core Prolog engine (libswipl.dll)
- Standard library
- Development headers
- Documentation

**Registry Entries** (Windows):
- `HKEY_LOCAL_MACHINE\SOFTWARE\SWI\Prolog`
- Used by PySwip to locate installation

**Environment Variables**:
- `SWI_HOME_DIR`: Installation directory
- `PATH`: Must include `C:\Program Files\swipl\bin`

**Cannot Be Bundled Because**:
- Requires registry entries
- Dynamic library loading
- Complete standard library needed
- Size constraints

**Deployment Strategy**:
- Document as prerequisite
- Provide installation guide
- Include verification script
- Show clear error if missing

---

### NVIDIA GPU Drivers (Optional)

**Required For**: GPU-accelerated training and inference

**Minimum Version**: 
- CUDA 11.8: Driver 450.80.02 or later
- CUDA 12.1: Driver 525.60.13 or later

**Download**: https://www.nvidia.com/Download/index.aspx

**Components**:
- NVIDIA Display Driver
- CUDA Runtime (included in PyTorch wheels)
- cuDNN (included in PyTorch wheels)

**Verification**:
```batch
nvidia-smi
# Should show GPU info and driver version
```

**Size**: ~500-700 MB

**Not Required For**:
- CPU-only deployment
- Systems without NVIDIA GPU
- Inference on CPU (slower but functional)

---

### Microsoft Visual C++ Redistributable

**Required For**: Many Python packages with C/C++ extensions

**Version**: Visual C++ 2015-2022 Redistributable (x64)

**Download**: https://aka.ms/vs/17/release/vc_redist.x64.exe

**Purpose**:
- Runtime libraries for C++ extensions
- Required by PyTorch, OpenCV, NumPy

**Size**: ~25 MB

**Usually Pre-installed**: Most Windows systems have this

**Verification**:
- Check "Programs and Features" in Control Panel
- Look for "Microsoft Visual C++ 2015-2022 Redistributable"

---

## Prometheus Monitoring Dependencies

For metrics collection and monitoring:

### Python Prometheus Client

**prometheus_client**

```
prometheus_client==0.19.0
```

**Purpose**:
- Expose metrics endpoint
- Counter, Gauge, Histogram metrics
- HTTP server for /metrics

**Size**: ~2 MB

**Installation**:
```bash
pip install prometheus_client==0.19.0
```

**Windows Packaging**:
- Easily bundled with PyInstaller
- Minimal size overhead

---

### Prometheus Server (Separate Installation)

**Not bundled with application** - runs as separate service

**Version**: 2.48.0 or later

**Download**: https://prometheus.io/download/

**Windows Installation**:
1. Download `prometheus-2.48.0.windows-amd64.zip`
2. Extract to `C:\Program Files\Prometheus\`
3. Configure `prometheus.yml`
4. Run as Windows service or manually

**Size**: ~150 MB

**Components**:
- Prometheus server (prometheus.exe)
- Configuration file (prometheus.yml)
- Alert manager (optional)
- Data storage directory

**Configuration**:
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'neurosymbolic-app'
    static_configs:
      - targets: ['localhost:8000']
```

---

### Grafana (Optional, for Visualization)

**Version**: 10.2.0 or later

**Download**: https://grafana.com/grafana/download

**Size**: ~300 MB

**Purpose**:
- Metric visualization
- Dashboard creation
- Alerting interface

**Installation**:
- Download Windows installer
- Install as service
- Access at http://localhost:3000

**Not Required For**:
- Basic monitoring (Prometheus enough)
- Command-line usage
- Automated processing

---

### Optional Monitoring Tools

**Node Exporter** (system metrics):
```
node_exporter-1.7.0.windows-amd64
```

**Size**: ~20 MB

**Purpose**:
- System-level metrics (CPU, memory, disk)
- Hardware monitoring

**psutil** (Python system monitoring):
```
psutil==5.9.6
```

**Size**: ~500 KB

**Purpose**:
- CPU and memory usage from Python
- Process monitoring
- Cross-platform system info

**pynvml** (NVIDIA GPU monitoring):
```
nvidia-ml-py==12.535.133
```

**Size**: ~500 KB

**Purpose**:
- GPU utilization
- GPU memory usage
- Temperature monitoring

---

## Development and Packaging Dependencies

### PyInstaller

**For**: Creating Windows executables

```
pyinstaller==6.3.0
```

**Purpose**:
- Package Python application as .exe
- Bundle dependencies
- Create standalone distribution

**Size**: ~5 MB

**Installation**:
```bash
pip install pyinstaller==6.3.0
```

**Dependencies**:
- pyinstaller-hooks-contrib
- altgraph
- pefile (Windows)
- macholib (macOS)

---

### Alternative Packaging Tools

**cx_Freeze**:
```
cx_Freeze==6.15.10
```

**Purpose**: Alternative packager with MSI support

**Nuitka**:
```
nuitka==1.9
```

**Purpose**: Compile Python to C++ for performance

**py2exe** (Windows-only):
```
py2exe==0.13.0.1
```

**Purpose**: Windows-specific packaging

---

### Testing Dependencies

**pytest**:
```
pytest==7.4.3
pytest-cov==4.1.0
```

**Purpose**:
- Unit testing
- Integration testing
- Coverage reports

**Installation**:
```bash
pip install pytest pytest-cov
```

---

### Code Quality Tools

**flake8** (linting):
```
flake8==6.1.0
```

**black** (code formatting):
```
black==23.12.1
```

**mypy** (type checking):
```
mypy==1.7.1
```

**Installation**:
```bash
pip install flake8 black mypy
```

---

## Optional Dependencies

### Enhanced GPU Monitoring

**nvidia-ml-py3**:
```
nvidia-ml-py3==7.352.0
```

**Purpose**: Advanced GPU metrics

### Database Support (Future)

**SQLAlchemy**:
```
sqlalchemy==2.0.23
```

**Purpose**: Database ORM for backend

**psycopg2** (PostgreSQL):
```
psycopg2-binary==2.9.9
```

### Web Framework (Future Backend)

**FastAPI**:
```
fastapi==0.104.1
uvicorn==0.24.0
```

**Purpose**: REST API server

**Flask** (Alternative):
```
flask==3.0.0
```

---

## Dependency Management

### Virtual Environment

**Recommended**: Always use virtual environment

**Creation**:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

**Benefits**:
- Isolated dependencies
- No conflicts with system Python
- Clean uninstallation

---

### Requirements Files

**Structure**:
```
requirements/
├── common.txt       # Core dependencies
├── dev.txt          # Development tools
├── monitoring.txt   # Prometheus stack
└── optional.txt     # Optional features

requirements.txt     # Main file (includes common.txt)
requirements-kaggle.txt  # Kaggle environment
```

**Installation**:
```bash
# Core dependencies
pip install -r requirements.txt

# With development tools
pip install -r requirements/dev.txt

# With monitoring
pip install -r requirements/monitoring.txt
```

---

### Freezing Dependencies

**Generate requirements.txt**:
```bash
pip freeze > requirements.txt
```

**Better approach** (only direct dependencies):
```bash
pip install pipreqs
pipreqs . --force
```

---

### Dependency Updates

**Check for updates**:
```bash
pip list --outdated
```

**Update specific package**:
```bash
pip install --upgrade package_name
```

**Update all** (careful!):
```bash
pip install --upgrade -r requirements.txt
```

**Best Practice**:
- Test updates in development environment first
- Update one major package at a time
- Check compatibility with other packages
- Run full test suite after updates

---

## Security and Updates

### Security Scanning

**pip-audit** (dependency vulnerabilities):
```bash
pip install pip-audit
pip-audit
```

**Safety**:
```bash
pip install safety
safety check
```

### Known Security Issues

**PyYAML** (CVE-2020-14343):
- Fixed in version 5.4+
- Current version (6.0.1) is safe

**Pillow** (various CVEs):
- Keep updated to latest version
- Bundled with opencv-python and matplotlib

**Requests** (if using):
- Keep updated for SSL security

---

### Update Schedule Recommendations

| Dependency Type | Update Frequency | Testing Required |
|----------------|------------------|------------------|
| Security patches | Immediately | Regression tests |
| Minor versions | Monthly | Full test suite |
| Major versions | Quarterly | Extensive testing |
| PyTorch | Per release cycle | Performance benchmarks |
| YOLO/Ultralytics | When needed | Accuracy validation |

---

## Troubleshooting Dependency Issues

### Installation Failures

**Issue**: Package installation fails with compilation error

**Solutions**:
1. **Install build tools**:
   ```bash
   # Windows
   # Download Visual Studio Build Tools
   # https://visualstudio.microsoft.com/downloads/
   ```

2. **Use pre-built wheels**:
   ```bash
   pip install package_name --only-binary :all:
   ```

3. **Try different version**:
   ```bash
   pip install package_name==older_version
   ```

---

### Dependency Conflicts

**Issue**: Package A requires package B version 1.x, but package C requires version 2.x

**Solutions**:

1. **Check compatibility**:
   ```bash
   pip install pipdeptree
   pipdeptree
   ```

2. **Create separate environments**:
   - Use different virtual environments for conflicting packages

3. **Pin working versions**:
   ```bash
   # requirements.txt
   package-a==1.2.3
   package-b==2.3.4
   ```

---

### Import Errors

**Issue**: `ImportError: No module named 'xxx'`

**Solutions**:

1. **Verify installation**:
   ```bash
   pip list | grep xxx
   ```

2. **Check virtual environment**:
   ```bash
   which python  # Linux/macOS
   where python  # Windows
   ```

3. **Reinstall package**:
   ```bash
   pip uninstall xxx
   pip install xxx
   ```

---

### PyInstaller Hidden Imports

**Issue**: Package works in development but fails in packaged executable

**Solutions**:

1. **Add hidden imports to spec file**:
   ```python
   hiddenimports=[
       'package.submodule',
       'missing_module',
   ]
   ```

2. **Use hooks**:
   - Create `hook-package.py`
   - Place in `hooks/` directory

3. **Include data files**:
   ```python
   datas=[
       ('package/data/*', 'package/data'),
   ]
   ```

---

### Version Compatibility Matrix

| Python | PyTorch | Ultralytics | NumPy | Status |
|--------|---------|-------------|-------|--------|
| 3.10 | 2.2.2 | 8.2.77 | 1.26.4 | ✅ Recommended |
| 3.11 | 2.2.2 | 8.2.77 | 1.26.4 | ✅ Supported |
| 3.9 | 2.2.2 | 8.2.77 | 1.26.4 | ⚠️ Not tested |
| 3.12 | 2.2.2 | 8.2.77 | 1.26.4 | ❌ Issues reported |

---

## Conclusion

This comprehensive guide covers all dependencies required for the Neurosymbolic Object Detection application, from core Python packages to external system requirements and monitoring tools.

**Key Takeaways**:

1. **Python Packages**: ~1.1-2.8 GB depending on CPU vs GPU
2. **SWI-Prolog**: Required, must be installed separately (~150 MB)
3. **GPU Drivers**: Optional, for GPU acceleration (~500-700 MB)
4. **Prometheus**: Optional, for monitoring (separate installation)
5. **Development Tools**: PyInstaller for packaging (~5 MB)

**Critical Dependencies That Cannot Be Bundled**:
- ⚠️ SWI-Prolog (requires system installation)
- ⚠️ NVIDIA GPU Drivers (if using GPU)
- ⚠️ Microsoft Visual C++ Redistributable (usually pre-installed)

**For More Information**:
- [WINDOWS_PACKAGING_GUIDE.md](WINDOWS_PACKAGING_GUIDE.md) - Packaging instructions
- [PROMETHEUS_INTEGRATION_GUIDE.md](PROMETHEUS_INTEGRATION_GUIDE.md) - Monitoring setup
- [WINDOWS_EXECUTABLE_USER_GUIDE.md](WINDOWS_EXECUTABLE_USER_GUIDE.md) - End-user instructions
