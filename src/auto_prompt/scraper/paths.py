from __future__ import annotations

import re
from pathlib import Path

_FOLDER_SAFE_RE = re.compile(r"[^a-zA-Z0-9_-]+")


def sanitize_folder_name(folder_name: str) -> str:
    """Replace non-alphanumeric characters with underscores, stripping leading/trailing underscores."""

    cleaned = _FOLDER_SAFE_RE.sub("_", folder_name.strip()).strip("_")
    return cleaned or "scrape"


def resolve_output_dir(*, out_root: Path, folder_name: str) -> Path:
    """Return the output directory for ``folder_name`` under ``out_root``.

    ``folder_name`` may contain ``/`` separators to create nested directories.
    Each segment is sanitized individually. The resulting path is guaranteed to
    stay inside ``out_root``.

    Raises :class:`ValueError` if the resolved path escapes ``out_root``.
    """

    segments = [s for s in folder_name.split("/") if s.strip()]
    safe_path = "/".join(sanitize_folder_name(s) for s in segments) if segments else "scrape"

    candidate = (out_root / safe_path).resolve()
    root = out_root.resolve()

    if candidate == root or root not in candidate.parents:
        msg = f"Refusing to write outside out_root: {candidate}"
        raise ValueError(msg)
    return candidate

