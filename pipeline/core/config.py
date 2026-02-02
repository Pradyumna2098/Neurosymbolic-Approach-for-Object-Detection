"""Configuration helpers shared by the neurosymbolic pipeline stages."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional

from shared.utils.config_utils import ConfigError, apply_overrides, expand_path, load_config_file

DEFAULT_CONFIG_PATH = Path("shared/configs/pipeline_kaggle.yaml")

_DEFAULTS: Dict[str, Any] = {
    "nms_iou_threshold": 0.6,
    "class_map": {
        0: "plane",
        1: "ship",
        2: "storage_tank",
        3: "baseball_diamond",
        4: "tennis_court",
        5: "basketball_court",
        6: "Ground_Track_Field",
        7: "harbor",
        8: "Bridge",
        9: "large_vehicle",
        10: "small_vehicle",
        11: "helicopter",
        12: "roundabout",
        13: "soccer_ball_field",
        14: "swimming_pool",
    },
}


def load_pipeline_config(
    config_path: Optional[Path], overrides: Mapping[str, Any]
) -> Dict[str, Any]:
    """Load the shared pipeline configuration and apply CLI overrides."""

    config: Dict[str, Any] = dict(_DEFAULTS)

    resolved_path = config_path
    if resolved_path is None and DEFAULT_CONFIG_PATH.is_file():
        resolved_path = DEFAULT_CONFIG_PATH

    if resolved_path is not None:
        config.update(load_config_file(Path(resolved_path)))

    config = apply_overrides(config, overrides)
    config["class_map"] = normalise_class_map(config["class_map"])
    return config


def normalise_class_map(class_map: Any) -> Dict[int, str]:
    """Convert a class-map definition from YAML into a normalised mapping."""

    if isinstance(class_map, Mapping):
        return {int(key): str(value) for key, value in class_map.items()}
    if isinstance(class_map, Iterable):
        return {idx: str(name) for idx, name in enumerate(class_map)}
    raise ConfigError("'class_map' must be defined as a mapping or list in the configuration file.")


def apply_path_overrides(config: Dict[str, Any], keys: Iterable[str]) -> Dict[str, Any]:
    """Expand path-like configuration entries into :class:`~pathlib.Path` objects."""

    for key in keys:
        if key in config:
            config[key] = expand_path(config[key])
    return config


def require_keys(config: Mapping[str, Any], keys: Iterable[str]) -> None:
    """Ensure that required configuration keys are available and non-null."""

    for key in keys:
        if config.get(key) is None:
            raise ConfigError(
                f"Configuration value '{key}' is required. Provide it via the YAML file or CLI flag."
            )
