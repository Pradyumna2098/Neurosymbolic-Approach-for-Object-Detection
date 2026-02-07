@echo off
REM Launcher script for Neurosymbolic Backend Server Only
REM This script starts only the backend API server

echo ================================================
echo Neurosymbolic Object Detection Backend Server
echo ================================================
echo.

REM Get the directory where this script is located
set "APP_DIR=%~dp0"
cd /d "%APP_DIR%backend"

echo Starting backend server...
echo API will be available at: http://localhost:8000
echo API documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.
echo ================================================
echo.

REM Start the backend server
neurosymbolic-backend.exe

REM If the server exits, pause so user can see any error messages
echo.
echo ================================================
echo Backend server has stopped.
echo ================================================
pause
