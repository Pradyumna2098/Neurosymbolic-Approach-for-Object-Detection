"""Build a knowledge graph from SAHI predictions with configurable paths."""

from __future__ import annotations

import argparse
import logging
import math
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence, Tuple

import matplotlib.pyplot as plt
import networkx as nx
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

LOGGER = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path("configs/knowledge_graph_kaggle.yaml")

ALLOWED_LOCATED_ON = {("large_vehicle", "Bridge")}
ALLOWED_LOCATED_NEAR = {
    ("ship", "harbor"),
    ("small_vehicle", "small_vehicle"),
    ("helicopter", "plane"),
    ("small_vehicle", "roundabout"),
    ("roundabout", "small_vehicle"),
    ("storage_tank", "harbor"),
    ("small_vehicle", "tennis_court"),
    ("small_vehicle", "basketball_court"),
    ("small_vehicle", "soccer_ball_field"),
    ("small_vehicle", "Ground_Track_Field"),
    ("small_vehicle", "baseball_diamond"),
}
ALLOWED_ADJACENT_TO = {
    ("tennis_court", "basketball_court"),
    ("baseball_diamond", "soccer_ball_field"),
    ("swimming_pool", "Ground_Track_Field"),
    ("large_vehicle", "small_vehicle"),
    ("plane", "plane"),
}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a weighted knowledge graph from SAHI predictions.",
        epilog=(
            "Example:\n"
            "  python -m src.weighted_kg_sahi --config configs/knowledge_graph.yaml \\\n"
            "      --model-path weights/best.pt --knowledge-graph-dir outputs/kg"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--config", type=Path, help="Path to a YAML configuration file.")
    parser.add_argument("--model-path", dest="model_path", help="Path to trained YOLO weights.")
    parser.add_argument("--knowledge-graph-dir", dest="knowledge_graph_dir", help="Directory for KG artefacts.")
    parser.add_argument("--data-split", dest="data_splits", action="append", help="Mapping of split=name:path entries.")
    parser.add_argument("--confidence-threshold", dest="confidence_threshold", type=float, help="Model confidence threshold.")
    parser.add_argument("--slice-height", dest="slice_height", type=int, help="Slice height for SAHI.")
    parser.add_argument("--slice-width", dest="slice_width", type=int, help="Slice width for SAHI.")
    parser.add_argument("--overlap-height", dest="overlap_height", type=float, help="Slice overlap height ratio.")
    parser.add_argument("--overlap-width", dest="overlap_width", type=float, help="Slice overlap width ratio.")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        help="Python logging level to use for console output.",
    )
    return parser.parse_args(argv)


def configure_logging(log_level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def load_configuration(args: argparse.Namespace) -> Dict[str, Any]:
    config: Dict[str, Any] = {
        "confidence_threshold": 0.3,
        "slice_height": 1024,
        "slice_width": 1024,
        "overlap_height": 0.2,
        "overlap_width": 0.2,
        "knowledge_graph_dir": Path("knowledge_graph"),
        "facts_filename": "facts.pl",
        "graph_filename": "knowledge_graph_visuals.png",
    }

    config_path = args.config
    if config_path is None and DEFAULT_CONFIG_PATH.is_file():
        config_path = DEFAULT_CONFIG_PATH

    if config_path is not None:
        config.update(load_config_file(config_path))

    overrides = {
        "model_path": args.model_path,
        "knowledge_graph_dir": args.knowledge_graph_dir,
        "confidence_threshold": args.confidence_threshold,
        "slice_height": args.slice_height,
        "slice_width": args.slice_width,
        "overlap_height": args.overlap_height,
        "overlap_width": args.overlap_width,
    }
    config = apply_overrides(config, overrides)

    if args.data_splits:
        split_mapping = {}
        for item in args.data_splits:
            if "=" not in item:
                raise ConfigError("Data split overrides must be in 'name=path' format.")
            name, value = item.split("=", 1)
            split_mapping[name.strip()] = value.strip()
        config["data_splits"] = split_mapping

    for key in ("model_path", "knowledge_graph_dir"):
        if key not in config or config[key] is None:
            raise ConfigError(f"Configuration value '{key}' is required. Provide it via the YAML file or CLI flag.")

    if "data_splits" not in config or not config["data_splits"]:
        raise ConfigError("At least one data split must be defined in the configuration.")

    config["model_path"] = expand_path(config["model_path"])
    config["knowledge_graph_dir"] = expand_path(config["knowledge_graph_dir"])
    config["data_splits"] = {name: expand_path(path) for name, path in config["data_splits"].items()}

    ensure_paths(
        [
            PathRequirement(config["model_path"], "Model weights", expect_directory=False),
            PathRequirement(config["knowledge_graph_dir"], "Knowledge graph", expect_directory=True, create=True),
        ]
    )

    ensure_paths(
        [
            PathRequirement(path, f"Dataset split '{name}'", expect_directory=True)
            for name, path in config["data_splits"].items()
        ]
    )

    facts_filename = config.get("facts_filename", "facts.pl")
    graph_filename = config.get("graph_filename", "knowledge_graph_visuals.png")
    config["facts_path"] = config["knowledge_graph_dir"] / facts_filename
    config["graph_image_path"] = config["knowledge_graph_dir"] / graph_filename

    return config


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


def load_detection_model(config: Mapping[str, Any]) -> AutoDetectionModel:
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    LOGGER.info("Using device: %s", device)
    try:
        detection_model = AutoDetectionModel.from_pretrained(
            model_type="yolov8",
            model_path=str(config["model_path"]),
            confidence_threshold=float(config["confidence_threshold"]),
            device=device,
        )
    except Exception as exc:  # pragma: no cover - defensive programming
        raise RuntimeError(f"Error loading model: {exc}") from exc
    LOGGER.info("Loaded YOLO model from %s", config["model_path"])
    return detection_model


def add_relation(relation_counts: Dict[Tuple[str, str, str], int], rel: str, obj_a_class: str, obj_b_class: str) -> None:
    key = (rel, obj_a_class, obj_b_class)
    relation_counts[key] = relation_counts.get(key, 0) + 1


def process_dataset(
    detection_model: AutoDetectionModel,
    data_splits: Mapping[str, Path],
    config: Mapping[str, Any],
) -> Dict[Tuple[str, str, str], int]:
    relation_counts: Dict[Tuple[str, str, str], int] = {}
    for split, img_dir in data_splits.items():
        image_files = [p for p in sorted(img_dir.iterdir()) if p.suffix.lower() in {".jpg", ".jpeg", ".png"}]
        if not image_files:
            LOGGER.warning("Directory for split '%s' does not contain any images: %s", split, img_dir)
            continue
        LOGGER.info("Processing split %s with %d images", split, len(image_files))
        for index, image_path in enumerate(image_files, start=1):
            LOGGER.debug("Processing image %d/%d (%s)", index, len(image_files), image_path.name)
            try:
                result = get_sliced_prediction(
                    str(image_path),
                    detection_model,
                    slice_height=int(config["slice_height"]),
                    slice_width=int(config["slice_width"]),
                    overlap_height_ratio=float(config["overlap_height"]),
                    overlap_width_ratio=float(config["overlap_width"]),
                    verbose=0,
                )
            except Exception as exc:  # pragma: no cover - defensive programming
                LOGGER.exception("Error processing image %s: %s", image_path.name, exc)
                continue

            objects = [(o.category.name, o.score.value, o.bbox.to_voc_bbox()) for o in result.object_prediction_list]
            for i in range(len(objects)):
                c1, _, b1 = objects[i]
                for j in range(i + 1, len(objects)):
                    c2, _, b2 = objects[j]
                    sorted_pair = tuple(sorted((c1, c2)))
                    add_relation(relation_counts, "cooccurs", sorted_pair[0], sorted_pair[1])

                    for subject, object_, sub_bbox, obj_bbox in ((c1, c2, b1, b2), (c2, c1, b2, b1)):
                        pair = (subject, object_)
                        if pair in ALLOWED_LOCATED_ON and get_intersection_area(sub_bbox, obj_bbox) / get_bbox_area(sub_bbox) >= 0.5:
                            add_relation(relation_counts, "located_on", subject, object_)
                        if (
                            pair in ALLOWED_LOCATED_NEAR
                            and get_distance(sub_bbox, obj_bbox) < 2 * ((get_bbox_diag(sub_bbox) + get_bbox_diag(obj_bbox)) / 2)
                        ):
                            add_relation(relation_counts, "located_near", subject, object_)
                        if pair in ALLOWED_ADJACENT_TO:
                            eps = 0.1 * get_bbox_diag(sub_bbox)
                            x1a, y1a, x2a, y2a = sub_bbox
                            x1b, y1b, x2b, y2b = obj_bbox
                            if (
                                abs(x2a - x1b) <= eps
                                or abs(x1a - x2b) <= eps
                                or abs(y2a - y1b) <= eps
                                or abs(y1a - y2b) <= eps
                            ):
                                add_relation(relation_counts, "adjacent_to", subject, object_)
        LOGGER.debug("Finished processing split %s", split)
    return relation_counts


def write_prolog_facts(relation_counts: Mapping[Tuple[str, str, str], int], facts_path: Path) -> None:
    with facts_path.open("w", encoding="utf-8") as fh:
        fh.write("% fact(Relation, Subject, Object, Count).\n")
        for (rel, subj, obj), count in sorted(relation_counts.items(), key=lambda item: item[0]):
            fh.write(f"fact('{rel}', '{subj}', '{obj}', {count}).\n")


def visualise_graph(relation_counts: Mapping[Tuple[str, str, str], int], graph_path: Path) -> None:
    relation_types = ["cooccurs", "located_near", "adjacent_to", "located_on"]
    relation_colors = {
        "cooccurs": "#d62728",
        "located_near": "#2ca02c",
        "adjacent_to": "#1f77b4",
        "located_on": "#9467bd",
    }
    thresholds = {
        "cooccurs": 12000,
        "located_near": 20,
        "adjacent_to": 75,
        "located_on": 0,
    }

    G = nx.DiGraph()
    for (rel, subj, obj), count in relation_counts.items():
        G.add_edge(subj, obj, relation=rel, weight=count)

    if not relation_counts:
        LOGGER.warning("No relations were generated; skipping visualisation.")
        return

    fig, axes = plt.subplots(len(relation_types), 1, figsize=(25, 20 * len(relation_types)))
    if len(relation_types) == 1:
        axes = [axes]

    for ax, rel_type in zip(axes, relation_types):
        min_weight = thresholds.get(rel_type, 0)
        subG = nx.DiGraph(
            [(u, v, d) for u, v, d in G.edges(data=True) if d.get("relation") == rel_type and d.get("weight", 0) > min_weight]
        )

        ax.set_title(f"Relation: {rel_type.replace('_', ' ').title()} (Count > {min_weight:,})", fontsize=24, fontweight="bold")
        if not subG.nodes:
            ax.text(0.5, 0.5, "No relations found for this threshold", ha="center", va="center", fontsize=18)
            ax.axis("off")
            continue

        pos = nx.spring_layout(subG, k=6.0 / math.sqrt(len(subG.nodes) + 0.01), seed=42, iterations=100)
        node_sizes = [dict(subG.degree()).get(n, 1) * 1500 + 800 for n in subG.nodes]

        edge_weights = [d["weight"] for _, _, d in subG.edges(data=True)]
        max_weight = max(edge_weights) if edge_weights else 1
        edge_widths = [((w / max_weight) * 8) + 1.5 for w in edge_weights]

        nx.draw_networkx_nodes(subG, pos, node_color="#a0cbe2", node_size=node_sizes, ax=ax, edgecolors="black")
        nx.draw_networkx_labels(subG, pos, font_size=12, font_weight="bold", ax=ax)
        nx.draw_networkx_edges(
            subG,
            pos,
            edge_color=relation_colors.get(rel_type, "#1f77b4"),
            width=edge_widths,
            arrows=True,
            arrowstyle="->",
            arrowsize=25,
            ax=ax,
            node_size=node_sizes,
            connectionstyle="arc3,rad=0.1",
        )
        nx.draw_networkx_edge_labels(
            subG,
            pos,
            edge_labels={(u, v): f"{d['weight']:,}" for u, v, d in subG.edges(data=True)},
            font_size=11,
            font_color="black",
            ax=ax,
        )
        ax.axis("off")

    plt.tight_layout(pad=5.0)
    plt.savefig(graph_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    LOGGER.info("Knowledge graph visualisation saved to %s", graph_path)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    configure_logging(args.log_level)

    try:
        config = load_configuration(args)
        detection_model = load_detection_model(config)
        relation_counts = process_dataset(detection_model, config["data_splits"], config)
        if not relation_counts:
            LOGGER.warning("No relations were extracted from the provided datasets.")
        write_prolog_facts(relation_counts, config["facts_path"])
        LOGGER.info("Prolog facts written to %s", config["facts_path"])
        visualise_graph(relation_counts, config["graph_image_path"])
    except ConfigError as exc:
        LOGGER.error("Configuration error: %s", exc)
        return 1
    except RuntimeError as exc:
        LOGGER.error(str(exc))
        return 1
    except Exception:  # pragma: no cover - defensive programming
        LOGGER.exception("Unexpected error while generating knowledge graph")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
