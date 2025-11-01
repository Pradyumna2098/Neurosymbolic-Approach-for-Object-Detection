"""Symbolic reasoning stage: apply Prolog-driven modifiers to detections."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

from config_utils import ConfigError, PathRequirement, ensure_paths
from pyswip import Prolog

from .config import apply_path_overrides, load_pipeline_config, require_keys
from .utils import (
    apply_symbolic_modifiers,
    load_prolog_modifiers,
    parse_predictions,
    save_predictions_to_file,
    write_explainability_report,
)

_REQUIRED_KEYS = [
    "nms_predictions_dir",
    "refined_predictions_dir",
    "rules_file",
    "report_file",
]


def build_parser() -> argparse.ArgumentParser:
    """Create an argument parser for the symbolic reasoning stage."""

    parser = argparse.ArgumentParser(description="Run the symbolic reasoning stage.")
    parser.add_argument("--config", type=Path, default=None, help="Path to a YAML configuration file.")
    parser.add_argument("--nms-predictions-dir", type=Path, dest="nms_predictions_dir", help="Directory containing NMS-filtered predictions.")
    parser.add_argument("--refined-predictions-dir", type=Path, dest="refined_predictions_dir", help="Directory to save refined predictions.")
    parser.add_argument("--rules-file", type=Path, dest="rules_file", help="Prolog rules file path.")
    parser.add_argument("--report-file", type=Path, dest="report_file", help="Explainability report output path.")
    return parser


def prepare_config(args: argparse.Namespace) -> Dict[str, Any]:
    """Load and validate configuration for the symbolic reasoning stage."""

    overrides = {
        "nms_predictions_dir": args.nms_predictions_dir,
        "refined_predictions_dir": args.refined_predictions_dir,
        "rules_file": args.rules_file,
        "report_file": args.report_file,
    }
    config = load_pipeline_config(args.config, overrides)
    require_keys(config, _REQUIRED_KEYS)
    apply_path_overrides(config, _REQUIRED_KEYS)
    ensure_paths(
        [
            PathRequirement(
                config["nms_predictions_dir"], "NMS predictions", expect_directory=True
            ),
            PathRequirement(
                config["refined_predictions_dir"], "Refined predictions", expect_directory=True, create=True
            ),
            PathRequirement(config["rules_file"], "Prolog rules", expect_directory=False),
            PathRequirement(config["report_file"].parent, "Report parent", expect_directory=True, create=True),
        ]
    )
    return config


def run(config: Mapping[str, Any]) -> None:
    """Run the symbolic reasoning stage using the provided configuration."""

    print("--- Stage 2: Symbolic Reasoning (CPU-only) ---")
    prolog = Prolog()
    prolog.consult(str(config["rules_file"]))
    modifier_map = load_prolog_modifiers(prolog)
    print(f"Loaded {len(modifier_map)} modifier rules.")

    nms_predictions = parse_predictions(config["nms_predictions_dir"])
    print(f"Loaded {len(nms_predictions)} NMS-filtered prediction files.")

    refined_predictions: Dict[str, Any] = {}
    full_report: List[Dict[str, Any]] = []

    for image_name, objects in nms_predictions.items():
        if not objects:
            continue
        refined_objs, report_entries = apply_symbolic_modifiers(
            objects, modifier_map, config["class_map"]
        )
        if refined_objs:
            refined_predictions[image_name] = refined_objs
        for entry in report_entries:
            entry["image_name"] = image_name
            full_report.append(entry)

    save_predictions_to_file(refined_predictions, config["refined_predictions_dir"])
    print(f"Final refined predictions saved to '{config['refined_predictions_dir']}'.")

    if full_report:
        write_explainability_report(full_report, config["report_file"])
        print(f"Explainability report saved to '{config['report_file']}'.")
    else:
        print("No symbolic reasoning actions were logged; explainability report not generated.")


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint for running the symbolic reasoning stage."""

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
