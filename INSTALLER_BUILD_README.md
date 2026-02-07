# Windows Installer Build Instructions

This directory contains scripts and configuration for creating a Windows installer for the Neurosymbolic Object Detection application using Inno Setup.

## Prerequisites

Before building the installer, ensure you have the following installed:

### Required Software

1. **Python 3.10 or 3.11**
   - Download: https://www.python.org/
   - Required for building the backend with PyInstaller

2. **Node.js 16.x or later**
   - Download: https://nodejs.org/
   - Required for building the frontend with Electron Forge

3. **Inno Setup 6.x**
   - Download: https://jrsoftware.org/isinfo.php
   - Required for creating the Windows installer
   - Install to default location: `C:\Program Files (x86)\Inno Setup 6\`

### Optional (for testing)

4. **SWI-Prolog 8.4.x or later**
   - Download: https://www.swi-prolog.org/download/stable
   - Required by the application for symbolic reasoning
   - Users will need to install this separately

5. **NVIDIA GPU Drivers**
   - Download: https://www.nvidia.com/Download/index.aspx
   - Optional, only needed for GPU acceleration

## Quick Start

### Automated Build (Recommended)

Run the automated build script that handles all steps:

**Windows (Batch Script):**
```batch
build_installer.bat
```

**Cross-Platform (Python Script):**
```bash
python build_installer.py
```

This will:
1. Build the backend with PyInstaller (~10-30 minutes)
2. Build the frontend with Electron Forge (~5-15 minutes)
3. Create the Windows installer with Inno Setup (~2-5 minutes)

### Skip Existing Builds

If you've already built the backend or frontend, you can skip those steps:

```bash
# Skip backend build (use existing build in dist/)
python build_installer.py --skip-backend

# Skip frontend build (use existing build in frontend/out/)
python build_installer.py --skip-frontend

# Skip both (only create installer)
python build_installer.py --skip-backend --skip-frontend
```

## Manual Build Process

If you prefer to build each component separately:

### Step 1: Build Backend

```bash
# Using the build script
python build.py --spec backend_api.spec

# Or manually with PyInstaller
pip install pyinstaller
pyinstaller backend_api.spec
```

Output: `dist/neurosymbolic-backend/`

### Step 2: Build Frontend

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Build the application
npm run package
```

Output: `frontend/out/Neurosymbolic Object Detection-win32-x64/`

### Step 3: Create Installer

Using Inno Setup Compiler (command line):

```batch
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

Or open `installer.iss` in Inno Setup GUI and click Build.

Output: `installer_output/NeurosymbolicApp_Setup_v1.0.0.exe`

## Installer Configuration

The installer is configured in `installer.iss`. Key settings:

### Application Information
- **Name:** Neurosymbolic Object Detection
- **Version:** 1.0.0
- **Publisher:** Pradyumna S R
- **Minimum Windows:** Windows 10 64-bit

### Installation Features
- Installs both frontend and backend
- Creates Start Menu shortcuts
- Optional desktop shortcut
- Optional quick launch shortcut
- Shows license agreement (MIT License)
- Creates data directories with proper permissions
- Checks for SWI-Prolog (warns if not installed)

### Installed Components
```
{app}/
├── frontend/                  # Electron frontend application
│   └── Neurosymbolic Object Detection.exe
├── backend/                   # PyInstaller backend server
│   └── neurosymbolic-backend.exe
├── configs/                   # Configuration examples
├── docs/                      # Documentation
├── data/                      # User data directory
├── models/                    # Model storage directory
├── logs/                      # Application logs
├── start_application.bat      # Quick launcher (both)
├── start_backend.bat          # Backend-only launcher
├── README.txt                 # User guide
└── LICENSE.txt                # License file
```

### Shortcuts Created
- **Start Menu:**
  - Neurosymbolic Object Detection (main app)
  - Neurosymbolic Object Detection Backend Server
  - Neurosymbolic Object Detection Documentation
  - Neurosymbolic Object Detection Uninstall
  
- **Desktop:** (optional)
  - Neurosymbolic Object Detection

- **Quick Launch:** (optional)
  - Neurosymbolic Object Detection

## Testing the Installer

### Testing Checklist

1. **Installation Test**
   - [ ] Run installer as administrator
   - [ ] Verify installation completes without errors
   - [ ] Check installation directory exists
   - [ ] Verify all files are present

2. **Shortcuts Test**
   - [ ] Desktop shortcut created (if selected)
   - [ ] Start Menu shortcuts created
   - [ ] All shortcuts launch correctly

3. **Application Test**
   - [ ] Frontend launches successfully
   - [ ] Backend server starts on http://localhost:8000
   - [ ] API documentation accessible at /docs
   - [ ] Upload and inference work correctly

4. **Uninstaller Test**
   - [ ] Uninstaller runs without errors
   - [ ] Application files removed
   - [ ] Shortcuts removed
   - [ ] User data handling prompt works

### Testing on Clean System

For best results, test on a clean Windows 10 or 11 virtual machine:

1. Install Windows 10/11 (fresh VM recommended)
2. Run the installer
3. Follow on-screen instructions
4. Test all functionality
5. Run uninstaller
6. Verify clean removal

### Known Issues to Test For

1. **SWI-Prolog Missing:**
   - Installer should warn but continue
   - Application should run without symbolic reasoning
   - Error messages should be clear

2. **Port Conflicts:**
   - Backend may fail if port 8000 is in use
   - Application should show helpful error message

3. **Antivirus Warnings:**
   - PyInstaller executables may trigger SmartScreen
   - Consider code signing for production releases

## Customization

### Changing Application Version

Edit in `installer.iss`:
```pascal
#define MyAppVersion "1.0.0"
```

Also update in:
- `frontend/package.json` - `version` field
- `backend/app/__init__.py` - `__version__` variable

### Changing Installation Directory

Edit in `installer.iss`:
```pascal
DefaultDirName={autopf}\YourAppName
```

### Adding Custom Icons

1. Create `.ico` files for application and installer
2. Place in `frontend/src/assets/` or `installer_assets/`
3. Update paths in `installer.iss`:
   ```pascal
   SetupIconFile=path\to\icon.ico
   WizardImageFile=path\to\wizard_large.bmp
   WizardSmallImageFile=path\to\wizard_small.bmp
   ```

### Customizing Installer Messages

Add custom messages in `installer.iss` under `[Messages]` section:
```pascal
[Messages]
WelcomeLabel1=Welcome to [name] Setup
WelcomeLabel2=Custom welcome message here
```

## Troubleshooting

### Build Errors

**"Python not found"**
- Install Python 3.10 or 3.11
- Add Python to PATH during installation

**"Node.js not found"**
- Install Node.js from https://nodejs.org/
- Restart terminal after installation

**"Inno Setup not found"**
- Install from https://jrsoftware.org/isinfo.php
- Use default installation path
- Or update `INNO_SETUP_PATH` in build scripts

**"Backend build failed"**
- Check `build/` directory for detailed logs
- Ensure all dependencies in requirements.txt are installed
- Try running `python build.py` separately to see detailed errors

**"Frontend build failed"**
- Delete `frontend/node_modules` and run `npm install` again
- Check Node.js version (16.x or later required)
- Try running `npm run package` separately in frontend directory

### Installer Issues

**"Installer won't run"**
- Run as administrator
- Temporarily disable antivirus
- Check Windows SmartScreen settings

**"Application won't start"**
- Install Microsoft Visual C++ Redistributable
- Check Windows Event Viewer for error details
- Verify SWI-Prolog installation (for symbolic features)

**"Missing DLL errors"**
- Install Microsoft Visual C++ Redistributable 2015-2022
- Download: https://aka.ms/vs/17/release/vc_redist.x64.exe

## Size Considerations

Expected sizes:
- **Backend build:** ~1.1 GB (CPU) or ~2.8 GB (GPU)
- **Frontend build:** ~150-300 MB
- **Total installer:** ~1.5-3 GB

To reduce size:
- Use CPU-only PyTorch (saves ~1.5 GB)
- Remove unused dependencies
- Enable compression in Inno Setup (already configured)

## CI/CD Integration

To automate installer builds in GitHub Actions:

```yaml
name: Build Windows Installer

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Install Inno Setup
        run: |
          choco install innosetup
      
      - name: Build Installer
        run: |
          python build_installer.py
      
      - name: Upload Installer
        uses: actions/upload-artifact@v3
        with:
          name: windows-installer
          path: installer_output/*.exe
```

## Distribution

Before distributing the installer:

1. **Test thoroughly** on clean Windows systems
2. **Sign the executable** with a code signing certificate (optional but recommended)
3. **Create checksums:**
   ```bash
   certutil -hashfile installer_output\NeurosymbolicApp_Setup_v1.0.0.exe SHA256
   ```
4. **Provide installation instructions** including:
   - System requirements
   - SWI-Prolog installation steps
   - GPU driver requirements (if applicable)
   - Troubleshooting guide

## Support

For issues or questions:
- GitHub Issues: https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection/issues
- Documentation: See `docs/` directory
- User Guide: `EXECUTABLE_README.txt`

## License

This installer and build system are part of the Neurosymbolic Object Detection project and are licensed under the MIT License. See LICENSE file for details.
