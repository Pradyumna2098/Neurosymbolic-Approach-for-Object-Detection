"""Complete neurosymbolic pipeline orchestrating NMS, symbolic reasoning, and evaluation."""

from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Tuple

import torch
import torchvision
from pyswip import Prolog
from torchmetrics.detection.mean_ap import MeanAveragePrecision

from config_utils import (
    ConfigError,
    PathRequirement,
    apply_overrides,
    ensure_paths,
    expand_path,
    load_config_file,
)

DEFAULT_CONFIG_PATH = Path("configs/pipeline_kaggle.yaml")


# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the neurosymbolic pipeline stages.")
    parser.add_argument("--config", type=Path, help="Path to a YAML configuration file.")
    parser.add_argument("--raw-predictions-dir", dest="raw_predictions_dir", help="Directory of raw YOLO predictions.")
    parser.add_argument("--nms-predictions-dir", dest="nms_predictions_dir", help="Directory for NMS-filtered predictions.")
    parser.add_argument("--refined-predictions-dir", dest="refined_predictions_dir", help="Directory for refined predictions.")
    parser.add_argument("--ground-truth-dir", dest="ground_truth_dir", help="Directory containing YOLO-format labels.")
    parser.add_argument("--rules-file", dest="rules_file", help="Prolog rules file path.")
    parser.add_argument("--report-file", dest="report_file", help="Explainability report output path.")
    parser.add_argument("--nms-iou-threshold", dest="nms_iou_threshold", type=float, help="IOU threshold used for NMS stage.")
    return parser.parse_args()


def load_configuration(args: argparse.Namespace) -> Dict[str, Any]:
    config: Dict[str, Any] = {
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

    config_path = args.config
    if config_path is None and DEFAULT_CONFIG_PATH.is_file():
        config_path = DEFAULT_CONFIG_PATH

    if config_path is not None:
        config.update(load_config_file(config_path))

    overrides = {
        "raw_predictions_dir": args.raw_predictions_dir,
        "nms_predictions_dir": args.nms_predictions_dir,
        "refined_predictions_dir": args.refined_predictions_dir,
        "ground_truth_dir": args.ground_truth_dir,
        "rules_file": args.rules_file,
        "report_file": args.report_file,
        "nms_iou_threshold": args.nms_iou_threshold,
    }
    config = apply_overrides(config, overrides)

    required_keys = [
        "raw_predictions_dir",
        "nms_predictions_dir",
        "refined_predictions_dir",
        "ground_truth_dir",
        "rules_file",
        "report_file",
    ]
    for key in required_keys:
        if key not in config or config[key] is None:
            raise ConfigError(f"Configuration value '{key}' is required. Provide it via the YAML file or CLI flag.")

    config["raw_predictions_dir"] = expand_path(config["raw_predictions_dir"])
    config["nms_predictions_dir"] = expand_path(config["nms_predictions_dir"])
    config["refined_predictions_dir"] = expand_path(config["refined_predictions_dir"])
    config["ground_truth_dir"] = expand_path(config["ground_truth_dir"])
    config["rules_file"] = expand_path(config["rules_file"])
    config["report_file"] = expand_path(config["report_file"])

    ensure_paths(
        [
            PathRequirement(config["raw_predictions_dir"], "Raw predictions", expect_directory=True),
            PathRequirement(config["nms_predictions_dir"], "NMS predictions", expect_directory=True, create=True),
            PathRequirement(config["refined_predictions_dir"], "Refined predictions", expect_directory=True, create=True),
            PathRequirement(config["ground_truth_dir"], "Ground truth", expect_directory=True),
            PathRequirement(config["rules_file"], "Prolog rules", expect_directory=False),
            PathRequirement(config["report_file"].parent, "Report parent", expect_directory=True, create=True),
        ]
    )

    config["class_map"] = _normalise_class_map(config["class_map"])
    return config


def _normalise_class_map(class_map: Any) -> Dict[int, str]:
    if isinstance(class_map, Mapping):
        return {int(key): str(value) for key, value in class_map.items()}
    if isinstance(class_map, Iterable):
        return {idx: str(name) for idx, name in enumerate(class_map)}
    raise ConfigError("'class_map' must be defined as a mapping or list in the configuration file.")


# ---------------------------------------------------------------------------
# Stage 1 – Pre-processing with NMS
# ---------------------------------------------------------------------------

def parse_predictions_for_nms(predictions_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    predictions: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for pred_file in predictions_dir.iterdir():
        if pred_file.suffix.lower() != ".txt":
            continue
        image_name = pred_file.with_suffix(".png").name
        with pred_file.open("r", encoding="utf-8") as fh:
            for line in fh:
                parts = line.strip().split()
                if len(parts) != 6:
                    continue
                category_id, cx, cy, w, h, conf = map(float, parts)
                predictions[image_name].append(
                    {
                        "category_id": int(category_id),
                        "bbox_yolo": [cx, cy, w, h],
                        "bbox_voc": [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
                        "confidence": conf,
                    }
                )
    return predictions


def pre_filter_with_nms(objects_in_image: List[Dict[str, Any]], iou_threshold: float) -> List[Dict[str, Any]]:
    if not objects_in_image:
        return []

    objects_by_class: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
    for obj in objects_in_image:
        objects_by_class[obj["category_id"]].append(obj)

    filtered_objects: List[Dict[str, Any]] = []
    for objects in objects_by_class.values():
        if len(objects) < 2:
            filtered_objects.extend(objects)
            continue
        boxes = torch.tensor([obj["bbox_voc"] for obj in objects], dtype=torch.float32)
        scores = torch.tensor([obj["confidence"] for obj in objects], dtype=torch.float32)
        keep_indices = torchvision.ops.nms(boxes, scores, iou_threshold)
        filtered_objects.extend(objects[idx] for idx in keep_indices)
    return filtered_objects


def save_predictions_to_file(predictions_dict: Mapping[str, List[Dict[str, Any]]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for image_name, objects in predictions_dict.items():
        txt_file = output_dir / (Path(image_name).stem + ".txt")
        with txt_file.open("w", encoding="utf-8") as fh:
            for obj in objects:
                cat_id = obj["category_id"]
                conf = obj["confidence"]
                cx, cy, w, h = obj["bbox_yolo"]
                fh.write(f"{cat_id} {cx} {cy} {w} {h} {conf}\n")


def run_stage_one(config: Dict[str, Any]) -> None:
    print("--- Stage 1: Pre-processing with NMS ---")
    raw_predictions = parse_predictions_for_nms(config["raw_predictions_dir"])
    print(f"Loaded {len(raw_predictions)} raw prediction files.")

    nms_predictions: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
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


# ---------------------------------------------------------------------------
# Stage 2 – Symbolic reasoning and explainability
# ---------------------------------------------------------------------------

def get_center(bbox: Iterable[float]) -> Tuple[float, float]:
    x1, y1, x2, y2 = bbox
    return (x1 + x2) / 2, (y1 + y2) / 2


def get_distance(bbox_a: Iterable[float], bbox_b: Iterable[float]) -> float:
    center_a, center_b = get_center(bbox_a), get_center(bbox_b)
    return math.hypot(center_a[0] - center_b[0], center_a[1] - center_b[1])


def get_bbox_area(bbox: Iterable[float]) -> float:
    x1, y1, x2, y2 = bbox
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def get_intersection_area(bbox_a: Iterable[float], bbox_b: Iterable[float]) -> float:
    x1a, y1a, x2a, y2a = bbox_a
    x1b, y1b, x2b, y2b = bbox_b
    ix1, iy1 = max(x1a, x1b), max(y1a, y1b)
    ix2, iy2 = min(x2a, x2b), min(y2a, y2b)
    return max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)


def get_bbox_diag(bbox: Iterable[float]) -> float:
    x1, y1, x2, y2 = bbox
    return math.hypot(x2 - x1, y2 - y1)


def parse_predictions(predictions_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    predictions: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    if not predictions_dir.exists():
        return predictions
    for pred_file in predictions_dir.iterdir():
        if pred_file.suffix.lower() != ".txt":
            continue
        image_name = pred_file.with_suffix(".png").name
        with pred_file.open("r", encoding="utf-8") as fh:
            for idx, line in enumerate(fh):
                parts = line.strip().split()
                if len(parts) != 6:
                    continue
                category_id, center_x, center_y, width, height, confidence = map(float, parts)
                x_min, y_min = center_x - width / 2, center_y - height / 2
                x_max, y_max = center_x + width / 2, center_y + height / 2
                predictions[image_name].append(
                    {
                        "id": f"det_{idx}",
                        "category_id": int(category_id),
                        "bbox": [x_min, y_min, x_max, y_max],
                        "bbox_yolo": [center_x, center_y, width, height],
                        "confidence": confidence,
                    }
                )
    return predictions


def load_prolog_modifiers(prolog_engine: Prolog) -> Dict[Tuple[str, str], float]:
    modifier_map: Dict[Tuple[str, str], float] = {}
    for solution in prolog_engine.query("confidence_modifier(A, B, Weight)"):
        key = (solution["A"], solution["B"])
        modifier_map[key] = solution["Weight"]
    return modifier_map


def apply_symbolic_modifiers(
    objects_in_image: List[Dict[str, Any]], modifier_map: Mapping[Tuple[str, str], float], class_map: Mapping[int, str]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    modified_objects = {obj["id"]: dict(obj) for obj in objects_in_image}
    change_log: List[Dict[str, Any]] = []

    obj_ids = list(modified_objects.keys())
    for i in range(len(obj_ids)):
        for j in range(i + 1, len(obj_ids)):
            id_a, id_b = obj_ids[i], obj_ids[j]
            if id_a not in modified_objects or id_b not in modified_objects:
                continue
            obj_a, obj_b = modified_objects[id_a], modified_objects[id_b]
            class_a, class_b = class_map[obj_a["category_id"]], class_map[obj_b["category_id"]]
            original_conf_a, original_conf_b = obj_a["confidence"], obj_b["confidence"]
            weight = modifier_map.get((class_a, class_b)) or modifier_map.get((class_b, class_a))
            if weight is None:
                continue

            log_entry = None
            if weight > 1.0:
                avg_diag = (get_bbox_diag(obj_a["bbox"]) + get_bbox_diag(obj_b["bbox"])) / 2
                if get_distance(obj_a["bbox"], obj_b["bbox"]) < 2 * avg_diag:
                    obj_a["confidence"] = min(1.0, original_conf_a * weight)
                    obj_b["confidence"] = min(1.0, original_conf_b * weight)
                    log_entry = {
                        "action": "BOOST",
                        "rule_pair": f"{class_a}<->{class_b}",
                        "object_1": class_a,
                        "conf_1_before": f"{original_conf_a:.2f}",
                        "conf_1_after": f"{obj_a['confidence']:.2f}",
                        "object_2": class_b,
                        "conf_2_before": f"{original_conf_b:.2f}",
                        "conf_2_after": f"{obj_b['confidence']:.2f}",
                    }
            elif weight < 1.0:
                intersection = get_intersection_area(obj_a["bbox"], obj_b["bbox"])
                min_area = min(get_bbox_area(obj_a["bbox"]), get_bbox_area(obj_b["bbox"]))
                if min_area > 0 and intersection / min_area > 0.5:
                    suppressed_obj, kept_obj = (
                        (obj_b, obj_a) if obj_a["confidence"] > obj_b["confidence"] else (obj_a, obj_b)
                    )
                    original_conf = suppressed_obj["confidence"]
                    suppressed_obj["confidence"] *= weight
                    log_entry = {
                        "action": "PENALTY",
                        "rule_pair": f"{class_a}<->{class_b}",
                        "object_1": class_a,
                        "object_2": class_b,
                        "conf_1_before": f"{original_conf_a:.2f}",
                        "conf_1_after": f"{obj_a['confidence']:.2f}",
                        "conf_2_before": f"{original_conf_b:.2f}",
                        "conf_2_after": f"{obj_b['confidence']:.2f}",
                        "suppressed_object": class_map[suppressed_obj["category_id"]],
                        "conf_before": f"{original_conf:.2f}",
                        "conf_after": f"{suppressed_obj['confidence']:.2f}",
                        "kept_object": class_map[kept_obj["category_id"]],
                        "kept_object_conf": f"{kept_obj['confidence']:.2f}",
                    }
            if log_entry:
                change_log.append(log_entry)

    return list(modified_objects.values()), change_log


def run_stage_two(config: Dict[str, Any]) -> None:
    print("--- Stage 2: Symbolic Reasoning (CPU-only) ---")
    prolog = Prolog()
    prolog.consult(str(config["rules_file"]))
    modifier_map = load_prolog_modifiers(prolog)
    print(f"Loaded {len(modifier_map)} modifier rules.")

    nms_predictions = parse_predictions(config["nms_predictions_dir"])
    print(f"Loaded {len(nms_predictions)} NMS-filtered prediction files.")

    refined_predictions: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    full_report: List[Dict[str, Any]] = []

    for image_name, objects in nms_predictions.items():
        if not objects:
            continue
        refined_objs, report_entries = apply_symbolic_modifiers(objects, modifier_map, config["class_map"])
        if refined_objs:
            refined_predictions[image_name] = refined_objs
        for entry in report_entries:
            entry["image_name"] = image_name
            full_report.append(entry)

    save_predictions_to_file(refined_predictions, config["refined_predictions_dir"])
    print(f"Final refined predictions saved to '{config['refined_predictions_dir']}'.")

    if full_report:
        fieldnames = [
            "image_name",
            "action",
            "rule_pair",
            "object_1",
            "conf_1_before",
            "conf_1_after",
            "object_2",
            "conf_2_before",
            "conf_2_after",
            "suppressed_object",
            "kept_object",
            "kept_object_conf",
        ]
        with config["report_file"].open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(full_report)
        print(f"Explainability report saved to '{config['report_file']}'.")
    else:
        print("No symbolic reasoning actions were logged; explainability report not generated.")


# ---------------------------------------------------------------------------
# Stage 3 – Evaluation
# ---------------------------------------------------------------------------

def parse_ground_truths(label_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    ground_truths: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for label_file in label_dir.iterdir():
        if label_file.suffix.lower() != ".txt":
            continue
        image_name = label_file.with_suffix(".png").name
        with label_file.open("r", encoding="utf-8") as fh:
            for line in fh:
                parts = line.strip().split()
                if len(parts) != 5:
                    continue
                category_id = int(parts[0])
                center_x, center_y, width, height = map(float, parts[1:])
                x_min = center_x - width / 2
                y_min = center_y - height / 2
                x_max = center_x + width / 2
                y_max = center_y + height / 2
                ground_truths[image_name].append(
                    {
                        "category_id": category_id,
                        "bbox": [x_min, y_min, x_max, y_max],
                    }
                )
    return ground_truths


def calculate_map(predictions: Mapping[str, List[Dict[str, Any]]], ground_truths: Mapping[str, List[Dict[str, Any]]]) -> Dict[str, torch.Tensor]:
    metric = MeanAveragePrecision(box_format="xyxy")
    preds_for_metric, targets_for_metric = [], []

    for image_name, gt_objects in ground_truths.items():
        if image_name in predictions:
            preds_for_metric.append(
                {
                    "boxes": torch.tensor([p["bbox"] for p in predictions[image_name]], dtype=torch.float32),
                    "scores": torch.tensor([p["confidence"] for p in predictions[image_name]], dtype=torch.float32),
                    "labels": torch.tensor([p["category_id"] for p in predictions[image_name]], dtype=torch.int64),
                }
            )
        else:
            preds_for_metric.append(
                {
                    "boxes": torch.empty((0, 4), dtype=torch.float32),
                    "scores": torch.empty((0,), dtype=torch.float32),
                    "labels": torch.empty((0,), dtype=torch.int64),
                }
            )

        targets_for_metric.append(
            {
                "boxes": torch.tensor([gt["bbox"] for gt in gt_objects], dtype=torch.float32),
                "labels": torch.tensor([gt["category_id"] for gt in gt_objects], dtype=torch.int64),
            }
        )

    metric.update(preds_for_metric, targets_for_metric)
    return metric.compute()


def run_stage_three(config: Dict[str, Any]) -> None:
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


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()
    try:
        config = load_configuration(args)
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)

    run_stage_one(config)
    run_stage_two(config)
    run_stage_three(config)


if __name__ == "__main__":
    main()
