@echo off
REM Build script for Windows executable packaging with PyInstaller
REM This script packages the Neurosymbolic Object Detection Backend API

echo ========================================
echo Neurosymbolic Backend - Build Script
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or 3.11
    pause
    exit /b 1
)

echo [1/6] Checking Python version...
python --version

REM Check if virtual environment exists
if not exist "venv_build" (
    echo.
    echo [2/6] Creating virtual environment...
    python -m venv venv_build
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo.
    echo [2/6] Using existing virtual environment...
)

REM Activate virtual environment
echo.
echo [3/6] Activating virtual environment...
call venv_build\Scripts\activate.bat

REM Upgrade pip
echo.
echo [4/6] Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo [5/6] Installing dependencies...
echo This may take several minutes...

REM Install PyInstaller first
pip install pyinstaller==6.3.0

REM Install backend requirements
if exist "backend\requirements.txt" (
    echo Installing backend requirements...
    pip install -r backend\requirements.txt
) else if exist "requirements.txt" (
    echo Installing common requirements...
    pip install -r requirements.txt
) else (
    echo ERROR: No requirements.txt found
    pause
    exit /b 1
)

REM Check for GPU vs CPU PyTorch
echo.
echo Checking PyTorch installation...
python -c "import torch; print(f'PyTorch {torch.__version__}')"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

REM Clean previous build
echo.
echo [6/6] Building executable...
if exist "dist\neurosymbolic-backend" (
    echo Cleaning previous build...
    rmdir /s /q dist\neurosymbolic-backend
)
if exist "build" (
    rmdir /s /q build
)

REM Run PyInstaller
echo.
echo Running PyInstaller...
echo This will take 10-30 minutes depending on your system...
pyinstaller backend_api.spec

if %errorlevel% neq 0 (
    echo.
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

REM Verify build
echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Executable location: dist\neurosymbolic-backend\
echo.

REM Test the executable
echo Testing executable...
dist\neurosymbolic-backend\neurosymbolic-backend.exe --help >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Executable runs successfully
) else (
    echo ! Executable may have issues - check manually
)

echo.
echo Build size:
dir dist\neurosymbolic-backend /s | find "File(s)"

echo.
echo ========================================
echo Next Steps:
echo ========================================
echo 1. Test the executable: cd dist\neurosymbolic-backend
echo 2. Run: neurosymbolic-backend.exe
echo 3. Check that API starts on http://localhost:8000
echo 4. Install SWI-Prolog if not already installed
echo.
echo Note: SWI-Prolog must be installed separately
echo Download from: https://www.swi-prolog.org/download/stable
echo.

pause
