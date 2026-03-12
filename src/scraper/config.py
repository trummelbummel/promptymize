from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class ScrapeTarget:
    folder_name: str
    url: str


@dataclass(frozen=True)
class ScraperConfig:
    targets: list[ScrapeTarget]


def load_config(path: Path) -> ScraperConfig:
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
        url = item.get("url")
        if not isinstance(folder_name, str) or not folder_name.strip():
            msg = f"targets[{i}].folder_name must be a non-empty string"
            raise ValueError(msg)
        if not isinstance(url, str) or not url.strip():
            msg = f"targets[{i}].url must be a non-empty string"
            raise ValueError(msg)
        targets.append(ScrapeTarget(folder_name=folder_name.strip(), url=url.strip()))

    return ScraperConfig(targets=targets)

