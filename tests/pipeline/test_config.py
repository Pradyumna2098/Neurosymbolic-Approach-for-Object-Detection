"""Additional tests for pipeline configuration."""

import pytest
from pathlib import Path
import yaml


def test_pipeline_config_files_exist():
    """Test that pipeline configuration files exist."""
    repo_root = Path(__file__).resolve().parents[2]
    configs_dir = repo_root / "shared"
    
    assert configs_dir.exists(), f"Shared configs directory not found: {configs_dir}"
    
    # Check for expected config files
    expected_configs = [
        "pipeline_kaggle.yaml",
        "pipeline_local.yaml",
        "training_kaggle.yaml",
        "training_local.yaml"
    ]
    
    for config_file in expected_configs:
        config_path = configs_dir / config_file
        assert config_path.exists(), f"Config file not found: {config_path}"


def test_pipeline_config_structure():
    """Test that pipeline config files have valid YAML structure."""
    repo_root = Path(__file__).resolve().parents[2]
    configs_dir = repo_root / "shared"
    
    pipeline_config = configs_dir / "pipeline_local.yaml"
    
    if pipeline_config.exists():
        with open(pipeline_config, 'r') as f:
            config = yaml.safe_load(f)
        
        # Just verify it's a valid YAML and is a dict
        assert isinstance(config, dict), "Config should be a dictionary"
        assert len(config) > 0, "Config should not be empty"
