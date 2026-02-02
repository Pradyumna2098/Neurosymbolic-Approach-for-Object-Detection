"""Compatibility wrapper that delegates to the modular neurosymbolic pipeline."""

from __future__ import annotations

from pipeline.core.run_pipeline import main


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
