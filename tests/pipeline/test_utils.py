"""Unit tests for key neurosymbolic pipeline helpers."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List

import torch

sys.path.append(str(Path(__file__).resolve().parents[1]))

from pipeline.utils import apply_symbolic_modifiers, pre_filter_with_nms


def test_pre_filter_with_nms_removes_overlapping_boxes() -> None:
    """NMS keeps only the highest-confidence box for heavily overlapping detections."""

    objects = [
        {
            "category_id": 0,
            "bbox_voc": [0.0, 0.0, 2.0, 2.0],
            "bbox_yolo": [1.0, 1.0, 2.0, 2.0],
            "confidence": 0.9,
        },
        {
            "category_id": 0,
            "bbox_voc": [0.2, 0.2, 2.2, 2.2],
            "bbox_yolo": [1.2, 1.2, 2.0, 2.0],
            "confidence": 0.6,
        },
    ]

    filtered = pre_filter_with_nms(objects, iou_threshold=0.5)
    assert len(filtered) == 1
    assert filtered[0]["confidence"] == 0.9


def test_apply_symbolic_modifiers_boosts_close_detections() -> None:
    """Boosting rules raise the confidence of nearby objects."""

    objects = [
        {
            "id": "a",
            "category_id": 0,
            "bbox": [0.0, 0.0, 1.0, 1.0],
            "confidence": 0.5,
        },
        {
            "id": "b",
            "category_id": 1,
            "bbox": [0.5, 0.5, 1.5, 1.5],
            "confidence": 0.4,
        },
    ]
    modifiers: Dict[tuple[str, str], float] = {("tree", "car"): 1.5}
    class_map = {0: "tree", 1: "car"}

    refined, report = apply_symbolic_modifiers(objects, modifiers, class_map)

    assert torch.isclose(torch.tensor(refined[0]["confidence"]), torch.tensor(0.75))
    assert torch.isclose(torch.tensor(refined[1]["confidence"]), torch.tensor(0.6))
    assert report and report[0]["action"] == "BOOST"


def test_apply_symbolic_modifiers_penalises_overlapping_objects() -> None:
    """Penalty rules suppress the lower-confidence object when boxes overlap heavily."""

    objects: List[Dict[str, object]] = [
        {
            "id": "a",
            "category_id": 0,
            "bbox": [0.0, 0.0, 2.0, 2.0],
            "confidence": 0.8,
        },
        {
            "id": "b",
            "category_id": 1,
            "bbox": [0.2, 0.2, 2.2, 2.2],
            "confidence": 0.7,
        },
    ]
    modifiers: Dict[tuple[str, str], float] = {("tree", "truck"): 0.5}
    class_map = {0: "tree", 1: "truck"}

    refined, report = apply_symbolic_modifiers(objects, modifiers, class_map)

    suppressed = next(obj for obj in refined if obj["id"] == "b")
    assert torch.isclose(torch.tensor(suppressed["confidence"]), torch.tensor(0.35))
    assert report and report[0]["action"] == "PENALTY"
