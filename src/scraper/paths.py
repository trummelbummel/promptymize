from __future__ import annotations

import re
from pathlib import Path

_FOLDER_SAFE_RE = re.compile(r"[^a-zA-Z0-9_-]+")


def sanitize_folder_name(folder_name: str) -> str:
    """Return a filesystem-safe folder name based on ``folder_name``."""

    cleaned = _FOLDER_SAFE_RE.sub("_", folder_name.strip()).strip("_")
    return cleaned or "scrape"


def resolve_output_dir(*, out_root: Path, folder_name: str) -> Path:
    """Return the output directory for ``folder_name`` under ``out_root``.

    Ensures the resulting path stays inside ``out_root`` to avoid accidental
    writes outside the configured resources directory.
    """

    safe = sanitize_folder_name(folder_name)
    candidate = (out_root / safe).resolve()
    root = out_root.resolve()
    if candidate == root or root not in candidate.parents:
        msg = f"Refusing to write outside out_root: {candidate}"
        raise ValueError(msg)
    return candidate

