"""Utility helpers for loading YAML configuration files and validating paths."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Optional

import yaml


class ConfigError(Exception):
    """Raised when configuration loading or validation fails."""


@dataclass
class PathRequirement:
    path: Path
    description: str
    expect_directory: bool = True
    create: bool = False


def load_config_file(config_path: Path) -> Dict[str, Any]:
    """Load a YAML configuration file and return its contents.

    Parameters
    ----------
    config_path:
        Path to the YAML configuration file.

    Raises
    ------
    ConfigError
        If the configuration file does not exist or cannot be parsed.
    """

    config_path = Path(config_path).expanduser()
    if not config_path.is_file():
        raise ConfigError(f"Configuration file '{config_path}' was not found.")

    try:
        with config_path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except yaml.YAMLError as exc:  # pragma: no cover - defensive programming
        raise ConfigError(f"Could not parse configuration file '{config_path}': {exc}") from exc

    if not isinstance(data, MutableMapping):
        raise ConfigError(
            f"Configuration file '{config_path}' must define a mapping at the top level."
        )

    return dict(data)


def apply_overrides(config: MutableMapping[str, Any], overrides: Mapping[str, Any]) -> Dict[str, Any]:
    """Apply non-``None`` overrides to the configuration mapping."""

    for key, value in overrides.items():
        if value is not None:
            config[key] = value
    return dict(config)


def ensure_paths(requirements: Iterable[PathRequirement]) -> None:
    """Validate that required paths exist, creating directories when requested."""

    for requirement in requirements:
        path = requirement.path.expanduser()
        if requirement.expect_directory:
            if path.is_dir():
                continue
            if requirement.create:
                path.mkdir(parents=True, exist_ok=True)
                continue
            raise ConfigError(f"{requirement.description} directory not found: '{path}'.")
        else:
            if path.is_file():
                continue
            raise ConfigError(f"{requirement.description} file not found: '{path}'.")


def expand_path(value: Optional[str | Path]) -> Optional[Path]:
    """Convert a user-supplied path-like value into a :class:`Path`."""

    if value is None:
        return None
    return Path(value).expanduser()
