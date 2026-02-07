#!/usr/bin/env python3
"""
Cross-platform build script for PyInstaller packaging.

This script handles building the Neurosymbolic Backend API executable
for Windows, Linux, and macOS with proper environment detection.
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
    print("\n" + "=" * 60)
    print(message)
    print("=" * 60 + "\n")


def print_step(step: int, total: int, message: str) -> None:
    """Print a formatted step message."""
    print(f"\n[{step}/{total}] {message}")
    print("-" * 60)


def check_python_version() -> bool:
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major == 3 and version.minor in [10, 11]:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor} is not recommended")
        print("  Recommended: Python 3.10 or 3.11")
        return False


def run_command(cmd: list, description: str) -> bool:
    """Run a command and handle errors."""
    try:
        print(f"  Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        print(f"  Error: {e}")
        if e.stderr:
            print(f"  stderr: {e.stderr}")
        return False


def setup_virtual_environment(venv_dir: Path) -> bool:
    """Create and setup virtual environment."""
    print_step(2, 7, "Setting up virtual environment")
    
    if venv_dir.exists():
        print(f"  Using existing virtual environment: {venv_dir}")
    else:
        print(f"  Creating virtual environment: {venv_dir}")
        if not run_command([sys.executable, "-m", "venv", str(venv_dir)],
                          "Virtual environment creation"):
            return False
    
    return True


def get_venv_python(venv_dir: Path) -> Path:
    """Get path to Python in virtual environment."""
    if platform.system() == "Windows":
        return venv_dir / "Scripts" / "python.exe"
    else:
        return venv_dir / "bin" / "python"


def install_dependencies(venv_python: Path, requirements_file: Path) -> bool:
    """Install dependencies from requirements file."""
    print_step(4, 7, "Installing dependencies")
    print("  This may take several minutes...")
    
    # Upgrade pip
    print("  Upgrading pip...")
    if not run_command([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"],
                      "Pip upgrade"):
        return False
    
    # Install PyInstaller
    print("  Installing PyInstaller...")
    if not run_command([str(venv_python), "-m", "pip", "install", "pyinstaller==6.3.0"],
                      "PyInstaller installation"):
        return False
    
    # Install project dependencies
    print(f"  Installing requirements from {requirements_file}...")
    if not run_command([str(venv_python), "-m", "pip", "install", "-r", str(requirements_file)],
                      "Dependencies installation"):
        return False
    
    return True


def check_pytorch_installation(venv_python: Path) -> None:
    """Check PyTorch installation and CUDA availability."""
    print_step(5, 7, "Checking PyTorch installation")
    
    try:
        result = subprocess.run(
            [str(venv_python), "-c", "import torch; print(f'PyTorch {torch.__version__}')"],
            capture_output=True, text=True, check=True
        )
        print(f"  {result.stdout.strip()}")
        
        result = subprocess.run(
            [str(venv_python), "-c", "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"],
            capture_output=True, text=True, check=True
        )
        print(f"  {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print("  ⚠ Could not check PyTorch installation")


def clean_build_directories() -> None:
    """Clean previous build artifacts."""
    print_step(6, 7, "Cleaning previous build")
    
    dirs_to_clean = [
        Path("dist") / "neurosymbolic-backend",
        Path("build"),
    ]
    
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            print(f"  Removing {dir_path}...")
            shutil.rmtree(dir_path)


def run_pyinstaller(venv_python: Path, spec_file: Path) -> bool:
    """Run PyInstaller to build the executable."""
    print_step(7, 7, "Building executable with PyInstaller")
    print("  This will take 10-30 minutes depending on your system...")
    
    if not run_command([str(venv_python), "-m", "PyInstaller", str(spec_file)],
                      "PyInstaller build"):
        return False
    
    return True


def verify_build() -> bool:
    """Verify the build was successful."""
    print("\n" + "=" * 60)
    print("Verifying build...")
    print("=" * 60)
    
    dist_dir = Path("dist") / "neurosymbolic-backend"
    if not dist_dir.exists():
        print("✗ Build directory not found")
        return False
    
    exe_name = "neurosymbolic-backend.exe" if platform.system() == "Windows" else "neurosymbolic-backend"
    exe_path = dist_dir / exe_name
    
    if not exe_path.exists():
        print(f"✗ Executable not found: {exe_path}")
        return False
    
    print(f"✓ Executable created: {exe_path}")
    
    # Calculate size
    total_size = sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file())
    size_mb = total_size / (1024 * 1024)
    print(f"✓ Build size: {size_mb:.1f} MB")
    
    return True


def print_next_steps() -> None:
    """Print instructions for next steps."""
    print("\n" + "=" * 60)
    print("Build completed successfully!")
    print("=" * 60)
    
    dist_dir = Path("dist") / "neurosymbolic-backend"
    print(f"\nExecutable location: {dist_dir.absolute()}")
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Test the executable:")
    print(f"   cd {dist_dir}")
    
    if platform.system() == "Windows":
        print("   neurosymbolic-backend.exe")
    else:
        print("   ./neurosymbolic-backend")
    
    print("\n2. Check that API starts on http://localhost:8000")
    print("\n3. Install external dependencies if not already installed:")
    print("   - SWI-Prolog: https://www.swi-prolog.org/download/stable")
    print("   - NVIDIA GPU Drivers (optional, for GPU acceleration)")
    
    print("\n" + "=" * 60)


def main():
    """Main build process."""
    parser = argparse.ArgumentParser(
        description="Build Neurosymbolic Backend API executable"
    )
    parser.add_argument(
        "--venv",
        type=str,
        default="venv_build",
        help="Virtual environment directory (default: venv_build)"
    )
    parser.add_argument(
        "--requirements",
        type=str,
        default="backend/requirements.txt",
        help="Requirements file (default: backend/requirements.txt)"
    )
    parser.add_argument(
        "--spec",
        type=str,
        default="backend_api.spec",
        help="PyInstaller spec file (default: backend_api.spec)"
    )
    parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="Skip dependency installation (use existing environment)"
    )
    
    args = parser.parse_args()
    
    # Convert to Path objects
    venv_dir = Path(args.venv)
    requirements_file = Path(args.requirements)
    spec_file = Path(args.spec)
    
    # Verify files exist
    if not requirements_file.exists():
        # Try alternative path
        requirements_file = Path("requirements.txt")
        if not requirements_file.exists():
            print(f"✗ Requirements file not found: {args.requirements}")
            sys.exit(1)
    
    if not spec_file.exists():
        print(f"✗ Spec file not found: {args.spec}")
        sys.exit(1)
    
    print_header("Neurosymbolic Backend - Build Script")
    
    # Step 1: Check Python version
    print_step(1, 7, "Checking Python version")
    if not check_python_version():
        print("\n⚠ Warning: Using non-recommended Python version")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Step 2: Setup virtual environment
    if not setup_virtual_environment(venv_dir):
        sys.exit(1)
    
    venv_python = get_venv_python(venv_dir)
    
    # Step 3: Activate message
    print_step(3, 7, "Using virtual environment")
    print(f"  Python: {venv_python}")
    
    # Step 4: Install dependencies
    if not args.skip_deps:
        if not install_dependencies(venv_python, requirements_file):
            sys.exit(1)
    else:
        print_step(4, 7, "Skipping dependency installation (--skip-deps)")
    
    # Step 5: Check PyTorch
    check_pytorch_installation(venv_python)
    
    # Step 6: Clean build
    clean_build_directories()
    
    # Step 7: Build
    if not run_pyinstaller(venv_python, spec_file):
        print("\n✗ Build failed")
        sys.exit(1)
    
    # Verify
    if not verify_build():
        print("\n✗ Build verification failed")
        sys.exit(1)
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main()
