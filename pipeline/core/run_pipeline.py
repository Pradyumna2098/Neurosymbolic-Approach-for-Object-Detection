"""Runner script that orchestrates all neurosymbolic pipeline stages."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from shared.utils.config_utils import ConfigError

from pipeline.core import eval as evaluation
from pipeline.core import preprocess, symbolic


def build_parser() -> argparse.ArgumentParser:
    """Create an argument parser for executing the full pipeline."""

    parser = argparse.ArgumentParser(description="Run the full neurosymbolic pipeline.")
    parser.add_argument("--config", type=Path, default=None, help="Path to a YAML configuration file.")
    parser.add_argument("--raw-predictions-dir", type=Path, dest="raw_predictions_dir", help="Directory of raw YOLO predictions.")
    parser.add_argument("--nms-predictions-dir", type=Path, dest="nms_predictions_dir", help="Directory for NMS-filtered predictions.")
    parser.add_argument("--refined-predictions-dir", type=Path, dest="refined_predictions_dir", help="Directory for refined predictions.")
    parser.add_argument("--ground-truth-dir", type=Path, dest="ground_truth_dir", help="Directory containing YOLO-format labels.")
    parser.add_argument("--rules-file", type=Path, dest="rules_file", help="Prolog rules file path.")
    parser.add_argument("--report-file", type=Path, dest="report_file", help="Explainability report output path.")
    parser.add_argument("--nms-iou-threshold", type=float, dest="nms_iou_threshold", help="IOU threshold used for NMS stage.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint orchestrating all three pipeline stages."""

    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        preprocess_config = preprocess.prepare_config(args)
        symbolic_config = symbolic.prepare_config(args)
        evaluation_config = evaluation.prepare_config(args)
    except ConfigError as exc:  # pragma: no cover - CLI error handling
        parser.error(str(exc))

    preprocess.run(preprocess_config)
    symbolic.run(symbolic_config)
    evaluation.run(evaluation_config)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
