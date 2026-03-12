from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Tag
from markdownify import markdownify as html_to_md

from auto_prompt.scraper.fetch import fetch_html


@dataclass(frozen=True)
class ScrapeResult:
    """Result of scraping a single documentation page."""

    url: str
    title: str
    output_dir: Path
    markdown_path: Path
    html_path: Path
    meta_path: Path


_FOLDER_SAFE_RE = re.compile(r"[^a-zA-Z0-9_-]+")


def sanitize_folder_name(folder_name: str) -> str:
    """Return a filesystem-safe folder name based on ``folder_name``."""

    cleaned = _FOLDER_SAFE_RE.sub("_", folder_name.strip()).strip("_")
    return cleaned or "scrape"


def resolve_output_dir(*, out_root: Path, folder_name: str) -> Path:
    """Return the output directory for ``folder_name`` under ``out_root``."""

    safe = sanitize_folder_name(folder_name)
    candidate = (out_root / safe).resolve()
    root = out_root.resolve()
    if candidate == root or root not in candidate.parents:
        msg = f"Refusing to write outside out_root: {candidate}"
        raise ValueError(msg)
    return candidate


def _pick_main_container(soup: BeautifulSoup) -> Tag:
    for selector in ("main", "article", '[role="main"]', "body"):
        el = soup.select_one(selector)
        if isinstance(el, Tag):
            return el
    msg = "Could not find a main content container"
    raise ValueError(msg)


def _strip_noise(container: Tag) -> None:
    for selector in (
        "script",
        "style",
        "noscript",
        "svg",
        "header",
        "footer",
        "nav",
        "aside",
        "form",
        '[aria-hidden="true"]',
    ):
        for el in list(container.select(selector)):
            el.decompose()


def html_to_markdown(html: str) -> tuple[str, str]:
    """Convert documentation HTML into a title and markdown body."""

    soup = BeautifulSoup(html, "html.parser")
    title = (soup.title.get_text(strip=True) if soup.title else "").strip() or "Untitled"
    container = _pick_main_container(soup)
    _strip_noise(container)
    md = html_to_md(str(container), heading_style="ATX", code_language_callback=lambda _: "")
    md = md.replace("\r\n", "\n").strip() + "\n"
    return title, md


def write_scrape(*, url: str, folder_name: str, out_root: Path) -> ScrapeResult:
    """Fetch, convert and write a single page to disk."""

    out_root_resolved = out_root.resolve()
    output_dir = resolve_output_dir(out_root=out_root_resolved, folder_name=folder_name)
    output_dir.mkdir(parents=True, exist_ok=True)

    html = fetch_html(url)
    title, md = html_to_markdown(html)

    markdown_path = output_dir / "page.md"
    html_path = output_dir / "raw.html"
    meta_path = output_dir / "meta.json"

    markdown_path.write_text(md, encoding="utf-8")
    html_path.write_text(html, encoding="utf-8")

    meta: dict[str, Any] = {
        "url": url,
        "title": title,
        "scraped_at": datetime.now(tz=timezone.utc).isoformat(),
        "hostname": urlparse(url).hostname,
        "output": {
            "markdown": str(markdown_path.relative_to(out_root_resolved)),
            "html": str(html_path.relative_to(out_root_resolved)),
        },
    }
    meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return ScrapeResult(
        url=url,
        title=title,
        output_dir=output_dir,
        markdown_path=markdown_path,
        html_path=html_path,
        meta_path=meta_path,
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""

    p = argparse.ArgumentParser(description="Scrape a documentation page to resources/<foldername>/")
    p.add_argument("url", help="Documentation page URL to scrape")
    p.add_argument("foldername", help="Folder name under resources/ to write into")
    p.add_argument(
        "--out-root",
        default="resources",
        help="Output root directory (default: resources)",
    )
    return p


def fetch_html_cli(url: str) -> str:
    """Separate fetch function for CLI use, delegating to shared fetch_html."""

    return fetch_html(url)


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``auto-prompt-scrape`` CLI."""

    args = build_parser().parse_args(argv)
    out_root = Path(args.out_root)
    result = write_scrape(url=args.url, folder_name=args.foldername, out_root=out_root)
    print(str(result.markdown_path))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

