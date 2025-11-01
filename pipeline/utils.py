"""Utility helpers shared across the neurosymbolic pipeline stages."""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Mapping, MutableMapping, Tuple

import torch
import torchvision
from torchmetrics.detection.mean_ap import MeanAveragePrecision

if TYPE_CHECKING:  # pragma: no cover - imported only for type checking
    from pyswip import Prolog


PredictionDict = Dict[str, List[Dict[str, Any]]]


def parse_predictions_for_nms(predictions_dir: Path) -> PredictionDict:
    """Load YOLO-format predictions and derive additional metadata for NMS."""

    predictions: PredictionDict = defaultdict(list)
    for pred_file in predictions_dir.iterdir():
        if pred_file.suffix.lower() != ".txt":
            continue
        image_name = pred_file.with_suffix(".png").name
        with pred_file.open("r", encoding="utf-8") as handle:
            for line in handle:
                parts = line.strip().split()
                if len(parts) != 6:
                    continue
                category_id, cx, cy, width, height, confidence = map(float, parts)
                predictions[image_name].append(
                    {
                        "category_id": int(category_id),
                        "bbox_yolo": [cx, cy, width, height],
                        "bbox_voc": [cx - width / 2, cy - height / 2, cx + width / 2, cy + height / 2],
                        "confidence": confidence,
                    }
                )
    return predictions


def pre_filter_with_nms(objects_in_image: List[Dict[str, Any]], iou_threshold: float) -> List[Dict[str, Any]]:
    """Apply torchvision NMS filtering to objects belonging to the same class."""

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
        keep_indices = torchvision.ops.nms(boxes, scores, float(iou_threshold))
        filtered_objects.extend(objects[idx] for idx in keep_indices)
    return filtered_objects


def save_predictions_to_file(predictions_dict: Mapping[str, List[Dict[str, Any]]], output_dir: Path) -> None:
    """Persist predictions to YOLO text files compatible with the rest of the pipeline."""

    output_dir.mkdir(parents=True, exist_ok=True)
    for image_name, objects in predictions_dict.items():
        txt_file = output_dir / (Path(image_name).stem + ".txt")
        with txt_file.open("w", encoding="utf-8") as handle:
            for obj in objects:
                cx, cy, width, height = obj["bbox_yolo"]
                handle.write(
                    f"{obj['category_id']} {cx} {cy} {width} {height} {obj['confidence']}\n"
                )


def get_center(bbox: Iterable[float]) -> Tuple[float, float]:
    """Return the centre coordinates of a bounding box."""

    x1, y1, x2, y2 = bbox
    return (x1 + x2) / 2, (y1 + y2) / 2


def get_distance(bbox_a: Iterable[float], bbox_b: Iterable[float]) -> float:
    """Compute the Euclidean distance between the centres of two boxes."""

    center_a, center_b = get_center(bbox_a), get_center(bbox_b)
    return math.hypot(center_a[0] - center_b[0], center_a[1] - center_b[1])


def get_bbox_area(bbox: Iterable[float]) -> float:
    """Calculate the area of a bounding box."""

    x1, y1, x2, y2 = bbox
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def get_intersection_area(bbox_a: Iterable[float], bbox_b: Iterable[float]) -> float:
    """Calculate the area of intersection between two bounding boxes."""

    x1a, y1a, x2a, y2a = bbox_a
    x1b, y1b, x2b, y2b = bbox_b
    ix1, iy1 = max(x1a, x1b), max(y1a, y1b)
    ix2, iy2 = min(x2a, x2b), min(y2a, y2b)
    return max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)


def get_bbox_diag(bbox: Iterable[float]) -> float:
    """Return the diagonal length of a bounding box."""

    x1, y1, x2, y2 = bbox
    return math.hypot(x2 - x1, y2 - y1)


def parse_predictions(predictions_dir: Path) -> PredictionDict:
    """Read YOLO prediction files and normalise them into a structured mapping."""

    predictions: PredictionDict = defaultdict(list)
    if not predictions_dir.exists():
        return predictions
    for pred_file in predictions_dir.iterdir():
        if pred_file.suffix.lower() != ".txt":
            continue
        image_name = pred_file.with_suffix(".png").name
        with pred_file.open("r", encoding="utf-8") as handle:
            for idx, line in enumerate(handle):
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


def load_prolog_modifiers(prolog_engine: "Prolog") -> Dict[Tuple[str, str], float]:
    """Extract symbolic modifier weights from a Prolog engine."""

    modifier_map: Dict[Tuple[str, str], float] = {}
    for solution in prolog_engine.query("confidence_modifier(A, B, Weight)"):
        modifier_map[(solution["A"], solution["B"])] = solution["Weight"]
    return modifier_map


def apply_symbolic_modifiers(
    objects_in_image: List[Dict[str, Any]],
    modifier_map: Mapping[Tuple[str, str], float],
    class_map: Mapping[int, str],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Apply symbolic modifiers to object confidences and generate explainability logs."""

    modified_objects: Dict[str, MutableMapping[str, Any]] = {
        obj["id"]: dict(obj) for obj in objects_in_image
    }
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


def write_explainability_report(report: List[Dict[str, Any]], report_file: Path) -> None:
    """Persist the explainability change log to disk."""

    if not report:
        return

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
    with report_file.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report)


def parse_ground_truths(label_dir: Path) -> PredictionDict:
    """Load YOLO-format ground-truth annotations and convert to VOC coordinates."""

    ground_truths: PredictionDict = defaultdict(list)
    for label_file in label_dir.iterdir():
        if label_file.suffix.lower() != ".txt":
            continue
        image_name = label_file.with_suffix(".png").name
        with label_file.open("r", encoding="utf-8") as handle:
            for line in handle:
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


def calculate_map(
    predictions: Mapping[str, List[Dict[str, Any]]],
    ground_truths: Mapping[str, List[Dict[str, Any]]],
) -> Dict[str, torch.Tensor]:
    """Compute mean average precision statistics for a set of predictions."""

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
