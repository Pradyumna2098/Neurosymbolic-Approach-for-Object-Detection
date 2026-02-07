# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification file for Neurosymbolic Object Detection Backend API.

This spec file packages the FastAPI backend application with all dependencies
including PyTorch, YOLO models, and computer vision libraries.

External Dependencies (NOT bundled, must be installed separately):
- SWI-Prolog 8.4.x or later (required for symbolic reasoning)
- NVIDIA GPU Drivers (optional, for GPU acceleration)
"""

import os
import sys
from pathlib import Path

block_cipher = None

# Determine the root directory
ROOT_DIR = Path('.').absolute()

# Hidden imports required for the application
# These modules are dynamically imported and need to be explicitly included
hidden_imports = [
    # FastAPI and web framework
    'uvicorn',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'fastapi',
    'fastapi.responses',
    'pydantic',
    'pydantic.networks',
    'pydantic_settings',
    
    # YOLO and object detection
    'ultralytics',
    'ultralytics.models',
    'ultralytics.models.yolo',
    'ultralytics.models.yolo.detect',
    'ultralytics.models.yolo.obb',
    'ultralytics.engine',
    'ultralytics.engine.predictor',
    'ultralytics.utils',
    'ultralytics.utils.checks',
    'ultralytics.utils.downloads',
    'ultralytics.nn',
    'ultralytics.nn.modules',
    
    # SAHI for sliced inference
    'sahi',
    'sahi.models',
    'sahi.models.yolov8',
    'sahi.predict',
    'sahi.slicing',
    'sahi.utils',
    
    # PySwip and Prolog integration
    'pyswip',
    'pyswip.prolog',
    'pyswip.core',
    
    # PyTorch and torchvision
    'torch',
    'torch.nn',
    'torch.optim',
    'torch.utils',
    'torch.utils.data',
    'torchvision',
    'torchvision.ops',
    'torchvision.transforms',
    'torchmetrics',
    'torchmetrics.detection',
    'torchmetrics.detection.mean_ap',
    
    # Computer vision
    'cv2',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    
    # Scientific computing
    'numpy',
    'pandas',
    'matplotlib',
    'matplotlib.pyplot',
    'networkx',
    
    # Utilities
    'yaml',
    'tqdm',
    'multipart',
]

# Data files to include in the bundle
datas = [
    # Backend application source
    ('backend/app', 'backend/app'),
    
    # Configuration files
    ('shared/configs', 'shared/configs'),
    
    # Prolog rules (if they exist in pipeline/prolog)
    ('pipeline/prolog', 'pipeline/prolog') if (ROOT_DIR / 'pipeline' / 'prolog').exists() else None,
    
    # Environment example
    ('backend/.env.example', 'backend'),
]

# Remove None entries from datas
datas = [d for d in datas if d is not None]

# Binaries - empty for now, PyTorch DLLs are auto-detected
binaries = []

# Analysis of the main script
a = Analysis(
    ['backend/app/main.py'],  # Main entry point
    pathex=[str(ROOT_DIR)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Remove unused GUI libraries to reduce size
        'tkinter',
        'tk',
        'tcl',
        '_tkinter',
        
        # Remove test modules
        'matplotlib.tests',
        'numpy.tests',
        'pandas.tests',
        'torch.testing',
        'unittest',
        'test',
        'pytest',
        
        # Remove unused web frameworks
        'flask',
        'django',
        
        # Remove unused documentation
        'sphinx',
        'docutils',
        'pydoc',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Filter out unnecessary binaries to reduce size
# Remove Tcl/Tk binaries if accidentally included
a.binaries = [x for x in a.binaries if not x[0].startswith('tk')]
a.binaries = [x for x in a.binaries if not x[0].startswith('tcl')]
a.binaries = [x for x in a.binaries if not x[0].startswith('_tk')]

# Package pure Python modules and compiled modules
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # Use directory mode for faster startup
    name='neurosymbolic-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress binaries with UPX
    console=True,  # Console application for logging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path if available: 'assets/icon.ico'
)

# Collect all files into a directory
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='neurosymbolic-backend',
)
