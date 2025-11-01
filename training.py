"""Training and inference utilities for the YOLOv11 OBB model."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

import cv2
from tqdm import tqdm
from ultralytics import YOLO

from config_utils import (
    ConfigError,
    PathRequirement,
    apply_overrides,
    ensure_paths,
    expand_path,
    load_config_file,
)

DEFAULT_CONFIG_PATH = Path("configs/training_kaggle.yaml")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train YOLOv11-OBB and generate inference artefacts.")
    parser.add_argument("--config", type=Path, help="Path to a YAML configuration file.")
    parser.add_argument("--data-yaml", dest="data_yaml", help="Path to the dataset YAML description.")
    parser.add_argument("--trained-model-name", dest="trained_model_name", help="Name of the Ultralytics run directory.")
    parser.add_argument("--model-name", dest="model_name", help="Initial weights to use when constructing the YOLO model.")
    parser.add_argument("--test-image-dir", dest="test_image_dir", help="Directory containing test images for inference.")
    parser.add_argument("--visualization-dir", dest="visualization_dir", help="Directory in which to save annotated images.")
    parser.add_argument("--model-weights-dir", dest="model_weights_dir", help="Directory containing trained model weights.")
    parser.add_argument("--zip-output-path", dest="zip_output_path", help="Location for the zipped inference artefacts.")
    parser.add_argument("--zip-source-dir", dest="zip_source_dir", help="Directory whose contents should be archived.")
    parser.add_argument("--epochs", type=int, help="Number of training epochs.")
    parser.add_argument("--imgsz", type=int, help="Inference and training image size.")
    parser.add_argument("--batch", type=int, help="Training batch size.")
    parser.add_argument("--workers", type=int, help="Number of dataloader workers.")
    parser.add_argument(
        "--conf-threshold", dest="conf_threshold", type=float, help="Confidence threshold used during inference.")
    return parser.parse_args()


def load_configuration(args: argparse.Namespace) -> Dict[str, Any]:
    config: Dict[str, Any] = {
        "model_name": "yolo11n-obb.pt",
        "trained_model_name": "dota_experiment_v11_1024",
        "imgsz": 1024,
        "epochs": 50,
        "batch": 8,
        "workers": 0,
        "conf_threshold": 0.3,
    }

    config_path = args.config
    if config_path is None and DEFAULT_CONFIG_PATH.is_file():
        config_path = DEFAULT_CONFIG_PATH

    if config_path is not None:
        config.update(load_config_file(config_path))

    overrides = {
        "data_yaml": args.data_yaml,
        "model_name": args.model_name,
        "trained_model_name": args.trained_model_name,
        "test_image_dir": args.test_image_dir,
        "visualization_dir": args.visualization_dir,
        "model_weights_dir": args.model_weights_dir,
        "zip_output_path": args.zip_output_path,
        "zip_source_dir": args.zip_source_dir,
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "batch": args.batch,
        "workers": args.workers,
        "conf_threshold": args.conf_threshold,
    }
    config = apply_overrides(config, overrides)

    for key in ("data_yaml", "test_image_dir", "visualization_dir", "model_weights_dir", "zip_output_path"):
        if key not in config or config[key] is None:
            raise ConfigError(f"Configuration value '{key}' is required. Provide it via the YAML file or CLI flag.")

    config["data_yaml"] = expand_path(config["data_yaml"])
    config["test_image_dir"] = expand_path(config["test_image_dir"])
    config["visualization_dir"] = expand_path(config["visualization_dir"])
    config["model_weights_dir"] = expand_path(config["model_weights_dir"])
    config["zip_output_path"] = expand_path(config["zip_output_path"])
    if config.get("zip_source_dir") is None:
        config["zip_source_dir"] = config["visualization_dir"]
    config["zip_source_dir"] = expand_path(config["zip_source_dir"])

    ensure_paths(
        [
            PathRequirement(config["data_yaml"], "Dataset YAML", expect_directory=False),
            PathRequirement(config["test_image_dir"], "Test image", expect_directory=True),
            PathRequirement(config["visualization_dir"], "Visualization", expect_directory=True, create=True),
            PathRequirement(config["model_weights_dir"], "Model weights", expect_directory=True, create=True),
            PathRequirement(config["zip_output_path"].parent, "Zip output parent", expect_directory=True, create=True),
            PathRequirement(config["zip_source_dir"], "Zip source", expect_directory=True),
        ]
    )

    return config


def train_yolov11_obb(config: Dict[str, Any]) -> YOLO:
    model = YOLO(config["model_name"])
    model.train(
        data=str(config["data_yaml"]),
        epochs=int(config["epochs"]),
        imgsz=int(config["imgsz"]),
        batch=int(config["batch"]),
        workers=int(config["workers"]),
        name=str(config["trained_model_name"]),
        save=True,
        save_txt=True,
    )
    return model


def run_inference(model_path: Path, config: Dict[str, Any]) -> Path:
    model = YOLO(str(model_path))
    output_dir = config["visualization_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    all_predictions = {}

    for img_name in tqdm(sorted(p.name for p in config["test_image_dir"].iterdir()), desc="Running inference"):
        if not img_name.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        img_path = config["test_image_dir"] / img_name
        results = model(str(img_path), imgsz=int(config["imgsz"]), conf=float(config["conf_threshold"]))[0]

        predictions = []
        result_image = cv2.imread(str(img_path))

        if results and results.boxes:
            for box in results.boxes:
                xyxy = box.xyxy[0].cpu().numpy().tolist()
                conf = float(box.conf[0].item())
                cls_id = int(box.cls[0].item())
                label = model.names[cls_id]

                predictions.append(
                    {
                        "class": label,
                        "confidence": round(conf, 4),
                        "bbox": [round(x, 2) for x in xyxy],
                    }
                )

                x1, y1, x2, y2 = map(int, xyxy)
                cv2.rectangle(result_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    result_image,
                    f"{label} {conf:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 0),
                    2,
                )

        out_path = output_dir / img_name
        cv2.imwrite(str(out_path), result_image)

        all_predictions[img_name] = predictions

    json_path = output_dir / "yolo_predictions.json"
    with json_path.open("w", encoding="utf-8") as fh:
        json.dump(all_predictions, fh, indent=2)

    return json_path


def package_results(config: Dict[str, Any]) -> Path:
    zip_path = config["zip_output_path"]
    subprocess.run(["zip", "-r", str(zip_path), str(config["zip_source_dir"])], check=False)
    return zip_path


def main() -> None:
    args = parse_args()
    try:
        config = load_configuration(args)
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Starting YOLOv11-OBB Training...")
    trained_model = train_yolov11_obb(config)

    best_model_path = None
    if hasattr(trained_model, "trainer") and getattr(trained_model.trainer, "best", None):
        best_model_path = Path(trained_model.trainer.best)
    else:
        candidate = config["model_weights_dir"] / "best.pt"
        if candidate.is_file():
            best_model_path = candidate

    if best_model_path is None:
        print(
            "Unable to determine the best model weights automatically. Please check your training run.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("Running Inference on Test Images...")
    json_output = run_inference(best_model_path, config)

    print("Zipping Results for Download...")
    zip_result_path = package_results(config)

    print(f"Visual results saved to: {config['visualization_dir']}")
    print(f"JSON file saved to: {json_output}")
    print(f"Download zipped results from: {zip_result_path}")


if __name__ == "__main__":
    main()
