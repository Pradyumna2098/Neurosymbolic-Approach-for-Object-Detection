#!/usr/bin/env python3
"""
Windows Installer Build Script for Neurosymbolic Object Detection Application

This script automates the process of:
1. Building the backend with PyInstaller
2. Building the frontend with Electron Forge
3. Creating the Windows installer with Inno Setup

Usage:
    python build_installer.py
    python build_installer.py --skip-backend
    python build_installer.py --skip-frontend
    python build_installer.py --skip-backend --skip-frontend
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def print_header(message: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(message)
    print("=" * 80 + "\n")


def print_step(step: int, total: int, message: str) -> None:
    """Print a formatted step message."""
    print(f"\n[{step}/{total}] {message}")
    print("-" * 80)


def check_command_available(command: str, install_url: str = None) -> bool:
    """Check if a command is available in PATH."""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        print(f"  ✓ {command} found")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"  ✗ {command} not found")
        if install_url:
            print(f"    Install from: {install_url}")
        return False


def check_file_exists(file_path: Path, description: str) -> bool:
    """Check if a file exists."""
    if file_path.exists():
        print(f"  ✓ {description} found")
        return True
    else:
        print(f"  ✗ {description} not found: {file_path}")
        return False


def check_prerequisites() -> bool:
    """Check if all prerequisites are met."""
    print_step(1, 5, "Checking prerequisites")
    
    # Check Python
    if not check_command_available("python", "https://www.python.org/"):
        return False
    
    # Check Node.js
    if not check_command_available("node", "https://nodejs.org/"):
        return False
    
    # Check npm
    if not check_command_available("npm", "https://nodejs.org/"):
        return False
    
    # Check Inno Setup (Windows only)
    if platform.system() == "Windows":
        inno_paths = [
            Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
            Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
        ]
        
        inno_found = False
        for inno_path in inno_paths:
            if inno_path.exists():
                print(f"  ✓ Inno Setup found at {inno_path}")
                inno_found = True
                break
        
        if not inno_found:
            print("  ✗ Inno Setup not found")
            print("    Install from: https://jrsoftware.org/isinfo.php")
            return False
    else:
        print("  ⚠ Warning: Not running on Windows. Inno Setup compilation will be skipped.")
    
    # Check required files
    if not check_file_exists(Path("backend_api.spec"), "Backend spec file"):
        return False
    
    if not check_file_exists(Path("frontend/package.json"), "Frontend package.json"):
        return False
    
    if not check_file_exists(Path("installer.iss"), "Inno Setup script"):
        return False
    
    print("\n✓ All prerequisites satisfied")
    return True


def build_backend(skip: bool = False) -> bool:
    """Build the backend with PyInstaller."""
    print_step(2, 5, "Building backend with PyInstaller")
    
    if skip:
        print("Skipping backend build (--skip-backend flag provided)")
        backend_dir = Path("dist/neurosymbolic-backend")
        if not backend_dir.exists():
            print(f"✗ Backend build not found at {backend_dir}")
            print("  Please build the backend first or remove --skip-backend flag")
            return False
        print("Using existing backend build")
        return True
    
    print("Building backend... This may take 10-30 minutes.")
    
    try:
        # Run the build script
        result = subprocess.run(
            [sys.executable, "build.py", "--spec", "backend_api.spec"],
            check=True
        )
        
        # Verify backend build
        backend_exe = Path("dist/neurosymbolic-backend/neurosymbolic-backend.exe")
        if not backend_exe.exists():
            print(f"✗ Backend executable not found after build: {backend_exe}")
            return False
        
        print("\n✓ Backend build completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Backend build failed: {e}")
        return False


def build_frontend(skip: bool = False) -> bool:
    """Build the frontend with Electron Forge."""
    print_step(3, 5, "Building frontend with Electron Forge")
    
    if skip:
        print("Skipping frontend build (--skip-frontend flag provided)")
        frontend_out = Path("frontend/out")
        if not frontend_out.exists():
            print(f"✗ Frontend build not found at {frontend_out}")
            print("  Please build the frontend first or remove --skip-frontend flag")
            return False
        print("Using existing frontend build")
        return True
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print(f"✗ Frontend directory not found: {frontend_dir}")
        return False
    
    # Check if node_modules exists
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("Installing frontend dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        except subprocess.CalledProcessError as e:
            print(f"✗ npm install failed: {e}")
            return False
    
    print("Building frontend with Electron Forge...")
    print("This may take 5-15 minutes.")
    
    try:
        # Run npm package command
        subprocess.run(["npm", "run", "package"], cwd=frontend_dir, check=True)
        
        # Verify frontend build
        frontend_out = frontend_dir / "out" / "Neurosymbolic Object Detection-win32-x64"
        if not frontend_out.exists():
            print(f"✗ Frontend build output not found: {frontend_out}")
            return False
        
        print("\n✓ Frontend build completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Frontend build failed: {e}")
        return False


def create_installer() -> bool:
    """Create the Windows installer with Inno Setup."""
    print_step(4, 5, "Creating Windows installer with Inno Setup")
    
    if platform.system() != "Windows":
        print("⚠ Skipping Inno Setup compilation (not running on Windows)")
        return True
    
    # Find Inno Setup compiler
    inno_paths = [
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
    ]
    
    iscc_path = None
    for path in inno_paths:
        if path.exists():
            iscc_path = path
            break
    
    if not iscc_path:
        print("✗ Inno Setup compiler not found")
        return False
    
    # Create output directory
    output_dir = Path("installer_output")
    output_dir.mkdir(exist_ok=True)
    
    print("Compiling installer... This may take a few minutes.")
    
    try:
        # Run Inno Setup compiler
        result = subprocess.run(
            [str(iscc_path), "/Q", "installer.iss"],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Verify installer was created
        installer_file = output_dir / "NeurosymbolicApp_Setup_v1.0.0.exe"
        if not installer_file.exists():
            print(f"✗ Installer file not created: {installer_file}")
            return False
        
        # Get file size
        size_mb = installer_file.stat().st_size / (1024 * 1024)
        
        print("\n✓ Installer created successfully")
        print(f"  Location: {installer_file}")
        print(f"  Size: ~{size_mb:.1f} MB")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Inno Setup compilation failed: {e}")
        if e.stderr:
            print(f"  Error output: {e.stderr}")
        return False


def print_summary() -> None:
    """Print build summary and next steps."""
    print_step(5, 5, "Build Summary")
    
    print_header("Build completed successfully!")
    
    installer_file = Path("installer_output/NeurosymbolicApp_Setup_v1.0.0.exe")
    if installer_file.exists():
        size_mb = installer_file.stat().st_size / (1024 * 1024)
        print(f"Installer Location: {installer_file.absolute()}")
        print(f"Installer Size: ~{size_mb:.1f} MB")
    
    print("\n" + "=" * 80)
    print("Next Steps:")
    print("=" * 80)
    
    print("\n1. Test the installer on a clean Windows 10/11 system")
    print("   - Run the installer as administrator")
    print("   - Verify desktop and Start Menu shortcuts are created")
    print("   - Test the application launches correctly")
    print("   - Test the uninstaller")
    
    print("\n2. Before distribution, ensure:")
    print("   - SWI-Prolog installation instructions are provided")
    print("   - NVIDIA driver requirements are documented (for GPU support)")
    print("   - System requirements are clearly stated")
    
    print("\n3. Optional: Sign the installer with a code signing certificate")
    print("   to prevent Windows SmartScreen warnings")
    
    print("\n" + "=" * 80)


def main():
    """Main build process."""
    parser = argparse.ArgumentParser(
        description="Build Windows installer for Neurosymbolic Object Detection"
    )
    parser.add_argument(
        "--skip-backend",
        action="store_true",
        help="Skip backend build (use existing build)"
    )
    parser.add_argument(
        "--skip-frontend",
        action="store_true",
        help="Skip frontend build (use existing build)"
    )
    
    args = parser.parse_args()
    
    print_header("Neurosymbolic Object Detection - Windows Installer Build Script")
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n✗ Prerequisites check failed")
        print("Please install missing dependencies and try again.")
        sys.exit(1)
    
    # Build backend
    if not build_backend(skip=args.skip_backend):
        print("\n✗ Backend build failed")
        sys.exit(1)
    
    # Build frontend
    if not build_frontend(skip=args.skip_frontend):
        print("\n✗ Frontend build failed")
        sys.exit(1)
    
    # Create installer
    if not create_installer():
        print("\n✗ Installer creation failed")
        sys.exit(1)
    
    # Print summary
    print_summary()


if __name__ == "__main__":
    main()
