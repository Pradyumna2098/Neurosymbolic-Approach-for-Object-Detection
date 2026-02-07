@echo off
REM Launcher script for Neurosymbolic Object Detection Application
REM This script starts both the backend server and frontend application

echo ================================================
echo Neurosymbolic Object Detection Application
echo ================================================
echo.

REM Get the directory where this script is located
set "APP_DIR=%~dp0"
cd /d "%APP_DIR%"

echo Starting backend server...
echo.

REM Start the backend server in a new window
start "Neurosymbolic Backend" "%APP_DIR%backend\neurosymbolic-backend.exe"

REM Wait a few seconds for the backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Check if backend is running
tasklist /FI "IMAGENAME eq neurosymbolic-backend.exe" 2>NUL | find /I /N "neurosymbolic-backend.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Backend server started successfully.
) else (
    echo Warning: Backend server may not have started properly.
    echo Please check the backend console window for errors.
)

echo.
echo Starting frontend application...
echo.

REM Start the frontend application
start "Neurosymbolic Frontend" "%APP_DIR%frontend\Neurosymbolic Object Detection.exe"

echo.
echo ================================================
echo Application launched!
echo ================================================
echo.
echo Backend API: http://localhost:8000
echo Frontend: Running in separate window
echo.
echo To stop the application:
echo 1. Close the frontend window
echo 2. Close the backend console window or press Ctrl+C
echo.
echo This window will close in 5 seconds...
timeout /t 5 /nobreak >nul
