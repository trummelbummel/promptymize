from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WebScrapeResult:
    """Result of a single scrape.

    :param url: The scraped URL.
    :param folder_name: Logical folder name for this target.
    :param output_dir: Directory containing this target's outputs.
    :param markdown_path: Path to the text-only markdown file.
    :param html_path: Path to the saved source HTML file.
    :param meta_path: Path to the metadata JSON file.
    """

    url: str
    folder_name: str
    output_dir: Path
    markdown_path: Path
    html_path: Path
    meta_path: Path

