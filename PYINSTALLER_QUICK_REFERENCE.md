# PyInstaller Packaging Quick Reference

Quick reference for building and distributing the Neurosymbolic Backend executable.

---

## Quick Start

### Build Executable (Windows)
```batch
build_windows.bat
```

### Build Executable (Cross-platform)
```bash
python build.py
```

### Verify Build
```bash
python verify_build.py
```

### Create Distribution Package
```bash
python create_distribution.py
```

### Test Executable
```bash
cd dist/neurosymbolic-backend
neurosymbolic-backend.exe
# Open http://localhost:8000/docs
```

---

## File Structure

```
Repository Root/
├── backend_api.spec              # PyInstaller specification
├── build.py                      # Cross-platform build script
├── build_windows.bat             # Windows build script
├── verify_build.py               # Build verification
├── create_distribution.py        # Distribution packager
├── EXECUTABLE_README.txt         # User guide
├── PYINSTALLER_IMPLEMENTATION_SUMMARY.md  # This file
│
├── backend/
│   └── app/
│       └── core/
│           └── resource_path.py  # Resource utilities
│
└── dist/                         # Build output (gitignored)
    ├── neurosymbolic-backend/    # Executable directory
    │   ├── neurosymbolic-backend.exe
    │   ├── _internal/            # Dependencies
    │   ├── backend/
    │   ├── shared/
    │   └── pipeline/
    │
    └── NeurosymbolicApp_v1.0/    # Distribution package
        ├── neurosymbolic-backend/
        ├── configs/
        ├── models/
        ├── data/
        ├── docs/
        ├── README.txt
        └── start_server.bat
```

---

## Common Commands

### Build with Custom Options
```bash
# Use different virtual environment
python build.py --venv my_venv

# Skip dependency installation (use existing venv)
python build.py --skip-deps

# Use custom requirements file
python build.py --requirements my_requirements.txt

# Use custom spec file
python build.py --spec my_app.spec
```

### Distribution Options
```bash
# Custom output directory
python create_distribution.py --output-dir MyApp_v2.0

# Skip ZIP archive creation
python create_distribution.py --no-archive
```

### Manual PyInstaller Build
```bash
# Activate virtual environment
source venv_build/bin/activate  # Linux/Mac
venv_build\Scripts\activate     # Windows

# Run PyInstaller
pyinstaller backend_api.spec
```

---

## Build Requirements

### System Requirements
- Windows 10/11 (for Windows builds)
- Python 3.10 or 3.11
- 8 GB RAM minimum (16 GB recommended)
- 10 GB free disk space

### Python Packages
- pyinstaller==6.3.0
- All dependencies from backend/requirements.txt or requirements.txt

### Build Time
- Initial: 10-30 minutes
- Subsequent: 5-15 minutes

### Output Size
- CPU version: ~1.1 GB
- GPU version: ~2.8 GB

---

## Troubleshooting

### Build Fails with Import Errors
**Solution:** Add missing module to `hiddenimports` in `backend_api.spec`
```python
hiddenimports=[
    'missing_module',
    'another_module',
]
```

### Executable Crashes on Startup
**Solution:** 
1. Check `verify_build.py` output
2. Test in development: `python backend/app/main.py`
3. Check logs in `logs/` directory

### Missing Resources in Executable
**Solution:** Add to `datas` in `backend_api.spec`
```python
datas=[
    ('path/to/resource', 'destination/in/bundle'),
]
```

### Large Executable Size
**Solutions:**
1. Use CPU-only PyTorch (saves ~1.5 GB)
2. Add more modules to `excludes` list
3. Enable UPX compression (already enabled)

### Slow Startup Time
**Solutions:**
1. Use directory mode (already configured)
2. Lazy import heavy modules in code
3. Use SSD for executable location

---

## External Dependencies

### SWI-Prolog (Required)
**Install:** https://www.swi-prolog.org/download/stable  
**Verify:** `swipl --version`  
**Note:** Cannot be bundled, must install separately

### NVIDIA GPU Drivers (Optional)
**Install:** https://www.nvidia.com/Download/index.aspx  
**Verify:** `nvidia-smi`  
**Note:** Only for GPU acceleration

### Visual C++ Redistributable (Usually pre-installed)
**Install:** https://aka.ms/vs/17/release/vc_redist.x64.exe  
**Note:** Only if getting DLL errors

---

## Resource Path Usage

### In Code
```python
from app.core.resource_path import (
    get_resource_path,
    get_data_path,
    get_models_path,
    is_frozen,
)

# Get bundled resource
config = get_resource_path('shared/configs/pipeline.yaml')

# Get writable data directory
uploads = get_data_path('uploads')

# Get models directory
model = get_models_path('best.pt')

# Check if running as executable
if is_frozen():
    print("Running as PyInstaller executable")
else:
    print("Running in development")
```

### Environment Detection
- **Development:** Paths relative to repository root
- **Packaged:** Resources from `sys._MEIPASS`, data from executable directory

---

## Distribution Checklist

Before distributing to users:

- [ ] Build executable successfully
- [ ] Run `verify_build.py` (all checks pass)
- [ ] Test executable on clean Windows machine
- [ ] Verify SWI-Prolog integration
- [ ] Test API endpoints (upload, predict, results)
- [ ] Create distribution package
- [ ] Include configuration examples
- [ ] Update README.txt with version info
- [ ] Test ZIP extraction and launcher
- [ ] Document known issues
- [ ] Provide support contact

---

## Version Information

**Current Version:** 1.0.0  
**Build Date:** 2026-02-07  
**Python Version:** 3.10/3.11  
**PyTorch Version:** 2.6.0  
**PyInstaller Version:** 6.3.0

---

## Support

**Documentation:**
- User Guide: `EXECUTABLE_README.txt`
- Implementation Details: `PYINSTALLER_IMPLEMENTATION_SUMMARY.md`
- Packaging Guide: `docs/feature_implementation/WINDOWS_PACKAGING_GUIDE.md`

**Scripts:**
- Build: `build.py` or `build_windows.bat`
- Verify: `verify_build.py`
- Package: `create_distribution.py`

**Issues:**
- GitHub Repository: https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection/issues

---

## Quick Checklist

### For Developers
```bash
# 1. Build
python build.py

# 2. Verify
python verify_build.py

# 3. Test
cd dist/neurosymbolic-backend
./neurosymbolic-backend.exe

# 4. Package
cd ../..
python create_distribution.py

# 5. Distribute
# Upload dist/NeurosymbolicApp_v1.0.zip
```

### For Users
```bash
# 1. Extract ZIP
# 2. Install SWI-Prolog
# 3. Run start_server.bat
# 4. Open http://localhost:8000/docs
```

---

**Last Updated:** 2026-02-07
