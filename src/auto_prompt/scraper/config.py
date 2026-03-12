from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import yaml

_SLUG_RE = re.compile(r"[^a-zA-Z0-9]+")


@dataclass(frozen=True)
class ScrapeTarget:
    folder_name: str
    url: str


@dataclass(frozen=True)
class ScraperConfig:
    targets: list[ScrapeTarget]


def _slug_from_url(url: str) -> str:
    """Derive a short filesystem-safe slug from a URL path."""

    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        path = parsed.hostname or "index"
    last_segment = path.rsplit("/", 1)[-1]
    slug = _SLUG_RE.sub("_", last_segment).strip("_").lower()
    return slug or "page"


def load_config(path: Path) -> ScraperConfig:
    """Load scraper targets from a YAML file.

    ``url`` may be a single string or a list of strings. When a list is given
    each URL becomes its own :class:`ScrapeTarget` placed under
    ``<folder_name>/<slug>`` so that files don't overwrite each other.
    """

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        msg = "Config root must be a mapping"
        raise ValueError(msg)

    raw_targets = raw.get("targets")
    if not isinstance(raw_targets, list):
        msg = "Config must contain 'targets' as a list"
        raise ValueError(msg)

    targets: list[ScrapeTarget] = []
    for i, item in enumerate(raw_targets):
        if not isinstance(item, dict):
            msg = f"targets[{i}] must be a mapping"
            raise ValueError(msg)

        folder_name = item.get("folder_name")
        if not isinstance(folder_name, str) or not folder_name.strip():
            msg = f"targets[{i}].folder_name must be a non-empty string"
            raise ValueError(msg)

        url = item.get("url")
        if isinstance(url, str) and url.strip():
            targets.append(ScrapeTarget(folder_name=folder_name.strip(), url=url.strip()))
        elif isinstance(url, list):
            for j, u in enumerate(url):
                if not isinstance(u, str) or not u.strip():
                    msg = f"targets[{i}].url[{j}] must be a non-empty string"
                    raise ValueError(msg)
                slug = _slug_from_url(u.strip())
                sub_folder = f"{folder_name.strip()}/{slug}"
                targets.append(ScrapeTarget(folder_name=sub_folder, url=u.strip()))
        else:
            msg = f"targets[{i}].url must be a non-empty string or list of strings"
            raise ValueError(msg)

    return ScraperConfig(targets=targets)

