from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup, Tag
from markdownify import markdownify as html_to_md


@dataclass(frozen=True)
class ScrapeResult:
    url: str
    title: str
    output_dir: Path
    markdown_path: Path
    html_path: Path
    meta_path: Path


_FOLDER_SAFE_RE = re.compile(r"[^a-zA-Z0-9_-]+")


def sanitize_folder_name(folder_name: str) -> str:
    cleaned = _FOLDER_SAFE_RE.sub("_", folder_name.strip()).strip("_")
    return cleaned or "scrape"


def resolve_output_dir(*, out_root: Path, folder_name: str) -> Path:
    safe = sanitize_folder_name(folder_name)
    candidate = (out_root / safe).resolve()
    root = out_root.resolve()
    if candidate == root or root not in candidate.parents:
        msg = f"Refusing to write outside out_root: {candidate}"
        raise ValueError(msg)
    return candidate


def _fetch_html_requests(url: str, *, timeout_s: float = 30.0) -> str:
    headers = {
        "User-Agent": "auto-prompt-scraper/0.0.1 (+https://github.com/trummelbummel/auto-prompt)",
        "Accept": "text/html,application/xhtml+xml",
    }
    resp = requests.get(url, headers=headers, timeout=timeout_s)
    resp.raise_for_status()
    resp.encoding = resp.encoding or "utf-8"
    return resp.text


def _fetch_html_playwright(url: str, *, timeout_s: float = 45.0) -> str:
    # Lazy import so basic scraping works without browser dependencies installed.
    from playwright.sync_api import sync_playwright  # type: ignore[import-not-found]

    timeout_ms = int(timeout_s * 1000)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=timeout_ms)
            return page.content()
        finally:
            browser.close()


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

    for el in list(container.select('[role="navigation"], [role="banner"], [role="contentinfo"]')):
        el.decompose()


def html_to_markdown(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    title = (soup.title.get_text(strip=True) if soup.title else "").strip() or "Untitled"
    container = _pick_main_container(soup)
    _strip_noise(container)
    md = html_to_md(str(container), heading_style="ATX", code_language_callback=lambda _: "")
    md = md.replace("\r\n", "\n").strip() + "\n"
    return title, md


def _looks_like_unrendered_shell(md: str) -> bool:
    nonempty = [line.strip() for line in md.splitlines() if line.strip()]
    if len(nonempty) <= 20 and any(line.lower() == "loading..." for line in nonempty):
        return True
    if len(md.strip()) < 400:
        return True
    return False


def fetch_html(url: str, *, timeout_s: float = 30.0, render_js: bool = True) -> str:
    html = _fetch_html_requests(url, timeout_s=timeout_s)
    if not render_js:
        return html

    try:
        _title, md = html_to_markdown(html)
    except Exception:
        md = ""

    if _looks_like_unrendered_shell(md):
        return _fetch_html_playwright(url, timeout_s=max(timeout_s, 45.0))
    return html


def write_scrape(*, url: str, folder_name: str, out_root: Path, render_js: bool = True) -> ScrapeResult:
    out_root_resolved = out_root.resolve()
    output_dir = resolve_output_dir(out_root=out_root_resolved, folder_name=folder_name)
    output_dir.mkdir(parents=True, exist_ok=True)

    html = fetch_html(url, render_js=render_js)
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
    p = argparse.ArgumentParser(description="Scrape a documentation page to resources/<foldername>/")
    p.add_argument("url", help="Documentation page URL to scrape")
    p.add_argument("foldername", help="Folder name under resources/ to write into")
    p.add_argument(
        "--out-root",
        default="resources",
        help="Output root directory (default: resources)",
    )
    p.add_argument(
        "--no-render-js",
        action="store_true",
        help="Disable JS rendering fallback (faster, but some sites will only return a shell).",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    out_root = Path(args.out_root)
    result = write_scrape(
        url=args.url,
        folder_name=args.foldername,
        out_root=out_root,
        render_js=not args.no_render_js,
    )
    print(str(result.markdown_path))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

