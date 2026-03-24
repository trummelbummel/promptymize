from __future__ import annotations

import re
from pathlib import Path

_SEGMENT_INVALID = re.compile(r"[^a-zA-Z0-9._-]+")


def sanitize_folder_name(name: str) -> str:
    """
    Turn a configured folder name into a safe single path segment.

    :param name: Raw folder name from configuration.
    :return: Sanitized segment safe for use under the output root.
    """

    cleaned = name.strip()
    if not cleaned:
        return "scrape"
    out = _SEGMENT_INVALID.sub("_", cleaned)
    out = out.strip("_")
    if not out:
        return "scrape"
    return out


def resolve_output_dir(out_root: Path, folder_name: str) -> Path:
    """
    Resolve the output directory for a scrape target under ``out_root``.

    ``folder_name`` may contain nested segments separated by ``/``; each
    segment is sanitized. ``..`` and ``.`` segments are ignored so paths
    cannot escape ``out_root``.

    :param out_root: Root directory for scraped data (e.g. ``sources/data``).
    :param folder_name: Logical folder path from configuration.
    :return: Absolute resolved path under ``out_root``.
    """

    root = out_root.resolve()
    raw_parts = folder_name.replace("\\", "/").split("/")
    segments: list[str] = []
    for part in raw_parts:
        if not part or part == ".":
            continue
        if part == "..":
            continue
        segments.append(sanitize_folder_name(part))
    if not segments:
        return root / "scrape"
    out = root
    for seg in segments:
        out = out / seg
    return out
