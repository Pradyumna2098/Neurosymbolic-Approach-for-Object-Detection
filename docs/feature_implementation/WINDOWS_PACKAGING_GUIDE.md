# Windows Packaging Guide for Neurosymbolic Object Detection Application

## Table of Contents

1. [Overview](#overview)
2. [Packaging Options Comparison](#packaging-options-comparison)
3. [Recommended Approach: PyInstaller](#recommended-approach-pyinstaller)
4. [Alternative Approaches](#alternative-approaches)
5. [Dependency Management](#dependency-management)
6. [Step-by-Step Packaging Instructions](#step-by-step-packaging-instructions)
7. [Advanced Configuration](#advanced-configuration)
8. [Troubleshooting](#troubleshooting)

---

## Overview

This guide provides comprehensive instructions for packaging the Neurosymbolic Object Detection application as a Windows executable. The application is a complex Python-based system that combines:

- **YOLO-based Neural Networks** (YOLOv11-OBB with Ultralytics)
- **Symbolic Reasoning** (Prolog integration via PySwip)
- **Knowledge Graph Construction** (NetworkX)
- **Computer Vision** (OpenCV, SAHI)
- **Deep Learning** (PyTorch, TorchVision)

### Key Challenges

1. **Large Dependencies**: PyTorch, YOLO models, and CV libraries create large executables
2. **Native Dependencies**: PySwip requires SWI-Prolog system installation
3. **GPU Support**: CUDA libraries for GPU acceleration
4. **Dynamic Loading**: Model files and configuration need external loading
5. **Multi-Stage Pipeline**: Training, inference, and symbolic reasoning stages

---

## Packaging Options Comparison

### 1. PyInstaller

**Best for:** Standalone executables, CLI applications, moderate complexity

#### Pros
- ✅ Most mature and widely used Python packager
- ✅ Excellent support for PyTorch and deep learning libraries
- ✅ Handles hidden imports automatically in most cases
- ✅ Cross-platform support (Windows, Linux, macOS)
- ✅ Single-file or single-directory executables
- ✅ Active community and extensive documentation
- ✅ Good integration with virtual environments
- ✅ Hook system for custom packaging logic

#### Cons
- ❌ Large executable sizes (500MB-2GB for PyTorch apps)
- ❌ Slow startup time due to unpacking
- ❌ Requires manual handling of native dependencies (SWI-Prolog)
- ❌ May flag as false positive by antivirus software
- ❌ Limited support for some dynamic imports

#### Suitability: **⭐⭐⭐⭐⭐ Highly Recommended**
Best choice for this application due to mature PyTorch support and CLI nature.

---

### 2. cx_Freeze

**Best for:** Cross-platform distribution, smaller executables

#### Pros
- ✅ More efficient packaging than PyInstaller
- ✅ Better cross-platform consistency
- ✅ Smaller executable sizes
- ✅ Faster startup times
- ✅ Good documentation
- ✅ MSI installer creation for Windows

#### Cons
- ❌ Less automatic dependency detection
- ❌ Requires more manual configuration
- ❌ Fewer hooks for complex libraries
- ❌ Less community support for PyTorch/deep learning
- ❌ May struggle with hidden imports in ML libraries

#### Suitability: **⭐⭐⭐⭐ Good Alternative**
Viable option if executable size is a critical concern.

---

### 3. py2exe

**Best for:** Windows-only deployment, legacy support

#### Pros
- ✅ Windows-native packaging
- ✅ Lightweight compared to PyInstaller
- ✅ Direct Windows executable creation
- ✅ Good integration with Windows installer tools

#### Cons
- ❌ Windows-only (no cross-platform support)
- ❌ Less active development compared to PyInstaller
- ❌ Limited support for modern Python 3.10+ features
- ❌ Poor support for PyTorch and complex dependencies
- ❌ Requires extensive manual configuration

#### Suitability: **⭐⭐ Not Recommended**
Limited support for modern deep learning frameworks.

---

### 4. Nuitka

**Best for:** Performance-critical applications, native code compilation

#### Pros
- ✅ Compiles Python to C++ for better performance
- ✅ Smaller executables with better startup time
- ✅ No runtime unpacking overhead
- ✅ Better execution speed
- ✅ Growing support for complex packages

#### Cons
- ❌ Compilation time is very long (hours for large projects)
- ❌ Requires C++ compiler toolchain
- ❌ Complex configuration for ML libraries
- ❌ Less mature than PyInstaller
- ❌ May have compatibility issues with dynamic code

#### Suitability: **⭐⭐⭐ Potential Option for Optimization**
Consider for production if performance is critical after initial deployment with PyInstaller.

---

### 5. Docker + Windows Containers

**Best for:** Server deployment, containerized workflows

#### Pros
- ✅ Complete environment isolation
- ✅ Consistent across development and production
- ✅ Easy dependency management
- ✅ Version control of entire environment
- ✅ Scalable deployment

#### Cons
- ❌ Requires Docker Desktop on Windows
- ❌ Large image sizes (several GB)
- ❌ Not a traditional executable
- ❌ Users need Docker knowledge
- ❌ Resource overhead

#### Suitability: **⭐⭐⭐⭐ Recommended for Server/Enterprise Deployment**
Excellent for deployment on Windows servers or cloud environments.

---

### 6. Electron + Python Backend

**Best for:** Desktop GUI applications with web technologies

#### Pros
- ✅ Modern, native-looking GUI
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ Rich ecosystem of UI components
- ✅ Easy to create professional interfaces
- ✅ Separate frontend/backend concerns

#### Cons
- ❌ Very large package sizes (200MB+ before Python)
- ❌ High memory usage
- ❌ Requires JavaScript/TypeScript knowledge
- ❌ Complex build process
- ❌ Overhead of running both Electron and Python

#### Suitability: **⭐⭐⭐ Good for Future GUI Version**
Consider if developing a full desktop GUI application later.

---

### 7. Web Application (FastAPI/Flask + Frontend)

**Best for:** Multi-user, remote access, web-based workflows

#### Pros
- ✅ No packaging needed, just deploy server
- ✅ Accessible from any device with browser
- ✅ Easy updates and maintenance
- ✅ Multi-user support
- ✅ Separate frontend and backend development
- ✅ Can use existing frontend directory

#### Cons
- ❌ Requires server hosting
- ❌ Network connectivity required
- ❌ Not a traditional executable
- ❌ Requires web development knowledge
- ❌ Security considerations for web exposure

#### Suitability: **⭐⭐⭐⭐ Excellent for Future Backend/Frontend Integration**
The repository already has backend and frontend directories prepared for this approach.

---

## Summary Table

| Option | Ease of Use | Executable Size | PyTorch Support | Native Deps | Cross-Platform | Overall Rating |
|--------|-------------|-----------------|-----------------|-------------|----------------|----------------|
| **PyInstaller** | ⭐⭐⭐⭐⭐ | 500MB-2GB | ⭐⭐⭐⭐⭐ | ⚠️ Manual | ✅ Yes | ⭐⭐⭐⭐⭐ |
| **cx_Freeze** | ⭐⭐⭐⭐ | 300MB-1.5GB | ⭐⭐⭐⭐ | ⚠️ Manual | ✅ Yes | ⭐⭐⭐⭐ |
| **py2exe** | ⭐⭐⭐ | 400MB-1GB | ⭐⭐ | ⚠️ Manual | ❌ Windows only | ⭐⭐ |
| **Nuitka** | ⭐⭐ | 200MB-800MB | ⭐⭐⭐ | ⚠️ Manual | ✅ Yes | ⭐⭐⭐ |
| **Docker** | ⭐⭐⭐⭐ | 2GB-5GB | ⭐⭐⭐⭐⭐ | ✅ Included | ✅ Yes | ⭐⭐⭐⭐ |
| **Electron** | ⭐⭐⭐ | 300MB-2GB | ⭐⭐⭐⭐ | ⚠️ Manual | ✅ Yes | ⭐⭐⭐ |
| **Web App** | ⭐⭐⭐⭐ | N/A | ⭐⭐⭐⭐⭐ | ✅ Included | ✅ Yes | ⭐⭐⭐⭐ |

---

## Recommended Approach: PyInstaller

Based on the analysis, **PyInstaller is the recommended solution** for packaging this application as a Windows executable because:

1. **Proven PyTorch Support**: Extensive experience in packaging PyTorch applications
2. **CLI-First Design**: The application is primarily CLI-based, which PyInstaller handles excellently
3. **Community Support**: Large user base with solutions to common issues
4. **Flexibility**: Can create both single-file and directory-based distributions
5. **Development Workflow**: Easy to integrate into CI/CD pipelines

### When to Consider Alternatives

- **cx_Freeze**: If executable size is critical and you need Windows installer (MSI)
- **Docker**: For server/enterprise deployments or when GPU support is essential
- **Web App**: For multi-user scenarios or when the backend/frontend is fully developed
- **Nuitka**: For performance optimization after successful PyInstaller deployment

---

## Dependency Management

### Core Dependencies

The application requires these major dependency categories:

#### 1. Deep Learning Framework
```
torch==2.2.2
torchvision==0.17.2
```
- **Impact**: ~500MB-1GB
- **GPU Version**: Add +2GB for CUDA libraries
- **Packaging Note**: PyTorch includes many dynamic libraries

#### 2. Computer Vision & ML
```
ultralytics==8.2.77      # YOLO implementation
sahi==0.11.16            # Sliced inference
opencv-python==4.10.0.84 # Image processing
torchmetrics==1.4.0.post0
```
- **Impact**: ~200MB
- **Packaging Note**: OpenCV includes native libraries

#### 3. Symbolic Reasoning
```
pyswip==0.2.10
```
- **Impact**: ~5MB Python package
- **Critical**: Requires **SWI-Prolog** system installation (100-150MB)
- **Packaging Note**: **Cannot be bundled**, must be installed separately

#### 4. Scientific Computing
```
numpy==1.26.4
pandas==2.2.2
matplotlib==3.8.4
networkx==3.3
```
- **Impact**: ~150MB
- **Packaging Note**: NumPy/Pandas have native extensions

#### 5. Utilities
```
pyyaml==6.0.1
tqdm==4.66.4
```
- **Impact**: ~5MB

### External Requirements

#### SWI-Prolog (CRITICAL)

**Must be installed separately** on the target Windows machine:

1. **Download**: [SWI-Prolog for Windows](https://www.swi-prolog.org/download/stable)
2. **Version**: 8.4.x or later recommended
3. **Installation Path**: Default (`C:\Program Files\swipl\`)
4. **Environment**: Add to PATH automatically during installation

**Why it can't be bundled:**
- PySwip dynamically loads SWI-Prolog shared libraries (`.dll` files)
- Requires registry entries for proper operation
- Needs complete Prolog standard library and predicates

#### CUDA Toolkit (Optional, for GPU)

For GPU acceleration:
1. **NVIDIA Driver**: Latest stable driver for GPU
2. **CUDA Toolkit**: Version matching PyTorch (CUDA 11.8 or 12.1 for PyTorch 2.2.2)
3. **cuDNN**: Included in PyTorch wheels typically

**Packaging Options:**
- **CPU-only**: Use `torch` and `torchvision` CPU versions (smaller)
- **GPU**: Bundle CUDA DLLs (adds ~2GB but enables GPU)

---

## Step-by-Step Packaging Instructions

### Prerequisites

1. **Windows 10/11** (64-bit)
2. **Python 3.10 or 3.11** (tested versions)
3. **Git** for cloning the repository
4. **Visual Studio Build Tools** (for some dependencies)

### Step 1: Environment Setup

```batch
# Clone the repository
git clone https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection.git
cd Neurosymbolic-Approach-for-Object-Detection

# Create virtual environment
python -m venv venv_package
venv_package\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip
```

### Step 2: Install Dependencies

```batch
# Install core dependencies
pip install -r requirements.txt

# Install PyInstaller
pip install pyinstaller==6.3.0
```

**For GPU support**, replace torch/torchvision with CUDA versions:
```batch
pip uninstall torch torchvision
pip install torch==2.2.2+cu118 torchvision==0.17.2+cu118 --index-url https://download.pytorch.org/whl/cu118
```

### Step 3: Install SWI-Prolog

1. Download from https://www.swi-prolog.org/download/stable
2. Run installer: `swipl-X.Y.Z-1.x64.exe`
3. **Important**: Check "Add to PATH" during installation
4. Verify installation:
```batch
swipl --version
```

### Step 4: Create PyInstaller Spec File

Create `neurosymbolic_app.spec` in the repository root:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Hidden imports required for the application
hidden_imports = [
    'ultralytics',
    'ultralytics.models',
    'ultralytics.models.yolo',
    'ultralytics.engine',
    'sahi',
    'sahi.models',
    'sahi.predict',
    'pyswip',
    'pyswip.prolog',
    'torchmetrics',
    'torchmetrics.detection',
    'cv2',
    'networkx',
    'pandas',
    'numpy',
    'yaml',
    'matplotlib',
    'PIL',
]

# Data files to include
datas = [
    ('pipeline/prolog/*.pl', 'pipeline/prolog'),  # Prolog rules
    ('shared/configs/*.yaml', 'shared/configs'),  # Configuration files
]

# Analysis of the main script
a = Analysis(
    ['pipeline/core/run_pipeline.py'],  # Main entry point
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',  # Remove unused GUI libraries
        'matplotlib.tests',
        'numpy.tests',
        'pandas.tests',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Filter out unnecessary files
a.binaries = [x for x in a.binaries if not x[0].startswith('tk')]
a.binaries = [x for x in a.binaries if not x[0].startswith('tcl')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='neurosymbolic-pipeline',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress with UPX
    console=True,  # Console application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path if available: 'assets/icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='neurosymbolic-pipeline',
)
```

### Step 5: Create Additional Entry Points (Optional)

For other pipeline stages, create additional spec files:

**training_app.spec** for `pipeline/training/training.py`:
```python
# Similar to above but with:
a = Analysis(
    ['pipeline/training/training.py'],
    # ... rest similar
)
```

**sahi_prediction_app.spec** for `pipeline/inference/sahi_yolo_prediction.py`:
```python
a = Analysis(
    ['pipeline/inference/sahi_yolo_prediction.py'],
    # ... rest similar
)
```

### Step 6: Build the Executable

```batch
# Build using the spec file
pyinstaller neurosymbolic_app.spec

# Output will be in dist/neurosymbolic-pipeline/
```

**Build time**: 10-30 minutes depending on system

### Step 7: Test the Executable

```batch
cd dist\neurosymbolic-pipeline
neurosymbolic-pipeline.exe --help
```

### Step 8: Package for Distribution

Create a distribution folder structure:

```
NeurosymbolicApp_v1.0/
├── neurosymbolic-pipeline/     (PyInstaller output)
│   ├── neurosymbolic-pipeline.exe
│   ├── _internal/              (dependencies)
│   └── ...
├── configs/                     (sample configurations)
│   ├── pipeline_example.yaml
│   └── training_example.yaml
├── models/                      (empty, for user models)
├── data/                        (empty, for user data)
├── requirements_prolog.txt      (SWI-Prolog requirement note)
├── README.txt                   (quick start guide)
└── LICENSE.txt
```

### Step 9: Create Windows Installer (Optional)

Use **Inno Setup** to create a professional installer:

1. Download Inno Setup: https://jrsoftware.org/isinfo.php
2. Create `installer_script.iss`:

```inno
[Setup]
AppName=Neurosymbolic Object Detection
AppVersion=1.0
DefaultDirName={pf}\NeurosymbolicApp
DefaultGroupName=Neurosymbolic Object Detection
OutputDir=output
OutputBaseFilename=NeurosymbolicApp_Setup_v1.0
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\neurosymbolic-pipeline\*"; DestDir: "{app}"; Flags: recursesubdirs
Source: "shared\configs\*.yaml"; DestDir: "{app}\configs"; Flags: recursesubdirs
Source: "README.txt"; DestDir: "{app}"
Source: "LICENSE"; DestDir: "{app}"; DestName: "LICENSE.txt"

[Icons]
Name: "{group}\Neurosymbolic Pipeline"; Filename: "{app}\neurosymbolic-pipeline.exe"
Name: "{group}\Uninstall"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\README.txt"; Description: "View README"; Flags: postinstall shellexec skipifsilent
```

3. Compile with Inno Setup to create `.exe` installer

---

## Advanced Configuration

### Optimizing Executable Size

#### 1. Use CPU-Only PyTorch
```batch
pip install torch==2.2.2 torchvision==0.17.2 --index-url https://download.pytorch.org/whl/cpu
```
**Savings**: ~1.5GB

#### 2. Exclude Unused Modules
Add to spec file:
```python
excludes=[
    'tkinter', 'test', 'unittest',
    'email', 'http', 'xml', 'xmlrpc',
    'pydoc', 'doctest',
    'matplotlib.tests', 'numpy.tests',
]
```

#### 3. Use UPX Compression
Already enabled in spec file, but verify UPX is installed:
```batch
# Download UPX from https://upx.github.io/
# Extract to C:\upx\ and add to PATH
```

#### 4. Single File Mode (Trade-off)
Change spec file:
```python
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,  # Add this
    a.zipfiles,  # Add this
    a.datas,     # Add this
    [],
    name='neurosymbolic-pipeline',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)

# Remove COLLECT section
```

**Result**: Single `.exe` file, but slower startup (extracts to temp on each run)

### GPU Support Configuration

For GPU-enabled executables:

1. **Include CUDA DLLs**:
```python
# In spec file, add to datas:
import torch
cuda_path = os.path.dirname(torch.__file__)
datas += [(f'{cuda_path}/lib/*.dll', 'torch/lib')]
```

2. **Verify CUDA in executable**:
```batch
neurosymbolic-pipeline.exe
# Check if torch.cuda.is_available() returns True
```

### Multi-Entry Point Package

Create a launcher script `launcher.py`:

```python
"""Launcher for multiple pipeline entry points."""
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Neurosymbolic Pipeline Launcher")
    parser.add_argument('command', choices=['train', 'predict', 'pipeline', 'knowledge-graph'])
    parser.add_argument('args', nargs=argparse.REMAINDER)
    
    args = parser.parse_args()
    
    if args.command == 'train':
        from pipeline.training import training
        training.main(args.args)
    elif args.command == 'predict':
        from pipeline.inference import sahi_yolo_prediction
        sahi_yolo_prediction.main(args.args)
    elif args.command == 'pipeline':
        from pipeline.core import run_pipeline
        run_pipeline.main(args.args)
    elif args.command == 'knowledge-graph':
        from pipeline.inference import weighted_kg_sahi
        weighted_kg_sahi.main(args.args)

if __name__ == '__main__':
    main()
```

Then package with this as the entry point.

---

## Troubleshooting

### Issue 1: PyInstaller Build Fails

**Symptom**: ImportError during build or analysis phase

**Solutions**:
1. **Update PyInstaller**:
   ```batch
   pip install --upgrade pyinstaller
   ```

2. **Add hidden imports** to spec file:
   ```python
   hiddenimports=['missing_module']
   ```

3. **Check for conflicting packages**:
   ```batch
   pip check
   ```

### Issue 2: SWI-Prolog Not Found

**Symptom**: `pyswip.prolog.PrologError: SWI-Prolog not found`

**Solutions**:
1. **Verify SWI-Prolog in PATH**:
   ```batch
   where swipl
   # Should show: C:\Program Files\swipl\bin\swipl.exe
   ```

2. **Set environment variable** in code:
   ```python
   import os
   os.environ['SWI_HOME_DIR'] = r'C:\Program Files\swipl'
   ```

3. **Check DLL access**:
   ```batch
   # Ensure libswipl.dll is accessible
   dir "C:\Program Files\swipl\bin\libswipl.dll"
   ```

### Issue 3: CUDA Not Available

**Symptom**: `torch.cuda.is_available()` returns False in executable

**Solutions**:
1. **Verify CUDA DLLs** are included in `_internal`:
   ```batch
   dir dist\neurosymbolic-pipeline\_internal\*cuda*.dll
   ```

2. **Install NVIDIA driver** on target machine

3. **Use CPU version** if GPU not critical:
   ```python
   # In code, add fallback:
   device = 'cuda' if torch.cuda.is_available() else 'cpu'
   ```

### Issue 4: Large Executable Size

**Symptom**: Executable is over 2GB

**Solutions**:
1. **Use CPU-only PyTorch** (saves ~1.5GB)
2. **Enable UPX compression**
3. **Exclude test modules** in spec file
4. **Consider Docker** as alternative for large deployments

### Issue 5: Slow Startup Time

**Symptom**: Executable takes 30+ seconds to start

**Solutions**:
1. **Use directory mode** instead of single file:
   - Keep COLLECT section in spec file
   - Distribute entire `dist/neurosymbolic-pipeline/` folder

2. **Optimize imports**:
   - Lazy load heavy modules (torch, cv2)
   - Use conditional imports

3. **Disable debug mode**:
   ```python
   debug=False  # in spec file
   ```

### Issue 6: Missing Model Files

**Symptom**: Application can't find YOLO weights or Prolog rules

**Solutions**:
1. **Use absolute paths** in configuration:
   ```yaml
   model_path: C:\Users\YourName\models\best.pt
   ```

2. **Bundle with application**:
   ```python
   # In spec file datas:
   ('models/*.pt', 'models'),
   ```

3. **Use resource path helper**:
   ```python
   import sys
   import os
   
   def resource_path(relative_path):
       """Get absolute path to resource, works for dev and PyInstaller."""
       if getattr(sys, 'frozen', False):
           # Running in PyInstaller bundle
           base_path = sys._MEIPASS
       else:
           base_path = os.path.abspath(".")
       return os.path.join(base_path, relative_path)
   ```

### Issue 7: Antivirus False Positives

**Symptom**: Antivirus software flags executable as malware

**Solutions**:
1. **Code sign the executable** with a valid certificate
2. **Submit to antivirus vendors** for whitelisting
3. **Use digital signature**:
   ```batch
   signtool sign /f certificate.pfx /p password /t http://timestamp.server neurosymbolic-pipeline.exe
   ```
4. **Distribute source code** alongside for transparency

### Issue 8: Configuration File Not Found

**Symptom**: `FileNotFoundError: config file not found`

**Solutions**:
1. **Bundle configs** in spec file:
   ```python
   datas=[('shared/configs/*.yaml', 'shared/configs')]
   ```

2. **Provide external config**:
   - Ship config files alongside executable
   - Use command-line argument: `--config path/to/config.yaml`

3. **Check working directory**:
   ```batch
   # Run from correct directory
   cd dist\neurosymbolic-pipeline
   .\neurosymbolic-pipeline.exe --config ..\..\configs\pipeline.yaml
   ```

---

## CI/CD Integration

### Automated Building with GitHub Actions

Create `.github/workflows/build_windows.yml`:

```yaml
name: Build Windows Executable

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller==6.3.0
    
    - name: Build executable
      run: |
        pyinstaller neurosymbolic_app.spec
    
    - name: Create release archive
      run: |
        Compress-Archive -Path dist/neurosymbolic-pipeline/* -DestinationPath neurosymbolic-app-windows.zip
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: windows-executable
        path: neurosymbolic-app-windows.zip
```

---

## Best Practices

1. **Test on Clean Windows Installation**: Verify executable works without development tools
2. **Document External Dependencies**: Clearly list SWI-Prolog and GPU requirements
3. **Version Your Builds**: Include version in executable name
4. **Provide Checksum**: SHA256 hash for verifying downloads
5. **Include Sample Data**: Small dataset for testing
6. **Create Comprehensive README**: Installation and usage instructions
7. **Monitor Executable Size**: Track size increases between versions
8. **Regular Updates**: Rebuild when dependencies update
9. **User Feedback**: Collect feedback on installation issues
10. **Fallback Options**: Provide Python installation instructions as alternative

---

## Conclusion

**PyInstaller is the recommended solution** for packaging this neurosymbolic object detection application as a Windows executable. While it creates large executables (500MB-2GB), it provides the best compatibility with PyTorch and complex ML dependencies.

**Key Takeaways**:
- ✅ Use PyInstaller for reliability and PyTorch support
- ⚠️ SWI-Prolog must be installed separately (cannot be bundled)
- 💡 Consider Docker for enterprise/server deployments
- 🚀 Plan for web application when backend/frontend are developed
- 📦 Always test on clean Windows installation before distribution

For additional support with Prometheus integration, see [PROMETHEUS_INTEGRATION_GUIDE.md](PROMETHEUS_INTEGRATION_GUIDE.md).

For user instructions, see [WINDOWS_EXECUTABLE_USER_GUIDE.md](WINDOWS_EXECUTABLE_USER_GUIDE.md).
