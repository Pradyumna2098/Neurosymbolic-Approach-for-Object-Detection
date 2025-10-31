# Neurosymbolic-Approach-for-Object-Detection

## Neural Conception + Symbolic Modules

This repository contains two main components used in the project:

- `Neural Conception Module/Code_files/`: training and inference scripts for the neural model (YOLO/Sahi code)
- `Neural Conception Module/Training_results/`: local training outputs (ignored by default)
- `Symbolic Module/Code_files/`: symbolic pipeline, Prolog facts and rules

Notes
- Large files and training results are excluded by `.gitignore`. If you want to share a trained model, use GitHub Releases or cloud storage.
- `*.pt` model files should be tracked via Git LFS if you choose to store any in the repo.

Quick start
1. (Optional) Create and activate a virtualenv

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. Train or run models (examples)

```powershell
# Train (example — adjust paths/args as needed)
python "Neural Conception Module/Code_files/training.py"

# Run symbolic pipeline
python "Symbolic Module/Code_files/nsai pipeline.py"
```

Repository housekeeping
- This repo intentionally ignores `Neural Conception Module/Training_results/` to avoid huge commits.
- If you want to publish models, enable Git LFS and track `*.pt` before committing them.

Replace the sections above with project-specific usage and authorship as needed.
