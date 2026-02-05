"""Project-wide configuration helpers."""
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
ASSETS_DIR = DATA_DIR / "assets"
FINAL_DIR = DATA_DIR / "final"


def ensure_dirs() -> None:
    """Create expected data directories if they do not exist."""
    for path in (CACHE_DIR, ASSETS_DIR, FINAL_DIR):
        path.mkdir(parents=True, exist_ok=True)
