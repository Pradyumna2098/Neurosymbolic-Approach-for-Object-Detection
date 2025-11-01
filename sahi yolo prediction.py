"""Generate sliced SAHI predictions using a configurable YOLO model."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import torch
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction

from config_utils import (
    ConfigError,
    PathRequirement,
    apply_overrides,
    ensure_paths,
    expand_path,
    load_config_file,
)

DEFAULT_CONFIG_PATH = Path("configs/prediction_kaggle.yaml")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SAHI sliced predictions with YOLO.")
    parser.add_argument("--config", type=Path, help="Path to a YAML configuration file.")
    parser.add_argument("--model-path", dest="model_path", help="Path to the trained YOLO weights.")
    parser.add_argument("--test-images-dir", dest="test_images_dir", help="Directory of images to predict on.")
    parser.add_argument("--output-predictions-dir", dest="output_predictions_dir", help="Directory to write predictions.")
    parser.add_argument("--confidence-threshold", dest="confidence_threshold", type=float, help="YOLO confidence threshold.")
    parser.add_argument("--slice-height", dest="slice_height", type=int, help="Slice height for SAHI.")
    parser.add_argument("--slice-width", dest="slice_width", type=int, help="Slice width for SAHI.")
    parser.add_argument("--overlap-height", dest="overlap_height", type=float, help="Slice overlap height ratio.")
    parser.add_argument("--overlap-width", dest="overlap_width", type=float, help="Slice overlap width ratio.")
    return parser.parse_args()


def load_configuration(args: argparse.Namespace) -> dict:
    config = {
        "confidence_threshold": 0.01,
        "slice_height": 1024,
        "slice_width": 1024,
        "overlap_height": 0.2,
        "overlap_width": 0.2,
        "postprocess_type": "GREEDYNMM",
        "postprocess_match_metric": "IOU",
        "postprocess_match_threshold": 0.5,
    }

    config_path = args.config
    if config_path is None and DEFAULT_CONFIG_PATH.is_file():
        config_path = DEFAULT_CONFIG_PATH

    if config_path is not None:
        config.update(load_config_file(config_path))

    overrides = {
        "model_path": args.model_path,
        "test_images_dir": args.test_images_dir,
        "output_predictions_dir": args.output_predictions_dir,
        "confidence_threshold": args.confidence_threshold,
        "slice_height": args.slice_height,
        "slice_width": args.slice_width,
        "overlap_height": args.overlap_height,
        "overlap_width": args.overlap_width,
    }
    config = apply_overrides(config, overrides)

    for key in ("model_path", "test_images_dir", "output_predictions_dir"):
        if key not in config or config[key] is None:
            raise ConfigError(f"Configuration value '{key}' is required. Provide it via the YAML file or CLI flag.")

    config["model_path"] = expand_path(config["model_path"])
    config["test_images_dir"] = expand_path(config["test_images_dir"])
    config["output_predictions_dir"] = expand_path(config["output_predictions_dir"])

    ensure_paths(
        [
            PathRequirement(config["model_path"], "Model weights", expect_directory=False),
            PathRequirement(config["test_images_dir"], "Test image", expect_directory=True),
            PathRequirement(config["output_predictions_dir"], "Output predictions", expect_directory=True, create=True),
        ]
    )

    return config


def main() -> None:
    args = parse_args()
    try:
        config = load_configuration(args)
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    try:
        detection_model = AutoDetectionModel.from_pretrained(
            model_type="yolov8",
            model_path=str(config["model_path"]),
            confidence_threshold=float(config["confidence_threshold"]),
            device=device,
        )
        print("YOLO model loaded successfully.")
    except Exception as exc:  # pragma: no cover - defensive programming
        print(f"ERROR loading model: {exc}", file=sys.stderr)
        sys.exit(1)

    image_files = [p for p in sorted(config["test_images_dir"].iterdir()) if p.suffix.lower() in {".jpg", ".jpeg", ".png"}]
    if not image_files:
        print(
            f"No images found in '{config['test_images_dir']}'. Ensure the directory contains .jpg/.jpeg/.png files.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("🚀 Starting prediction generation...")
    print(f"   All prediction files will be saved to: {config['output_predictions_dir']}")

    for index, image_path in enumerate(image_files, start=1):
        print(f"  Processing image {index}/{len(image_files)}: {image_path.name}", end="\r")
        output_filepath = config["output_predictions_dir"] / (image_path.stem + ".txt")

        try:
            result = get_sliced_prediction(
                str(image_path),
                detection_model,
                slice_height=int(config["slice_height"]),
                slice_width=int(config["slice_width"]),
                overlap_height_ratio=float(config["overlap_height"]),
                overlap_width_ratio=float(config["overlap_width"]),
                postprocess_type=config.get("postprocess_type", "GREEDYNMM"),
                postprocess_match_metric=config.get("postprocess_match_metric", "IOU"),
                postprocess_match_threshold=float(config.get("postprocess_match_threshold", 0.5)),
                verbose=0,
            )
        except Exception as exc:  # pragma: no cover - defensive programming
            print(f"\nError processing image {image_path.name}: {exc}", file=sys.stderr)
            continue

        img_h, img_w = result.image_height, result.image_width
        with output_filepath.open("w", encoding="utf-8") as output_file:
            for pred in result.object_prediction_list:
                x1, y1, x2, y2 = pred.bbox.to_voc_bbox()
                dw, dh = 1.0 / img_w, 1.0 / img_h
                x_center = (x1 + x2) / 2.0
                y_center = (y1 + y2) / 2.0
                width = x2 - x1
                height = y2 - y1

                x_center_norm = x_center * dw
                y_center_norm = y_center * dh
                width_norm = width * dw
                height_norm = height * dh

                output_file.write(
                    f"{pred.category.id} {x_center_norm:.6f} {y_center_norm:.6f} {width_norm:.6f} {height_norm:.6f} {pred.score.value:.6f}\n"
                )

    print("\nPrediction generation complete. All files saved to the output directory.")


if __name__ == "__main__":
    main()
