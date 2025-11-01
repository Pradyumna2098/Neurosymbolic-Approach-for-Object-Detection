"""Evaluation stage: compute mAP metrics across predictions."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

import torch

from config_utils import ConfigError, PathRequirement, ensure_paths

from .config import apply_path_overrides, load_pipeline_config, require_keys
from .utils import calculate_map, parse_ground_truths, parse_predictions

_REQUIRED_KEYS = [
    "ground_truth_dir",
    "raw_predictions_dir",
    "nms_predictions_dir",
    "refined_predictions_dir",
]


def build_parser() -> argparse.ArgumentParser:
    """Create an argument parser for the evaluation stage."""

    parser = argparse.ArgumentParser(description="Run the evaluation stage.")
    parser.add_argument("--config", type=Path, default=None, help="Path to a YAML configuration file.")
    parser.add_argument("--ground-truth-dir", type=Path, dest="ground_truth_dir", help="Directory containing YOLO-format labels.")
    parser.add_argument("--raw-predictions-dir", type=Path, dest="raw_predictions_dir", help="Directory of raw YOLO predictions.")
    parser.add_argument("--nms-predictions-dir", type=Path, dest="nms_predictions_dir", help="Directory of NMS-filtered predictions.")
    parser.add_argument("--refined-predictions-dir", type=Path, dest="refined_predictions_dir", help="Directory of symbolic-refined predictions.")
    return parser


def prepare_config(args: argparse.Namespace) -> Dict[str, Any]:
    """Load and validate configuration for the evaluation stage."""

    overrides = {
        "ground_truth_dir": args.ground_truth_dir,
        "raw_predictions_dir": args.raw_predictions_dir,
        "nms_predictions_dir": args.nms_predictions_dir,
        "refined_predictions_dir": args.refined_predictions_dir,
    }
    config = load_pipeline_config(args.config, overrides)
    require_keys(config, _REQUIRED_KEYS)
    apply_path_overrides(config, _REQUIRED_KEYS)
    ensure_paths(
        [
            PathRequirement(config["ground_truth_dir"], "Ground truth", expect_directory=True),
            PathRequirement(config["raw_predictions_dir"], "Raw predictions", expect_directory=True),
            PathRequirement(config["nms_predictions_dir"], "NMS predictions", expect_directory=True),
            PathRequirement(config["refined_predictions_dir"], "Refined predictions", expect_directory=True),
        ]
    )
    return config


def run(config: Mapping[str, Any]) -> None:
    """Run the evaluation stage using the provided configuration."""

    print("--- Stage 3: Final Evaluation ---")

    print("Loading ground truths")
    ground_truths = parse_ground_truths(config["ground_truth_dir"])
    print(f"Loaded {len(ground_truths)} ground truth files.")

    print("Loading raw YOLO predictions")
    raw_preds = parse_predictions(config["raw_predictions_dir"])
    print(f"Loaded {len(raw_preds)} raw prediction files.")

    print("Loading NMS-filtered predictions")
    nms_preds = parse_predictions(config["nms_predictions_dir"])
    print(f"Loaded {len(nms_preds)} NMS-filtered prediction files.")

    print("Loading final refined predictions")
    refined_preds = parse_predictions(config["refined_predictions_dir"])
    print(f"Loaded {len(refined_preds)} refined prediction files.")

    print("\n--- Calculating mAP for Raw YOLO Detections ---")
    map_raw = calculate_map(raw_preds, ground_truths)

    print("\n--- Calculating mAP for NMS-Filtered Detections ---")
    map_nms = calculate_map(nms_preds, ground_truths)

    print("\n--- Calculating mAP for Final Symbolic-Refined Detections ---")
    map_refined = calculate_map(refined_preds, ground_truths)

    print("\n\n--- 🏆 FINAL RESULTS COMPARISON ---")
    print("Metric          | Raw YOLO | NMS Only | Symbolic Refined")
    print("----------------|----------|----------|-----------------")

    map50_raw = map_raw.get("map_50", torch.tensor(-1.0)).item()
    map50_nms = map_nms.get("map_50", torch.tensor(-1.0)).item()
    map50_refined = map_refined.get("map_50", torch.tensor(-1.0)).item()
    print(f"mAP@.50         | {map50_raw:.4f}   | {map50_nms:.4f}   | {map50_refined:.4f}")

    map_raw_val = map_raw.get("map", torch.tensor(-1.0)).item()
    map_nms_val = map_nms.get("map", torch.tensor(-1.0)).item()
    map_refined_val = map_refined.get("map", torch.tensor(-1.0)).item()
    print(f"mAP@.50:.95     | {map_raw_val:.4f}   | {map_nms_val:.4f}   | {map_refined_val:.4f}")
    print("==================================================")


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint for running the evaluation stage."""

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
