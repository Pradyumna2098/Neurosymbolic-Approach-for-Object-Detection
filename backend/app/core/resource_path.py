"""Resource path utilities for PyInstaller bundled executables.

This module provides helpers to locate resources (files, directories) in both
development and PyInstaller-bundled environments.
"""

import sys
from pathlib import Path
from typing import Union


def get_resource_path(relative_path: Union[str, Path]) -> Path:
    """Get absolute path to resource, works for dev and PyInstaller bundle.
    
    When running as a PyInstaller executable, resources are extracted to
    a temporary directory (sys._MEIPASS). This function handles both cases.
    
    Args:
        relative_path: Path relative to the application root.
    
    Returns:
        Absolute path to the resource.
    
    Example:
        >>> config_path = get_resource_path('shared/configs/pipeline.yaml')
        >>> prolog_rules = get_resource_path('pipeline/prolog/rules.pl')
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running in PyInstaller bundle
        base_path = Path(sys._MEIPASS)
    else:
        # Running in normal Python environment
        # Go up from backend/app/core to repository root
        base_path = Path(__file__).parent.parent.parent.parent
    
    return base_path / relative_path


def get_data_path(relative_path: Union[str, Path] = '') -> Path:
    """Get path to data directory, always in writable location.
    
    Data directory is never bundled in the executable and must be in a
    writable location. This returns the path relative to the executable
    or script location.
    
    Environment variable DATA_ROOT can be used to override the default location.
    
    Args:
        relative_path: Path relative to data root.
    
    Returns:
        Absolute path to data location.
    
    Example:
        >>> uploads_dir = get_data_path('uploads')
        >>> results_dir = get_data_path('results/job_001')
    """
    # Check for environment variable override
    env_data_root = sys.modules.get('os', __import__('os')).environ.get('DATA_ROOT')
    
    if env_data_root:
        base_path = Path(env_data_root)
    elif getattr(sys, 'frozen', False):
        # Running as executable - use directory where exe is located
        # Note: This may not be writable in protected locations (e.g., Program Files)
        # Users should set DATA_ROOT environment variable for such cases
        base_path = Path(sys.executable).parent / 'data'
    else:
        # Running in development - use backend/data or root data
        base_path = Path(__file__).parent.parent.parent / 'data'
    
    if relative_path:
        return base_path / relative_path
    return base_path


def get_models_path(relative_path: Union[str, Path] = '') -> Path:
    """Get path to models directory.
    
    Models are not bundled due to their large size. They should be placed
    in a 'models' directory next to the executable or in the project root.
    
    Args:
        relative_path: Path relative to models directory.
    
    Returns:
        Absolute path to models location.
    
    Example:
        >>> yolo_model = get_models_path('best.pt')
        >>> custom_model = get_models_path('custom/yolo11m.pt')
    """
    if getattr(sys, 'frozen', False):
        # Running as executable
        base_path = Path(sys.executable).parent / 'models'
    else:
        # Running in development
        base_path = Path(__file__).parent.parent.parent.parent / 'models'
    
    if relative_path:
        return base_path / relative_path
    return base_path


def is_frozen() -> bool:
    """Check if running as PyInstaller executable.
    
    Returns:
        True if running as frozen executable, False otherwise.
    
    Example:
        >>> if is_frozen():
        ...     print("Running as executable")
        ... else:
        ...     print("Running in development")
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def get_executable_dir() -> Path:
    """Get directory containing the executable or script.
    
    Returns:
        Path to directory containing executable or main script.
    
    Example:
        >>> exe_dir = get_executable_dir()
        >>> print(f"Application running from: {exe_dir}")
    """
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent.parent.parent.parent


def ensure_writable_paths() -> None:
    """Ensure all required writable directories exist.
    
    Creates data, models, and logs directories if they don't exist.
    Should be called at application startup.
    
    Raises:
        OSError: If directories cannot be created.
    """
    data_dir = get_data_path()
    models_dir = get_models_path()
    logs_dir = get_executable_dir() / 'logs'
    
    for directory in [data_dir, models_dir, logs_dir]:
        directory.mkdir(parents=True, exist_ok=True)
        
        # Verify directory is writable
        test_file = directory / '.write_test'
        try:
            test_file.touch()
            test_file.unlink()
        except (OSError, PermissionError) as e:
            raise OSError(f"Directory not writable: {directory}") from e


def check_swipl_available() -> bool:
    """Check if SWI-Prolog is available on the system.
    
    PySwip requires SWI-Prolog to be installed separately. This function
    checks if it can be found.
    
    Returns:
        True if SWI-Prolog is available, False otherwise.
    
    Example:
        >>> if not check_swipl_available():
        ...     print("Warning: SWI-Prolog not found")
        ...     print("Symbolic reasoning will be disabled")
    """
    try:
        # Try to import pyswip
        from pyswip import Prolog
        
        # Try to create a Prolog instance
        Prolog()
        return True
    except Exception:
        return False


def get_runtime_info() -> dict:
    """Get information about the runtime environment.
    
    Useful for debugging and logging.
    
    Returns:
        Dictionary with runtime information.
    
    Example:
        >>> info = get_runtime_info()
        >>> print(f"Frozen: {info['frozen']}")
        >>> print(f"Python: {info['python_version']}")
    """
    import platform
    
    info = {
        'frozen': is_frozen(),
        'python_version': sys.version,
        'platform': platform.platform(),
        'executable_dir': str(get_executable_dir()),
        'data_dir': str(get_data_path()),
        'models_dir': str(get_models_path()),
        'swipl_available': check_swipl_available(),
    }
    
    if is_frozen():
        info['meipass'] = sys._MEIPASS
        info['executable'] = sys.executable
    
    return info
