from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

_SLUG_RE = re.compile(r"[^a-zA-Z0-9]+")


@dataclass(frozen=True)
class ScrapeTarget:
    """
    A single URL to scrape and the folder it should be written into.

    :param folder_name: Logical folder name under the scrape root.
    :param url: The URL that should be scraped.
    """

    folder_name: str
    url: str


@dataclass(frozen=True)
class ScraperConfig:
    """
    Collection of scrape targets parsed from a YAML config file.

    :param targets: List of individual scrape targets.
    """

    targets: list[ScrapeTarget]


def _slug_from_url(url: str) -> str:
    """
    Derive a short filesystem-safe slug from the last path segment of ``url``.

    :param url: URL whose path should be converted into a slug.
    :return: Lowercase slug suitable for use in directory names.
    """

    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        path = parsed.hostname or "index"
    last_segment = path.rsplit("/", 1)[-1]
    slug = _SLUG_RE.sub("_", last_segment).strip("_").lower()
    return slug or "page"


def _parse_target(index: int, item: dict[str, Any]) -> list[ScrapeTarget]:
    """
    Validate and expand a single raw target entry into one or more :class:`ScrapeTarget`.

    :param index: Index of the target in the raw ``targets`` list (for error messages).
    :param item: Raw mapping describing a single target.
    :return: One or more validated :class:`ScrapeTarget` instances.
    :raises ValueError: If required fields are missing or of the wrong type.
    """

    folder_name = item.get("folder_name")
    if not isinstance(folder_name, str) or not folder_name.strip():
        msg = f"targets[{index}].folder_name must be a non-empty string"
        raise ValueError(msg)

    folder_name = folder_name.strip()
    url = item.get("url")

    if isinstance(url, str) and url.strip():
        return [ScrapeTarget(folder_name=folder_name, url=url.strip())]

    if isinstance(url, list):
        targets: list[ScrapeTarget] = []
        for j, u in enumerate(url):
            if not isinstance(u, str) or not u.strip():
                msg = f"targets[{index}].url[{j}] must be a non-empty string"
                raise ValueError(msg)
            slug = _slug_from_url(u.strip())
            targets.append(ScrapeTarget(folder_name=f"{folder_name}/{slug}", url=u.strip()))
        return targets

    msg = f"targets[{index}].url must be a non-empty string or list of strings"
    raise ValueError(msg)


def load_config(path: Path) -> ScraperConfig:
    """Load scraper targets from a YAML file.

    ``url`` may be a single string or a list of strings. When a list is given
    each URL becomes its own :class:`ScrapeTarget` placed under
    ``<folder_name>/<slug>`` so that files don't overwrite each other.

    :param path: Path to the YAML configuration file.
    :return: Parsed configuration describing all scrape targets.
    :raises ValueError: If the file contents do not match the expected schema.
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
        targets.extend(_parse_target(i, item))

    return ScraperConfig(targets=targets)

