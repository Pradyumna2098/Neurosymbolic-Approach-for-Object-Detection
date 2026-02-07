#!/usr/bin/env python3
"""
Create distribution package for the Neurosymbolic Backend executable.

This script packages the PyInstaller-built executable with all necessary
support files into a clean distribution directory.
"""

import argparse
import shutil
import sys
from pathlib import Path


def print_step(message: str) -> None:
    """Print a formatted step message."""
    print(f"\n{'=' * 70}")
    print(f"  {message}")
    print(f"{'=' * 70}\n")


def create_distribution_structure(dist_root: Path) -> dict:
    """Create the distribution directory structure.
    
    Args:
        dist_root: Root directory for distribution
        
    Returns:
        Dictionary mapping directory names to paths
    """
    print_step("Creating distribution structure")
    
    directories = {
        'root': dist_root,
        'executable': dist_root / 'neurosymbolic-backend',
        'configs': dist_root / 'configs',
        'models': dist_root / 'models',
        'data': dist_root / 'data',
        'docs': dist_root / 'docs',
    }
    
    for name, path in directories.items():
        if name != 'executable':  # Don't create executable dir, will be copied
            path.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ Created: {path}")
    
    return directories


def copy_executable(source_dir: Path, dest_dir: Path) -> bool:
    """Copy the PyInstaller executable directory.
    
    Args:
        source_dir: Source executable directory (dist/neurosymbolic-backend)
        dest_dir: Destination directory
        
    Returns:
        True if successful
    """
    print_step("Copying executable")
    
    if not source_dir.exists():
        print(f"  ✗ Executable directory not found: {source_dir}")
        print(f"    Run build script first!")
        return False
    
    if dest_dir.exists():
        print(f"  Removing existing: {dest_dir}")
        shutil.rmtree(dest_dir)
    
    print(f"  Copying: {source_dir} -> {dest_dir}")
    shutil.copytree(source_dir, dest_dir)
    
    # Calculate size
    total_size = sum(f.stat().st_size for f in dest_dir.rglob('*') if f.is_file())
    size_mb = total_size / (1024 * 1024)
    print(f"  ✓ Copied executable ({size_mb:.1f} MB)")
    
    return True


def copy_configs(source_dir: Path, dest_dir: Path) -> None:
    """Copy example configuration files.
    
    Args:
        source_dir: Source configs directory
        dest_dir: Destination configs directory
    """
    print_step("Copying configuration examples")
    
    # Copy .env.example to configs directory
    env_example = source_dir / '.env.example'
    if env_example.exists():
        shutil.copy2(env_example, dest_dir / '.env.example')
        print(f"  ✓ Copied: .env.example")
    
    # Copy sample configs from shared/configs if they exist
    shared_configs = Path('shared/configs')
    if shared_configs.exists():
        for config_file in shared_configs.glob('*.yaml'):
            # Copy as example files
            dest_file = dest_dir / f"{config_file.stem}_example.yaml"
            shutil.copy2(config_file, dest_file)
            print(f"  ✓ Copied: {config_file.name} -> {dest_file.name}")


def create_readme_files(dist_root: Path) -> None:
    """Create README files for empty directories.
    
    Args:
        dist_root: Distribution root directory
    """
    print_step("Creating README files")
    
    # Models directory README
    models_readme = dist_root / 'models' / 'README.txt'
    models_readme.write_text(
        "Place your trained YOLO model files here.\n\n"
        "Example:\n"
        "  models/\n"
        "    best.pt\n"
        "    yolov11m-obb.pt\n\n"
        "Configure the model path in .env:\n"
        "  MODEL_PATH=./models/best.pt\n"
    )
    print(f"  ✓ Created: models/README.txt")
    
    # Data directory README
    data_readme = dist_root / 'data' / 'README.txt'
    data_readme.write_text(
        "This directory is used for application data storage.\n\n"
        "Subdirectories created on first run:\n"
        "  uploads/         - Uploaded images\n"
        "  jobs/            - Job metadata\n"
        "  results/         - Processing results\n"
        "  visualizations/  - Output visualizations\n\n"
        "This directory should have write permissions.\n"
    )
    print(f"  ✓ Created: data/README.txt")


def copy_documentation(dest_dir: Path) -> None:
    """Copy documentation files.
    
    Args:
        dest_dir: Destination docs directory
    """
    print_step("Copying documentation")
    
    # Copy main executable readme
    readme_source = Path('EXECUTABLE_README.txt')
    if readme_source.exists():
        shutil.copy2(readme_source, dest_dir.parent / 'README.txt')
        print(f"  ✓ Copied: README.txt")
    
    # Copy license if exists
    license_source = Path('LICENSE')
    if license_source.exists():
        shutil.copy2(license_source, dest_dir.parent / 'LICENSE.txt')
        print(f"  ✓ Copied: LICENSE.txt")
    
    # Copy documentation from docs/ if desired
    # For now, just copy key guides
    docs_to_copy = [
        'docs/feature_implementation/WINDOWS_PACKAGING_GUIDE.md',
        'docs/feature_implementation/WINDOWS_EXECUTABLE_USER_GUIDE.md',
    ]
    
    for doc_path in docs_to_copy:
        doc_file = Path(doc_path)
        if doc_file.exists():
            dest_file = dest_dir / doc_file.name
            shutil.copy2(doc_file, dest_file)
            print(f"  ✓ Copied: {doc_file.name}")


def create_installer_manifest(dist_root: Path) -> None:
    """Create manifest file listing all files in distribution.
    
    Args:
        dist_root: Distribution root directory
    """
    print_step("Creating distribution manifest")
    
    manifest_file = dist_root / 'MANIFEST.txt'
    
    with manifest_file.open('w', encoding='utf-8') as f:
        f.write("Neurosymbolic Object Detection - Distribution Manifest\n")
        f.write("=" * 60 + "\n\n")
        
        # List all files
        all_files = sorted(dist_root.rglob('*'))
        file_count = 0
        total_size = 0
        
        for file_path in all_files:
            if file_path.is_file():
                rel_path = file_path.relative_to(dist_root)
                size = file_path.stat().st_size
                total_size += size
                file_count += 1
                
                size_mb = size / (1024 * 1024)
                f.write(f"{rel_path}\t({size_mb:.2f} MB)\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write(f"Total files: {file_count}\n")
        f.write(f"Total size: {total_size / (1024 * 1024):.1f} MB\n")
    
    print(f"  ✓ Created: MANIFEST.txt")
    print(f"    Files: {file_count}")
    print(f"    Size: {total_size / (1024 * 1024):.1f} MB")


def create_batch_launcher(dist_root: Path) -> None:
    """Create a Windows batch file launcher.
    
    Args:
        dist_root: Distribution root directory
    """
    print_step("Creating launcher scripts")
    
    launcher_bat = dist_root / 'start_server.bat'
    launcher_bat.write_text(
        '@echo off\n'
        'echo Starting Neurosymbolic Backend API...\n'
        'echo.\n'
        'cd neurosymbolic-backend\n'
        'neurosymbolic-backend.exe\n'
        'pause\n'
    )
    print(f"  ✓ Created: start_server.bat")


def package_distribution(dist_root: Path, output_name: str) -> bool:
    """Create a ZIP archive of the distribution.
    
    Args:
        dist_root: Distribution root directory
        output_name: Name for the output archive (without extension)
        
    Returns:
        True if successful
    """
    print_step("Creating distribution archive")
    
    try:
        output_file = dist_root.parent / output_name
        
        print(f"  Creating archive: {output_file}.zip")
        shutil.make_archive(str(output_file), 'zip', dist_root)
        
        archive_size = (output_file.with_suffix('.zip')).stat().st_size / (1024 * 1024)
        print(f"  ✓ Created: {output_file}.zip ({archive_size:.1f} MB)")
        
        return True
    except Exception as e:
        print(f"  ✗ Failed to create archive: {e}")
        return False


def main():
    """Main distribution creation process."""
    parser = argparse.ArgumentParser(
        description="Create distribution package for Neurosymbolic Backend"
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='NeurosymbolicApp_v1.0',
        help='Output directory name (default: NeurosymbolicApp_v1.0)'
    )
    parser.add_argument(
        '--no-archive',
        action='store_true',
        help='Skip creating ZIP archive'
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("  Neurosymbolic Backend - Distribution Packager")
    print("=" * 70)
    
    # Paths
    executable_source = Path('dist/neurosymbolic-backend')
    dist_root = Path('dist') / args.output_dir
    
    # Verify executable exists
    if not executable_source.exists():
        print("\n✗ ERROR: Executable not found!")
        print(f"  Expected: {executable_source}")
        print("\n  Build the executable first:")
        print("    python build.py")
        sys.exit(1)
    
    # Create distribution
    directories = create_distribution_structure(dist_root)
    
    if not copy_executable(executable_source, directories['executable']):
        sys.exit(1)
    
    copy_configs(Path('backend'), directories['configs'])
    create_readme_files(dist_root)
    copy_documentation(directories['docs'])
    create_installer_manifest(dist_root)
    create_batch_launcher(dist_root)
    
    # Create archive
    if not args.no_archive:
        package_distribution(dist_root, args.output_dir)
    
    # Final summary
    print("\n" + "=" * 70)
    print("  Distribution created successfully!")
    print("=" * 70)
    print(f"\nLocation: {dist_root.absolute()}")
    
    if not args.no_archive:
        archive_path = dist_root.parent / f"{dist_root.name}.zip"
        print(f"Archive: {archive_path.absolute()}")
    
    print("\nContents:")
    print("  neurosymbolic-backend/  - Executable and dependencies")
    print("  configs/                - Configuration examples")
    print("  models/                 - Place your models here")
    print("  data/                   - Working directory")
    print("  docs/                   - Documentation")
    print("  README.txt              - User guide")
    print("  start_server.bat        - Quick launcher")
    
    print("\nNext steps:")
    print("  1. Test the distribution on a clean Windows machine")
    print("  2. Ensure SWI-Prolog is installed")
    print("  3. Place your model files in models/")
    print("  4. Run start_server.bat to start the API")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
