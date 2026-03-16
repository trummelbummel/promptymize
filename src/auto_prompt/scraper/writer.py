from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from auto_prompt.scraper.paths import resolve_output_dir
from auto_prompt.scraper.types import WebScrapeResult


class ScrapeWriter:
    """
    Persist scrape artefacts (Markdown, HTML, metadata) to disk.

    Instances of this class are stateless and can be reused safely.
    """

    def write(
        self,
        *,
        url: str,
        folder_name: str,
        html: str,
        text: str,
        out_root: Path,
    ) -> WebScrapeResult:
        """
        Write ``text`` and ``html`` under ``out_root/<folder_name>/`` and return a descriptor.

        :param url: URL that was scraped.
        :param folder_name: Logical folder name used to determine the output path.
        :param html: Raw HTML content to persist.
        :param text: Normalized text or Markdown representation to persist.
        :param out_root: Root directory under which all scrape outputs are written.
        :return: Descriptor describing the written artefacts for this scrape.
        """

        resolved_root = out_root.resolve()
        output_dir = resolve_output_dir(out_root=resolved_root, folder_name=folder_name)
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
                "markdown": str(markdown_path.relative_to(resolved_root)),
                "html": str(html_path.relative_to(resolved_root)),
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
    """
    Persist scrape artefacts using the shared default :class:`ScrapeWriter`.

    :param url: URL that was scraped.
    :param folder_name: Logical folder name used to determine the output path.
    :param html: Raw HTML content to persist.
    :param text: Normalized text or Markdown representation to persist.
    :param out_root: Root directory under which all scrape outputs are written.
    :return: Descriptor describing the written artefacts for this scrape.
    """

    return _DEFAULT_WRITER.write(url=url, folder_name=folder_name, html=html, text=text, out_root=out_root)

