"""Additional tests for pipeline configuration."""

import pytest
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[2]))

from pipeline.config import load_config


def test_load_config_from_yaml(tmp_path):
    """Test loading configuration from YAML file."""
    config_file = tmp_path / "test_config.yaml"
    config_content = """
raw_predictions_dir: /test/predictions
refined_predictions_dir: /test/refined
ground_truth_dir: /test/ground_truth
"""
    config_file.write_text(config_content)
    
    config = load_config(str(config_file))
    assert config.raw_predictions_dir == "/test/predictions"
    assert config.refined_predictions_dir == "/test/refined"
    assert config.ground_truth_dir == "/test/ground_truth"


def test_load_config_missing_file():
    """Test error handling for missing config file."""
    with pytest.raises((FileNotFoundError, SystemExit)):
        load_config("/nonexistent/config.yaml")
