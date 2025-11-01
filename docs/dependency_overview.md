# Dependency Overview

The following table summarises the third-party dependencies required by the
command-line entry points in this repository. Standard-library modules and
intra-repository imports are omitted for brevity.

| Module | Third-party dependencies |
| --- | --- |
| `training.py` | `opencv-python`, `tqdm`, `ultralytics` |
| `nsai pipeline.py` | (none) |
| `src/sahi_yolo_prediction.py` | `torch`, `sahi` |
| `src/weighted_kg_sahi.py` | `matplotlib`, `networkx`, `torch`, `sahi` |

All of the packages listed above are pinned in `requirements/common.txt`, while
hardware-specific PyTorch builds are provided via `requirements.txt`
(defaulting to CPU wheels) and `requirements-kaggle.txt` (CUDA 12.1 wheels for
Kaggle runtimes).
