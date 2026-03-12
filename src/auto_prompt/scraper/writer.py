from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from auto_prompt.scraper.paths import resolve_output_dir
from auto_prompt.scraper.types import WebScrapeResult


class ScrapeWriter:
    """Persist scrape results and return descriptors."""

    def write(
        self,
        *,
        url: str,
        folder_name: str,
        html: str,
        text: str,
        out_root: Path,
    ) -> WebScrapeResult:
        """Persist scrape result under ``out_root`` and return a descriptor."""

        out_root_resolved = out_root.resolve()
        output_dir = resolve_output_dir(out_root=out_root_resolved, folder_name=folder_name)
        output_dir.mkdir(parents=True, exist_ok=True)

        markdown_path = output_dir / "page.md"
        html_path = output_dir / "source.html"
        meta_path = output_dir / "meta.json"

        markdown_path.write_text(text, encoding="utf-8")
        html_path.write_text(html, encoding="utf-8")

        meta: dict[str, Any] = {
            "url": url,
            "folder_name": folder_name,
            "scraped_at": datetime.now(tz=timezone.utc).isoformat(),
            "hostname": urlparse(url).hostname,
            "output": {
                "markdown": str(markdown_path.relative_to(out_root_resolved)),
                "html": str(html_path.relative_to(out_root_resolved)),
            },
        }
        meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        return WebScrapeResult(
            url=url,
            folder_name=folder_name,
            output_dir=output_dir,
            markdown_path=markdown_path,
            html_path=html_path,
            meta_path=meta_path,
        )


_DEFAULT_WRITER = ScrapeWriter()


def write_scrape_outputs(
    *,
    url: str,
    folder_name: str,
    html: str,
    text: str,
    out_root: Path,
) -> WebScrapeResult:
    """Convenience wrapper around :class:`ScrapeWriter` for callers."""

    return _DEFAULT_WRITER.write(url=url, folder_name=folder_name, html=html, text=text, out_root=out_root)

