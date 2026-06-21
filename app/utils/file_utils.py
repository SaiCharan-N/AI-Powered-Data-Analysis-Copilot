import re
from pathlib import Path


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_stem(filename: str) -> str:
    stem = Path(filename).stem.lower()
    safe = re.sub(r"[^a-z0-9_]+", "_", stem).strip("_")
    return safe or "dataset"
