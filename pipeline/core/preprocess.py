"""Pre-processing stage: apply NMS filtering to raw detections."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

from shared.utils.config_utils import ConfigError, PathRequirement, ensure_paths

from pipeline.core.config import apply_path_overrides, load_pipeline_config, require_keys
from pipeline.core.utils import parse_predictions_for_nms, pre_filter_with_nms, save_predictions_to_file

_REQUIRED_KEYS = ["raw_predictions_dir", "nms_predictions_dir"]


def build_parser() -> argparse.ArgumentParser:
    """Create an argument parser for the preprocessing CLI entrypoint."""

    parser = argparse.ArgumentParser(description="Run the NMS preprocessing stage.")
    parser.add_argument("--config", type=Path, default=None, help="Path to a YAML configuration file.")
    parser.add_argument("--raw-predictions-dir", type=Path, dest="raw_predictions_dir", help="Directory of raw YOLO predictions.")
    parser.add_argument("--nms-predictions-dir", type=Path, dest="nms_predictions_dir", help="Directory to save NMS-filtered predictions.")
    parser.add_argument("--nms-iou-threshold", type=float, dest="nms_iou_threshold", help="IOU threshold used for NMS stage.")
    return parser


def prepare_config(args: argparse.Namespace) -> Dict[str, Any]:
    """Load and validate configuration for the preprocessing stage."""

    overrides = {
        "raw_predictions_dir": args.raw_predictions_dir,
        "nms_predictions_dir": args.nms_predictions_dir,
        "nms_iou_threshold": args.nms_iou_threshold,
    }
    config = load_pipeline_config(args.config, overrides)
    require_keys(config, _REQUIRED_KEYS)
    apply_path_overrides(config, _REQUIRED_KEYS)
    ensure_paths(
        [
            PathRequirement(config["raw_predictions_dir"], "Raw predictions", expect_directory=True),
            PathRequirement(
                config["nms_predictions_dir"], "NMS predictions", expect_directory=True, create=True
            ),
        ]
    )
    return config


def run(config: Mapping[str, Any]) -> None:
    """Run the preprocessing stage using the provided configuration."""

    print("--- Stage 1: Pre-processing with NMS ---")
    raw_predictions = parse_predictions_for_nms(config["raw_predictions_dir"])
    print(f"Loaded {len(raw_predictions)} raw prediction files.")

    nms_predictions: Dict[str, Any] = {}
    total_before, total_after = 0, 0
    for image_name, objects in raw_predictions.items():
        total_before += len(objects)
        filtered = pre_filter_with_nms(objects, float(config["nms_iou_threshold"]))
        total_after += len(filtered)
        if filtered:
            nms_predictions[image_name] = filtered

    print(f"NMS completed. Reduced detections from {total_before} to {total_after}.")
    save_predictions_to_file(nms_predictions, config["nms_predictions_dir"])
    print(f"Cleaned predictions saved to '{config['nms_predictions_dir']}'.")


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint for running the preprocessing stage."""

    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = prepare_config(args)
    except ConfigError as exc:  # pragma: no cover - CLI error handling
        parser.error(str(exc))
    run(config)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
