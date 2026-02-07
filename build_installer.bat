@echo off
REM =============================================================================
REM Build script for creating Windows Installer with Inno Setup
REM This script:
REM 1. Builds the backend with PyInstaller
REM 2. Builds the frontend with Electron Forge
REM 3. Creates the Windows installer with Inno Setup
REM =============================================================================

setlocal enabledelayedexpansion

echo =============================================================================
echo Neurosymbolic Object Detection - Windows Installer Build Script
echo =============================================================================
echo.

REM Store the root directory
set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

REM =============================================================================
REM Step 1: Check Prerequisites
REM =============================================================================

echo [1/5] Checking prerequisites...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or 3.11 from https://www.python.org/
    pause
    exit /b 1
)
echo   [OK] Python found

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo   [OK] Node.js found

REM Check if Inno Setup is installed
set "INNO_SETUP_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%INNO_SETUP_PATH%" (
    echo ERROR: Inno Setup is not installed at expected location
    echo Expected: %INNO_SETUP_PATH%
    echo Please install Inno Setup from https://jrsoftware.org/isinfo.php
    echo.
    echo After installation, update INNO_SETUP_PATH in this script if needed.
    pause
    exit /b 1
)
echo   [OK] Inno Setup found

REM Check if required files exist
if not exist "backend_api.spec" (
    echo ERROR: backend_api.spec not found
    echo Please ensure you are running this script from the repository root.
    pause
    exit /b 1
)
echo   [OK] Backend spec file found

if not exist "frontend\package.json" (
    echo ERROR: frontend\package.json not found
    echo Please ensure the frontend directory exists.
    pause
    exit /b 1
)
echo   [OK] Frontend package.json found

if not exist "installer.iss" (
    echo ERROR: installer.iss not found
    echo Please ensure the Inno Setup script exists.
    pause
    exit /b 1
)
echo   [OK] Inno Setup script found

echo.
echo All prerequisites satisfied.
echo.

REM =============================================================================
REM Step 2: Build Backend with PyInstaller
REM =============================================================================

echo [2/5] Building backend with PyInstaller...
echo.

REM Check if we should skip backend build
if "%1"=="--skip-backend" (
    echo Skipping backend build (--skip-backend flag provided)
    if not exist "dist\neurosymbolic-backend" (
        echo ERROR: Backend build not found at dist\neurosymbolic-backend
        echo Please build the backend first or remove --skip-backend flag
        pause
        exit /b 1
    )
    echo Using existing backend build.
) else (
    echo Building backend... This may take 10-30 minutes.
    echo.
    
    REM Run the build script
    python build.py --spec backend_api.spec
    
    if errorlevel 1 (
        echo.
        echo ERROR: Backend build failed
        echo Please check the error messages above.
        pause
        exit /b 1
    )
    
    REM Verify backend build
    if not exist "dist\neurosymbolic-backend\neurosymbolic-backend.exe" (
        echo ERROR: Backend executable not found after build
        pause
        exit /b 1
    )
    
    echo.
    echo Backend build completed successfully.
)

echo.

REM =============================================================================
REM Step 3: Build Frontend with Electron Forge
REM =============================================================================

echo [3/5] Building frontend with Electron Forge...
echo.

REM Check if we should skip frontend build
if "%1"=="--skip-frontend" (
    echo Skipping frontend build (--skip-frontend flag provided)
    if not exist "frontend\out" (
        echo ERROR: Frontend build not found at frontend\out
        echo Please build the frontend first or remove --skip-frontend flag
        pause
        exit /b 1
    )
    echo Using existing frontend build.
) else (
    cd frontend
    
    REM Check if node_modules exists, install if not
    if not exist "node_modules" (
        echo Installing frontend dependencies...
        call npm install
        if errorlevel 1 (
            echo ERROR: npm install failed
            cd ..
            pause
            exit /b 1
        )
    )
    
    echo Building frontend with Electron Forge...
    echo This may take 5-15 minutes.
    echo.
    
    REM Build the frontend
    call npm run package
    
    if errorlevel 1 (
        echo.
        echo ERROR: Frontend build failed
        echo Please check the error messages above.
        cd ..
        pause
        exit /b 1
    )
    
    cd ..
    
    REM Verify frontend build
    if not exist "frontend\out\Neurosymbolic Object Detection-win32-x64" (
        echo ERROR: Frontend build output not found
        echo Expected: frontend\out\Neurosymbolic Object Detection-win32-x64
        pause
        exit /b 1
    )
    
    echo.
    echo Frontend build completed successfully.
)

echo.

REM =============================================================================
REM Step 4: Create Installer with Inno Setup
REM =============================================================================

echo [4/5] Creating Windows installer with Inno Setup...
echo.

REM Create installer_output directory if it doesn't exist
if not exist "installer_output" mkdir installer_output

echo Compiling installer... This may take a few minutes.
echo.

REM Run Inno Setup compiler
"%INNO_SETUP_PATH%" /Q "installer.iss"

if errorlevel 1 (
    echo.
    echo ERROR: Inno Setup compilation failed
    echo Please check the error messages above.
    pause
    exit /b 1
)

REM Verify installer was created
set "INSTALLER_FILE=installer_output\NeurosymbolicApp_Setup_v1.0.0.exe"
if not exist "%INSTALLER_FILE%" (
    echo ERROR: Installer file not created
    echo Expected: %INSTALLER_FILE%
    pause
    exit /b 1
)

echo.
echo Installer created successfully.
echo.

REM =============================================================================
REM Step 5: Display Summary
REM =============================================================================

echo [5/5] Build Summary
echo.
echo =============================================================================
echo Build completed successfully!
echo =============================================================================
echo.

REM Get file size
for %%A in ("%INSTALLER_FILE%") do set "INSTALLER_SIZE=%%~zA"
set /a "INSTALLER_SIZE_MB=!INSTALLER_SIZE! / 1048576"

echo Installer Location: %INSTALLER_FILE%
echo Installer Size: ~!INSTALLER_SIZE_MB! MB
echo.

echo =============================================================================
echo Next Steps:
echo =============================================================================
echo.
echo 1. Test the installer on a clean Windows 10/11 system
echo    - Run the installer as administrator
echo    - Verify desktop and Start Menu shortcuts are created
echo    - Test the application launches correctly
echo    - Test the uninstaller
echo.
echo 2. Before distribution, ensure:
echo    - SWI-Prolog installation instructions are provided
echo    - NVIDIA driver requirements are documented (for GPU support)
echo    - System requirements are clearly stated
echo.
echo 3. Optional: Sign the installer with a code signing certificate
echo    to prevent Windows SmartScreen warnings
echo.
echo =============================================================================
echo.

REM Open the output directory
explorer "installer_output"

echo Press any key to exit...
pause >nul
